#!/usr/bin/env node
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

const DEFAULT_DEBUG = 'http://127.0.0.1:9222';

function parseArgs(argv) {
  const args = { debug: DEFAULT_DEBUG, waitMs: 15000, out: '' };
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const next = argv[i + 1];
    if (key === '--url') { args.url = next; i += 1; }
    else if (key === '--out') { args.out = next; i += 1; }
    else if (key === '--debug') { args.debug = next; i += 1; }
    else if (key === '--wait-ms') { args.waitMs = Number(next); i += 1; }
    else if (key === '--help' || key === '-h') { args.help = true; }
    else throw new Error(`Unknown argument: ${key}`);
  }
  return args;
}

function usage() {
  return `Usage: node cdp-capture.mjs --url https://maps.google.com/search/... --out capture.json [--wait-ms 20000]\n\nChrome must be running with --remote-debugging-port=9222.`;
}

async function requestJson(url, init = {}) {
  const res = await fetch(url, init);
  if (!res.ok) throw new Error(`${init.method ?? 'GET'} ${url} failed: ${res.status} ${res.statusText}`);
  return res.json();
}

class CdpClient {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.handlers = new Map();
  }

  async open() {
    await new Promise((resolveOpen, rejectOpen) => {
      const timeout = setTimeout(() => rejectOpen(new Error('Timed out connecting to Chrome DevTools')), 5000);
      this.ws.addEventListener('open', () => { clearTimeout(timeout); resolveOpen(); }, { once: true });
      this.ws.addEventListener('error', () => { clearTimeout(timeout); rejectOpen(new Error('WebSocket connection failed')); }, { once: true });
    });
    this.ws.addEventListener('message', (event) => {
      const message = JSON.parse(event.data);
      if (message.id && this.pending.has(message.id)) {
        const { resolve: ok, reject } = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(JSON.stringify(message.error)));
        else ok(message.result ?? {});
        return;
      }
      if (message.method) {
        const callbacks = this.handlers.get(message.method) ?? [];
        for (const callback of callbacks) callback(message.params ?? {});
      }
    });
  }

  on(method, callback) {
    const callbacks = this.handlers.get(method) ?? [];
    callbacks.push(callback);
    this.handlers.set(method, callbacks);
  }

  send(method, params = {}) {
    const id = this.nextId;
    this.nextId += 1;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolveSend, rejectSend) => {
      this.pending.set(id, { resolve: resolveSend, reject: rejectSend });
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          rejectSend(new Error(`CDP command timed out: ${method}`));
        }
      }, 10000);
    });
  }

  close() {
    this.ws.close();
  }
}

function sanitizeHeaders(headers) {
  const redacted = {};
  for (const [key, value] of Object.entries(headers ?? {})) {
    if (/^(authorization|cookie|set-cookie|x-client-data)$/i.test(key)) redacted[key] = '[redacted]';
    else redacted[key] = String(value);
  }
  return redacted;
}

function shouldTryBody(response) {
  const type = String(response.mimeType || response.headers?.['content-type'] || response.headers?.['Content-Type'] || '').toLowerCase();
  return response.encodedDataLength < 2_000_000 && (
    type.includes('json') ||
    type.includes('text') ||
    type.includes('javascript') ||
    type.includes('protobuf') ||
    type.includes('x-protobuffer') ||
    type.includes('application/octet-stream')
  );
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.url || !args.out) {
    console.log(usage());
    process.exit(args.help ? 0 : 1);
  }

  const debugBase = args.debug.replace(/\/$/, '');
  let target;
  try {
    target = await requestJson(`${debugBase}/json/new?${encodeURIComponent('about:blank')}`, { method: 'PUT' });
  } catch (error) {
    throw new Error(`Cannot create Chrome target at ${debugBase}. Start Chrome with --remote-debugging-port=9222. ${error.message}`);
  }

  const cdp = new CdpClient(target.webSocketDebuggerUrl);
  await cdp.open();

  const startedAt = new Date().toISOString();
  const requests = new Map();
  const events = [];

  cdp.on('Network.requestWillBeSent', (params) => {
    const record = requests.get(params.requestId) ?? { requestId: params.requestId };
    record.request = {
      url: params.request.url,
      method: params.request.method,
      headers: sanitizeHeaders(params.request.headers),
      postData: params.request.postData ? String(params.request.postData).slice(0, 20000) : undefined,
      mixedContentType: params.request.mixedContentType,
      initialPriority: params.request.initialPriority,
      referrerPolicy: params.request.referrerPolicy,
    };
    record.type = params.type;
    record.initiator = params.initiator;
    record.wallTime = params.wallTime;
    record.timestamp = params.timestamp;
    requests.set(params.requestId, record);
    events.push({ method: 'Network.requestWillBeSent', params });
  });

  cdp.on('Network.responseReceived', (params) => {
    const record = requests.get(params.requestId) ?? { requestId: params.requestId };
    record.response = {
      url: params.response.url,
      status: params.response.status,
      statusText: params.response.statusText,
      headers: sanitizeHeaders(params.response.headers),
      mimeType: params.response.mimeType,
      encodedDataLength: params.response.encodedDataLength,
      remoteIPAddress: params.response.remoteIPAddress,
      remotePort: params.response.remotePort,
      protocol: params.response.protocol,
      securityDetails: params.response.securityDetails ? {
        protocol: params.response.securityDetails.protocol,
        issuer: params.response.securityDetails.issuer,
        subjectName: params.response.securityDetails.subjectName,
        validFrom: params.response.securityDetails.validFrom,
        validTo: params.response.securityDetails.validTo,
      } : undefined,
    };
    requests.set(params.requestId, record);
    events.push({ method: 'Network.responseReceived', params });
  });

  cdp.on('Network.loadingFinished', async (params) => {
    const record = requests.get(params.requestId);
    if (!record?.response || !shouldTryBody(record.response)) return;
    try {
      const body = await cdp.send('Network.getResponseBody', { requestId: params.requestId });
      record.body = {
        base64Encoded: Boolean(body.base64Encoded),
        sample: String(body.body ?? '').slice(0, 100000),
        truncated: String(body.body ?? '').length > 100000,
      };
    } catch {
      // Some responses are unavailable by design. Keep the request metadata.
    }
  });

  cdp.on('Network.loadingFailed', (params) => {
    const record = requests.get(params.requestId) ?? { requestId: params.requestId };
    record.failure = { errorText: params.errorText, canceled: params.canceled, blockedReason: params.blockedReason };
    requests.set(params.requestId, record);
  });

  await cdp.send('Network.enable', { maxTotalBufferSize: 100_000_000, maxResourceBufferSize: 20_000_000 });
  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');
  await cdp.send('Page.navigate', { url: args.url });
  await new Promise((resolveWait) => setTimeout(resolveWait, args.waitMs));

  const pageState = await cdp.send('Runtime.evaluate', {
    expression: `(() => ({ title: document.title, url: location.href, bodyText: document.body?.innerText?.slice(0, 5000) || '', scripts: [...document.scripts].map(s => s.src).filter(Boolean).slice(0, 200) }))()`,
    returnByValue: true,
  }).catch((error) => ({ result: { value: { error: error.message } } }));

  const output = {
    capturedAt: startedAt,
    targetUrl: args.url,
    finalPageState: pageState.result?.value,
    requests: [...requests.values()],
    eventCount: events.length,
  };

  const outPath = resolve(args.out);
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, `${JSON.stringify(output, null, 2)}\n`);
  cdp.close();
  console.error(`Wrote ${outPath} with ${output.requests.length} requests`);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});

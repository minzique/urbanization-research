#!/usr/bin/env node
import { readFile } from 'node:fs/promises';

function usage() {
  return 'Usage: node analyze-capture.mjs capture.json';
}

function parseUrl(raw) {
  try { return new URL(raw); } catch { return null; }
}

function isApiCandidate(record) {
  const url = parseUrl(record.request?.url || record.response?.url || '');
  if (!url) return false;
  const type = record.type || '';
  const mime = record.response?.mimeType || '';
  const path = url.pathname;
  return /Fetch|XHR|Other/i.test(type)
    || /json|protobuf|octet-stream|text\/plain/i.test(mime)
    || /\/(api|rpc|search|preview|place|places|maps|batchexecute|vt|pb|list|details)\b/i.test(path)
    || url.searchParams.has('pb')
    || url.searchParams.has('q')
    || url.searchParams.has('query');
}

function summarizeBody(record) {
  const sample = record.body?.sample;
  if (!sample) return '';
  const decoded = record.body.base64Encoded ? '[base64 body captured]' : sample;
  const text = decoded.slice(0, 2000);
  const hints = [];
  for (const pattern of ['place_id', 'rating', 'reviews', 'latitude', 'longitude', 'business', 'opening', 'phone', 'website', 'photos', 'Godagama']) {
    if (text.toLowerCase().includes(pattern.toLowerCase())) hints.push(pattern);
  }
  return hints.length ? `body hints: ${hints.join(', ')}` : `body sample: ${JSON.stringify(text.slice(0, 300))}`;
}

function groupKey(record) {
  const url = parseUrl(record.request?.url || record.response?.url || '');
  if (!url) return 'invalid-url';
  const params = [...url.searchParams.keys()].sort().join('&');
  return `${record.request?.method || 'GET'} ${url.origin}${url.pathname}${params ? ` ?${params}` : ''}`;
}

async function main() {
  const file = process.argv[2];
  if (!file) {
    console.error(usage());
    process.exit(1);
  }
  const capture = JSON.parse(await readFile(file, 'utf8'));
  const records = capture.requests ?? [];
  const candidates = records.filter(isApiCandidate);
  const groups = new Map();
  for (const record of candidates) {
    const key = groupKey(record);
    const arr = groups.get(key) ?? [];
    arr.push(record);
    groups.set(key, arr);
  }

  console.log(`# Capture analysis: ${file}\n`);
  console.log(`- Captured at: ${capture.capturedAt}`);
  console.log(`- Target URL: ${capture.targetUrl}`);
  console.log(`- Final URL: ${capture.finalPageState?.url ?? ''}`);
  console.log(`- Title: ${capture.finalPageState?.title ?? ''}`);
  console.log(`- Total requests: ${records.length}`);
  console.log(`- API candidates: ${candidates.length}`);
  console.log('');

  if (capture.finalPageState?.bodyText) {
    console.log('## Page text sample\n');
    console.log('```text');
    console.log(capture.finalPageState.bodyText.slice(0, 1500));
    console.log('```\n');
  }

  console.log('## Candidate endpoint groups\n');
  const sortedGroups = [...groups.entries()].sort((a, b) => b[1].length - a[1].length);
  for (const [key, arr] of sortedGroups) {
    const statuses = [...new Set(arr.map(r => r.response?.status ?? 'pending'))].join(', ');
    const types = [...new Set(arr.map(r => r.type || 'unknown'))].join(', ');
    const mime = [...new Set(arr.map(r => r.response?.mimeType || ''))].filter(Boolean).join(', ');
    console.log(`### ${key}`);
    console.log(`- Count: ${arr.length}`);
    console.log(`- Statuses: ${statuses}`);
    console.log(`- Types: ${types}`);
    console.log(`- MIME: ${mime}`);
    const firstUrl = arr[0].request?.url || arr[0].response?.url || '';
    console.log(`- Example URL: ${firstUrl}`);
    const post = arr.find(r => r.request?.postData)?.request?.postData;
    if (post) console.log(`- Example POST body: \`${post.slice(0, 500).replaceAll('`', '\\`')}\``);
    const bodySummary = summarizeBody(arr.find(r => r.body?.sample) || arr[0]);
    if (bodySummary) console.log(`- ${bodySummary}`);
    console.log('');
  }

  console.log('## Script assets\n');
  for (const src of capture.finalPageState?.scripts ?? []) console.log(`- ${src}`);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});

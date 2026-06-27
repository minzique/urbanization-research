#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

const CSV_COLUMNS = [
  'place_id', 'name', 'brand', 'category', 'subcategory', 'lat', 'lng', 'address', 'area', 'radius_zone',
  'google_maps_url', 'website', 'phone', 'business_status', 'rating', 'review_count', 'price_level',
  'current_opening_hours', 'first_review_date', 'first_photo_date', 'earliest_visible_activity_date',
  'latest_visible_activity_date', 'opening_date_if_available', 'last_seen_date', 'source_method',
  'evidence_url', 'evidence_screenshot', 'confidence', 'notes'
];

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const next = argv[i + 1];
    if (key === '--profile') { args.profile = next; i += 1; }
    else if (key === '--areas') { args.areas = next; i += 1; }
    else if (key === '--categories') { args.categories = next; i += 1; }
    else if (key === '--out') { args.out = next; i += 1; }
    else if (key === '--help' || key === '-h') { args.help = true; }
    else throw new Error(`Unknown argument: ${key}`);
  }
  return args;
}

function usage() {
  return 'Usage: node extract-pois.mjs --profile endpoint-profile.local.json --areas study-areas.json --categories categories.json --out google_maps_godagama_pois.csv';
}

function render(template, vars) {
  return String(template ?? '').replace(/\{([a-zA-Z0-9_]+)\}/g, (_, key) => encodeURIComponent(vars[key] ?? ''));
}

function renderHeaderValue(value) {
  return String(value).replace(/\$\{([A-Z0-9_]+)\}/g, (_, key) => process.env[key] ?? '');
}

function parsePath(path) {
  if (!path) return [];
  return String(path).split('.').filter(Boolean).flatMap((part) => {
    if (part.endsWith('[]')) return [{ key: part.slice(0, -2), flatten: true }];
    return [{ key: part, flatten: false }];
  });
}

function getPath(value, path) {
  const parts = parsePath(path);
  let current = [value];
  for (const part of parts) {
    const next = [];
    for (const item of current) {
      if (item == null) continue;
      const child = Array.isArray(item) && /^\d+$/.test(part.key) ? item[Number(part.key)] : item[part.key];
      if (part.flatten && Array.isArray(child)) next.push(...child);
      else if (child !== undefined) next.push(child);
    }
    current = next;
  }
  if (current.length === 0) return '';
  if (current.length === 1) return current[0];
  return current;
}

function stringifyCell(value) {
  if (value == null) return '';
  if (Array.isArray(value)) return value.map(stringifyCell).filter(Boolean).join(' | ');
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function csvEscape(value) {
  const text = stringifyCell(value);
  return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(rows) {
  const lines = [CSV_COLUMNS.join(',')];
  for (const row of rows) lines.push(CSV_COLUMNS.map((column) => csvEscape(row[column] ?? '')).join(','));
  return `${lines.join('\n')}\n`;
}

function normalizeTextResponse(text, mode) {
  if (mode === 'json') return JSON.parse(text);
  if (mode === 'json-xssi') return JSON.parse(text.replace(/^\)\]\}'\s*,?\n?/, ''));
  return text;
}

function mapItem(item, profile, context) {
  const row = Object.fromEntries(CSV_COLUMNS.map((column) => [column, '']));
  for (const [column, path] of Object.entries(profile.fieldMap ?? {})) {
    row[column] = getPath(item, path);
  }
  row.category = context.category.id;
  row.area = context.area.label;
  row.radius_zone = context.area.id;
  row.last_seen_date = new Date().toISOString().slice(0, 10);
  row.source_method = 'competition_private_api';
  row.evidence_url = context.url;
  row.confidence = row.earliest_visible_activity_date || row.first_review_date || row.first_photo_date || row.opening_date_if_available ? 'approximate' : 'current_only';
  row.notes = `query=${context.query}; extractor_profile=${profile.name ?? 'unnamed'}`;
  return row;
}

async function sleep(ms) {
  await new Promise((resolveSleep) => setTimeout(resolveSleep, ms));
}

async function fetchPage(profile, vars) {
  const url = render(profile.urlTemplate, vars);
  const headers = Object.fromEntries(Object.entries(profile.headers ?? {}).map(([k, v]) => [k, renderHeaderValue(v)]));
  const init = { method: profile.method ?? 'GET', headers };
  if (profile.bodyTemplate) init.body = render(profile.bodyTemplate, vars);
  const res = await fetch(url, init);
  const text = await res.text();
  if (!res.ok) throw new Error(`${init.method} ${url} failed: ${res.status} ${res.statusText}: ${text.slice(0, 500)}`);
  return { url, status: res.status, parsed: normalizeTextResponse(text, profile.responseMode ?? 'json'), rawSample: text.slice(0, 1000) };
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.profile || !args.areas || !args.categories || !args.out) {
    console.log(usage());
    process.exit(args.help ? 0 : 1);
  }

  const profile = JSON.parse(await readFile(args.profile, 'utf8'));
  const { areas } = JSON.parse(await readFile(args.areas, 'utf8'));
  const { categories } = JSON.parse(await readFile(args.categories, 'utf8'));
  const rows = [];
  const provenance = [];
  const seen = new Set();

  for (const area of areas) {
    for (const category of categories) {
      for (const queryPart of category.queries) {
        let pageToken = '';
        const query = `${queryPart} near ${area.label.replace(/ comparator| core 1 km| catchment 3 km| pressure zone 5 km/g, '')}, Sri Lanka`;
        for (let page = 1; page <= (profile.maxPagesPerSearch ?? 1); page += 1) {
          const vars = { ...area, query, page_token: pageToken };
          const fetched = await fetchPage(profile, vars);
          const items = getPath(fetched.parsed, profile.itemsPath);
          const itemList = Array.isArray(items) ? items : (items ? [items] : []);
          for (const item of itemList) {
            const row = mapItem(item, profile, { area, category, query, url: fetched.url });
            const key = row.place_id || `${row.name}|${row.lat}|${row.lng}`;
            if (!key || seen.has(key)) continue;
            seen.add(key);
            rows.push(row);
          }
          provenance.push({ at: new Date().toISOString(), area: area.id, category: category.id, query, page, url: fetched.url, status: fetched.status, itemCount: itemList.length });
          pageToken = stringifyCell(getPath(fetched.parsed, profile.nextPageTokenPath));
          if (!pageToken) break;
          await sleep(profile.delayMs ?? 250);
        }
      }
    }
  }

  const outPath = resolve(args.out);
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, toCsv(rows));
  await writeFile(outPath.replace(/\.csv$/i, '.provenance.ndjson'), provenance.map((entry) => JSON.stringify(entry)).join('\n') + '\n');
  console.error(`Wrote ${rows.length} unique POIs to ${outPath}`);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});

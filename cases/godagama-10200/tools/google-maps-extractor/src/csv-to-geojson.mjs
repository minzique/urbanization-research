#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const next = argv[i + 1];
    if (key === '--in') { args.in = next; i += 1; }
    else if (key === '--out') { args.out = next; i += 1; }
    else if (key === '--help' || key === '-h') { args.help = true; }
    else throw new Error(`Unknown argument: ${key}`);
  }
  return args;
}

function usage() {
  return 'Usage: node csv-to-geojson.mjs --in google_maps_godagama_pois.csv --out google_maps_godagama_pois.geojson';
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = '';
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];
    if (quoted) {
      if (char === '"' && next === '"') { cell += '"'; i += 1; }
      else if (char === '"') quoted = false;
      else cell += char;
    } else if (char === '"') quoted = true;
    else if (char === ',') { row.push(cell); cell = ''; }
    else if (char === '\n') { row.push(cell); rows.push(row); row = []; cell = ''; }
    else if (char !== '\r') cell += char;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const headers = rows.shift() ?? [];
  return rows.filter((values) => values.length === headers.length).map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ''])));
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.in || !args.out) {
    console.log(usage());
    process.exit(args.help ? 0 : 1);
  }
  const rows = parseCsv(await readFile(args.in, 'utf8'));
  const features = rows
    .filter((row) => row.lat && row.lng && Number.isFinite(Number(row.lat)) && Number.isFinite(Number(row.lng)))
    .map((row) => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [Number(row.lng), Number(row.lat)] },
      properties: Object.fromEntries(Object.entries(row).filter(([key]) => key !== 'lat' && key !== 'lng'))
    }));
  const outPath = resolve(args.out);
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, `${JSON.stringify({ type: 'FeatureCollection', features }, null, 2)}\n`);
  console.error(`Wrote ${features.length} features to ${outPath}`);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});

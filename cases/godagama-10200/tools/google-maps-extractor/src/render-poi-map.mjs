#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const next = argv[i + 1];
    if (key === '--geojson') { args.geojson = next; i += 1; }
    else if (key === '--out') { args.out = next; i += 1; }
    else if (key === '--help' || key === '-h') { args.help = true; }
    else throw new Error(`Unknown argument: ${key}`);
  }
  return args;
}

function usage() {
  return 'Usage: node render-poi-map.mjs --geojson google_maps_godagama_pois.geojson --out google_maps_godagama_pois_map.html';
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.geojson || !args.out) {
    console.log(usage());
    process.exit(args.help ? 0 : 1);
  }
  const geojson = JSON.parse(await readFile(args.geojson, 'utf8'));
  const embedded = JSON.stringify(geojson);
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Godagama Google Maps POI extraction</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
  body { margin: 0; font-family: system-ui, -apple-system, Segoe UI, sans-serif; }
  #map { height: 100vh; }
  .panel { position: absolute; z-index: 1000; top: 16px; left: 16px; max-width: 360px; background: white; border-radius: 14px; padding: 14px 16px; box-shadow: 0 12px 40px rgba(0,0,0,.18); }
  .panel h1 { font-size: 16px; margin: 0 0 6px; }
  .panel p { font-size: 12px; margin: 0; color: #444; line-height: 1.35; }
  .legend { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 12px; margin-top: 10px; font-size: 11px; }
  .dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 5px; }
</style>
</head>
<body>
<div class="panel">
  <h1>Godagama / Homagama corridor POIs</h1>
  <p>Extracted from the competition Maps-compatible private web endpoint. Use filters in code or browser devtools for category-specific analysis.</p>
  <div class="legend" id="legend"></div>
</div>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const data = ${embedded};
const colors = {
  supermarket: '#15803d', grocery: '#65a30d', bakery: '#f59e0b', restaurant: '#ef4444', cafe: '#a16207', fast_food: '#dc2626',
  pharmacy: '#06b6d4', clinic: '#0ea5e9', hospital: '#2563eb', bank: '#7c3aed', atm: '#8b5cf6', fuel_station: '#111827',
  school: '#0891b2', university: '#0f766e', tuition: '#14b8a6', hardware: '#78716c', vehicle_service: '#475569', tyre_shop: '#334155',
  electronics: '#9333ea', courier: '#db2777', apartment: '#f97316', land_development: '#b45309', real_estate_office: '#92400e',
  hotel_guesthouse: '#e11d48', government_office: '#64748b', religious_place: '#ca8a04'
};
const map = L.map('map', { preferCanvas: true }).setView([6.850694, 80.0324106], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap contributors' }).addTo(map);
const layers = {};
for (const feature of data.features) {
  const p = feature.properties;
  const cat = p.category || 'other';
  const color = colors[cat] || '#0f172a';
  if (!layers[cat]) layers[cat] = L.layerGroup().addTo(map);
  const [lng, lat] = feature.geometry.coordinates;
  const popup = '<strong>' + escapeHtml(p.name || '') + '</strong><br>'
    + escapeHtml(cat) + ' · ' + escapeHtml(p.subcategory || '') + '<br>'
    + escapeHtml(p.address || '') + '<br>Rating: ' + escapeHtml(p.rating || '')
    + '<br>First photo/activity: ' + escapeHtml(p.first_photo_date || '')
    + '<br><a href="' + escapeHtml(p.google_maps_url || '') + '" target="_blank">Maps link</a>';
  L.circleMarker([lat, lng], { radius: 4, color, fillColor: color, fillOpacity: 0.72, weight: 1 })
    .bindPopup(popup)
    .addTo(layers[cat]);
}
L.control.layers(null, layers, { collapsed: true }).addTo(map);
for (const [cat, color] of Object.entries(colors)) {
  if (!layers[cat]) continue;
  const div = document.createElement('div');
  div.innerHTML = '<span class="dot" style="background:' + color + '"></span>' + escapeHtml(cat);
  document.getElementById('legend').appendChild(div);
}
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
</script>
</body>
</html>
`;
  const outPath = resolve(args.out);
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, html);
  console.error(`Wrote ${outPath}`);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});

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

const BRAND_PATTERNS = [
  ['Keells', /\bkeells\b/i],
  ['Cargills Food City', /\bcargills\b|food city/i],
  ['Sathosa', /\bsathosa\b|සතොස/i],
  ['LAUGFS', /\blaugfs\b/i],
  ['Perera and Sons', /perera|\bp\s*&\s*s\b/i],
  ['Caravan Fresh', /caravan/i],
  ['Pizza Hut', /pizza hut/i],
  ['KFC', /\bkfc\b/i],
  ['BOC', /bank of ceylon|\bboc\b/i],
  ["People's Bank", /people'?s bank/i],
  ['Commercial Bank', /commercial bank/i],
  ['HNB', /\bhnb\b|hatton national/i],
  ['Sampath Bank', /sampath/i],
  ['DFCC', /\bdfcc\b/i],
  ['LOLC', /\blolc\b/i],
  ['NSBM', /\bnsbm\b/i]
];

function parseArgs(argv) {
  const args = { delayMs: 300, baseUrl: 'https://www.google.com', mapsHost: 'https://www.google.com', maxRowsPerSearch: 20 };
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const next = argv[i + 1];
    if (key === '--areas') { args.areas = next; i += 1; }
    else if (key === '--categories') { args.categories = next; i += 1; }
    else if (key === '--out') { args.out = next; i += 1; }
    else if (key === '--area-filter') { args.areaFilter = new RegExp(next); i += 1; }
    else if (key === '--category-filter') { args.categoryFilter = new RegExp(next); i += 1; }
    else if (key === '--delay-ms') { args.delayMs = Number(next); i += 1; }
    else if (key === '--base-url') { args.baseUrl = next.replace(/\/$/, ''); i += 1; }
    else if (key === '--maps-host') { args.mapsHost = next.replace(/\/$/, ''); i += 1; }
    else if (key === '--max-queries') { args.maxQueries = Number(next); i += 1; }
    else if (key === '--help' || key === '-h') { args.help = true; }
    else throw new Error(`Unknown argument: ${key}`);
  }
  return args;
}

function usage() {
  return `Usage: node extract-google-tbm-map.mjs --areas study-areas.json --categories categories.json --out google_maps_godagama_pois.csv [--area-filter godagama] [--category-filter supermarket|bank]\n\nThis extractor uses the Google-Maps-like private web endpoint discovered in normal page boot:\n  /maps/search/<query> -> linked /search?tbm=map&...&pb=... JSON-ish payload\n`;
}

async function sleep(ms) {
  await new Promise((resolveSleep) => setTimeout(resolveSleep, ms));
}

function searchNameForArea(area) {
  if (area.search_name) return area.search_name;
  if (area.id.startsWith('godagama')) return 'Godagama, Sri Lanka';
  if (area.id.startsWith('homagama')) return 'Homagama, Sri Lanka';
  if (area.id.startsWith('meegoda')) return 'Meegoda, Sri Lanka';
  if (area.id.startsWith('kottawa')) return 'Kottawa Makumbura, Sri Lanka';
  if (area.id.startsWith('kahathuduwa')) return 'Kahathuduwa, Sri Lanka';
  if (area.id.startsWith('padukka')) return 'Padukka, Sri Lanka';
  return `${area.label}, Sri Lanka`;
}

function makeQuery(queryPart, area) {
  return `${queryPart} near ${searchNameForArea(area)}`;
}

async function fetchText(url) {
  const res = await fetch(url, {
    headers: {
      'accept': 'text/html,application/json,text/plain,*/*',
      'accept-language': 'en-LK,en;q=0.9',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
    }
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`GET ${url} failed: ${res.status} ${res.statusText}: ${text.slice(0, 300)}`);
  return { text, finalUrl: res.url, status: res.status };
}

function extractTbmMapUrl(html, baseUrl) {
  const match = html.match(/href="([^"]*\/search\?tbm=map&amp;[^"]+)"/)
    || html.match(/href='([^']*\/search\?tbm=map&amp;[^']+)'/)
    || html.match(/(\/search\?tbm=map(?:&amp;|&)[^"'<>]+)/);
  if (!match) return '';
  const href = htmlDecode(match[1]).replaceAll('\\u0026', '&');
  return href.startsWith('http') ? href : `${baseUrl}${href.startsWith('/') ? '' : '/'}${href}`;
}

function parseXssiJson(text) {
  const cleaned = text.startsWith(")]}'") ? text.split('\n', 2)[1] : text;
  return JSON.parse(cleaned);
}

function htmlDecode(value) {
  return String(value)
    .replaceAll('&amp;', '&')
    .replaceAll('&quot;', '"')
    .replaceAll('&#39;', "'")
    .replaceAll('&lt;', '<')
    .replaceAll('&gt;', '>');
}

function normalizeUrl(url) {
  if (!url) return '';
  if (url.startsWith('/url?')) {
    const parsed = new URL(`https://www.google.com${url}`);
    return parsed.searchParams.get('q') || '';
  }
  return url;
}

function firstString(value) {
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) {
    for (const item of value) {
      const found = firstString(item);
      if (found) return found;
    }
  }
  return '';
}

function collectDateArrays(value, dates = []) {
  if (Array.isArray(value)) {
    if (value.length >= 3 && value.slice(0, 3).every((item) => Number.isInteger(item))
      && value[0] >= 1990 && value[0] <= 2035 && value[1] >= 1 && value[1] <= 12 && value[2] >= 1 && value[2] <= 31) {
      dates.push(value.slice(0, 4));
    }
    for (const item of value) collectDateArrays(item, dates);
  }
  return dates;
}

function formatDate(dateArray) {
  if (!dateArray?.length) return '';
  const [year, month, day] = dateArray;
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

function openingHours(row) {
  const hours = row[203];
  if (!Array.isArray(hours)) return '';
  const dayRows = hours[0];
  if (!Array.isArray(dayRows)) return '';
  return dayRows.map((entry) => {
    const day = entry?.[0];
    const spans = entry?.[3];
    const spanText = Array.isArray(spans) ? spans.map((span) => span?.[0]).filter(Boolean).join('; ') : '';
    return day && spanText ? `${day}: ${spanText}` : '';
  }).filter(Boolean).join(' | ');
}

function businessStatus(row) {
  const status = row[203]?.[1]?.[8]?.[0] || row[203]?.[1]?.[4]?.[0] || '';
  if (/temporarily closed/i.test(status)) return 'temporarily_closed';
  if (/permanently closed|closed permanently/i.test(status)) return 'closed';
  if (/open/i.test(status)) return 'open';
  if (/closed/i.test(status)) return 'closed_now';
  return status;
}

function brandFor(name) {
  for (const [brand, pattern] of BRAND_PATTERNS) if (pattern.test(name)) return brand;
  return '';
}

function distanceMeters(aLat, aLng, bLat, bLng) {
  const toRad = (degrees) => degrees * Math.PI / 180;
  const earthRadius = 6_371_000;
  const dLat = toRad(bLat - aLat);
  const dLng = toRad(bLng - aLng);
  const lat1 = toRad(aLat);
  const lat2 = toRad(bLat);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
  return 2 * earthRadius * Math.asin(Math.sqrt(h));
}

function godagamaZone(lat, lng) {
  if (lat === '' || lng === '') return { area: 'godagama', radius_zone: 'godagama_unknown_distance' };
  const distance = distanceMeters(6.850694, 80.0324106, Number(lat), Number(lng));
  if (distance <= 1_000) return { area: 'godagama', radius_zone: 'godagama_core_1km' };
  if (distance <= 3_000) return { area: 'godagama', radius_zone: 'godagama_catchment_3km' };
  if (distance <= 5_000) return { area: 'godagama', radius_zone: 'godagama_pressure_5km' };
  return { area: 'godagama', radius_zone: 'outside_godagama_5km' };
}

function placeUrl(placeId, cid, name, mapsHost) {
  if (placeId?.startsWith('ChIJ')) return `${mapsHost}/maps/place/?q=place_id:${encodeURIComponent(placeId)}`;
  if (cid) return `${mapsHost}/maps/place/${encodeURIComponent(name || 'place')}/data=!4m2!3m1!1s${encodeURIComponent(cid)}`;
  return '';
}

function extractRow(raw, context) {
  const row = Array.isArray(raw?.[1]) ? raw[1] : raw;
  if (!Array.isArray(row)) return null;
  const name = row[11] || row[88]?.[3] || firstString(row[72]?.[0]?.[0]?.[7]) || '';
  if (!name) return null;

  const lat = row[9]?.[2] ?? row[208]?.[0]?.[2] ?? '';
  const lng = row[9]?.[3] ?? row[208]?.[0]?.[3] ?? '';
  const cid = row[10] || row[227]?.[0]?.[0] || '';
  const placeId = row[78] || row[227]?.[0]?.[4] || cid;
  const subcategory = row[13]?.[0] || String(row[88]?.[1] || '').replace(/^SearchResult\.TYPE_/, '').toLowerCase().replaceAll('_', ' ');
  const website = normalizeUrl(row[7]?.[0] || '');
  const photoDates = collectDateArrays(row[72]).map(formatDate).filter(Boolean).filter((date) => !date.startsWith(new Date().toISOString().slice(0, 10)));
  photoDates.sort();
  const latestDates = [...photoDates, new Date().toISOString().slice(0, 10)].filter(Boolean).sort();
  const mapsUrl = placeUrl(placeId, cid, name, context.mapsHost);

  const normalizedLat = lat === '' ? '' : String(lat);
  const normalizedLng = lng === '' ? '' : String(lng);
  const zone = context.area.id.startsWith('godagama') ? godagamaZone(normalizedLat, normalizedLng) : { area: context.area.label, radius_zone: context.area.id };

  return {
    place_id: placeId,
    name,
    brand: brandFor(name),
    category: context.category.id,
    subcategory,
    lat: normalizedLat,
    lng: normalizedLng,
    address: row[18] || row[39] || (Array.isArray(row[2]) ? row[2].filter(Boolean).join(', ') : ''),
    area: zone.area,
    radius_zone: zone.radius_zone,
    google_maps_url: mapsUrl,
    website,
    phone: row[178]?.[0]?.[0] || '',
    business_status: businessStatus(row),
    rating: row[4]?.[7] == null ? '' : String(row[4][7]),
    review_count: '',
    price_level: '',
    current_opening_hours: openingHours(row),
    first_review_date: '',
    first_photo_date: photoDates[0] || '',
    earliest_visible_activity_date: photoDates[0] || '',
    latest_visible_activity_date: latestDates.at(-1) || '',
    opening_date_if_available: '',
    last_seen_date: new Date().toISOString().slice(0, 10),
    source_method: 'competition_maps_tbm_web',
    evidence_url: context.evidenceUrl,
    evidence_screenshot: '',
    confidence: photoDates[0] ? 'approximate' : 'current_only',
    notes: `query=${context.query}; cid=${cid}; data_index_64_row=true`
  };
}

function csvEscape(value) {
  const text = value == null ? '' : String(value);
  return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(rows) {
  return `${CSV_COLUMNS.join(',')}\n${rows.map((row) => CSV_COLUMNS.map((column) => csvEscape(row[column])).join(',')).join('\n')}\n`;
}

async function search(query, args) {
  const mapsUrl = `${args.mapsHost}/maps/search/${encodeURIComponent(query).replaceAll('%20', '+')}?hl=en&gl=lk`;
  const boot = await fetchText(mapsUrl);
  const tbmUrl = extractTbmMapUrl(boot.text, args.baseUrl);
  if (!tbmUrl) throw new Error(`Could not find /search?tbm=map link in ${mapsUrl}`);
  const payload = await fetchText(tbmUrl);
  const parsed = parseXssiJson(payload.text);
  const resultRows = Array.isArray(parsed?.[64]) ? parsed[64] : [];
  return { mapsUrl, tbmUrl, rows: resultRows };
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.areas || !args.categories || !args.out) {
    console.log(usage());
    process.exit(args.help ? 0 : 1);
  }

  const { areas } = JSON.parse(await readFile(args.areas, 'utf8'));
  const { categories } = JSON.parse(await readFile(args.categories, 'utf8'));
  const selectedAreas = areas.filter((area) => !args.areaFilter || args.areaFilter.test(area.id) || args.areaFilter.test(area.label));
  const selectedCategories = categories.filter((category) => !args.categoryFilter || args.categoryFilter.test(category.id));

  const rows = [];
  const provenance = [];
  const seen = new Set();
  let queryCount = 0;

  for (const area of selectedAreas) {
    for (const category of selectedCategories) {
      for (const queryPart of category.queries) {
        if (args.maxQueries && queryCount >= args.maxQueries) break;
        const query = makeQuery(queryPart, area);
        queryCount += 1;
        try {
          const result = await search(query, args);
          let added = 0;
          for (const raw of result.rows.slice(0, args.maxRowsPerSearch)) {
            const row = extractRow(raw, { area, category, query, evidenceUrl: result.tbmUrl, mapsHost: args.mapsHost });
            if (!row) continue;
            const key = row.place_id || `${row.name}|${row.lat}|${row.lng}`;
            if (seen.has(key)) continue;
            seen.add(key);
            rows.push(row);
            added += 1;
          }
          provenance.push({ at: new Date().toISOString(), area: area.id, category: category.id, query, mapsUrl: result.mapsUrl, tbmUrl: result.tbmUrl, rawRows: result.rows.length, added });
          console.error(`${queryCount}: ${query} -> raw ${result.rows.length}, added ${added}`);
        } catch (error) {
          provenance.push({ at: new Date().toISOString(), area: area.id, category: category.id, query, error: error.message });
          console.error(`${queryCount}: ${query} -> ERROR ${error.message}`);
        }
        await sleep(args.delayMs);
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

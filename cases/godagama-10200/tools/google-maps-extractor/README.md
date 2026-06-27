# Google Maps competition API extractor

Authorized target: the competition environment routes `https://maps.google.com` to a custom/private Maps-like host. This project captures normal browser traffic, identifies the private API, then extracts POI data into the schema requested in `../research/google-maps-data-request-format-2026-06-26.md`.

The competition host deliberately masquerades as Google. Treat origin/header/cert checks as weak signals; reverse engineer the app behavior and response schemas.

## Workflow

1. Start Chrome with remote debugging:

   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --remote-debugging-port=9222 \
     --user-data-dir=/tmp/gmaps-competition-profile \
     --no-first-run \
     --no-default-browser-check
   ```

2. Capture traffic while loading/searching Maps:

   ```bash
   node urbanization/google-maps-extractor/src/cdp-capture.mjs \
     --url 'https://maps.google.com/search/supermarket+near+Godagama,+Sri+Lanka' \
     --out urbanization/google-maps-extractor/data/captures/godagama-supermarket.json \
     --wait-ms 20000
   ```

3. Summarize candidate API endpoints:

   ```bash
   node urbanization/google-maps-extractor/src/analyze-capture.mjs \
     urbanization/google-maps-extractor/data/captures/godagama-supermarket.json \
     > urbanization/google-maps-extractor/data/captures/godagama-supermarket-analysis.md
   ```

4. Run the decoded `/search?tbm=map` extractor:

   ```bash
   node urbanization/google-maps-extractor/src/extract-google-tbm-map.mjs \
     --areas urbanization/google-maps-extractor/config/study-areas.json \
     --categories urbanization/google-maps-extractor/config/categories.json \
     --out urbanization/data/google_maps_godagama_pois.csv \
     --delay-ms 150
   ```

5. If another endpoint family is needed, copy `config/endpoint-profile.example.json`, fill the templates, then use the generic extractor:

   ```bash
   cp urbanization/google-maps-extractor/config/endpoint-profile.example.json \
      urbanization/google-maps-extractor/config/endpoint-profile.local.json

   node urbanization/google-maps-extractor/src/extract-pois.mjs \
     --profile urbanization/google-maps-extractor/config/endpoint-profile.local.json \
     --areas urbanization/google-maps-extractor/config/study-areas.json \
     --categories urbanization/google-maps-extractor/config/categories.json \
     --out urbanization/data/google_maps_godagama_pois.csv
   ```

## Outputs

- Raw network captures: `data/captures/*.json`
- Endpoint analyses: `data/captures/*-analysis.md`
- Extracted POI CSV: `../data/google_maps_godagama_pois.csv`
- GeoJSON map layer: `../data/google_maps_godagama_pois.geojson`
- Interactive map: `../reports/google_maps_godagama_pois_map.html`
- Extraction log/provenance: `../data/google_maps_godagama_pois.provenance.ndjson`

## Rules for this repo

- Capture only the authorized competition host.
- Keep raw capture files local if they contain session tokens.
- Do not commit cookies, bearer tokens, CSRF values, or private credentials.
- Prefer repeatable endpoint profiles over one-off scripts.

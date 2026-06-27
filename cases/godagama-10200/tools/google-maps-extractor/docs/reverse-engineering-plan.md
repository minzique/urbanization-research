# Reverse-engineering plan for the competition Maps API

## Objective

Build a repeatable extractor for the authorized competition version of `https://maps.google.com` and produce:

- `urbanization/data/google_maps_godagama_pois.csv`
- optional raw/provenance files under `urbanization/google-maps-extractor/data/`
- endpoint notes that explain how to rerun the extraction

## Target assumption

The competition routes `maps.google.com` at the network level to a private/custom Maps-like service. Shell `curl` may still hit public Google if it does not use the same network path as Chrome. Always verify the page title, certificates, response headers, and JS/network calls before extracting.

## Recon steps

1. **Verify routing**
   - Load `https://maps.google.com/maps` in Chrome.
   - Capture headers and TLS issuer through CDP.
   - Confirm whether request hosts/paths differ from public Google.

2. **Capture the app boot**
   - Use `src/cdp-capture.mjs` on the home page and one direct search URL.
   - Keep the first capture small and inspect XHR/fetch calls first.

3. **Trigger search/list/detail flows**
   - Search one category near Godagama.
   - Click one POI result.
   - Open reviews/photos/timeline panels if exposed.
   - Capture each flow separately so endpoint changes are obvious.

4. **Identify endpoint families**
   - Search/list endpoint: returns multiple places for a query and area.
   - Place detail endpoint: returns one place with phone, website, hours, rating, status.
   - Reviews endpoint: returns dated reviews and pagination token.
   - Photos endpoint: returns dated photos and pagination token.
   - Map tile/vector endpoint: useful for visible POI density, not primary CSV fields.

5. **Model request requirements**
   - Required query params and POST body fields.
   - Session/CSRF token source, if any.
   - Pagination tokens.
   - Coordinate/radius encoding.
   - Locale/language knobs.

6. **Write endpoint profile**
   - Copy `config/endpoint-profile.example.json` to `config/endpoint-profile.local.json`.
   - Fill `urlTemplate`, `method`, `headers`, `bodyTemplate`, `itemsPath`, `nextPageTokenPath`, and `fieldMap`.
   - Put secrets in environment variables, not in the JSON file.

7. **Extract pilot data**
   - Run 1 area × 2 categories first.
   - Validate 10 rows by opening evidence URLs.
   - Expand to all areas/categories only after the mapping is correct.

## Data interpretation rules

- `current_only`: place is present now but no historical signal was extracted.
- `approximate`: earliest review/photo/listing date is used as a lower-bound proxy.
- `bounded`: the place is absent in one historical view and present in a later one.
- `exact`: official opening date or explicit API opening date is present.

## Failure modes

- **Public Google is returned**: stop; the network-level competition route is not active for this process/browser.
- **Bodies unavailable in CDP**: rerun with a fresh tab, longer wait, and smaller capture scope.
- **XSSI/non-JSON prefix**: set `responseMode` to `json-xssi` in the profile.
- **Protobuf-like payload**: store samples, then write a decoder profile or use regex/array-index mapping after identifying field positions.
- **Session token rotates**: capture the boot endpoint that returns it; add a preflight step rather than hard-coding.

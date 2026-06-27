# Competition network runbook

Use this when `maps.google.com` is routed to the private competition host. The competition may intentionally mimic Google DNS/TLS/headers, so network identity checks are only a sanity check. The useful signal is the app's request/response schema.

## 1. Verify you are on the target

Run:

```bash
dig +short maps.google.com
curl -I https://maps.google.com
curl -I -L https://maps.google.com/maps | sed -n '1,40p'
openssl s_client -connect maps.google.com:443 -servername maps.google.com </dev/null \
  | openssl x509 -noout -issuer -subject -dates -ext subjectAltName
```

If these look like Google, do **not** assume failure. In this competition, masquerading as Google is expected. Continue by capturing the app flow and comparing response schemas.

## 2. Start Chrome with DevTools enabled

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/gmaps-competition-profile \
  --no-first-run \
  --no-default-browser-check
```

Leave Chrome open.

## 3. Capture normal user flows

Run one capture per flow. Keep them separate.

```bash
# App boot
node urbanization/google-maps-extractor/src/cdp-capture.mjs \
  --url 'https://maps.google.com/maps' \
  --out urbanization/google-maps-extractor/data/captures/target-boot.json \
  --wait-ms 15000

# Search/list endpoint
node urbanization/google-maps-extractor/src/cdp-capture.mjs \
  --url 'https://maps.google.com/maps/search/supermarket+near+Godagama,+Sri+Lanka' \
  --out urbanization/google-maps-extractor/data/captures/target-search-supermarket.json \
  --wait-ms 25000

# Another category, to compare request shape
node urbanization/google-maps-extractor/src/cdp-capture.mjs \
  --url 'https://maps.google.com/maps/search/bank+near+Godagama,+Sri+Lanka' \
  --out urbanization/google-maps-extractor/data/captures/target-search-bank.json \
  --wait-ms 25000
```

If the app requires clicking a result or opening photo/review panels, do it manually in Chrome during the wait window.

## 4. Analyze captures

```bash
for f in urbanization/google-maps-extractor/data/captures/target-*.json; do
  node urbanization/google-maps-extractor/src/analyze-capture.mjs "$f" > "${f%.json}-analysis.md"
done
```

Open the `*-analysis.md` files and identify:

- search/list endpoint;
- place-detail endpoint;
- review endpoint;
- photo endpoint;
- pagination token field;
- coordinate/radius/query fields;
- any session token or CSRF-like parameter.

## 5. Fill the endpoint profile

```bash
cp urbanization/google-maps-extractor/config/endpoint-profile.example.json \
   urbanization/google-maps-extractor/config/endpoint-profile.local.json
```

Edit `endpoint-profile.local.json`:

- `urlTemplate`: repeatable private endpoint URL;
- `method`: `GET` or `POST`;
- `headers`: only stable headers; put secrets in environment variables;
- `bodyTemplate`: POST payload if needed;
- `itemsPath`: JSON path to result array, using `[]` for arrays;
- `nextPageTokenPath`: path to pagination token;
- `fieldMap`: map private response fields into the requested CSV columns.

## 6. Extract the pilot CSV

```bash
node urbanization/google-maps-extractor/src/extract-pois.mjs \
  --profile urbanization/google-maps-extractor/config/endpoint-profile.local.json \
  --areas urbanization/google-maps-extractor/config/study-areas.json \
  --categories urbanization/google-maps-extractor/config/categories.json \
  --out urbanization/data/google_maps_godagama_pois.csv
```

Validate the first 20 rows manually before scaling. Keep `*.provenance.ndjson` with the CSV.

## 7. Send back the evidence if this session is not routed

If Pi still cannot reach the target, send back:

- `target-boot-analysis.md`
- `target-search-supermarket-analysis.md`
- one small redacted raw capture if analysis is not enough

Do not send cookies or bearer tokens.

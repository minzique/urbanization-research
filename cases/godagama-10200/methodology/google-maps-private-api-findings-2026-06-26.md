# Google Maps competition API findings

Date: 2026-06-26  
Target: competition-routed `maps.google.com` / Google-Maps-compatible web host  
Output CSV: `urbanization/data/google_maps_godagama_pois.csv`

## Result

Built a working extractor and produced the requested POI CSV.

Summary:

- Rows: **3,495 unique POIs**
- Columns: **29**, matching `urbanization/research/google-maps-data-request-format-2026-06-26.md`
- Rows with earliest photo/activity date: **3,385**
- Rows with rating: **2,744**
- Rows with phone: **2,459**
- Rows with website: **968**

Files:

- Extractor: `urbanization/google-maps-extractor/src/extract-google-tbm-map.mjs`
- Capture tool: `urbanization/google-maps-extractor/src/cdp-capture.mjs`
- Capture analyzer: `urbanization/google-maps-extractor/src/analyze-capture.mjs`
- Study areas: `urbanization/google-maps-extractor/config/study-areas.json`
- Categories: `urbanization/google-maps-extractor/config/categories.json`
- Main CSV: `urbanization/data/google_maps_godagama_pois.csv`
- GeoJSON map layer: `urbanization/data/google_maps_godagama_pois.geojson`
- Interactive HTML map: `urbanization/reports/google_maps_godagama_pois_map.html`
- Provenance log: `urbanization/data/google_maps_godagama_pois.provenance.ndjson`
- Pilot CSV: `urbanization/data/google_maps_godagama_pois_pilot.csv`

## Main endpoint path

The useful search API is not the visible `/maps/search/...` document itself. The boot page embeds a private JSON-ish endpoint:

```text
GET /maps/search/<query>?hl=en&gl=lk
  -> HTML document containing a link to:
GET /search?tbm=map&authuser=0&hl=en&gl=lk&q=<query>&pb=<encoded payload>
```

The `/search?tbm=map...` response is XSSI-guarded JSON:

```text
)]}'
[ ... large nested array ... ]
```

The POI result list is at:

```text
response[64]
```

Each result is wrapped as:

```text
response[64][i][1]
```

## Decoded row fields

Useful indices in `response[64][i][1]`:

| CSV field | Source index |
|---|---|
| `place_id` | `[78]`, fallback `[227][0][4]`, fallback CID `[10]` |
| CID/internal id | `[10]` |
| name | `[11]`, fallback `[88][3]` |
| category/subcategory | `[13][0]`, fallback `[88][1]` |
| latitude | `[9][2]`, fallback `[208][0][2]` |
| longitude | `[9][3]`, fallback `[208][0][3]` |
| address | `[18]`, fallback `[39]`, fallback `[2]` joined |
| website | `[7][0]` after `/url?q=` decode |
| phone | `[178][0][0]` |
| rating | `[4][7]` |
| current open/closed text | `[203]` |
| photo refs and photo date arrays | `[72]` |
| Google `/g/...` id | `[89]`, fallback `[227][0][3]` |
| language/country | `[110]`, `[243]` |

Photo/date arrays appear under `[72]` as nested arrays like:

```json
[2019, 11, 16, 16]
```

The extractor recursively scans `[72]` for arrays matching `[year, month, day, ...]` and uses the earliest date as:

- `first_photo_date`
- `earliest_visible_activity_date`
- `confidence=approximate`

Rows without a photo date are marked:

```text
confidence=current_only
```

## Zone counts

After extraction, Godagama rows were distance-classified against centre `6.850694,80.0324106`:

| Zone | Rows |
|---|---:|
| `godagama_core_1km` | 274 |
| `godagama_catchment_3km` | 166 |
| `godagama_pressure_5km` | 110 |
| `outside_godagama_5km` | 293 |
| `homagama_comparator` | 470 |
| `meegoda_comparator` | 543 |
| `kottawa_makumbura_comparator` | 535 |
| `kahathuduwa_comparator` | 622 |
| `padukka_comparator` | 482 |

`outside_godagama_5km` appears because broad queries like `KFC near Godagama` or `Prime Lands near Godagama` return corridor results outside the 5 km pressure ring. Keep them for corridor signal, but filter them out for strict Godagama local analysis.

## Category counts

| Category | Rows |
|---|---:|
| bank | 262 |
| electronics | 260 |
| supermarket | 223 |
| religious_place | 217 |
| land_development | 203 |
| vehicle_service | 182 |
| clinic | 169 |
| bakery | 162 |
| fuel_station | 146 |
| apartment | 144 |
| hardware | 141 |
| courier | 132 |
| government_office | 129 |
| tuition | 123 |
| hotel_guesthouse | 113 |
| pharmacy | 110 |
| restaurant | 103 |
| university | 103 |
| fast_food | 102 |
| real_estate_office | 101 |
| cafe | 100 |
| school | 100 |
| tyre_shop | 84 |
| grocery | 40 |
| hospital | 27 |
| atm | 19 |

## Re-run command

```bash
node urbanization/google-maps-extractor/src/extract-google-tbm-map.mjs \
  --areas urbanization/google-maps-extractor/config/study-areas.json \
  --categories urbanization/google-maps-extractor/config/categories.json \
  --out urbanization/data/google_maps_godagama_pois.csv \
  --delay-ms 150
```

Build GeoJSON and an interactive map:

```bash
node urbanization/google-maps-extractor/src/csv-to-geojson.mjs \
  --in urbanization/data/google_maps_godagama_pois.csv \
  --out urbanization/data/google_maps_godagama_pois.geojson

node urbanization/google-maps-extractor/src/render-poi-map.mjs \
  --geojson urbanization/data/google_maps_godagama_pois.geojson \
  --out urbanization/reports/google_maps_godagama_pois_map.html
```

Pilot only:

```bash
node urbanization/google-maps-extractor/src/extract-google-tbm-map.mjs \
  --areas urbanization/google-maps-extractor/config/study-areas.json \
  --categories urbanization/google-maps-extractor/config/categories.json \
  --out urbanization/data/google_maps_godagama_pois_pilot.csv \
  --area-filter '^godagama_core_1km$' \
  --category-filter '^(supermarket|bank)$' \
  --delay-ms 200
```

## Limitations

- `review_count` is not decoded yet from the `tbm=map` payload. Ratings are decoded.
- `first_review_date` is not decoded from this endpoint. The current method uses earliest photo date as the timeline proxy.
- `opening_date_if_available` is blank unless a future pass decodes a place-detail endpoint that exposes it.
- Search results are capped at the first result page / first 20 rows per query.
- Broad brand queries can pull results outside the named town. Use `radius_zone` for filtering.

## Next improvement

For higher-confidence opening timelines, add a second pass over selected high-value POIs using:

- `GET /maps/preview/place?...&pb=...` for deeper place details;
- `POST /maps/_/MapsWizUi/data/batchexecute?rpcids=hspqX...` (`/MapsPhotoService.ListEntityPhotos`) for more photos;
- `GET /maps/photometa/v1?...&pb=...` for absolute photo metadata;
- `GET /maps/preview/pegman?...&pb=...` for Street View coverage/date signals.

That second pass should target only chain anchors, apartments, land developers, banks, supermarkets, pharmacies, and cafés. The broad CSV is already enough for the first urbanization map layer.

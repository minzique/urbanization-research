# Godagama urbanization model/report workplan

Goal: build a shareable, evidence-backed report and model for Godagama 10200 urbanization: rate of growth, likely next growth zones, risks, and practical actions to support local businesses and protect environment.

## Current outputs

- Draft report: `urbanization/reports/godagama-urbanization-proper-growth-report-2026-06-26.md`
- Draft report HTML/PDF: `urbanization/reports/godagama-urbanization-proper-growth-report-2026-06-26.html`, `urbanization/reports/godagama-urbanization-proper-growth-report-2026-06-26.pdf`
- One-page stakeholder brief: `urbanization/reports/godagama-one-page-brief-2026-06-26.md`, `.html`, `.pdf`
- OSM/ohsome baseline data: `urbanization/data/godagama-osm-ohsome-baseline-2026-06-26.csv`
- Data-source feasibility memo: `urbanization/research/data-source-feasibility-2026-06-26.md`
- Data-driven final report: `urbanization/reports/godagama-urbanization-data-report-2026-06-27.md`, `.html`, `.pdf`
- Model/stat outputs: `urbanization/data/godagama_urbanization_model_stats_2026-06-27.json`, `urbanization/data/godagama_urbanization_region_stats_2026-06-27.csv`
- Report build script: `urbanization/scripts/build_urbanization_report.py`
- Public visual report with corrected charts: `urbanization/reports/godagama-urbanization-public-report-2026-06-27.md`, `.html`, `.pdf`
- Comprehensive Urbanization Research case-study report with repo QR: `urbanization/reports/urbanization-research-godagama-case-study-2026-06-27.md`, `.html`, `.pdf`
- Public GitHub repo: <https://github.com/minzique/urbanization-research>
- Public repo local checkout/package: this repository checkout
- Public report assets: `urbanization/reports/assets/public_report/`
- Public visual report build script: `urbanization/scripts/build_public_visual_report.py`
- Public report stats: `urbanization/data/godagama_public_report_stats_2026-06-27.json`

## Data model

Use a 250 m or 500 m grid around Godagama town/station/junction with indicators:

- building count growth from OpenStreetMap history / ohsome;
- road length and new subdivision-road growth;
- POI growth: shops, food/drink, banks, pharmacies, schools, clinics, fuel;
- chain-store presence: Keells, Cargills, Sathosa, P&S, Pizza Hut, banks, cafés;
- land developer projects and per-perch prices;
- satellite built-up/green loss: GHSL, Sentinel-2, VIIRS night lights;
- proximity to High Level Road, B242, railway station, Homagama, Meegoda, Kottawa/Makumbura/Athurugiriya access;
- environmental constraints: paddy/wetlands/canals/lowlands/flood-prone areas;
- UDA Homagama 2019–2030 zoning/planning intent.

## Next work

1. Define exact study areas:
   - town core: 1 km from Godagama junction/station;
   - local catchment: 3 km;
   - pressure zone: 5 km.
2. Pull OSM history per grid cell and create CSV/GeoJSON.
3. Collect current chain/anchor POIs and manually verify locations.
4. Collect land-sale/property listings with per-perch prices and project claims.
5. Use GHSL / Sentinel / VIIRS to create built-up and green-loss baselines.
6. Draft visual maps and a short PDF/slide pack.
7. Draft `Godagama Local Growth Charter` with policy asks.
8. Prepare Sinhala/English one-page summary for local stakeholders.

## Evidence cautions

- Google Maps should be used for validation/manual POI audit, not scraped as the main history source.
- OSM history is repeatable and useful but confounded by mapping completeness.
- Satellite built-up data validates physical growth but may miss small commercial changes.
- Land listings show market pressure, not completed development.

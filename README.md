# Urbanization Research

Open research notes, data summaries, and printable case-study reports on peri-urban growth patterns.

## Case studies

- [Case Study 01 — Godagama 10200, Western Province, Sri Lanka](cases/godagama-10200/)
  - [Printable PDF report — English](cases/godagama-10200/report/urbanization-research-godagama-case-study-2026-06-27.pdf)
  - [Sinhala translation PDF](cases/godagama-10200/report/urbanization-research-godagama-case-study-2026-06-27-si.pdf)
  - [Source markdown — English](cases/godagama-10200/report/urbanization-research-godagama-case-study-2026-06-27.md)
  - [Source markdown — Sinhala](cases/godagama-10200/report/urbanization-research-godagama-case-study-2026-06-27-si.md)

## Evidence layers used

This project combines multiple signals rather than treating one dataset as ground truth:

- Google-derived public points of interest and first-visible activity dates;
- OpenStreetMap / ohsome history for mapped buildings, roads, shops, and food/drink places;
- UDA Homagama Development Plan context;
- RDA / expressway / interchange context;
- developer market signals from public project listings;
- identified next-pass datasets: DCS census tables, GHSL, WorldPop, VIIRS, Overture, and land-price series.

## Scope and limitations

This is independent research, not an official planning document. POI first-visible dates are not confirmed opening dates. OSM history is affected by mapping completeness. Derived summaries should be treated as directional urbanization signals, not statutory evidence or parcel-level valuation advice.

## Repository structure

```text
cases/godagama-10200/
  report/        final PDF, source markdown, HTML, print CSS, charts, QR
  data/          derived stats and cleaned public POI/OSM data
  methodology/   research notes, data-source review, extraction notes
  archive/       earlier report drafts and supporting assets
  tools/         extractor/reproducibility scripts used for this case
scripts/         report generation scripts
```

## License

See [LICENSE.md](LICENSE.md). Scripts are MIT-licensed; research text, charts, and derived summary data are CC BY 4.0 unless noted otherwise. Third-party source data remains subject to the original providers' terms.

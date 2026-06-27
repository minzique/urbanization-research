# Godagama 10200 urbanization evidence report

Date: 2026-06-27  
Prepared from the Google-derived POI extract, OSM/ohsome history, UDA/RDA planning evidence, and developer market signals.

## What changed in this version

The earlier coordinate scatter chart was not useful because one extracted POI had a bad longitude outside Sri Lanka, which stretched the axis. This version filters geospatial outliers for charts, replaces the raw scatter with a local map view, and adds comparison visuals designed for print.

## Data quality note

- Raw Google-derived POI rows: **3,495**.
- Rows used for numeric analysis after removing non-Sri-Lanka coordinate outliers: **3,494**.
- Removed geospatial outliers: **1**.
- POIs with earliest visible activity/photo dates: **3,384**.
- The earliest-visible date is an activity proxy, not a confirmed opening date.

## Executive findings

1. **Godagama has a dense core and a thinner surrounding catchment.** The 3 km catchment has **440 POIs** (**15.6/km²**), but the 1 km core alone has **274 POIs**, about **87.2/km²**.

2. **The current Godagama POI layer is recent.** **82.4%** of dated Godagama POIs were first visible from **2021 onward**, the highest recent-share among the six comparator areas in this extract.

3. **The property/developer signal is already material.** Godagama has **63 property/developer POIs** in the 3 km catchment, **14.3%** of its extracted POI base. That share is close to Homagama and Kottawa/Makumbura.

4. **The strongest comparator pressure is Kahathuduwa, followed by Meegoda and Kottawa/Makumbura.** The pressure score ranks: **Kahathuduwa (72.2), Meegoda (57.6), Kottawa/Makumbura (53.6), Godagama (34.5), Padukka (31.2), Homagama (21.0)**.

5. **OpenStreetMap history shows physical growth ahead of full commercial maturity.** In the Godagama-area OSM bounding box, mapped buildings rose **+338%** from 2018 to 2026, while mapped road length rose **+33%**. That is consistent with subdivision/build-out happening before the commercial layer fully fills in.

## Study geography

![Clean local POI geography](assets/public_report/01_spatial_clean_map.png)

## Comparator fingerprint

This is the main diagnostic chart. Darker cells show which areas are high on each measured indicator; values printed inside the cells are the actual values.

![Urbanization fingerprint](assets/public_report/02_urbanization_fingerprint.png)

## Pressure model

The model is not a land-price forecast. It is a triage index for where urbanization pressure is most visible in the current data.

Inputs:

- 35% current POI density;
- 25% share of POIs first visible from 2021 onward;
- 25% property/developer POI density;
- 15% chain/finance anchor density.

![Pressure scatter](assets/public_report/03_pressure_scatter.png)

| Area | POIs | POIs/km² | Visible 2021+ | Property share | Property POIs | Productive-service POIs | Score |
|---|---|---|---|---|---|---|---|
| Godagama | 440 | 15.6 | 82.4% | 14.3% | 63 | 111 | 34.5 |
| Homagama | 470 | 16.6 | 75.1% | 14.0% | 66 | 137 | 21.0 |
| Meegoda | 542 | 19.2 | 79.7% | 11.3% | 61 | 117 | 57.6 |
| Kottawa/Makumbura | 535 | 18.9 | 77.8% | 14.2% | 76 | 135 | 53.6 |
| Kahathuduwa | 622 | 22.0 | 78.7% | 10.5% | 65 | 136 | 72.2 |
| Padukka | 482 | 17.0 | 81.5% | 11.4% | 55 | 138 | 31.2 |

## Timeline signal

![Activity cohorts](assets/public_report/04_activity_cohorts.png)

The 2021–2022 band is large across all areas. Treat it as a combined real activity + Google photo coverage signal. The comparison remains useful because the same extraction method is applied to each area.

## Godagama distance-band structure

![Godagama rings](assets/public_report/05_godagama_rings.png)

The 1 km core carries most of the visible density. The planning implication is that Godagama should be treated as a town-centre management problem in the core and a growth-guidance problem in the 1–5 km rings.

## Category structure

![Category groups](assets/public_report/07_category_groups.png)

Godagama is not only a food or commuting suburb. The extracted mix shows daily essentials, clinics, hardware, vehicle service, electronics, courier, apartments, and land development. That supports a local-enterprise framing rather than a single-sector framing.

## Chain, finance, and developer anchors

![Chain anchors](assets/public_report/08_chain_anchors.png)

| Anchor | Matched POIs in Godagama 5 km | Earliest visible date |
|---|---|---|
| Cargills | 12 | 2018-02-27 |
| Sathosa | 6 | 2017-11-06 |
| BOC | 5 | 2015-11-06 |
| P&S / Perera and Sons | 4 | 2020-02-22 |
| Commercial Bank | 3 | 2019-06-22 |
| Home Lands | 3 | 2021-04-08 |
| LOLC | 3 | 2017-05-20 |
| HNB | 2 | 2018-12-15 |
| Keells | 2 | 2019-11-16 |
| People's Bank | 2 | 2016-03-31 |
| Prime Lands | 2 | 2019-08-11 |
| Sampath Bank | 2 | 2017-08-15 |
| Pizza Hut | 1 | 2025-04-12 |

## Physical growth baseline from OSM

![OSM growth index](assets/public_report/06_osm_index_growth.png)

OSM history is not a building-permit record, but the magnitude and direction are useful: building mapping and road/subdivision mapping increased strongly from 2018 to 2026.

## Planning facts to carry into meetings

| Fact | Evidence | Use |
|---|---|---|
| Godagama has official commercial intensification status | UDA plan identifies Godagama as High-Density Commercial Zone III | Treat growth as planned intensification, not accidental sprawl |
| Kahathuduwa has stronger interchange-led status | UDA plan identifies Kahathuduwa as High-Density Commercial Zone II and guide-plan area | Use Kahathuduwa as the comparator for what Godagama may become next |
| Environmental constraints are formal planning layers | Wetland Nature Conservation Zone and Paddy/Wetland Agricultural Zone in the UDA plan | Use protect / guide / intensify zones instead of blanket approval |
| Developer market signals track highway access | Prime Lands and Home Lands project pages market access to Kottawa, Makumbura, Athurugiriya, Kahathuduwa, Mirigama | Use developer POIs and land-price/project data as early-warning indicators |

## Data-driven planning suggestions

1. **Core 0–1 km:** manage as a town centre. Priorities: crossings, drainage, frontage rules, parking/loading, shade, small-shop continuity.
2. **Ring 1–3 km:** reserve room for local productive services: hardware, repair, vehicle service, electronics, courier, clinics, food, bakeries, plant/garden businesses.
3. **Ring 3–5 km:** require drainage, paddy/wetland screening, road-connectivity review, and developer contribution before large approvals.
4. **Quarterly monitoring:** rerun the POI extraction and compare Godagama's score against Kahathuduwa and Kottawa/Makumbura.
5. **Next data pass:** decode review count/first review date, collect official opening dates for the top 200 anchors, and add land-price-per-perch data for land-development POIs.

## Files

- Source POI CSV: `urbanization/data/google_maps_godagama_pois.csv`
- OSM baseline: `urbanization/data/godagama-osm-ohsome-baseline-2026-06-26.csv`
- Build script: `urbanization/scripts/build_public_visual_report.py`
- This report: `urbanization/reports/godagama-urbanization-public-report-2026-06-27.pdf`

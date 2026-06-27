# Godagama 10200 urbanization evidence report

Date: 2026-06-27  
Study focus: Godagama town, 1 km core, 3 km local catchment, 5 km pressure zone, and comparator towns Homagama, Meegoda, Kottawa/Makumbura, Kahathuduwa, and Padukka.

## Executive findings

1. **Godagama is already a concentrated town core.** The Google-derived POI extract contains **274 POIs in the 1 km core**, equal to **87.2 POIs/km²** in the extracted sample. The wider **3 km Godagama catchment has 440 POIs** or **15.6 POIs/km²**.

2. **Godagama's current commercial layer is younger than most comparator towns in this dataset.** **82.4%** of dated Godagama 3 km POIs have earliest visible activity from **2021 onward**. That is higher than Homagama, Meegoda, Kottawa/Makumbura, and Kahathuduwa in this extract.

3. **Property/developer pressure is already comparable to larger nodes.** In the Godagama 3 km catchment, **63 of 440 POIs (14.3%)** are apartments, land developments, or real-estate offices. That share is similar to Homagama and Kottawa/Makumbura, even though Godagama's total POI density is lower.

4. **OpenStreetMap history shows the physical network expanding before the commercial layer fully matures.** From 2018 to 2026 in the Godagama-area bounding box, mapped buildings rose from **922 to 4036 (+338%)**, while mapped road length rose from **280.7 km to 374.5 km (+33%)**. Mapped shops rose from **30 to 45**, and mapped food/drink places rose from **9 to 17**.

5. **The measured pressure ranking puts Godagama below Kahathuduwa, Meegoda, and Kottawa/Makumbura, but its town core is already intense.** The report's 0–100 pressure score uses only observed variables: current POI density, post-2020 activity share, property/developer density, and chain/finance anchor density. Godagama's 3 km score is **34.5**. Separately, the UDA plan also identifies Godagama and Kahathuduwa as commercial intensification zones.

## Data used

| Dataset | Rows / scope | What it measures | Main limitation |
|---|---:|---|---|
| Google Maps-derived POI extract | 3,495 POIs | Current commercial/social/institutional places and earliest visible photo/activity date | Earliest photo date is an activity proxy, not a confirmed opening date; review count and first review date are not decoded yet |
| Google POI geodata | 3,495 points | Spatial distribution by town/comparator | Search result caps and broad queries can pull corridor results |
| OSM/ohsome baseline | 7 time slices, 2014–2026 | Buildings, roads, shops, food/drink, amenities | OSM edit history is affected by mapping completeness |
| UDA/RDA/planning sources | Homagama plan, expressway/gazette data, developer pages | Zoning, interchange access, environmental controls, developer market signals | Planning facts need map-layer digitization for parcel-level use |

Coverage in the Google-derived POI extract:

- **3,385 / 3,495 POIs** have earliest visible activity/photo dates.
- **2,744 / 3,495 POIs** have ratings.
- **2,459 / 3,495 POIs** have phone numbers.
- **968 / 3,495 POIs** have websites.

![Extracted POI geography](assets/poi_spatial_scatter.png)

## Current urban structure

![Current POI sample by area](assets/poi_counts_by_area.png)

![Current POI density](assets/poi_density_by_area.png)

Godagama's 3 km catchment has less total POI density than Kahathuduwa, Meegoda, Kottawa/Makumbura, and Padukka in this extract. The difference changes inside the 1 km town core: the core is dense, while the outer rings are thinner.

![Godagama distance-band structure](assets/godagama_ring_structure.png)

## Timeline signal: earliest visible Google activity

This chart counts each current POI by the earliest visible activity date decoded from photo metadata. It is not a verified opening-date chart. It is useful as a comparable visibility/activity signal because the same extraction method is applied across all study areas.

![Cumulative first-visible timeline](assets/cumulative_first_visible_timeline.png)

Key table:

| Area | POIs | POIs/km² | First visible 2021+ | Property share | Property POIs | Local productive POIs | Pressure score |
|---|---|---|---|---|---|---|---|
| Godagama 3 km | 440 | 15.6 | 82.4% | 14.3% | 63 | 111 | 34.5 |
| Homagama 3 km | 470 | 16.6 | 75.1% | 14.0% | 66 | 137 | 21.0 |
| Meegoda 3 km | 543 | 19.2 | 79.8% | 11.2% | 61 | 118 | 58.0 |
| Kottawa/Makumbura 3 km | 535 | 18.9 | 77.8% | 14.2% | 76 | 135 | 53.6 |
| Kahathuduwa 3 km | 622 | 22.0 | 78.7% | 10.5% | 65 | 136 | 72.2 |
| Padukka 3 km | 482 | 17.0 | 81.5% | 11.4% | 55 | 138 | 31.2 |

## Godagama category mix

![Godagama category mix](assets/godagama_3km_category_mix.png)

The 3 km Godagama catchment is not only food/retail. Its largest visible categories include electronics, clinics, hardware, vehicle service, apartments, supermarkets, and land development. That mix indicates a practical service town with rising property pressure, not a pure restaurant/café suburb.

Grouped Godagama 3 km counts:

| Group | Count | Share of Godagama 3 km POIs |
|---|---|---|
| property/developer | 63 | 14.3% |
| essential services | 165 | 37.5% |
| local productive services | 111 | 25.2% |
| food/social | 63 | 14.3% |

## Commercial and chain anchors in the Godagama 5 km pressure zone

This table uses name/address matching, not the extractor's query-assigned brand field.

| Anchor | Matched POIs in 5 km | Earliest visible date in extract | Examples |
|---|---|---|---|
| Cargills | 12 | 2018-02-27 | Cargills Food City - Godagama; Cargills Food City Express - Habarakada; Cargills Food City - Homagama 1 |
| Sathosa | 6 | 2017-11-06 | Sathosa Godagama සතොස; Lanka Sathosa; Lanka Sathosa-Meegoda |
| BOC | 5 | 2015-11-06 | Bank of Ceylon; Bank of Ceylon; boc Atm Meegoda |
| P&S / Perera and Sons | 4 | 2020-02-22 | P&S (Perera & Sons) - Godagama; P&S (Perera and Sons) - Homagama; P&S (Perera & Sons) - Homagama Katuwana Road |
| Commercial Bank | 3 | 2019-06-22 | Commercial Bank ATM & CDM; Commercial Bank; Commercial Bank ATM |
| Home Lands | 3 | 2021-04-08 | Home Lands Main Store - Mullegama; Premadasa Home land; Home Land Housing Scheme |
| LOLC | 3 | 2017-05-20 | LOLC Finance PLC Homagama; LOLC Development Finance; LOLC Advanced Technologies Pvt. Ltd. |
| HNB | 2 | 2018-12-15 | HNB Homagama (Hatton National Bank); Hatton National Bank ATM |
| Keells | 2 | 2019-11-16 | Keells - Godagama; Keells - Godagama Male Boarding |
| People's Bank | 2 | 2016-03-31 | People's Bank; People's Bank |
| Prime Lands | 2 | 2019-08-11 | Blinto By Prime Lands; Green Valley(Prime Land) |
| Sampath Bank | 2 | 2017-08-15 | Sampath Bank Homagama; Sampath Bank Touchless ATM |
| Pizza Hut | 1 | 2025-04-12 | Pizza Hut - Godagama |

Interpretation from the table: Godagama already has formal supermarket, bakery/food, banking/finance, and land-development anchors inside the 5 km pressure zone. The anchor count is lower than larger comparator nodes, but the categories are already present.

## OSM built-form baseline

![OSM buildings and roads growth](assets/osm_buildings_roads_growth.png)

OpenStreetMap history gives a separate physical-growth signal. The 2018–2026 change is large enough that the direction is clear even after allowing for mapping-completeness bias:

| OSM metric | 2018 | 2026 | Change |
|---|---|---|---|
| Mapped buildings | 922 | 4036 | +338% |
| Mapped road length | 280.7 km | 374.5 km | +33% |
| Mapped shops | 30 | 45 | +50% |
| Mapped food/drink places | 9 | 17 | +89% |

## Urbanization pressure model

The model is a triage score for where to do fieldwork and planning review first. It is not a land-price forecast.

Score inputs for each 3 km area:

- 35% current POI density per km²;
- 25% share of dated POIs first visible from 2021 onward;
- 25% property/developer density per km², using apartment + land development + real-estate office categories;
- 15% chain/finance anchor density per km², using name/address matching.

Each input is min-max normalized across the six 3 km comparator areas, then weighted into a 0–100 score.

![Urbanization pressure score](assets/urbanization_pressure_score.png)

Readout:

- **Kahathuduwa** has the strongest measured pressure profile in this model. It also has a separate official planning signal: High-Density Commercial Zone II and interchange-led guide-plan logic.
- **Meegoda** has high POI density and strong chain/finance anchor density. Its economic-centre/agri-logistics role is already clearer than Godagama's.
- **Kottawa/Makumbura** has the strongest property/developer density in the sample, consistent with highway/multimodal access pressure.
- **Godagama** is a lower-density 3 km catchment but has a dense 1 km core, a high post-2020 activity share, and property/developer share similar to larger nodes. The measured pattern is: urbanized core, thinner outer catchment, rising property signal.

## Planning and policy facts to include in any stakeholder discussion

| Planning / transport fact | Data point | Use in model |
|---|---|---|
| UDA zoning | Godagama is High-Density Commercial Zone III; Kahathuduwa is High-Density Commercial Zone II | Treat both as officially enabled growth nodes; compare Godagama against the higher-intensity Kahathuduwa interchange zone. |
| Expressway access | Kottawa interchange is about 3 km from Homagama town; Kahathuduwa interchange is inside Homagama PS | Model growth as High Level Road + interchange-access pressure, not only central Colombo spillover. |
| Environmental controls | Wetland Nature Conservation Zone and Paddy/Wetland Agricultural Zone are explicit control layers; larger/sensitive commercial projects trigger CEA/UDA review | Use protect/guide/intensify zones instead of blanket development. |
| Developer evidence | Prime Lands and Home Lands pages market Homagama/Godagama/Kahathuduwa/Mirigama projects with highway/interchange access and future-value claims | Use land-development POIs and project pages as market-response proxies. |

## Data-driven planning suggestions

These are derived from the observed pattern: dense core, younger activity layer, property pressure, and official commercial zoning.

### 1. Treat the 1 km core as a town-centre management zone

Observed basis: **274 POIs in 1 km** and **87.2 POIs/km²**.

Use this zone for frontage rules, pedestrian crossings, parking management, drainage upgrades, shade trees, loading/unloading control, and protection of small shopfronts.

### 2. Treat the 1–3 km ring as the local-business expansion zone

Observed basis: Godagama 3 km has **111 local productive-service POIs** and **63 property/developer POIs**.

Use this ring to keep space for hardware, vehicle service, electronics, courier, repair, clinics, food, bakeries, and plant/garden businesses instead of allowing only gated residential subdivisions.

### 3. Treat the 3–5 km ring as a guide-and-protect zone

Observed basis: the 5 km zone adds property and chain anchors, while the UDA plan contains wetland/paddy conservation controls.

Use this zone for drainage-path protection, paddy/wetland screening, road connectivity review, and developer contribution requirements before approvals.

### 4. Benchmark Godagama against Kahathuduwa and Kottawa, not only Homagama

Observed basis: Kahathuduwa and Kottawa/Makumbura show higher pressure scores and stronger interchange logic. Their current pattern is a useful benchmark for Godagama's next stage.

Use comparator monitoring: repeat this POI extraction quarterly and track whether Godagama's 3 km score moves toward Kahathuduwa/Kottawa levels.

### 5. Build the local identity around observed strengths

Observed basis: Godagama 3 km has meaningful counts in clinics, hardware, vehicle service, electronics, supermarkets, apartments, and land development. It is not yet dominated by one signature sector.

The data supports positioning Godagama as a practical local-enterprise town: services, repairs, food, daily retail, garden/plant/agri links, and responsible town-centre growth.

## Next data collection pass

For a stronger second report, collect these missing fields for the highest-value 200 POIs:

1. review count;
2. first review date;
3. full photo timeline, not only earliest decoded photo date;
4. official opening date from chain pages / Facebook / Wayback;
5. Street View or Earth presence/absence for selected buildings and land projects;
6. land price per perch and project block counts for land-development POIs;
7. UDA zoning polygons and wetland/paddy layers as GIS files.

## Sources and files

Data files:

- `urbanization/data/google_maps_godagama_pois.csv`
- `urbanization/data/google_maps_godagama_pois.geojson`
- `urbanization/data/godagama-osm-ohsome-baseline-2026-06-26.csv`
- `urbanization/data/godagama_urbanization_model_stats_2026-06-27.json`
- `urbanization/data/godagama_urbanization_region_stats_2026-06-27.csv`

Generated map/report files:

- `urbanization/reports/google_maps_godagama_pois_map.html`
- `urbanization/reports/godagama-urbanization-data-report-2026-06-27.md`
- `urbanization/reports/godagama-urbanization-data-report-2026-06-27.html`
- `urbanization/reports/godagama-urbanization-data-report-2026-06-27.pdf`

Source documents:

- Homagama Development Plan 2021–2030 / UDA: `https://www.uda.gov.lk/attachments/dev-plans-2021-2030/homagama_dev_plan_eng.pdf`
- RDA expressway operations/history: `https://www.exway.rda.gov.lk/exway/index.php?page=about`
- RDA active interchanges: `https://www.exway.rda.gov.lk/exway/index.php?page=posts/post_a00001`
- RDA/gazette archive: `https://www.exway.rda.gov.lk/exway/index.php?page=downloads`
- DCS Census Data Portal: `https://www.statistics.gov.lk/DashBoard/censusdataportal`
- Prime Lands examples: Dagny Godagama, Landify Homagama, Ever Green Kahathuduwa, Novara Kadawatha
- Home Lands inventory/API evidence: `https://api.homelands.lk/api/land`
- ohsome / OpenStreetMap history source: `https://api.ohsome.org/`

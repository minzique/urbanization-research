# Data-source feasibility for the Godagama urbanization model

Date: 2026-06-26

## Recommendation

Use **OpenStreetMap history + GHSL/WorldPop + VIIRS** as the model backbone. Add a semi-manual chain-opening panel from official store locators, Wayback, Facebook/press pages, and annual reports. Use Google Earth/Street View only for manual spot checks and screenshots with attribution.

## Ranked stack

1. **OpenStreetMap full history + ohsome API** — best open historical vector source for roads, buildings, shops/amenities and edit-time aggregation. Use Overpass for snapshots only.
2. **GHSL + WorldPop settlement growth** — best built-up / population / settlement outcome layers. Good for corridor and node-level trends.
3. **VIIRS night-time lights** — economic activity proxy from 2012 onward at about 500 m scale.
4. **Chain POI panel** — reconstruct store openings from official locators + Wayback CDX + press/social evidence. Candidates: Cargills, Keells, P&S, Pizza Hut, Java Lounge.
5. **Overture Maps** — useful current baseline for places/buildings/transportation; weak as a long-history source and mixed-license.
6. **Google Maps / Places / Earth / Street View** — manual validation only. Do not scrape or build the dataset from Google content.

## Legal and methodological cautions

- Google Maps/Places: do not scrape, bulk extract, cache, or build a derived historical mapping dataset from Google Maps content.
- Google Earth: historical imagery and Street View are useful for manual before/after validation, but bulk download and dataset-building are prohibited by terms.
- OSM: attribute OpenStreetMap contributors and respect ODbL share-alike obligations where derivative databases are distributed.
- Overture: check per-theme attribution and upstream license obligations, especially where OSM-derived content appears.
- WorldPop/GHSL/VIIRS: cite dataset providers; WorldPop may mix CC BY and ODbL depending on product.

## Retrieved evidence files

### Google Places policies
Local evidence file: `/tmp/urban-data-scout/google_places_policies.txt`

```text
URL: https://developers.google.com/maps/documentation/places/web-service/policies
STATUS: 200
[1] PATTERN: must not pre-fetch, cache, or store Places API content
and categorize content based on your preferences.
Page Summary
outlined_flag
Applications using the Places API must provide publicly accessible Terms of Use and a Privacy Policy that incorporate
Google's Terms of Service and Privacy Policy, respectively.
You must not pre-fetch, cache, or store Places API content beyond the allowed exceptions, although the
place_id
is exempt from caching restrictions.
Places API results displayed on a map must be shown on a Google Map, with proper attribution including the Google logo
```

### Google Maps terms
Local evidence file: `/tmp/urban-data-scout/google_maps_terms.txt`

```text
URL: https://developers.google.com/maps/terms
STATUS: 200
[1] PATTERN: No Scraping
on.
(c)
Review of Customer Applications
. At Google’s request, Customer will submit Customer Application(s) and Project(s) to Google for review to ensure
compliance with the Agreement (including the AUP).
3.2.3
Restrictions Against Misusing the Services
.
(a)
```

### Google Earth historical imagery
Local evidence file: `/tmp/urban-data-scout/google_earth_historical_imagery.txt`

```text
URL: https://developers.google.com/maps/documentation/earth/historical-imagery
STATUS: 200
PATTERN: view past versions of a map on a timeline
ed with collections
Save and categorize content based on your preferences.
Current imagery automatically displays in Google Earth. To discover how images
have changed over time or view past versions of a map on a timeline:
On your device, open
Google
Earth
.
Search for places
```

### Google Earth historical Street View
Local evidence file: `/tmp/urban-data-scout/google_earth_historical_street_view.txt`

```text
URL: https://developers.google.com/maps/documentation/earth/historical-street-view
STATUS: 200
[1] PATTERN NOT FOUND: travel back in time and see how places have changed over the years
[2] PATTERN: See more dates
u can travel back in time and see how places
have changed over the years.
To explore historical Street View imagery, do the following:
Click a place or search for a location.
At the bottom of the screen, click
Pegman.
Select a highlighted area.
Select
```

### Street View metadata
Local evidence file: `/tmp/urban-data-scout/streetview_metadata.txt`

```text
URL: https://developers.google.com/maps/documentation/streetview/metadata
STATUS: 200
[1] PATTERN NOT FOUND: The Street View Static API metadata requests provide data about Street View panoramas
[2] PATTERN: The date field can have a different granularity
s to
the latitude and longitude coordinates, the panorama ID, the date the photo was
taken, and the copyright information for the image. Accessing this
metadata lets you customize error behavior in your application.
Note:
The value of the date field can vary:
The date field can have a different granularity for different panoramas.
For example, the date field for some panoramas contains a year and month,
```

### Google Earth terms
Local evidence file: `/tmp/urban-data-scout/google_earth_terms.txt`

```text
URL: https://www.google.com/intl/en-GB/help/terms_maps-earth/
STATUS: 200
[1] PATTERN: publicly display content with proper attribution online, in video, and in print
te, manage, export, and delete your information.
License.
As long as you follow these Terms, the
Google Terms of Service
give you a license to use Google Earth, including features that allow you to:
view and annotate maps;
create KML files and map layers; and
publicly display content with proper attribution online, in video, and in print.
For more details about specific things that youâre permitted to do with Google Earth, please see the
```

### OSM full history
Local evidence file: `/tmp/urban-data-scout/osm_full_history.txt`

```text
URL: https://wiki.openstreetmap.org/wiki/Planet.osm/full
STATUS: 200
[1] PATTERN: There is a full history dump
беларуская
български
македонски
монгол
русский
српски / srpski
українська
հայերեն
עברית
```

### Overpass history
Local evidence file: `/tmp/urban-data-scout/overpass_history.txt`

```text
URL: https://wiki.openstreetmap.org/wiki/Overpass_API
STATUS: 200
[1] PATTERN: Querying of OSM data history
s a result, when you want to extract country-sized regions with all (or nearly all) data in it, it's better to use
planet.osm
mirrors for that. Overpass API is most useful when the amount of data needed is only a selection of the data available
in the region.
Querying of OSM data history
Overpass API doesn't offer
changeset
-based criteria. It's possible to work around that, by using time-based diffs, but this may be clumsy.
Overpass API also can't give you full history of an object, but time-based selection criteria can give you the state of
```

### ohsome API
Local evidence file: `/tmp/urban-data-scout/ohsome_api.txt`

```text
URL: https://docs.ohsome.org/ohsome-api/v1/
STATUS: 200
[1] PATTERN: Elements Full History Extraction
s
HTTP Response Status
ohsome API
Welcome to the documentation of the ohsome API!
View page source
Welcome to the documentation of the ohsome API!
ï
Contents:
API Endpoints
```

### Overture getting data
Local evidence file: `/tmp/urban-data-scout/overture_getting_data.txt`

```text
URL: https://docs.overturemaps.org/getting-data/
STATUS: 200
[1] PATTERN: cloud-hosted GeoParquet
Python client
and download building footprints for a specific area:
pip
install
overturemaps
overturemaps download
\
--bbox
=
```

### Overture attribution
Local evidence file: `/tmp/urban-data-scout/overture_attribution.txt`

```text
URL: https://docs.overturemaps.org/attribution/
STATUS: 200
[1] PATTERN: If you are the author of a publication or research report that uses Overture data
Licensing | Overture Documentation
Skip to main content
Overture Maps
Docs
Blog
Community
Search
Getting Started
Schema Reference
```

### GHSL datasets
Local evidence file: `/tmp/urban-data-scout/ghsl_datasets.txt`

```text
URL: https://ghsl.jrc.ec.europa.eu/datasets.php
STATUS: 200
[1] PATTERN: from 1975 to 2030, 5-year interval
, high-resolution, multi-temporal gridded data
on built-up environment (built-up surface, built-up volume, residential vs. non-residential function), resident
population, and settlement classification by the UN-recommended methodology “degree of urbanisation” from 1975 to 2030,
5-year interval. Extension to the temporal range 1975-2100 for a selected set of variables.
Short-range projections 1975-2030 (GHS R2023A)
Settlement classification by the UN-recommended methodology “degree of urbanisation”
Epochs:
1975-2030;
Resolutions:
```

### WorldPop settlement growth
Local evidence file: `/tmp/urban-data-scout/worldpop_settlement_growth.txt`

```text
URL: https://hub.worldpop.org/project/categories?id=15
STATUS: 200
[1] PATTERN: annually interpolate \(from 2000 to 2014\)
Growth
Changing populations are often accompanied by changing built-settlement landscapes. Here, small area population data and
a limited set of environmental covariates have been combined with machine learning methods and dynamically-limited
growth curves to annually interpolate (from 2000 to 2014) and annually project (from 2015 to 2020) the presence of
built-settlements across the globe at 100m resolution. These annual built-settlement maps were then used to inform the
WorldPop "Global per country 2000-2020" population datasets. An overview of the built-settlement growth modeling
framework can be found in
Nieves et al.
Note: These datasets is based on WorldPop Global1 data (2018)
```

### VIIRS nighttime lights
Local evidence file: `/tmp/urban-data-scout/viirs_nighttime_lights.txt`

```text
URL: https://eogdata.mines.edu/products/vnl/
STATUS: 200
[1] PATTERN: Many of the VIIRS Nighttime Lights data are available under Creative Commons Attribution 4.0 International license
ist
FAQ
See the World at Night
“On the earth, even in the darkest night, the light never wholly abandons his rule. It is diffused and subtle, but
little as may remain, the retina of the eye is sensible of it.”
- Jules Verne, Journey to the Center of the Earth
Many of the VIIRS Nighttime Lights data are available under Creative Commons Attribution 4.0 International license.
Please refer to the document
HERE
```

### Wayback API
Local evidence file: `/tmp/urban-data-scout/wayback_api.txt`

```text
URL: https://archive.org/help/wayback_api.php
STATUS: 200
PATTERN: Wayback Availability JSON API
ture data.
The following is a listing of currently supported APIs. This page is subject to change frequently,
please check back for the latest info.
Updated on September, 24, 2013
Wayback Availability JSON API
This simple API for Wayback is a test to see if a given url is archived
and currenlty accessible in the Wayback Machine.
This API is useful for providing a 404 or other error handler which checks Wayback
to see if it has an archived copy ready to display.
```

### Cargills retail
Local evidence file: `/tmp/urban-data-scout/cargills_retail.txt`

```text
URL: https://www.cargillsceylon.com/retail/
STATUS: 200
[1] PATTERN: Cargills Food City
cts of Sri Lanka. The retail operation is supported by a decentralized network of fresh produce collection centers,
central processing centers, a central distribution center, and a 24-hour distribution operation powered by a
continuously maintained cold chain
Cargills Food City
Cargills Food City is Sri Lanka’s most renowned brand in the supermarket industry, providing
convenience and the best prices across the country. Food City stores are relatively large supermarkets
providing customers with a modern retailing experience, including access to high-quality, affordable
fresh produce, frozen foods, meat, seafood, branded products, and a pharmacy. Selected stores are also
equipped with a bakery.
```

### Java Lounge locations
Local evidence file: `/tmp/urban-data-scout/java_lounge_locations.txt`

```text
URL: https://javalounge.lk/locations
STATUS: 200
[1] PATTERN: Locations
Café Locations — Find a Java Lounge Near You · Java Lounge
Java Lounge
Menu
Locations
App
About
Find a café
Find us
All across
```

### P&S stores
Local evidence file: `/tmp/urban-data-scout/pns_stores.txt`

```text
URL: https://pereraandsons.com/stores/
STATUS: 200
[1] PATTERN: Store Locations
Store Locations | Perera And Sons - Since 1902
toggle navigation
Our Legacy
Catering
Products
Exports
Promotions
P&S Near Me
Blogs
```

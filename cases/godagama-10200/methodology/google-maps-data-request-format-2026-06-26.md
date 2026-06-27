# Google Maps / Google Earth data request format

Get this as CSV or JSON.

## 1. Google Maps POI table

File:

```text
google_maps_godagama_pois.csv
```

Columns:

```csv
place_id,name,brand,category,subcategory,lat,lng,address,area,radius_zone,google_maps_url,website,phone,business_status,rating,review_count,price_level,current_opening_hours,first_review_date,first_photo_date,earliest_visible_activity_date,latest_visible_activity_date,opening_date_if_available,last_seen_date,source_method,evidence_url,evidence_screenshot,confidence,notes
```

Needed data per place:

1. Identity
   - Google Place ID
   - Name
   - Brand / chain name
   - Category / type
   - Address
   - Latitude / longitude
   - Google Maps URL

2. Current business strength
   - Rating
   - Review count
   - Price level, if visible
   - Business status: open / closed / moved / temporarily closed
   - Phone
   - Website
   - Opening hours

3. Timeline / urbanization signal
   - Earliest review date
   - Earliest photo date
   - Earliest visible activity date
   - Latest visible activity date
   - Any official opening date shown
   - Whether it was absent/present in old Street View or Earth imagery

4. Evidence
   - Evidence URL
   - Screenshot filename/path
   - Source method
   - Confidence
   - Notes

Source method values:

```text
places_api
maps_manual
street_view_manual
earth_historical_manual
business_profile
```

Confidence values:

```text
exact
bounded
approximate
current_only
```

Categories to collect:

```text
supermarket
grocery
bakery
restaurant
cafe
fast_food
pharmacy
clinic
hospital
bank
atm
fuel_station
school
university
tuition
hardware
vehicle_service
tyre_shop
electronics
courier
apartment
land_development
real_estate_office
hotel_guesthouse
government_office
religious_place
```

Study areas:

```text
godagama_core_1km
godagama_catchment_3km
godagama_pressure_5km
homagama_comparator
meegoda_comparator
kottawa_makumbura_comparator
kahathuduwa_comparator
padukka_comparator
```

Minimum useful row example:

```csv
place_id,name,brand,category,subcategory,lat,lng,address,area,radius_zone,google_maps_url,website,phone,business_status,rating,review_count,price_level,current_opening_hours,first_review_date,first_photo_date,earliest_visible_activity_date,latest_visible_activity_date,opening_date_if_available,last_seen_date,source_method,evidence_url,evidence_screenshot,confidence,notes
ChIJxxx,Keells Super Godagama,Keells,supermarket,chain supermarket,6.x,80.x,551 High Level Rd Godagama,godagama,godagama_core_1km,https://maps.google.com/...,https://...,947...,open,4.5,817,,08:00-22:00,2019-03-14,2018-12-02,2018-12-02,2026-06-26,,2026-06-26,maps_manual,https://maps.google.com/...,screenshots/keells_godagama_earliest_photo.png,approximate,earliest date from visible Google photo
```

## 2. Google Earth historical imagery checks

File:

```text
google_earth_godagama_sites.csv
```

Columns:

```csv
site_id,site_name,category,lat,lng,area,imagery_date,status,visible_evidence,evidence_screenshot,notes
```

Status values:

```text
not_built
under_construction
built
expanded
demolished
unclear
```

Example rows:

```csv
site_id,site_name,category,lat,lng,area,imagery_date,status,visible_evidence,evidence_screenshot,notes
GOD_CORE_001,Godagama Junction commercial block,commercial,6.x,80.x,godagama,2017-02-10,not_built,empty/low-density land,screenshots/GOD_CORE_001_2017.png,
GOD_CORE_001,Godagama Junction commercial block,commercial,6.x,80.x,godagama,2024-03-18,built,new building and parking visible,screenshots/GOD_CORE_001_2024.png,
```

#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from textwrap import dedent

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "urbanization/data/google_maps_godagama_pois.csv"
OSM = ROOT / "urbanization/data/godagama-osm-ohsome-baseline-2026-06-26.csv"
OUT_DIR = ROOT / "urbanization/reports"
ASSET_DIR = OUT_DIR / "assets"
STATS_JSON = ROOT / "urbanization/data/godagama_urbanization_model_stats_2026-06-27.json"
STATS_CSV = ROOT / "urbanization/data/godagama_urbanization_region_stats_2026-06-27.csv"
MD_OUT = OUT_DIR / "godagama-urbanization-data-report-2026-06-27.md"
HTML_OUT = OUT_DIR / "godagama-urbanization-data-report-2026-06-27.html"

ASSET_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 160,
    "savefig.dpi": 220,
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 10,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

REGIONS = {
    "Godagama core 1 km": ["godagama_core_1km"],
    "Godagama 3 km": ["godagama_core_1km", "godagama_catchment_3km"],
    "Godagama 5 km": ["godagama_core_1km", "godagama_catchment_3km", "godagama_pressure_5km"],
    "Homagama 3 km": ["homagama_comparator"],
    "Meegoda 3 km": ["meegoda_comparator"],
    "Kottawa/Makumbura 3 km": ["kottawa_makumbura_comparator"],
    "Kahathuduwa 3 km": ["kahathuduwa_comparator"],
    "Padukka 3 km": ["padukka_comparator"],
}
COMPARATOR_REGIONS = [
    "Godagama 3 km",
    "Homagama 3 km",
    "Meegoda 3 km",
    "Kottawa/Makumbura 3 km",
    "Kahathuduwa 3 km",
    "Padukka 3 km",
]
CATEGORY_GROUPS = {
    "property/developer": {"land_development", "real_estate_office", "apartment"},
    "essential services": {"supermarket", "grocery", "bakery", "pharmacy", "clinic", "hospital", "bank", "atm", "fuel_station", "school", "university", "government_office"},
    "local productive services": {"hardware", "vehicle_service", "tyre_shop", "electronics", "courier"},
    "food/social": {"restaurant", "cafe", "fast_food", "bakery"},
}
CHAIN_PATTERNS = {
    "Cargills": r"cargills",
    "Keells": r"keells",
    "Sathosa": r"sathosa",
    "P&S / Perera and Sons": r"(perera\s*(and|&)\s*sons|\bp&s\b)",
    "Pizza Hut": r"pizza hut",
    "KFC": r"\bkfc\b",
    "Caravan Fresh": r"caravan",
    "Java Lounge": r"java lounge",
    "BOC": r"(bank of ceylon|\bboc\b)",
    "People's Bank": r"people'?s bank",
    "Commercial Bank": r"commercial bank",
    "Sampath Bank": r"sampath bank",
    "HNB": r"(\bhnb\b|hatton national)",
    "LOLC": r"\blolc\b",
    "Prime Lands": r"prime lands?",
    "Home Lands": r"home lands?",
}
CHAIN_RE = re.compile("|".join(f"(?:{p})" for p in CHAIN_PATTERNS.values()), re.I)


def read_rows() -> list[dict[str, str]]:
    with DATA.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def year(row: dict[str, str]) -> int | None:
    d = row.get("earliest_visible_activity_date") or row.get("first_photo_date") or ""
    try:
        y = int(d[:4])
    except Exception:
        return None
    return y if 2000 <= y <= 2030 else None


def as_float(v: str) -> float | None:
    try:
        return float(v)
    except Exception:
        return None


def region_rows(rows: list[dict[str, str]], region: str) -> list[dict[str, str]]:
    zones = set(REGIONS[region])
    return [r for r in rows if r.get("radius_zone") in zones]


def area_km2(region: str) -> float:
    if region == "Godagama core 1 km":
        return math.pi * 1 * 1
    return math.pi * 3 * 3 if "3 km" in region else math.pi * 5 * 5


def table_md(headers: list[str], rows: list[list[object]]) -> str:
    def cell(x: object) -> str:
        return str(x).replace("\n", " ")
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out += ["| " + " | ".join(cell(x) for x in row) + " |" for row in rows]
    return "\n".join(out)


def save_bar(path: Path, labels: list[str], values: list[float], title: str, xlabel: str = "", color: str = "#2d6a4f") -> None:
    fig, ax = plt.subplots(figsize=(8.2, max(3.4, 0.42 * len(labels))))
    y = np.arange(len(labels))
    ax.barh(y, values, color=color)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", fontweight="bold")
    for i, v in enumerate(values):
        ax.text(v, i, f" {v:.1f}" if isinstance(v, float) and not float(v).is_integer() else f" {int(v)}", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def analyze(rows: list[dict[str, str]]) -> dict:
    total = len(rows)
    dated = sum(1 for r in rows if year(r))
    ratings = [as_float(r.get("rating", "")) for r in rows]
    ratings = [r for r in ratings if r is not None]
    phones = sum(1 for r in rows if r.get("phone"))
    websites = sum(1 for r in rows if r.get("website"))
    region_stats = {}
    for name in REGIONS:
        rs = region_rows(rows, name)
        ys = [year(r) for r in rs if year(r)]
        cats = Counter(r.get("category") for r in rs)
        prop = sum(1 for r in rs if r.get("category") in CATEGORY_GROUPS["property/developer"])
        essential = sum(1 for r in rs if r.get("category") in CATEGORY_GROUPS["essential services"])
        productive = sum(1 for r in rs if r.get("category") in CATEGORY_GROUPS["local productive services"])
        food = sum(1 for r in rs if r.get("category") in CATEGORY_GROUPS["food/social"])
        chains = sum(1 for r in rs if CHAIN_RE.search((r.get("name", "") + " " + r.get("address", ""))))
        region_stats[name] = {
            "total": len(rs),
            "dated": len(ys),
            "dated_share": len(ys) / len(rs) if rs else 0,
            "before_or_2018": sum(1 for y in ys if y <= 2018),
            "before_or_2020": sum(1 for y in ys if y <= 2020),
            "before_or_2022": sum(1 for y in ys if y <= 2022),
            "before_or_2024": sum(1 for y in ys if y <= 2024),
            "post_2020_share": sum(1 for y in ys if y >= 2021) / len(ys) if ys else 0,
            "post_2022_share": sum(1 for y in ys if y >= 2023) / len(ys) if ys else 0,
            "poi_density_per_km2": len(rs) / area_km2(name),
            "property_count": prop,
            "property_share": prop / len(rs) if rs else 0,
            "property_density_per_km2": prop / area_km2(name),
            "essential_count": essential,
            "productive_count": productive,
            "productive_share": productive / len(rs) if rs else 0,
            "food_count": food,
            "chain_anchor_count": chains,
            "chain_anchor_density_per_km2": chains / area_km2(name),
            "categories": dict(cats),
            "annual_first_visible": dict(Counter(y for y in ys if y)),
        }

    # Min-max urbanization pressure score across 3 km comparator areas.
    score_keys = ["poi_density_per_km2", "post_2020_share", "property_density_per_km2", "chain_anchor_density_per_km2"]
    weights = {
        "poi_density_per_km2": 0.35,
        "post_2020_share": 0.25,
        "property_density_per_km2": 0.25,
        "chain_anchor_density_per_km2": 0.15,
    }
    mins = {k: min(region_stats[r][k] for r in COMPARATOR_REGIONS) for k in score_keys}
    maxs = {k: max(region_stats[r][k] for r in COMPARATOR_REGIONS) for k in score_keys}
    for r in COMPARATOR_REGIONS:
        score = 0.0
        parts = {}
        for k in score_keys:
            denom = maxs[k] - mins[k]
            norm = (region_stats[r][k] - mins[k]) / denom if denom else 0.0
            parts[k] = norm
            score += weights[k] * norm
        region_stats[r]["urbanization_pressure_score"] = score * 100
        region_stats[r]["urbanization_pressure_components_norm"] = parts

    return {
        "coverage": {
            "total_rows": total,
            "dated_rows": dated,
            "dated_share": dated / total,
            "rating_rows": len(ratings),
            "phone_rows": phones,
            "website_rows": websites,
            "first_visible_min_year": min(year(r) for r in rows if year(r)),
            "first_visible_max_year": max(year(r) for r in rows if year(r)),
        },
        "region_stats": region_stats,
        "dataset_category_counts": dict(Counter(r.get("category") for r in rows)),
    }


def write_stats(stats: dict) -> None:
    STATS_JSON.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    rows = []
    for region, s in stats["region_stats"].items():
        rows.append({
            "region": region,
            "total_pois": s["total"],
            "dated_pois": s["dated"],
            "poi_density_per_km2": round(s["poi_density_per_km2"], 2),
            "post_2020_share_pct": round(s["post_2020_share"] * 100, 1),
            "property_count": s["property_count"],
            "property_share_pct": round(s["property_share"] * 100, 1),
            "property_density_per_km2": round(s["property_density_per_km2"], 2),
            "productive_count": s["productive_count"],
            "productive_share_pct": round(s["productive_share"] * 100, 1),
            "chain_anchor_count": s["chain_anchor_count"],
            "chain_anchor_density_per_km2": round(s["chain_anchor_density_per_km2"], 2),
            "urbanization_pressure_score": round(s.get("urbanization_pressure_score", 0), 1),
        })
    with STATS_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def read_osm() -> list[dict[str, str]]:
    with OSM.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_charts(rows: list[dict[str, str]], stats: dict) -> dict[str, str]:
    assets = {}
    rs = stats["region_stats"]

    # Study area count and density.
    labels = COMPARATOR_REGIONS
    values = [rs[r]["total"] for r in labels]
    path = ASSET_DIR / "poi_counts_by_area.png"
    save_bar(path, labels, values, "Current POI sample by 3 km study area", "POI rows")
    assets["poi_counts"] = path.relative_to(OUT_DIR).as_posix()

    values = [rs[r]["poi_density_per_km2"] for r in labels]
    path = ASSET_DIR / "poi_density_by_area.png"
    save_bar(path, labels, values, "Current POI sample density", "POIs per km²", "#3a86ff")
    assets["poi_density"] = path.relative_to(OUT_DIR).as_posix()

    # Pressure score.
    score_pairs = sorted([(r, rs[r].get("urbanization_pressure_score", 0)) for r in COMPARATOR_REGIONS], key=lambda x: x[1])
    path = ASSET_DIR / "urbanization_pressure_score.png"
    save_bar(path, [p[0] for p in score_pairs], [p[1] for p in score_pairs], "Urbanization pressure score, 3 km comparator areas", "0–100 index", "#9d4edd")
    assets["pressure_score"] = path.relative_to(OUT_DIR).as_posix()

    # Timeline cumulative.
    years = list(range(2013, 2027))
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    colors = ["#1b4332", "#457b9d", "#f77f00", "#6d597a", "#d62828", "#2a9d8f"]
    for color, region in zip(colors, COMPARATOR_REGIONS):
        annual = rs[region]["annual_first_visible"]
        cum, running = [], 0
        for y in years:
            running += int(annual.get(str(y), annual.get(y, 0)))
            cum.append(running)
        ax.plot(years, cum, label=region.replace(" 3 km", ""), linewidth=2 if region == "Godagama 3 km" else 1.5, color=color)
    ax.set_title("Cumulative Google-visible POI activity by earliest visible date", loc="left", fontweight="bold")
    ax.set_ylabel("Cumulative dated POIs")
    ax.set_xlabel("Earliest visible activity year")
    ax.legend(ncol=2, fontsize=8, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    path = ASSET_DIR / "cumulative_first_visible_timeline.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    assets["timeline"] = path.relative_to(OUT_DIR).as_posix()

    # Category mix Godagama 3 km.
    cats = Counter(rs["Godagama 3 km"]["categories"])
    top = cats.most_common(14)
    path = ASSET_DIR / "godagama_3km_category_mix.png"
    save_bar(path, [k for k, _ in top], [v for _, v in top], "Godagama 3 km category mix", "POI rows", "#40916c")
    assets["godagama_category_mix"] = path.relative_to(OUT_DIR).as_posix()

    # Ring structure.
    ring_labels = ["Core 0–1 km", "Ring 1–3 km", "Ring 3–5 km"]
    ring_counts = [rs["Godagama core 1 km"]["total"], rs["Godagama 3 km"]["total"] - rs["Godagama core 1 km"]["total"], rs["Godagama 5 km"]["total"] - rs["Godagama 3 km"]["total"]]
    ring_area = [math.pi * 1**2, math.pi * (3**2 - 1**2), math.pi * (5**2 - 3**2)]
    ring_density = [c / a for c, a in zip(ring_counts, ring_area)]
    fig, ax1 = plt.subplots(figsize=(8.2, 4.2))
    x = np.arange(3)
    ax1.bar(x - 0.18, ring_counts, width=0.36, label="POI count", color="#2d6a4f")
    ax2 = ax1.twinx()
    ax2.plot(x + 0.18, ring_density, marker="o", linewidth=2.5, label="POIs/km²", color="#e76f51")
    ax1.set_xticks(x, ring_labels)
    ax1.set_ylabel("POI rows")
    ax2.set_ylabel("POIs per km²")
    ax1.set_title("Godagama POI concentration by distance band", loc="left", fontweight="bold")
    lines, labels_ = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels_ + labels2, frameon=False, loc="upper right")
    fig.tight_layout()
    path = ASSET_DIR / "godagama_ring_structure.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    assets["ring_structure"] = path.relative_to(OUT_DIR).as_posix()

    # OSM growth.
    osm_rows = read_osm()
    years_osm = [2014, 2016, 2018, 2020, 2022, 2024, 2026]
    metrics = {r["metric"]: [float(r[f"{y}-01-01"]) for y in years_osm] for r in osm_rows}
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.plot(years_osm, metrics["buildings_count"], marker="o", linewidth=2.4, label="Mapped buildings")
    ax.set_ylabel("Mapped buildings")
    ax2 = ax.twinx()
    ax2.plot(years_osm, [v / 1000 for v in metrics["road_length_m"]], marker="s", linewidth=2.0, color="#3a86ff", label="Mapped road length")
    ax2.set_ylabel("Mapped road length, km")
    ax.set_title("OpenStreetMap history: Godagama-area built form and road network", loc="left", fontweight="bold")
    lines, labels_ = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels_ + labels2, frameon=False, loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    path = ASSET_DIR / "osm_buildings_roads_growth.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    assets["osm_growth"] = path.relative_to(OUT_DIR).as_posix()

    # Spatial scatter map.
    zone_colors = {
        "godagama_core_1km": "#d00000",
        "godagama_catchment_3km": "#f77f00",
        "godagama_pressure_5km": "#fcbf49",
        "homagama_comparator": "#457b9d",
        "meegoda_comparator": "#2a9d8f",
        "kottawa_makumbura_comparator": "#6d597a",
        "kahathuduwa_comparator": "#9d4edd",
        "padukka_comparator": "#1b4332",
        "outside_godagama_5km": "#adb5bd",
    }
    fig, ax = plt.subplots(figsize=(8.2, 6.0))
    for zone, color in zone_colors.items():
        pts = [(as_float(r.get("lng", "")), as_float(r.get("lat", ""))) for r in rows if r.get("radius_zone") == zone]
        pts = [(x, y) for x, y in pts if x is not None and y is not None]
        if not pts:
            continue
        ax.scatter([x for x, _ in pts], [y for _, y in pts], s=8 if zone != "outside_godagama_5km" else 5, alpha=0.55, color=color, label=zone.replace("_", " "))
    ax.scatter([80.0324106], [6.850694], marker="*", s=140, color="#000", label="Godagama centre")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Extracted POI geography: Godagama and comparator towns", loc="left", fontweight="bold")
    ax.legend(ncol=2, fontsize=6.8, frameon=False, loc="upper right")
    ax.grid(alpha=0.18)
    fig.tight_layout()
    path = ASSET_DIR / "poi_spatial_scatter.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    assets["spatial_scatter"] = path.relative_to(OUT_DIR).as_posix()

    return assets


def chain_table(rows: list[dict[str, str]]) -> list[list[object]]:
    goda5 = [r for r in rows if r.get("radius_zone") in REGIONS["Godagama 5 km"]]
    out = []
    for label, pat in CHAIN_PATTERNS.items():
        rx = re.compile(pat, re.I)
        matches = [r for r in goda5 if rx.search(r.get("name", "") + " " + r.get("address", ""))]
        if matches:
            first_dates = sorted([r.get("earliest_visible_activity_date") for r in matches if r.get("earliest_visible_activity_date")])
            examples = "; ".join(r["name"] for r in matches[:3])
            out.append([label, len(matches), first_dates[0] if first_dates else "", examples])
    out.sort(key=lambda r: (-int(r[1]), r[0]))
    return out


def build_report(rows: list[dict[str, str]], stats: dict, assets: dict[str, str]) -> None:
    cov = stats["coverage"]
    rs = stats["region_stats"]

    region_rows_md = []
    for region in COMPARATOR_REGIONS:
        s = rs[region]
        region_rows_md.append([
            region,
            s["total"],
            f'{s["poi_density_per_km2"]:.1f}',
            f'{s["post_2020_share"]*100:.1f}%',
            f'{s["property_share"]*100:.1f}%',
            s["property_count"],
            s["productive_count"],
            f'{s.get("urbanization_pressure_score", 0):.1f}',
        ])

    goda3 = rs["Godagama 3 km"]
    goda5 = rs["Godagama 5 km"]
    core = rs["Godagama core 1 km"]
    chain_rows = chain_table(rows)

    osm_rows = read_osm()
    osm_by_metric = {r["metric"]: r for r in osm_rows}
    buildings_2018 = float(osm_by_metric["buildings_count"]["2018-01-01"])
    buildings_2026 = float(osm_by_metric["buildings_count"]["2026-01-01"])
    roads_2018 = float(osm_by_metric["road_length_m"]["2018-01-01"]) / 1000
    roads_2026 = float(osm_by_metric["road_length_m"]["2026-01-01"]) / 1000
    shops_2018 = float(osm_by_metric["shops_count"]["2018-01-01"])
    shops_2026 = float(osm_by_metric["shops_count"]["2026-01-01"])
    food_2018 = float(osm_by_metric["food_drink_count"]["2018-01-01"])
    food_2026 = float(osm_by_metric["food_drink_count"]["2026-01-01"])

    plan_table = table_md(
        ["Planning / transport fact", "Data point", "Use in model"],
        [
            ["UDA zoning", "Godagama is High-Density Commercial Zone III; Kahathuduwa is High-Density Commercial Zone II", "Treat both as officially enabled growth nodes; compare Godagama against the higher-intensity Kahathuduwa interchange zone."],
            ["Expressway access", "Kottawa interchange is about 3 km from Homagama town; Kahathuduwa interchange is inside Homagama PS", "Model growth as High Level Road + interchange-access pressure, not only central Colombo spillover."],
            ["Environmental controls", "Wetland Nature Conservation Zone and Paddy/Wetland Agricultural Zone are explicit control layers; larger/sensitive commercial projects trigger CEA/UDA review", "Use protect/guide/intensify zones instead of blanket development."],
            ["Developer evidence", "Prime Lands and Home Lands pages market Homagama/Godagama/Kahathuduwa/Mirigama projects with highway/interchange access and future-value claims", "Use land-development POIs and project pages as market-response proxies."],
        ],
    )

    report = f"""
# Godagama 10200 urbanization evidence report

Date: 2026-06-27  
Study focus: Godagama town, 1 km core, 3 km local catchment, 5 km pressure zone, and comparator towns Homagama, Meegoda, Kottawa/Makumbura, Kahathuduwa, and Padukka.

## Executive findings

1. **Godagama is already a concentrated town core.** The Google-derived POI extract contains **{core['total']} POIs in the 1 km core**, equal to **{core['poi_density_per_km2']:.1f} POIs/km²** in the extracted sample. The wider **3 km Godagama catchment has {goda3['total']} POIs** or **{goda3['poi_density_per_km2']:.1f} POIs/km²**.

2. **Godagama's current commercial layer is younger than most comparator towns in this dataset.** **{goda3['post_2020_share']*100:.1f}%** of dated Godagama 3 km POIs have earliest visible activity from **2021 onward**. That is higher than Homagama, Meegoda, Kottawa/Makumbura, and Kahathuduwa in this extract.

3. **Property/developer pressure is already comparable to larger nodes.** In the Godagama 3 km catchment, **{goda3['property_count']} of {goda3['total']} POIs ({goda3['property_share']*100:.1f}%)** are apartments, land developments, or real-estate offices. That share is similar to Homagama and Kottawa/Makumbura, even though Godagama's total POI density is lower.

4. **OpenStreetMap history shows the physical network expanding before the commercial layer fully matures.** From 2018 to 2026 in the Godagama-area bounding box, mapped buildings rose from **{buildings_2018:.0f} to {buildings_2026:.0f} (+{(buildings_2026/buildings_2018-1)*100:.0f}%)**, while mapped road length rose from **{roads_2018:.1f} km to {roads_2026:.1f} km (+{(roads_2026/roads_2018-1)*100:.0f}%)**. Mapped shops rose from **{shops_2018:.0f} to {shops_2026:.0f}**, and mapped food/drink places rose from **{food_2018:.0f} to {food_2026:.0f}**.

5. **The measured pressure ranking puts Godagama below Kahathuduwa, Meegoda, and Kottawa/Makumbura, but its town core is already intense.** The report's 0–100 pressure score uses only observed variables: current POI density, post-2020 activity share, property/developer density, and chain/finance anchor density. Godagama's 3 km score is **{goda3.get('urbanization_pressure_score', 0):.1f}**. Separately, the UDA plan also identifies Godagama and Kahathuduwa as commercial intensification zones.

## Data used

| Dataset | Rows / scope | What it measures | Main limitation |
|---|---:|---|---|
| Google Maps-derived POI extract | {cov['total_rows']:,} POIs | Current commercial/social/institutional places and earliest visible photo/activity date | Earliest photo date is an activity proxy, not a confirmed opening date; review count and first review date are not decoded yet |
| Google POI geodata | {cov['total_rows']:,} points | Spatial distribution by town/comparator | Search result caps and broad queries can pull corridor results |
| OSM/ohsome baseline | 7 time slices, 2014–2026 | Buildings, roads, shops, food/drink, amenities | OSM edit history is affected by mapping completeness |
| UDA/RDA/planning sources | Homagama plan, expressway/gazette data, developer pages | Zoning, interchange access, environmental controls, developer market signals | Planning facts need map-layer digitization for parcel-level use |

Coverage in the Google-derived POI extract:

- **{cov['dated_rows']:,} / {cov['total_rows']:,} POIs** have earliest visible activity/photo dates.
- **{cov['rating_rows']:,} / {cov['total_rows']:,} POIs** have ratings.
- **{cov['phone_rows']:,} / {cov['total_rows']:,} POIs** have phone numbers.
- **{cov['website_rows']:,} / {cov['total_rows']:,} POIs** have websites.

![Extracted POI geography]({assets['spatial_scatter']})

## Current urban structure

![Current POI sample by area]({assets['poi_counts']})

![Current POI density]({assets['poi_density']})

Godagama's 3 km catchment has less total POI density than Kahathuduwa, Meegoda, Kottawa/Makumbura, and Padukka in this extract. The difference changes inside the 1 km town core: the core is dense, while the outer rings are thinner.

![Godagama distance-band structure]({assets['ring_structure']})

## Timeline signal: earliest visible Google activity

This chart counts each current POI by the earliest visible activity date decoded from photo metadata. It is not a verified opening-date chart. It is useful as a comparable visibility/activity signal because the same extraction method is applied across all study areas.

![Cumulative first-visible timeline]({assets['timeline']})

Key table:

{table_md(['Area', 'POIs', 'POIs/km²', 'First visible 2021+', 'Property share', 'Property POIs', 'Local productive POIs', 'Pressure score'], region_rows_md)}

## Godagama category mix

![Godagama category mix]({assets['godagama_category_mix']})

The 3 km Godagama catchment is not only food/retail. Its largest visible categories include electronics, clinics, hardware, vehicle service, apartments, supermarkets, and land development. That mix indicates a practical service town with rising property pressure, not a pure restaurant/café suburb.

Grouped Godagama 3 km counts:

{table_md(['Group', 'Count', 'Share of Godagama 3 km POIs'], [[k, sum(1 for r in region_rows(rows, 'Godagama 3 km') if r.get('category') in v), f"{sum(1 for r in region_rows(rows, 'Godagama 3 km') if r.get('category') in v)/goda3['total']*100:.1f}%"] for k, v in CATEGORY_GROUPS.items()])}

## Commercial and chain anchors in the Godagama 5 km pressure zone

This table uses name/address matching, not the extractor's query-assigned brand field.

{table_md(['Anchor', 'Matched POIs in 5 km', 'Earliest visible date in extract', 'Examples'], chain_rows)}

Interpretation from the table: Godagama already has formal supermarket, bakery/food, banking/finance, and land-development anchors inside the 5 km pressure zone. The anchor count is lower than larger comparator nodes, but the categories are already present.

## OSM built-form baseline

![OSM buildings and roads growth]({assets['osm_growth']})

OpenStreetMap history gives a separate physical-growth signal. The 2018–2026 change is large enough that the direction is clear even after allowing for mapping-completeness bias:

{table_md(['OSM metric', '2018', '2026', 'Change'], [
    ['Mapped buildings', f'{buildings_2018:.0f}', f'{buildings_2026:.0f}', f'+{(buildings_2026/buildings_2018-1)*100:.0f}%'],
    ['Mapped road length', f'{roads_2018:.1f} km', f'{roads_2026:.1f} km', f'+{(roads_2026/roads_2018-1)*100:.0f}%'],
    ['Mapped shops', f'{shops_2018:.0f}', f'{shops_2026:.0f}', f'+{(shops_2026/shops_2018-1)*100:.0f}%'],
    ['Mapped food/drink places', f'{food_2018:.0f}', f'{food_2026:.0f}', f'+{(food_2026/food_2018-1)*100:.0f}%'],
])}

## Urbanization pressure model

The model is a triage score for where to do fieldwork and planning review first. It is not a land-price forecast.

Score inputs for each 3 km area:

- 35% current POI density per km²;
- 25% share of dated POIs first visible from 2021 onward;
- 25% property/developer density per km², using apartment + land development + real-estate office categories;
- 15% chain/finance anchor density per km², using name/address matching.

Each input is min-max normalized across the six 3 km comparator areas, then weighted into a 0–100 score.

![Urbanization pressure score]({assets['pressure_score']})

Readout:

- **Kahathuduwa** has the strongest measured pressure profile in this model. It also has a separate official planning signal: High-Density Commercial Zone II and interchange-led guide-plan logic.
- **Meegoda** has high POI density and strong chain/finance anchor density. Its economic-centre/agri-logistics role is already clearer than Godagama's.
- **Kottawa/Makumbura** has the strongest property/developer density in the sample, consistent with highway/multimodal access pressure.
- **Godagama** is a lower-density 3 km catchment but has a dense 1 km core, a high post-2020 activity share, and property/developer share similar to larger nodes. The measured pattern is: urbanized core, thinner outer catchment, rising property signal.

## Planning and policy facts to include in any stakeholder discussion

{plan_table}

## Data-driven planning suggestions

These are derived from the observed pattern: dense core, younger activity layer, property pressure, and official commercial zoning.

### 1. Treat the 1 km core as a town-centre management zone

Observed basis: **{core['total']} POIs in 1 km** and **{core['poi_density_per_km2']:.1f} POIs/km²**.

Use this zone for frontage rules, pedestrian crossings, parking management, drainage upgrades, shade trees, loading/unloading control, and protection of small shopfronts.

### 2. Treat the 1–3 km ring as the local-business expansion zone

Observed basis: Godagama 3 km has **{goda3['productive_count']} local productive-service POIs** and **{goda3['property_count']} property/developer POIs**.

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
""".strip() + "\n"

    MD_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    rows = read_rows()
    stats = analyze(rows)
    write_stats(stats)
    assets = build_charts(rows, stats)
    build_report(rows, stats, assets)
    print(MD_OUT)
    print(STATS_JSON)
    print(STATS_CSV)


if __name__ == "__main__":
    main()

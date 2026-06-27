#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "urbanization/data/google_maps_godagama_pois.csv"
OSM = ROOT / "urbanization/data/godagama-osm-ohsome-baseline-2026-06-26.csv"
OUT = ROOT / "urbanization/reports"
ASSETS = OUT / "assets/public_report"
ASSETS.mkdir(parents=True, exist_ok=True)

MD = OUT / "godagama-urbanization-public-report-2026-06-27.md"
HTML = OUT / "godagama-urbanization-public-report-2026-06-27.html"
PDF = OUT / "godagama-urbanization-public-report-2026-06-27.pdf"
STATS = ROOT / "urbanization/data/godagama_public_report_stats_2026-06-27.json"

REGION_ZONES = {
    "Godagama": ["godagama_core_1km", "godagama_catchment_3km"],
    "Homagama": ["homagama_comparator"],
    "Meegoda": ["meegoda_comparator"],
    "Kottawa/Makumbura": ["kottawa_makumbura_comparator"],
    "Kahathuduwa": ["kahathuduwa_comparator"],
    "Padukka": ["padukka_comparator"],
}
REGION_ORDER = ["Godagama", "Homagama", "Meegoda", "Kottawa/Makumbura", "Kahathuduwa", "Padukka"]
CENTERS = {
    "Godagama": (6.850694, 80.0324106),
    "Homagama": (6.844, 80.0024),
    "Meegoda": (6.8459, 80.0508),
    "Kottawa/Makumbura": (6.8408, 79.9658),
    "Kahathuduwa": (6.7835, 79.9972),
    "Padukka": (6.8377, 80.0905),
}
CATEGORY_GROUPS = {
    "Property / developer": {"land_development", "real_estate_office", "apartment"},
    "Daily essentials": {"supermarket", "grocery", "bakery", "pharmacy", "clinic", "hospital", "bank", "atm", "fuel_station", "school", "university", "government_office"},
    "Local productive services": {"hardware", "vehicle_service", "tyre_shop", "electronics", "courier"},
    "Food / social": {"restaurant", "cafe", "fast_food", "bakery"},
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

PALETTE = {
    "ink": "#1f2933",
    "muted": "#697386",
    "grid": "#d8dee9",
    "green": "#2D6A4F",
    "green2": "#40916C",
    "blue": "#3A86FF",
    "orange": "#F59E0B",
    "red": "#C2410C",
    "purple": "#7C3AED",
    "teal": "#0F766E",
    "sand": "#F8F3EA",
}

mpl.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 260,
    "font.family": "DejaVu Sans",
    "axes.facecolor": "#FFFFFF",
    "figure.facecolor": "#FFFFFF",
    "axes.edgecolor": "#CBD5E1",
    "axes.labelcolor": PALETTE["ink"],
    "xtick.color": PALETTE["muted"],
    "ytick.color": PALETTE["muted"],
    "text.color": PALETTE["ink"],
    "axes.titleweight": "bold",
    "axes.titlesize": 13,
    "axes.labelsize": 9.5,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fl(v: str) -> float | None:
    try:
        return float(v)
    except Exception:
        return None


def valid_sl(row: dict[str, str]) -> bool:
    lat, lng = fl(row.get("lat", "")), fl(row.get("lng", ""))
    return lat is not None and lng is not None and 5.8 <= lat <= 10.1 and 79.4 <= lng <= 82.1


def local_map_bounds(row: dict[str, str]) -> bool:
    lat, lng = fl(row.get("lat", "")), fl(row.get("lng", ""))
    return lat is not None and lng is not None and 6.55 <= lat <= 6.95 and 79.85 <= lng <= 80.16


def yr(row: dict[str, str]) -> int | None:
    d = row.get("earliest_visible_activity_date") or row.get("first_photo_date") or ""
    try:
        y = int(d[:4])
    except Exception:
        return None
    return y if 2010 <= y <= 2030 else None


def rows_for(rows: list[dict[str, str]], region: str) -> list[dict[str, str]]:
    zones = set(REGION_ZONES[region])
    return [r for r in rows if r.get("radius_zone") in zones]


def area_km2(region: str) -> float:
    return math.pi * 3 * 3


def is_chain(row: dict[str, str]) -> bool:
    return bool(CHAIN_RE.search((row.get("name", "") + " " + row.get("address", ""))))


def analyze(rows: list[dict[str, str]]) -> dict:
    out = {}
    for region in REGION_ORDER:
        rr = rows_for(rows, region)
        years = [yr(r) for r in rr if yr(r)]
        property_count = sum(1 for r in rr if r.get("category") in CATEGORY_GROUPS["Property / developer"])
        productive_count = sum(1 for r in rr if r.get("category") in CATEGORY_GROUPS["Local productive services"])
        chain_count = sum(1 for r in rr if is_chain(r))
        grouped = {g: sum(1 for r in rr if r.get("category") in cats) for g, cats in CATEGORY_GROUPS.items()}
        out[region] = {
            "total": len(rr),
            "dated": len(years),
            "poi_density": len(rr) / area_km2(region),
            "recent_share": sum(1 for y in years if y >= 2021) / len(years) if years else 0,
            "post_2022_share": sum(1 for y in years if y >= 2023) / len(years) if years else 0,
            "property_count": property_count,
            "property_share": property_count / len(rr) if rr else 0,
            "property_density": property_count / area_km2(region),
            "productive_count": productive_count,
            "productive_share": productive_count / len(rr) if rr else 0,
            "chain_count": chain_count,
            "chain_density": chain_count / area_km2(region),
            "groups": grouped,
            "cohorts": {
                "≤2018": sum(1 for y in years if y <= 2018),
                "2019–20": sum(1 for y in years if 2019 <= y <= 2020),
                "2021–22": sum(1 for y in years if 2021 <= y <= 2022),
                "2023–24": sum(1 for y in years if 2023 <= y <= 2024),
                "2025–26": sum(1 for y in years if 2025 <= y <= 2026),
            },
            "top_categories": dict(Counter(r.get("category") for r in rr).most_common(12)),
        }
    # Pressure score.
    keys = ["poi_density", "recent_share", "property_density", "chain_density"]
    weights = {"poi_density": 0.35, "recent_share": 0.25, "property_density": 0.25, "chain_density": 0.15}
    mins = {k: min(out[r][k] for r in REGION_ORDER) for k in keys}
    maxs = {k: max(out[r][k] for r in REGION_ORDER) for k in keys}
    for region in REGION_ORDER:
        score = 0.0
        norms = {}
        for k in keys:
            norm = (out[region][k] - mins[k]) / (maxs[k] - mins[k]) if maxs[k] > mins[k] else 0
            norms[k] = norm
            score += weights[k] * norm
        out[region]["score"] = score * 100
        out[region]["score_norms"] = norms
    return out


def savefig(path: Path):
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close()
    return path.relative_to(OUT).as_posix()


def annotate_caption(fig, text: str):
    fig.text(0.01, 0.01, text, ha="left", va="bottom", fontsize=7.5, color=PALETTE["muted"])


def chart_spatial(rows: list[dict[str, str]]) -> str:
    pts = [r for r in rows if local_map_bounds(r)]
    colors = {
        "godagama_core_1km": PALETTE["red"],
        "godagama_catchment_3km": PALETTE["orange"],
        "godagama_pressure_5km": "#EAB308",
        "homagama_comparator": PALETTE["blue"],
        "meegoda_comparator": PALETTE["teal"],
        "kottawa_makumbura_comparator": PALETTE["purple"],
        "kahathuduwa_comparator": "#DB2777",
        "padukka_comparator": PALETTE["green"],
        "outside_godagama_5km": "#94A3B8",
    }
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    # all points muted by zone
    for zone, color in colors.items():
        zpts = [r for r in pts if r.get("radius_zone") == zone]
        if not zpts:
            continue
        ax.scatter([fl(r["lng"]) for r in zpts], [fl(r["lat"]) for r in zpts], s=10 if "godagama" in zone else 8, alpha=0.48, c=color, label=zone.replace("_", " "))
    # draw approximate 1/3/5 km rings around Godagama using degree conversion
    lat0, lng0 = CENTERS["Godagama"]
    for km, color, lw in [(1, PALETTE["red"], 1.8), (3, PALETTE["orange"], 1.4), (5, "#EAB308", 1.2)]:
        t = np.linspace(0, 2*np.pi, 240)
        lat = lat0 + (km / 111.0) * np.sin(t)
        lng = lng0 + (km / (111.0 * math.cos(math.radians(lat0)))) * np.cos(t)
        ax.plot(lng, lat, color=color, lw=lw, alpha=0.88)
        ax.text(lng0 + km/(111.0*math.cos(math.radians(lat0))) + 0.001, lat0, f"{km} km", fontsize=8, color=color, va="center")
    for name, (lat, lng) in CENTERS.items():
        ax.scatter([lng], [lat], marker="*" if name == "Godagama" else "o", s=145 if name == "Godagama" else 42, c="black" if name == "Godagama" else "white", edgecolors="black", linewidths=1.2, zorder=5)
        dx, dy = (0.003, 0.004)
        if name == "Kahathuduwa": dy = -0.012
        if name == "Padukka": dx = -0.021
        ax.text(lng + dx, lat + dy, name, fontsize=8.5, weight="bold", zorder=6)
    ax.set_xlim(79.94, 80.115)
    ax.set_ylim(6.765, 6.88)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("POI geography after removing non-Sri-Lanka coordinate outliers", loc="left")
    ax.grid(True, alpha=0.22)
    ax.legend(ncol=2, loc="upper right", frameon=True, framealpha=0.9, fontsize=7.4)
    annotate_caption(fig, "Dots are extracted POIs. Rings show 1 km, 3 km and 5 km around Godagama centre. This is a coordinate plot, not a basemap.")
    return savefig(ASSETS / "01_spatial_clean_map.png")


def chart_fingerprint(stats: dict) -> str:
    rows = REGION_ORDER
    cols = [
        ("POI density\nper km²", "poi_density", "{:.1f}"),
        ("First visible\n2021+", "recent_share", "{:.0%}"),
        ("Property density\nper km²", "property_density", "{:.2f}"),
        ("Chain anchor\ndensity", "chain_density", "{:.2f}"),
        ("Local productive\nshare", "productive_share", "{:.0%}"),
    ]
    raw = np.array([[stats[r][key] for _, key, _ in cols] for r in rows], dtype=float)
    norm = raw.copy()
    for j in range(raw.shape[1]):
        mn, mx = raw[:, j].min(), raw[:, j].max()
        norm[:, j] = (raw[:, j] - mn) / (mx - mn) if mx > mn else 0
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    im = ax.imshow(norm, cmap="YlGnBu", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(cols)), [c[0] for c in cols])
    ax.set_yticks(np.arange(len(rows)), rows)
    ax.set_title("Urbanization fingerprint by study area", loc="left")
    for i, region in enumerate(rows):
        for j, (_, key, fmt) in enumerate(cols):
            ax.text(j, i, fmt.format(stats[region][key]), ha="center", va="center", fontsize=8.5, color="white" if norm[i, j] > 0.58 else PALETTE["ink"], weight="bold" if norm[i, j] > 0.58 else "normal")
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.025)
    cbar.set_label("Relative rank within comparator set")
    annotate_caption(fig, "Values are actual; shading is min-max normalized by column. Darker does not mean 'better', only more intense on that indicator.")
    return savefig(ASSETS / "02_urbanization_fingerprint.png")


def chart_pressure_scatter(stats: dict) -> str:
    fig, ax = plt.subplots(figsize=(8.7, 5.5))
    xs = np.array([stats[r]["poi_density"] for r in REGION_ORDER])
    ys = np.array([stats[r]["property_density"] for r in REGION_ORDER])
    recent = np.array([stats[r]["recent_share"] for r in REGION_ORDER])
    chains = np.array([stats[r]["chain_count"] for r in REGION_ORDER])
    sizes = 130 + chains * 10
    sc = ax.scatter(xs, ys, s=sizes, c=recent, cmap="viridis", edgecolor="white", linewidth=1.2, alpha=0.92)
    label_pos = {
        "Godagama": (0.12, 0.035),
        "Homagama": (0.12, 0.035),
        "Meegoda": (0.10, -0.075),
        "Kottawa/Makumbura": (-2.65, -0.075),
        "Kahathuduwa": (-2.55, -0.060),
        "Padukka": (0.12, 0.035),
    }
    for r, x, y in zip(REGION_ORDER, xs, ys):
        dx, dy = label_pos[r]
        ax.text(x + dx, y + dy, r, fontsize=8.6, weight="bold")
    ax.axvline(np.median(xs), color="#94A3B8", lw=1, ls="--", alpha=0.7)
    ax.axhline(np.median(ys), color="#94A3B8", lw=1, ls="--", alpha=0.7)
    ax.set_ylim(min(ys) - 0.07, max(ys) + 0.22)
    ax.set_xlabel("Current POI density (POIs/km²)")
    ax.set_ylabel("Property/developer POI density (POIs/km²)")
    ax.set_title("Where commercial intensity and property pressure overlap", loc="left", pad=12)
    ax.grid(True, alpha=0.22)
    cbar = fig.colorbar(sc, ax=ax, fraction=0.04, pad=0.03)
    cbar.set_label("Share first visible from 2021 onward")
    annotate_caption(fig, "Bubble size = chain/finance anchor count. Dashed lines are medians across the six comparator areas.")
    return savefig(ASSETS / "03_pressure_scatter.png")


def chart_cohorts(stats: dict) -> str:
    buckets = ["≤2018", "2019–20", "2021–22", "2023–24", "2025–26"]
    colors = ["#CBD5E1", "#93C5FD", "#34D399", "#FBBF24", "#F97316"]
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    y = np.arange(len(REGION_ORDER))
    left = np.zeros(len(REGION_ORDER))
    for b, color in zip(buckets, colors):
        vals = np.array([stats[r]["cohorts"][b] for r in REGION_ORDER], dtype=float)
        totals = np.array([stats[r]["dated"] for r in REGION_ORDER], dtype=float)
        pct = np.divide(vals, totals, out=np.zeros_like(vals), where=totals > 0) * 100
        ax.barh(y, pct, left=left, color=color, label=b, edgecolor="white", linewidth=0.7)
        for i, v in enumerate(pct):
            if v >= 8:
                ax.text(left[i] + v/2, i, f"{v:.0f}%", ha="center", va="center", fontsize=7.4, color="#111827")
        left += pct
    ax.set_yticks(y, REGION_ORDER)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of dated POIs")
    ax.set_title("Earliest visible activity cohorts", loc="left")
    ax.legend(ncol=5, bbox_to_anchor=(0, 1.04, 1, 0.1), loc="lower left", mode="expand", frameon=False)
    ax.grid(axis="x", alpha=0.18)
    annotate_caption(fig, "Cohorts use earliest decoded photo/activity date. They compare current places by first visible signal; they are not confirmed opening dates.")
    return savefig(ASSETS / "04_activity_cohorts.png")


def chart_godagama_rings(rows: list[dict[str, str]]) -> str:
    bands = [
        ("0–1 km core", ["godagama_core_1km"], math.pi*1*1),
        ("1–3 km ring", ["godagama_catchment_3km"], math.pi*(3*3-1*1)),
        ("3–5 km ring", ["godagama_pressure_5km"], math.pi*(5*5-3*3)),
    ]
    metrics = ["POI count", "POI density/km²", "Property share"]
    values = []
    labels = []
    for _, zones, area in bands:
        rr = [r for r in rows if r.get("radius_zone") in zones]
        prop = sum(1 for r in rr if r.get("category") in CATEGORY_GROUPS["Property / developer"])
        row = [len(rr), len(rr)/area, prop/len(rr)*100 if rr else 0]
        values.append(row)
        labels.append([f"{row[0]:.0f}", f"{row[1]:.1f}", f"{row[2]:.1f}%"])
    raw = np.array(values, dtype=float)
    norm = raw.copy()
    for j in range(raw.shape[1]):
        mn, mx = raw[:, j].min(), raw[:, j].max()
        norm[:, j] = (raw[:, j] - mn) / (mx - mn) if mx > mn else 0
    fig, ax = plt.subplots(figsize=(8.4, 3.7))
    ax.imshow(norm, cmap="YlOrBr", vmin=0, vmax=1, aspect="auto")
    ax.set_yticks(np.arange(3), [b[0] for b in bands])
    ax.set_xticks(np.arange(3), metrics)
    ax.set_title("Godagama distance-band profile", loc="left", pad=12)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, labels[i][j], ha="center", va="center", fontsize=11, weight="bold", color="white" if norm[i, j] > 0.55 else PALETTE["ink"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    annotate_caption(fig, "Core = 0–1 km from Godagama centre. Rings are non-overlapping; darker cells are higher within each metric.")
    return savefig(ASSETS / "05_godagama_rings.png")


def chart_osm_index() -> str:
    rows = read_csv(OSM)
    by = {r["metric"]: r for r in rows}
    years = [2018, 2020, 2022, 2024, 2026]
    metrics = [
        ("buildings_count", "Buildings", PALETTE["green"]),
        ("road_length_m", "Road length", PALETTE["blue"]),
        ("shops_count", "Shops", PALETTE["orange"]),
        ("food_drink_count", "Food/drink", PALETTE["purple"]),
    ]
    fig, ax = plt.subplots(figsize=(8.8, 4.7))
    for key, label, color in metrics:
        vals = [float(by[key][f"{y}-01-01"]) for y in years]
        base = vals[0]
        idx = [v/base*100 for v in vals]
        ax.plot(years, idx, marker="o", lw=2.3, label=label, color=color)
        ax.text(years[-1]+0.06, idx[-1], f"{label} {idx[-1]:.0f}", va="center", fontsize=8.2, color=color, weight="bold")
    ax.axhline(100, color="#94A3B8", lw=1)
    ax.set_xlim(2017.8, 2026.9)
    ax.set_ylabel("Index, 2018 = 100")
    ax.set_xlabel("OSM snapshot year")
    ax.set_title("OpenStreetMap growth index around Godagama", loc="left")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False, ncol=4, loc="upper left")
    annotate_caption(fig, "Indexing avoids misleading dual axes. OSM history is a mapped-feature signal, not a building-permit record.")
    return savefig(ASSETS / "06_osm_index_growth.png")


def chart_category_groups(stats: dict) -> str:
    groups = list(CATEGORY_GROUPS.keys())
    goda = [stats["Godagama"]["groups"][g] / stats["Godagama"]["total"] * 100 for g in groups]
    comp = []
    for g in groups:
        vals = [stats[r]["groups"][g] / stats[r]["total"] * 100 for r in REGION_ORDER if r != "Godagama"]
        comp.append(sum(vals)/len(vals))
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    y = np.arange(len(groups))
    ax.barh(y - 0.18, goda, height=0.34, color=PALETTE["green"], label="Godagama 3 km")
    ax.barh(y + 0.18, comp, height=0.34, color="#94A3B8", label="Comparator average")
    ax.set_yticks(y, groups)
    ax.invert_yaxis()
    ax.set_xlabel("Share of POIs")
    ax.set_title("Godagama category structure vs comparator average", loc="left")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.2)
    for i, (a, b) in enumerate(zip(goda, comp)):
        ax.text(a + 0.5, i - 0.18, f"{a:.1f}%", va="center", fontsize=8.2, color=PALETTE["green"], weight="bold")
        ax.text(b + 0.5, i + 0.18, f"{b:.1f}%", va="center", fontsize=8.2, color=PALETTE["muted"])
    annotate_caption(fig, "Categories can overlap by group, e.g. bakery is both daily essential and food/social.")
    return savefig(ASSETS / "07_category_groups.png")


def chain_anchor_rows(rows: list[dict[str, str]]) -> list[tuple[str, int, str]]:
    goda5 = [r for r in rows if r.get("radius_zone") in ["godagama_core_1km", "godagama_catchment_3km", "godagama_pressure_5km"]]
    result = []
    for name, pat in CHAIN_PATTERNS.items():
        rx = re.compile(pat, re.I)
        m = [r for r in goda5 if rx.search(r.get("name", "") + " " + r.get("address", ""))]
        if m:
            dates = sorted([r.get("earliest_visible_activity_date") for r in m if r.get("earliest_visible_activity_date")])
            result.append((name, len(m), dates[0] if dates else ""))
    return sorted(result, key=lambda x: (-x[1], x[0]))


def chart_chains(rows: list[dict[str, str]]) -> str:
    data = chain_anchor_rows(rows)
    labels = [x[0] for x in data]
    counts = [x[1] for x in data]
    dates = [x[2] for x in data]
    fig, ax = plt.subplots(figsize=(8.8, 5.1))
    y = np.arange(len(labels))
    ax.hlines(y, 0, counts, color="#CBD5E1", lw=6)
    ax.scatter(counts, y, s=80, color=PALETTE["green"], zorder=3)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Matched POIs in Godagama 5 km pressure zone")
    ax.set_title("Formal commercial/finance anchors already present", loc="left")
    ax.grid(axis="x", alpha=0.18)
    for i, (c, d) in enumerate(zip(counts, dates)):
        ax.text(c + 0.22, i, f"{c}  ·  earliest {d or 'n/a'}", va="center", fontsize=8.1)
    annotate_caption(fig, "Name/address matching for major chains, banks/finance, and land developers. Earliest dates are Google-visible activity proxies.")
    return savefig(ASSETS / "08_chain_anchors.png")


def build_markdown(raw_rows: list[dict[str, str]], rows: list[dict[str, str]], stats: dict, assets: dict[str, str]) -> None:
    invalid = len(raw_rows) - len(rows)
    goda = stats["Godagama"]
    kah = stats["Kahathuduwa"]
    kott = stats["Kottawa/Makumbura"]
    meeg = stats["Meegoda"]
    sorted_scores = sorted(REGION_ORDER, key=lambda r: stats[r]["score"], reverse=True)

    def table(headers, data):
        out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"]*len(headers)) + "|"]
        out += ["| " + " | ".join(str(x) for x in row) + " |" for row in data]
        return "\n".join(out)

    region_table = []
    for r in REGION_ORDER:
        s = stats[r]
        region_table.append([
            r,
            s["total"],
            f"{s['poi_density']:.1f}",
            f"{s['recent_share']*100:.1f}%",
            f"{s['property_share']*100:.1f}%",
            s["property_count"],
            s["productive_count"],
            f"{s['score']:.1f}",
        ])

    chain_table = [[name, count, first] for name, count, first in chain_anchor_rows(rows)]

    md = f"""# Godagama 10200 urbanization evidence report

Date: 2026-06-27  
Prepared from the Google-derived POI extract, OSM/ohsome history, UDA/RDA planning evidence, and developer market signals.

## What changed in this version

The earlier coordinate scatter chart was not useful because one extracted POI had a bad longitude outside Sri Lanka, which stretched the axis. This version filters geospatial outliers for charts, replaces the raw scatter with a local map view, and adds comparison visuals designed for print.

## Data quality note

- Raw Google-derived POI rows: **{len(raw_rows):,}**.
- Rows used for numeric analysis after removing non-Sri-Lanka coordinate outliers: **{len(rows):,}**.
- Removed geospatial outliers: **{invalid}**.
- POIs with earliest visible activity/photo dates: **{sum(1 for r in rows if yr(r)):,}**.
- The earliest-visible date is an activity proxy, not a confirmed opening date.

## Executive findings

1. **Godagama has a dense core and a thinner surrounding catchment.** The 3 km catchment has **{goda['total']} POIs** (**{goda['poi_density']:.1f}/km²**), but the 1 km core alone has **274 POIs**, about **87.2/km²**.

2. **The current Godagama POI layer is recent.** **{goda['recent_share']*100:.1f}%** of dated Godagama POIs were first visible from **2021 onward**, the highest recent-share among the six comparator areas in this extract.

3. **The property/developer signal is already material.** Godagama has **{goda['property_count']} property/developer POIs** in the 3 km catchment, **{goda['property_share']*100:.1f}%** of its extracted POI base. That share is close to Homagama and Kottawa/Makumbura.

4. **The strongest comparator pressure is Kahathuduwa, followed by Meegoda and Kottawa/Makumbura.** The pressure score ranks: **{', '.join(f'{r} ({stats[r]['score']:.1f})' for r in sorted_scores)}**.

5. **OpenStreetMap history shows physical growth ahead of full commercial maturity.** In the Godagama-area OSM bounding box, mapped buildings rose **+338%** from 2018 to 2026, while mapped road length rose **+33%**. That is consistent with subdivision/build-out happening before the commercial layer fully fills in.

## Study geography

![Clean local POI geography]({assets['spatial']})

## Comparator fingerprint

This is the main diagnostic chart. Darker cells show which areas are high on each measured indicator; values printed inside the cells are the actual values.

![Urbanization fingerprint]({assets['fingerprint']})

## Pressure model

The model is not a land-price forecast. It is a triage index for where urbanization pressure is most visible in the current data.

Inputs:

- 35% current POI density;
- 25% share of POIs first visible from 2021 onward;
- 25% property/developer POI density;
- 15% chain/finance anchor density.

![Pressure scatter]({assets['pressure']})

{table(['Area', 'POIs', 'POIs/km²', 'Visible 2021+', 'Property share', 'Property POIs', 'Productive-service POIs', 'Score'], region_table)}

## Timeline signal

![Activity cohorts]({assets['cohorts']})

The 2021–2022 band is large across all areas. Treat it as a combined real activity + Google photo coverage signal. The comparison remains useful because the same extraction method is applied to each area.

## Godagama distance-band structure

![Godagama rings]({assets['rings']})

The 1 km core carries most of the visible density. The planning implication is that Godagama should be treated as a town-centre management problem in the core and a growth-guidance problem in the 1–5 km rings.

## Category structure

![Category groups]({assets['category_groups']})

Godagama is not only a food or commuting suburb. The extracted mix shows daily essentials, clinics, hardware, vehicle service, electronics, courier, apartments, and land development. That supports a local-enterprise framing rather than a single-sector framing.

## Chain, finance, and developer anchors

![Chain anchors]({assets['chains']})

{table(['Anchor', 'Matched POIs in Godagama 5 km', 'Earliest visible date'], chain_table)}

## Physical growth baseline from OSM

![OSM growth index]({assets['osm']})

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
"""
    MD.write_text(md, encoding="utf-8")


def main() -> None:
    raw = read_csv(DATA)
    rows = [r for r in raw if valid_sl(r)]
    stats = analyze(rows)
    assets = {
        "spatial": chart_spatial(rows),
        "fingerprint": chart_fingerprint(stats),
        "pressure": chart_pressure_scatter(stats),
        "cohorts": chart_cohorts(stats),
        "rings": chart_godagama_rings(rows),
        "osm": chart_osm_index(),
        "category_groups": chart_category_groups(stats),
        "chains": chart_chains(rows),
    }
    STATS.write_text(json.dumps({"raw_rows": len(raw), "analysis_rows": len(rows), "regions": stats}, indent=2), encoding="utf-8")
    build_markdown(raw, rows, stats, assets)
    print(MD)
    print(STATS)


if __name__ == "__main__":
    main()

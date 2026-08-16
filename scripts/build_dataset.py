#!/usr/bin/env python3
"""Build a bounded, public Overture Places extract without credentials."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any

from markets import daily_markets

RELEASE = "2026-06-17.0"
SCHEMA_VERSION = 1
RECORDS_PER_MARKET = 350
TARGET_TERMS = (
    "restaurant", "food_and_drink", "cafe", "coffee_shop", "diner", "bistro", "bakery",
    "pizzeria", "brewery", "brewpub", "taproom", "beer_garden", "dessert", "ice_cream",
    "farmers_market", "public_market", "museum", "zoo", "aquarium", "botanical",
    "tourist_attraction", "landmark", "monument", "historic_site", "art_gallery",
    "visitor_center", "theme_park", "amusement_park", "nature_center", "observatory",
)


def category_values(row: dict[str, Any]) -> list[str]:
    categories = row.get("categories") or {}
    taxonomy = row.get("taxonomy") or {}
    values = [row.get("basic_category"), categories.get("primary"), taxonomy.get("primary")]
    values.extend(categories.get("alternate") or [])
    values.extend(taxonomy.get("hierarchy") or [])
    values.extend(taxonomy.get("alternates") or [])
    return [str(value).lower().replace("-", "_") for value in values if value]


def relevant(row: dict[str, Any]) -> bool:
    return any(term in value for value in category_values(row) for term in TARGET_TERMS)


def market_bbox(market: dict[str, Any]) -> tuple[float, float, float, float]:
    radius = min(30.0, max(2.0, float(market["radiusMiles"])))
    latitude = float(market["latitude"])
    longitude = float(market["longitude"])
    lat_delta = radius / 69.0
    lng_delta = radius / (69.0 * max(0.2, math.cos(math.radians(latitude))))
    return longitude - lng_delta, latitude - lat_delta, longitude + lng_delta, latitude + lat_delta


def public_row(row: dict[str, Any]) -> dict[str, Any] | None:
    from shapely import wkb

    geometry = row.get("geometry")
    if not geometry:
        return None
    point = wkb.loads(bytes(geometry))
    if point.geom_type != "Point":
        return None
    sources = [
        {"dataset": source.get("dataset")}
        for source in (row.get("sources") or [])
        if isinstance(source, dict) and source.get("dataset")
    ]
    return {
        "id": str(row.get("id") or ""),
        "names": row.get("names"),
        "basic_category": row.get("basic_category"),
        "taxonomy": row.get("taxonomy"),
        "categories": row.get("categories"),
        "confidence": row.get("confidence"),
        "websites": row.get("websites"),
        "brand": row.get("brand"),
        "addresses": row.get("addresses"),
        "sources": sources[:8],
        "operating_status": row.get("operating_status"),
        "geometry": {"type": "Point", "coordinates": [point.x, point.y]},
    }


def download_market(market: dict[str, Any], cap: int = RECORDS_PER_MARKET) -> list[dict[str, Any]]:
    from overturemaps import record_batch_reader

    try:
        reader = record_batch_reader(
            "place", bbox=market_bbox(market), release=RELEASE, stac=True,
            connect_timeout=10, request_timeout=45,
        )
    except Exception:
        reader = record_batch_reader(
            "place", bbox=market_bbox(market), release=RELEASE, stac=False,
            connect_timeout=10, request_timeout=45,
        )
    if reader is None:
        return []
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for batch in reader:
        for row in batch.to_pylist():
            if not relevant(row):
                continue
            cleaned = public_row(row)
            record_id = cleaned and cleaned.get("id")
            if cleaned and record_id and record_id not in seen:
                seen.add(str(record_id))
                records.append(cleaned)
            if len(records) >= cap:
                return sorted(records, key=lambda item: item["id"])
    return sorted(records, key=lambda item: item["id"])


def build_payload(today: dt.date, downloader=download_market) -> dict[str, Any]:
    markets = []
    for selected in daily_markets(today.toordinal()):
        records = downloader(selected)
        if not records:
            raise RuntimeError(f"No qualifying records returned for {selected['city']}, {selected['stateCode']}.")
        markets.append({"market": selected, "records": records})
    return {
        "schemaVersion": SCHEMA_VERSION,
        "release": RELEASE,
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "markets": markets,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/latest.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        selected = daily_markets(dt.date.today().toordinal())
        print(json.dumps({"release": RELEASE, "markets": selected}, indent=2))
        return 0
    payload = build_payload(dt.date.today())
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({
        "generatedAt": payload["generatedAt"],
        "release": RELEASE,
        "markets": [f"{item['market']['city']}, {item['market']['stateCode']}" for item in payload["markets"]],
        "records": sum(len(item["records"]) for item in payload["markets"]),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

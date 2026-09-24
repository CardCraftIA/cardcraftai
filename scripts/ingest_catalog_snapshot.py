"""Ingest a CardCraft source snapshot into the canonical Catalog Core.

This command is intentionally maintenance-only. The Streamlit app never calls an
external catalog during this import. Syncs are resumable because every entity is
upserted by a stable canonical/source key.

Example:
  python scripts/ingest_catalog_snapshot.py \
      artifacts/tcgdex/tcgdex_cards.jsonl \
      --source tcgdex \
      --batch-size 200

Required environment variables for a real ingest:
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from supabase import create_client


def normalize_search(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).strip().lower()
    decomposed = unicodedata.normalize("NFKD", text)
    folded = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    folded = re.sub(r"[^0-9a-z\u3040-\u30ff\u3400-\u9fff♀♂]+", " ", folded)
    return re.sub(r"\s+", " ", folded).strip()


def chunks(values: list[dict], size: int) -> Iterable[list[dict]]:
    for offset in range(0, len(values), size):
        yield values[offset : offset + size]


def preferred_localized_name(names: dict) -> str:
    if not isinstance(names, dict):
        return ""
    for language in ("en", "pt", "es", "fr", "de", "it", "ja", "zh-tw", "id", "th"):
        value = str(names.get(language) or "").strip()
        if value:
            return value
    for value in names.values():
        value = str(value or "").strip()
        if value:
            return value
    return ""


def parse_date(value: object) -> str | None:
    value = str(value or "").strip()
    return value if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else None


def integer_or_none(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def data_quality(record: dict) -> int:
    points = 45
    card = record.get("card") or {}
    localizations = record.get("localizations") or []
    variants = record.get("variants") or []
    if record.get("set", {}).get("source_id"):
        points += 10
    if record.get("local_id"):
        points += 8
    if card.get("rarity"):
        points += 5
    if card.get("illustrator"):
        points += 5
    if localizations:
        points += 10
    if any(row.get("image_url") for row in localizations if isinstance(row, dict)):
        points += 7
    if variants:
        points += 5
    if card.get("attributes"):
        points += 5
    return min(100, points)


def canonical_set_key(record: dict) -> str:
    game = str(record.get("game_slug") or "pokemon")
    source_set = str((record.get("set") or {}).get("source_id") or "").strip()
    return f"cc:{game}:set:{source_set}"


def canonical_card_key(record: dict) -> str:
    game = str(record.get("game_slug") or "pokemon")
    source_key = str(record.get("source_key") or "").strip()
    return f"cc:{game}:card:{source_key}"


def build_set_row(record: dict) -> dict:
    set_data = record.get("set") or {}
    names = set_data.get("names") or {}
    card_count = set_data.get("card_count") or {}
    name = preferred_localized_name(names) or str(set_data.get("source_id") or "Unknown set")
    return {
        "game_slug": str(record.get("game_slug") or "pokemon"),
        "canonical_key": canonical_set_key(record),
        "code": str(set_data.get("code") or set_data.get("source_id") or ""),
        "name": name,
        "name_search": normalize_search(name),
        "series": preferred_localized_name(set_data.get("series_names") or {}),
        "release_date": parse_date(set_data.get("release_date")),
        "printed_total": integer_or_none(card_count.get("official")),
        "total": integer_or_none(card_count.get("total")),
        "region": "",
        "status": "active",
        "source_count": 1,
        "attributes": {
            "source_set_id": str(set_data.get("source_id") or ""),
            "series_source_id": str(set_data.get("series_source_id") or ""),
            "localized_names": names,
            "localized_series_names": set_data.get("series_names") or {},
            "third_party": set_data.get("third_party") or {},
            **(set_data.get("attributes") or {}),
        },
        "last_seen_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_card_row(record: dict, set_id: str | None) -> dict:
    card = record.get("card") or {}
    attrs = dict(card.get("attributes") or {})
    return {
        "game_slug": str(record.get("game_slug") or "pokemon"),
        "set_id": set_id,
        "canonical_key": canonical_card_key(record),
        "collector_number": str(record.get("local_id") or ""),
        "local_id": str(record.get("local_id") or ""),
        "category": str(card.get("category") or ""),
        "rarity": str(card.get("rarity") or ""),
        "illustrator": str(card.get("illustrator") or ""),
        "hp": integer_or_none(card.get("hp")),
        "dex_ids": [int(value) for value in (card.get("dex_ids") or []) if isinstance(value, int)],
        "release_date": parse_date((record.get("set") or {}).get("release_date")),
        "status": "active",
        "verification_status": "source_verified",
        "data_quality": data_quality(record),
        "source_count": 1,
        "attributes": attrs,
        "last_seen_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_localization_rows(record: dict, card_id: str) -> list[dict]:
    rows = []
    for localization in record.get("localizations") or []:
        if not isinstance(localization, dict):
            continue
        language = str(localization.get("language") or "").strip().lower()
        name = str(localization.get("name") or "").strip()
        if not language or not name:
            continue
        rows.append(
            {
                "card_id": card_id,
                "language": language,
                "name": name,
                "name_search": normalize_search(name),
                "description": str(localization.get("description") or ""),
                # Rules/attacks that are shared across languages stay once on
                # catalog_cards.attributes. Repeating that payload for every
                # localization would multiply database size dramatically.
                "rules": {},
                "image_url": str(localization.get("image_url") or ""),
                "image_small_url": str(localization.get("image_small_url") or ""),
                "image_status": "remote_reference"
                if localization.get("image_url")
                else "unavailable",
                "source_count": 1,
                "attributes": {
                    "set_name": str(localization.get("set_name") or ""),
                    "series_name": str(localization.get("series_name") or ""),
                    "image_base_url": str(localization.get("image_base_url") or ""),
                },
                "last_seen_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return rows


def build_variant_rows(record: dict, card_id: str) -> list[dict]:
    rows = []
    for variant in record.get("variants") or []:
        if not isinstance(variant, dict):
            continue
        key = str(variant.get("variant_key") or "").strip()
        if not key:
            continue
        rows.append(
            {
                "card_id": card_id,
                "variant_key": key,
                "variant_type": str(variant.get("variant_type") or "normal"),
                "subtype": str(variant.get("subtype") or ""),
                "size": str(variant.get("size") or "standard"),
                "stamps": [str(value) for value in (variant.get("stamps") or [])],
                "external_ids": variant.get("external_ids") or {},
                "attributes": variant.get("attributes") or {},
                "verification_status": "source_verified",
                "source_count": 1,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return rows


def source_record_row(record: dict, source_id: int) -> dict:
    canonical = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "source_id": source_id,
        "source_key": str(record.get("source_key") or ""),
        "language": "und",
        "entity_type": "card",
        "payload_hash": digest,
        # The complete source snapshot is preserved as a build artifact with
        # its own SHA-256. Keeping the full ~source record again in Postgres
        # would duplicate tens of megabytes and reduce the space available for
        # canonical cards, languages and variants.
        "payload": {
            "schema_version": record.get("schema_version"),
            "provider": record.get("provider"),
            "source_key": record.get("source_key"),
            "record_sha256": digest,
        },
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def get_id_map(client, table: str, key_column: str, keys: list[str]) -> dict[str, str]:
    if not keys:
        return {}
    result = client.table(table).select(f"id,{key_column}").in_(key_column, keys).execute()
    return {
        str(row[key_column]): str(row["id"])
        for row in (result.data or [])
        if row.get("id") and row.get(key_column)
    }


def upsert_batches(client, table: str, rows: list[dict], on_conflict: str, batch_size: int) -> None:
    for batch in chunks(rows, batch_size):
        if batch:
            client.table(table).upsert(batch, on_conflict=on_conflict).execute()


def ingest_batch(client, source_id: int, records: list[dict], batch_size: int) -> tuple[int, int]:
    now = datetime.now(timezone.utc).isoformat()

    set_rows_by_key = {canonical_set_key(record): build_set_row(record) for record in records}
    upsert_batches(client, "catalog_sets", list(set_rows_by_key.values()), "canonical_key", batch_size)
    set_ids = get_id_map(client, "catalog_sets", "canonical_key", list(set_rows_by_key))

    card_rows = [
        build_card_row(record, set_ids.get(canonical_set_key(record)))
        for record in records
    ]
    upsert_batches(client, "catalog_cards", card_rows, "canonical_key", batch_size)
    card_ids = get_id_map(
        client,
        "catalog_cards",
        "canonical_key",
        [canonical_card_key(record) for record in records],
    )

    localizations: list[dict] = []
    variants: list[dict] = []
    source_records: list[dict] = []
    source_links: list[dict] = []

    for record in records:
        card_id = card_ids.get(canonical_card_key(record))
        if not card_id:
            continue
        localizations.extend(build_localization_rows(record, card_id))
        variants.extend(build_variant_rows(record, card_id))
        source_records.append(source_record_row(record, source_id))
        source_links.append(
            {
                "source_id": source_id,
                "source_key": str(record.get("source_key") or ""),
                "language": "und",
                "card_id": card_id,
                "confidence": 100,
                "field_coverage": {
                    "identity": True,
                    "set": True,
                    "localizations": bool(record.get("localizations")),
                    "variants": bool(record.get("variants")),
                },
                "last_seen_at": now,
            }
        )

    upsert_batches(
        client,
        "catalog_card_localizations",
        localizations,
        "card_id,language",
        batch_size,
    )
    upsert_batches(
        client,
        "catalog_card_variants",
        variants,
        "card_id,variant_key",
        batch_size,
    )
    upsert_batches(
        client,
        "catalog_source_records",
        source_records,
        "source_id,source_key,language,entity_type",
        batch_size,
    )

    # Source links use nullable target columns; avoid re-inserting an existing
    # card link because ordinary UNIQUE semantics treat NULLs as distinct.
    for link in source_links:
        existing = (
            client.table("catalog_source_links")
            .select("id")
            .eq("source_id", source_id)
            .eq("source_key", link["source_key"])
            .eq("language", "und")
            .eq("card_id", link["card_id"])
            .limit(1)
            .execute()
        )
        if existing.data:
            (
                client.table("catalog_source_links")
                .update({"last_seen_at": now, "field_coverage": link["field_coverage"], "confidence": 100})
                .eq("id", existing.data[0]["id"])
                .execute()
            )
        else:
            client.table("catalog_source_links").insert(link).execute()

    return len(card_rows), len(localizations)


def read_records(path: Path, limit: int = 0) -> Iterable[dict]:
    emitted = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("schema_version") != 1 or record.get("provider") != "tcgdex":
                raise ValueError(f"Unsupported snapshot row at line {line_number}")
            if not record.get("source_key") or not record.get("local_id"):
                raise ValueError(f"Missing identity at line {line_number}")
            yield record
            emitted += 1
            if limit and emitted >= limit:
                return


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--source", default="tcgdex")
    parser.add_argument("--batch-size", type=int, default=150)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    records = list(read_records(args.snapshot, args.limit))
    print(f"Validated {len(records)} snapshot records from {args.snapshot}")

    if args.dry_run:
        print(
            json.dumps(
                {
                    "cards": len(records),
                    "localizations": sum(len(row.get("localizations") or []) for row in records),
                    "variants": sum(len(row.get("variants") or []) for row in records),
                    "sets": len({canonical_set_key(row) for row in records}),
                },
                indent=2,
            )
        )
        return

    url = os.environ.get("SUPABASE_URL", "").strip()
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not service_key:
        raise SystemExit("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")

    client = create_client(url, service_key)
    source_response = (
        client.table("catalog_sources")
        .select("id,code")
        .eq("code", args.source)
        .limit(1)
        .execute()
    )
    if not source_response.data:
        raise SystemExit(f"Catalog source {args.source!r} is not registered")
    source_id = int(source_response.data[0]["id"])

    run = (
        client.table("catalog_sync_runs")
        .insert(
            {
                "source_id": source_id,
                "mode": "full_rebuild",
                "status": "running",
                "discovered_count": len(records),
                "metadata": {"snapshot": args.snapshot.name},
            }
        )
        .execute()
    )
    run_id = str(run.data[0]["id"]) if run.data else ""
    inserted = 0
    localized = 0

    try:
        for batch in chunks(records, max(1, args.batch_size)):
            cards_done, localizations_done = ingest_batch(
                client, source_id, batch, max(1, args.batch_size)
            )
            inserted += cards_done
            localized += localizations_done
            print(f"Ingested {inserted}/{len(records)} canonical card records")
        if run_id:
            (
                client.table("catalog_sync_runs")
                .update(
                    {
                        "status": "completed",
                        "finished_at": datetime.now(timezone.utc).isoformat(),
                        "inserted_count": inserted,
                        "updated_count": localized,
                        "metadata": {
                            "snapshot": args.snapshot.name,
                            "localizations": localized,
                        },
                    }
                )
                .eq("id", run_id)
                .execute()
            )
    except Exception:
        if run_id:
            (
                client.table("catalog_sync_runs")
                .update(
                    {
                        "status": "failed",
                        "finished_at": datetime.now(timezone.utc).isoformat(),
                        "inserted_count": inserted,
                        "updated_count": localized,
                        "error_count": 1,
                    }
                )
                .eq("id", run_id)
                .execute()
            )
        raise


if __name__ == "__main__":
    main()

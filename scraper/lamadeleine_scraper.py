import requests
import sys
import os
from datetime import datetime

from constants import BASE_URL, PER_PAGE, HEADERS
from parser import build_dataframe

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def fetch_all_locations() -> list:
    all_records = []
    page = 1

    while True:
        log(f"Fetching page {page}...")
        resp = requests.get(
            BASE_URL,
            params={"per_page": PER_PAGE, "page": page},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()

        batch = resp.json()
        if not batch:
            break

        all_records.extend(batch)

        total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
        total_items = int(resp.headers.get("X-WP-Total", len(all_records)))
        log(f"  Page {page}/{total_pages} done — {total_items} total locations reported by API.")

        if page >= total_pages:
            break
        page += 1

    log(f"Fetched {len(all_records)} raw records in total.")
    return all_records


def save(df) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    csv_path  = os.path.join(OUTPUT_DIR, "lamadeleine_locations.csv")
    xlsx_path = os.path.join(OUTPUT_DIR, "lamadeleine_locations.xlsx")

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    log(f"Saved -> {csv_path}")

    df.to_excel(xlsx_path, index=False, engine="openpyxl")
    log(f"Saved -> {xlsx_path}")


def log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}")


def main() -> None:
    try:
        records = fetch_all_locations()
        df      = build_dataframe(records)
        save(df)
        log("Done.")
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

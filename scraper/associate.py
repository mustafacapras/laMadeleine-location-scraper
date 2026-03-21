import argparse
import os
import sys
import pandas as pd
from datetime import datetime

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR      = os.path.join(SCRIPT_DIR, "..", "data")
LOCATIONS_CSV = os.path.join(DATA_DIR, "lamadeleine_locations.csv")
OUTPUT_CSV    = os.path.join(DATA_DIR, "reviews_with_locations.csv")

def log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}")


def associate(reviews_path: str) -> None:
    review_cols = [
        "storeID",
        "reviewerID",
        "reviewRating",
        "reviewText",
        "reviewDate",
        "overallRating",
        "numberReviews",
    ]

    output_cols = [
        "storeID",
        "locationName",
        "city",
        "state",
        "postalCode",
        "streetAddress",
        "streetAddress2",
        "fullAddress",
        "reviewerID",
        "reviewRating",
        "reviewText",
        "reviewDate",
        "overallRating",
        "numberReviews",
    ]
    if not os.path.exists(reviews_path):
        print(f"ERROR: Reviews file not found: {reviews_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(LOCATIONS_CSV):
        print(f"ERROR: Locations file not found: {LOCATIONS_CSV}", file=sys.stderr)
        print("  Run first: python scraper/lamadeleine_scraper.py", file=sys.stderr)
        sys.exit(1)

    log(f"Loading reviews from: {reviews_path}")
    reviews = pd.read_csv(reviews_path)
    log(f"  {len(reviews):,} total rows loaded.")

    reviews = reviews[
        reviews["name"].str.contains("la Madeleine", case=False, na=False)
    ].copy()
    log(f"  {len(reviews):,} la Madeleine rows after filtering.")

    reviews["storeID"] = reviews["website"].str.extract(r"/locations/([^/?#\s]+)")

    before = len(reviews)
    reviews = reviews[
        reviews["storeID"].str.match(r"^[a-z][a-z0-9-]+$", na=False)
    ].copy()
    dropped = before - len(reviews)
    if dropped:
        log(f"  Dropped {dropped} rows with unrecognised website URLs.")

    log(f"  {reviews['storeID'].nunique()} unique locations found in reviews.")

    log(f"Loading locations from: {LOCATIONS_CSV}")
    locations = pd.read_csv(LOCATIONS_CSV)
    log(f"  {len(locations)} locations loaded.")

    reviews_slim = reviews[review_cols].copy()
    reviews_slim["storeID"] = reviews_slim["storeID"].astype(str)
    locations["storeID"]    = locations["storeID"].astype(str)

    joined = reviews_slim.merge(locations, on="storeID", how="left")[output_cols]

    unmatched = joined["locationName"].isna().sum()
    if unmatched:
        log(f"  WARNING: {unmatched} reviews could not be matched to a location.")
    else:
        log("  All reviews matched successfully.")

    os.makedirs(DATA_DIR, exist_ok=True)
    joined.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    log(f"Saved -> {OUTPUT_CSV}")
    log(f"Done. {len(joined):,} rows | {joined['storeID'].nunique()} locations.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Join Google Reviews with scraped la Madeleine location data."
    )
    parser.add_argument("--reviews", required=True, help="Path to googleReview.csv")
    args = parser.parse_args()
    associate(args.reviews)

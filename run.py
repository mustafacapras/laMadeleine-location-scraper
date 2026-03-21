import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scraper"))

from lamadeleine_scraper import fetch_all_locations, save, log
from parser import build_dataframe
from associate import associate

DEFAULT_REVIEWS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "", "googleReview.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run scraper then associate reviews.")
    parser.add_argument("--reviews", default=DEFAULT_REVIEWS, help="Path to googleReview.csv")
    args = parser.parse_args()

    log("Step 1: Scraping locations...")
    records = fetch_all_locations()
    df = build_dataframe(records)
    save(df)

    log("Step 2: Associating reviews...")
    associate(args.reviews)

if __name__ == "__main__":
    main()
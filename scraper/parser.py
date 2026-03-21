import pandas as pd
from constants import STATE_ABBR, REQUIRED_COLUMNS


def clean(val) -> str:
    return str(val).strip() if val is not None else ""


def normalize_state(raw_state: str) -> str:
    s = raw_state.strip()
    if len(s) == 2:
        return s.upper()
    return STATE_ABBR.get(s, s)


def parse_location(raw: dict) -> dict:
    hero = raw.get("acf", {}).get("locationHero", {})

    store_id = clean(raw.get("slug", ""))
    street1  = clean(hero.get("addressLine1", ""))
    street2  = clean(hero.get("addressLine2", ""))
    city     = clean(hero.get("city", ""))
    state    = normalize_state(hero.get("state", ""))
    zipcode  = clean(hero.get("zip", ""))

    parts = [p for p in [street1, street2, city, state, zipcode] if p]

    return {
        "locationName":   clean(hero.get("storeName", "")),
        "postalCode":     zipcode,
        "streetAddress":  street1,
        "streetAddress2": street2,
        "fullAddress":    ", ".join(parts),
        "city":           city,
        "state":          state,
        "storeID":        store_id,
    }


def build_dataframe(records: list) -> pd.DataFrame:
    rows = [parse_location(r) for r in records]
    df = pd.DataFrame(rows, columns=REQUIRED_COLUMNS)

    before = len(df)
    df = df.drop_duplicates(subset=["storeID"]).reset_index(drop=True)
    df = df[df["state"].str.match(r"^[A-Z]{2}$", na=False)].reset_index(drop=True)
    print(f"Kept {len(df)} unique US locations (dropped {before - len(df)} duplicates/non-US).")
    return df

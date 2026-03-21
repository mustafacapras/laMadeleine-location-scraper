# la Madeleine Location Scraper

Extracts all US restaurant locations from [lamadeleine.com/locations](https://lamadeleine.com/locations) and associates them with Google Reviews data for per-location sentiment analysis.

Built as part of the **Bain & Company WDF Specialist Technical Assessment**.

---

## How it works

Using Chrome DevTools (Network → Fetch/XHR), the page was found to call:

```
GET https://lamadeleine.com/wp-json/wp/v2/restaurant-locations?per_page=150
```

This WordPress REST API endpoint returns all location records as JSON.
The scraper calls it directly instead of parsing HTML — faster and more stable.
Pagination is handled automatically using the `X-WP-TotalPages` response header.

---

## Output fields

| Field | Description |
|---|---|
| `locationName` | Restaurant name |
| `postalCode` | ZIP code |
| `streetAddress` | Primary street address |
| `streetAddress2` | Suite / unit (if any) |
| `fullAddress` | Full formatted address |
| `city` | City |
| `state` | 2-letter US state code |
| `storeID` | Unique store identifier (URL slug) |

---

## Local setup

```bash
# 1. Create and activate virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Step 1 — Extract location data

```bash
python scraper/lamadeleine_scraper.py
```

Output written to `data/`:
- `lamadeleine_locations.csv`
- `lamadeleine_locations.xlsx`

### Step 2 — Associate with Google Reviews

Place the provided `googleReview.csv` file in the project root, then run:

```bash
python scraper/associate.py --reviews googleReview.csv
```

Output written to `data/`:
- `reviews_with_locations.csv`

---

## GitHub Actions

Two triggers are configured:

| Trigger | When |
|---|---|
| **Manual** | Actions tab → Run workflow |
| **Quarterly** | 1st of January, April, July, October at 06:00 UTC |

On each run the scraper executes and updated output files are committed
back to the repository automatically.

> **Important:** Go to **Settings → Actions → General → Workflow permissions**
> and select **Read and write permissions** before the first run.

---

## Repository structure

```
├── .github/
│   └── workflows/
│       └── scrape.yml              # GitHub Actions workflow
├── scraper/
│   ├── lamadeleine_scraper.py      # Extracts location data from API
│   └── associate.py                # Joins reviews with location data
├── data/
│   ├── lamadeleine_locations.csv   # Location data (87 US locations)
│   ├── lamadeleine_locations.xlsx  # Location data (Excel format)
│   └── reviews_with_locations.csv  # Google Reviews joined to locations
├── .gitignore
├── requirements.txt
└── README.md
```

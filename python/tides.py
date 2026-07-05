from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import urlopen
from urllib.error import URLError

LOCATION_NAME = "Westward Ho!/Sandymere"
LATITUDE = 51.0308
LONGITUDE = -4.2141

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_PATH = DATA_DIR / "tides.json"

# Tides API: free, no key required
API_URL = (
    "https://api.tides.noaa.gov/api/prod/datagetter"
    f"?station=8458479&date=today&product=predictions&datum=MLLW&units=metric&format=json&application=claude_family_dashboard"
)


def fetch_tides() -> dict[str, Any]:
    """Fetch tide predictions from NOAA API."""
    with urlopen(API_URL, timeout=10) as response:
        raw = json.loads(response.read())

    predictions = raw.get("predictions", [])
    
    if not predictions:
        raise ValueError("No tide predictions returned from API")

    # Extract high and low tides for today
    tides = []
    for pred in predictions[:6]:  # Get next 6 predictions
        t = pred["t"]
        v = float(pred["v"])
        
        # Parse ISO timestamp to extract time
        dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
        time_str = dt.strftime("%H:%M")
        
        # Determine if high or low based on whether it's a local extremum
        # For now, alternate High/Low (NOAA provides them in order)
        tide_type = "High" if len(tides) % 2 == 0 else "Low"
        
        tides.append({
            "type": tide_type,
            "time": time_str,
            "height_m": round(v, 2)
        })

    return {
        "location": LOCATION_NAME,
        "tides": tides,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def write_tides_json(tides: dict[str, Any]) -> None:
    """Write tides to data/tides.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(tides, indent=2) + "\n")


def main() -> None:
    """Fetch tides and write to disk."""
    try:
        tides = fetch_tides()
        write_tides_json(tides)
        print(f"[tides] Updated: {len(tides['tides'])} tide predictions")
        exit(0)
    except Exception as error:
        print(f"[tides] Fetch failed, keeping existing data: {error}")
        exit(0)


if __name__ == "__main__":
    main()

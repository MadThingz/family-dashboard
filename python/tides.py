from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import urlopen

# -----------------------------
# Location: Westward Ho!
# -----------------------------
LOCATION_NAME = "Westward Ho!, England"
LATITUDE = 51.0308
LONGITUDE = -4.2141

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_PATH = DATA_DIR / "tides.json"

# -----------------------------
# WorldTides API (your key)
# -----------------------------
API_KEY = "19534665-2167-494d-b7eb-9c56742c321b"

API_URL = (
    "https://www.worldtides.info/api/v2?"
    f"extremes&lat={LATITUDE}&lon={LONGITUDE}&key={API_KEY}"
)

def fetch_tides() -> dict[str, Any]:
    """Fetch tide extremes (high/low) for Westward Ho!."""
    with urlopen(API_URL, timeout=10) as response:
        raw = json.loads(response.read())

    extremes = raw.get("extremes", [])
    if not extremes:
        raise ValueError("No tide data returned from WorldTides")

    tides = []
    for event in extremes:
        dt = datetime.fromtimestamp(event["dt"], tz=timezone.utc)
        time_str = dt.strftime("%H:%M")

        tides.append({
            "type": event["type"],          # "High" or "Low"
            "time": time_str,               # formatted time
            "height_m": round(event["height"], 2)
        })

    return {
        "location": LOCATION_NAME,
        "tides": tides,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def write_tides_json(tides: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(tides, indent=2) + "\n")


def main() -> None:
    try:
        tides = fetch_tides()
        write_tides_json(tides)
        print(f"[tides] Updated: {len(tides['tides'])} tide events")
        exit(0)
    except Exception as error:
        print(f"[tides] Fetch failed, keeping existing data: {error}")
        exit(0)


if __name__ == "__main__":
    main()

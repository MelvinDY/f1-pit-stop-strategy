"""
Fetch and cache F1 race data from the Ergast API for seasons 2011-2023.

Usage:
    python data/fetch_data.py

On first run: queries the API and caches responses as JSON under data/raw/.
On subsequent runs: reads from cache — no API calls made.
Outputs: data/pit_stops.csv, data/lap_times.csv, data/results.csv
"""

import sys
from pathlib import Path

import pandas as pd

# Allow imports from src/
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.api import get_drivers, get_lap_times, get_pit_stops, get_races, get_results

SEASONS = list(range(2011, 2024))
DATA_DIR = Path(__file__).parent

# ── progress helpers ──────────────────────────────────────────────────────────

def _bar(done: int, total: int, width: int = 20) -> str:
    filled = int(width * done / total) if total else 0
    return f"[{'█' * filled}{'░' * (width - filled)}] {done}/{total}"

def _pct(done: int, total: int) -> str:
    return f"{100 * done / total:.0f}%" if total else "0%"

def _progress(season: int, step: str, round_done: int = 0, round_total: int = 0):
    season_idx = SEASONS.index(season) + 1
    season_total = len(SEASONS)
    season_pct = _pct(season_idx - 1, season_total)  # pct before this season completes
    if round_total:
        print(
            f"  [{season_pct} overall | season {season_idx}/{season_total}] "
            f"{step}: {_bar(round_done, round_total)} ({_pct(round_done, round_total)})",
            end="\r", flush=True,
        )
    else:
        print(f"  [{season_pct} overall | season {season_idx}/{season_total}] {step}...",
              end=" ", flush=True)

# ── fetchers ──────────────────────────────────────────────────────────────────

def fetch_races(season: int) -> list[dict]:
    rows = []
    for race in get_races(season):
        rows.append({
            "season":       int(race["season"]),
            "round":        int(race["round"]),
            "race_name":    race["raceName"],
            "circuit_id":   race["Circuit"]["circuitId"],
            "circuit_name": race["Circuit"]["circuitName"],
            "date":         race.get("date"),
        })
    return rows


def fetch_results(season: int) -> list[dict]:
    rows = []
    for race in get_results(season):
        for res in race.get("Results", []):
            rows.append({
                "season":      int(race["season"]),
                "round":       int(race["round"]),
                "driver_id":   res["Driver"]["driverId"],
                "constructor": res["Constructor"]["constructorId"],
                "grid":        int(res.get("grid", 0)),
                "position":    res.get("position"),
                "status":      res.get("status"),
                "laps":        int(res.get("laps", 0)),
                "points":      float(res.get("points", 0)),
            })
    return rows


def fetch_pit_stops(season: int, races: list[dict]) -> list[dict]:
    rows = []
    total = len(races)
    skipped = []
    for i, race in enumerate(races):
        round_num = race["round"]
        _progress(season, "pit stops", i, total)
        try:
            for race_obj in get_pit_stops(season, round_num):
                for stop in race_obj.get("PitStops", []):
                    rows.append({
                        "season":    season,
                        "round":     round_num,
                        "driver_id": stop["driverId"],
                        "stop":      int(stop["stop"]),
                        "lap":       int(stop["lap"]),
                        "time":      stop.get("time"),
                        "duration":  stop.get("duration"),
                    })
        except (RuntimeError, Exception) as e:
            skipped.append(round_num)
            print(f"\n  ⚠ Skipped {season} R{round_num} pit stops ({e})")
    _progress(season, "pit stops", total, total)
    print()
    if skipped:
        print(f"  ⚠ Skipped rounds: {skipped} (rate limited — re-run later to fill gaps)")
    return rows


def fetch_lap_times(season: int, races: list[dict]) -> list[dict]:
    rows = []
    total = len(races)
    skipped = []
    for i, race in enumerate(races):
        round_num = race["round"]
        _progress(season, "lap times", i, total)
        try:
            for race_obj in get_lap_times(season, round_num):
                for lap_obj in race_obj.get("Laps", []):
                    lap_num = int(lap_obj["number"])
                    for timing in lap_obj.get("Timings", []):
                        rows.append({
                            "season":    season,
                            "round":     round_num,
                            "lap":       lap_num,
                            "driver_id": timing["driverId"],
                            "position":  int(timing.get("position", 0)),
                            "time":      timing.get("time"),
                        })
        except (RuntimeError, Exception) as e:
            skipped.append(round_num)
            print(f"\n  ⚠ Skipped {season} R{round_num} lap times ({e})")
    _progress(season, "lap times", total, total)
    print()
    if skipped:
        print(f"  ⚠ Skipped rounds: {skipped} (rate limited — re-run later to fill gaps)")
    return rows


def fetch_drivers(season: int) -> list[dict]:
    rows = []
    for d in get_drivers(season):
        rows.append({
            "season":       season,
            "driver_id":    d["driverId"],
            "given_name":   d.get("givenName"),
            "family_name":  d.get("familyName"),
            "nationality":  d.get("nationality"),
        })
    return rows


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    all_races = []
    all_results = []
    all_pit_stops = []
    all_lap_times = []
    all_drivers = []

    total_seasons = len(SEASONS)
    for idx, season in enumerate(SEASONS):
        overall_pct = _pct(idx, total_seasons)
        print(f"\n{'─' * 50}")
        print(f"Season {season}  [{idx + 1}/{total_seasons}]  {overall_pct} overall")
        print(f"{'─' * 50}")

        _progress(season, "races")
        races = fetch_races(season)
        all_races.extend(races)
        print(f"✓  {len(races)} races")

        _progress(season, "results")
        results = fetch_results(season)
        all_results.extend(results)
        print(f"✓  {len(results)} results")

        pit_stops = fetch_pit_stops(season, races)
        all_pit_stops.extend(pit_stops)
        print(f"  └─ {len(pit_stops)} pit stops collected")

        lap_times = fetch_lap_times(season, races)
        all_lap_times.extend(lap_times)
        print(f"  └─ {len(lap_times):,} lap time records collected")

        _progress(season, "drivers")
        drivers = fetch_drivers(season)
        all_drivers.extend(drivers)
        print(f"✓  {len(set(d['driver_id'] for d in drivers))} drivers")

    print(f"\n{'─' * 50}")
    print("100% — Saving CSVs...")
    pd.DataFrame(all_races).to_csv(DATA_DIR / "races.csv", index=False)
    pd.DataFrame(all_results).to_csv(DATA_DIR / "results.csv", index=False)
    pd.DataFrame(all_pit_stops).to_csv(DATA_DIR / "pit_stops.csv", index=False)
    pd.DataFrame(all_lap_times).to_csv(DATA_DIR / "lap_times.csv", index=False)
    pd.DataFrame(all_drivers).drop_duplicates(subset=["driver_id"]).to_csv(
        DATA_DIR / "drivers.csv", index=False
    )

    print("\nDone.")
    print(f"  races.csv:     {len(all_races):,} rows")
    print(f"  results.csv:   {len(all_results):,} rows")
    print(f"  pit_stops.csv: {len(all_pit_stops):,} rows")
    print(f"  lap_times.csv: {len(all_lap_times):,} rows")
    print(f"  drivers.csv:   {pd.read_csv(DATA_DIR / 'drivers.csv').shape[0]:,} rows")


if __name__ == "__main__":
    main()

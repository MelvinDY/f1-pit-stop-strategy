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

SEASONS = range(2011, 2024)
DATA_DIR = Path(__file__).parent


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
    for race in races:
        round_num = race["round"]
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
    return rows


def fetch_lap_times(season: int, races: list[dict]) -> list[dict]:
    rows = []
    for race in races:
        round_num = race["round"]
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


def main():
    all_races = []
    all_results = []
    all_pit_stops = []
    all_lap_times = []
    all_drivers = []

    for season in SEASONS:
        print(f"Season {season}...")

        races = fetch_races(season)
        all_races.extend(races)
        print(f"  {len(races)} races")

        results = fetch_results(season)
        all_results.extend(results)
        print(f"  {len(results)} results")

        pit_stops = fetch_pit_stops(season, races)
        all_pit_stops.extend(pit_stops)
        print(f"  {len(pit_stops)} pit stops")

        lap_times = fetch_lap_times(season, races)
        all_lap_times.extend(lap_times)
        print(f"  {len(lap_times)} lap time records")

        drivers = fetch_drivers(season)
        all_drivers.extend(drivers)
        print(f"  {len(set(d['driver_id'] for d in drivers))} drivers")

    print("\nSaving CSVs...")
    pd.DataFrame(all_races).to_csv(DATA_DIR / "races.csv", index=False)
    pd.DataFrame(all_results).to_csv(DATA_DIR / "results.csv", index=False)
    pd.DataFrame(all_pit_stops).to_csv(DATA_DIR / "pit_stops.csv", index=False)
    pd.DataFrame(all_lap_times).to_csv(DATA_DIR / "lap_times.csv", index=False)
    pd.DataFrame(all_drivers).drop_duplicates(subset=["driver_id"]).to_csv(
        DATA_DIR / "drivers.csv", index=False
    )

    print("Done.")
    print(f"  races.csv:     {len(all_races):,} rows")
    print(f"  results.csv:   {len(all_results):,} rows")
    print(f"  pit_stops.csv: {len(all_pit_stops):,} rows")
    print(f"  lap_times.csv: {len(all_lap_times):,} rows")
    print(f"  drivers.csv:   {pd.read_csv(DATA_DIR / 'drivers.csv').shape[0]:,} rows")


if __name__ == "__main__":
    main()

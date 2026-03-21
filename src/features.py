"""
Feature engineering pipeline for F1 pit stop strategy analysis.

Usage:
    from src.features import build_features
    features_df = build_features(pit, laps, races)
"""

import pandas as pd
import numpy as np

# Tyre compound standardisation map (defined in notebook 02)
COMPOUND_MAP = {
    'SOFT':         'Soft',
    'SUPERSOFT':    'Soft',
    'ULTRASOFT':    'Soft',
    'HYPERSOFT':    'Soft',
    'MEDIUM':       'Medium',
    'HARD':         'Hard',
    'INTERMEDIATE': 'Intermediate',
    'WET':          'Wet',
    'FULL WET':     'Wet',
}

COMPOUND_HARDNESS = {
    'Soft':         1,
    'Medium':       2,
    'Hard':         3,
    'Intermediate': 4,
    'Wet':          5,
}

STREET_CIRCUITS = {
    'monaco', 'baku', 'albert_park', 'marina_bay', 'jeddah', 'miami', 'las_vegas'
}
HIGH_DEG_CIRCUITS = {
    'bahrain', 'catalunya', 'istanbul', 'sakhir', 'portimao', 'shanghai'
}


def _stop_lap_pct(pit: pd.DataFrame, laps: pd.DataFrame) -> pd.Series:
    """Pit lap as a fraction of total race laps — normalises across circuits."""
    total = laps.groupby(['season', 'round'])['lap'].max().reset_index(name='total_laps')
    df = pit.merge(total, on=['season', 'round'], how='left')
    return df['lap'] / df['total_laps']


def _gap_to_car_ahead(pit: pd.DataFrame, laps: pd.DataFrame) -> pd.Series:
    """
    Approximate gap to the car ahead at the pit lap.
    Computed as the difference in lap number between the driver and the car
    one position ahead, using lap_times position data.
    Returns NaN where position data is unavailable.
    """
    # Get position of each driver on each lap
    pos = laps[['season', 'round', 'lap', 'driver_id', 'position']].copy()

    # For each pit stop, look up the driver's position on lap L-1
    pit_lookup = pit[['season', 'round', 'driver_id', 'lap']].copy()
    pit_lookup['lookup_lap'] = pit_lookup['lap'] - 1

    merged = pit_lookup.merge(
        pos.rename(columns={'driver_id': 'driver_id', 'position': 'pos_driver'}),
        left_on=['season', 'round', 'driver_id', 'lookup_lap'],
        right_on=['season', 'round', 'driver_id', 'lap'],
        how='left'
    )

    # Find the driver in P-1 on that lap
    pos_ahead = pos.copy()
    pos_ahead['position_ahead'] = pos_ahead['position'] - 1
    merged2 = merged.merge(
        pos_ahead[['season', 'round', 'lap', 'position_ahead', 'driver_id']].rename(
            columns={'driver_id': 'driver_ahead', 'lap': 'lap_y2'}
        ),
        left_on=['season', 'round', 'lookup_lap', 'pos_driver'],
        right_on=['season', 'round', 'lap_y2', 'position_ahead'],
        how='left'
    )

    # Gap proxy: difference in cumulative lap time is not available from Ergast;
    # use position difference as a binary proxy (0 = P1, no car ahead)
    gap = (merged2['pos_driver'] - 1).clip(lower=0).reset_index(drop=True)
    return gap


def _is_undercut_attempt(pit: pd.DataFrame, laps: pd.DataFrame) -> pd.Series:
    """
    Binary flag: 1 if the driver pitted 1–3 laps before the car they were
    directly racing (the car one position ahead at pit entry).

    Logic:
    1. For each pit stop at lap L, find the car one position ahead (rival).
    2. Check if the rival pitted in the window [L+1, L+3].
    3. If yes → this driver undercut the rival → flag = 1.
    """
    pos = laps[['season', 'round', 'lap', 'driver_id', 'position']].copy()

    # Driver's position at lap L-1
    pit_with_pos = pit[['season', 'round', 'driver_id', 'lap']].copy()
    pit_with_pos = pit_with_pos.merge(
        pos.rename(columns={'position': 'pos_at_pit'}),
        left_on=['season', 'round', 'driver_id', 'lap'],
        right_on=['season', 'round', 'driver_id', 'lap'],
        how='left'
    )

    # Find rival: driver in pos_at_pit - 1 on lap L-1
    rival_pos = pit_with_pos[['season', 'round', 'lap', 'pos_at_pit']].copy()
    rival_pos['rival_position'] = rival_pos['pos_at_pit'] - 1
    rival_pos = rival_pos.merge(
        pos[['season', 'round', 'lap', 'position', 'driver_id']].rename(
            columns={'driver_id': 'rival_id', 'position': 'rival_position'}
        ),
        on=['season', 'round', 'lap', 'rival_position'],
        how='left'
    )

    # Check if rival pitted in [L+1, L+3]
    pit_laps = pit.groupby(['season', 'round', 'driver_id'])['lap'].apply(list).reset_index(name='stop_laps')

    def rival_pitted_soon(row):
        rival = row.get('rival_id')
        if pd.isna(rival):
            return 0
        key = (row['season'], row['round'], rival)
        rival_stops = pit_laps[
            (pit_laps['season'] == row['season']) &
            (pit_laps['round'] == row['round']) &
            (pit_laps['driver_id'] == rival)
        ]['stop_laps'].values
        if len(rival_stops) == 0:
            return 0
        window = range(row['lap'] + 1, row['lap'] + 4)
        return int(any(sl in window for sl in rival_stops[0]))

    flags = rival_pos.apply(rival_pitted_soon, axis=1)
    return flags.reset_index(drop=True)


def _team_avg_stop_time(pit: pd.DataFrame) -> pd.Series:
    """
    Rolling mean pit stop duration per constructor per season.
    Uses expanding() to prevent data leakage — each stop's value reflects
    only stops that occurred before it in the season.
    """
    pit_sorted = pit.sort_values(['season', 'constructor', 'round', 'stop'])
    rolling = (
        pit_sorted.groupby(['season', 'constructor'])['duration_s']
        .expanding()
        .mean()
        .reset_index(level=[0, 1], drop=True)
    )
    # Reindex to match original pit row order
    return rolling.reindex(pit.index)


def _prior_stops(pit: pd.DataFrame) -> pd.Series:
    """Number of stops already made before this one in the same race."""
    return pit['stop'] - 1


def _circuit_type(pit: pd.DataFrame) -> pd.Series:
    """Classify each circuit as street, high_degradation, or high_speed."""
    def classify(cid):
        if cid in STREET_CIRCUITS:
            return 'street'
        if cid in HIGH_DEG_CIRCUITS:
            return 'high_degradation'
        return 'high_speed'
    return pit['circuit_id'].apply(classify)


def build_features(
    pit: pd.DataFrame,
    laps: pd.DataFrame,
    races: pd.DataFrame,
    results: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the full feature matrix from cleaned data.

    Parameters
    ----------
    pit     : cleaned pit_stops DataFrame (output of notebook 02)
    laps    : cleaned lap_times DataFrame
    races   : raw races DataFrame (for circuit_id)
    results : cleaned results DataFrame (for constructor)

    Returns
    -------
    DataFrame with all 7 features + target variable.
    """
    df = pit.copy()

    # Merge circuit_id and constructor if not already present
    if 'circuit_id' not in df.columns:
        df = df.merge(races[['season', 'round', 'circuit_id']], on=['season', 'round'], how='left')
    if 'constructor' not in df.columns:
        cmap = results[['season', 'round', 'driver_id', 'constructor']].drop_duplicates()
        df = df.merge(cmap, on=['season', 'round', 'driver_id'], how='left')

    # 1. stop_lap_pct
    total_laps = laps.groupby(['season', 'round'])['lap'].max().reset_index(name='total_laps')
    df = df.merge(total_laps, on=['season', 'round'], how='left')
    df['stop_lap_pct'] = df['lap'] / df['total_laps']

    # 2. gap_to_car_ahead (position-based proxy)
    pos = laps[['season', 'round', 'lap', 'driver_id', 'position']].copy()
    pos_at_pit = pos.rename(columns={'lap': 'lap', 'position': 'pos_at_pit'})
    df = df.merge(
        pos_at_pit,
        left_on=['season', 'round', 'driver_id', 'lap'],
        right_on=['season', 'round', 'driver_id', 'lap'],
        how='left'
    )
    df['gap_to_car_ahead'] = (df['pos_at_pit'] - 1).clip(lower=0).fillna(0)

    # 3. is_undercut_attempt
    pit_laps_map = (
        pit.groupby(['season', 'round', 'driver_id'])['lap']
        .apply(set)
        .to_dict()
    )

    def undercut_flag(row):
        if pd.isna(row.get('pos_at_pit')) or row['pos_at_pit'] <= 1:
            return 0
        rival_pos = row['pos_at_pit'] - 1
        rivals = pos[
            (pos['season'] == row['season']) &
            (pos['round'] == row['round']) &
            (pos['lap'] == row['lap'] - 1) &
            (pos['position'] == rival_pos)
        ]['driver_id'].values
        if len(rivals) == 0:
            return 0
        rival_id = rivals[0]
        rival_stops = pit_laps_map.get((row['season'], row['round'], rival_id), set())
        window = {row['lap'] + 1, row['lap'] + 2, row['lap'] + 3}
        return int(bool(rival_stops & window))

    df['is_undercut_attempt'] = df.apply(undercut_flag, axis=1)

    # 4. compound_hardness (placeholder — real compound joined via FastF1 in notebook 04)
    if 'compound' in df.columns:
        df['compound'] = df['compound'].str.upper().map(COMPOUND_MAP)
        df['compound_hardness'] = df['compound'].map(COMPOUND_HARDNESS)
    else:
        # Proxy: stop number approximates compound progression
        df['compound_hardness'] = df['stop'].clip(1, 3)

    # 5. team_avg_stop_time (expanding mean — leakage-free)
    df = df.sort_values(['season', 'constructor', 'round', 'stop'])
    df['team_avg_stop_time'] = (
        df.groupby(['season', 'constructor'])['duration_s']
        .expanding()
        .mean()
        .reset_index(level=[0, 1], drop=True)
        .reindex(df.index)
    )
    df = df.sort_index()

    # 6. prior_stops
    df['prior_stops'] = (df['stop'] - 1).clip(lower=0)

    # 7. circuit_type
    df['circuit_type'] = df['circuit_id'].apply(
        lambda cid: 'street' if cid in STREET_CIRCUITS
        else ('high_degradation' if cid in HIGH_DEG_CIRCUITS else 'high_speed')
    )

    feature_cols = [
        'season', 'round', 'driver_id',
        'stop_lap_pct', 'gap_to_car_ahead', 'is_undercut_attempt',
        'compound_hardness', 'team_avg_stop_time', 'prior_stops',
        'circuit_type', 'position_gained',
    ]

    available = [c for c in feature_cols if c in df.columns]
    return df[available].reset_index(drop=True)

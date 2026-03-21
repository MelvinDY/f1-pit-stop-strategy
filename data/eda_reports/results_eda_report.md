# EDA Report: results
> Generated: 2026-03-22 00:54

## Basic Information
- **File:** `results.csv`
- **Size:** 244.7 KB
- **Format:** CSV (general scientific data)

## Data Structure
- **Rows:** 5,497
- **Columns:** 9
- **Duplicate rows:** 0

### Column Types
|             | 0       |
|:------------|:--------|
| season      | int64   |
| round       | int64   |
| driver_id   | object  |
| constructor | object  |
| grid        | int64   |
| position    | int64   |
| status      | object  |
| laps        | int64   |
| points      | float64 |

## Missing Values
No missing values.

## Statistical Summary
|             |   count |   unique | top      |   freq |       mean |       std |   min |   25% |   50% |   75% |   max |
|:------------|--------:|---------:|:---------|-------:|-----------:|----------:|------:|------:|------:|------:|------:|
| season      |    5497 |      nan | nan      |    nan | 2016.94    |   3.80658 |  2011 |  2014 |  2017 |  2020 |  2023 |
| round       |    5497 |      nan | nan      |    nan |   10.6098  |   5.88125 |     1 |     6 |    11 |    16 |    22 |
| driver_id   |    5497 |       74 | hamilton |    261 |  nan       | nan       |   nan |   nan |   nan |   nan |   nan |
| constructor |    5497 |       22 | red_bull |    524 |  nan       | nan       |   nan |   nan |   nan |   nan |   nan |
| grid        |    5497 |      nan | nan      |    nan |   10.8632  |   6.187   |     0 |     6 |    11 |    16 |    24 |
| position    |    5497 |      nan | nan      |    nan |   11.0433  |   6.14522 |     1 |     6 |    11 |    16 |    24 |
| status      |    5497 |       77 | Finished |   2806 |  nan       | nan       |   nan |   nan |   nan |   nan |   nan |
| laps        |    5497 |      nan | nan      |    nan |   53.4239  |  17.7396  |     0 |    51 |    56 |    66 |    87 |
| points      |    5497 |      nan | nan      |    nan |    4.84019 |   7.15279 |     0 |     0 |     0 |     8 |    50 |

## Key Findings
- 5,497 total records across 9 columns
- 0 duplicate rows detected
- No missing values

## Recommendations
- Apply domain-specific filters (safety car laps, DNFs, formation laps)
- Standardise categorical labels before feature engineering
- Validate join keys across tables (season + round + driver_id)
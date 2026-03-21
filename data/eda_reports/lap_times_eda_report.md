# EDA Report: lap_times
> Generated: 2026-03-22 00:54

## Basic Information
- **File:** `lap_times.csv`
- **Size:** 8715.9 KB
- **Format:** CSV (general scientific data)

## Data Structure
- **Rows:** 293,710
- **Columns:** 6
- **Duplicate rows:** 0

### Column Types
|           | 0      |
|:----------|:-------|
| season    | int64  |
| round     | int64  |
| lap       | int64  |
| driver_id | object |
| position  | int64  |
| time      | object |

## Missing Values
No missing values.

## Statistical Summary
|           |   count |   unique | top      |   freq |      mean |       std |   min |   25% |   50% |   75% |   max |
|:----------|--------:|---------:|:---------|-------:|----------:|----------:|------:|------:|------:|------:|------:|
| season    |  293710 |      nan | nan      |    nan | 2016.98   |   3.81863 |  2011 |  2014 |  2017 |  2020 |  2023 |
| round     |  293710 |      nan | nan      |    nan |   10.5985 |   5.87654 |     1 |     6 |    10 |    16 |    22 |
| lap       |  293710 |      nan | nan      |    nan |   30.1599 |  18.2398  |     1 |    15 |    29 |    44 |    87 |
| driver_id |  293710 |       74 | hamilton |  14944 |  nan      | nan       |   nan |   nan |   nan |   nan |   nan |
| position  |  293710 |      nan | nan      |    nan |   10.0301 |   5.65579 |     0 |     5 |    10 |    15 |    24 |
| time      |  293710 |    66439 | 1:38.525 |     21 |  nan      | nan       |   nan |   nan |   nan |   nan |   nan |

## Key Findings
- 293,710 total records across 6 columns
- 0 duplicate rows detected
- No missing values

## Recommendations
- Apply domain-specific filters (safety car laps, DNFs, formation laps)
- Standardise categorical labels before feature engineering
- Validate join keys across tables (season + round + driver_id)
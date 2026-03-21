# EDA Report: pit_stops
> Generated: 2026-03-22 00:54

## Basic Information
- **File:** `pit_stops.csv`
- **Size:** 381.3 KB
- **Format:** CSV (general scientific data)

## Data Structure
- **Rows:** 10,546
- **Columns:** 7
- **Duplicate rows:** 0

### Column Types
|           | 0      |
|:----------|:-------|
| season    | int64  |
| round     | int64  |
| driver_id | object |
| stop      | int64  |
| lap       | int64  |
| time      | object |
| duration  | object |

## Missing Values
|          |   missing |   pct |
|:---------|----------:|------:|
| duration |        12 |  0.11 |

## Statistical Summary
|           |   count |   unique | top      |   freq |       mean |        std |   min |   25% |   50% |   75% |   max |
|:----------|--------:|---------:|:---------|-------:|-----------:|-----------:|------:|------:|------:|------:|------:|
| season    |   10546 |      nan | nan      |    nan | 2016.64    |   3.93261  |  2011 |  2013 |  2016 |  2020 |  2023 |
| round     |   10546 |      nan | nan      |    nan |   10.4151  |   5.8949   |     1 |     5 |    10 |    15 |    22 |
| driver_id |   10546 |       73 | hamilton |    515 |  nan       | nan        |   nan |   nan |   nan |   nan |   nan |
| stop      |   10546 |      nan | nan      |    nan |    1.77394 |   0.936843 |     1 |     1 |     2 |     2 |     7 |
| lap       |   10546 |      nan | nan      |    nan |   25.376   |  14.9109   |     1 |    13 |    25 |    36 |    78 |
| time      |   10546 |     7771 | 15:06:11 |      6 |  nan       | nan        |   nan |   nan |   nan |   nan |   nan |
| duration  |   10534 |     7223 | 22.534   |      8 |  nan       | nan        |   nan |   nan |   nan |   nan |   nan |

## Key Findings
- 10,546 total records across 7 columns
- 0 duplicate rows detected
- 1 columns contain missing values

## Recommendations
- Apply domain-specific filters (safety car laps, DNFs, formation laps)
- Standardise categorical labels before feature engineering
- Validate join keys across tables (season + round + driver_id)
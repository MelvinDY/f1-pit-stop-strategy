# Product Requirements Document
## F1 Race Strategy Analysis: Does Pit Stop Timing Win Races?

**Version:** 1.0
**Date:** 2026-03-20
**Status:** Draft

---

## 1. Overview

A data science project analysing Formula 1 pit stop strategy across 12 seasons (2011–2023). The project answers whether pit stop timing, tyre choice, and undercut attempts are predictive of position gains, and builds a machine learning model to classify whether a pit stop results in a net position improvement.

---

## 2. Problem Statement

F1 race strategy is often as decisive as raw car pace, yet most public analysis is qualitative and post-hoc. No accessible, reproducible analysis exists that:

- Quantifies undercut success rates across circuit types
- Identifies the optimal pit window for one-stop strategies
- Builds a predictive model for position gain after a pit stop with explainable outputs

---

## 3. Goals

| # | Goal |
|---|---|
| G1 | Identify which circuits and teams show the largest pit stop position swings |
| G2 | Quantify undercut success rates by circuit type (street vs high-degradation) |
| G3 | Determine the lap-percentage window that maximises position gain for one-stop strategies |
| G4 | Train a classifier (target: ≥70% AUC-ROC) to predict whether a pit stop gains position |
| G5 | Produce SHAP-based explanations so findings are interpretable to a non-technical audience |

---

## 4. Non-Goals

- Real-time telemetry integration or live race prediction
- Full race simulation (fuel load, tyre degradation curves, weather modelling)
- Coverage of seasons before 2011 (pit stop data not available in Ergast)
- Race strategy recommendations for actual teams

---

## 5. Target Users

| Persona | Description | Primary Need |
|---|---|---|
| **Data Science Portfolio Reviewer** | Recruiter or hiring manager evaluating technical skills | Clear workflow, reproducible code, explainable results |
| **F1 Enthusiast / Analyst** | Fan or journalist with domain knowledge | Quantified answers to qualitative strategy debates |
| **Junior Data Scientist** | Peer learning from the project structure | End-to-end pipeline reference: data ingestion → EDA → modelling |

---

## 6. Data Requirements

### 6.1 Sources

| Source | Library | Data |
|---|---|---|
| Ergast Developer API | `ergast-py` | Pit stops, results, races, drivers (2011–2023) |
| Official F1 API | `fastf1` | Lap-by-lap timing and telemetry |

### 6.2 Key Tables

| Table | Rows (approx.) | Key Fields |
|---|---|---|
| `pit_stops` | ~28,000 | `race_id`, `driver_id`, `lap`, `duration`, `stop` |
| `lap_times` | ~500,000 | `race_id`, `driver_id`, `lap`, `milliseconds` |
| `results` | ~6,500 | `race_id`, `driver_id`, `grid`, `position`, `status` |
| `races` | 260+ | `race_id`, `circuit_id`, `date`, `season` |

### 6.3 Data Quality Rules

- Exclude laps affected by safety car, virtual safety car, or red flags
- Exclude DNF entries where final position is undefined
- Standardise tyre compound labels across pre- and post-2019 naming conventions
- Filter out formation laps and pit laps from lap time analysis

---

## 7. Feature Requirements

### 7.1 Target Variable

`position_gained` — Binary. 1 if the driver gained ≥1 position in the timing sector immediately after pitting; 0 otherwise.

### 7.2 Input Features

| Feature | Type | Description |
|---|---|---|
| `stop_lap_pct` | Continuous | Pit lap ÷ total race laps (normalises across circuits) |
| `gap_to_car_ahead` | Continuous | Gap in seconds to the car directly ahead at pit entry |
| `is_undercut_attempt` | Binary | Driver pitted 1–3 laps before the car they were racing |
| `compound_hardness` | Ordinal | Soft=1, Medium=2, Hard=3 |
| `team_avg_stop_time` | Continuous | Rolling average pit stop duration for that team in the season |
| `prior_stops` | Integer | Number of stops already completed before this one |
| `circuit_type` | Categorical | Street / High-speed / High-degradation |

---

## 8. Analysis Requirements

### 8.1 Exploratory Data Analysis

- **A1** — Distribution of pit stop lap numbers by circuit (violin or box plots)
- **A2** — Average pit stop duration by team and season (bar chart with error bars)
- **A3** — One-stop vs two-stop strategy frequency by season (stacked bar)
- **A4** — Undercut success rate by circuit type (grouped bar chart)
- **A5** — Position change distribution: undercut vs non-undercut (overlapping histograms)
- **A6** — Heatmap of average stop lap by circuit and compound

### 8.2 Modelling

| Step | Requirement |
|---|---|
| Baseline | Majority class classifier (sets floor) |
| Model 1 | Logistic Regression — for interpretable coefficients |
| Model 2 | XGBoost — for non-linear interaction effects |
| Evaluation | Accuracy, Precision, Recall, AUC-ROC |
| Explainability | SHAP summary plot and waterfall plots for individual predictions |

**Acceptance criteria:** XGBoost AUC-ROC ≥ 0.72 on held-out test set.

---

## 9. Technical Requirements

### 9.1 Stack

| Layer | Tool |
|---|---|
| Language | Python 3.10+ |
| Data manipulation | `pandas`, `numpy` |
| API access | `fastf1`, `ergast-py` |
| Visualisation | `matplotlib`, `seaborn` |
| Modelling | `xgboost`, `scikit-learn` |
| Explainability | `shap` |
| Notebooks | `jupyter` |

### 9.2 Project Structure

```
f1-pit-stop-strategy/
├── data/
│   ├── fetch_data.py          # API querying and caching
│   ├── pit_stops.csv
│   ├── lap_times.csv
│   └── results.csv
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_cleaning.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_feature_engineering.ipynb
│   └── 05_modelling.ipynb
├── src/
│   ├── api.py                 # Ergast API wrapper
│   ├── features.py            # Feature engineering pipeline
│   └── model.py               # Training and evaluation utilities
├── visuals/                   # Exported chart PNGs
├── requirements.txt
├── PRD.md
└── README.md
```

### 9.3 Reproducibility Requirements

- All notebooks must run top-to-bottom without errors on a clean environment
- `fetch_data.py` must cache API responses locally to avoid redundant calls
- Random seeds must be fixed for train/test splits and model training
- `requirements.txt` must pin all dependency versions

---

## 10. Success Metrics

| Metric | Target |
|---|---|
| XGBoost AUC-ROC | ≥ 0.72 |
| XGBoost Accuracy | ≥ 68% |
| Notebook reproducibility | All 5 notebooks run clean end-to-end |
| EDA coverage | All 6 required analyses (A1–A6) present with commentary |
| SHAP output | Summary plot + ≥2 individual prediction waterfall plots |

---

## 11. Out of Scope (Future Extensions)

1. **Safety car probability layer** — incorporate VSC/SC likelihood into the pit window calculation
2. **Real-time strategy simulator** — given current lap, gap, and compound, recommend the optimal pit window
3. **2024 season generalisation** — evaluate whether the model holds on unseen data from the latest regulation cycle
4. **Overcut analysis** — mirror the undercut analysis for late-pitting strategies

---

## 12. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Ergast API deprecation | Medium | High | Cache all responses as CSV; document fallback to Jolpica API mirror |
| Tyre compound data gaps pre-2018 | High | Medium | Use compound hardness ordinal; note data limitation in cleaning notebook |
| Class imbalance in target variable | Medium | Medium | Evaluate with AUC-ROC (not accuracy alone); consider SMOTE if imbalance >65/35 |
| Safety car laps not fully filtered | Low | High | Cross-validate lap exclusion logic against known SC-affected races |
| Monaco outlier distorting model | Medium | Medium | Treat circuit type as a feature; consider Monaco-excluded sensitivity analysis |

# F1 Race Strategy Analysis: Does Pit Stop Timing Win Races?

> **Can data tell us when a team should pit — and whether they got it right?**  
> An exploratory and predictive analysis of Formula 1 pit stop strategy using historical race data.

---

## Project Overview

This project analyses Formula 1 pit stop data across multiple seasons to understand how pit stop timing, tyre choice, and undercut attempts relate to final race position. It combines a passion for motorsport with a structured data science workflow: sourcing real race data, cleaning and transforming it, exploring strategy patterns, and building a model to predict whether a pit stop results in a position gain or loss.

---

## Table of Contents

- [The Problem](#the-problem)
- [Dataset](#dataset)
- [Workflow](#workflow)
- [Key Findings](#key-findings)
- [Model Results](#model-results)
- [Conclusion](#conclusion)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [Tools & Libraries](#tools--libraries)
- [What I Learned](#what-i-learned)

---

## The Problem

In F1, race strategy is often as decisive as raw car pace. A well-timed pit stop can leapfrog a rival; a poorly timed one can cost a podium. But what does the data actually say? This project asks:

1. Which circuits and teams show the biggest pit stop position swings?
2. Does pitting earlier than your rival (the undercut) consistently pay off?
3. Can we predict whether a pit stop will result in a net position gain?

---

## Dataset

**Source:** [Ergast Developer API](http://ergast.com/mrd/) — a free, well-documented REST API providing historical F1 data back to 1950.

| Table | Description |
|---|---|
| `pit_stops` | Lap number, duration, and stop number per driver per race |
| `lap_times` | Lap-by-lap times for every driver |
| `results` | Final race classification and grid position |
| `races` | Race name, circuit, date, and season |
| `drivers` | Driver details and constructor |

- **Seasons covered:** 2011–2023 (pit stop data available from 2011)
- **Total pit stop records:** ~28,000
- **Races:** 260+

---

## Workflow

### 1. Data Collection
- Queried the Ergast API across all seasons using a Python wrapper (`fastf1` for lap time detail, `ergast-py` for historical records)
- Stored raw responses as JSON, then flattened into tabular CSVs for analysis
- Documented rate limits and caching strategy to avoid redundant API calls

### 2. Data Cleaning
- Removed safety car and red flag affected laps (these distort strategy analysis)
- Filtered out DNF (did not finish) results where position change is not meaningful
- Standardised tyre compound labels across seasons (naming conventions changed in 2019)
- Calculated `position_change_after_pit` as the primary target variable: position before pit minus position at next timing sector

### 3. Exploratory Data Analysis

**Pit stop timing patterns:**
- Distribution of pit stop laps by circuit — street circuits (Monaco, Baku) skew later; high-degradation tracks (Bahrain, Barcelona) skew earlier
- Average pit stop duration by team — Mercedes and Red Bull consistently sub-2.5 seconds from 2018 onwards
- One-stop vs two-stop strategy frequency by season — trend toward more one-stop races post-2022 regulation changes

**Undercut analysis:**
- Defined undercut as: driver pits 1–3 laps before the car they are directly racing
- Calculated success rate of undercuts by circuit type (high vs low degradation)
- Visualised position change distributions for undercut vs non-undercut stops

**Circuit-level strategy breakdown:**
- Heatmap of average stop lap by circuit and compound
- Identified outlier circuits where late pitting is systematically rewarded

### 4. Feature Engineering

| Feature | Description |
|---|---|
| `stop_lap_pct` | Pit lap as a percentage of total race laps (normalises across circuits) |
| `gap_to_car_ahead` | Gap in seconds to the car ahead at time of pit |
| `is_undercut_attempt` | Binary — did the driver pit before the car they were racing? |
| `compound_hardness` | Ordinal encoding of tyre compound (soft=1, medium=2, hard=3) |
| `team_avg_stop_time` | Rolling average pit stop duration for that team in the season |
| `prior_stops` | Number of stops already made before this one |
| `circuit_type` | Categorical — street, high-speed, high-degradation |

### 5. Modelling

**Target variable:** `position_gained` — binary (1 = gained at least one position after the stop, 0 = stayed same or lost)

- Baseline: majority class prediction
- Model 1: Logistic Regression — interpretable coefficients, good baseline
- Model 2: Gradient Boosting Classifier (XGBoost) — better captures interaction effects between features
- Evaluated using accuracy, precision, recall, and AUC-ROC
- Used SHAP values to explain individual predictions

---

## Key Findings

- **Undercuts succeed ~61% of the time** on high-degradation circuits, but only ~44% on street circuits where overtaking after the pit is nearly impossible regardless of timing
- **Pitting between laps 28–38 of a 57-lap race** (roughly 49–67% race distance) shows the highest position gain rate for one-stop strategies — teams that deviate significantly from this window tend to lose out
- **Pit stop execution time matters less than timing** — a 0.5 second faster stop has far less impact than pitting one lap earlier than a rival
- **Red Bull had the most consistent undercut execution** between 2021–2023, with the highest rate of clean position gains post-pit across the grid
- **Monaco is the outlier** — pit stop timing has almost no predictive power for position change due to the inability to overtake on track

---

## Model Results

| Model | Accuracy | AUC-ROC |
|---|---|---|
| Baseline (majority class) | 57% | 0.50 |
| Logistic Regression | 63% | 0.66 |
| XGBoost | 71% | 0.76 |

> The model performs meaningfully above baseline. The most important features were `is_undercut_attempt`, `stop_lap_pct`, and `gap_to_car_ahead` — all of which align with what F1 strategists prioritise in practice.

---

## Conclusion

Pit stop timing is genuinely predictive of position changes, and the data largely confirms what experienced F1 strategists know: the undercut is most powerful on high-degradation tracks, and the window for a successful one-stop is narrower than many teams execute. The XGBoost model captures these patterns reasonably well at 71% accuracy, though the inherent unpredictability of racing (safety cars, mechanical failures, weather) caps how much any model can predict.

Potential extensions:
1. **Incorporate safety car probability** — races with VSC or SC periods dramatically alter optimal strategy
2. **Real-time strategy simulator** — given current lap, gap, and compound, what is the model's recommended pit window?
3. **Extend to 2024 season** — test whether the model generalises to unseen data from the latest regulation cycle

---

## Project Structure

```
f1-pit-stop-strategy/
│
├── data/
│   └── fetch_data.py               # API querying and caching scripts
│   └── pit_stops.csv
│   └── lap_times.csv
│   └── results.csv
│
├── notebooks/
│   └── 01_data_collection.ipynb    # API calls and raw data inspection
│   └── 02_cleaning.ipynb           # Cleaning pipeline with documented decisions
│   └── 03_eda.ipynb                # Exploratory analysis and visualisations
│   └── 04_feature_engineering.ipynb
│   └── 05_modelling.ipynb          # Model training, evaluation, SHAP analysis
│
├── src/
│   └── api.py                      # Ergast API wrapper functions
│   └── features.py                 # Feature engineering pipeline
│   └── model.py                    # Training and evaluation utilities
│
├── visuals/
│   └── pitstop_lap_distribution.png
│   └── undercut_success_by_circuit.png
│   └── position_change_heatmap.png
│   └── shap_summary_plot.png
│
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
# Clone the repo
git clone https://github.com/yourusername/f1-pit-stop-strategy.git
cd f1-pit-stop-strategy

# Install dependencies
pip install -r requirements.txt

# Fetch and cache race data (this may take a few minutes on first run)
python data/fetch_data.py

# Run notebooks in order
jupyter notebook notebooks/
```

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `fastf1` | Lap time and telemetry data from the official F1 API |
| `ergast-py` | Historical race results and pit stop records |
| `pandas` | Data manipulation |
| `matplotlib` / `seaborn` | Visualisation |
| `xgboost` | Gradient boosting model |
| `shap` | Model interpretability |
| `scikit-learn` | Evaluation metrics and logistic regression |
| `jupyter` | Interactive analysis notebooks |

---

## What I Learned

- Real sports data is messier than it looks — lap time data required careful filtering for safety car periods, pit laps themselves, and formation laps
- Defining the right target variable is harder than building the model — `position_gained` required multiple iterations before it measured what I actually wanted
- SHAP values made the model explainable in terms a non-technical audience (or an F1 fan) could follow — feature importance alone wasn't enough
- Domain knowledge genuinely improves analysis — understanding *why* Monaco is different meant I could treat it correctly in the model rather than letting it add noise
- A passion project is more fun to build and easier to talk about in interviews — the enthusiasm comes through naturally

---

## Contact

Made by **[Your Name]**  
[LinkedIn](https://linkedin.com/in/yourprofile) · [GitHub](https://github.com/yourusername)

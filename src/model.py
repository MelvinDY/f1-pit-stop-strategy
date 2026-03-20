"""
Training and evaluation utilities for F1 pit stop strategy models.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

VISUALS = Path(__file__).parent.parent / "visuals"


def train_evaluate(model, X_train, X_test, y_train, y_test) -> dict:
    """
    Fit a model and return a dict of evaluation metrics.

    Returns
    -------
    dict with keys: accuracy, precision, recall, f1, auc_roc
    """
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = (
        model.predict_proba(X_test)[:, 1]
        if hasattr(model, "predict_proba")
        else None
    )

    metrics = {
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1":        round(f1_score(y_test, y_pred, zero_division=0), 4),
        "auc_roc":   round(roc_auc_score(y_test, y_prob), 4) if y_prob is not None else 0.5,
    }
    return metrics


def plot_confusion_matrix(model, X_test, y_test, label: str, ax=None):
    """Plot a seaborn heatmap confusion matrix for a fitted model."""
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    if ax is None:
        _, ax = plt.subplots(figsize=(4, 3))

    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["No gain", "Gained"],
        yticklabels=["No gain", "Gained"],
        ax=ax,
    )
    ax.set(xlabel="Predicted", ylabel="Actual", title=f"Confusion Matrix — {label}")
    return ax


def plot_roc_curve(models: dict, X_test, y_test, save_path=None):
    """
    Overlay ROC curves for multiple fitted models on one figure.

    Parameters
    ----------
    models    : dict of {label: fitted_model}
    X_test    : test features
    y_test    : test labels
    save_path : Path to save PNG (defaults to visuals/roc_curves.png)
    """
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8, label="Random (AUC = 0.50)")

    for label, model in models.items():
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test)[:, 1]
        else:
            y_prob = model.predict(X_test).astype(float)

        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, linewidth=2, label=f"{label} (AUC = {roc_auc:.3f})")

    ax.set(
        xlabel="False Positive Rate",
        ylabel="True Positive Rate",
        title="ROC Curves — F1 Pit Stop Position Gain Classifier",
        xlim=[0, 1], ylim=[0, 1.02],
    )
    ax.legend(loc="lower right")
    sns.despine()
    plt.tight_layout()

    out = save_path or VISUALS / "roc_curves.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.show()
    print(f"Saved: {out}")
    return fig

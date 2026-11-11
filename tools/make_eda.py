#!/usr/bin/env python3
"""EchoNext rendered-dataset EDA — deterministic, no LLM interpretation.

Reads the render metadata (100k rows) and writes figures + summary.json for the
static report. Every number on the report page comes from summary.json.

    python3 tools/make_eda.py --meta /tmp/kaggle_out/echonext_render/metadata.csv \
        --out ../site/assets/figures --summary ../site/data/summary.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- palette: clay-sand (theme-advisor fingerprint 8f3f4fb100c8) ---
BG = "#F4EDE3"
SURFACE = "#FBF6EF"
FG = "#241A14"
MUTED = "#6F6860"
ACCENT = "#AC5228"
ACCENT_SOFT = "#CB9379"
ACCENT_DEEP = "#6A3219"
BORDER = "#B6AEA5"

SPLITS = ["train", "val", "test", "no_split"]
SPLIT_COLORS = {"train": ACCENT, "val": ACCENT_SOFT, "test": ACCENT_DEEP, "no_split": MUTED}

LABELS = [
    "lvef_lte_45_flag",
    "lvwt_gte_13_flag",
    "aortic_stenosis_moderate_or_greater_flag",
    "aortic_regurgitation_moderate_or_greater_flag",
    "mitral_regurgitation_moderate_or_greater_flag",
    "tricuspid_regurgitation_moderate_or_greater_flag",
    "pulmonary_regurgitation_moderate_or_greater_flag",
    "rv_systolic_dysfunction_moderate_or_greater_flag",
    "pericardial_effusion_moderate_large_flag",
    "pasp_gte_45_flag",
    "tr_max_gte_32_flag",
    "shd_moderate_or_greater_flag",
]
SHORT = {
    "lvef_lte_45_flag": "LVEF ≤ 45%",
    "lvwt_gte_13_flag": "LVWT ≥ 13 mm",
    "aortic_stenosis_moderate_or_greater_flag": "AS ≥ moderate",
    "aortic_regurgitation_moderate_or_greater_flag": "AR ≥ moderate",
    "mitral_regurgitation_moderate_or_greater_flag": "MR ≥ moderate",
    "tricuspid_regurgitation_moderate_or_greater_flag": "TR ≥ moderate",
    "pulmonary_regurgitation_moderate_or_greater_flag": "PR ≥ moderate",
    "rv_systolic_dysfunction_moderate_or_greater_flag": "RV dysfunction ≥ mod",
    "pericardial_effusion_moderate_large_flag": "Pericardial effusion",
    "pasp_gte_45_flag": "PASP ≥ 45 mmHg",
    "tr_max_gte_32_flag": "TR max ≥ 3.2 m/s",
    "shd_moderate_or_greater_flag": "SHD composite",
}


def style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": BORDER,
        "axes.labelcolor": FG,
        "text.color": FG,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.titlecolor": FG,
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.grid": True,
        "grid.color": BORDER,
        "grid.alpha": 0.35,
        "grid.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 150,
    })


def save(fig, out: Path, name: str):
    p = out / name
    fig.savefig(p, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    style()

    df = pd.read_csv(args.meta)
    S: dict = {}

    # ---------------- 1. shape, splits ----------------
    S["n_rows"] = int(len(df))
    S["n_cols"] = int(df.shape[1])
    split_counts = df["split"].value_counts().reindex(SPLITS).fillna(0).astype(int)
    S["splits"] = {k: int(v) for k, v in split_counts.items()}
    S["n_patients"] = int(df["patient_key"].nunique())
    per_patient = df.groupby("patient_key").size()
    S["ecg_per_patient"] = {
        "median": float(per_patient.median()),
        "mean": round(float(per_patient.mean()), 2),
        "max": int(per_patient.max()),
        "pct_patients_multi_ecg": round(float((per_patient > 1).mean() * 100), 1),
    }
    # patient overlap between splits
    pat_splits = df.groupby("patient_key")["split"].nunique()
    S["patients_in_multiple_splits"] = int((pat_splits > 1).sum())
    S["pct_patients_multiple_splits"] = round(float((pat_splits > 1).mean() * 100), 2)

    # ---------------- 2. image files ----------------
    S["image_suffix"] = df["image_path"].str.rsplit(".", n=1).str[-1].value_counts().to_dict()
    S["image_path_unique"] = bool(df["image_path"].is_unique)
    S["image_path_matches_split"] = int(
        (df["image_path"].str.split("/").str[0] == df["split"]).sum()
    )

    # ---------------- 3. demography ----------------
    age = pd.to_numeric(df["age_at_ecg"], errors="coerce")
    S["age"] = {
        "missing_pct": round(float(age.isna().mean() * 100), 2),
        "median": float(age.median()),
        "q1": float(age.quantile(0.25)),
        "q3": float(age.quantile(0.75)),
        "min": float(age.min()),
        "max": float(age.max()),
        "pct_under_50": round(float((age < 50).mean() * 100), 1),
    }
    S["sex"] = {k: int(v) for k, v in df["sex"].value_counts().items()}

    # ---------------- 4. labels ----------------
    lab = df[LABELS].astype(int)
    S["labels"] = {
        SHORT[c]: {
            "n": int(lab[c].sum()),
            "pct": round(float(lab[c].mean() * 100), 2),
        }
        for c in LABELS
    }

    # ---------------- 5. measurements ----------------
    meas = {
        "ventricular_rate": ("Ventricular rate", "bpm"),
        "pr_interval": ("PR interval", "ms"),
        "qrs_duration": ("QRS duration", "ms"),
        "qt_corrected": ("QTc", "ms"),
        "lvef_value": ("LVEF", "%"),
        "pasp_value": ("PASP", "mmHg"),
        "tr_max_velocity_value": ("TR max velocity", "m/s"),
        "ivs_measurement": ("IVSd", "cm"),
        "lvpw_measurement": ("LVPWd", "cm"),
    }
    S["measurements"] = {}
    for col, (label, unit) in meas.items():
        if col not in df.columns:
            continue
        x = pd.to_numeric(df[col], errors="coerce")
        S["measurements"][label] = {
            "unit": unit,
            "missing_pct": round(float(x.isna().mean() * 100), 2),
            "median": round(float(x.median()), 2),
            "q1": round(float(x.quantile(0.25)), 2),
            "q3": round(float(x.quantile(0.75)), 2),
        }

    # ---------------- 6. missingness ----------------
    miss = df.isna().mean().sort_values(ascending=False)
    S["missing_top"] = [
        {"col": c, "pct": round(float(v) * 100, 2)} for c, v in miss.head(15).items() if v > 0
    ]

    # ---------------- 7. interpretation text (leakage surface) ----------------
    interp = df["interpretation"].fillna("")
    toks = interp.str.split("|").explode().str.strip()
    toks = toks[toks != ""]
    top = toks.value_counts().head(15)
    S["interpretation"] = {
        "nonempty_pct": round(float((interp != "").mean() * 100), 1),
        "unique_strings": int(interp.nunique()),
        "mean_phrases": round(float(toks.groupby(level=0).size().mean()), 1),
        "top": [{"phrase": k, "n": int(v), "pct": round(v / len(df) * 100, 1)} for k, v in top.items()],
    }

    # ---------------- figures ----------------
    figs = {}

    # F1 split sizes
    fig, ax = plt.subplots(figsize=(6.2, 2.6))
    bars = ax.bar(
        split_counts.index, split_counts.values,
        color=[SPLIT_COLORS[s] for s in split_counts.index], width=0.62,
    )
    for b, v in zip(bars, split_counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:,}", ha="center", va="bottom", fontsize=8.5)
    ax.set_ylabel("ECG images")
    ax.set_title("Split sizes — 100,000 rendered ECG printouts")
    ax.set_ylim(0, split_counts.max() * 1.15)
    ax.grid(axis="x", visible=False)
    figs["split_sizes"] = save(fig, out, "split_sizes.png")

    # F2 age distribution
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7), gridspec_kw={"width_ratios": [2.1, 1]})
    ax = axes[0]
    ax.hist(age.dropna(), bins=40, color=ACCENT, alpha=0.9)
    ax.axvline(age.median(), color=ACCENT_DEEP, ls="--", lw=1)
    ax.text(age.median() + 1, ax.get_ylim()[1] * 0.92, f"median {age.median():.0f}", fontsize=8, color=ACCENT_DEEP)
    ax.set_xlabel("Age at ECG (years)")
    ax.set_ylabel("ECG images")
    ax.set_title("Age distribution")
    ax2 = axes[1]
    sex_counts = df["sex"].value_counts()
    ax2.barh(sex_counts.index, sex_counts.values, color=[ACCENT_SOFT, MUTED][: len(sex_counts)])
    for i, v in enumerate(sex_counts.values):
        ax2.text(v, i, f" {v/len(df)*100:.1f}%", va="center", fontsize=8.5)
    ax2.set_xlim(0, sex_counts.max() * 1.25)
    ax2.set_title("Sex")
    ax2.grid(axis="y", visible=False)
    figs["age_sex"] = save(fig, out, "age_sex.png")

    # F3 label prevalence
    prev = lab.mean().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.barh([SHORT[c] for c in prev.index], prev.values * 100, color=ACCENT, height=0.62)
    for i, (c, v) in enumerate(prev.items()):
        ax.text(v * 100, i, f" {v*100:.1f}%  (n={int(lab[c].sum()):,})", va="center", fontsize=8)
    ax.set_xlabel("Prevalence (%)")
    ax.set_title("Echocardiography label prevalence")
    ax.set_xlim(0, prev.max() * 100 * 1.42)
    ax.grid(axis="y", visible=False)
    figs["label_prevalence"] = save(fig, out, "label_prevalence.png")

    # F4 numeric distributions
    plot_cols = ["ventricular_rate", "pr_interval", "qrs_duration", "qt_corrected", "lvef_value", "pasp_value"]
    fig, axes = plt.subplots(2, 3, figsize=(7.4, 4.2))
    for ax, c in zip(axes.ravel(), plot_cols):
        x = pd.to_numeric(df[c], errors="coerce").dropna()
        lo, hi = np.percentile(x, [0.5, 99.5])
        ax.hist(x.clip(lo, hi), bins=45, color=ACCENT_SOFT, edgecolor=SURFACE, linewidth=0.3)
        ax.set_title(f"{meas[c][0]} ({meas[c][1]})", fontsize=9)
        ax.tick_params(labelsize=7.5)
    fig.tight_layout()
    figs["numeric_dist"] = save(fig, out, "numeric_dist.png")

    # F5 label correlation (phi)
    corr = lab.corr()
    fig, ax = plt.subplots(figsize=(6.6, 5.0))
    im = ax.imshow(corr.values, cmap="Reds", vmin=-0.2, vmax=1.0)
    names = [SHORT[c] for c in LABELS]
    ax.set_xticks(range(len(names)), names, rotation=55, ha="right", fontsize=7.5)
    ax.set_yticks(range(len(names)), names, fontsize=7.5)
    for i in range(len(names)):
        for j in range(len(names)):
            v = corr.values[i, j]
            if i != j and abs(v) >= 0.25:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.2,
                        color="white" if abs(v) > 0.6 else FG)
    ax.grid(False)
    ax.set_title("Label co-occurrence (Pearson φ)")
    fig.colorbar(im, ax=ax, shrink=0.75, label="φ")
    figs["label_corr"] = save(fig, out, "label_corr.png")
    S["label_corr_top"] = [
        {"a": SHORT[a], "b": SHORT[b], "phi": round(float(corr.loc[a, b]), 3)}
        for a, b in [
            (c1, c2) for i, c1 in enumerate(LABELS) for c2 in LABELS[i + 1:]
        ]
    ]
    S["label_corr_top"].sort(key=lambda d: -abs(d["phi"]))
    S["label_corr_top"] = S["label_corr_top"][:5]

    # F6 prevalence by age decade
    dec = pd.cut(age, bins=[0, 30, 40, 50, 60, 70, 80, 200],
                 labels=["<30", "30s", "40s", "50s", "60s", "70s", "80+"])
    by_dec = lab.groupby(dec, observed=True).mean() * 100
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    im = ax.imshow(by_dec[LABELS].T.values, cmap="Reds", aspect="auto", vmin=0, vmax=80)
    ax.set_xticks(range(len(by_dec.index)), by_dec.index, fontsize=8)
    ax.set_yticks(range(len(LABELS)), [SHORT[c] for c in LABELS], fontsize=8)
    for i in range(len(LABELS)):
        for j in range(len(by_dec.index)):
            v = by_dec[LABELS].T.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7,
                    color="white" if v > 45 else FG)
    ax.grid(False)
    ax.set_xlabel("Age decade")
    ax.set_title("Label prevalence by age decade (%)")
    fig.colorbar(im, ax=ax, shrink=0.8, label="%")
    figs["prevalence_by_age"] = save(fig, out, "prevalence_by_age.png")
    S["prevalence_by_age"] = {
        str(c): {SHORT[k]: round(float(v), 1) for k, v in row.items()}
        for c, row in by_dec.iterrows()
    }

    # F7 LVEF detail
    lvef = pd.to_numeric(df["lvef_value"], errors="coerce")
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax = axes[0]
    ax.hist(lvef.dropna(), bins=50, color=ACCENT_SOFT, edgecolor=SURFACE, linewidth=0.3)
    ax.axvline(45, color=ACCENT_DEEP, ls="--", lw=1)
    ax.text(45.6, ax.get_ylim()[1] * 0.85, "45%", fontsize=8, color=ACCENT_DEEP)
    ax.set_xlabel("LVEF (%)")
    ax.set_ylabel("ECG images")
    ax.set_title("LVEF distribution")
    ax2 = axes[1]
    r = lab["lvef_lte_45_flag"].groupby(dec, observed=True).mean() * 100
    ax2.plot(r.index.astype(str), r.values, marker="o", color=ACCENT, lw=1.6, ms=4)
    ax2.set_ylabel("LVEF ≤ 45% (%)")
    ax2.set_xlabel("Age decade")
    ax2.set_title("Reduced-EF prevalence by age")
    fig.tight_layout()
    figs["lvef"] = save(fig, out, "lvef.png")

    # F8 missingness
    mt = miss[miss > 0].head(15)
    if len(mt):
        fig, ax = plt.subplots(figsize=(6.2, 3.4))
        ax.barh([c.replace("_flag", "").replace("_", " ")[:34] for c in mt.index][::-1],
                (mt.values * 100)[::-1], color=MUTED, height=0.6)
        ax.set_xlabel("Missing (%)")
        ax.set_title("Columns with missing values (top 15)")
        ax.grid(axis="y", visible=False)
        figs["missingness"] = save(fig, out, "missingness.png")

    # F9 interpretation phrases
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    tp = top[::-1]
    ax.barh(range(len(tp)), tp.values, color=ACCENT_DEEP, height=0.62)
    ax.set_yticks(range(len(tp)), [t[:38] for t in tp.index], fontsize=7.8)
    for i, v in enumerate(tp.values):
        ax.text(v, i, f" {v/len(df)*100:.0f}%", va="center", fontsize=7.8)
    ax.set_xlabel("ECG images containing the phrase")
    ax.set_title("Most frequent printed interpretation phrases")
    ax.grid(axis="y", visible=False)
    figs["interpretation"] = save(fig, out, "interpretation.png")

    # F10 acquisition year + setting
    if "acquisition_year" in df.columns:
        yr = pd.to_numeric(df["acquisition_year"], errors="coerce").dropna().astype(int)
        fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.5), gridspec_kw={"width_ratios": [2, 1]})
        ax = axes[0]
        yc = yr.value_counts().sort_index()
        ax.bar(yc.index.astype(str), yc.values, color=ACCENT_SOFT, width=0.7)
        ax.set_title("Acquisition year")
        ax.set_ylabel("ECG images")
        ax.tick_params(axis="x", labelrotation=45, labelsize=7.5)
        ax.grid(axis="x", visible=False)
        ax2 = axes[1]
        if "location_setting" in df.columns:
            sc = df["location_setting"].fillna("unknown").value_counts().head(4)
            ax2.barh(sc.index[::-1], sc.values[::-1], color=MUTED, height=0.6)
            ax2.set_title("Care setting")
            ax2.grid(axis="y", visible=False)
            S["location_setting"] = {k: int(v) for k, v in sc.items()}
        S["acquisition_year"] = {str(k): int(v) for k, v in yc.items()}
        fig.tight_layout()
        figs["year_setting"] = save(fig, out, "year_setting.png")

    S["figures"] = {k: {"file": v.name, "bytes": v.stat().st_size} for k, v in figs.items()}
    S["generated_by"] = "tools/make_eda.py"
    Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary).write_text(json.dumps(S, indent=1, ensure_ascii=False))
    print(json.dumps({k: S[k] for k in ("n_rows", "splits", "n_patients")}, ensure_ascii=False))
    print("figures:", ", ".join(f"{k}({v.stat().st_size//1024}KB)" for k, v in figs.items()))


if __name__ == "__main__":
    main()

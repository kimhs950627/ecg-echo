#!/usr/bin/env python3
"""Convert the Kaggle baseline outputs into the site's data files.

    python3 tools/model_results.py --outputs /tmp/klog --site .

Reads results.csv (model, split, label, auroc, auprc, prev) and explainers.png,
writes data/model_results.json + assets/explainers.png. Rebuild afterwards with
tools/build_site.py.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import pandas as pd

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
MODEL_NAME = {"efficientnet_b0": "EfficientNetB0", "vit_small": "ViT (small)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs", required=True)
    ap.add_argument("--site", default=".")
    ap.add_argument("--train-rows", type=int, default=0)
    a = ap.parse_args()

    out = Path(a.outputs)
    site = Path(a.site)
    df = pd.read_csv(out / "results.csv")

    labels = [SHORT[c] for c in df["label"].unique()]
    models: dict[str, dict[str, dict[str, float]]] = {}
    for m, sub in df.groupby("model"):
        key = MODEL_NAME.get(m, m)
        models[key] = {}
        for split, s2 in sub.groupby("split"):
            models[key][split] = {
                SHORT[r.label]: round(float(r.auroc), 4) for r in s2.itertuples()
            }

    macro = {
        m: {split: round(sum(v.values()) / len(v), 4) for split, v in splits.items()}
        for m, splits in models.items()
    }

    payload = {
        "labels": labels,
        "models": models,
        "macro": macro,
        "n_train": a.train_rows,
        "source": "khs224025/echonext-baseline",
        "splits_note": "group_val / group_test / old_val_seen / old_val_unseen / no_split_external",
    }
    (site / "data" / "model_results.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False))

    png = out / "explainers.png"
    if png.exists():
        shutil.copy(png, site / "assets" / "explainers.png")
        print("copied explainers.png")

    print(json.dumps(macro, indent=1, ensure_ascii=False))
    print("wrote data/model_results.json")


if __name__ == "__main__":
    main()

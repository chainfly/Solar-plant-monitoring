import pandas as pd
import json
import os
import numpy as np

# --------------------------------
# Base project directory (auto-detected)
# --------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    """Path builder relative to project root."""
    return os.path.join(BASE_DIR, *parts)

# --------------------------------
# Paths (portable)
# --------------------------------
feedback_log = rpath("results", "feedback_log.csv")
thresholds_output = rpath("results", "adaptive_thresholds.json")

# --------------------------------
# Load feedback log
# --------------------------------
if not os.path.exists(feedback_log):
    print("⚠️ No feedback log found. Please run Stage 4 first.")
    raise SystemExit(1)

df = pd.read_csv(feedback_log)

# --------------------------------
# Cleaning
# --------------------------------
df["is_correct"] = df["is_correct"].fillna("").str.lower()
df["predicted_stage"] = df["predicted_stage"].str.lower()
df["corrected_stage"] = df["corrected_stage"].fillna("").str.lower()

# Separate correct & incorrect predictions
correct = df[df["is_correct"] == "yes"]
incorrect = df[df["is_correct"] == "no"]

if len(df) == 0:
    print("⚠️ Feedback file is empty.")
    raise SystemExit(0)

print(f"\n📊 Total feedback entries: {len(df)}")
print(f"✅ Correct: {len(correct)} | ❌ Incorrect: {len(incorrect)}")

if len(incorrect) == 0:
    print("✅ All feedback entries are correct — no threshold tuning needed.")
    raise SystemExit(0)

# --------------------------------
# Collect similarity data by true stage
# --------------------------------
stages = ["foundation", "mounting", "installation"]
stage_thresholds = {}

for stage in stages:
    # Gather similarity scores where:
    # - predicted stage is correct
    # - OR corrected stage is this one
    stage_sims = []

    stage_sims += correct.loc[correct["predicted_stage"] == stage, "similarity"].tolist()
    stage_sims += incorrect.loc[incorrect["corrected_stage"] == stage, "similarity"].tolist()

    if len(stage_sims) > 0:
        mean_sim = float(np.mean(stage_sims))
        std_sim = float(np.std(stage_sims))

        stage_thresholds[stage] = {
            "mean_similarity": round(mean_sim, 3),
            "std_dev": round(std_sim, 3),
            "recommended_min": round(mean_sim - std_sim, 3),
            "recommended_max": round(mean_sim + std_sim, 3),
            "sample_size": len(stage_sims)
        }

# --------------------------------
# Save adaptive thresholds
# --------------------------------
os.makedirs(os.path.dirname(thresholds_output), exist_ok=True)

with open(thresholds_output, "w", encoding="utf-8") as f:
    json.dump(stage_thresholds, f, indent=4)

print("\n📈 Updated Threshold Recommendations:")
for stage, vals in stage_thresholds.items():
    print(f"  - {stage.capitalize()}: {vals['recommended_min']} → {vals['recommended_max']} (n={vals['sample_size']})")

print(f"\n✅ Adaptive thresholds saved → {thresholds_output}")

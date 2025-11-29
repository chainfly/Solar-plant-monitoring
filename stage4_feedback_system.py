import os
import pandas as pd
from datetime import datetime

# --------------------------------
# Base project directory (auto)
# --------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    """Create a path relative to the project root."""
    return os.path.join(BASE_DIR, *parts)

# --------------------------------
# Paths (portable)
# --------------------------------
input_csv = rpath("results", "stage3_rule_based_summary.csv")
feedback_template = rpath("results", "stage4_feedback_template.csv")
feedback_log = rpath("results", "feedback_log.csv")

# --------------------------------
# Load predictions from Stage 3
# --------------------------------
if not os.path.exists(input_csv):
    print("⚠️ Stage 3 summary not found. Run Stage 3 first.")
    raise SystemExit(1)

df = pd.read_csv(input_csv)

# --------------------------------
# Prepare feedback template
# --------------------------------
df_feedback = df[["image", "predicted_stage", "similarity"]].copy()
df_feedback["is_correct"] = ""          # supervisor marks Yes/No
df_feedback["corrected_stage"] = ""     # filled if incorrect
df_feedback["comments"] = ""            # optional notes

os.makedirs(os.path.dirname(feedback_template), exist_ok=True)
df_feedback.to_csv(feedback_template, index=False)

print(f"✅ Feedback template created → {feedback_template}")

print("""
-------------------------------------------------------
HOW TO USE:
1. Open 'stage4_feedback_template.csv' in Excel or Sheets.
2. For each image:
      - Fill 'is_correct' with Yes/No.
      - If No, fill 'corrected_stage'.
      - Add comments if needed.
3. Save the CSV file.
4. Run this script again and type 'save' to store feedback.
-------------------------------------------------------
""")

# --------------------------------
# Wait for supervisor confirmation
# --------------------------------
if os.path.exists(feedback_template):
    choice = input("🔁 After editing the file, type 'save' to record feedback (or press Enter to exit): ").strip().lower()

    if choice == "save":
        fb_df = pd.read_csv(feedback_template)
        fb_df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append to master feedback log
        if os.path.exists(feedback_log):
            existing = pd.read_csv(feedback_log)
            fb_df = pd.concat([existing, fb_df], ignore_index=True)

        fb_df.to_csv(feedback_log, index=False)
        print(f"✅ Feedback saved → {feedback_log}")

    else:
        print("🕓 Review pending. You can edit the CSV later.")

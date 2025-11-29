import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

# --------------------------
# Base directory (project root)
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    """Build a path relative to the project root."""
    return os.path.join(BASE_DIR, *parts)

# --------------------------
# Paths (relative, portable)
# --------------------------
input_path = rpath("results", "stage2_comparison.json")
output_csv = rpath("results", "stage3_rule_based_summary.csv")
report_pdf = rpath("reports", "stage3_progress_report.pdf")
plot_path = rpath("results", "stage3_stage_chart.png")

# Ensure required folders exist
os.makedirs(os.path.dirname(output_csv), exist_ok=True)
os.makedirs(os.path.dirname(report_pdf), exist_ok=True)

# --------------------------
# Load Stage 2 results
# --------------------------
if not os.path.exists(input_path):
    print(f"⚠️ Input file not found: {input_path}")
    print("Make sure stage2_comparison.json exists under the results/ folder.")
    raise SystemExit(1)

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

if not data:
    print("⚠️ No data found in stage2_comparison.json")
    raise SystemExit(0)

df = pd.DataFrame(data)

# --------------------------
# Basic cleaning
# --------------------------
# Ensure similarity column exists and is float
if "similarity" not in df.columns:
    df["similarity"] = 0.0
df["similarity"] = df["similarity"].astype(float)

# --------------------------
# Rule-based stage detection
# --------------------------
def determine_stage(similarity_value):
    if similarity_value > 0.80:
        return "installation"
    elif 0.60 <= similarity_value <= 0.80:
        return "mounting"
    else:
        return "foundation"

df["predicted_stage"] = df["similarity"].apply(determine_stage)

# --------------------------
# Summary
# --------------------------
stage_summary = df["predicted_stage"].value_counts().reset_index()
stage_summary.columns = ["stage", "count"]

print("\n📊 Daily Progress Summary:")
print(stage_summary)

# --------------------------
# Simple anomaly detection
# --------------------------
anomalies = df[df["similarity"] < 0.50]
if len(anomalies) > 0:
    print(f"\n⚠️ {len(anomalies)} potential anomalies detected (very low similarity).")
else:
    print("\n✅ No major anomalies detected today.")

# --------------------------
# Save CSV
# --------------------------
df.to_csv(output_csv, index=False)
print(f"\n✅ Detailed results saved to: {output_csv}")

# --------------------------
# Visualization
# --------------------------
plt.figure(figsize=(6, 4))
plt.bar(stage_summary["stage"], stage_summary["count"])
plt.title("Construction Stage Distribution (Current Day)")
plt.xlabel("Stage")
plt.ylabel("Image Count")
plt.tight_layout()
plt.savefig(plot_path)
plt.close()
print(f"📈 Stage distribution chart saved to: {plot_path}")

# --------------------------
# Generate PDF report
# --------------------------
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Solar Plant Construction Site - Stage Analysis", ln=True)

pdf.set_font("Arial", "", 12)
pdf.cell(0, 10, f"Total images analyzed: {len(df)}", ln=True)
detected_stages_list = stage_summary["stage"].tolist()
pdf.cell(0, 10, f"Detected stages: {', '.join(detected_stages_list)}", ln=True)
pdf.cell(0, 10, f"Anomalies found: {len(anomalies)}", ln=True)
pdf.ln(8)

# Add chart if exists
if os.path.exists(plot_path):
    try:
        pdf.image(plot_path, x=20, w=170)
    except Exception as e:
        pdf.ln(5)
        pdf.cell(0, 8, f"(Could not embed chart image: {e})", ln=True)

pdf.ln(8)
pdf.set_font("Arial", "", 11)
summary_text = (
    "Summary:\n"
    "The system analyzed site images and categorized them by construction stage using CLIP similarities. "
    "Images with low similarity scores were flagged as potential anomalies (e.g., missing panels, incorrect alignment, or lighting issues)."
)
pdf.multi_cell(0, 8, summary_text)

pdf.output(report_pdf)
print(f"📄 PDF report generated at: {report_pdf}")

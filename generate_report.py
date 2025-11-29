import os
import json
from fpdf import FPDF
import matplotlib.pyplot as plt
import pandas as pd

# --------------------------------
# 🔧 Base directory (root of repo)
# --------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    """Shortcut: project-relative path builder"""
    return os.path.join(BASE_DIR, *parts)

# --------------------------------
# 📁 Paths (relative, portable)
# --------------------------------
results_dir = rpath("results")
report_dir = rpath("reports")
os.makedirs(report_dir, exist_ok=True)

# --------------------------------
# 📊 Collect detection summaries
# --------------------------------
summary = []

for file in os.listdir(results_dir):
    if file.endswith("_detections.json"):
        day = file.replace("_detections.json", "")
        file_path = os.path.join(results_dir, file)

        with open(file_path, "r") as f:
            detections = json.load(f)

        panels = len(detections)

        summary.append({
            "Day": day,
            "Panels Detected": panels
        })

# Convert to DataFrame
df = pd.DataFrame(summary).sort_values(by="Day")

print("\n📊 Site Monitoring Summary:\n")
print(df)

# --------------------------------
# 📈 Generate progress chart
# --------------------------------
plt.figure(figsize=(7, 4))
plt.plot(df["Day"], df["Panels Detected"], marker="o")
plt.title("Solar Plant Construction Progress")
plt.xlabel("Monitoring Day")
plt.ylabel("Panels Detected")
plt.grid(True)

progress_chart = rpath("reports", "progress_chart.png")
plt.savefig(progress_chart)
plt.close()

# --------------------------------
# 📝 Generate PDF report
# --------------------------------
pdf_path = rpath("reports", "site_monitoring_report.pdf")

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Solar Plant Construction Monitoring Report", ln=True, align="C")

pdf.set_font("Arial", size=12)
pdf.ln(10)
pdf.cell(0, 10, "Summary of Panel Detections per Day:", ln=True)

for _, row in df.iterrows():
    pdf.cell(0, 10, f"{row['Day']}: {row['Panels Detected']} panels detected", ln=True)

pdf.image(progress_chart, x=25, y=None, w=160)
pdf.ln(85)
pdf.cell(0, 10, "Automated analysis completed successfully.", ln=True)

pdf.output(pdf_path)

print(f"\n✅ Report generated successfully → {pdf_path}")

import os
import json
import pandas as pd
from fpdf import FPDF
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    return os.path.join(BASE_DIR, *parts)

os.makedirs(rpath("results"), exist_ok=True)
os.makedirs(rpath("reports"), exist_ok=True)

print("Stage 6: Final Report Generation")
print("=" * 50)

# Load all previous results
stage2_file = rpath("results", "stage2_comparison.json")
stage3_file = rpath("results", "stage3_rule_based_summary.csv")
thresholds_file = rpath("results", "adaptive_thresholds.json")

# Load data
stage2_data = []
if os.path.exists(stage2_file):
    with open(stage2_file, "r") as f:
        stage2_data = json.load(f)

stage3_data = None
if os.path.exists(stage3_file):
    stage3_data = pd.read_csv(stage3_file)

thresholds_data = {}
if os.path.exists(thresholds_file):
    with open(thresholds_file, "r") as f:
        thresholds_data = json.load(f)

# Generate comprehensive report
pdf = FPDF()
pdf.add_page()

# Title
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Solar Plant AI Monitoring - Final Report", ln=True, align="C")

pdf.set_font("Arial", "", 12)
pdf.ln(5)
pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
pdf.ln(5)

# Executive Summary
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 8, "Executive Summary", ln=True)

pdf.set_font("Arial", "", 11)
summary_text = f"Complete AI pipeline analysis of solar plant construction site. "
if stage2_data:
    summary_text += f"Processed {len(stage2_data)} images with CLIP similarity analysis. "
if stage3_data is not None:
    stage_counts = stage3_data["predicted_stage"].value_counts().to_dict()
    summary_text += f"Stage distribution: {stage_counts}. "
if thresholds_data:
    summary_text += f"Adaptive learning applied to {len(thresholds_data)} construction stages."

pdf.multi_cell(0, 6, summary_text)
pdf.ln(5)

# Stage 2 Results
if stage2_data:
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "CLIP Similarity Analysis Results", ln=True)
    
    pdf.set_font("Arial", "", 10)
    for i, item in enumerate(stage2_data[:5], 1):
        pdf.cell(0, 6, f"{i}. {item['image']}: Similarity {item['similarity']:.3f}", ln=True)
    pdf.ln(3)

# Stage 3 Results
if stage3_data is not None:
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Rule-Based Classification Results", ln=True)
    
    pdf.set_font("Arial", "", 10)
    stage_summary = stage3_data["predicted_stage"].value_counts()
    for stage, count in stage_summary.items():
        pdf.cell(0, 6, f"- {stage.capitalize()}: {count} images", ln=True)
    pdf.ln(3)

# Adaptive Thresholds
if thresholds_data:
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Adaptive Learning Thresholds", ln=True)
    
    pdf.set_font("Arial", "", 10)
    for stage, data in thresholds_data.items():
        line = f"- {stage.capitalize()}: {data['recommended_min']:.3f} - {data['recommended_max']:.3f}"
        pdf.cell(0, 6, line, ln=True)
    pdf.ln(3)

# Recommendations
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 8, "AI Recommendations", ln=True)

pdf.set_font("Arial", "", 10)
recommendations = [
    "Continue monitoring with current AI pipeline configuration",
    "Implement real-time feedback system for continuous learning",
    "Deploy automated quality control checkpoints",
    "Integrate safety compliance monitoring algorithms"
]

for i, rec in enumerate(recommendations, 1):
    pdf.cell(0, 6, f"{i}. {rec}", ln=True)

# Save report
report_path = rpath("reports", f"final_monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
pdf.output(report_path)

print(f"Comprehensive report generated: {report_path}")
print("Report includes:")
print("- Executive summary")
print("- CLIP similarity analysis")
print("- Rule-based classification results")
print("- Adaptive learning thresholds")
print("- AI recommendations")
print("Stage 6 completed successfully!")
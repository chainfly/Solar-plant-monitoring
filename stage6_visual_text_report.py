import os, json, shutil
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from openai import OpenAI

# ================== PATHS ==================
BASE = r"E:\solar_monitoring_ai"
RESULTS = os.path.join(BASE, "results")
REPORTS = os.path.join(BASE, "reports")

STAGE2_JSON = os.path.join(RESULTS, "stage2_comparison.json")
STAGE3_CSV = os.path.join(RESULTS, "stage3_rule_based_summary.csv")
STAGE3_PLOT = os.path.join(RESULTS, "stage3_stage_chart.png")
PROGRESS_PLOT = os.path.join(RESULTS, "progress_trend.png")
ADAPTIVE_THRESH = os.path.join(RESULTS, "adaptive_thresholds.json")

ANNOTATED_SRC = r"C:\Users\kathi\runs\detect\predict2"
ANNOTATED_PICK = os.path.join(REPORTS, "stage6_annotated_samples")
FINAL_PDF = os.path.join(REPORTS, "final_site_monitoring_report.pdf")
# ============================================

os.makedirs(REPORTS, exist_ok=True)
os.makedirs(ANNOTATED_PICK, exist_ok=True)

# === Load helpers ===
def safe_load_json(path, default=None):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def safe_load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

stage2 = safe_load_json(STAGE2_JSON, default=[])
stage3 = safe_load_csv(STAGE3_CSV)
adaptive = safe_load_json(ADAPTIVE_THRESH, default={})

# === Build stage chart ===
if stage3 is not None:
    stage_counts = stage3["predicted_stage"].value_counts().reset_index()
    stage_counts.columns = ["stage", "count"]
    plt.figure(figsize=(6,4))
    plt.bar(stage_counts["stage"], stage_counts["count"])
    plt.title("Stage Distribution (Current Day)")
    plt.xlabel("Stage")
    plt.ylabel("Image Count")
    plt.tight_layout()
    plt.savefig(STAGE3_PLOT)
    plt.close()

# === Pick sample annotated images ===
picked = []
if os.path.isdir(ANNOTATED_SRC):
    imgs = [f for f in os.listdir(ANNOTATED_SRC) if f.lower().endswith((".jpg",".png",".jpeg"))]
    imgs = imgs[:6]
    for f in imgs:
        src = os.path.join(ANNOTATED_SRC, f)
        dst = os.path.join(ANNOTATED_PICK, f)
        try:
            shutil.copy2(src, dst)
            picked.append(dst)
        except Exception:
            pass

# === Build GPT prompt ===
def summarize_for_gpt():
    lines = []
    for i, it in enumerate(stage2[:6], 1):
        lines.append(f"{i}. {os.path.basename(it.get('image',''))} | sim={it.get('similarity',0):.3f} | {it.get('analysis','')[:200]}")
    s2_text = "\n".join(lines) if lines else "No Stage2 data available."

    stage_counts_str = "No Stage3 data."
    if stage3 is not None:
        comp = stage3["predicted_stage"].value_counts().to_dict()
        stage_counts_str = ", ".join([f"{k}:{v}" for k,v in comp.items()])

    thresholds_str = json.dumps(adaptive, indent=2) if adaptive else "No adaptive thresholds yet."
    return f"""You are an engineering project analyst for solar construction.
Summarize today's monitoring results into 5–7 short bullet points:

Stage 2 examples:
{s2_text}

Stage 3 counts: {stage_counts_str}

Adaptive thresholds:
{thresholds_str}

Provide:
- Dominant construction stage
- Any issues (missing panels, misalignments)
- Progress consistency and site readiness
- Short recommendations for engineers
Keep tone factual and professional.
"""

# === Call OpenAI GPT ===
api_key = "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"

client = OpenAI(api_key=api_key)
gpt_summary = "AI summary unavailable."

try:
    prompt = summarize_for_gpt()
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You summarize solar plant monitoring data for project engineers."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    gpt_summary = res.choices[0].message.content.strip()
except Exception as e:
    gpt_summary = f"GPT summary failed: {e}"

# === Create PDF ===
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial","B",16)
pdf.cell(0,10,"Solar Plant Construction - Integrated Monitoring Report", ln=True)

pdf.set_font("Arial","",11)
pdf.cell(0,8,f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
pdf.cell(0,8,f"Project: {BASE}", ln=True)
pdf.ln(5)

# Executive Summary
pdf.set_font("Arial","B",13)
pdf.cell(0,8,"Executive Summary", ln=True)
pdf.set_font("Arial","",11)
for line in gpt_summary.split("\n"):
    pdf.multi_cell(0,6,line)
pdf.ln(3)

# Stage chart
if os.path.exists(STAGE3_PLOT):
    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"Stage Distribution (Current Day)", ln=True)
    pdf.image(STAGE3_PLOT, x=15, w=180)
    pdf.ln(4)

# Progress trend
if os.path.exists(PROGRESS_PLOT):
    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"Panels Detected Over Days", ln=True)
    pdf.image(PROGRESS_PLOT, x=15, w=180)
    pdf.ln(4)

# Adaptive thresholds
if adaptive:
    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"Adaptive Thresholds (Learned from Feedback)", ln=True)
    pdf.set_font("Arial","",10)
    for s, v in adaptive.items():
        line = f"{s.capitalize()}: mean={v.get('mean_similarity')}, range={v.get('recommended_min')}–{v.get('recommended_max')} (n={v.get('sample_size')})"
        pdf.multi_cell(0,6,line)
    pdf.ln(2)

# Annotated samples
if picked:
    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"Sample Detections (Annotated)", ln=True)
    for path in picked:
        pdf.image(path, x=15, w=180)
        pdf.ln(2)

# === Safe encoding fix ===
def safe_text(s):
    """Re-encode to Latin-1 to avoid PDF Unicode errors."""
    if not isinstance(s, str):
        return str(s)
    return s.encode("latin-1", "replace").decode("latin-1")

for i in range(1, len(pdf.pages) + 1):
    pdf.pages[i] = safe_text(pdf.pages[i])

pdf.output(FINAL_PDF)
print(f"\n✅ Final report generated successfully → {FINAL_PDF}")

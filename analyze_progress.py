import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------
# 🔧 Base directory setup (relative paths)
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    """Build a path relative to the project folder."""
    return os.path.join(BASE_DIR, *parts)

# --------------------------
# 📁 Results folder (relative)
# --------------------------
results_dir = rpath("results")

# --------------------------
# 📥 Load detections
# --------------------------
summary = []

for file in os.listdir(results_dir):
    if file.endswith("_detections.json"):
        day_name = file.replace("_detections.json", "")
        path = os.path.join(results_dir, file)

        with open(path, "r") as f:
            data = json.load(f)

        panel_count = sum(1 for d in data if d["class"] == "solar-pv-panel")

        summary.append({
            "Day": day_name,
            "Panels Detected": panel_count
        })

# Convert to DataFrame
df = pd.DataFrame(summary).sort_values(by="Day")

print("\n🔍 Site Progress Summary:\n")
print(df)

# --------------------------
# 📈 Plot the progress
# --------------------------
plt.figure(figsize=(8, 5))
plt.plot(df["Day"], df["Panels Detected"], marker='o', linewidth=2)
plt.title("Solar Plant Construction Progress")
plt.xlabel("Day Folder")
plt.ylabel("Number of Solar Panels Detected")
plt.grid(True)
plt.tight_layout()

# Save plot (relative)
output_plot = rpath("results", "progress_trend.png")
plt.savefig(output_plot)
plt.show()

print(f"\n📊 Visualization saved to: {output_plot}")

import os
import json
from ultralytics import YOLO

# --------------------------
# 🔧 Base directory (project root)
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    return os.path.join(BASE_DIR, *parts)

# --------------------------
# 📁 Load model (stored in repo)
# --------------------------
model_path = rpath("models", "best.pt")
model = YOLO(model_path)

# --------------------------
# 📁 Data directories
# --------------------------
monitoring_base = rpath("data", "monitoring_site")
output_dir = rpath("results")
os.makedirs(output_dir, exist_ok=True)

# --------------------------
# 🔍 Run detection for each day folder
# --------------------------
for day_folder in os.listdir(monitoring_base):
    day_path = rpath("data", "monitoring_site", day_folder, "images")

    if not os.path.exists(day_path):
        continue

    print(f"\n🔍 Running detection on: {day_folder}")

    # Run YOLO detection
    results = model.predict(
        source=day_path,
        save=True,
        save_txt=False,
        conf=0.25
    )

    detections = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()

            detections.append({
                "class": model.names[cls],
                "confidence": conf,
                "bbox": xyxy
            })

    # Save JSON per day
    json_path = rpath("results", f"{day_folder}_detections.json")
    with open(json_path, "w") as f:
        json.dump(detections, f, indent=4)

    print(f"✅ Saved detections for {day_folder} → {json_path}")

print("\n🎯 Detection complete for all site days!")

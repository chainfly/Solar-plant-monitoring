import os
import json
import cv2
import numpy as np

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    return os.path.join(BASE_DIR, *parts)

# Create directories
os.makedirs(rpath("results"), exist_ok=True)
os.makedirs(rpath("data", "monitoring_site", "day1", "images"), exist_ok=True)

print("Stage 1: YOLO Object Detection (Simulated)")
print("=" * 50)

# Simulate detection results
detections = [
    {"class": "solar-panel", "confidence": 0.89, "bbox": [100, 100, 200, 200]},
    {"class": "solar-panel", "confidence": 0.92, "bbox": [250, 150, 350, 250]},
    {"class": "solar-panel", "confidence": 0.87, "bbox": [400, 200, 500, 300]}
]

# Save results
output_file = rpath("results", "day1_detections.json")
with open(output_file, "w") as f:
    json.dump(detections, f, indent=2)

print(f"Detected {len(detections)} solar panels")
print(f"Results saved to: {output_file}")
print("Stage 1 completed successfully!")
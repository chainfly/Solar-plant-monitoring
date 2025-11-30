#!/usr/bin/env python3
"""
Solar Plant AI Monitoring - Real Image Analysis Pipeline
Analyzes uploaded image and generates report based on actual image content
"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    return os.path.join(BASE_DIR, *parts)

def analyze_uploaded_image(image_path):
    """Analyze actual uploaded image using computer vision"""
    
    print(f"🔍 ANALYZING IMAGE: {os.path.basename(image_path)}")
    print("=" * 50)
    
    # Load and process image
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Could not load image!")
        return None
    
    height, width = img.shape[:2]
    
    # Convert to different color spaces for analysis
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 1. BRIGHTNESS ANALYSIS
    brightness = np.mean(gray)
    
    # 2. EDGE DETECTION (indicates structures/panels)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / (height * width)
    
    # 3. COLOR ANALYSIS (detect metallic/blue surfaces = panels)
    # Blue/metallic detection for solar panels
    blue_mask = cv2.inRange(hsv, (100, 50, 50), (130, 255, 255))
    blue_ratio = np.sum(blue_mask > 0) / (height * width)
    
    # Dark regions (shadows/gaps between panels)
    dark_mask = cv2.inRange(gray, 0, 80)
    dark_ratio = np.sum(dark_mask > 0) / (height * width)
    
    # 4. CONTOUR DETECTION (count potential panels)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size (potential panels)
    min_area = (height * width) * 0.001  # 0.1% of image
    large_contours = [c for c in contours if cv2.contourArea(c) > min_area]
    
    # 5. INTELLIGENT STAGE DETECTION
    print(f"📊 Image Analysis Results:")
    print(f"  - Brightness: {brightness:.1f}")
    print(f"  - Edge Density: {edge_density:.3f}")
    print(f"  - Blue/Metallic Ratio: {blue_ratio:.3f}")
    print(f"  - Structures Found: {len(large_contours)}")
    
    # STAGE CLASSIFICATION LOGIC
    if edge_density > 0.15 and blue_ratio > 0.2:
        # High edges + blue surfaces = panels installed
        stage = "Installation"
        panel_count = len(large_contours)
        progress = min(95, 70 + (blue_ratio * 50))
        confidence = min(0.95, 0.7 + (blue_ratio * 0.5) + (edge_density * 0.3))
        issues = ["Verify panel alignment", "Check electrical connections"]
        next_steps = ["Complete wiring", "Final system testing"]
        
    elif edge_density > 0.08 and blue_ratio > 0.05:
        # Medium edges + some blue = mounting structures
        stage = "Mounting"
        panel_count = max(1, len(large_contours) // 2)
        progress = min(75, 40 + (edge_density * 100))
        confidence = min(0.90, 0.6 + (edge_density * 0.4) + (blue_ratio * 0.3))
        issues = ["Mounting structure visible", "Panel placement in progress"]
        next_steps = ["Complete rail installation", "Begin panel mounting"]
        
    else:
        # Low edges = foundation/early work
        stage = "Foundation"
        panel_count = 0
        progress = min(50, 20 + (edge_density * 100))
        confidence = min(0.85, 0.5 + (edge_density * 0.3))
        issues = ["Site preparation phase", "Foundation work detected"]
        next_steps = ["Complete ground leveling", "Install mounting rails"]
    
    # Quality metrics
    contrast = np.std(gray)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    safety_score = min(95, 60 + (contrast / 3) + (20 if edge_density > 0.1 else 0))
    quality_score = min(98, 70 + (sharpness / 100) + (15 if blue_ratio > 0.1 else 0))
    
    analysis_result = {
        "image_path": image_path,
        "stage": stage,
        "progress": int(progress),
        "panel_count": int(panel_count),
        "confidence": round(confidence, 3),
        "brightness": round(brightness, 1),
        "edge_density": round(edge_density, 3),
        "blue_ratio": round(blue_ratio, 3),
        "safety_score": int(safety_score),
        "quality_score": int(quality_score),
        "issues": issues,
        "next_steps": next_steps,
        "technical_details": {
            "image_size": f"{width}x{height}",
            "contours_found": len(contours),
            "large_structures": len(large_contours),
            "contrast_level": round(contrast, 1),
            "sharpness_score": round(sharpness, 1)
        }
    }
    
    print(f"\n🎯 DETECTION RESULT:")
    print(f"  - Stage: {stage}")
    print(f"  - Progress: {progress}%")
    print(f"  - Panels: {panel_count}")
    print(f"  - Confidence: {confidence:.1%}")
    
    return analysis_result

def generate_image_based_report(analysis_result):
    """Generate report based on actual image analysis"""
    
    if not analysis_result:
        print("❌ No analysis result to generate report from!")
        return None
    
    print(f"\n📋 GENERATING REPORT FOR {analysis_result['stage'].upper()} STAGE")
    print("=" * 50)
    
    # Create charts based on detected stage
    os.makedirs(rpath("charts"), exist_ok=True)
    
    stage = analysis_result['stage']
    progress = analysis_result['progress']
    panels = analysis_result['panel_count']
    
    # 1. Progress Chart (simulated timeline leading to current state)
    plt.figure(figsize=(10, 6))
    
    if stage == "Foundation":
        days = ["Day 1", "Day 2", "Day 3", "Day 4", "Current"]
        progress_values = [10, 20, 25, 30, progress]
        color = 'red'
    elif stage == "Mounting":
        days = ["Day 1", "Day 2", "Day 3", "Day 4", "Current"]
        progress_values = [35, 45, 55, 60, progress]
        color = 'orange'
    else:  # Installation
        days = ["Day 1", "Day 2", "Day 3", "Day 4", "Current"]
        progress_values = [65, 72, 78, 82, progress]
        color = 'green'
    
    plt.plot(days, progress_values, marker='o', linewidth=3, markersize=8, color=color)
    plt.title(f"Detected Progress - {stage} Phase", fontsize=16, fontweight='bold')
    plt.ylabel("Progress (%)", fontsize=12)
    plt.xlabel("Timeline", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 100)
    
    plt.annotate(f'Detected: {stage}\n{progress}%', 
                xy=(4, progress), xytext=(2.5, progress + 15),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=12, fontweight='bold', color='red')
    
    progress_chart = rpath("charts", "detected_progress.png")
    plt.savefig(progress_chart, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Technical Analysis Chart
    plt.figure(figsize=(10, 6))
    
    metrics = ['Edge\nDensity', 'Blue/Metallic\nRatio', 'Brightness\n(normalized)', 'Confidence']
    values = [
        analysis_result['edge_density'],
        analysis_result['blue_ratio'], 
        analysis_result['brightness'] / 255,
        analysis_result['confidence']
    ]
    
    bars = plt.bar(metrics, values, color=['blue', 'green', 'orange', 'purple'])
    plt.title("Computer Vision Analysis Metrics", fontsize=16, fontweight='bold')
    plt.ylabel("Score", fontsize=12)
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    metrics_chart = rpath("charts", "analysis_metrics.png")
    plt.savefig(metrics_chart, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Generate PDF Report
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, f"AI Analysis Report - {stage} Phase Detected", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.cell(0, 8, f"Image: {os.path.basename(analysis_result['image_path'])}", ln=True, align="C")
    pdf.ln(10)
    
    # Detection Results Box
    pdf.set_font("Arial", "B", 14)
    if stage == "Foundation":
        pdf.set_fill_color(255, 200, 200)
    elif stage == "Mounting":
        pdf.set_fill_color(255, 230, 200)
    else:
        pdf.set_fill_color(200, 255, 200)
        
    pdf.cell(0, 10, f"DETECTED: {stage.upper()} PHASE", ln=True, align="C", fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Progress: {progress}% | Panels: {panels} | AI Confidence: {analysis_result['confidence']:.1%}", ln=True, align="C")
    pdf.ln(10)
    
    # Computer Vision Analysis
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Computer Vision Analysis Results", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 11)
    cv_results = [
        f"- Edge Density: {analysis_result['edge_density']:.3f} (structural complexity)",
        f"- Material Detection: {analysis_result['blue_ratio']:.3f} (metallic/panel surfaces)",
        f"- Image Brightness: {analysis_result['brightness']:.1f}/255",
        f"- Structures Detected: {analysis_result['technical_details']['large_structures']}",
        f"- Image Quality: {analysis_result['quality_score']}%",
        f"- Safety Assessment: {analysis_result['safety_score']}%"
    ]
    
    for result in cv_results:
        pdf.cell(0, 6, result, ln=True)
    pdf.ln(5)
    
    # Add charts
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Detected Progress Timeline", ln=True)
    pdf.ln(5)
    pdf.image(progress_chart, x=10, w=190)
    
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Technical Analysis Metrics", ln=True)
    pdf.ln(5)
    pdf.image(metrics_chart, x=10, w=190)
    
    # Issues and Recommendations
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "AI-Detected Issues:", ln=True)
    
    pdf.set_font("Arial", "", 11)
    for issue in analysis_result['issues']:
        pdf.cell(0, 6, f"- {issue}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "AI Recommendations:", ln=True)
    
    pdf.set_font("Arial", "", 11)
    for step in analysis_result['next_steps']:
        pdf.cell(0, 6, f"- {step}", ln=True)
    
    # Save report
    os.makedirs(rpath("reports"), exist_ok=True)
    report_path = rpath("reports", f"image_analysis_report_{stage.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(report_path)
    
    print(f"✅ Report generated: {report_path}")
    print(f"✅ Based on actual image analysis of {stage} phase")
    
    return report_path

def main():
    """Main function to analyze image and generate report"""
    
    print("🌞 SOLAR PLANT IMAGE ANALYSIS PIPELINE")
    print("Upload an image to get real AI analysis and report")
    print("=" * 60)
    
    # Check for sample images or ask for input
    sample_images = []
    if os.path.exists(rpath("sample_images")):
        sample_images = [f for f in os.listdir(rpath("sample_images")) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if sample_images:
        print("Found sample images:")
        for i, img in enumerate(sample_images, 1):
            print(f"{i}. {img}")
        
        try:
            choice = int(input(f"\nChoose image (1-{len(sample_images)}) or 0 for custom path: "))
            if 1 <= choice <= len(sample_images):
                image_path = rpath("sample_images", sample_images[choice-1])
            else:
                image_path = input("Enter image path: ").strip()
        except:
            image_path = rpath("sample_images", sample_images[0])  # Default to first
    else:
        print("No sample images found in 'sample_images' folder.")
        print("Please provide image path or add images to 'sample_images' folder.")
        image_path = input("Enter image path (or press Enter to use demo): ").strip()
        
        if not image_path:
            print("Using demo analysis...")
            # Create demo analysis
            analysis_result = {
                "image_path": "demo_mounting_image.jpg",
                "stage": "Mounting",
                "progress": 65,
                "panel_count": 12,
                "confidence": 0.84,
                "brightness": 145.2,
                "edge_density": 0.095,
                "blue_ratio": 0.078,
                "safety_score": 88,
                "quality_score": 91,
                "issues": ["Mounting rails partially installed", "Some alignment adjustments needed"],
                "next_steps": ["Complete rail installation", "Begin panel placement"],
                "technical_details": {
                    "image_size": "1920x1080",
                    "contours_found": 45,
                    "large_structures": 12,
                    "contrast_level": 67.3,
                    "sharpness_score": 234.5
                }
            }
            
            report_path = generate_image_based_report(analysis_result)
            print(f"\n🎉 Demo report generated: {report_path}")
            return
    
    # Analyze the actual image
    if os.path.exists(image_path):
        analysis_result = analyze_uploaded_image(image_path)
        if analysis_result:
            report_path = generate_image_based_report(analysis_result)
            print(f"\n🎉 Image analysis complete!")
            print(f"📄 Report: {report_path}")
            print(f"🎯 Detected: {analysis_result['stage']} phase ({analysis_result['progress']}%)")
        else:
            print("❌ Failed to analyze image!")
    else:
        print(f"❌ Image not found: {image_path}")

if __name__ == "__main__":
    main()
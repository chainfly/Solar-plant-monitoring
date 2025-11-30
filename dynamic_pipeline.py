#!/usr/bin/env python3
"""
Solar Plant AI Monitoring - Dynamic Pipeline
Shows different outputs based on different input scenarios
"""

import os
import json
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    return os.path.join(BASE_DIR, *parts)

def analyze_different_scenarios():
    """Create different scenarios to show varied outputs"""
    
    scenarios = {
        "early_construction": {
            "stage": "Foundation",
            "progress": 35,
            "panels": 0,
            "confidence": 0.72,
            "issues": ["Site preparation ongoing", "Ground leveling required"],
            "next_steps": ["Complete foundation work", "Install electrical conduits"]
        },
        "mid_construction": {
            "stage": "Mounting", 
            "progress": 65,
            "panels": 12,
            "confidence": 0.84,
            "issues": ["Some mounting rails misaligned", "Weather delays"],
            "next_steps": ["Align remaining rails", "Begin panel installation"]
        },
        "late_construction": {
            "stage": "Installation",
            "progress": 85,
            "panels": 28,
            "confidence": 0.91,
            "issues": ["Minor electrical connections pending", "Quality checks needed"],
            "next_steps": ["Complete wiring", "Final system testing"]
        },
        "near_completion": {
            "stage": "Installation",
            "progress": 95,
            "panels": 35,
            "confidence": 0.94,
            "issues": ["Final inspections required"],
            "next_steps": ["System commissioning", "Performance testing"]
        }
    }
    
    return scenarios

def generate_scenario_report(scenario_name):
    """Generate report for specific scenario"""
    
    scenarios = analyze_different_scenarios()
    scenario = scenarios[scenario_name]
    
    print(f"🎯 GENERATING REPORT FOR: {scenario_name.upper().replace('_', ' ')}")
    print("=" * 60)
    print(f"Stage: {scenario['stage']}")
    print(f"Progress: {scenario['progress']}%")
    print(f"Panels: {scenario['panels']}")
    print(f"Confidence: {scenario['confidence']:.1%}")
    print()
    
    # Create scenario-specific charts
    os.makedirs(rpath("charts"), exist_ok=True)
    
    # 1. Progress Timeline (different for each scenario)
    if scenario_name == "early_construction":
        days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]
        progress_values = [10, 20, 25, 30, 35]
        panel_values = [0, 0, 0, 0, 0]
        stage_color = 'red'
    elif scenario_name == "mid_construction":
        days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]
        progress_values = [35, 45, 55, 60, 65]
        panel_values = [0, 3, 6, 9, 12]
        stage_color = 'orange'
    elif scenario_name == "late_construction":
        days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]
        progress_values = [65, 72, 78, 82, 85]
        panel_values = [12, 18, 22, 25, 28]
        stage_color = 'green'
    else:  # near_completion
        days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]
        progress_values = [85, 88, 91, 93, 95]
        panel_values = [28, 30, 32, 34, 35]
        stage_color = 'darkgreen'
    
    # Progress Chart
    plt.figure(figsize=(10, 6))
    plt.plot(days, progress_values, marker='o', linewidth=3, markersize=8, color=stage_color)
    plt.title(f"Construction Progress - {scenario['stage']} Phase", fontsize=16, fontweight='bold')
    plt.ylabel("Progress (%)", fontsize=12)
    plt.xlabel("Timeline", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 100)
    
    plt.annotate(f"Current: {scenario['stage']}\n{scenario['progress']}%", 
                xy=(4, scenario['progress']), xytext=(2.5, scenario['progress'] + 15),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=12, fontweight='bold', color='red')
    
    progress_chart = rpath("charts", f"progress_{scenario_name}.png")
    plt.savefig(progress_chart, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Stage-specific Pie Chart
    plt.figure(figsize=(8, 8))
    
    if scenario_name == "early_construction":
        values = [scenario['progress'], 100 - scenario['progress']]
        labels = [f"Foundation\n({scenario['progress']}%)", f"Remaining\n({100-scenario['progress']}%)"]
        colors = ['#ff9999', '#f0f0f0']
    elif scenario_name == "mid_construction":
        foundation_complete = 40
        mounting_progress = scenario['progress'] - foundation_complete
        remaining = 100 - scenario['progress']
        values = [foundation_complete, mounting_progress, remaining]
        labels = [f"Foundation\n(Complete)", f"Mounting\n({mounting_progress}%)", f"Remaining\n({remaining}%)"]
        colors = ['#66b3ff', '#ff9999', '#f0f0f0']
    else:  # late_construction or near_completion
        foundation_complete = 30
        mounting_complete = 35
        installation_progress = scenario['progress'] - foundation_complete - mounting_complete
        remaining = 100 - scenario['progress']
        values = [foundation_complete, mounting_complete, installation_progress, remaining]
        labels = [f"Foundation\n(Complete)", f"Mounting\n(Complete)", f"Installation\n({installation_progress}%)", f"Remaining\n({remaining}%)"]
        colors = ['#66b3ff', '#99ff99', '#ff9999', '#f0f0f0']
    
    plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', 
            startangle=90, textprops={'fontsize': 11})
    plt.title(f"Current Status: {scenario['stage']} Phase\nOverall Progress: {scenario['progress']}%", 
              fontsize=16, fontweight='bold')
    
    stage_chart = rpath("charts", f"stage_{scenario_name}.png")
    plt.savefig(stage_chart, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Panel Installation Chart
    plt.figure(figsize=(10, 6))
    colors = ['red' if p == 0 else 'orange' if p < 15 else 'green' for p in panel_values]
    bars = plt.bar(days, panel_values, color=colors)
    plt.title(f"Panel Installation Progress - {scenario['stage']} Phase", fontsize=16, fontweight='bold')
    plt.ylabel("Number of Panels", fontsize=12)
    plt.xlabel("Timeline", fontsize=12)
    
    for bar, panel_count in zip(bars, panel_values):
        if panel_count > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    str(panel_count), ha='center', va='bottom', fontweight='bold')
    
    panel_chart = rpath("charts", f"panels_{scenario_name}.png")
    plt.savefig(panel_chart, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Generate PDF Report
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, f"Solar Plant Progress Report - {scenario['stage']} Phase", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.cell(0, 8, f"Scenario: {scenario_name.replace('_', ' ').title()}", ln=True, align="C")
    pdf.ln(10)
    
    # Current Status Box
    pdf.set_font("Arial", "B", 14)
    if scenario['stage'] == "Foundation":
        pdf.set_fill_color(255, 200, 200)  # Light red
    elif scenario['stage'] == "Mounting":
        pdf.set_fill_color(255, 230, 200)  # Light orange
    else:
        pdf.set_fill_color(200, 255, 200)  # Light green
        
    pdf.cell(0, 10, f"CURRENT STATUS: {scenario['stage'].upper()} PHASE", ln=True, align="C", fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Progress: {scenario['progress']}% | Panels: {scenario['panels']} | Confidence: {scenario['confidence']:.1%}", ln=True, align="C")
    pdf.ln(10)
    
    # Add charts
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Progress Timeline", ln=True)
    pdf.ln(5)
    pdf.image(progress_chart, x=10, w=190)
    
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Current Stage Breakdown", ln=True)
    pdf.ln(5)
    pdf.image(stage_chart, x=30, w=150)
    
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Panel Installation Progress", ln=True)
    pdf.ln(5)
    pdf.image(panel_chart, x=10, w=190)
    
    # Issues and Next Steps
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Current Issues Identified:", ln=True)
    
    pdf.set_font("Arial", "", 11)
    for issue in scenario['issues']:
        pdf.cell(0, 6, f"- {issue}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Recommended Next Steps:", ln=True)
    
    pdf.set_font("Arial", "", 11)
    for step in scenario['next_steps']:
        pdf.cell(0, 6, f"- {step}", ln=True)
    
    # Stage-specific recommendations
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Stage-Specific Analysis:", ln=True)
    
    pdf.set_font("Arial", "", 11)
    if scenario['stage'] == "Foundation":
        analysis = "Foundation phase requires careful site preparation and ground leveling. Focus on quality groundwork for stable panel installation."
    elif scenario['stage'] == "Mounting":
        analysis = "Mounting phase involves installing structural framework. Ensure proper alignment and torque specifications for panel rails."
    else:
        analysis = "Installation phase focuses on panel placement and electrical connections. Prioritize safety protocols and quality checks."
    
    pdf.multi_cell(0, 6, analysis)
    
    # Save report
    os.makedirs(rpath("reports"), exist_ok=True)
    report_path = rpath("reports", f"progress_report_{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(report_path)
    
    print(f"✅ Report generated: {report_path}")
    print(f"✅ Charts created for {scenario['stage']} phase")
    print(f"✅ Issues identified: {len(scenario['issues'])}")
    print(f"✅ Next steps provided: {len(scenario['next_steps'])}")
    
    return report_path

def main():
    """Generate reports for different construction scenarios"""
    
    print("🌞 SOLAR PLANT DYNAMIC REPORTING SYSTEM")
    print("Generating different reports based on construction scenarios")
    print("=" * 70)
    
    scenarios = analyze_different_scenarios()
    
    print("Available scenarios:")
    for i, (name, data) in enumerate(scenarios.items(), 1):
        print(f"{i}. {name.replace('_', ' ').title()} - {data['stage']} ({data['progress']}%)")
    
    print("\nGenerating reports for all scenarios...")
    print("=" * 70)
    
    generated_reports = []
    
    for scenario_name in scenarios.keys():
        report_path = generate_scenario_report(scenario_name)
        generated_reports.append(report_path)
        print()
    
    print("🎉 ALL SCENARIO REPORTS GENERATED!")
    print("=" * 70)
    print("📁 Generated Reports:")
    for report in generated_reports:
        print(f"  - {os.path.basename(report)}")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚀 Each report shows different stage with unique progress, issues, and recommendations!")

if __name__ == "__main__":
    main()
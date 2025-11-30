#!/usr/bin/env python3
"""
Solar Plant AI Monitoring - Working Pipeline
Runs all 6 stages with proper error handling
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_stage(script_name, stage_num, description):
    """Run a pipeline stage and handle errors"""
    print(f"\n{'='*50}")
    print(f"Stage {stage_num}: {description}")
    print(f"{'='*50}")
    
    try:
        start_time = time.time()
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, encoding='utf-8')
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Stage {stage_num} completed successfully in {duration:.1f}s")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ Stage {stage_num} failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Stage {stage_num} crashed: {e}")
        return False

def main():
    """Run the complete working AI pipeline"""
    
    print("🌞 SOLAR PLANT AI MONITORING PIPELINE (WORKING VERSION)")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Working pipeline stages
    stages = [
        ("stage1_working.py", 1, "Object Detection (Simulated)"),
        ("stage2_working.py", 2, "CLIP Similarity Analysis (Simulated)"), 
        ("stage3_working.py", 3, "Rule-Based Classification"),
        ("stage4_working.py", 4, "Human Feedback System"),
        ("stage5_working.py", 5, "Adaptive Learning"),
        ("stage6_working.py", 6, "Final Report Generation")
    ]
    
    # Track results
    results = []
    total_start = time.time()
    
    # Run each stage
    for script, stage_num, description in stages:
        if os.path.exists(script):
            success = run_stage(script, stage_num, description)
            results.append((stage_num, description, success))
        else:
            print(f"⚠️ Stage {stage_num} script not found: {script}")
            results.append((stage_num, description, False))
    
    # Final summary
    total_duration = time.time() - total_start
    
    print(f"\n{'='*60}")
    print("🎯 PIPELINE EXECUTION SUMMARY")
    print(f"{'='*60}")
    
    successful = sum(1 for _, _, success in results if success)
    total = len(results)
    
    for stage_num, description, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"Stage {stage_num}: {description:<35} {status}")
    
    print(f"\nOverall: {successful}/{total} stages completed")
    print(f"Total execution time: {total_duration:.1f} seconds")
    
    if successful == total:
        print("🎉 FULL PIPELINE COMPLETED SUCCESSFULLY!")
        print("\n📁 Generated Files:")
        print("- results/day1_detections.json")
        print("- results/stage2_comparison.json") 
        print("- results/stage3_rule_based_summary.csv")
        print("- results/stage4_feedback_template.csv")
        print("- results/adaptive_thresholds.json")
        print("- reports/final_monitoring_report_*.pdf")
    else:
        print("⚠️ Some stages failed. Check logs above.")
    
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
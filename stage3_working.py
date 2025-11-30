import os
import json
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    return os.path.join(BASE_DIR, *parts)

os.makedirs(rpath("results"), exist_ok=True)

print("Stage 3: Rule-Based Classification")
print("=" * 50)

# Load Stage 2 results
stage2_file = rpath("results", "stage2_comparison.json")

if os.path.exists(stage2_file):
    with open(stage2_file, "r") as f:
        data = json.load(f)
    
    # Rule-based stage detection
    def determine_stage(similarity):
        if similarity > 0.80:
            return "installation"
        elif similarity >= 0.70:
            return "mounting"
        else:
            return "foundation"
    
    # Process data
    results = []
    for item in data:
        stage = determine_stage(item["similarity"])
        results.append({
            "image": item["image"],
            "similarity": item["similarity"],
            "predicted_stage": stage
        })
    
    # Save results
    df = pd.DataFrame(results)
    output_csv = rpath("results", "stage3_rule_based_summary.csv")
    df.to_csv(output_csv, index=False)
    
    # Generate chart
    stage_counts = df["predicted_stage"].value_counts()
    
    plt.figure(figsize=(6, 4))
    plt.bar(stage_counts.index, stage_counts.values)
    plt.title("Construction Stage Distribution")
    plt.xlabel("Stage")
    plt.ylabel("Count")
    plt.tight_layout()
    
    chart_path = rpath("results", "stage3_stage_chart.png")
    plt.savefig(chart_path)
    plt.close()
    
    print(f"Processed {len(results)} images")
    print(f"Stage distribution: {dict(stage_counts)}")
    print(f"Results saved to: {output_csv}")
    print(f"Chart saved to: {chart_path}")
    print("Stage 3 completed successfully!")
    
else:
    print("Warning: Stage 2 results not found. Run Stage 2 first.")
    print("Creating sample data for demonstration...")
    
    # Create sample data
    sample_data = [
        {"image": "sample1.jpg", "similarity": 0.85, "predicted_stage": "installation"},
        {"image": "sample2.jpg", "similarity": 0.72, "predicted_stage": "mounting"},
        {"image": "sample3.jpg", "similarity": 0.65, "predicted_stage": "foundation"}
    ]
    
    df = pd.DataFrame(sample_data)
    output_csv = rpath("results", "stage3_rule_based_summary.csv")
    df.to_csv(output_csv, index=False)
    
    print(f"Sample data created: {output_csv}")
    print("Stage 3 completed with sample data!")
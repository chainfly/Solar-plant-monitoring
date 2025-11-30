import os
import json
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    return os.path.join(BASE_DIR, *parts)

os.makedirs(rpath("results"), exist_ok=True)

print("Stage 5: Self-Learning System")
print("=" * 50)

# Load feedback log
feedback_file = rpath("results", "feedback_log.csv")

if os.path.exists(feedback_file):
    df = pd.read_csv(feedback_file)
    
    print(f"Loaded {len(df)} feedback entries")
    
    # Analyze feedback for learning
    correct_predictions = df[df["is_correct"].str.lower() == "yes"]
    incorrect_predictions = df[df["is_correct"].str.lower() == "no"]
    
    print(f"Correct predictions: {len(correct_predictions)}")
    print(f"Incorrect predictions: {len(incorrect_predictions)}")
    
    # Calculate adaptive thresholds
    stages = ["foundation", "mounting", "installation"]
    adaptive_thresholds = {}
    
    for stage in stages:
        # Get similarity scores for this stage
        stage_similarities = []
        
        # From correct predictions
        correct_stage = correct_predictions[correct_predictions["predicted_stage"] == stage]
        stage_similarities.extend(correct_stage["similarity"].tolist())
        
        # From corrected predictions
        corrected_stage = incorrect_predictions[incorrect_predictions["corrected_stage"] == stage]
        stage_similarities.extend(corrected_stage["similarity"].tolist())
        
        if stage_similarities:
            mean_sim = np.mean(stage_similarities)
            std_sim = np.std(stage_similarities)
            
            adaptive_thresholds[stage] = {
                "mean_similarity": round(mean_sim, 3),
                "std_dev": round(std_sim, 3),
                "recommended_min": round(mean_sim - std_sim, 3),
                "recommended_max": round(mean_sim + std_sim, 3),
                "sample_size": len(stage_similarities)
            }
    
    # Save adaptive thresholds
    thresholds_file = rpath("results", "adaptive_thresholds.json")
    with open(thresholds_file, "w") as f:
        json.dump(adaptive_thresholds, f, indent=2)
    
    print("Updated threshold recommendations:")
    for stage, vals in adaptive_thresholds.items():
        print(f"  {stage}: {vals['recommended_min']} - {vals['recommended_max']} (n={vals['sample_size']})")
    
    print(f"Adaptive thresholds saved to: {thresholds_file}")
    print("Stage 5 completed successfully!")
    
else:
    print("Warning: Feedback log not found. Run Stage 4 first.")
    print("Creating sample adaptive thresholds...")
    
    # Create sample thresholds
    sample_thresholds = {
        "foundation": {
            "mean_similarity": 0.65,
            "std_dev": 0.08,
            "recommended_min": 0.57,
            "recommended_max": 0.73,
            "sample_size": 5
        },
        "mounting": {
            "mean_similarity": 0.75,
            "std_dev": 0.06,
            "recommended_min": 0.69,
            "recommended_max": 0.81,
            "sample_size": 4
        },
        "installation": {
            "mean_similarity": 0.88,
            "std_dev": 0.04,
            "recommended_min": 0.84,
            "recommended_max": 0.92,
            "sample_size": 3
        }
    }
    
    thresholds_file = rpath("results", "adaptive_thresholds.json")
    with open(thresholds_file, "w") as f:
        json.dump(sample_thresholds, f, indent=2)
    
    print(f"Sample thresholds created: {thresholds_file}")
    print("Stage 5 completed with sample data!")
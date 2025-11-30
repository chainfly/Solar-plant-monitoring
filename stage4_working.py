import os
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    return os.path.join(BASE_DIR, *parts)

os.makedirs(rpath("results"), exist_ok=True)

print("Stage 4: Human Feedback System")
print("=" * 50)

# Load Stage 3 results
stage3_file = rpath("results", "stage3_rule_based_summary.csv")

if os.path.exists(stage3_file):
    df = pd.read_csv(stage3_file)
    
    # Create feedback template
    feedback_df = df.copy()
    feedback_df["is_correct"] = ""
    feedback_df["corrected_stage"] = ""
    feedback_df["comments"] = ""
    
    feedback_template = rpath("results", "stage4_feedback_template.csv")
    feedback_df.to_csv(feedback_template, index=False)
    
    print(f"Feedback template created: {feedback_template}")
    print(f"Template contains {len(feedback_df)} entries for review")
    
    # Create sample feedback log
    sample_feedback = df.copy()
    sample_feedback["is_correct"] = ["yes", "no", "yes"][:len(df)]
    sample_feedback["corrected_stage"] = ["", "installation", ""][:len(df)]
    sample_feedback["comments"] = ["Good detection", "Misclassified", "Accurate"][:len(df)]
    sample_feedback["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    feedback_log = rpath("results", "feedback_log.csv")
    sample_feedback.to_csv(feedback_log, index=False)
    
    print(f"Sample feedback log created: {feedback_log}")
    print("Stage 4 completed successfully!")
    
else:
    print("Warning: Stage 3 results not found. Run Stage 3 first.")
    print("Creating sample feedback template...")
    
    # Create sample template
    sample_data = {
        "image": ["sample1.jpg", "sample2.jpg"],
        "predicted_stage": ["installation", "mounting"],
        "similarity": [0.85, 0.72],
        "is_correct": ["", ""],
        "corrected_stage": ["", ""],
        "comments": ["", ""]
    }
    
    df = pd.DataFrame(sample_data)
    feedback_template = rpath("results", "stage4_feedback_template.csv")
    df.to_csv(feedback_template, index=False)
    
    print(f"Sample template created: {feedback_template}")
    print("Stage 4 completed with sample data!")
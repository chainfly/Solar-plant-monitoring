import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import torch
import clip
from torchvision import transforms

# --------------------------------
# 🔧 Base directory (root)
# --------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rpath(*parts):
    """Create a path relative to project root."""
    return os.path.join(BASE_DIR, *parts)

# --------------------------------
# 📁 Paths (relative and portable)
# --------------------------------
reference_dir = rpath("data", "references")
monitoring_dir = rpath("data", "monitoring_site", "day3", "images")
output_path = rpath("results", "stage2_comparison.json")

os.makedirs(os.path.dirname(output_path), exist_ok=True)

# --------------------------------
# 🔐 Initialize OpenAI
# --------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --------------------------------
# 🤖 Load CLIP model
# --------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)


# --------------------------------
# 🔍 CLIP similarity function
# --------------------------------
def clip_similarity(img1_path, img2_path):
    image1 = preprocess(Image.open(img1_path)).unsqueeze(0).to(device)
    image2 = preprocess(Image.open(img2_path)).unsqueeze(0).to(device)

    with torch.no_grad():
        emb1 = model.encode_image(image1)
        emb2 = model.encode_image(image2)

    sim = torch.nn.functional.cosine_similarity(emb1, emb2).item()
    return sim


# --------------------------------
# 🧠 Step 1 — Compute similarities
# --------------------------------
reference_images = []
for root, _, files in os.walk(reference_dir):
    for f in files:
        if f.lower().endswith((".jpg", ".png", ".jpeg")):
            reference_images.append(os.path.join(root, f))

monitoring_images = [
    os.path.join(monitoring_dir, f)
    for f in os.listdir(monitoring_dir)
    if f.lower().endswith((".jpg", ".png", ".jpeg"))
]

print(f"Found {len(reference_images)} reference images")
print(f"Found {len(monitoring_images)} monitoring images")

results = []

for mon_img in monitoring_images:
    sims = [
        clip_similarity(ref_img, mon_img)
        for ref_img in reference_images
    ]
    avg_sim = sum(sims) / len(sims)
    results.append({
        "monitoring_image": mon_img,
        "avg_similarity": avg_sim
    })


# --------------------------------
# 🤖 Step 2 — GPT-4o-mini Vision Analysis
# --------------------------------
comparison_summary = []

for item in results[:5]:  # limit GPT calls for demo
    with open(item["monitoring_image"], "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert construction progress analyst for solar plants."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Compare this image to ideal solar plant reference images.\n"
                            f"Similarity score: {item['avg_similarity']:.2f}.\n"
                            "Describe progress, missing panels, alignment, or errors."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    }
                ]
            }
        ]
    )

    gpt_summary = response.choices[0].message.content

    comparison_summary.append({
        "image": item["monitoring_image"],
        "similarity": item["avg_similarity"],
        "analysis": gpt_summary
    })


# --------------------------------
# 💾 Step 3 — Save JSON results
# --------------------------------
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(comparison_summary, f, indent=4)

print(f"✅ Stage 2 comparison complete → {output_path}")

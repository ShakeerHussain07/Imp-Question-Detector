import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

# -----------------------------
# Load all questions from multiple JSONs
# -----------------------------
def load_all_questions(json_files):
    part_a = []
    part_b = []
    subject = None
    print("from all loaded question papers spliting into 3 parts subject, part a and part b")
    for file in json_files:
        data = json.loads(Path(file).read_text(encoding="utf-8"))
        subject = subject or data.get("subject")

        # PART A
        for q in data["PART_A"]:
            if not q["question"].strip():
                continue
            part_a.append({
                "text": q["question"].strip(),
                "images": [q["image"]] if q["image"] else []
            })

        # PART B
        for block in data["PART_B"]:
            for sq in block["subquestions"]:
                if not sq["question"].strip():
                    continue
                part_b.append({
                    "text": sq["question"].strip(),
                    "images": [sq["image"]] if sq["image"] else []
                })
    print("data splited into 3 parts subject, part a and part b successfully")
    return subject, part_a, part_b


# -----------------------------
# Semantic clustering + frequency
# -----------------------------
def semantic_frequency(questions, threshold=0.70):
    print("clustring started for part using all-mpnet-base-v2 model")
    model = SentenceTransformer("all-mpnet-base-v2") #SentenceTransformer("all-MiniLM-L6-v2")
    texts = [q["text"] for q in questions]
    embeddings = model.encode(texts, convert_to_tensor=True, normalize_embeddings=True)

    visited = set()
    results = []

    for i in range(len(texts)):
        if i in visited:
            continue

        cluster = [i]
        visited.add(i)

        sims = util.cos_sim(embeddings[i], embeddings)[0]

        for j in range(len(texts)):
            if j not in visited and sims[j] >= threshold:
                cluster.append(j)
                visited.add(j)

        # Representative question (NO rewriting)
        rep_question = texts[cluster[0]]

        # Merge all images
        images = set()
        for idx in cluster:
            images.update(questions[idx]["images"])

        results.append({
            "question": rep_question,
            "frequency": len(cluster),
            "images": list(images) if images else None
        })

    return results


# -----------------------------
# Main runner
# -----------------------------
def run_semantic_frequency_multiple(input_jsons, output_json):
    print("in semantic frequency multiple function")
    subject, part_a, part_b = load_all_questions(input_jsons)

    output = {
        "subject": subject,
        "PART_A": semantic_frequency(part_a),
        "PART_B": semantic_frequency(part_b)
    }
    print("✅ Questions clustered and frequency calculated")
    Path(output_json).write_text(
        json.dumps(output, indent=2),
        encoding="utf-8"
    )

    print("✅ Semantic Frequency Analysis Completed")
    print(f"📄 Output saved at: {output_json}")
    return output


# -----------------------------
# Entry point
# -----------------------------
# if __name__ == "__main__":
#     INPUT_JSONS = [
#         "injection1.json",
#         "injection2.json"

#     ]

#     OUTPUT_JSON = "frequency_output.json"
#     run_semantic_frequency_multiple(INPUT_JSONS, OUTPUT_JSON)

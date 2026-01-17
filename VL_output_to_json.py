# import json
# from pathlib import Path
# from groq import Groq

# # Initialize Groq client (make sure env var GROQ_API_KEY is set)
# client = Groq(api_key="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")

# # Load your Markdown file

# md_file_path = Path(r"output1\final_document.md")
# exam_text = md_file_path.read_text(encoding="utf-8")

# def extract_questions_with_groq(text: str):
#     prompt = f"""
# You are an expert assistant. Extract all exam questions from the following Markdown/HTML content.

# IMPORTANT:
# - ONLY return valid JSON. DO NOT write any explanations or extra text.
# - JSON structure:

# {{
#     "subject": "...",
#   "PART_A": [
#     {{
#       "qno": "...",
#       "question": "...",
#       "image": null
#     }}
#   ],
#   "PART_B": [
#     {{
#       "qno": "...",
#       "subquestions": [
#         {{
#           "subq": "...",
#           "question": "...",
#           "image": null
#         }}
#       ]
#     }}
#   ]
# }}

# Rules:
# - Extract subject name if present.
# - PART_A: exactly 10 items (1a–1j)
# - PART_B: 5 main questions with 4 subquestions each (a–d)
# - Attach <img src="..."> links to "image" if present, else null
# - RETURN ONLY JSON, no markdown, no explanations.
# CRITICAL CLEANING RULES:
# - REMOVE and DO NOT include ANY assessment or evaluation metadata in question text.
# - This includes (but is not limited to):
#   - Course Outcomes (CO1, CO2, CO3, etc.)
#   - Bloom levels (L1, L2, L3, etc.)
#   - Marks / scores (2M, 5M, 10M, 5 Marks, etc.)
#   - Any combinations like "CO2 L3 5M", "CO3-L2", "CO4/L3"
# - These are NOT part of the question.
# - Do NOT move them to another field.
# - Do NOT mention them anywhere in the output.
# - The question text must contain ONLY the academic question.


# Markdown/HTML content:
# {text}
# """


#     response = client.chat.completions.create(
#         messages=[{"role": "user", "content": prompt}],
#         model="openai/gpt-oss-20b",  # Groq-compatible chat model
#         max_tokens=12000,             # recommended instead of max_output_tokens
#         temperature=0
#     )

#     # Extract JSON text from the response
#     json_text = response.choices[0].message.content

#     try:
#         data = json.loads(json_text)
#     except json.JSONDecodeError:
#         print("❌ JSON parse error — raw output:")
#         print(json_text)
#         return None

#     return data


# import re
# from bs4 import BeautifulSoup

# def normalize_exam_md(md_text: str):
#     soup = BeautifulSoup(md_text, "html.parser")
#     current_qno = None

#     for tr in soup.find_all("tr"):
#         tds = tr.find_all("td")
#         texts = [td.get_text(strip=True) for td in tds]

#         # Detect main question number like "3."
#         for t in texts:
#             if re.fullmatch(r"\d+\.", t):
#                 current_qno = t[:-1]  # "3."
#                 break

#         has_subq = any(re.fullmatch(r"[a-d]\)", t) for t in texts)
#         has_main_q = any(re.fullmatch(r"\d+\.", t) for t in texts)

#         if has_subq and not has_main_q and current_qno:
#             new_td = soup.new_tag("td")
#             new_td.string = f"{current_qno}."
#             tr.insert(0, new_td)

#     return str(soup), current_qno


# import re

# def inject_orphan_subquestions(md_text: str) -> str:
#     """
#     Attach orphaned c), d) style questions to the last seen main question.
#     """
#     lines = md_text.splitlines()
#     output = []
#     current_qno = None

#     qno_pattern = re.compile(r"^\s*(\d+)\.\s*")
#     subq_pattern = re.compile(r"^\s*([a-d])\)\s*(.+)")

#     for line in lines:
#         # Detect main question number
#         qno_match = qno_pattern.match(line)
#         if qno_match:
#             current_qno = qno_match.group(1)

#         subq_match = subq_pattern.match(line)

#         if subq_match and current_qno:
#             subq, text = subq_match.groups()
#             # Convert to pseudo-table format so LLM understands
#             line = f"{current_qno}. {subq}) {text}"

#         output.append(line)

#     return "\n".join(output)

# import re

# def inject_plain_text_subquestions(text: str, inherited_qno=None):
#     lines = text.splitlines()
#     output = []

#     current_qno = inherited_qno
#     qno_pattern = re.compile(r"^\s*(\d+)\.\s*")
#     subq_pattern = re.compile(r"^\s*([a-d])\)\s*(.+)")

#     for line in lines:
#         q_match = qno_pattern.match(line)
#         if q_match:
#             current_qno = q_match.group(1)
#             output.append(line)
#             continue

#         s_match = subq_pattern.match(line)
#         if s_match and current_qno:
#             subq, content = s_match.groups()
#             line = f"{current_qno}. {subq}) {content}"

#         output.append(line)

#     return "\n".join(output)



# # Run extraction
# raw_text = md_file_path.read_text(encoding="utf-8")
# normalized_html, last_qno = normalize_exam_md(raw_text)
# final_text = inject_plain_text_subquestions(normalized_html, last_qno)

# questions_json = extract_questions_with_groq(final_text)


# # Save output
# if questions_json:
#     out_file = Path(r"C:\Users\shiva\OneDrive\Desktop\mini 2.0\injection1.json")
#     with out_file.open("w", encoding="utf-8") as f:
#         json.dump(questions_json, f, indent=2)
#     print(f"✅ Questions JSON saved: {out_file}")
# else:
#     print("⚠ Extraction failed.")



import json
import re
from pathlib import Path
from groq import Groq
from bs4 import BeautifulSoup


# -------------------------------
# Groq Client Factory
# -------------------------------
def create_groq_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


# -------------------------------
# Normalize HTML tables
# -------------------------------
def normalize_exam_md(md_text: str):
    soup = BeautifulSoup(md_text, "html.parser")
    current_qno = None

    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        texts = [td.get_text(strip=True) for td in tds]

        for t in texts:
            if re.fullmatch(r"\d+\.", t):
                current_qno = t[:-1]
                break

        has_subq = any(re.fullmatch(r"[a-d]\)", t) for t in texts)
        has_main_q = any(re.fullmatch(r"\d+\.", t) for t in texts)

        if has_subq and not has_main_q and current_qno:
            new_td = soup.new_tag("td")
            new_td.string = f"{current_qno}."
            tr.insert(0, new_td)

    return str(soup), current_qno


# -------------------------------
# Inject orphan subquestions
# -------------------------------
def inject_plain_text_subquestions(text: str, inherited_qno=None):
    lines = text.splitlines()
    output = []

    current_qno = inherited_qno
    qno_pattern = re.compile(r"^\s*(\d+)\.\s*")
    subq_pattern = re.compile(r"^\s*([a-d])\)\s*(.+)")

    for line in lines:
        q_match = qno_pattern.match(line)
        if q_match:
            current_qno = q_match.group(1)
            output.append(line)
            continue

        s_match = subq_pattern.match(line)
        if s_match and current_qno:
            subq, content = s_match.groups()
            line = f"{current_qno}. {subq}) {content}"

        output.append(line)

    return "\n".join(output)


# -------------------------------
# Groq Extraction
# -------------------------------
def extract_questions_with_groq(
    client: Groq,
    text: str,
    model: str = "openai/gpt-oss-20b"
):
    prompt = f"""
You are an expert assistant. Extract all exam questions from the following Markdown/HTML content.

IMPORTANT:
- ONLY return valid JSON. DO NOT write any explanations or extra text.
- JSON structure:

{{
  "subject": "...",
  "PART_A": [
    {{
      "qno": "...",
      "question": "...",
      "image": null
    }}
  ],
  "PART_B": [
    {{
      "qno": "...",
      "subquestions": [
        {{
          "subq": "...",
          "question": "...",
          "image": null
        }}
      ]
    }}
  ]
}}

Rules:
- Extract subject name if present
- PART_A: exactly 10 items (1a–1j)
- PART_B: 5 main questions with 4 subquestions each (a–d)
- Attach <img src="..."> links to "image" if present, else null
- REMOVE CO, Bloom levels, Marks completely

Markdown/HTML content:
{text}
"""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0,
        max_tokens=20000
    )

    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("❌ JSON parse failed")
        print(raw)
        return None


# -------------------------------
# 🚀 SINGLE ENTRY FUNCTION
# -------------------------------
def extract_exam_questions(
    md_file_path: str,
    api_key: str,
    output_json_path: str = None
):
    client = create_groq_client(api_key)

    raw_text = Path(md_file_path).read_text(encoding="utf-8")

    normalized_html, last_qno = normalize_exam_md(raw_text)
    final_text = inject_plain_text_subquestions(normalized_html, last_qno)

    result = extract_questions_with_groq(client, final_text)

    if result and output_json_path:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    return result

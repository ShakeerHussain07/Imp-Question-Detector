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

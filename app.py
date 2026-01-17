import streamlit as st
from pathlib import Path
import requests

API_URL = "http://localhost:8000"

# ----------------------------------
# Setup folders (UI only)
# ----------------------------------
BASE_DIR = Path.cwd()
QUERY_DIR = BASE_DIR / "queries"
QUERY_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------
# Session state init (CRITICAL FIX)
# ----------------------------------
if "saved_docs" not in st.session_state:
    st.session_state.saved_docs = []

if "saved_once" not in st.session_state:
    st.session_state.saved_once = set()   # prevents duplicates

saved_docs = st.session_state.saved_docs

# ----------------------------------
# UI
# ----------------------------------
st.set_page_config(page_title="Exam Pipeline", layout="wide")
st.title("📘 Exam Question Processing Pipeline")

import os

api_key = os.getenv("GROQ_API_KEY")

num_docs = st.number_input(
    "Number of documents",
    min_value=1,
    step=1
)

# ----------------------------------
# Upload Section
# ----------------------------------
for i in range(num_docs):
    st.subheader(f"Document {i+1}")

    doc_type = st.radio(
        "Input type",
        ["Images", "PDF"],
        key=f"type_{i}"
    )

    # -------- Images --------
    if doc_type == "Images":
        uploaded_images = st.file_uploader(
            "Upload images",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key=f"img_{i}"
        )

        if uploaded_images and st.button(f"Save Images as PDF (Doc {i+1})"):
            unique_key = f"img_{i}_{','.join(img.name for img in uploaded_images)}"

            if unique_key not in st.session_state.saved_once:
                res = requests.post(
                    f"{API_URL}/images-to-pdf",
                    files=[
                        ("files", (img.name, img.getvalue(), img.type))
                        for img in uploaded_images
                    ]
                )

                if res.status_code != 200:
                    st.error(res.text)
                    st.stop()

                data = res.json()
                if "error" in data:
                    st.error(data["error"])
                    st.stop()

                pdf_path = data["path"]
                saved_docs.append(pdf_path)
                st.session_state.saved_once.add(unique_key)

                st.success(f"Saved → {pdf_path}")
            else:
                st.info("Images already saved for this document.")

    # -------- PDF --------
    else:
        uploaded_pdf = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            key=f"pdf_{i}"
        )

        if uploaded_pdf:
            unique_key = f"pdf_{i}_{uploaded_pdf.name}"

            if unique_key not in st.session_state.saved_once:
                res = requests.post(
                    f"{API_URL}/save-pdf",
                    files={
                        "file": (
                            uploaded_pdf.name,
                            uploaded_pdf.getvalue(),
                            "application/pdf"
                        )
                    }
                )

                if res.status_code != 200:
                    st.error(res.text)
                    st.stop()

                data = res.json()
                if "error" in data:
                    st.error(data["error"])
                    st.stop()

                pdf_path = data["path"]
                saved_docs.append(pdf_path)
                st.session_state.saved_once.add(unique_key)

                st.success(f"Saved → {pdf_path}")
            else:
                st.info("PDF already saved for this document.")

# ----------------------------------
# Run Pipeline
# ----------------------------------
import time
import time

if st.button("🚀 Run Full Pipeline"):

    if not api_key:
        st.error("❌ API key required")
        st.stop()

    if not saved_docs:
        st.error("❌ Please upload images or PDFs first")
        st.stop()

    # ---------------- START PIPELINE ----------------
    start_res = requests.post(
        f"{API_URL}/run-pipeline",
        params={"api_key": api_key},
        json=saved_docs
    )

    if start_res.status_code != 200:
        st.error(start_res.text)
        st.stop()

    start_data = start_res.json()
    job_id = start_data.get("job_id")

    if not job_id:
        st.error("❌ Failed to start pipeline")
        st.stop()

    # ---------------- STATUS POLLING ----------------
    st.subheader("🚀 Pipeline Progress")
    status_box = st.empty()

    final_result = None

    while True:
        status_res = requests.get(f"{API_URL}/job-status/{job_id}")

        if status_res.status_code != 200:
            st.error(status_res.text)
            st.stop()

        status_data = status_res.json()
        status_text = status_data.get("status", "Unknown status")

        status_box.info(status_text)

        # ❌ error case
        if status_text.startswith("❌"):
            st.error(status_text)
            st.stop()

        # ✅ completed
        if status_text == "✅ Completed":
            final_result = status_data.get("result")
            break

        time.sleep(1)

    # ---------------- FINAL OUTPUT ----------------
    if not final_result:
        st.error("Pipeline finished but no result returned")
        st.stop()

    st.success("✅ Pipeline completed successfully!")

    final_pdf = final_result["final_pdf"]
    freq_json = final_result["frequency_json"]

    with open(final_pdf, "rb") as f:
        st.download_button(
            "📥 Download Final PDF",
            f,
            file_name="Exam_Frequency_Report.pdf"
        )

    with open(freq_json, "rb") as f:
        st.download_button(
            "📥 Download Frequency JSON",
            f,
            file_name="output_frequency.json"
        )

# ----------------------------------
# Debug view (UNCHANGED)
# ----------------------------------
st.subheader("📂 PDFs available in queries/")
st.write([str(p) for p in QUERY_DIR.glob("*.pdf")])

st.subheader("📂 Recently Uploaded PDFs (This Session Only)")
if saved_docs:
    st.write(saved_docs)
else:
    st.info("No documents uploaded in this session.")

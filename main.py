from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import List
import uuid
import threading
import time

# ---------------- YOUR MODULES ----------------
import engine as vl_engine
import Image_topdf as img2pdf_engine
import frequency as freq_engine
from json_to_pdf import json_to_pdf_with_images
from VL_output_to_json import extract_exam_questions

# ---------------- APP ----------------
app = FastAPI(title="Exam Pipeline Backend", version="0.1.0")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- PATHS ----------------
BASE_DIR = Path(__file__).resolve().parent
QUERY_DIR = BASE_DIR / "queries"
QUERY_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- JOB STATUS STORE ----------------
job_status = {}     # job_id → status
job_result = {}     # job_id → result

# ======================================================
# SAVE PDF
# ======================================================
@app.post("/save-pdf")
async def save_pdf(file: UploadFile = File(...)):
    pdf_name = f"{uuid.uuid4().hex}_{file.filename}"
    pdf_path = QUERY_DIR / pdf_name
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
    return {"path": str(pdf_path)}

# ======================================================
# IMAGES → PDF
# ======================================================
@app.post("/images-to-pdf")
async def images_to_pdf(files: List[UploadFile] = File(...)):
    pdf_path = QUERY_DIR / f"doc_{uuid.uuid4().hex}.pdf"
    img2pdf_engine.images_to_pdf(files=files, output_pdf_path=pdf_path)
    return {"path": str(pdf_path)}

# ======================================================
# BACKGROUND PIPELINE (DO NOT CHANGE LOGIC)
# ======================================================
def pipeline_worker(job_id: str, api_key: str, docs: List[str]):
    try:
        job_status[job_id] = "🔍 Running VL model..."

        docs = [Path(p) for p in docs]
        vl_results = []
        for i, pdf in enumerate(docs, start=1):
            md = vl_engine.VL_model(str(pdf), query_id=i)
            vl_results.append(md)

        job_status[job_id] = "🧠 Extracting JSON using LLM..."

        json_files = []
        for md in vl_results:
            out_json = md.replace(".md", ".json")
            extract_exam_questions(md, api_key, out_json)
            json_files.append(out_json)

        job_status[job_id] = "📊 Running semantic frequency..."

        freq_out = freq_engine.run_semantic_frequency_multiple(
            json_files, "output_frequency.json"
        )

        job_status[job_id] = "📄 Generating final PDF..."

        final_pdf = json_to_pdf_with_images(
            freq_out, image_base_dir="vl_output_bro"
        )

        job_result[job_id] = {
            "final_pdf": final_pdf,
            "frequency_json": "output_frequency.json"
        }

        job_status[job_id] = "✅ Completed"

    except Exception as e:
        job_status[job_id] = f"❌ Error: {e}"

# ======================================================
# START PIPELINE
# ======================================================
@app.post("/run-pipeline")
async def run_pipeline(api_key: str, docs: List[str]):
    job_id = uuid.uuid4().hex
    job_status[job_id] = "🚀 Job started"

    thread = threading.Thread(
        target=pipeline_worker,
        args=(job_id, api_key, docs),
        daemon=True
    )
    thread.start()

    return {"job_id": job_id}

# ======================================================
# GET JOB STATUS
# ======================================================
@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    return {
        "status": job_status.get(job_id, "Unknown job"),
        "result": job_result.get(job_id)
    }
import os
from fastapi.responses import FileResponse
# ======================================================
# DOWNLOAD FILE (FOR VUE FRONTEND)
# ======================================================
@app.get("/download")
async def download_file(path: str):
    if not os.path.exists(path):
        return {"error": "File not found"}

    return FileResponse(
        path,
        filename=os.path.basename(path),
        media_type="application/octet-stream"
    )

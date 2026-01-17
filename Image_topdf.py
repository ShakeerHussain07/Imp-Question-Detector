from PIL import Image
from io import BytesIO
from pathlib import Path

def images_to_pdf(files, output_pdf_path: Path):
    images = []

    for file in files:
        # FastAPI UploadFile → bytes → PIL Image
        file_bytes = file.file.read()
        img = Image.open(BytesIO(file_bytes)).convert("RGB")
        images.append(img)

    if not images:
        raise ValueError("No valid images provided")

    images[0].save(
        output_pdf_path,
        save_all=True,
        append_images=images[1:]
    )

    return str(output_pdf_path)

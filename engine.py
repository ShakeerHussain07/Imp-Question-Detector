# import base64
# import os
# import requests

# API_URL = "https://j103s9d2e4dccfoc.aistudio-app.com/layout-parsing"
# TOKEN = "3f77a7dbc0756fef96d9d6791f485b062106ef51"

# # file_path = r"C:\Users\shiva\OneDrive\Desktop\ip.pdf"

# # ---------- READ PDF ----------
# def VL_model(file_path: str):
#     with open(file_path, "rb") as file:
#         file_bytes = file.read()
#         file_data = base64.b64encode(file_bytes).decode("ascii")

#     headers = {
#         "Authorization": f"token {TOKEN}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "file": file_data,
#         "fileType": 0,
#         "useDocOrientationClassify": False,
#         "useDocUnwarping": False,
#         "useChartRecognition": False,
#     }

#     response = requests.post(API_URL, json=payload, headers=headers)
#     assert response.status_code == 200

#     result = response.json()["result"]

#     # ---------- OUTPUT ----------
#     output_dir = "img2"
#     os.makedirs(output_dir, exist_ok=True)

#     FINAL_MD_PATH = os.path.join(output_dir, "final_document.md")

#     with open(FINAL_MD_PATH, "w", encoding="utf-8") as final_md:

#         for i, res in enumerate(result["layoutParsingResults"]):

#             # Page separator (VERY IMPORTANT for parsing later)
#             final_md.write(f"\n\n---\n## PAGE {i+1}\n---\n\n")

#             # Append markdown text
#             final_md.write(res["markdown"]["text"])
#             final_md.write("\n")

#             # Save embedded images
#             for img_path, img_url in res["markdown"]["images"].items():
#                 full_img_path = os.path.join(output_dir, img_path)
#                 os.makedirs(os.path.dirname(full_img_path), exist_ok=True)

#                 img_bytes = requests.get(img_url).content
#                 with open(full_img_path, "wb") as img_file:
#                     img_file.write(img_bytes)

#             # Save detected layout images (figures, tables)
#             for img_name, img_url in res["outputImages"].items():
#                 img_response = requests.get(img_url)
#                 if img_response.status_code == 200:
#                     filename = os.path.join(output_dir, f"{img_name}_page{i+1}.jpg")
#                     with open(filename, "wb") as f:
#                         f.write(img_response.content)

#     print(f"✅ Single merged markdown saved at: {FINAL_MD_PATH}")
#     return FINAL_MD_PATH
import base64
import os
import requests

API_URL = "https://j103s9d2e4dccfoc.aistudio-app.com/layout-parsing"
TOKEN = "3f77a7dbc0756fef96d9d6791f485b062106ef51"

def VL_model(file_path: str, query_id: int):
    # ---------- READ PDF ----------
    with open(file_path, "rb") as file:
        file_data = base64.b64encode(file.read()).decode("ascii")

    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "file": file_data,
        "fileType": 0,
        "useDocOrientationClassify": False,
        "useDocUnwarping": False,
        "useChartRecognition": False,
    }

    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()["result"]

    # ---------- OUTPUT STRUCTURE ----------
    BASE_DIR = "vl_output_bro"
    IMG_DIR = os.path.join(BASE_DIR, "imgs")
    QUERY_DIR = os.path.join(BASE_DIR, f"query_{query_id}")

    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(QUERY_DIR, exist_ok=True)

    FINAL_MD_PATH = os.path.join(QUERY_DIR, "final_document.md")

    with open(FINAL_MD_PATH, "w", encoding="utf-8") as final_md:

        for page_no, res in enumerate(result["layoutParsingResults"], start=1):

            # ---------- PAGE HEADER ----------
            final_md.write(f"\n\n---\n## PAGE {page_no}\n---\n\n")
            final_md.write(res["markdown"]["text"])
            final_md.write("\n")

            # ---------- EMBEDDED MARKDOWN IMAGES ----------
            for img_path, img_url in res["markdown"]["images"].items():
                # ✅ USE EXACT SAME IMAGE NAME AS HTML
                img_name = os.path.basename(img_path)
                img_file_path = os.path.join(IMG_DIR, img_name)

                if not os.path.exists(img_file_path):
                    img_bytes = requests.get(img_url).content
                    with open(img_file_path, "wb") as img_file:
                        img_file.write(img_bytes)

                # ✅ RELATIVE PATH FROM query_X → imgs
                final_md.write(f"\n![img](../imgs/{img_name})\n")

            # ---------- DETECTED LAYOUT IMAGES ----------
            for img_name, img_url in res["outputImages"].items():
                img_name = f"{img_name}.jpg"
                img_file_path = os.path.join(IMG_DIR, img_name)

                if not os.path.exists(img_file_path):
                    img_bytes = requests.get(img_url).content
                    with open(img_file_path, "wb") as f:
                        f.write(img_bytes)

    print(f"✅ VL markdown saved at: {FINAL_MD_PATH}")
    print(f"✅ Images saved in: {IMG_DIR}")
    return FINAL_MD_PATH



import os
import fitz  # PyMuPDF
import re
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests

APP_PORT =int(os.getenv("SERVICE_PORT"))

OUTPUT_FOLDER = './output'
# Tạo FastAPI app
app = FastAPI()

# Thư mục lưu trữ tệp PDF tạm thời
UPLOAD_FOLDER = './pdf_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Hàm loại bỏ khoảng trắng dư thừa
def remove_space_redundant(text):
    words = text.split()
    clean_text = " ".join(words)
    return clean_text

# Hàm lấy nội dung từ file PDF
def get_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Hàm tạo cấu trúc JSON từ văn bản
def create_chunk_json(text):
    content_between_chapters = re.findall(
        r"(Chương \b(?:I{1,3}(?:V?X?)?|VI{0,3}|XI{0,3}V?|XVI{0,3})\b\.?)(.*?)(?=(Chương \b(?:I{1,3}(?:V?X?)?|VI{0,3}|XI{0,3}V?|XVI{0,3})\b\.? |$))", 
        text, 
        re.DOTALL
    )
    
    chapter_title = []
    rule_title = []
    contents = []

    for content_between_chapter in content_between_chapters:
        chapter_name_temp = content_between_chapter[0].strip()
        content_chapter_temp = content_between_chapter[1].strip()
        chapter_title.append(chapter_name_temp)
        contents.append(content_chapter_temp)

    regex_chapter = re.compile(r'(Chương \b(?:I{1,3}(?:V?X?)?|VI{0,3}|XI{0,3}V?|XVI{0,3})\b\.?)\s*(.*)')
    regex_rule = re.compile(r'(Điều \d+\.)(.*?)(?=(Điều \d+\. |$))', re.DOTALL)

    data = []
    for content_chap in contents:
        matches_chapter = regex_chapter.findall(content_chap)
        matches_rule = regex_rule.findall(content_chap)

        for match_rule in matches_rule:
            for match_chapter in matches_chapter:
                temp = match_chapter[0] + "\n" + match_chapter[1]
                chapter_title.append(temp.strip())

            temp_title_rule = match_rule[0] + match_rule[1].split('\n')[0].strip()
            rule_title.append(temp_title_rule.strip())
            temp_content_rule = remove_space_redundant(" ".join(match_rule[1].split('\n')[1:]).strip())
            # chia nho noi dung thanh cac doan nho temp_content_rule voi do dai toi da la 1000
            while len(temp_content_rule) > 512:
                data.append({
                    'title': f"Document Title\n{chapter_title[-1]}\n{temp_title_rule}",
                    'context': temp_content_rule[:512]
                })
                temp_content_rule = temp_content_rule[512:]

    return data

# API để tải tệp PDF lên và xử lý
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file format. Only PDF is supported.")

    # Lưu tệp PDF vào thư mục tạm thời
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        # Đọc và xử lý tệp PDF
        text = get_text_from_pdf(file_path)
        json_data = create_chunk_json(text)

        # tao file json tu json_data va luu file json vao ./output
        
        json_file_path = os.path.join(OUTPUT_FOLDER, file.filename.replace('.pdf', '.json'))
        with open(json_file_path, 'w') as f:
            json.dump(json_data, f, ensure_ascii=False)

        await handle_indexing_pipeline()
        return JSONResponse(content={"message": "File uploaded and processed successfully", "json_file_path": json_file_path})

    finally:
        # Xóa tệp PDF sau khi xử lý xong
        os.remove(file_path)

async def handle_indexing_pipeline():
    # doc cac file json trong folder output va gui request den indexing pipeline
    # de index cac document

    # doc cac file json trong folder output

    for file_name in os.listdir(OUTPUT_FOLDER):
        if file_name.endswith(".json"):
            file_path = os.path.join(OUTPUT_FOLDER, file_name)
            with open(file_path, 'r') as f:
                # send file to indexing pipeline

                response = requests.post("http://indexing-pipeline:6001/embed_and_import_json", files={"file": f})
                
                print(response.json())

   
    return response


if __name__ == "__main__":
    # Chạy ứng dụng FastAPI bằng Uvicorn
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=APP_PORT,reload=True)

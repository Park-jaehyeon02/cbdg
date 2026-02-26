from fastapi import FastAPI, File, UploadFile
from paddleocr import PaddleOCR
import requests
import cv2
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vercel 주소만 넣는 것이 보안상 좋지만, 테스트를 위해 "*" 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GPU를 사용하도록 설정 (RTX 5080의 위력!)
ocr = PaddleOCR(use_angle_cls=True, lang='korean', use_gpu=True)


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    # 1. 이미지 읽기
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 2. Local OCR 실행 (5080 기반 초고속 추출)
    result = ocr.ocr(image, cls=True)
    full_text = ""
    for idx in range(len(result)):
        for line in result[idx]:
            full_text += line[1][0] + " "

    # 3. Ollama (Llama 3.1)에게 분석 요청
    prompt = f"""
    당신은 부동산 전문 법률 AI '철벽등기'입니다. 
    다음 등기부등본/계약서 텍스트를 분석하여 '신탁 사기'나 '독소 조항'이 있는지 판독하세요.
    결과는 (🟢안전/🟡주의/🔴위험) 단계와 이유를 포함해야 합니다.

    분석할 텍스트: {full_text}
    """

    response = requests.post("http://localhost:11434/api/generate",
                             json={"model": "llama3.1", "prompt": prompt, "stream": False})

    return {
        "analysis": response.json().get("response"),
        "extracted_text": full_text[:200] + "..."  # 확인용 일부 출력
    }
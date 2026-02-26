from fastapi import FastAPI, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
import easyocr
import numpy as np
import cv2
import requests
import uvicorn

app = FastAPI()

# Vercel 프론트엔드와 통신을 위한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RTX 5080 환경: 드라이버 안정화 전까지는 gpu=False(CPU) 권장, 가능하면 True로 시도
print("🚀 철벽등기 AI 엔진 로딩 중... (EasyOCR)")
reader = easyocr.Reader(['ko', 'en'], gpu=False)


@app.get("/")
def home():
    return {"message": "철벽등기 백엔드 서버가 작동 중입니다. (Port 8000)"}


# [1단계] 이미지에서 텍스트 추출 (OCR)
@app.post("/ocr")
async def get_ocr_text(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = reader.readtext(image)
    # 가독성을 위해 줄바꿈으로 텍스트 결합
    full_text = "\n".join([res[1] for res in results])

    return {"extracted_text": full_text}


# [2단계] 사용자가 수정한 텍스트 분석 (LLM)
@app.post("/analyze-final")
async def analyze_final(data: dict = Body(...)):
    user_text = data.get("text", "")

    # 5080의 성능을 믿고 상세한 프롬프트를 보냅니다.
    prompt = f"""
    당신은 대한민국 부동산 법률 전문가 AI '철벽등기'입니다.
    사용자가 검수한 다음 등기부/계약서 텍스트를 분석하여 '전세사기' 위험도를 판독하세요.

    [텍스트 내용]:
    {user_text}

    [응답 양식]:
    1. 등급: 🟢안전 / 🟡주의 / 🔴위험 중 하나를 선택하고 크게 표시.
    2. 분석 요약: 발견된 주요 위험 요소(신탁, 근저당, 가압류 등)를 설명.
    3. 상세 조치: 사용자가 임대인이나 중개사에게 확인해야 할 구체적인 질문 리스트.
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.1", "prompt": prompt, "stream": False},
            timeout=60
        )
        analysis = response.json().get("response", "분석 결과를 생성하지 못했습니다.")
    except Exception as e:
        analysis = f"Ollama 연결 실패: {str(e)}"

    return {"analysis": analysis}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
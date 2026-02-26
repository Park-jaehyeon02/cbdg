from fastapi import FastAPI, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
import easyocr
import numpy as np
import cv2
import requests
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RTX 5080 환경: 현재는 안전을 위해 gpu=False로 세팅되어 있습니다.
# 나중에 cu128이 sm_120을 완벽지원하면 True로 바꾸세요!
print("🚀 RTX 5080 서버 준비 완료 (EasyOCR)")
reader = easyocr.Reader(['ko', 'en'], gpu=False)


@app.get("/")
def home():
    return {"message": "철벽등기 서버 가동 중"}


# [Step 1] 이미지 -> 텍스트 추출
@app.post("/ocr")
async def get_ocr_text(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    results = reader.readtext(image)
    full_text = "\n".join([res[1] for res in results])
    return {"extracted_text": full_text}


# [Step 2] 수정된 텍스트 -> 최종 위험 분석
@app.post("/analyze")
async def analyze_final(data: dict = Body(...)):
    user_text = data.get("text", "")

    prompt = f"""
    당신은 부동산 전문 AI '철벽등기'입니다. 
    다음 등기부 텍스트를 정밀 분석하여 전세사기 위험도를 판독하세요.

    [텍스트]:
    {user_text}

    결과는 반드시 🟢안전/🟡주의/🔴위험 등급을 포함하여 상세히 설명하세요.
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.1", "prompt": prompt, "stream": False},
            timeout=60
        )
        analysis = response.json().get("response", "분석 결과를 가져오지 못했습니다.")
    except Exception as e:
        analysis = f"Ollama 연결 오류: {str(e)}"

    return {"analysis": analysis}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
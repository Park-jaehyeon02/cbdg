from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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


# 데이터 모델 정의 (유니코드 에러 방지)
class AnalysisRequest(BaseModel):
    text: str


print("🚀 RTX 5080 서버 가동 중 (EasyOCR CPU Mode)")
reader = easyocr.Reader(['ko', 'en'], gpu=False)


@app.get("/")
def home():
    return {"status": "online"}


# [1단계] 이미지에서 텍스트 추출 (FormData로 파일을 받음)
@app.post("/ocr")
async def get_ocr_text(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="이미지를 읽을 수 없습니다.")

        results = reader.readtext(image)
        full_text = "\n".join([res[1] for res in results])
        return {"extracted_text": full_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# [2단계] 수정된 텍스트 분석 (JSON으로 텍스트를 받음)
@app.post("/analyze")
async def analyze_final(request: AnalysisRequest):  # BaseModel 적용
    user_text = request.text

    if not user_text.strip():
        return {"analysis": "분석할 내용이 없습니다. 텍스트를 입력해주세요."}

    prompt = f"부동산 전문가로서 다음 내용을 분석해 🟢안전/🟡주의/🔴위험 등급을 매겨줘:\n{user_text}"

    try:
        # Ollama API 호출
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.1", "prompt": prompt, "stream": False},
            timeout=60
        )
        return {"analysis": response.json().get("response", "분석 실패")}
    except Exception as e:
        return {"analysis": f"Ollama 연결 오류: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import easyocr
import numpy as np
import cv2
import requests
import uvicorn

app = FastAPI()

# 프론트엔드 연동을 위한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 데이터 모델 정의 (JSON 파싱 에러 방지)
class AnalysisRequest(BaseModel):
    text: str


# 엔진 초기화 (RTX 5080 호환성을 위해 우선 CPU 모드로 설정)
print("🚀 철벽등기 엔진 가동 중...")
reader = easyocr.Reader(['ko', 'en'], gpu=False)


@app.get("/")
def home():
    return {"status": "online", "device": "RTX 5080 Ready"}


# [1단계] 이미지 업로드 -> 텍스트 추출 (OCR)
@app.post("/ocr")
async def get_ocr_text(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="이미지를 읽을 수 없습니다.")

        results = reader.readtext(image)
        # 줄바꿈을 포함하여 가독성 있게 텍스트 결합
        full_text = "\n".join([res[1] for res in results])

        return {"extracted_text": full_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# [2단계] 사용자가 수정한 텍스트 분석 (LLM)
@app.post("/analyze")
async def analyze_final(request: AnalysisRequest):
    user_text = request.text

    if not user_text.strip():
        return {"analysis": "분석할 내용이 없습니다. 텍스트를 입력해주세요."}

    # RTX 5080의 성능을 활용한 정밀 분석 프롬프트
    prompt = f"""
    당신은 부동산 전문 AI '철벽등기'입니다. 
    사용자가 검수한 다음 텍스트에서 전세사기 위험(신탁, 근저당, 압류 등)을 분석하세요.
    반드시 🟢안전 / 🟡주의 / 🔴위험 등급을 먼저 표시하고 상세 이유를 설명하세요.
    ---
    분석할 내용:
    {user_text}
    """

    try:
        # 로컬 Ollama 서버 호출
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
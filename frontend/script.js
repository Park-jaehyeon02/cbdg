const imageInput = document.getElementById('imageInput');
const ocrBtn = document.getElementById('ocrBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const editableText = document.getElementById('editableText');
const loading = document.getElementById('loading');
const serverUrlInput = document.getElementById('serverUrl');

// 파일 선택 시 활성화
imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        document.getElementById('fileName').innerText = e.target.files[0].name;
        ocrBtn.disabled = false;
    }
});

// [Step 1] OCR 추출
ocrBtn.addEventListener('click', async () => {
    const url = serverUrlInput.value.trim();
    if (!url) return alert("ngrok 주소를 입력하세요!");

    const formData = new FormData();
    formData.append('file', imageInput.files[0]);
    loading.classList.remove('hidden');

    try {
        const res = await fetch(`${url}/ocr`, { method: 'POST', body: formData });
        const data = await res.json();
        editableText.value = data.extracted_text;

        document.getElementById('step1').classList.add('hidden');
        document.getElementById('step2').classList.remove('hidden');
    } catch (err) {
        alert("OCR 실패: " + err.message);
    } finally {
        loading.classList.add('hidden');
    }
});

// [Step 2] 최종 분석 (JSON 전송)
analyzeBtn.addEventListener('click', async () => {
    const url = serverUrlInput.value.trim();
    const final_text = editableText.value;

    if (!final_text.trim()) return alert("수정할 내용이 없습니다.");

    loading.classList.remove('hidden');

    try {
        const res = await fetch(`${url}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: final_text }) // 텍스트만 전송
        });

        const data = await res.json();
        document.getElementById('step2').classList.add('hidden');
        document.getElementById('step3').classList.remove('hidden');
        document.getElementById('analysisResult').innerText = data.analysis;

        // 결과 배지 색상 업데이트
        updateBadge(data.analysis);
    } catch (err) {
        alert("분석 실패: " + err.message);
    } finally {
        loading.classList.add('hidden');
    }
});

function updateBadge(text) {
    const badge = document.getElementById('statusBadge');
    if (text.includes('🔴')) {
        badge.style.background = "#ef4444"; badge.innerText = "위험";
    } else if (text.includes('🟡')) {
        badge.style.background = "#f59e0b"; badge.innerText = "주의";
    } else {
        badge.style.background = "#10b981"; badge.innerText = "안전";
    }
}
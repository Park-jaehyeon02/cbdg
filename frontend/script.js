const imageInput = document.getElementById('imageInput');
const ocrBtn = document.getElementById('ocrBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const serverUrlInput = document.getElementById('serverUrl');

// 파일 선택 시 이름 표시
imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        document.getElementById('fileName').innerText = e.target.files[0].name;
        ocrBtn.disabled = false;
    }
});

// [1단계] OCR 요청
ocrBtn.addEventListener('click', async () => {
    const url = serverUrlInput.value.trim();
    if (!url) return alert("ngrok 주소를 입력해주세요!");

    const formData = new FormData();
    formData.append('file', imageInput.files[0]);

    loading.classList.remove('hidden');

    try {
        const response = await fetch(`${url}/ocr`, { method: 'POST', body: formData });
        const data = await response.json();

        document.getElementById('editableText').value = data.extracted_text;
        document.getElementById('uploadSection').classList.add('hidden');
        document.getElementById('editSection').classList.remove('hidden');
    } catch (err) {
        alert("OCR 실패: " + err.message);
    } finally {
        loading.classList.add('hidden');
    }
});

// [2단계] AI 분석 요청
analyzeBtn.addEventListener('click', async () => {
    const url = serverUrlInput.value.trim();
    const text = document.getElementById('editableText').value;

    loading.classList.remove('hidden');

    try {
        const response = await fetch(`${url}/analyze-final`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await response.json();

        document.getElementById('editSection').classList.add('hidden');
        document.getElementById('resultSection').classList.remove('hidden');
        document.getElementById('analysisResult').innerText = data.analysis;

        // 등급에 따른 배지 색상 변경
        const badge = document.getElementById('statusBadge');
        if (data.analysis.includes('🔴')) {
            badge.style.backgroundColor = "#ef4444"; badge.innerText = "위험";
        } else if (data.analysis.includes('🟡')) {
            badge.style.backgroundColor = "#f59e0b"; badge.innerText = "주의";
        } else {
            badge.style.backgroundColor = "#10b981"; badge.innerText = "안전";
        }
    } catch (err) {
        alert("분석 실패: " + err.message);
    } finally {
        loading.classList.add('hidden');
    }
});
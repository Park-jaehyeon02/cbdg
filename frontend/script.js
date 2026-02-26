const imageInput = document.getElementById('imageInput');
const ocrBtn = document.getElementById('ocrBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const editableText = document.getElementById('editableText');
const loading = document.getElementById('loading');
const serverUrlInput = document.getElementById('serverUrl');

// 스텝 변경 함수
function setStep(stepNum) {
    document.querySelectorAll('.step').forEach((s, idx) => {
        s.classList.toggle('active', idx + 1 <= stepNum);
    });
}

// 파일 선택 처리
imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        document.getElementById('fileName').innerText = `📄 ${e.target.files[0].name}`;
        ocrBtn.disabled = false;
    }
});

// [Step 1] OCR 추출
ocrBtn.addEventListener('click', async () => {
    const url = serverUrlInput.value.trim();
    if (!url) return alert("서버 주소를 입력해주세요!");

    const formData = new FormData();
    formData.append('file', imageInput.files[0]);
    loading.classList.remove('hidden');

    try {
        const res = await fetch(`${url}/ocr`, { method: 'POST', body: formData });
        const data = await res.json();

        editableText.value = data.extracted_text;
        document.getElementById('step1').classList.add('hidden');
        document.getElementById('step2').classList.remove('hidden');
        setStep(2);
    } catch (err) {
        alert("OCR 오류: " + err.message);
    } finally {
        loading.classList.add('hidden');
    }
});

// [Step 2] AI 분석
analyzeBtn.addEventListener('click', async () => {
    const url = serverUrlInput.value.trim();
    const final_text = editableText.value;
    if (!final_text.trim()) return alert("검수할 내용이 없습니다.");

    loading.classList.remove('hidden');

    try {
        const res = await fetch(`${url}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: final_text })
        });
        const data = await res.json();

        document.getElementById('step2').classList.add('hidden');
        document.getElementById('step3').classList.remove('hidden');
        document.getElementById('analysisResult').innerText = data.analysis;
        setStep(3);
        updateStatusBadge(data.analysis);
    } catch (err) {
        alert("분석 오류: " + err.message);
    } finally {
        loading.classList.add('hidden');
    }
});

function updateStatusBadge(text) {
    const badge = document.getElementById('statusBadge');
    if (text.includes('🔴')) {
        badge.style.background = "#ef4444"; badge.innerText = "위험 🔴";
    } else if (text.includes('🟡')) {
        badge.style.background = "#f59e0b"; badge.innerText = "주의 🟡";
    } else {
        badge.style.background = "#10b981"; badge.innerText = "안전 🟢";
    }
}
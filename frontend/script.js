const imageInput = document.getElementById('imageInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultSection = document.getElementById('resultSection');
const analysisResult = document.getElementById('analysisResult');
const statusBadge = document.getElementById('statusBadge');
const loading = document.getElementById('loading');

imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        document.getElementById('fileName').innerText = e.target.files[0].name;
        analyzeBtn.disabled = false;
    }
});

analyzeBtn.addEventListener('click', async () => {
    const serverUrl = document.getElementById('serverUrl').value.trim();
    if (!serverUrl) return alert("ngrok 주소를 입력해주세요!");

    const formData = new FormData();
    formData.append('file', imageInput.files[0]);

    loading.classList.remove('hidden');
    resultSection.classList.add('hidden');

    try {
        const response = await fetch(`${serverUrl}/analyze`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        // 결과 표시
        loading.classList.add('hidden');
        resultSection.classList.remove('hidden');
        analysisResult.innerText = data.analysis;

        // 상태 배지 색상 결정
        if (data.analysis.includes('🔴')) {
            statusBadge.innerText = "위험";
            statusBadge.style.backgroundColor = "#ef4444";
        } else if (data.analysis.includes('🟡')) {
            statusBadge.innerText = "주의";
            statusBadge.style.backgroundColor = "#f59e0b";
        } else {
            statusBadge.innerText = "안전";
            statusBadge.style.backgroundColor = "#10b981";
        }
    } catch (error) {
        alert("분석 실패: " + error.message);
        loading.classList.add('hidden');
    }
});
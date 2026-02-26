// [2단계 분석 버튼 이벤트 부분만 교체]
analyzeBtn.addEventListener('click', async () => {
    const url = serverUrlInput.value.trim();
    const textToAnalyze = editableText.value; // 사용자가 수정한 텍스트

    if (!textToAnalyze) return alert("분석할 텍스트가 없습니다.");

    loading.classList.remove('hidden');

    try {
        const response = await fetch(`${url}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // 반드시 명시
            },
            body: JSON.stringify({ text: textToAnalyze }) // 구조 확인: { "text": "..." }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(JSON.stringify(errorData.detail));
        }

        const data = await response.json();

        document.getElementById('editSection').classList.add('hidden');
        document.getElementById('resultSection').classList.remove('hidden');
        document.getElementById('analysisResult').innerText = data.analysis;

        // 등급 배지 업데이트 (중복 코드 생략)
        updateStatusBadge(data.analysis);

    } catch (err) {
        console.error("Error details:", err);
        alert("분석 실패: " + err.message);
    } finally {
        loading.classList.add('hidden');
    }
});

function updateStatusBadge(analysis) {
    const badge = document.getElementById('statusBadge');
    if (analysis.includes('🔴')) {
        badge.style.backgroundColor = "#ef4444"; badge.innerText = "위험";
    } else if (analysis.includes('🟡')) {
        badge.style.backgroundColor = "#f59e0b"; badge.innerText = "주의";
    } else {
        badge.style.backgroundColor = "#10b981"; badge.innerText = "안전";
    }
}
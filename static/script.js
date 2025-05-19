document.getElementById('upload-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const fileInput = document.getElementById('file');
    const modelSelect = document.getElementById('model-select');
    const processStatus = document.getElementById('process-status');
    const resultDiv = document.getElementById('result');

    const file = fileInput.files[0];
    const model = modelSelect.value;

    if (!file) {
        alert('Vui lòng chọn một file CSV!');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', model);

    try {
        // Bắt đầu tính thời gian
        const startTime = performance.now();

        // Hiển thị trạng thái đang xử lý
        processStatus.innerHTML = `<p>Đang tải lên và xử lý file...</p>`;
        resultDiv.innerHTML = '';

        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Kiểm tra nếu kết quả không hợp lệ
        if (!data || !data.status) {
            throw new Error('Dữ liệu trả về từ server không hợp lệ!');
        }

        // Kết thúc tính thời gian
        const endTime = performance.now();
        const elapsedTime = ((endTime - startTime) / 1000).toFixed(2); // Chuyển mili giây sang giây

        // Cập nhật trạng thái hoàn tất
        processStatus.innerHTML = `<p>Dự đoán hoàn thành trong ${elapsedTime} giây.</p>`;

        // Hiển thị trạng thái của nhãn có số lượng nhiều nhất
        resultDiv.innerHTML = `
            <h2>Kết quả dự đoán:</h2>
            <p style="color: black; font-weight: bold;">${data.status}</p>
        `;
    } catch (error) {
        console.error('Lỗi:', error);
        processStatus.innerHTML = `<p class="error">Lỗi xảy ra: ${error.message}</p>`;
    }
});

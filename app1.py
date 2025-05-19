from flask import Flask, render_template, jsonify
import os
import pandas as pd
import numpy as np
import threading
import time
import glob
from scipy import signal
import tensorflow as tf

app = Flask(__name__)

# Định nghĩa đường dẫn mô hình
model_path = "/Users/truongvietanh/Downloads/Model python Đồ án/App/models/"

# Tải mô hình DNN
try:
    dnn_model = tf.keras.models.load_model(model_path + "DNN_model.h5")
    print("Tải mô hình DNN thành công")
except Exception as e:
    print(f"Lỗi khi tải mô hình DNN: {e}")
    dnn_model = None

# Ánh xạ nhãn cho kết quả
label_mapping = {
    0: "Máy ở trạng thái Normal",
    1: "Máy bị lỗi mất cân bằng",
    2: "Máy bị lỗi lệch trục ngang",
    3: "Máy bị lỗi lệch trục dọc"
}

# Thư mục chứa các file CSV cảm biến
CSV_FOLDER = "/Users/truongvietanh/Downloads/Model ML Đồ án/Model DA2/fault-induction-motor-dataset/normal/normal"

# Lưu trữ lịch sử dự đoán (tối đa 10 bản ghi)
prediction_history = []

# Hàm FFT
def FFT(data):
    autocorr = signal.fftconvolve(data, data[::-1], mode='full')
    return pd.DataFrame(autocorr)

# Hàm giảm số lượng dữ liệu
def downSampler(data, a, b):
    data_decreased = []
    x = b
    for i in range(int(len(data) / x)):
        chunk = data.iloc[a:b, :].sum() / x
        data_decreased.append(chunk)
        a += x
        b += x
    return pd.DataFrame(data_decreased).reset_index(drop=True)

# Hàm tiền xử lý để chuẩn bị dữ liệu đầu vào cho mô hình
def preprocess_data(file_path):
    try:
        # Đọc file CSV
        df = pd.read_csv(file_path, header=None)
        
        # Áp dụng downsampling
        df = downSampler(df, 0, 5000)
        
        # Áp dụng FFT
        df = FFT(df)
        
        # Chuyển đổi thành mảng numpy
        processed = df.values
        
        # Định hình lại nếu cần
        if len(processed.shape) == 1:
            processed = np.expand_dims(processed, axis=0)
            
        # Kiểm tra xem mô hình có cần định hình cụ thể không
        if dnn_model is not None:
            input_shape = dnn_model.input_shape
            if len(input_shape) > 2:  # Nếu mô hình mong đợi nhiều chiều hơn
                processed = processed.reshape(1, -1, 1)  # Ví dụ reshape, điều chỉnh nếu cần
                
        return processed
    except Exception as e:
        print(f"Lỗi khi tiền xử lý dữ liệu: {e}")
        return None

# Dự đoán từ file csv mới nhất
def read_and_predict():
    global prediction_history
    
    try:
        if dnn_model is None:
            print("Mô hình DNN chưa được tải")
            return False
            
        files = glob.glob(os.path.join(CSV_FOLDER, "*.csv"))
        if not files:
            print("Không tìm thấy file CSV trong thư mục")
            return False
        
        latest_file = max(files, key=os.path.getctime)
        print(f"Đang xử lý file: {latest_file}")
        
        # Tiền xử lý dữ liệu
        processed_data = preprocess_data(latest_file)
        if processed_data is None:
            print("Tiền xử lý dữ liệu thất bại")
            return False
            
        # Thực hiện dự đoán sử dụng mô hình DNN
        prediction = dnn_model.predict(processed_data)
        predicted_label = int(np.argmax(prediction, axis=1)[0])
        
        # Lấy văn bản nhãn dự đoán
        label_text = label_mapping.get(predicted_label, "Không xác định")
        
        # Ghi lại dự đoán vào lịch sử
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        prediction_history.insert(0, {
            "time": timestamp,
            "file": os.path.basename(latest_file),
            "label": predicted_label,
            "label_text": label_text
        })
        
        # Giới hạn 10 kết quả gần đây nhất
        prediction_history[:] = prediction_history[:10]
        
        print(f"Dự đoán: {label_text}")
        return True
        
    except Exception as e:
        print(f"Lỗi trong read_and_predict: {e}")
        return False

# Tự động cập nhật dự đoán mỗi 5 phút
def auto_run():
    while True:
        read_and_predict()
        time.sleep(300)  # 5 phút

# Giao diện chính
@app.route("/")
def index():
    return render_template("services1.html", history=prediction_history)

# API trả về lịch sử dự đoán
@app.route("/api/history")
def api_history():
    return jsonify(prediction_history)

# API để kích hoạt dự đoán thủ công
@app.route("/api/predict_now")
def api_predict_now():
    success = read_and_predict()
    return jsonify({
        "status": "success" if success else "error",
        "latest": prediction_history[0] if prediction_history else None
    })

# Khởi động luồng dự đoán nền
if __name__ == "__main__":
    # Khởi động luồng dự đoán nền
    threading.Thread(target=auto_run, daemon=True).start()
    
    # Khởi động ứng dụng Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
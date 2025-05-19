from flask import Flask, request, render_template, jsonify
import pandas as pd
import joblib
from collections import Counter
import numpy as np
from scipy import signal
import tensorflow as tf  # Nếu dùng mô hình DNN của Keras/TensorFlow

app = Flask(__name__)

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

# Đường dẫn đến mô hình
model_path = "/Users/truongvietanh/Downloads/Model python Đồ án/App/models/"

# Load các mô hình
models = {
    "dt_model": joblib.load(model_path + "dt_model.pkl"),
    "rf_model": joblib.load(model_path + "rf_model.pkl"),
    "SVM_model": joblib.load(model_path + "SVM_model.pkl"),
    "KNN_model": joblib.load(model_path + "kNN_model.pkl"),
}

# Kiểm tra xem DNN model có phải TensorFlow không
try:
    models["DNN_model"] = tf.keras.models.load_model(model_path + "DNN_model.h5")
except Exception as e:
    print("Lỗi khi tải DNN model:", e)

# Map số nhãn thành trạng thái tương ứng
label_mapping = {
    0: "Máy ở trạng thái Normal",
    1: "Máy bị lỗi mất cân bằng",
    2: "Máy bị lỗi lệch trục ngang",
    3: "Máy bị lỗi lệch trục dọc"
}

@app.route('/')
def index():
    return render_template('services.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    model_name = request.form.get('model', 'dt_model')
    
    if model_name not in models:
        return jsonify({'error': 'Invalid model selected'}), 400
    
    try:
        # Đọc file CSV
        data = pd.read_csv(file)
        data = downSampler(data, 0, 5000)
        data = FFT(data)

        # Chọn mô hình
        model = models[model_name]

        # Xử lý đầu vào nếu là mô hình DNN
        if model_name == "DNN_model":
            data = data.to_numpy().reshape((data.shape[0], data.shape[1], 1))  # Nếu cần reshape
            predictions = model.predict(data)
            predictions = np.argmax(predictions, axis=1)  # Nếu mô hình trả về xác suất softmax
        else:
            predictions = model.predict(data)

        # Đếm số lượng dự đoán cho mỗi nhãn
        label_counts = dict(Counter(predictions))
        label_counts = {int(key): value for key, value in label_counts.items()}

        # Xác định nhãn xuất hiện nhiều nhất
        most_common_label = max(label_counts, key=label_counts.get)
        most_common_label_text = label_mapping.get(most_common_label, "Không xác định")

        return jsonify({
            'label_counts': label_counts,
            'most_common_label': most_common_label,
            'status': most_common_label_text
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

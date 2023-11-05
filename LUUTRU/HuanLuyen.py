import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
import pyodbc
import time
import joblib
# Ghi lại thời điểm bắt đầu
start_time = time.time()
# Thiết lập thông tin kết nối
server = 'DESKTOP-6BMLQQ6\SQLSERVER'  # Tên hoặc địa chỉ IP của máy chủ SQL
database = 'BARBERSHOP12'  # Tên cơ sở dữ liệu
username = 'SA'  # Tên người dùng SQL
password = '352636'  # Mật khẩu SQL

connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

# Kết nối đến cơ sở dữ liệu
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Đọc tập dữ liệu huấn luyện từ file CSV
df = pd.read_csv('Du_lieu_huan_luyen2.txt')
print(df)
# Tạo một bản sao của cột "Nhan" để sử dụng sau này
labels = df['Nhan'].copy()
# Tạo cột nhãn dựa trên các giá trị
#df['Nhan'] = df['Nhan'].apply(lambda x: 0 if x == 'khongnhap' else (1 if x == 'nhapit' else 2))

# Chuẩn hóa các đặc trưng số
scaler = StandardScaler()
df[['LuongTon', 'SoLuongNhap', 'NgayNhapHangGanNhat']] = scaler.fit_transform(df[['LuongTon', 'SoLuongNhap', 'NgayNhapHangGanNhat']])
# Chia dữ liệu thành tập huấn luyện và tập kiểm tra
X = df[['LuongTon', 'SoLuongNhap', 'NgayNhapHangGanNhat']]
y = df['Nhan']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Tạo và huấn luyện mô hình SVM cho bài toán phân loại

model = SVC(kernel='linear', C=0.544)
model.fit(X_train, y_train)
print(f"Số lượng hỗ trợ vectors: {len(model.support_)}")
print(f"Kích thước ma trận hệ số: {model.coef_.shape}")
# Dự đoán trên tập kiểm tra
y_pred = model.predict(X_test)
print(X_test)
# Đánh giá mô hình

mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error: {mae}")

# Lưu mô hình

joblib.dump(model, 'svm_model.pkl')

print("Model trained and saved successfully.")

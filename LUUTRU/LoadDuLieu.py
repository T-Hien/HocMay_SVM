import pandas as pd
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
# Tạo kết nối SQL
#engine = create_engine(connection_string)


# ***********************************************
model = joblib.load('svm_model.pkl')
# Tên của stored procedure hoặc câu truy vấn SQL
stored_proc_name = "NhapHang_TonKho"

# Thực hiện truy vấn SQL hoặc gọi stored procedure và chuyển kết quả thành DataFrame
query = f"EXEC {stored_proc_name}"
dt = pd.read_sql_query(query, conn)
# Chọn các đặc trưng cần dự đoán
X_new = dt[['LuongTon', 'SoLuongNhap', 'NgayNhapHangGanNhat']]

# Dự đoán nhãn cho sản phẩm mới
y_pred = model.predict(X_new)
print(y_pred)

# Gán nhãn cho từng sản phẩm dựa trên ngưỡng
labels = ["khongnhap" if pred == 0 else "nhap" for pred in y_pred]

# SQL Merge Query
sql_merge = """
MERGE INTO HocMay AS target
USING (VALUES (?, ?, ?, ?, ?, ?)) AS source (MaSanPham, TenSanPham, ThoiGianNhap, SoLuongTon, SoLuongNhap, Nhan)
ON target.MaSanPham = source.MaSanPham
WHEN MATCHED THEN
    UPDATE SET target.Nhan = source.Nhan,target.ThoiGianNhap = source.ThoiGianNhap,
    target.SoLuongTon = source.SoLuongTon,target.SoLuongNhap = source.SoLuongNhap
WHEN NOT MATCHED THEN
    INSERT (MaSanPham, TenSanPham, ThoiGianNhap, SoLuongTon, SoLuongNhap, Nhan)
    VALUES (source.MaSanPham, source.TenSanPham, source.ThoiGianNhap, source.SoLuongTon, source.SoLuongNhap, source.Nhan);
"""

print('MaSP', 'TenSP', 'LuongTon', 'SoLuongNhap', 'ThoiGian', 'Nhan')
# Lặp qua dữ liệu và lưu trữ vào cơ sở dữ liệu
for i, label in enumerate(labels):
    masp = dt['MaSanPham'].iloc[i]
    tensp = dt['TenSanPham'].iloc[i]
    thoigian = int(dt['NgayNhapHangGanNhat'].iloc[i])
    luongton = int(dt['LuongTon'].iloc[i])
    soluongnhap = int(dt['SoLuongNhap'].iloc[i])
    nhan = label

    print(f"{masp}, {tensp}, {luongton}, {soluongnhap}, {thoigian}: {label}")
    try:
        cursor.execute(sql_merge, (masp, tensp, thoigian, luongton, soluongnhap, nhan))
        conn.commit()
    except Exception as e:
        print(f"Lỗi: {str(e)}")

# Đóng kết nối
conn.close()

# Ghi lại thời điểm kết thúc
end_time = time.time()

# Tính thời gian chạy tổng cộng
elapsed_time = end_time - start_time

print(f"Thời gian chạy mô hình: {elapsed_time} giây")

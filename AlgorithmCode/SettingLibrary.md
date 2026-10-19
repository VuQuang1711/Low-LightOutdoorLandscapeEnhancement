# Hướng Dẫn Cài Đặt & Thiết Lập Thư Viện (SettingLibrary)

Tài liệu này hướng dẫn chi tiết cách thiết lập môi trường Python và cài đặt toàn bộ các thư viện cần thiết để thực thi các thuật toán trong thư mục **`AlgorithmCode`** (Đồ án Xử Lý Ảnh Số: *Nâng cao chất lượng ảnh phong cảnh ngoại cảnh thiếu sáng*).

---

## 1. Danh Sách Thư Viện Cốt Lõi

| Tên Thư Viện | Phiên Bản Đề Xuất | Vai Trò & Chức Năng Trong Thuật Toán |
| :--- | :--- | :--- |
| **`opencv-python`** | `>= 4.8.0` | Đọc/ghi ảnh, chuyển đổi không gian màu BGR $\leftrightarrow$ HSV, cân bằng lược đồ mức xám (HE / CLAHE), lọc song phương bảo tồn biên (`Bilateral Filter`). |
| **`numpy`** | `>= 1.24.0` | Tính toán đại số tuyến tính ma trận ảnh, bảng tra cứu tăng tốc O(1) (`Lookup Table - LUT`), cắt ngưỡng phân vị cho Multi-Scale Retinex. |
| **`scikit-image`** | `>= 0.20.0` | Đánh giá định lượng học thuật chỉ số bảo toàn cấu trúc thị giác **SSIM** (`structural_similarity`). |
| **`scipy`** | `>= 1.10.0` | Khoa học tính toán, xử lý tín hiệu và các hàm toán học hỗ trợ. |
| **`matplotlib`** | `>= 3.7.0` | Xuất biểu đồ so sánh và ghép ma trận 6 khung ảnh đối chiếu trực quan 4 thuật toán (`so_sanh_4_thuat_toan.png`). |

---

## 2. Các Cách Cài Đặt (Chọn 1 Trong 3 Cách)

### Cách 1: Tự động 1-Click trên Windows (Nhanh nhất)
1. Mở thư mục `Project/AlgorithmCode/` trong File Explorer.
2. Nhấp đúp chuột (Double-click) vào tệp:
   ```text
   install_requirements.bat
   ```
3. Cửa sổ dòng lệnh sẽ tự động kiểm tra Python, nâng cấp pip và cài đặt trọn gói tất cả thư viện cần thiết.

---

### Cách 2: Chạy Script Python Kiểm Tra Trạng Thái
Mở Terminal tại thư mục `Project` và thực hiện:
```powershell
py AlgorithmCode/install_requirements.py
```
*Script sẽ quét kiểm tra từng thư viện, hiển thị phiên bản hiện có (hoặc đánh dấu `[✗]` nếu chưa cài) và tự động tải cài đặt phần còn thiếu.*

---

### Cách 3: Cài Đặt Thủ Công Bằng Lệnh `pip`
Mở Terminal tại thư mục `Project` hoặc `AlgorithmCode`:
```powershell
# Nâng cấp pip lên bản mới nhất
py -m pip install --upgrade pip

# Cài đặt qua file cấu hình requirements.txt
py -m pip install -r AlgorithmCode/requirements.txt
```

---

## 3. Thiết Lập Môi Trường Ảo (Tùy Chọn - Khuyên Dùng)

Nếu bạn muốn cô lập môi trường của đồ án để tránh xung đột với các môn học khác:

```powershell
# 1. Khởi tạo môi trường ảo tên .venv tại thư mục Project
py -m venv .venv

# 2. Kích hoạt môi trường ảo (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# (Nếu dùng Command Prompt - cmd)
.\.venv\Scripts\activate.bat

# 3. Cài đặt thư viện vào môi trường ảo
pip install -r AlgorithmCode/requirements.txt
```

---

## 4. Kiểm Tra Sau Khi Cài Đặt

Sau khi cài đặt xong, bạn có thể kiểm tra hoạt động ngay bằng cách chạy file tổng hợp so sánh cả 4 thuật toán trên tập 50 ảnh mẫu:

```powershell
py AlgorithmCode/all_algorithms.py
```

Nếu màn hình in ra bảng số liệu định lượng **PSNR, SSIM, NIQE** và thông báo đã xuất ảnh vào `AlgorithmCode/output_demo/so_sanh_4_thuat_toan.png` thì môi trường của bạn đã sẵn sàng 100%.

---

## 5. Xử Lý Các Sự Cố Thường Gặp (Troubleshooting)

1. **Lỗi `'py'` hoặc `'python'` không được nhận diện:**
   - Nguyên nhân: Python chưa được thêm vào biến môi trường hệ thống (`PATH`).
   - Khắc phục: Cài lại Python từ [python.org](https://www.python.org/) và nhớ tích chọn vào ô **"Add python.exe to PATH"**.

2. **Lỗi `PermissionError` (Không đủ quyền ghi):**
   - Thêm cờ `--user` vào cuối lệnh cài đặt:
     ```powershell
     py -m pip install -r AlgorithmCode/requirements.txt --user
     ```

3. **Lỗi mạng tải chậm hoặc Timeout khi tải gói:**
   - Sử dụng mirror máy chủ gần hơn:
     ```powershell
     py -m pip install -r AlgorithmCode/requirements.txt -i https://pypi.org/simple
     ```

# ĐỒ ÁN : NÂNG CAO CHẤT LƯỢNG ẢNH NGOẠI CẢNH THIẾU SÁNG
## A Comparative Study of Traditional Image Enhancement Techniques in Low-Light Outdoor Landscapes

> **Đề tài:** Nghiên cứu và so sánh hiệu năng các kỹ thuật xử lý ảnh truyền thống (**Histogram Equalization**, **CLAHE**, **Gamma Correction**, **Multi-Scale Retinex**) trong bài toán phục hồi và tăng cường chất lượng ảnh phong cảnh ngoại cảnh chụp trong điều kiện ánh sáng yếu.

---

## ⚡ HƯỚNG DẪN THỰC HIỆN

### 1. Yêu cầu môi trường
- Máy tính đã cài đặt **Python 3.9+** (khuyên dùng Python 3.10, 3.11 hoặc 3.12).
- **Lưu ý:** Khi cài đặt Python, nhớ tích chọn ô **`Add python.exe to PATH`**.

### 2. Cài đặt thư viện phụ thuộc
Nhấp đúp chuột vào tệp:
👉 **`install_requirements.bat`** *(Hệ thống tự động phát hiện Python và cài đặt đầy đủ thư viện)*

*Hoặc cài đặt qua dòng lệnh Terminal / Command Prompt:*
```bash
pip install -r requirements.txt
```

---

## 🚀 3 CÁCH KHỞI CHẠY CHƯƠNG TRÌNH

### CÁCH 1: Giao diện Web Dashboard Tương Tác (Khuyên dùng - Trực quan nhất)
Nhấp đúp chuột vào tệp:
👉 **`run_web.bat`**

*Hoặc gõ lệnh:*
```bash
py run_web.py
# (hoặc: python run_web.py)
```
- Trình duyệt sẽ tự động mở tại địa chỉ: **`http://127.0.0.1:8501`**
- **Tính năng trên Web:**
  - So sánh trực quan đồng thời 4 thuật toán (**HE**, **CLAHE**, **Gamma**, **MSR**).
  - Thanh trượt **Split View** kéo so sánh ảnh trước/sau xử lý theo thời gian thực.
  - Bản đồ nhiệt sai khác (**Difference Heatmap**) trực quan hóa vùng được kéo sáng.
  - Biểu đồ phân bố tần suất mức xám **Histogram** và biểu đồ mạng nhện **Radar IQA**.
  - Bảng chỉ số định lượng học thuật: **PSNR**, **SSIM**, **NIQE**, độ lệch Delta và thời gian xử lý (ms).
  - Cho phép **tải ảnh bất kỳ từ máy tính lên** để xử lý theo chuẩn No-Reference (NIQE).
  - Chạy thử nghiệm Benchmark hàng loạt tự động trên nhiều mẫu ảnh.

---

### CÁCH 2: Chạy các thuật toán độc lập (Standalone Console Scripts)
Toàn bộ mã nguồn 4 thuật toán độc lập được đặt trong thư mục **`AlgorithmCode/`**:
- **Chạy so sánh cả 4 thuật toán cùng lúc:**
  Nhấp đúp vào:
  👉 **`AlgorithmCode/run_all.bat`** *(hoặc gõ `py AlgorithmCode/all_algorithms.py`)*
  - Xuất bảng chỉ số PSNR / SSIM / NIQE ra màn hình terminal.
  - Tự động lưu ảnh ghép so sánh 6 ô trực quan vào thư mục `AlgorithmCode/output_demo/so_sanh_4_thuat_toan.png`.

- **Chạy từng thuật toán riêng biệt:**
  ```bash
  cd AlgorithmCode
  py 01_histogram_equalization.py   # Cân bằng biểu đồ mức xám toàn cục & Adaptive HE
  py 02_clahe.py                    # CLAHE khảo sát 3 ngưỡng Clip Limit (1.5, 3.0, 5.0)
  py 03_gamma_correction.py         # Gamma Correction khảo sát 6 hệ số gamma
  py 04_multi_scale_retinex.py      # Multi-Scale Retinex 3 quy mô Gauss (15, 80, 250)
  ```
  *(Toàn bộ ảnh kết quả từng thuật toán được tự động lưu trong `AlgorithmCode/output_demo/`)*.

---

### CÁCH 3: Đánh giá Benchmark Hàng Loạt (Batch Evaluation)
Để đánh giá thống kê trung bình trên toàn bộ 50 ảnh mẫu trong tập dữ liệu:
```bash
py batch_eval.py
```
- Kết quả trung bình và chi tiết từng ảnh sẽ được tự động xuất ra tệp CSV: **`outputs/benchmark_results.csv`**.

---

## 📂 CẤU TRÚC THƯ MỤC DỰ ÁN

```text
Project/
├── AlgorithmCode/                  # Bộ mã nguồn độc lập 4 thuật toán
│   ├── 01_histogram_equalization.py
│   ├── 02_clahe.py
│   ├── 03_gamma_correction.py
│   ├── 04_multi_scale_retinex.py
│   ├── all_algorithms.py
│   ├── data/                      # 50 ảnh phong cảnh mẫu chuẩn
│   ├── output_demo/               # Thư mục chứa ảnh kết quả xuất ra
│   ├── path_utils.py              # Xử lý đường dẫn tiếng Việt & tự tìm dữ liệu
│   ├── install_requirements.bat
│   ├── run_all.bat
│   └── README.md
├── dataset/                       # 50 ảnh phong cảnh phục vụ Web & Benchmark
├── outputs/                       # Thư mục lưu kết quả CSV & báo cáo
├── src/                           # Tầng kiến trúc lõi 3 lớp (Core Architecture)
│   ├── config.py                  # Quản lý đường dẫn và cấu hình hệ thống
│   ├── data_loader.py             # Đọc ảnh an toàn Unicode, mô phỏng thiếu sáng & nhiễu
│   ├── enhancement_modules.py     # Triển khai 4 thuật toán trên kênh độ sáng (HSV/LAB)
│   ├── metrics.py                 # Bộ đo lường chất lượng IQA (PSNR, SSIM, NIQE)
│   ├── model_logic.py             # Điều phối Pipeline so sánh & xếp hạng
│   ├── resource_manager.py        # Giải phóng bộ nhớ RAM
│   └── web_server.py              # FastAPI Web Server phục vụ REST API & UI
├── web/                           # Giao diện Web Dashboard (HTML5 / CSS3 / JavaScript)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── test/                          # Bộ kiểm thử tự động (Unit Tests)
├── config/config.yaml             # Cấu hình tham số mặc định
├── batch_eval.py                  # Script đánh giá hàng loạt
├── requirements.txt               # Danh sách thư viện phụ thuộc
├── install_requirements.bat       # Script 1-click cài đặt thư viện
├── run_web.bat                    # Script 1-click khởi chạy Web
├── run_web.py                     # Entrypoint khởi chạy Web Server
├── README.md                      # Tài liệu tổng quan dự án
└── HUONG_DAN_CHAY.md              # Hướng dẫn chi tiết cho người nhận bài nộp
```

---

## 🛠️ KHẮC PHỤC SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

1. **Lỗi `'python'` hoặc `'py'` không được nhận diện:**
   - Nguyên nhân: Chưa tích chọn `Add Python to PATH` khi cài đặt Python.
   - Khắc phục: Cài đặt lại Python từ [python.org](https://www.python.org/) và nhớ đánh dấu vào ô **Add Python to PATH**.

2. **Cổng 8501 bị chiếm dụng:**
   - Chạy với cổng khác bằng lệnh:
     ```bash
     py run_web.py --port 8080
     ```

3. **Chạy trên macOS / Linux:**
   - Mở Terminal tại thư mục dự án và chạy:
     ```bash
     pip3 install -r requirements.txt
     python3 run_web.py
     ```

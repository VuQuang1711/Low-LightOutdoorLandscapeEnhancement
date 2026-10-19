# Thư Mục Mã Nguồn Thuật Toán (AlgorithmCode)

Thư mục này chứa toàn bộ mã nguồn của **4 thuật toán xử lý ảnh truyền thống** nhằm giải quyết bài toán nâng cao chất lượng ảnh phong cảnh ngoại cảnh thiếu sáng. Toàn bộ code được viết hoàn toàn độc lập, có chú thích chi tiết công thức toán học, quy trình từng bước và hàm `main()` để có thể chạy thử nghiệm trực tiếp ngay lập tức.

---

## 1. Cấu Trúc Các Tệp Mã Nguồn

| Tệp Mã Nguồn | Thuật Toán Triển Khai | Thành Viên Phụ Trách / Mục Đích |
| :--- | :--- | :--- |
| **[`all_algorithms.py`](file:///e:/15DHKHDL03/2026-2027/HKI_26_27/ImageProcessing/Project/AlgorithmCode/all_algorithms.py)** | **Tổng hợp cả 4 thuật toán** | So sánh đồng thời 4 phương pháp trên cùng một ảnh, in bảng so sánh và xuất ảnh đối chiếu 6 ô trực quan (`so_sanh_4_thuat_toan.png`). |
| **[`01_histogram_equalization.py`](file:///e:/15DHKHDL03/2026-2027/HKI_26_27/ImageProcessing/Project/AlgorithmCode/01_histogram_equalization.py)** | **Histogram Equalization (HE & AHE)** | Cân bằng biểu đồ mức xám toàn cục và thích nghi cục bộ (AHE). Phục vụ báo cáo Word và nộp code cá nhân. |
| **[`02_clahe.py`](file:///e:/15DHKHDL03/2026-2027/HKI_26_27/ImageProcessing/Project/AlgorithmCode/02_clahe.py)** | **CLAHE (Contrast Limited Adaptive HE)** | Cân bằng tương phản thích nghi giới hạn độ dốc CDF qua Clip Limit $\beta$ và nội suy song tuyến (Bilinear Interpolation). Phục vụ làm Slide và báo cáo. |
| **[`03_gamma_correction.py`](file:///e:/15DHKHDL03/2026-2027/HKI_26_27/ImageProcessing/Project/AlgorithmCode/03_gamma_correction.py)** | **Gamma Correction** | Hiệu chỉnh lũy thừa phi tuyến với **vòng lặp thử nghiệm nhiều giá trị gamma** ($\gamma \in [0.25, 0.40, 0.50, 0.65, 0.85, 1.20]$) và tối ưu hóa bằng Lookup Table (LUT). |
| **[`04_multi_scale_retinex.py`](file:///e:/15DHKHDL03/2026-2027/HKI_26_27/ImageProcessing/Project/AlgorithmCode/04_multi_scale_retinex.py)** | **Multi-Scale Retinex (MSR / MSRCR)** | Phân rã phản xạ và độ rọi đa quy mô Gauss ($\sigma = 15, 80, 250$), co giãn dải động theo phân vị, phục vụ thuyết trình và bảng so sánh. |

---

## 2. Quy Chuẩn Kỹ Thuật Đạt Chuẩn Đề Tài

1. **Chống Lệch/Bệt Màu:** Không áp dụng thuật toán trực tiếp lên 3 kênh màu RGB. Tất cả các file đều chuyển sang không gian màu **HSV**, chỉ xử lý trên kênh độ sáng **V (Value)**, bảo tồn nguyên vẹn 100% màu sắc tự nhiên của cảnh quan (kênh H và S).
2. **Khử Nhiễu Tiền Xử Lý (Pre-denoising):** Bổ sung **Bilateral Filter** để bảo tồn đường biên sắc nét của cây cối, đồi núi trước khi kéo sáng, ngăn chặn hiện tượng khuếch đại nhiễu hạt.
3. **Bộ 3 Chỉ Số Đo Lường Học Thuật:**
   - **PSNR (Peak Signal-to-Noise Ratio):** Đơn vị dB, đo tỷ số tín hiệu cực đại trên sai số bình phương trung bình MSE.
   - **SSIM (Structural Similarity Index):** Đo lường độ tương đồng cấu trúc thị giác mắt người ($[0, 1]$).
   - **NIQE (Naturalness Image Quality Evaluator):** Chỉ số tự nhiên không cần ảnh gốc (Blind No-reference) - **Càng nhỏ càng tự nhiên**.

---

## 3. Thư Mục Dữ Liệu Kiểm Thử & Cơ Chế Tự Dò Tìm Thông Minh

Thư mục `AlgorithmCode/data/` chứa sẵn **50 ảnh mẫu đầu tiên** (`00000.jpg` đến `00049.jpg`) được chuẩn hóa từ dataset gốc.
- **Tự động dò tìm thư mục thông minh:** Hệ thống tích hợp `path_utils.py`, tự động quét tìm thư mục dữ liệu ở cả môi trường chạy độc lập (`AlgorithmCode/data`), môi trường dự án lớn (`Project/dataset`), hoặc thư mục làm việc hiện tại mà không bao giờ bị lỗi sai đường dẫn.
- **Hỗ trợ Unicode 100%:** Khắc phục triệt để lỗi của OpenCV trên Windows khi đường dẫn chứa tiếng Việt có dấu, dấu cách hoặc ký tự đặc biệt (sử dụng luồng byte nhị phân qua `imdecode`/`imencode`).
- **Xử lý Input File an toàn & linh hoạt:** 
  - Có thể truyền đường dẫn file ảnh cụ thể bên ngoài: `py all_algorithms.py "C:\Anh_Test\hinh1.jpg"`.
  - Có thể truyền số thứ tự ảnh trong dataset: `py all_algorithms.py 15`.
  - Tự động nhận diện nếu ảnh đầu vào đã là ảnh thiếu sáng thực tế để tránh làm tối thêm hai lần.
  - Tự động sinh ảnh phong cảnh nhân tạo dự phòng nếu thư mục data bị xóa, đảm bảo **không bao giờ bị crash**.

---

## 4. Cài Đặt Thư Viện Cần Thiết

*(Xem hướng dẫn chi tiết đầy đủ tại file: [`SettingLibrary.md`](file:///e:/15DHKHDL03/2026-2027/HKI_26_27/ImageProcessing/Project/AlgorithmCode/SettingLibrary.md))*

Bạn có thể cài đặt tự động bằng một trong các cách sau:
- **Cách 1 (Nhanh nhất trên Windows):** Nhấp đúp chuột vào file [`install_requirements.bat`](file:///e:/15DHKHDL03/2026-2027/HKI_26_27/ImageProcessing/Project/AlgorithmCode/install_requirements.bat).
- **Cách 2 (Chạy script Python kiểm tra chi tiết):**
  ```powershell
  py AlgorithmCode/install_requirements.py
  ```
- **Cách 3 (Cài đặt qua pip tiêu chuẩn):**
  ```powershell
  py -m pip install -r AlgorithmCode/requirements.txt
  ```

---

## 5. Cách Chạy Thử Nghiệm

### Cách 1: Chạy bằng 1-Click (Không cần gõ lệnh)
Nhấp đúp chuột vào tệp:
```text
run_all.bat
```
Tệp sẽ tự động nhận diện Python (`py`, `python`, `python3`) và thực thi ngay lập tức thuật toán tổng hợp so sánh cả 4 phương pháp.

### Cách 2: Chạy bằng dòng lệnh Terminal / PowerShell
Mở Terminal tại thư mục `Project` hoặc `AlgorithmCode`:

```powershell
# Chạy file tổng hợp so sánh cả 4 thuật toán:
py AlgorithmCode/all_algorithms.py

# Chạy file riêng biệt cho từng thuật toán:
py AlgorithmCode/01_histogram_equalization.py
py AlgorithmCode/02_clahe.py
py AlgorithmCode/03_gamma_correction.py
py AlgorithmCode/04_multi_scale_retinex.py

# Tùy chọn: Chọn ảnh cụ thể trong dataset (theo tên hoặc index):
py AlgorithmCode/all_algorithms.py 00015.jpg
py AlgorithmCode/02_clahe.py 10

# Tùy chọn: Truyền trực tiếp ảnh bên ngoài bất kỳ (kể cả đường dẫn tiếng Việt):
py AlgorithmCode/all_algorithms.py "D:\HinhAnh\anh_thieu_sang.jpg"
```

*Tất cả kết quả ảnh sau khi chạy sẽ được tự động lưu vào thư mục `AlgorithmCode/output_demo/` (bao gồm biểu đồ ghép 6 ô `so_sanh_4_thuat_toan.png`).*

---

## 6. Hướng Dẫn Đóng Gói (Nén File & Gửi Bài)

Để đảm bảo khi thầy cô hoặc người khác giải nén ra bất kỳ đâu trên máy tính đều chạy được 100%:

### Cách Nén:
1. **Nếu nén thư mục độc lập `AlgorithmCode`:**
   - Chọn thư mục `AlgorithmCode/` -> Click chuột phải -> Chọn **Compress to ZIP file** (hoặc WinRAR -> Add to `AlgorithmCode.zip`).
   - Đảm bảo trong file ZIP chứa đầy đủ:
     - 5 tệp mã nguồn Python (`all_algorithms.py`, `01_...`, `02_...`, `03_...`, `04_...`)
     - Tệp tiện ích `path_utils.py`
     - Thư mục dữ liệu `data/` (chứa các file `.jpg`)
     - Hai tệp thực thi Windows: `install_requirements.bat`, `run_all.bat`
     - Tệp thư viện: `requirements.txt`
2. **Khi người nhận giải nén ra:**
   - Bước 1: Nhấp đúp vào `install_requirements.bat` (chỉ cần chạy 1 lần để cài thư viện).
   - Bước 2: Nhấp đúp vào `run_all.bat` để chạy ngay chương trình.
   - Code sẽ tự động nhận diện thư mục, không bị phụ thuộc vào ổ đĩa hay tên thư mục chứa dấu tiếng Việt.


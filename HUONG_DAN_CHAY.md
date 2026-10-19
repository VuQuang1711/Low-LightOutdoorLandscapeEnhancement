# HƯỚNG DẪN CHI TIẾT DÀNH CHO NGƯỜI CHẤM / NGƯỜI NHẬN BÀI NỘP
## Đồ án Xử Lý Ảnh Số: So Sánh 4 Thuật Toán Nâng Cao Chất Lượng Ảnh Thiếu Sáng

Tài liệu này hướng dẫn từng bước chi tiết giúp Thầy/Cô hoặc Người nhận bài có thể giải nén và khởi chạy toàn bộ đồ án một cách nhanh chóng và dễ dàng nhất trên bất kỳ máy tính nào.

---

### BƯỚC 1: GIẢI NÉN TỆP TIN DỰ ÁN
1. Nhấp chuột phải vào tệp nén **`Project.zip`** (hoặc `AlgorithmCode.zip`).
2. Chọn **Extract All...** (hoặc dùng WinRAR/7-Zip chọn **Extract here** / **Extract to folder**).
3. Mở thư mục dự án vừa được giải nén ra.

---

### BƯỚC 2: CÀI ĐẶT THƯ VIỆN PHỤ THUỘC (CHỈ CẦN LÀM LẦN ĐẦU)

Hệ thống đã chuẩn bị sẵn kịch bản tự động nhận diện môi trường Python trên máy:

- **Cách 1 (Khuyên dùng - 1 Click chuột):**
  Nhấp đúp chuột trái vào tệp:
  👉 **`install_requirements.bat`**
  - Màn hình đen (CMD) sẽ hiện lên màu xanh, tự động nhận diện `py`, `python` hoặc `python3` và cài đặt toàn bộ các thư viện cần thiết (`opencv-python`, `numpy`, `scipy`, `scikit-image`, `fastapi`, `uvicorn`, `matplotlib`, `pyyaml`).
  - Khi cài đặt hoàn tất, nhấn phím bất kỳ để đóng cửa sổ.

- **Cách 2 (Qua Terminal / Dòng lệnh nếu Thầy/Cô quen dùng Terminal):**
  Mở Terminal (hoặc CMD / PowerShell) tại thư mục dự án và chạy:
  ```bash
  pip install -r requirements.txt
  ```

---

### BƯỚC 3: KHỞI CHẠY DỰ ÁN (3 CHẾ ĐỘ ĐÁNH GIÁ)

Thầy/Cô có thể lựa chọn 1 trong 3 chế độ đánh giá dưới đây tùy theo yêu cầu chấm điểm:

#### CHẾ ĐỘ 1: KHỞI CHẠY GIAO DIỆN WEB DASHBOARD (TRỰC QUAN NHẤT - KHUYÊN DÙNG)
Phục vụ việc đánh giá trực quan, tương tác trực tiếp với các thuật toán:

- **Cách chạy 1-Click:**
  Nhấp đúp chuột vào tệp:
  👉 **`run_web.bat`**
  *(Hoặc mở Terminal gõ lệnh: `py run_web.py`)*

- **Kết quả:**
  1. Trình duyệt web mặc định sẽ tự động mở trang: **`http://127.0.0.1:8501`**.
  2. Toàn bộ 4 thuật toán (**HE**, **CLAHE**, **Gamma Correction**, **Multi-Scale Retinex**) sẽ tự động chạy song song trên ảnh mẫu và hiển thị kết quả.

- **Các tính năng Thầy/Cô có thể kiểm tra trên Web:**
  - **Lựa chọn ảnh mẫu:** Kéo thanh trượt `Chọn Ảnh Mẫu Trong Dataset` (hệ thống có sẵn 50 ảnh phong cảnh ngoại cảnh độ phân giải cao).
  - **So sánh 4 khung hình song song:** Xem ảnh sau xử lý của từng thuật toán kèm các chỉ số PSNR, SSIM, NIQE ngay bên dưới mỗi ảnh.
  - **Thanh trượt Split View (Trước/Sau):** Chọn tab *Thanh Trượt Split (Trước/Sau)* để kéo thanh chia so sánh trực tiếp vùng sáng/tối.
  - **Bản đồ nhiệt sai khác (Difference Heatmaps):** Chuyển sang tab *Bản Đồ Nhiệt* để xem trực quan các vùng chi tiết bóng râm và mây trời được phục hồi.
  - **Bảng điểm xếp hạng & Khuyến nghị học thuật:** Xem thuật toán nào đạt điểm tương đồng cấu trúc (SSIM) cao nhất, độ tự nhiên (NIQE) tốt nhất và phương pháp được đề xuất tổng hợp.
  - **Biểu đồ phân phối Histogram:** So sánh đường cong mức xám trước và sau nâng cao tương phản.
  - **Tải ảnh cá nhân:** Chuyển sang tab *Tải Ảnh Lên* ở thanh bên trái để tải một ảnh phong cảnh chụp đêm bất kỳ từ máy tính cá nhân lên kiểm tra.
  - **Chạy Benchmark Hàng Loạt:** Nhấn nút *Chạy Benchmark Hàng Loạt* ở cuối trang để hệ thống tự động đánh giá trên tập dữ liệu và tính toán điểm trung bình.

---

#### CHẾ ĐỘ 2: CHẠY CÁC THUẬT TOÁN ĐỘC LẬP TRONG `AlgorithmCode/` (MÃ NGUỒN THUẦN TÚY)
Dành cho việc kiểm tra mã nguồn từng thuật toán trong môi trường console:

1. **Chạy so sánh cả 4 thuật toán:**
   - Mở thư mục `AlgorithmCode/`.
   - Nhấp đúp chuột vào tệp 👉 **`run_all.bat`** *(hoặc gõ `py all_algorithms.py`)*.
   - Kết quả: In bảng điểm so sánh trực tiếp trên màn hình Terminal và tự động lưu biểu đồ so sánh 6 ô vào:
     `AlgorithmCode/output_demo/so_sanh_4_thuat_toan.png`.

2. **Chạy kiểm tra từng thuật toán đơn lẻ:**
   Mở CMD tại thư mục `AlgorithmCode/` và chạy:
   - **HE:** `py 01_histogram_equalization.py`
   - **CLAHE:** `py 02_clahe.py`
   - **Gamma Correction:** `py 03_gamma_correction.py`
   - **Multi-Scale Retinex:** `py 04_multi_scale_retinex.py`

*(Tất cả ảnh xuất ra được lưu tại `AlgorithmCode/output_demo/`)*.

---

#### CHẾ ĐỘ 3: CHẠY BÁO CÁO BENCHMARK HÀNG LOẠT (BATCH EVALUATION)
Dành cho việc kiểm tra thống kê số liệu định lượng:

1. Mở Terminal tại thư mục gốc của dự án.
2. Chạy lệnh:
   ```bash
   py batch_eval.py
   ```
3. Chương trình sẽ duyệt qua toàn bộ 50 ảnh phong cảnh trong thư mục `dataset/`, đo lường chỉ số trung bình (Mean PSNR, Mean SSIM, Mean NIQE) và lưu bảng kết quả chi tiết vào tệp tin:
   👉 **`outputs/benchmark_results.csv`** *(có thể mở trực tiếp bằng Microsoft Excel)*.

---

### BẢNG TỔNG HỢP CÁC LỆNH VÀ TỆP TIN CHÍNH

| Mục đích | Cách chạy nhanh nhất (1-Click) | Lệnh dòng lệnh tương đương |
| :--- | :--- | :--- |
| **Cài đặt thư viện** | Nhấp đúp `install_requirements.bat` | `pip install -r requirements.txt` |
| **Chạy Web Dashboard** | Nhấp đúp `run_web.bat` | `py run_web.py` |
| **Chạy 4 thuật toán Console** | Nhấp đúp `AlgorithmCode/run_all.bat` | `py AlgorithmCode/all_algorithms.py` |
| **Chạy Benchmark CSV** | Mở Terminal | `py batch_eval.py` |

---

### MỘT SỐ LƯU Ý KHI SỬ DỤNG
- Mã nguồn đã được tích hợp bộ công cụ tự động xử lý đường dẫn an toàn (`path_utils.py`), đảm bảo chạy bình thường kể cả khi thư mục giải nén nằm trong đường dẫn tiếng Việt có dấu.
- Nếu trên máy tính lệnh `py` không hoạt động, Thầy/Cô có thể thay bằng lệnh `python` hoặc `python3`.
- Để dừng máy chủ Web sau khi xem xong, chỉ cần nhấn tổ hợp phím **Ctrl + C** trong cửa sổ Terminal.

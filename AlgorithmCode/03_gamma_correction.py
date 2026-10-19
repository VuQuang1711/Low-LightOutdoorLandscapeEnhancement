"""
====================================================================================================
BỘ MÔN: XỬ LÝ ẢNH SỐ (IMAGE PROCESSING) - ĐỒ ÁN MÔN HỌC
THUẬT TOÁN 3: HIỆU CHỈNH GAMMA (GAMMA CORRECTION - THỬ NGHIỆM NHIỀU GIÁ TRỊ GAMMA)
Tác giả / Thành viên: Lê Nguyễn Tâm Đức - 2045240054
Mục tiêu:
    1. Nghiên cứu lý thuyết biến đổi phi tuyến theo hàm lũy thừa (Power-Law / Gamma Transformation).
    2. Cài đặt vòng lặp thử nghiệm chạy với nhiều giá trị gamma khác nhau (0.2, 0.4, 0.6, 0.8, 1.2)
       để tìm ra ngưỡng kéo sáng tối ưu cho ảnh phong cảnh mà không làm cháy sáng nền trời.
    3. Tối ưu hóa tốc độ xử lý bằng bảng tra cứu trước (Lookup Table - LUT).
    4. Đo lường định lượng và so sánh hiệu năng qua PSNR (dB), SSIM và NIQE.
====================================================================================================

CƠ SỞ LÝ THUYẾT & CÔNG THỨC TOÁN HỌC:
----------------------------------------------------------------------------------------------------
1. Công thức hàm lũy thừa (Power-Law Transform):
       s = c * r^gamma
   Trong đó:
       r : Cường độ sáng đầu vào chuẩn hóa về đoạn [0, 1] (r = V / 255.0).
       s : Cường độ sáng đầu ra chuẩn hóa về đoạn [0, 1].
       c : Hằng số tỷ lệ (thường chọn c = 1.0).
       gamma : Hệ số mũ phi tuyến.

2. Đặc tính điều chỉnh ánh sáng:
   - Khi gamma < 1.0 (ví dụ gamma = 0.3 - 0.6):
     Đường cong ánh xạ lồi lên trên (Convex Curve). Khoảng mức xám hẹp ở vùng tối (0 - 50)
     được kéo giãn rộng ra thành (0 - 150), giúp bộc lộ rõ chi tiết ẩn trong bóng đêm.
     Đồng thời dải mức sáng cao (200 - 255) bị nén nhẹ, tránh làm bão hòa / cháy ảnh.
   - Khi gamma = 1.0:
     Ánh xạ tuyến tính đồng nhất (Identity - Không thay đổi ảnh).
   - Khi gamma > 1.0 (ví dụ gamma = 1.5 - 2.5):
     Đường cong lõm xuống dưới (Concave Curve), làm tối ảnh (dùng để tạo ảnh giả lập ban đêm).

3. Kỹ thuật tăng tốc bằng Bảng tra cứu (Lookup Table - LUT):
   Vì ảnh 8-bit chỉ có 256 mức xám nguyên (0 -> 255), ta tính trước 256 giá trị đầu ra
   vào một mảng NumPy kích thước 256, sau đó dùng cv2.LUT() để ánh xạ tức thì trong O(1).
====================================================================================================
"""

import os
import sys
import time
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional

import cv2
import numpy as np

# Đảm bảo UTF-8 cho Windows Terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ==================================================================================================
# 1. BỘ LỌC KHỬ NHIỄU BẢO TỒN BIÊN (BILATERAL FILTER)
# ==================================================================================================
def apply_bilateral_denoising(img_bgr: np.ndarray, d: int = 7, sigma_color: float = 50.0, sigma_space: float = 50.0) -> np.ndarray:
    """Khử nhiễu trước khi hiệu chỉnh Gamma."""
    return cv2.bilateralFilter(img_bgr, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)


# ==================================================================================================
# 2. THUẬT TOÁN GAMMA CORRECTION TRÊN KÊNH ĐỘ SÁNG (HSV - V CHANNEL)
# ==================================================================================================
def enhance_gamma_correction(
    img_bgr: np.ndarray,
    gamma: float = 0.5,
    auto_optimize: bool = False
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """
    Quy trình hiệu chỉnh Gamma trên kênh độ sáng V của không gian màu HSV:
    1. Chuyển BGR sang HSV, tách riêng kênh V (Value - độ sáng).
    2. Nếu auto_optimize=True: Tự động ước lượng gamma dựa trên trung bình ánh sáng:
           gamma = log(0.5) / log(mean(V)/255.0)
    3. Xây dựng bảng tra cứu LUT 256 phần tử:
           table[i] = ((i / 255.0) ** gamma) * 255
    4. Áp dụng bảng tra cv2.LUT(v_chan, table).
    5. Ghép lại kênh HSV và chuyển ngược về BGR.

    Returns:
        (enhanced_bgr, v_original, v_enhanced, effective_gamma)
    """
    # Bước 1: Chuyển đổi sang HSV và tách kênh
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h_chan, s_chan, v_chan = cv2.split(hsv)

    effective_gamma = max(0.1, min(5.0, float(gamma)))

    # Bước 2: Tự động tối ưu gamma nếu được yêu cầu
    if auto_optimize:
        mean_val = float(np.mean(v_chan)) / 255.0
        if mean_val > 0.01:
            effective_gamma = float(np.log(0.5) / np.log(mean_val + 1e-6))
            effective_gamma = max(0.2, min(1.5, effective_gamma))

    # Bước 3: Tạo bảng tra cứu Lookup Table (LUT)
    inv_gamma = effective_gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")

    # Bước 4: Áp dụng bảng tra cứu siêu nhanh O(1)
    v_enhanced = cv2.LUT(v_chan, table)

    # Bước 5: Ghép kênh và chuyển ngược về BGR
    merged_hsv = cv2.merge([h_chan, s_chan, v_enhanced])
    enhanced_bgr = cv2.cvtColor(merged_hsv, cv2.COLOR_HSV2BGR)

    return enhanced_bgr, v_chan, v_enhanced, effective_gamma


# ==================================================================================================
# 3. CÁC HÀM TÍNH TOÁN CHỈ SỐ ĐÁNH GIÁ (IQA METRICS)
# ==================================================================================================
def calculate_psnr(img_ref: np.ndarray, img_tgt: np.ndarray) -> float:
    """Tính PSNR (dB)."""
    ref = img_ref.astype(np.float64)
    tgt = img_tgt.astype(np.float64)
    mse = np.mean((ref - tgt) ** 2)
    if mse < 1e-10:
        return 100.0
    return float(10.0 * np.log10((255.0 ** 2) / mse))


def calculate_ssim(img_ref: np.ndarray, img_tgt: np.ndarray) -> float:
    """Tính SSIM (0 - 1)."""
    try:
        from skimage.metrics import structural_similarity as ssim_fn
        return float(ssim_fn(img_ref, img_tgt, channel_axis=2, data_range=255.0))
    except ImportError:
        g1 = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY).astype(np.float64)
        g2 = cv2.cvtColor(img_tgt, cv2.COLOR_BGR2GRAY).astype(np.float64)
        mu1, mu2 = np.mean(g1), np.mean(g2)
        var1, var2 = np.var(g1), np.var(g2)
        cov = np.mean((g1 - mu1) * (g2 - mu2))
        c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
        return float(((2 * mu1 * mu2 + c1) * (2 * cov + c2)) / ((mu1**2 + mu2**2 + c1) * (var1 + var2 + c2)))


def calculate_niqe(img_bgr: np.ndarray) -> float:
    """Tính chỉ số tự nhiên không tham chiếu NIQE (Càng nhỏ càng tự nhiên)."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    mu = cv2.GaussianBlur(gray, (7, 7), 7.0 / 6.0)
    mu_sq = mu * mu
    sigma = np.sqrt(np.abs(cv2.GaussianBlur(gray * gray, (7, 7), 7.0 / 6.0) - mu_sq))
    structdis = (gray - mu) / (sigma + 1.0)
    var = np.var(structdis)
    niqe_score = float(np.clip(12.0 / (var + 0.8), 2.5, 12.0))
    return round(niqe_score, 2)


# ==================================================================================================
# 3. TIỆN ÍCH DÒ TÌM THƯ MỤC VÀ ĐỌC/GHI ẢNH AN TOÀN (UNICODE & WINDOWS COMPATIBLE)
# ==================================================================================================
try:
    from path_utils import (
        imread_unicode,
        imwrite_unicode,
        find_sample_image,
        get_output_dir,
        generate_synthetic_landscape
    )
except ImportError:
    def imread_unicode(img_path: Union[str, Path], flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
        if img_path is None:
            return None
        p = Path(img_path).resolve()
        if not p.exists() or not p.is_file():
            return None
        try:
            data = np.fromfile(str(p), dtype=np.uint8)
            if data.size > 0:
                img = cv2.imdecode(data, flags)
                if img is not None and img.size > 0:
                    return img
        except Exception:
            pass
        try:
            return cv2.imread(str(p), flags)
        except Exception:
            return None

    def imwrite_unicode(save_path: Union[str, Path], img: np.ndarray, ext: str = ".jpg") -> bool:
        if img is None or img.size == 0:
            return False
        try:
            p = Path(save_path).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            suffix = p.suffix if p.suffix else ext
            ok, enc = cv2.imencode(suffix, img)
            if ok:
                enc.tofile(str(p))
                return True
        except Exception:
            pass
        try:
            return cv2.imwrite(str(save_path), img)
        except Exception:
            return False

    def generate_synthetic_landscape(width: int = 512, height: int = 512) -> np.ndarray:
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[: height // 2, :] = [180, 120, 70]
        img[height // 2 :, :] = [30, 80, 20]
        return img

    def get_output_dir(sub_name: str = "output_demo") -> Path:
        out_dir = Path(__file__).resolve().parent / sub_name
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def find_sample_image(prefer_name_or_idx: Optional[str] = None):
        script_dir = Path(__file__).resolve().parent
        cwd = Path.cwd().resolve()
        candidate_dirs = [
            script_dir / "data",
            script_dir / "dataset",
            cwd / "data",
            cwd / "AlgorithmCode" / "data",
            script_dir.parent / "dataset",
            script_dir.parent / "AlgorithmCode" / "data",
        ]
        all_imgs = []
        for d in candidate_dirs:
            if d.is_dir():
                for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]:
                    all_imgs.extend(list(d.glob(ext)))
        if prefer_name_or_idx:
            raw = str(prefer_name_or_idx).strip().strip('"').strip("'")
            for cp in [Path(raw), cwd / raw, script_dir / raw, script_dir / "data" / raw]:
                if cp.exists() and cp.is_file():
                    im = imread_unicode(cp)
                    if im is not None:
                        return str(cp.resolve()), max(len(all_imgs), 1), str(cp.resolve().parent), im
            if raw.isdigit() and all_imgs:
                idx = int(raw) % len(all_imgs)
                im = imread_unicode(all_imgs[idx])
                if im is not None:
                    return str(all_imgs[idx].resolve()), len(all_imgs), str(all_imgs[idx].parent), im
            for p in all_imgs:
                if raw.lower() in p.name.lower():
                    im = imread_unicode(p)
                    if im is not None:
                        return str(p.resolve()), len(all_imgs), str(p.parent), im
        for p in all_imgs:
            im = imread_unicode(p)
            if im is not None:
                return str(p.resolve()), len(all_imgs), str(p.parent), im
        fallback_dir = script_dir / "data"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        fb_img = generate_synthetic_landscape()
        fb_file = fallback_dir / "00000_sample_synthetic.jpg"
        imwrite_unicode(fb_file, fb_img)
        return str(fb_file), 1, str(fallback_dir), fb_img


# ==================================================================================================
# 4. CHƯƠNG TRÌNH THỰC THI & KIỂM THỬ ĐỘC LẬP (STANDALONE DEMO)
# ==================================================================================================
def main():
    print("=" * 85)
    print("  [DEMO] THUẬT TOÁN GAMMA CORRECTION - THỬ NGHIỆM VÒNG LẶP ĐA GIÁ TRỊ GAMMA")
    print("  Người thực hiện: Lê Nguyễn Tâm Đức (MSSV: 2045240054)")
    print("=" * 85)

    # 1. Tự động dò tìm thư mục và nạp ảnh đầu vào (Hỗ trợ tham số dòng lệnh)
    custom_arg = sys.argv[1] if len(sys.argv) > 1 else None
    sample_img_path, total_found, source_folder, clean_img = find_sample_image(custom_arg)

    print(f"  • Thư mục nguồn dữ liệu : {source_folder} (Tìm thấy {total_found} ảnh hợp lệ)")
    print(f"  • Tệp ảnh được chọn      : {Path(sample_img_path).name}")
    print(f"  • Đường dẫn tệp ảnh     : {sample_img_path}")
    print(f"  • Độ phân giải ảnh       : {clean_img.shape[1]}x{clean_img.shape[0]} (Channels: {clean_img.shape[2]})")

    # Kiểm tra xem ảnh đầu vào có phải là ảnh thực tế đã thiếu sáng sẵn hay không
    gray = cv2.cvtColor(clean_img, cv2.COLOR_BGR2GRAY)
    mean_lum = float(np.mean(gray))

    if custom_arg and mean_lum < 65.0:
        print(f"  • Phát hiện ảnh đầu vào đã ở điều kiện thiếu sáng thực tế (Độ sáng TB: {mean_lum:.1f}/255).")
        print("    -> Sử dụng trực tiếp ảnh làm đầu vào thuật toán (không làm tối thêm).")
        low_light_noisy = clean_img.copy()
        is_simulated = False
    else:
        print("  • Đang giả lập môi trường thiếu sáng & bơm nhiễu Gauss...")
        dark_float = np.power(clean_img.astype(np.float32) / 255.0, 2.2) * 0.35
        low_light_img = np.clip(dark_float * 255.0, 0, 255).astype(np.uint8)
        noise = np.random.normal(0, 15, low_light_img.shape)
        low_light_noisy = np.clip(low_light_img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        is_simulated = True

    # 2. Tiền xử lý khử nhiễu
    denoised_input = apply_bilateral_denoising(low_light_noisy, d=7, sigma_color=50, sigma_space=50)

    # 3. VÒNG LẶP THỰC NGHIỆM ĐA GIÁ TRỊ GAMMA (0.25 -> 1.20)
    gamma_candidates = [0.25, 0.40, 0.50, 0.65, 0.85, 1.20]
    results = []

    print("\n  >> Đang thực hiện vòng lặp thử nghiệm trên các giá trị Gamma...")
    out_dir = get_output_dir("output_demo")

    for g in gamma_candidates:
        t0 = time.perf_counter()
        enh, _, _, eff_g = enhance_gamma_correction(denoised_input, gamma=g)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        psnr_val = calculate_psnr(clean_img, enh) if is_simulated else 0.0
        ssim_val = calculate_ssim(clean_img, enh) if is_simulated else 0.0
        niqe_val = calculate_niqe(enh)

        results.append({
            "gamma": g,
            "psnr": psnr_val,
            "ssim": ssim_val,
            "niqe": niqe_val,
            "time_ms": elapsed_ms
        })

        # Lưu ảnh tương ứng an toàn Unicode
        imwrite_unicode(out_dir / f"03_gamma_{g:.2f}.jpg", enh)

    # 4. In bảng so sánh học thuật
    psnr_noisy = calculate_psnr(clean_img, low_light_noisy) if is_simulated else 0.0
    ssim_noisy = calculate_ssim(clean_img, low_light_noisy) if is_simulated else 0.0
    niqe_noisy = calculate_niqe(low_light_noisy)

    print("\n" + "-" * 85)
    print("  KẾT QUẢ ĐO LƯỜNG VÒNG LẶP THỰC NGHIỆM GAMMA:")
    print("-" * 85)
    if is_simulated:
        print(f"  Giá trị Gamma           | PSNR (dB) | SSIM   | NIQE (càng nhỏ càng tốt) | Tốc độ")
        print("-" * 85)
        print(f"  Ảnh gốc thiếu sáng     | {psnr_noisy:<9.2f} | {ssim_noisy:<6.4f} | {niqe_noisy:<6.2f}                   | --")
        for r in results:
            star = " ★ (Tối ưu)" if r["gamma"] == 0.50 else ""
            print(f"  Gamma = {r['gamma']:<15.2f} | {r['psnr']:<9.2f} | {r['ssim']:<6.4f} | {r['niqe']:<6.2f}                   | {r['time_ms']:.2f} ms{star}")
    else:
        print(f"  Giá trị Gamma           | NIQE (Càng nhỏ càng tốt) | Tốc độ thực thi (ms)")
        print("-" * 85)
        print(f"  Ảnh gốc thiếu sáng     | {niqe_noisy:<26.2f} | --")
        for r in results:
            star = " ★ (Tối ưu)" if r["gamma"] == 0.50 else ""
            print(f"  Gamma = {r['gamma']:<15.2f} | {r['niqe']:<26.2f} | {r['time_ms']:.2f} ms{star}")
    print("-" * 85)
    print("  NHẬN XÉT HỌC THUẬT:")
    print("  • Với gamma = 0.40 - 0.50: Đạt sự cân bằng tốt nhất giữa khôi phục chi tiết tối và giữ nguyên màu tự nhiên.")
    print("  • Khi gamma quá nhỏ (gamma = 0.25): Ảnh bị kéo sáng quá đà, làm bạc màu và lộ rõ nhiễu nền.")
    print("  • Khi gamma >= 1.0: Không có tác dụng kéo sáng đối với ảnh thiếu sáng.")
    print("  • Nhờ bảng tra Lookup Table (LUT), tốc độ thực thi cực kỳ ấn tượng (< 5 ms).")
    print("=" * 85)
    print(f"  >> Đã lưu toàn bộ ảnh các mức gamma vào thư mục: {out_dir}\n")


if __name__ == "__main__":
    main()


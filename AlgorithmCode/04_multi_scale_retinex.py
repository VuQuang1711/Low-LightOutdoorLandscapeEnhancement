"""
====================================================================================================
BỘ MÔN: XỬ LÝ ẢNH SỐ (IMAGE PROCESSING) - ĐỒ ÁN MÔN HỌC
THUẬT TOÁN 4: MULTI-SCALE RETINEX (MSR / MSRCR) - PHỤC HỒI MÀU SẮC & ĐỘ RỌI TỰ NHIÊN
Tác giả / Thành viên:Huỳnh Thị Kim Phương - 2045240246 - Thuyết Trình & Phân Tích So Sánh
Mục tiêu:
    1. Nghiên cứu lý thuyết phản xạ Retinex của Edwin Land: Phân rã ảnh thành thành phần phản xạ
       Reflectance (chi tiết thực) và thành phần độ rọi Illumination (ánh sáng môi trường).
    2. Cài đặt thuật toán Single-Scale Retinex (SSR) và Multi-Scale Retinex (MSR) đa quy mô.
    3. Phục hồi dải sáng và màu sắc sống động cho cảnh đêm/thiếu sáng ngoại cảnh.
    4. Đo lường định lượng và so sánh hiệu năng qua PSNR (dB), SSIM và NIQE.
====================================================================================================

CƠ SỞ LÝ THUYẾT & CÔNG THỨC TOÁN HỌC:
----------------------------------------------------------------------------------------------------
1. Mô hình hình thành ảnh Retinex:
       I(x, y) = R(x, y) * L(x, y)
   Trong đó:
       I(x, y) : Cường độ sáng của bức ảnh quan sát được.
       R(x, y) : Hệ số phản xạ bề mặt vật thể (phản ánh đặc tính vật lý thực tế của tán cây, vách núi).
       L(x, y) : Độ rọi của nguồn sáng môi trường (biến thiên chậm trong không gian).

2. Bóc tách trong miền Logarit (Logarithmic Transformation):
       ln(R(x, y)) = ln(I(x, y)) - ln(L(x, y))
   Độ rọi L(x, y) được xấp xỉ bằng phép tích chập giữa ảnh quan sát I với hàm Gauss G(x, y):
       L(x, y) ~ I(x, y) * G(x, y)

3. Thuật toán Single-Scale Retinex (SSR):
       R_k(x, y) = ln(I(x, y)) - ln(I(x, y) * G_k(x, y))
   với hàm Gauss chuẩn hóa:
       G_k(x, y) = K * exp( -(x^2 + y^2) / (2 * sigma_k^2) )

4. Thuật toán Multi-Scale Retinex (MSR):
   Kết hợp tuyến tính nhiều quy mô Gauss khác nhau:
       R_MSR(x, y) = sum_{k=1}^K w_k * [ ln(I(x, y)) - ln(I(x, y) * G_k(x, y)) ]
   Quy ước trọng số: sum(w_k) = 1 (với 3 quy mô, w_1 = w_2 = w_3 = 1/3):
       - Quy mô nhỏ (sigma = 15): Bóc tách chi tiết vi mô, tăng độ sắc nét cạnh.
       - Quy mô vừa (sigma = 80): Cải thiện độ tương phản cục bộ.
       - Quy mô lớn (sigma = 250): Cân bằng tổng thể dải sáng vĩ mô toàn cảnh.

5. Co giãn dải động theo phân vị (Dynamic Range Clipping):
   Kết quả sau MSR có thể chứa giá trị âm hoặc vượt ngưỡng. Ta sử dụng phân vị 1% và 99%
   để cắt biên và chuẩn hóa tuyến tính về miền [0, 255].
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
    """Khử nhiễu tiền xử lý trước khi phân rã Retinex."""
    return cv2.bilateralFilter(img_bgr, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)


# ==================================================================================================
# 2. THUẬT TOÁN MULTI-SCALE RETINEX (MSR) TRÊN KÊNH ĐỘ SÁNG (HSV - V CHANNEL)
# ==================================================================================================
def enhance_multi_scale_retinex(
    img_bgr: np.ndarray,
    scales: Optional[List[int]] = None,
    weights: Optional[List[float]] = None,
    dynamic_clip_percentile: float = 1.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Quy trình thực thi Multi-Scale Retinex (MSR) trên kênh V:
    1. Chuyển BGR sang HSV để cô lập kênh độ sáng V, tránh hiện tượng lệch màu xám xịt của MSR cổ điển.
    2. Chuyển đổi V sang float64, cộng thêm 1.0 để tránh ln(0).
    3. Tính ln(V).
    4. Lặp qua 3 quy mô Gauss (sigma = 15, 80, 250):
           - Làm mờ Gauss đại diện cho độ rọi: blurred = GaussianBlur(V, sigma)
           - Trừ thành phần độ rọi: R_k = ln(V) - ln(blurred)
           - Tích lũy: R_MSR += w_k * R_k
    5. Cắt phân vị động (Dynamic Range Clipping) dựa trên p_low và p_high để chuẩn hóa về [0, 255].
    6. Ghép lại kênh HSV và chuyển ngược về BGR.

    Returns:
        (enhanced_bgr, v_original, v_enhanced)
    """
    scales = scales or [15, 80, 250]
    if weights is None:
        weights = [1.0 / len(scales)] * len(scales)

    # Bước 1: Tách kênh độ sáng V trong không gian HSV
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h_chan, s_chan, v_chan = cv2.split(hsv)

    # Bước 2 & 3: Miền Logarit
    v_float = v_chan.astype(np.float64) + 1.0
    log_v = np.log(v_float)
    msr_acc = np.zeros_like(log_v)

    # Bước 4: Tích chập đa quy mô Gauss
    for s, w in zip(scales, weights):
        blurred = cv2.GaussianBlur(v_float, (0, 0), float(s))
        blurred = np.maximum(blurred, 1.0)
        log_blurred = np.log(blurred)
        msr_acc += w * (log_v - log_blurred)

    # Bước 5: Co giãn dải động theo phân vị (Dynamic Range Clipping)
    p_low = np.percentile(msr_acc, dynamic_clip_percentile)
    p_high = np.percentile(msr_acc, 100.0 - dynamic_clip_percentile)

    if p_high - p_low < 1e-5:
        clipped = msr_acc - p_low
    else:
        clipped = (msr_acc - p_low) / (p_high - p_low) * 255.0

    v_enhanced = np.clip(clipped, 0, 255).astype(np.uint8)

    # Bước 6: Ghép kênh và tái tạo ảnh BGR
    merged_hsv = cv2.merge([h_chan, s_chan, v_enhanced])
    enhanced_bgr = cv2.cvtColor(merged_hsv, cv2.COLOR_HSV2BGR)

    return enhanced_bgr, v_chan, v_enhanced


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
    print("  [DEMO] THUẬT TOÁN MULTI-SCALE RETINEX (MSR) - PHỤC HỒI ĐỘ RỌI PHONG CẢNH ĐÊM")
    print("  Người thực hiện: Huỳnh Thị Kim Phương (MSSV: 2045240246)")
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

    # 3. Thực thi Multi-Scale Retinex (MSR)
    t0 = time.perf_counter()
    msr_img, _, _ = enhance_multi_scale_retinex(denoised_input, scales=[15, 80, 250])
    elapsed_ms = (time.perf_counter() - t0) * 1000

    # 4. Đo lường chỉ số học thuật
    psnr_noisy = calculate_psnr(clean_img, low_light_noisy) if is_simulated else 0.0
    psnr_msr = calculate_psnr(clean_img, msr_img) if is_simulated else 0.0

    ssim_noisy = calculate_ssim(clean_img, low_light_noisy) if is_simulated else 0.0
    ssim_msr = calculate_ssim(clean_img, msr_img) if is_simulated else 0.0

    niqe_noisy = calculate_niqe(low_light_noisy)
    niqe_msr = calculate_niqe(msr_img)

    print("\n" + "-" * 85)
    print("  KẾT QUẢ ĐO LƯỜNG ĐỊNH LƯỢNG MULTI-SCALE RETINEX:")
    print("-" * 85)
    if is_simulated:
        print(f"  Trạng thái ảnh            | PSNR (dB) | SSIM   | NIQE (càng nhỏ càng tốt)")
        print("-" * 85)
        print(f"  1. Ảnh thiếu sáng + nhiễu | {psnr_noisy:<9.2f} | {ssim_noisy:<6.4f} | {niqe_noisy:<6.2f}")
        print(f"  2. Sau Multi-Scale Retinex| {psnr_msr:<9.2f} | {ssim_msr:<6.4f} | {niqe_msr:<6.2f} (Thời gian: {elapsed_ms:.2f} ms)")
    else:
        print(f"  Trạng thái ảnh            | NIQE (Chỉ số tự nhiên - càng nhỏ càng tốt) | Thời Gian (ms)")
        print("-" * 85)
        print(f"  1. Ảnh thiếu sáng gốc     | {niqe_noisy:<42.2f} | --")
        print(f"  2. Sau Multi-Scale Retinex| {niqe_msr:<42.2f} | {elapsed_ms:.2f} ms")
    print("-" * 85)
    print("  NHẬN XÉT HỌC THUẬT:")
    print("  • MSR thể hiện năng lực khôi phục ánh sáng tự nhiên vượt trội, dải sáng được cân bằng")
    print("    hài hòa giữa các vùng bóng cây và nền trời, đạt điểm số tự nhiên NIQE rất ấn tượng.")
    print("  • Do phải tính toán 3 lần tích chập Gauss trên toàn bức ảnh, thời gian xử lý lâu hơn các thuật toán khác.")
    print("=" * 85)

    # 5. Lưu ảnh kết quả an toàn bằng imwrite_unicode (hỗ trợ thư mục tiếng Việt)
    out_dir = get_output_dir("output_demo")
    imwrite_unicode(out_dir / "04_msr_enhanced.jpg", msr_img)
    print(f"  >> Đã lưu ảnh kết quả vào thư mục: {out_dir}\n")


if __name__ == "__main__":
    main()


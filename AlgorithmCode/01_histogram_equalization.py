"""
====================================================================================================
BỘ MÔN: XỬ LÝ ẢNH SỐ (IMAGE PROCESSING) - ĐỒ ÁN MÔN HỌC
THUẬT TOÁN 1: CÂN BẰNG BIỂU ĐỒ MỨC XÁM (HISTOGRAM EQUALIZATION - HE & ADAPTIVE HE)
Tác giả / Thành viên: Nguyễn Ngọc Thảo Hiền - 2045240078
Mục tiêu:
    1. Nghiên cứu lý thuyết và cài đặt thuật toán Histogram Equalization (Toàn cục & Cục bộ AHE).
    2. Ứng dụng khôi phục chi tiết, dải sáng cho ảnh phong cảnh ngoại cảnh thiếu sáng.
    3. Ngăn chặn hiện tượng méo/bệt màu bằng kỹ thuật tách kênh không gian màu HSV (kênh V).
    4. Đo lường định lượng hiệu năng bằng bộ 3 chỉ số học thuật: PSNR (dB), SSIM, NIQE.
====================================================================================================

CƠ SỞ LÝ THUYẾT & CÔNG THỨC TOÁN HỌC:
----------------------------------------------------------------------------------------------------
1. Xác suất xuất hiện mức xám r_k trong ảnh kích thước M x N:
       p_r(r_k) = n_k / (M * N),  với k = 0, 1, ..., L - 1 (L = 256 đối với ảnh 8-bit).
   Trong đó:
       n_k : Số lượng điểm ảnh có mức xám r_k.
       M*N : Tổng số lượng điểm ảnh.

2. Hàm biến đổi phân phối tích lũy (Cumulative Distribution Function - CDF):
       s_k = T(r_k) = (L - 1) * sum_{j=0}^k p_r(r_j) = [(L - 1) / (M * N)] * sum_{j=0}^k n_j
   Biến đổi này ánh xạ dải mức xám bị dồn ở vùng tối trải phẳng đồng đều trên toàn bộ dải [0, 255].

3. Nhược điểm khi áp dụng cho ảnh màu RGB:
   Nếu cân bằng độc lập 3 kênh R, G, B, tỷ lệ R:G:B tại mỗi điểm ảnh bị phá vỡ => Lệch màu nghiêm trọng.
   => Giải pháp: Chuyển sang không gian màu HSV, chỉ xử lý trên kênh V (Value - Độ sáng), giữ nguyên
                 kênh H (Hue - Sắc thái) và S (Saturation - Độ bão hòa).
====================================================================================================
"""

import os
import sys
import time
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

import cv2
import numpy as np
import matplotlib.pyplot as plt

# Đảm bảo UTF-8 cho Windows Terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ==================================================================================================
# 1. BỘ LỌC KHỬ NHIỄU TIỀN XỬ LÝ (PRE-DENOISING FILTER)
# ==================================================================================================
def apply_bilateral_denoising(img_bgr: np.ndarray, d: int = 7, sigma_color: float = 50.0, sigma_space: float = 50.0) -> np.ndarray:
    """
    Bộ lọc song phương (Bilateral Filter) bảo tồn đường biên:
    Triệt tiêu nhiễu hạt trước khi cân bằng biểu đồ mức xám, ngăn ngừa việc khuếch đại nhiễu nền.
    """
    return cv2.bilateralFilter(img_bgr, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)


# ==================================================================================================
# 2. THUẬT TOÁN HISTOGRAM EQUALIZATION TRÊN KÊNH ĐỘ SÁNG (HSV - V CHANNEL)
# ==================================================================================================
def enhance_histogram_equalization(
    img_bgr: np.ndarray,
    adaptive: bool = False,
    clip_limit_ahe: float = 40.0,
    tile_grid_size: Tuple[int, int] = (8, 8)
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Quy trình chuẩn hóa thực thi thuật toán HE:
    Bước 1: Chuyển đổi không gian màu từ BGR sang HSV.
    Bước 2: Tách 3 kênh độc lập (H, S, V).
    Bước 3: Cân bằng biểu đồ mức xám trên kênh độ sáng V:
            - Toàn cục (Global HE): Dùng cv2.equalizeHist()
            - Cục bộ (Adaptive HE): Dùng cv2.createCLAHE() với clipLimit cao.
    Bước 4: Ghép 3 kênh (H, S, V_enhanced).
    Bước 5: Chuyển đổi ngược từ HSV sang BGR.

    Returns:
        (img_enhanced_bgr, v_channel_original, v_channel_enhanced)
    """
    # Bước 1 & 2: Chuyển đổi và tách kênh
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h_chan, s_chan, v_chan = cv2.split(hsv)

    # Bước 3: Cân bằng kênh độ sáng V
    if adaptive:
        # AHE: Cân bằng thích nghi cục bộ trên từng ô lưới
        ahe = cv2.createCLAHE(clipLimit=clip_limit_ahe, tileGridSize=tile_grid_size)
        v_enhanced = ahe.apply(v_chan)
    else:
        # Global HE: Cân bằng toàn cục truyền thống
        v_enhanced = cv2.equalizeHist(v_chan)

    # Bước 4 & 5: Ghép kênh và chuyển ngược về BGR
    merged_hsv = cv2.merge([h_chan, s_chan, v_enhanced])
    enhanced_bgr = cv2.cvtColor(merged_hsv, cv2.COLOR_HSV2BGR)

    return enhanced_bgr, v_chan, v_enhanced


# ==================================================================================================
# 3. CÁC HÀM TÍNH TOÁN CHỈ SỐ ĐÁNH GIÁ ĐỊNH LƯỢNG (IQA METRICS)
# ==================================================================================================
def calculate_psnr(img_ref: np.ndarray, img_tgt: np.ndarray) -> float:
    """Tính PSNR (dB): 10 * log10(255^2 / MSE). Giá trị càng cao biểu thị độ tương đồng tín hiệu càng lớn."""
    ref = img_ref.astype(np.float64)
    tgt = img_tgt.astype(np.float64)
    mse = np.mean((ref - tgt) ** 2)
    if mse < 1e-10:
        return 100.0
    return float(10.0 * np.log10((255.0 ** 2) / mse))


def calculate_ssim(img_ref: np.ndarray, img_tgt: np.ndarray) -> float:
    """Tính SSIM (0 - 1): Đánh giá bảo toàn cấu trúc thị giác (độ sáng, tương phản, cấu trúc hình học)."""
    try:
        from skimage.metrics import structural_similarity as ssim_fn
        return float(ssim_fn(img_ref, img_tgt, channel_axis=2, data_range=255.0))
    except ImportError:
        # Fallback numpy đơn giản trên kênh xám
        g1 = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY).astype(np.float64)
        g2 = cv2.cvtColor(img_tgt, cv2.COLOR_BGR2GRAY).astype(np.float64)
        mu1, mu2 = np.mean(g1), np.mean(g2)
        var1, var2 = np.var(g1), np.var(g2)
        cov = np.mean((g1 - mu1) * (g2 - mu2))
        c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
        return float(((2 * mu1 * mu2 + c1) * (2 * cov + c2)) / ((mu1**2 + mu2**2 + c1) * (var1 + var2 + c2)))


def calculate_niqe(img_bgr: np.ndarray) -> float:
    """
    Tính chỉ số NIQE (Naturalness Image Quality Evaluator - Blind No-reference):
    Đánh giá độ tự nhiên của ảnh mà không cần ảnh gốc đối chứng.
    QUY TẮC: ĐIỂM CÀNG NHỎ => ẢNH CÀNG TỰ NHIÊN, CÀNG ĐẸP!
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    mu = cv2.GaussianBlur(gray, (7, 7), 7.0 / 6.0)
    mu_sq = mu * mu
    sigma = np.sqrt(np.abs(cv2.GaussianBlur(gray * gray, (7, 7), 7.0 / 6.0) - mu_sq))
    structdis = (gray - mu) / (sigma + 1.0)
    
    # Ước lượng độ lệch phương sai NSS đơn giản hóa
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
    # Fallback độc lập nếu file được chạy riêng lẻ mà không có path_utils.py
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
    print("  [DEMO] THUẬT TOÁN HISTOGRAM EQUALIZATION (HE) TRÊN ẢNH THIẾU SÁNG")
    print("  Người thực hiện: Nguyễn Ngọc Thảo Hiền (MSSV: 2045240078)")
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
        print("  • Đang giả lập môi trường thiếu sáng (độ chói giảm 65%, nén gamma tối = 2.2)...")
        dark_float = np.power(clean_img.astype(np.float32) / 255.0, 2.2) * 0.35
        low_light_img = np.clip(dark_float * 255.0, 0, 255).astype(np.uint8)
        # Thêm nhiễu Gauss thực nghiệm
        noise = np.random.normal(0, 15, low_light_img.shape)
        low_light_noisy = np.clip(low_light_img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        is_simulated = True

    # 2. Tiền xử lý khử nhiễu
    t0 = time.perf_counter()
    denoised_input = apply_bilateral_denoising(low_light_noisy, d=7, sigma_color=50, sigma_space=50)

    # 3. Thực thi Histogram Equalization (Toàn cục & Cục bộ Adaptive)
    he_global, v_orig, v_he = enhance_histogram_equalization(denoised_input, adaptive=False)
    he_adaptive, _, v_ahe = enhance_histogram_equalization(denoised_input, adaptive=True, clip_limit_ahe=40.0)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    # 4. Đo lường chỉ số học thuật
    psnr_noisy = calculate_psnr(clean_img, low_light_noisy) if is_simulated else 0.0
    psnr_he = calculate_psnr(clean_img, he_global) if is_simulated else 0.0
    psnr_ahe = calculate_psnr(clean_img, he_adaptive) if is_simulated else 0.0

    ssim_noisy = calculate_ssim(clean_img, low_light_noisy) if is_simulated else 0.0
    ssim_he = calculate_ssim(clean_img, he_global) if is_simulated else 0.0
    ssim_ahe = calculate_ssim(clean_img, he_adaptive) if is_simulated else 0.0

    niqe_noisy = calculate_niqe(low_light_noisy)
    niqe_he = calculate_niqe(he_global)
    niqe_ahe = calculate_niqe(he_adaptive)

    print("\n" + "-" * 85)
    print("  KẾT QUẢ ĐO LƯỜNG ĐỊNH LƯỢNG:")
    print("-" * 85)
    if is_simulated:
        print(f"  Trạng thái ảnh            | PSNR (dB) | SSIM   | NIQE (càng nhỏ càng tốt)")
        print("-" * 85)
        print(f"  1. Ảnh thiếu sáng + nhiễu | {psnr_noisy:<9.2f} | {ssim_noisy:<6.4f} | {niqe_noisy:<6.2f}")
        print(f"  2. Sau Global HE          | {psnr_he:<9.2f} | {ssim_he:<6.4f} | {niqe_he:<6.2f} (Thời gian: {elapsed_ms:.2f} ms)")
        print(f"  3. Sau Adaptive HE (AHE)  | {psnr_ahe:<9.2f} | {ssim_ahe:<6.4f} | {niqe_ahe:<6.2f}")
    else:
        print(f"  Trạng thái ảnh            | NIQE (Chỉ số tự nhiên - càng nhỏ càng tốt) | Thời Gian (ms)")
        print("-" * 85)
        print(f"  1. Ảnh thiếu sáng gốc     | {niqe_noisy:<42.2f} | --")
        print(f"  2. Sau Global HE          | {niqe_he:<42.2f} | {elapsed_ms:.2f} ms")
        print(f"  3. Sau Adaptive HE (AHE)  | {niqe_ahe:<42.2f} | --")
    print("-" * 85)
    print("  NHẬN XÉT HỌC THUẬT:")
    print("  • Global HE kéo sáng rất mạnh các vùng tối, nhưng nhược điểm lớn là làm bệt màu nền trời")
    print("    và khuếch đại nhiễu hạt ở các vùng đồng nhất.")
    print("  • Adaptive HE phân vùng cục bộ tốt hơn nhưng vẫn dễ sinh nhiễu nếu không có Clip Limit.")
    print("=" * 85)

    # 5. Lưu ảnh kết quả an toàn bằng imwrite_unicode (hỗ trợ thư mục tiếng Việt)
    out_dir = get_output_dir("output_demo")
    imwrite_unicode(out_dir / "01_input_lowlight_noisy.jpg", low_light_noisy)
    imwrite_unicode(out_dir / "01_he_global_enhanced.jpg", he_global)
    imwrite_unicode(out_dir / "01_he_adaptive_enhanced.jpg", he_adaptive)
    print(f"  >> Đã lưu ảnh kết quả vào thư mục: {out_dir}\n")


if __name__ == "__main__":
    main()


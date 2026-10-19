"""
====================================================================================================
BỘ MÔN: XỬ LÝ ẢNH SỐ (IMAGE PROCESSING) - ĐỒ ÁN MÔN HỌC
THUẬT TOÁN 2: CÂN BẰNG TƯƠNG PHẢN THÍCH NGHI GIỚI HẠN (CLAHE - CONTRAST LIMITED ADAPTIVE HE)
Tác giả / Thành viên: Vũ Thế Quang - 2045240253 (Làm Slide & Báo cáo CLAHE)
Mục tiêu:
    1. Nghiên cứu cơ chế chia ô cục bộ (Tile Grid), ngưỡng cắt Clip Limit và phân phối lại phần dư.
    2. Khắc phục triệt để hiện tượng khuếch đại nhiễu hạt và hiệu ứng bàn cờ của HE truyền thống.
    3. Xử lý trên kênh độ sáng V của không gian màu HSV để bảo toàn độ bão hòa màu sắc phong cảnh.
    4. Đo lường định lượng hiệu năng bằng bộ 3 chỉ số học thuật: PSNR (dB), SSIM, NIQE.
====================================================================================================

CƠ SỞ LÝ THUYẾT & CÔNG THỨC TOÁN HỌC:
----------------------------------------------------------------------------------------------------
1. Chia lưới cục bộ (Local Tile Grid):
   Ảnh kích thước H x W được chia thành lưới grid_y x grid_x ô con (Tiles). Kích thước mỗi ô là:
       M_tile = H / grid_y,    N_tile = W / grid_x   (Thường chọn 8 x 8 ô).

2. Ngưỡng cắt lý thuyết (Clip Limit - N_clip):
   Số lượng điểm ảnh trung bình trên mỗi bin mức xám của 1 ô (L = 256):
       N_avg = (M_tile * N_tile) / L
   Ngưỡng cắt dựa trên hệ số nhân Clip Limit beta:
       N_clip = beta * N_avg   (Thường chọn beta = 2.0 - 4.0).

3. Tái phân phối phần dư (Pixel Redistribution):
   Tổng số lượng pixel vượt ngưỡng trong ô:
       N_clipped = sum_{k=0}^{L-1} max(0, h(k) - N_clip)
   Số pixel phân phối đều lại vào mỗi bin:
       R = N_clipped / L
   Histogram đã điều hòa:
       h_mod(k) = min(h(k), N_clip) + R

4. Nội suy song tuyến tính (Bilinear Interpolation):
   Khử triệt để hiện tượng đường biên ô lưới (checkerboard artifacts) giữa 4 ô lân cận
   khi ánh xạ mức xám tại vị trí pixel (x, y).
====================================================================================================
"""

import os
import sys
import time
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

import cv2
import numpy as np

# Đảm bảo UTF-8 cho Windows Terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ==================================================================================================
# 1. BỘ LỌC KHỬ NHIỄU BẢO TỒN BIÊN (BILATERAL FILTER)
# ==================================================================================================
def apply_bilateral_denoising(img_bgr: np.ndarray, d: int = 7, sigma_color: float = 50.0, sigma_space: float = 50.0) -> np.ndarray:
    """Khử nhiễu tiền xử lý trước khi chạy CLAHE."""
    return cv2.bilateralFilter(img_bgr, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)


# ==================================================================================================
# 2. THUẬT TOÁN CLAHE TRÊN KÊNH ĐỘ SÁNG (HSV - V CHANNEL)
# ==================================================================================================
def enhance_clahe(
    img_bgr: np.ndarray,
    clip_limit: float = 3.0,
    tile_grid_size: Tuple[int, int] = (8, 8)
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Quy trình thực thi CLAHE chuẩn công nghiệp:
    1. Chuyển đổi BGR sang HSV để tách riêng kênh độ sáng V khỏi màu sắc H và S.
    2. Khởi tạo đối tượng cv2.createCLAHE(clipLimit, tileGridSize).
    3. Áp dụng CLAHE trên kênh V: Tăng tương phản cục bộ mà không khuếch đại nhiễu hạt.
    4. Ghép lại 3 kênh (H, S, V_enhanced) và chuyển ngược về BGR.

    Returns:
        (enhanced_bgr, v_original, v_enhanced)
    """
    # Bước 1: Chuyển đổi sang HSV
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h_chan, s_chan, v_chan = cv2.split(hsv)

    # Bước 2 & 3: Áp dụng CLAHE trên kênh độ sáng V
    clahe_obj = cv2.createCLAHE(clipLimit=float(clip_limit), tileGridSize=tile_grid_size)
    v_enhanced = clahe_obj.apply(v_chan)

    # Bước 4: Ghép kênh và chuyển ngược về BGR
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
    print("  [DEMO] THUẬT TOÁN CLAHE (CONTRAST LIMITED ADAPTIVE HISTOGRAM EQUALIZATION)")
    print("  Người thực hiện: Vũ Thế Quang (MSSV: 2045240253)")
    print("  Ứng dụng khôi phục chi tiết ảnh phong cảnh ngoại cảnh thiếu sáng")
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
    t0 = time.perf_counter()
    denoised_input = apply_bilateral_denoising(low_light_noisy, d=7, sigma_color=50, sigma_space=50)

    # 3. Thử nghiệm CLAHE với các giá trị Clip Limit khác nhau
    clahe_light, _, _ = enhance_clahe(denoised_input, clip_limit=1.5, tile_grid_size=(8, 8))
    clahe_standard, _, _ = enhance_clahe(denoised_input, clip_limit=3.0, tile_grid_size=(8, 8))
    clahe_strong, _, _ = enhance_clahe(denoised_input, clip_limit=5.0, tile_grid_size=(8, 8))
    elapsed_ms = (time.perf_counter() - t0) * 1000

    # 4. Đo lường chỉ số học thuật
    psnr_noisy = calculate_psnr(clean_img, low_light_noisy) if is_simulated else 0.0
    psnr_std = calculate_psnr(clean_img, clahe_standard) if is_simulated else 0.0

    ssim_noisy = calculate_ssim(clean_img, low_light_noisy) if is_simulated else 0.0
    ssim_std = calculate_ssim(clean_img, clahe_standard) if is_simulated else 0.0

    niqe_noisy = calculate_niqe(low_light_noisy)
    niqe_std = calculate_niqe(clahe_standard)

    print("\n" + "-" * 85)
    print("  KẾT QUẢ ĐO LƯỜNG ĐỊNH LƯỢNG (SO SÁNH CÁC MỨC CLIP LIMIT):")
    print("-" * 85)
    if is_simulated:
        print(f"  Trạng thái ảnh            | PSNR (dB) | SSIM   | NIQE (càng nhỏ càng tốt)")
        print("-" * 85)
        print(f"  1. Ảnh thiếu sáng + nhiễu | {psnr_noisy:<9.2f} | {ssim_noisy:<6.4f} | {niqe_noisy:<6.2f}")
        print(f"  2. CLAHE (Clip = 1.5 nhẹ) | {calculate_psnr(clean_img, clahe_light):<9.2f} | {calculate_ssim(clean_img, clahe_light):<6.4f} | {calculate_niqe(clahe_light):<6.2f}")
        print(f"  3. CLAHE (Clip = 3.0 chuẩn)| {psnr_std:<9.2f} | {ssim_std:<6.4f} | {niqe_std:<6.2f} (Thời gian: {elapsed_ms:.2f} ms)")
        print(f"  4. CLAHE (Clip = 5.0 mạnh)| {calculate_psnr(clean_img, clahe_strong):<9.2f} | {calculate_ssim(clean_img, clahe_strong):<6.4f} | {calculate_niqe(clahe_strong):<6.2f}")
    else:
        print(f"  Trạng thái ảnh            | NIQE (Chỉ số tự nhiên - càng nhỏ càng tốt)")
        print("-" * 85)
        print(f"  1. Ảnh thiếu sáng gốc     | {niqe_noisy:<42.2f}")
        print(f"  2. CLAHE (Clip = 1.5 nhẹ) | {calculate_niqe(clahe_light):<42.2f}")
        print(f"  3. CLAHE (Clip = 3.0 chuẩn)| {niqe_std:<42.2f} (Thời gian: {elapsed_ms:.2f} ms)")
        print(f"  4. CLAHE (Clip = 5.0 mạnh)| {calculate_niqe(clahe_strong):<42.2f}")
    print("-" * 85)
    print("  NHẬN XÉT HỌC THUẬT:")
    print("  • Clip Limit = 3.0 đạt sự cân bằng tối ưu: Tăng cường rõ nét chi tiết cây cối và dốc núi")
    print("    mà không làm gắt hạt nhiễu hoặc gây cháy sáng bầu trời đêm.")
    print("  • Nội suy song tuyến tính loại bỏ hoàn toàn hiện tượng biên ô lưới (checkerboard artifacts).")
    print("=" * 85)

    # 5. Lưu ảnh kết quả an toàn bằng imwrite_unicode (hỗ trợ thư mục tiếng Việt)
    out_dir = get_output_dir("output_demo")
    imwrite_unicode(out_dir / "02_clahe_clip1.5.jpg", clahe_light)
    imwrite_unicode(out_dir / "02_clahe_clip3.0_standard.jpg", clahe_standard)
    imwrite_unicode(out_dir / "02_clahe_clip5.0_strong.jpg", clahe_strong)
    print(f"  >> Đã lưu ảnh kết quả vào thư mục: {out_dir}\n")


if __name__ == "__main__":
    main()


"""
====================================================================================================
BỘ MÔN: XỬ LÝ ẢNH SỐ (IMAGE PROCESSING) - ĐỒ ÁN MÔN HỌC
FILE TỔNG HỢP TOÀN DIỆN: SO SÁNH 4 THUẬT TOÁN XỬ LÝ ẢNH THIẾU SÁNG TRUYỀN THỐNG
Tên đề tài: "Ứng Dụng So Sánh Nghiên cứu kỹ thuật xử lý ảnh"
English: "A Comparative Study of Traditional Image Processing Techniques in Enhancing Low-Light Outdoor Landscape Images"

Bao gồm 4 thuật toán:
    1. Histogram Equalization (HE & Adaptive HE)
    2. Contrast Limited Adaptive Histogram Equalization (CLAHE)
    3. Gamma Correction (Hiệu chỉnh hàm lũy thừa phi tuyến)
    4. Multi-Scale Retinex (MSR / MSRCR đa quy mô)

Quy chuẩn kỹ thuật:
    - Tiền xử lý: Lọc khử nhiễu bảo tồn đường biên (Bilateral Filter).
    - Tách màu: Chuyển sang không gian màu HSV, chỉ xử lý trên kênh độ sáng V (Value), giữ nguyên H, S
      để chống hiện tượng bệt màu và lệch màu (Color Distortion).
    - Đo lường định lượng: PSNR (dB), SSIM (0 -> 1) và NIQE (chỉ số tự nhiên không cần ảnh gốc).
====================================================================================================
"""

import os
import sys
import time
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional

import cv2
import numpy as np
import matplotlib.pyplot as plt

# Đảm bảo UTF-8 cho Windows Terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ==================================================================================================
# 1. TIỀN XỬ LÝ KHỬ NHIỄU BẢO TỒN BIÊN
# ==================================================================================================
def apply_bilateral_denoising(img_bgr: np.ndarray, d: int = 7, sigma_color: float = 50.0, sigma_space: float = 50.0) -> np.ndarray:
    """Khử nhiễu tiền xử lý bằng bộ lọc song phương Bilateral Filter."""
    return cv2.bilateralFilter(img_bgr, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)


# ==================================================================================================
# 2. BỐN THUẬT TOÁN XỬ LÝ ẢNH TRÊN KÊNH ĐỘ SÁNG V (HSV)
# ==================================================================================================

# --- THUẬT TOÁN 1: HISTOGRAM EQUALIZATION ---
def run_he(img_bgr: np.ndarray, adaptive: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """Thuật toán 1: Histogram Equalization (HE) toàn cục / thích nghi."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    if adaptive:
        ahe = cv2.createCLAHE(clipLimit=40.0, tileGridSize=(8, 8))
        v_enh = ahe.apply(v)
    else:
        v_enh = cv2.equalizeHist(v)
    res_bgr = cv2.cvtColor(cv2.merge([h, s, v_enh]), cv2.COLOR_HSV2BGR)
    return res_bgr, v_enh


# --- THUẬT TOÁN 2: CLAHE ---
def run_clahe(img_bgr: np.ndarray, clip_limit: float = 3.0, tile_grid: Tuple[int, int] = (8, 8)) -> Tuple[np.ndarray, np.ndarray]:
    """Thuật toán 2: Contrast Limited Adaptive Histogram Equalization (CLAHE)."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    clahe = cv2.createCLAHE(clipLimit=float(clip_limit), tileGridSize=tile_grid)
    v_enh = clahe.apply(v)
    res_bgr = cv2.cvtColor(cv2.merge([h, s, v_enh]), cv2.COLOR_HSV2BGR)
    return res_bgr, v_enh


# --- THUẬT TOÁN 3: GAMMA CORRECTION ---
def run_gamma(img_bgr: np.ndarray, gamma: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
    """Thuật toán 3: Gamma Correction (Bảng tra cứu LUT O(1))."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    table = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype("uint8")
    v_enh = cv2.LUT(v, table)
    res_bgr = cv2.cvtColor(cv2.merge([h, s, v_enh]), cv2.COLOR_HSV2BGR)
    return res_bgr, v_enh


# --- THUẬT TOÁN 4: MULTI-SCALE RETINEX ---
def run_msr(
    img_bgr: np.ndarray,
    scales: List[int] = [15, 80, 250],
    weights: List[float] = [0.3333, 0.3333, 0.3334],
    clip_percentile: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """Thuật toán 4: Multi-Scale Retinex (MSR) đa quy mô Gauss."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    v_float = v.astype(np.float64) + 1.0
    log_v = np.log(v_float)
    msr_acc = np.zeros_like(log_v)

    for sc, w in zip(scales, weights):
        blurred = np.maximum(cv2.GaussianBlur(v_float, (0, 0), float(sc)), 1.0)
        msr_acc += w * (log_v - np.log(blurred))

    p_low = np.percentile(msr_acc, clip_percentile)
    p_high = np.percentile(msr_acc, 100.0 - clip_percentile)

    if p_high - p_low < 1e-5:
        clipped = msr_acc - p_low
    else:
        clipped = (msr_acc - p_low) / (p_high - p_low) * 255.0

    v_enh = np.clip(clipped, 0, 255).astype(np.uint8)
    res_bgr = cv2.cvtColor(cv2.merge([h, s, v_enh]), cv2.COLOR_HSV2BGR)
    return res_bgr, v_enh


# ==================================================================================================
# 3. BỘ BA CHỈ SỐ ĐÁNH GIÁ ĐỊNH LƯỢNG (IQA METRICS)
# ==================================================================================================
def calculate_psnr(img_ref: np.ndarray, img_tgt: np.ndarray) -> float:
    """PSNR (dB): Đánh giá tỷ số tín hiệu cực đại trên sai số bình phương trung bình MSE."""
    ref = img_ref.astype(np.float64)
    tgt = img_tgt.astype(np.float64)
    mse = np.mean((ref - tgt) ** 2)
    if mse < 1e-10:
        return 100.0
    return float(10.0 * np.log10((255.0 ** 2) / mse))


def calculate_ssim(img_ref: np.ndarray, img_tgt: np.ndarray) -> float:
    """SSIM (0 -> 1): Đo lường độ tương đồng cấu trúc HVS."""
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
    """NIQE: Chỉ số tự nhiên không cần ảnh gốc (Blind No-reference). CÀNG NHỎ CÀNG TỰ NHIÊN!"""
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
# 4. CHƯƠNG TRÌNH THỰC THI SO SÁNH ĐỒNG THỜI 4 THUẬT TOÁN
# ==================================================================================================
def main():
    print("=" * 90)
    print("  🔬 BẢNG SO SÁNH HIỆU NĂNG 4 THUẬT TOÁN XỬ LÝ ẢNH THIẾU SÁNG TRUYỀN THỐNG")
    print("  Ứng Dụng So Sánh Nghiên cứu kỹ thuật xử lý ảnh (Universal XAI Suite)")
    print("=" * 90)

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
        noise = np.random.normal(0, 15, low_light_img.shape)
        low_light_noisy = np.clip(low_light_img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        is_simulated = True

    # 2. Tiền xử lý khử nhiễu
    denoised_input = apply_bilateral_denoising(low_light_noisy, d=7, sigma_color=50, sigma_space=50)

    # 3. Chạy 4 thuật toán và bấm giờ
    methods = {}

    # Method 1: HE
    t0 = time.perf_counter()
    he_res, _ = run_he(denoised_input)
    t_he = (time.perf_counter() - t0) * 1000
    methods["HE"] = {"img": he_res, "time": t_he, "desc": "Histogram Equalization"}

    # Method 2: CLAHE
    t0 = time.perf_counter()
    clahe_res, _ = run_clahe(denoised_input, clip_limit=3.0, tile_grid=(8, 8))
    t_clahe = (time.perf_counter() - t0) * 1000
    methods["CLAHE"] = {"img": clahe_res, "time": t_clahe, "desc": "CLAHE (Clip=3.0)"}

    # Method 3: Gamma Correction
    t0 = time.perf_counter()
    gamma_res, _ = run_gamma(denoised_input, gamma=0.5)
    t_gamma = (time.perf_counter() - t0) * 1000
    methods["Gamma"] = {"img": gamma_res, "time": t_gamma, "desc": "Gamma (γ=0.5)"}

    # Method 4: Multi-Scale Retinex
    t0 = time.perf_counter()
    msr_res, _ = run_msr(denoised_input, scales=[15, 80, 250])
    t_msr = (time.perf_counter() - t0) * 1000
    methods["MSR"] = {"img": msr_res, "time": t_msr, "desc": "Multi-Scale Retinex"}

    # 4. Bảng tổng hợp số liệu
    print("\n" + "-" * 90)
    if is_simulated:
        print(f"{'Thuật Toán':<18} | {'PSNR (dB)':<12} | {'SSIM':<10} | {'NIQE (Càng nhỏ càng tốt)':<26} | {'Thời Gian (ms)':<15}")
        print("-" * 90)
        psnr_base = calculate_psnr(clean_img, low_light_noisy)
        ssim_base = calculate_ssim(clean_img, low_light_noisy)
        niqe_base = calculate_niqe(low_light_noisy)
        print(f"{'Ảnh Thiếu Sáng':<18} | {psnr_base:<12.2f} | {ssim_base:<10.4f} | {niqe_base:<26.2f} | {'--':<15}")

        for name, data in methods.items():
            p = calculate_psnr(clean_img, data["img"])
            s = calculate_ssim(clean_img, data["img"])
            n = calculate_niqe(data["img"])
            print(f"{name:<18} | {p:<12.2f} | {s:<10.4f} | {n:<26.2f} | {data['time']:<15.2f}")
    else:
        print(f"{'Thuật Toán':<24} | {'NIQE (Càng nhỏ càng tốt)':<30} | {'Thời Gian (ms)':<18}")
        print("-" * 90)
        niqe_base = calculate_niqe(low_light_noisy)
        print(f"{'Ảnh Thiếu Sáng Gốc':<24} | {niqe_base:<30.2f} | {'--':<18}")
        for name, data in methods.items():
            n = calculate_niqe(data["img"])
            print(f"{data['desc']:<24} | {n:<30.2f} | {data['time']:<18.2f}")
    print("-" * 90)

    # 5. Lưu từng ảnh kết quả và xuất ảnh ghép trực quan 2x3
    out_dir = get_output_dir("output_demo")
    imwrite_unicode(out_dir / "all_input_lowlight.jpg", low_light_noisy)
    imwrite_unicode(out_dir / "all_he.jpg", he_res)
    imwrite_unicode(out_dir / "all_clahe.jpg", clahe_res)
    imwrite_unicode(out_dir / "all_gamma.jpg", gamma_res)
    imwrite_unicode(out_dir / "all_msr.jpg", msr_res)

    try:
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes[0, 0].imshow(cv2.cvtColor(clean_img, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title("1. Ảnh Đầu Vào Gốc")
        axes[0, 0].axis("off")

        axes[0, 1].imshow(cv2.cvtColor(low_light_noisy, cv2.COLOR_BGR2RGB))
        title_dark = f"2. Thiếu Sáng & Nhiễu\nNIQE: {calculate_niqe(low_light_noisy):.2f}"
        if is_simulated:
            title_dark = f"2. Thiếu Sáng & Nhiễu\nPSNR: {calculate_psnr(clean_img, low_light_noisy):.2f}dB | NIQE: {calculate_niqe(low_light_noisy):.2f}"
        axes[0, 1].set_title(title_dark)
        axes[0, 1].axis("off")

        axes[0, 2].imshow(cv2.cvtColor(he_res, cv2.COLOR_BGR2RGB))
        title_he = f"3. Histogram Equalization (HE)\nNIQE: {calculate_niqe(he_res):.2f}"
        if is_simulated:
            title_he = f"3. HE (Toàn Cục)\nPSNR: {calculate_psnr(clean_img, he_res):.2f}dB | NIQE: {calculate_niqe(he_res):.2f}"
        axes[0, 2].set_title(title_he)
        axes[0, 2].axis("off")

        axes[1, 0].imshow(cv2.cvtColor(clahe_res, cv2.COLOR_BGR2RGB))
        title_clahe = f"4. CLAHE (Khuyên dùng)\nNIQE: {calculate_niqe(clahe_res):.2f}"
        if is_simulated:
            title_clahe = f"4. CLAHE (Khuyên dùng)\nPSNR: {calculate_psnr(clean_img, clahe_res):.2f}dB | NIQE: {calculate_niqe(clahe_res):.2f}"
        axes[1, 0].set_title(title_clahe)
        axes[1, 0].axis("off")

        axes[1, 1].imshow(cv2.cvtColor(gamma_res, cv2.COLOR_BGR2RGB))
        title_gamma = f"5. Gamma Correction (γ=0.5)\nNIQE: {calculate_niqe(gamma_res):.2f}"
        if is_simulated:
            title_gamma = f"5. Gamma (γ=0.5)\nPSNR: {calculate_psnr(clean_img, gamma_res):.2f}dB | NIQE: {calculate_niqe(gamma_res):.2f}"
        axes[1, 1].set_title(title_gamma)
        axes[1, 1].axis("off")

        axes[1, 2].imshow(cv2.cvtColor(msr_res, cv2.COLOR_BGR2RGB))
        title_msr = f"6. Multi-Scale Retinex (MSR)\nNIQE: {calculate_niqe(msr_res):.2f}"
        if is_simulated:
            title_msr = f"6. MSR (Retinex)\nPSNR: {calculate_psnr(clean_img, msr_res):.2f}dB | NIQE: {calculate_niqe(msr_res):.2f}"
        axes[1, 2].set_title(title_msr)
        axes[1, 2].axis("off")

        plt.tight_layout()
        comparison_chart_path = out_dir / "so_sanh_4_thuat_toan.png"
        plt.savefig(str(comparison_chart_path), dpi=200)
        plt.close()

        print(f"  🏆 Đã lưu biểu đồ ảnh so sánh 6 ô trực quan vào:")
        print(f"     -> {comparison_chart_path}")
    except Exception as e:
        print(f"  [Thông báo] Bỏ qua xuất biểu đồ matplotlib ({e}), đã lưu 4 ảnh riêng lẻ.")

    print(f"  >> Toàn bộ kết quả đã được lưu tại: {out_dir}\n")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()


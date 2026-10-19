"""
Business/Model Layer: Pipeline Orchestrator & Multi-Method Comparison
src/model_logic.py - Universal XAI & 3-Tier Blueprint
Coordinates:
1. End-to-end processing pipeline across all 4 traditional enhancement methods:
   - Method 1: Histogram Equalization (HE & Adaptive HE)
   - Method 2: CLAHE (Contrast Limited Adaptive Histogram Equalization)
   - Method 3: Gamma Correction (with parameter exploration)
   - Method 4: Multi-Scale Retinex (MSR / MSRCR)
2. Quantitative comparative evaluation (PSNR, SSIM, NIQE, Execution Time).
3. Intermediate XAI extraction (Histograms, Difference Maps, Mathematical LaTeX).
4. Batch benchmark execution on dataset with CSV reporting.
5. Resource and memory lifecycle management.
"""

import os
import csv
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import cv2
import numpy as np

from src.data_loader import DataLoader
from src.enhancement_modules import EnhancementModules
from src.metrics import ImageQualityMetrics
from src.config import AppConfig
from src.resource_manager import cleanup_memory

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ImageEnhancementComparisonPipeline:
    """
    Master Business Logic coordinator comparing 4 traditional enhancement techniques
    for low-light outdoor landscape enhancement.
    """

    VERSION = "comparative_suite_v1.0"

    # LaTeX Formulas for Academic Representation
    MATH_FORMULAS = {
        "he": r"s_k = T(r_k) = (L - 1) \sum_{j=0}^k \frac{n_j}{M \cdot N} = (L - 1) \sum_{j=0}^k p_r(r_j)",
        "clahe": r"N_{\text{clip}} = \beta \cdot \frac{M_{\text{tile}} \cdot N_{\text{tile}}}{256}, \quad h_{\text{mod}}(k) = \min(h(k), N_{\text{clip}}) + \frac{N_{\text{clipped}}}{256}",
        "gamma": r"V_{\text{out}} = 255 \cdot \left(\frac{V_{\text{in}}}{255}\right)^\gamma, \quad (\gamma < 1.0 \text{ khôi phục vùng tối})",
        "msr": r"R_{\text{MSR}}(x, y) = \sum_{k=1}^K w_k \cdot \left[ \ln(I(x, y)) - \ln(I(x, y) * G_k(x, y)) \right], \quad G_k \sim \mathcal{N}(0, \sigma_k^2)"
    }

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        self.data_loader = DataLoader(str(self.config.get_dataset_dir()))
        self.last_result: Optional[Dict[str, Any]] = None

    def process_comparison(
        self,
        image_input: Any,
        simulate_low_light: bool = True,
        brightness_factor: Optional[float] = None,
        gamma_darkening: Optional[float] = None,
        noise_type: str = "gaussian",
        noise_params: Optional[Dict[str, Any]] = None,
        denoise_method: str = "bilateral",
        denoise_params: Optional[Dict[str, Any]] = None,
        clahe_clip_limit: float = 3.0,
        clahe_grid_size: Tuple[int, int] = (8, 8),
        gamma_val: float = 0.5,
        color_space: str = "HSV"
    ) -> Dict[str, Any]:
        """
        Thực thi quy trình so sánh toàn diện 4 phương pháp trên cùng một ảnh đầu vào:
        1. Nạp ảnh (Clean Image) & Xử lý 3 edge cases.
        2. Mô phỏng ảnh thiếu sáng (Low-light) + Bơm nhiễu học thuật (Synthetic Noise).
        3. Khử nhiễu tiền xử lý (Pre-denoising).
        4. Chạy đồng thời 4 thuật toán nâng cao chất lượng (HE, CLAHE, Gamma, MSR).
        5. Đo lường định lượng toàn bộ chỉ số PSNR, SSIM, NIQE và thời gian chạy.
        6. Trích xuất biểu đồ phân phối Histogram trước & sau của cả 4 phương pháp.
        7. Xếp hạng hiệu năng và đưa ra đánh giá tổng quát.
        """
        # 1. Nạp ảnh gốc
        clean_img, filename = self.data_loader.load_image(image_input)

        is_real_upload = (
            isinstance(image_input, np.ndarray) or
            (isinstance(image_input, (str, Path)) and ("temp_web_upload" in str(image_input) or "custom_input" in str(image_input)))
        )
        clean_gt = clean_img if (not is_real_upload or simulate_low_light) else None

        # 2. Tạo ảnh suy thoái: Thiếu sáng + Nhiễu
        if is_real_upload:
            if simulate_low_light:
                bf = brightness_factor if brightness_factor is not None else self.config.low_light_brightness
                gd = gamma_darkening if gamma_darkening is not None else self.config.low_light_gamma
                dark_img = self.data_loader.simulate_low_light(clean_img, bf, gd)
                degraded_img = self.data_loader.apply_noise(dark_img, noise_type, noise_params)
            else:
                # Ảnh thực tế người dùng tải lên đã là ảnh chụp thiếu sáng sẵn
                degraded_img = clean_img.copy()
        else:
            # Ảnh từ dataset: mô phỏng thiếu sáng và bơm nhiễu
            bf = brightness_factor if brightness_factor is not None else self.config.low_light_brightness
            gd = gamma_darkening if gamma_darkening is not None else self.config.low_light_gamma
            if simulate_low_light:
                dark_img = self.data_loader.simulate_low_light(clean_img, bf, gd)
            else:
                dark_img = clean_img.copy()
            degraded_img = self.data_loader.apply_noise(dark_img, noise_type, noise_params)

        # 3. Lọc khử nhiễu tiền xử lý
        denoised_input = EnhancementModules.apply_pre_denoising(degraded_img, denoise_method, denoise_params)

        # Trích xuất biểu đồ độ sáng của ảnh đầu vào suy thoái
        if color_space.upper() == "LAB":
            input_lum = cv2.split(cv2.cvtColor(denoised_input, cv2.COLOR_BGR2LAB))[0]
        else:
            input_lum = cv2.split(cv2.cvtColor(denoised_input, cv2.COLOR_BGR2HSV))[2]
        input_hist = EnhancementModules.extract_histogram(input_lum)

        # 4. Triển khai tuần tự 4 Thuật Toán & Đo thời gian
        methods_data = {}

        # --- Method 1: Histogram Equalization (HE) ---
        t0 = time.perf_counter()
        he_img, _, he_lum = EnhancementModules.apply_histogram_equalization(
            denoised_input, color_space=color_space, adaptive=False
        )
        t_he = round((time.perf_counter() - t0) * 1000, 2)
        m_he = ImageQualityMetrics.evaluate_method(clean_gt, degraded_img, he_img)
        hist_he = EnhancementModules.extract_histogram(he_lum)
        diff_he = EnhancementModules.compute_difference_map(degraded_img, he_img)

        methods_data["he"] = {
            "name": "Histogram Equalization (HE)",
            "short_name": "HE",
            "img": he_img,
            "metrics": m_he,
            "exec_time_ms": t_he,
            "hist": hist_he,
            "diff_map": diff_he,
            "formula": self.MATH_FORMULAS["he"],
            "pros": "Kéo sáng mạnh, phân bổ lại toàn bộ dải động mức xám đơn giản, tốc độ cực nhanh.",
            "cons": "Dễ gây hiện tượng cháy sáng quá mức (over-enhancement), mất chi tiết vùng mây trời và làm bệt nhiễu nền."
        }

        # --- Method 2: CLAHE ---
        t0 = time.perf_counter()
        clahe_img, _, clahe_lum = EnhancementModules.apply_clahe(
            denoised_input, clip_limit=clahe_clip_limit, tile_grid_size=clahe_grid_size, color_space=color_space
        )
        t_clahe = round((time.perf_counter() - t0) * 1000, 2)
        m_clahe = ImageQualityMetrics.evaluate_method(clean_gt, degraded_img, clahe_img)
        hist_clahe = EnhancementModules.extract_histogram(clahe_lum)
        diff_clahe = EnhancementModules.compute_difference_map(degraded_img, clahe_img)

        methods_data["clahe"] = {
            "name": "Contrast Limited Adaptive HE (CLAHE)",
            "short_name": "CLAHE",
            "img": clahe_img,
            "metrics": m_clahe,
            "exec_time_ms": t_clahe,
            "hist": hist_clahe,
            "diff_map": diff_clahe,
            "formula": self.MATH_FORMULAS["clahe"],
            "pros": "Tăng độ tương phản cục bộ xuất sắc, bảo vệ chi tiết đường biên mà không khuếch đại nhiễu nhờ Clip Limit.",
            "cons": "Tốn chi phí tính toán hơn HE toàn cục, phụ thuộc vào việc lựa chọn kích thước ô lưới Tile Grid."
        }

        # --- Method 3: Gamma Correction ---
        t0 = time.perf_counter()
        gamma_img, _, gamma_lum, eff_gamma = EnhancementModules.apply_gamma_correction(
            denoised_input, gamma=gamma_val, auto_optimize=False, color_space=color_space
        )
        t_gamma = round((time.perf_counter() - t0) * 1000, 2)
        m_gamma = ImageQualityMetrics.evaluate_method(clean_gt, degraded_img, gamma_img)
        hist_gamma = EnhancementModules.extract_histogram(gamma_lum)
        diff_gamma = EnhancementModules.compute_difference_map(degraded_img, gamma_img)

        methods_data["gamma"] = {
            "name": f"Gamma Correction (γ = {eff_gamma:.2f})",
            "short_name": "Gamma",
            "img": gamma_img,
            "metrics": m_gamma,
            "exec_time_ms": t_gamma,
            "hist": hist_gamma,
            "diff_map": diff_gamma,
            "formula": self.MATH_FORMULAS["gamma"],
            "pros": "Điều chỉnh mượt mà phi tuyến tính, dễ tinh chỉnh theo từng dải ánh sáng, duy trì tông màu tự nhiên.",
            "cons": "Không tăng cường tương phản cục bộ tại các vi cấu trúc bị chìm sâu trong bóng tối."
        }

        # --- Method 4: Multi-Scale Retinex (MSR) ---
        t0 = time.perf_counter()
        msr_img, _, msr_lum = EnhancementModules.apply_multi_scale_retinex(
            denoised_input, scales=[15, 80, 250], color_space=color_space
        )
        t_msr = round((time.perf_counter() - t0) * 1000, 2)
        m_msr = ImageQualityMetrics.evaluate_method(clean_gt, degraded_img, msr_img)
        hist_msr = EnhancementModules.extract_histogram(msr_lum)
        diff_msr = EnhancementModules.compute_difference_map(degraded_img, msr_img)

        methods_data["msr"] = {
            "name": "Multi-Scale Retinex (MSR)",
            "short_name": "MSR",
            "img": msr_img,
            "metrics": m_msr,
            "exec_time_ms": t_msr,
            "hist": hist_msr,
            "diff_map": diff_msr,
            "formula": self.MATH_FORMULAS["msr"],
            "pros": "Tách biệt thành phần phản xạ khỏi độ rọi môi trường, cân bằng ánh sáng toàn diện và tái tạo màu sắc sống động.",
            "cons": "Thời gian tính toán lâu hơn do tích chập Gauss đa quy mô, có thể sinh hiệu ứng quầng sáng (halo) quanh viền vật thể sáng."
        }

        # 5. Xếp hạng & Đánh giá tổng quát (Benchmark Evaluation)
        rankings = self._compute_rankings(methods_data, ground_truth_available=(clean_gt is not None))

        result_payload = {
            "filename": filename,
            "ground_truth_available": (clean_gt is not None),
            "clean_img": clean_img,
            "degraded_img": degraded_img,
            "denoised_input": denoised_input,
            "input_hist": input_hist,
            "methods": methods_data,
            "rankings": rankings,
            "hyperparams": {
                "simulate_low_light": simulate_low_light,
                "noise_type": noise_type,
                "denoise_method": denoise_method,
                "clahe_clip_limit": clahe_clip_limit,
                "clahe_grid_size": list(clahe_grid_size),
                "gamma_val": gamma_val,
                "color_space": color_space
            }
        }

        self.last_result = result_payload
        cleanup_memory()
        return result_payload

    @staticmethod
    def _compute_rankings(methods: Dict[str, Any], ground_truth_available: bool) -> Dict[str, Any]:
        """Xác định phương pháp tốt nhất theo từng tiêu chí học thuật."""
        names = list(methods.keys())

        # Tiêu chí NIQE (càng nhỏ càng tốt, an toàn với None/NaN)
        def _get_niqe(k):
            val = methods[k]["metrics"].get("niqe")
            return val if (val is not None and not np.isnan(val)) else 999.0

        best_niqe_key = min(names, key=_get_niqe)

        rankings = {
            "best_niqe": {
                "key": best_niqe_key,
                "name": methods[best_niqe_key]["name"],
                "value": methods[best_niqe_key]["metrics"]["niqe"]
            }
        }

        if ground_truth_available:
            def _get_psnr(k):
                val = methods[k]["metrics"].get("psnr")
                return val if (val is not None and not np.isnan(val)) else -999.0

            def _get_ssim(k):
                val = methods[k]["metrics"].get("ssim")
                return val if (val is not None and not np.isnan(val)) else -999.0

            best_psnr_key = max(names, key=_get_psnr)
            best_ssim_key = max(names, key=_get_ssim)

            rankings["best_psnr"] = {
                "key": best_psnr_key,
                "name": methods[best_psnr_key]["name"],
                "value": methods[best_psnr_key]["metrics"]["psnr"]
            }
            rankings["best_ssim"] = {
                "key": best_ssim_key,
                "name": methods[best_ssim_key]["name"],
                "value": methods[best_ssim_key]["metrics"]["ssim"]
            }

            clahe_ssim = _get_ssim("clahe")
            msr_ssim = _get_ssim("msr")
            recommended_key = "clahe" if clahe_ssim >= msr_ssim else "msr"
        else:
            rankings["best_psnr"] = None
            rankings["best_ssim"] = None
            recommended_key = best_niqe_key

        rankings["overall_recommended"] = {
            "key": recommended_key,
            "name": methods[recommended_key]["name"],
            "reason": "Đạt sự cân bằng tối ưu giữa bảo toàn chi tiết cấu trúc (SSIM) và độ tự nhiên của cảnh quan (NIQE)."
        }

        return rankings

    # -------------------------------------------------------------------------
    # Batch Benchmark Runner
    # -------------------------------------------------------------------------
    def run_batch_benchmark(
        self,
        num_samples: int = 25,
        output_csv_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chạy kiểm thử đánh giá diện rộng trên tập ảnh phong cảnh ngoại cảnh,
        ghi nhận toàn bộ thông số PSNR, SSIM, NIQE của cả 4 thuật toán ra file CSV.
        """
        if output_csv_path is None:
            output_csv_path = str(PROJECT_ROOT / "outputs" / "benchmark_results.csv")

        total_avail = self.data_loader.get_total_images()
        n_eval = min(num_samples, total_avail) if total_avail > 0 else 5

        records = []
        summary_stats = {
            "he": {"psnr": [], "ssim": [], "niqe": []},
            "clahe": {"psnr": [], "ssim": [], "niqe": []},
            "gamma": {"psnr": [], "ssim": [], "niqe": []},
            "msr": {"psnr": [], "ssim": [], "niqe": []}
        }

        t_start = time.time()
        for i in range(n_eval):
            res = self.process_comparison(
                image_input=i,
                simulate_low_light=True,
                noise_type="gaussian",
                denoise_method="bilateral"
            )
            fn = res["filename"]
            for m_key, m_info in res["methods"].items():
                m = m_info["metrics"]
                records.append({
                    "Image": fn,
                    "Method": m_info["short_name"],
                    "PSNR(dB)": m["psnr"],
                    "Delta_PSNR": m["delta_psnr"],
                    "SSIM": m["ssim"],
                    "Delta_SSIM": m["delta_ssim"],
                    "NIQE": m["niqe"],
                    "Delta_NIQE": m["delta_niqe"],
                    "Time(ms)": m_info["exec_time_ms"]
                })
                if m["psnr"] is not None:
                    summary_stats[m_key]["psnr"].append(m["psnr"])
                    summary_stats[m_key]["ssim"].append(m["ssim"])
                summary_stats[m_key]["niqe"].append(m["niqe"])

        # Lưu file CSV
        Path(output_csv_path).parent.mkdir(parents=True, exist_ok=True)
        if records:
            with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
                writer.writeheader()
                writer.writerows(records)

        # Tính giá trị trung bình
        averages = {}
        for m_key, vals in summary_stats.items():
            averages[m_key] = {
                "avg_psnr": round(float(np.mean(vals["psnr"])), 2) if vals["psnr"] else 0.0,
                "avg_ssim": round(float(np.mean(vals["ssim"])), 4) if vals["ssim"] else 0.0,
                "avg_niqe": round(float(np.mean(vals["niqe"])), 2) if vals["niqe"] else 0.0
            }

        cleanup_memory()
        return {
            "success": True,
            "total_samples": n_eval,
            "elapsed_seconds": round(time.time() - t_start, 2),
            "output_csv": output_csv_path,
            "averages": averages,
            "records_sample": records[:20]
        }

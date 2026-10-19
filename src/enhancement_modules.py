"""
Business/Model Layer: Image Enhancement Modules
src/enhancement_modules.py - Universal XAI & 3-Tier Blueprint
Implements:
1. Standardized HSV/CIELAB Color-Space Wrappers (Prevents color distortion & hue shifts).
2. Edge-Preserving Pre-Denoising Filters (Bilateral, Non-Local Means, Median).
3. 4 Traditional Image Enhancement Algorithms:
   - Method 1: Histogram Equalization (HE & Adaptive HE).
   - Method 2: Contrast Limited Adaptive Histogram Equalization (CLAHE).
   - Method 3: Gamma Correction (with parameter exploration & auto-optimal gamma).
   - Method 4: Multi-Scale Retinex (MSR / MSRCR with dynamic range restoration).
4. Mathematical XAI Feature Extractors (Histograms, Transfer Functions, Difference Maps).
"""

from typing import Tuple, Dict, Any, Optional, List
import cv2
import numpy as np


class EnhancementModules:
    """
    Standardized suite of traditional image processing enhancement algorithms
    with color-space isolation on Luminance/Value channels.
    """

    # -------------------------------------------------------------------------
    # 1. Bộ lọc khử nhiễu tiền xử lý (Pre-Denoising Filters)
    # -------------------------------------------------------------------------
    @staticmethod
    def apply_pre_denoising(
        img_bgr: np.ndarray,
        method: str = "bilateral",
        params: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """
        Khử nhiễu trước khi tăng độ tương phản để tránh khuếch đại nhiễu hạt:
        - Bilateral Filter: Bảo tồn tối đa đường biên của phong cảnh (đồi núi, tán cây).
        - Non-Local Means: Khử nhiễu nền đồng nhất với độ mịn cao.
        - Median Filter: Triệt tiêu hoàn toàn nhiễu muối tiêu (Salt & Pepper).
        """
        params = params or {}
        m = str(method).lower().strip()

        if m in ("none", "identity", "raw"):
            return img_bgr.copy()

        elif m in ("bilateral", "bf"):
            d = int(params.get("d", 7))
            sc = float(params.get("sigma_color", 50.0))
            ss = float(params.get("sigma_space", 50.0))
            return cv2.bilateralFilter(img_bgr, d=d, sigmaColor=sc, sigmaSpace=ss)

        elif m in ("nlm", "non_local_means", "fast_nlm"):
            h = float(params.get("h", 7.0))
            tw = int(params.get("template_window_size", 7))
            sw = int(params.get("search_window_size", 21))
            return cv2.fastNlMeansDenoisingColored(
                img_bgr, None, h=h, hColor=h,
                templateWindowSize=tw, searchWindowSize=sw
            )

        elif m in ("median", "med"):
            ksize = int(params.get("ksize", 3))
            if ksize % 2 == 0:
                ksize += 1
            return cv2.medianBlur(img_bgr, ksize)

        elif m in ("gaussian", "gauss"):
            ksize = int(params.get("ksize", 5))
            if ksize % 2 == 0:
                ksize += 1
            sigma = float(params.get("sigma", 1.0))
            return cv2.GaussianBlur(img_bgr, (ksize, ksize), sigma)

        return img_bgr.copy()

    # -------------------------------------------------------------------------
    # 2. Wrapper chuẩn hóa xử lý trên kênh độ sáng (HSV / CIELAB)
    # -------------------------------------------------------------------------
    @staticmethod
    def luminance_wrapper(
        img_bgr: np.ndarray,
        enhancement_func,
        color_space: str = "HSV",
        **kwargs
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Hàm Wrapper chuẩn hóa theo yêu cầu Target:
        - Nhận ảnh BGR.
        - Chuyển đổi sang HSV (cv2.cvtColor(BGR2HSV)) hoặc LAB (cv2.cvtColor(BGR2LAB)).
        - Tách kênh: Chỉ áp dụng thuật toán tăng sáng trên kênh V (Value) hoặc L (Lightness).
        - Giữ nguyên các kênh sắc độ (H, S) hoặc (A, B) để ngăn chặn méo màu/bệt màu.
        - Ghép kênh (cv2.merge()) và chuyển ngược về BGR.

        Returns:
            Tuple[enhanced_bgr, orig_luminance, enh_luminance]
        """
        cs = color_space.upper().strip()

        if cs == "LAB":
            lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
            l_chan, a_chan, b_chan = cv2.split(lab)
            l_enhanced = enhancement_func(l_chan, **kwargs)
            l_enhanced = np.clip(l_enhanced, 0, 255).astype(np.uint8)
            merged = cv2.merge([l_enhanced, a_chan, b_chan])
            res_bgr = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
            return res_bgr, l_chan, l_enhanced

        else:  # Mặc định HSV
            hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            h_chan, s_chan, v_chan = cv2.split(hsv)
            v_enhanced = enhancement_func(v_chan, **kwargs)
            v_enhanced = np.clip(v_enhanced, 0, 255).astype(np.uint8)
            merged = cv2.merge([h_chan, s_chan, v_enhanced])
            res_bgr = cv2.cvtColor(merged, cv2.COLOR_HSV2BGR)
            return res_bgr, v_chan, v_enhanced

    # -------------------------------------------------------------------------
    # 3. Thuật toán 1: Histogram Equalization (HE & Adaptive HE)
    # -------------------------------------------------------------------------
    @classmethod
    def apply_histogram_equalization(
        cls,
        img_bgr: np.ndarray,
        color_space: str = "HSV",
        adaptive: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Phương pháp 1: Cân bằng biểu đồ mức xám (HE):
        - HE Toàn cục: Trải đều mật độ phân phối xác suất p(r_k) khắp dải [0, 255] qua hàm CDF:
          s_k = T(r_k) = (L - 1) sum_{j=0}^k p(r_j)
        - Adaptive HE: Cân bằng cục bộ trên từng ô lưới.
        """
        def _core_he(lum_chan: np.ndarray, is_adaptive: bool = False) -> np.ndarray:
            if is_adaptive:
                # AHE không giới hạn ngưỡng cắt (tương đương CLAHE với clipLimit lớn)
                ahe_obj = cv2.createCLAHE(clipLimit=40.0, tileGridSize=(8, 8))
                return ahe_obj.apply(lum_chan)
            else:
                return cv2.equalizeHist(lum_chan)

        return cls.luminance_wrapper(
            img_bgr,
            _core_he,
            color_space=color_space,
            is_adaptive=adaptive
        )

    # -------------------------------------------------------------------------
    # 4. Thuật toán 2: CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # -------------------------------------------------------------------------
    @classmethod
    def apply_clahe(
        cls,
        img_bgr: np.ndarray,
        clip_limit: float = 3.0,
        tile_grid_size: Tuple[int, int] = (8, 8),
        color_space: str = "HSV"
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Phương pháp 2: Cân bằng biểu đồ mức xám thích nghi giới hạn độ tương phản (CLAHE):
        - Chia ảnh thành lưới M x N ô cục bộ (Tiles).
        - Đặt ngưỡng cắt: N_clip = beta * N_avg để hạn chế độ dốc CDF.
        - Tái phân phối lượng pixel vượt ngưỡng đều vào 256 bin.
        - Khử đường biên ô lưới bằng nội suy song tuyến (Bilinear Interpolation).
        """
        cl = max(1.0, float(clip_limit))
        grid = (max(2, int(tile_grid_size[0])), max(2, int(tile_grid_size[1])))

        def _core_clahe(lum_chan: np.ndarray) -> np.ndarray:
            clahe_obj = cv2.createCLAHE(clipLimit=cl, tileGridSize=grid)
            return clahe_obj.apply(lum_chan)

        return cls.luminance_wrapper(
            img_bgr,
            _core_clahe,
            color_space=color_space
        )

    # -------------------------------------------------------------------------
    # 5. Thuật toán 3: Gamma Correction
    # -------------------------------------------------------------------------
    @classmethod
    def apply_gamma_correction(
        cls,
        img_bgr: np.ndarray,
        gamma: float = 0.5,
        auto_optimize: bool = False,
        color_space: str = "HSV"
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """
        Phương pháp 3: Hiệu chỉnh Gamma (Gamma Correction):
        - Chuẩn hóa I_norm = V / 255.
        - Kéo sáng vùng tối theo hàm lũy thừa phi tuyến:
          V_out = 255 * (V / 255)^gamma (với gamma < 1.0)
        - Nếu auto_optimize = True: Tự động ước lượng gamma tối ưu dựa trên độ sáng trung bình:
          gamma = log(0.5) / log(mean(V)/255 + epsilon)
        """
        # Xác định gamma thực tế
        effective_gamma = max(0.1, min(5.0, float(gamma)))

        def _core_gamma(lum_chan: np.ndarray) -> np.ndarray:
            nonlocal effective_gamma
            if auto_optimize:
                mean_val = float(np.mean(lum_chan)) / 255.0
                if mean_val > 0.01:
                    # Đưa độ sáng trung bình về ngưỡng 0.5
                    effective_gamma = float(np.log(0.5) / np.log(mean_val + 1e-6))
                    effective_gamma = max(0.2, min(1.5, effective_gamma))

            # Bảng tra Lookup Table (LUT) để tối ưu tốc độ tính toán
            inv_gamma = effective_gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
            return cv2.LUT(lum_chan, table)

        res_bgr, orig_lum, enh_lum = cls.luminance_wrapper(
            img_bgr,
            _core_gamma,
            color_space=color_space
        )
        return res_bgr, orig_lum, enh_lum, effective_gamma

    # -------------------------------------------------------------------------
    # 6. Thuật toán 4: Multi-Scale Retinex (MSR / MSRCR)
    # -------------------------------------------------------------------------
    @classmethod
    def apply_multi_scale_retinex(
        cls,
        img_bgr: np.ndarray,
        scales: Optional[List[int]] = None,
        weights: Optional[List[float]] = None,
        dynamic_clip_percentile: float = 1.0,
        color_space: str = "HSV"
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Phương pháp 4: Multi-Scale Retinex (MSR) trên kênh độ sáng:
        Lý thuyết Retinex của Edwin Land: I(x, y) = R(x, y) * L(x, y)
        - SSR: R_k(x, y) = log(I) - log(I * G_k) với G_k là bộ lọc Gaussian tại quy mô sigma_k.
        - MSR: R_MSR = sum_{k=1}^K w_k * [log(I) - log(I * G_k)] (với scales: 15, 80, 250).
        - Co giãn dải động (Dynamic range clipping & normalization) về [0, 255].
        Khi áp dụng trên kênh V (hoặc L), khắc phục hoàn toàn nhược điểm lệch màu xám xịt của MSR truyền thống.
        """
        scales = scales or [15, 80, 250]
        if weights is None:
            weights = [1.0 / len(scales)] * len(scales)

        def _core_msr(lum_chan: np.ndarray) -> np.ndarray:
            lum_float = lum_chan.astype(np.float32) + 1.0  # Tránh log(0)
            log_i = np.log(lum_float)
            msr_acc = np.zeros_like(log_i, dtype=np.float32)

            for s, w in zip(scales, weights):
                # Làm mờ Gauss đại diện cho thành phần độ rọi Illumination
                blurred = cv2.GaussianBlur(lum_float, (0, 0), float(s))
                blurred = np.maximum(blurred, 1.0)
                log_blurred = np.log(blurred)
                msr_acc += float(w) * (log_i - log_blurred)

            # Co giãn dải động (Dynamic Range Clipping) dựa trên phân vị
            p_low = np.percentile(msr_acc, dynamic_clip_percentile)
            p_high = np.percentile(msr_acc, 100.0 - dynamic_clip_percentile)

            if p_high - p_low < 1e-5:
                clipped = msr_acc - p_low
            else:
                clipped = (msr_acc - p_low) / (p_high - p_low) * 255.0

            return np.clip(clipped, 0, 255).astype(np.uint8)

        return cls.luminance_wrapper(
            img_bgr,
            _core_msr,
            color_space=color_space
        )

    # -------------------------------------------------------------------------
    # 7. Trích xuất đặc trưng toán học XAI (Feature Extractors)
    # -------------------------------------------------------------------------
    @staticmethod
    def extract_histogram(channel: np.ndarray) -> List[int]:
        """Trích xuất 256 bin tần suất mức xám của kênh ảnh."""
        hist = cv2.calcHist([channel], [0], None, [256], [0, 256]).flatten()
        return hist.astype(int).tolist()

    @staticmethod
    def compute_difference_map(img1_bgr: np.ndarray, img2_bgr: np.ndarray) -> np.ndarray:
        """
        Tính bản đồ nhiệt độ lệch (Difference Heatmap) trực quan hóa mức độ
        kéo sáng và khôi phục chi tiết giữa ảnh trước và sau xử lý.
        """
        g1 = cv2.cvtColor(img1_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        g2 = cv2.cvtColor(img2_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)

        # Lấy giá trị tuyệt đối độ lệch sáng
        diff = np.abs(g2 - g1)
        diff_norm = np.clip((diff / 255.0) * 255.0, 0, 255).astype(np.uint8)

        # Áp dụng bảng màu nhiệt COLORMAP_JET hoặc COLORMAP_INFERNO
        heatmap = cv2.applyColorMap(diff_norm, cv2.COLORMAP_JET)
        return heatmap

"""
Data Layer: Dataset Loader & Degradation Simulator
src/data_loader.py - Universal XAI & 3-Tier Blueprint
Handles:
1. Reading outdoor landscape dataset using OpenCV.
2. Handling edge cases (extremely dark images, dimensional variations, corrupted bytes).
3. Realistic Low-Light Simulation (Luminance scaling + Non-linear gamma darkening).
4. Academic Synthetic Noise Injection (Gaussian, Salt & Pepper, Poisson, Speckle).
"""

import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
import cv2
import numpy as np


class DataLoader:
    """
    Standardized Image Data Layer for outdoor landscape datasets.
    """

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    def __init__(self, dataset_dir: str):
        self.dataset_dir = Path(dataset_dir)
        self.image_paths: List[Path] = []
        self._scan_dataset()

    @staticmethod
    def _read_image_safe(img_path: Path) -> Optional[np.ndarray]:
        """Đọc ảnh an toàn 100% trên Windows kể cả khi đường dẫn chứa tiếng Việt có dấu."""
        try:
            path_str = str(img_path.resolve())
            data = np.fromfile(path_str, dtype=np.uint8)
            if data.size > 0:
                img = cv2.imdecode(data, cv2.IMREAD_COLOR)
                if img is not None and img.size > 0:
                    return img
        except Exception:
            pass
        try:
            return cv2.imread(str(img_path), cv2.IMREAD_COLOR)
        except Exception:
            return None

    def _scan_dataset(self) -> None:
        """Quét toàn bộ tập ảnh trong thư mục chỉ định và các thư mục dự phòng."""
        search_dirs = [self.dataset_dir]
        # Thêm các thư mục dự phòng nếu dataset_dir rỗng
        project_root = Path(__file__).resolve().parent.parent
        search_dirs.extend([
            project_root / "dataset",
            project_root / "AlgorithmCode" / "data",
            project_root / "data"
        ])

        for d in search_dirs:
            if not d.exists() or not d.is_dir():
                continue
            for ext in self.ALLOWED_EXTENSIONS:
                self.image_paths.extend(d.glob(f"*{ext}"))
                self.image_paths.extend(d.glob(f"*{ext.upper()}"))
            if not self.image_paths:
                for ext in self.ALLOWED_EXTENSIONS:
                    self.image_paths.extend(d.rglob(f"*{ext}"))
            if self.image_paths:
                break

        # Sắp xếp để giữ thứ tự ổn định
        self.image_paths = sorted(list(set(self.image_paths)))

    def get_total_images(self) -> int:
        return len(self.image_paths)

    def load_image(
        self,
        image_input: Any,
        target_max_size: int = 1024
    ) -> Tuple[np.ndarray, str]:
        """
        Nạp ảnh và xử lý 3 trường hợp biên (Edge Cases):
        - Case 1: Tệp lỗi hoặc không tồn tại -> Tạo ảnh mẫu phong cảnh nhân tạo dự phòng.
        - Case 2: Kích thước quá lớn -> Tự động scale tỉ lệ giữ nguyên aspect ratio để tối ưu bộ nhớ.
        - Case 3: Ảnh đơn sắc hoặc kênh alpha -> Chuẩn hóa về không gian 3 kênh BGR tiêu chuẩn.
        """
        img: Optional[np.ndarray] = None
        filename = "sample.png"

        if isinstance(image_input, int):
            if self.image_paths:
                idx = image_input % len(self.image_paths)
                path = self.image_paths[idx]
                filename = path.name
                img = self._read_image_safe(path)
        elif isinstance(image_input, np.ndarray):
            if image_input.size > 0:
                img = image_input.copy()
                filename = "custom_input.png"
        elif isinstance(image_input, (str, Path)):
            p = Path(image_input)
            if p.exists() and p.is_file():
                filename = p.name
                img = self._read_image_safe(p)


        # Edge Case 1: Nếu ảnh không đọc được, sinh ảnh tổng hợp phong cảnh mẫu
        if img is None or img.size == 0:
            filename = "synthetic_landscape.png"
            img = self._generate_synthetic_landscape()


        # Edge Case 2: Chuẩn hóa số kênh về 3 kênh BGR
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Edge Case 3: Resize nếu vượt quá target_max_size để tăng tốc xử lý và tránh tràn RAM
        h, w = img.shape[:2]
        if max(h, w) > target_max_size:
            scale = target_max_size / max(h, w)
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        return img, filename

    @staticmethod
    def _generate_synthetic_landscape() -> np.ndarray:
        """Tạo ảnh phong cảnh nhân tạo dự phòng khi chưa tải được dataset."""
        h, w = 512, 512
        img = np.zeros((h, w, 3), dtype=np.uint8)
        # Gradient bầu trời
        for y in range(h // 2):
            b = int(120 + 80 * (y / (h / 2)))
            g = int(80 + 60 * (y / (h / 2)))
            r = int(40 + 40 * (y / (h / 2)))
            img[y, :] = [b, g, r]
        # Mặt đất & ngọn đồi
        for x in range(w):
            mountain_y = int(h * 0.4 + 40 * np.sin(x * 0.02) + 20 * np.sin(x * 0.05))
            img[mountain_y:h // 2, x] = [40, 70, 30]
        # Thung lũng
        for y in range(h // 2, h):
            ratio = (y - h // 2) / (h // 2)
            img[y, :] = [int(30 * (1 - ratio)), int(110 * (1 - 0.4 * ratio)), int(40 * (1 - ratio))]
        return img

    # -------------------------------------------------------------------------
    # Mô phỏng môi trường thiếu sáng (Low-Light Degradation Pipeline)
    # -------------------------------------------------------------------------
    @staticmethod
    def simulate_low_light(
        img_bgr: np.ndarray,
        brightness_factor: float = 0.35,
        gamma_darkening: float = 2.2
    ) -> np.ndarray:
        """
        Mô phỏng ảnh chụp phong cảnh trong điều kiện thiếu sáng ban đêm:
        1. Giảm cường độ sáng tuyến tính theo tỷ lệ brightness_factor (0.1 - 0.6).
        2. Nén phi tuyến theo hàm Gamma tối: I_dark = I^gamma (gamma > 1) để các vùng bóng râm
           và bầu trời đêm chìm sâu vào dải tối như cảm biến ISO thấp.
        """
        img_float = img_bgr.astype(np.float32) / 255.0

        # Áp dụng gamma darkening phi tuyến
        darkened = np.power(img_float, gamma_darkening)

        # Scale thêm hệ số độ chói
        darkened = darkened * brightness_factor

        # Đưa về [0, 255] uint8
        res = np.clip(darkened * 255.0, 0, 255).astype(np.uint8)
        return res

    # -------------------------------------------------------------------------
    # Mô phỏng nhiễu học thuật (Synthetic Noise Injection)
    # -------------------------------------------------------------------------
    @staticmethod
    def apply_noise(
        img_bgr: np.ndarray,
        noise_type: str = "gaussian",
        params: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """
        Bơm nhiễu nhân tạo vào ảnh để kiểm thử năng lực khử nhiễu của thuật toán:
        - Gaussian: Nhiễu cộng phân phối chuẩn N(0, sigma^2).
        - Salt & Pepper: Nhiễu xung cực đại (255) và cực tiểu (0).
        - Poisson: Nhiễu lượng tử ánh sáng (Photon shot noise - đặc trưng thiếu sáng).
        - Speckle: Nhiễu nhân dạng đốm I * (1 + N(0, var)).
        """
        params = params or {}
        n_type = str(noise_type).lower().strip()

        if n_type in ("none", "clean"):
            return img_bgr.copy()

        elif n_type in ("gaussian", "gauss"):
            sigma = float(params.get("sigma", 15.0))
            noise = np.random.normal(0, sigma, img_bgr.shape)
            noisy = img_bgr.astype(np.float32) + noise
            return np.clip(noisy, 0, 255).astype(np.uint8)

        elif n_type in ("salt_and_pepper", "sp", "salt_pepper"):
            amount = float(params.get("amount", 0.02))
            s_vs_p = float(params.get("s_vs_p", 0.5))
            noisy = img_bgr.copy()

            # Salt (255)
            num_salt = int(np.ceil(amount * img_bgr.size * s_vs_p / 3))
            coords_salt = [np.random.randint(0, i, num_salt) for i in img_bgr.shape[:2]]
            noisy[tuple(coords_salt)] = 255

            # Pepper (0)
            num_pepper = int(np.ceil(amount * img_bgr.size * (1.0 - s_vs_p) / 3))
            coords_pepper = [np.random.randint(0, i, num_pepper) for i in img_bgr.shape[:2]]
            noisy[tuple(coords_pepper)] = 0
            return noisy

        elif n_type in ("poisson", "shot"):
            # Poisson Noise (Photon noise)
            vals = len(np.unique(img_bgr))
            vals = 2 ** np.ceil(np.log2(vals)) if vals > 0 else 256
            noisy = np.random.poisson(img_bgr.astype(np.float32) * vals / 255.0) / (vals / 255.0)
            return np.clip(noisy, 0, 255).astype(np.uint8)

        elif n_type in ("speckle", "multiplicative"):
            var = float(params.get("var", 0.04))
            noise = np.random.normal(0, np.sqrt(var), img_bgr.shape)
            noisy = img_bgr.astype(np.float32) * (1.0 + noise)
            return np.clip(noisy, 0, 255).astype(np.uint8)

        else:
            return img_bgr.copy()

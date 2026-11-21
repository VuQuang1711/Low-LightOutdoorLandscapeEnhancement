"""
Data Layer: Configuration Manager
src/config.py - Universal XAI & 3-Tier Blueprint
Loads and manages configuration parameters for the application.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class AppConfig:
    """
    Centralized configuration manager supporting YAML files with fallback defaults.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        if config_path is None:
            config_path = PROJECT_ROOT / "config" / "config.yaml"

        self.config_path = Path(config_path)
        if not self.config_path.is_absolute():
            self.config_path = PROJECT_ROOT / self.config_path
        self.config_path = self.config_path.resolve()
        self.raw_data: Dict[str, Any] = self._load_yaml()

    def _load_yaml(self) -> Dict[str, Any]:
        if self.config_path.is_file():
            try:
                with self.config_path.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        return data
            except (OSError, yaml.YAMLError) as e:
                print(f"[Warning] Failed to parse config file: {e}. Using default settings.")
        return {}

    # App Properties
    @property
    def app_name(self) -> str:
        return self.raw_data.get("app", {}).get("name", "Ứng Dụng So Sánh Nghiên cứu kỹ thuật xử lý ảnh")

    @property
    def english_title(self) -> str:
        return self.raw_data.get("app", {}).get("english_title", "A Comparative Study of Traditional Image Processing Techniques in Enhancing Low-Light Outdoor Landscape Images")

    @property
    def app_version(self) -> str:
        return self.raw_data.get("app", {}).get("version", "1.0.0")

    @property
    def host(self) -> str:
        return self.raw_data.get("app", {}).get("host", "127.0.0.1")

    @property
    def port(self) -> int:
        return int(self.raw_data.get("app", {}).get("port", 8501))

    # Dataset Directory
    def get_dataset_dir(self) -> Path:
        """Tự động tìm kiếm thư mục dataset khả dụng nhất."""
        dataset_config = self.raw_data.get("dataset", {})
        candidates = [
            Path(dataset_config.get("primary_dir", "dataset/dataset")),
            Path(dataset_config.get("fallback_dir", "dataset")),
            Path("AlgorithmCode/data"),
            Path("data"),
            Path("../AlgorithmCode/data"),
            Path("../dataset"),
        ]

        valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        for c in candidates:
            cand_p = c if c.is_absolute() else (PROJECT_ROOT / c).resolve()
            if cand_p.is_dir():
                # Kiểm tra xem thư mục có chứa ảnh không
                try:
                    for f in cand_p.iterdir():
                        if f.is_file() and f.suffix.lower() in valid_exts:
                            return cand_p
                except Exception:
                    pass

        # Nếu không có thư mục nào có ảnh, trả về thư mục dataset mặc định
        default_dir = PROJECT_ROOT / "dataset"
        default_dir.mkdir(parents=True, exist_ok=True)
        return default_dir


    # Low light parameters
    @property
    def low_light_enabled(self) -> bool:
        return bool(self.raw_data.get("low_light_simulation", {}).get("enabled", True))

    @property
    def low_light_brightness(self) -> float:
        return float(self.raw_data.get("low_light_simulation", {}).get("brightness_factor", 0.35))

    @property
    def low_light_gamma(self) -> float:
        return float(self.raw_data.get("low_light_simulation", {}).get("gamma_darkening", 2.2))

    # Noise parameters
    @property
    def noise_default_type(self) -> str:
        return str(self.raw_data.get("noise_simulation", {}).get("default_type", "gaussian"))

    @property
    def noise_gaussian_sigma(self) -> float:
        return float(self.raw_data.get("noise_simulation", {}).get("gaussian_sigma", 15.0))

    @property
    def noise_sp_amount(self) -> float:
        return float(self.raw_data.get("noise_simulation", {}).get("sp_amount", 0.02))

    @property
    def noise_speckle_var(self) -> float:
        return float(self.raw_data.get("noise_simulation", {}).get("speckle_var", 0.04))

    # Pre-denoising parameters
    @property
    def denoise_default_method(self) -> str:
        return str(self.raw_data.get("pre_denoising", {}).get("default_method", "bilateral"))

    @property
    def denoise_bilateral(self) -> Dict[str, Any]:
        return dict(self.raw_data.get("pre_denoising", {}).get(
            "bilateral", {"d": 7, "sigma_color": 50.0, "sigma_space": 50.0}
        ))

    @property
    def denoise_nlm(self) -> Dict[str, Any]:
        return dict(self.raw_data.get("pre_denoising", {}).get(
            "nlm", {"h": 7.0, "template_window_size": 7, "search_window_size": 21}
        ))

    @property
    def denoise_median(self) -> Dict[str, Any]:
        return dict(self.raw_data.get("pre_denoising", {}).get("median", {"ksize": 3}))

    # Algorithms defaults
    @property
    def color_space(self) -> str:
        return self.raw_data.get("algorithms", {}).get("color_space", "HSV")

    @property
    def he_type(self) -> str:
        return str(self.raw_data.get("algorithms", {}).get("histogram_equalization", {}).get("type", "global"))

    @property
    def clahe_clip_limit(self) -> float:
        return float(self.raw_data.get("algorithms", {}).get("clahe", {}).get("clip_limit", 3.0))

    @property
    def clahe_tile_grid_size(self) -> List[int]:
        return self.raw_data.get("algorithms", {}).get("clahe", {}).get("tile_grid_size", [8, 8])

    @property
    def gamma_default(self) -> float:
        return float(self.raw_data.get("algorithms", {}).get("gamma_correction", {}).get("gamma", 0.5))

    @property
    def gamma_auto_optimize(self) -> bool:
        return bool(self.raw_data.get("algorithms", {}).get("gamma_correction", {}).get("auto_optimize", False))

    @property
    def retinex_scales(self) -> List[int]:
        return self.raw_data.get("algorithms", {}).get("retinex", {}).get("scales", [15, 80, 250])

    @property
    def retinex_weights(self) -> List[float]:
        return self.raw_data.get("algorithms", {}).get("retinex", {}).get("weights", [1.0 / 3, 1.0 / 3, 1.0 / 3])

    @property
    def retinex_dynamic_clipping(self) -> float:
        return float(self.raw_data.get("algorithms", {}).get("retinex", {}).get("dynamic_clipping_percentile", 1.0))

"""
Business/Model Layer: Resource & Memory Manager
src/resource_manager.py - Universal XAI & 3-Tier Blueprint
Implements memory cleanup and system shutdown utilities to prevent memory leaks
when operating on massive image datasets (90,000 images, 1024x1024).
"""

import os
import gc
import shutil
from pathlib import Path
from typing import Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def cleanup_memory() -> None:
    """
    Thu hồi bộ nhớ định kỳ sau mỗi lần render đồ thị hoặc xử lý ảnh:
    - Đóng tất cả figure matplotlib còn mở (`plt.close('all')`)
    - Kích hoạt Garbage Collector giải phóng RAM (`gc.collect()`)
    """
    try:
        plt.close("all")
    except Exception:
        pass
    gc.collect()


def shutdown_resources(temp_dir: Optional[Path] = None) -> None:
    """
    Giải phóng toàn diện tài nguyên hệ thống khi tắt ứng dụng hoặc hoàn thành batch:
    - Đóng toàn bộ socket và đồ thị matplotlib
    - Dọn dẹp các tệp tải lên tạm thời trong thư mục outputs
    - Ép thu gom rác bộ nhớ RAM
    """
    cleanup_memory()

    if temp_dir is None:
        temp_dir = PROJECT_ROOT / "outputs"

    if temp_dir.exists():
        temp_file = temp_dir / "temp_web_upload.png"
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception:
                pass

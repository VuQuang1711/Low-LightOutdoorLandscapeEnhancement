#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động kiểm tra và cài đặt toàn bộ thư viện cần thiết cho AlgorithmCode.
Chạy bằng lệnh: py install_requirements.py
"""

import sys
import subprocess
import importlib

# Cấu hình UTF-8 cho console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_PACKAGES = [
    {"import_name": "cv2", "pip_name": "opencv-python", "desc": "Xử lý ảnh số OpenCV (cv2, Bilateral Filter, HSV, CLAHE)"},
    {"import_name": "numpy", "pip_name": "numpy", "desc": "Tính toán mảng nhiều chiều & Lookup Table (LUT)"},
    {"import_name": "skimage", "pip_name": "scikit-image", "desc": "Đo lường chỉ số học thuật SSIM (Structural Similarity)"},
    {"import_name": "scipy", "pip_name": "scipy", "desc": "Khoa học tính toán và tối ưu"},
    {"import_name": "matplotlib", "pip_name": "matplotlib", "desc": "Vẽ biểu đồ và xuất ảnh ghép so sánh 6 ô trực quan"},
]

def check_and_install():
    print("=" * 80)
    print("  KIỂM TRA VÀ CÀI ĐẶT THƯ VIỆN PYTHON CHO ALGORITHM CODE")
    print(f"  Python executable: {sys.executable}")
    print(f"  Python version   : {sys.version.split()[0]}")
    print("=" * 80)

    missing = []
    print("\n[1/2] Đang kiểm tra trạng thái các thư viện hiện tại:")
    for pkg in REQUIRED_PACKAGES:
        try:
            mod = importlib.import_module(pkg["import_name"])
            version = getattr(mod, "__version__", "Đã cài đặt")
            print(f"  [✓] {pkg['pip_name']:<18} : v{version:<10} ({pkg['desc']})")
        except ImportError:
            print(f"  [✗] {pkg['pip_name']:<18} : CHƯA CÀI ĐẶT  ({pkg['desc']})")
            missing.append(pkg["pip_name"])

    if not missing:
        print("\n" + "=" * 80)
        print("  Mọi thư viện cần thiết đều đã được cài đặt đầy đủ.")
        print("  Bạn có thể chạy ngay các thuật toán:")
        print("    py all_algorithms.py")
        print("    py 01_histogram_equalization.py")
        print("    py 02_clahe.py")
        print("    py 03_gamma_correction.py")
        print("    py 04_multi_scale_retinex.py")
        print("=" * 80)
        return

    print(f"\n[2/2] Phát hiện {len(missing)} thư viện còn thiếu. Đang tiến hành cài đặt qua pip...")
    cmd = [sys.executable, "-m", "pip", "install"] + missing
    print(f"  Thực thi: {' '.join(cmd)}\n")
    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 80)
        print("  [THÀNH CÔNG] Đã hoàn tất cài đặt toàn bộ thư viện!")
        print("=" * 80)
    except subprocess.CalledProcessError as e:
        print(f"\n[LỖI] Cài đặt thất bại với mã lỗi {e.returncode}. Vui lòng kiểm tra lại kết nối mạng.")

if __name__ == "__main__":
    check_and_install()

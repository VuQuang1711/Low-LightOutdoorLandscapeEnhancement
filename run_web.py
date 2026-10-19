"""
===================================================================================
File: run_web.py (Điểm khởi chạy ứng dụng Web Dashboard)
Tên Ứng Dụng: "Ứng Dụng So Sánh Nghiên cứu kỹ thuật xử lý ảnh"
Cách chạy nhanh:
    py run_web.py
===================================================================================
"""

import sys
import os
import threading
import webbrowser
from pathlib import Path

# Đảm bảo Project Root nằm trong sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Thiết lập encoding UTF-8 cho Windows Terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def is_port_available(host: str, port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def get_available_port(host: str, start_port: int, max_tries: int = 15) -> int:
    for p in range(start_port, start_port + max_tries):
        if is_port_available(host, p):
            return p
    return start_port


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Chạy Ứng Dụng So Sánh Nghiên cứu kỹ thuật xử lý ảnh")
    parser.add_argument("--port", type=int, default=8501, help="Cổng mạng (mặc định 8501)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Địa chỉ host (mặc định 127.0.0.1)")
    parser.add_argument("--no-browser", action="store_true", help="Không tự động mở trình duyệt")
    args = parser.parse_args()

    target_port = args.port
    if not is_port_available(args.host, target_port):
        alt_port = get_available_port(args.host, target_port + 1)
        print("!" * 80)
        print(f"  ⚠️ CẢNH BÁO: Cổng {target_port} đang bận (tiến trình trước chưa giải phóng hoặc đang chạy nền).")
        print(f"  👉 Hệ thống tự động chuyển sang cổng khả dụng: {alt_port}")
        print("!" * 80)
        target_port = alt_port

    url = f"http://{args.host}:{target_port}"

    print("=" * 80)
    print("  🔬 ỨNG DỤNG SO SÁNH NGHIÊN CỨU KỸ THUẬT XỬ LÝ ẢNH")
    print("  (A Comparative Study on Low-Light Outdoor Landscape Enhancement)")
    print("=" * 80)
    print(f"  • Chế độ: Modern Web Dashboard (HTML5 / CSS3 / JavaScript + FastAPI)")
    print(f"  • Thuật toán: HE, CLAHE, Gamma Correction, Multi-Scale Retinex (MSR)")
    print(f"  • Địa chỉ truy cập: {url}")
    print(f"  • Nhấn Ctrl + C trong Terminal để dừng máy chủ")
    print("=" * 80)

    if not args.no_browser:
        def open_browser():
            import time
            import urllib.request
            # Đợi máy chủ thực sự khởi động xong và phản hồi API trước khi mở trình duyệt
            for _ in range(30):
                time.sleep(0.4)
                try:
                    with urllib.request.urlopen(f"{url}/api/status", timeout=1):
                        break
                except Exception:
                    pass
            webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()

    from src.web_server import launch_web_server
    launch_web_server(host=args.host, port=target_port)


if __name__ == "__main__":
    main()

"""
Presentation Layer: FastAPI Web Server
src/web_server.py - Universal XAI & 3-Tier Blueprint
Serves the modern interactive HTML5/CSS3/JavaScript web interface and REST APIs.
"""

import sys
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.model_logic import ImageEnhancementComparisonPipeline
from src.config import AppConfig

app = FastAPI(
    title="Ứng Dụng So Sánh Nghiên cứu kỹ thuật xử lý ảnh",
    description="A Comparative Study of Traditional Image Processing Techniques in Enhancing Low-Light Outdoor Landscape Images",
    version="1.0.0"
)

# Kích hoạt CORS cho môi trường phát triển cục bộ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo Pipeline tầng nghiệp vụ
config = AppConfig()
pipeline = ImageEnhancementComparisonPipeline(config)


def cv2_to_b64(img_bgr: np.ndarray, quality: int = 88) -> str:
    """Mã hóa ảnh OpenCV BGR thành chuỗi Base64 JPEG để truyền qua Web."""
    if img_bgr is None or img_bgr.size == 0:
        return ""
    success, buffer = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not success:
        return ""
    encoded = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


class ProcessRequest(BaseModel):
    image_idx: int = 0
    custom_file_b64: Optional[str] = None
    simulate_low_light: bool = True
    brightness_factor: float = 0.35
    gamma_darkening: float = 2.2
    noise_type: str = "gaussian"
    noise_sigma: float = 15.0
    denoise_method: str = "bilateral"
    clahe_clip_limit: float = 3.0
    clahe_grid_size: List[int] = [8, 8]
    gamma_val: float = 0.5
    color_space: str = "HSV"


@app.get("/api/status")
async def get_status():
    """Trả về trạng thái hệ thống, cấu hình và tổng số ảnh trong Dataset."""
    total_imgs = pipeline.data_loader.get_total_images()
    return {
        "status": "ready",
        "app_name": config.app_name,
        "english_title": config.english_title,
        "total_images": total_imgs,
        "dataset_dir": str(pipeline.config.get_dataset_dir()),
        "version": pipeline.VERSION
    }


@app.post("/api/process")
def process_image(req: ProcessRequest):
    """
    Thực thi quy trình so sánh đồng thời 4 thuật toán trên ảnh đầu vào,
    trả về toàn bộ ảnh base64, biểu đồ phân phối và bảng điểm số IQA.
    Chạy trong threadpool của FastAPI để không làm nghẽn Event Loop.
    """
    try:
        if req.custom_file_b64:
            # Giải mã ảnh tải lên từ máy người dùng an toàn (hỗ trợ cả data URI và raw base64)
            try:
                b64_str = req.custom_file_b64
                if "," in b64_str:
                    _, b64_str = b64_str.split(",", 1)
                file_bytes = np.frombuffer(base64.b64decode(b64_str), dtype=np.uint8)
                custom_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                if custom_img is not None and custom_img.size > 0:
                    img_input = custom_img
                else:
                    img_input = req.image_idx
            except Exception:
                img_input = req.image_idx
        else:
            img_input = req.image_idx


        # Chạy Pipeline
        res = pipeline.process_comparison(
            image_input=img_input,
            simulate_low_light=req.simulate_low_light,
            brightness_factor=req.brightness_factor,
            gamma_darkening=req.gamma_darkening,
            noise_type=req.noise_type,
            noise_params={"sigma": req.noise_sigma, "amount": 0.02},
            denoise_method=req.denoise_method,
            clahe_clip_limit=req.clahe_clip_limit,
            clahe_grid_size=(req.clahe_grid_size[0], req.clahe_grid_size[1]),
            gamma_val=req.gamma_val,
            color_space=req.color_space
        )

        # Chuyển đổi dữ liệu 4 phương pháp sang base64
        serialized_methods = {}
        for m_key, m_val in res["methods"].items():
            serialized_methods[m_key] = {
                "name": m_val["name"],
                "short_name": m_val["short_name"],
                "img_b64": cv2_to_b64(m_val["img"]),
                "diff_map_b64": cv2_to_b64(m_val["diff_map"]),
                "metrics": m_val["metrics"],
                "exec_time_ms": m_val["exec_time_ms"],
                "hist": m_val["hist"],
                "formula": m_val["formula"],
                "pros": m_val["pros"],
                "cons": m_val["cons"]
            }

        return {
            "success": True,
            "filename": res["filename"],
            "ground_truth_available": res["ground_truth_available"],
            "clean_img_b64": cv2_to_b64(res["clean_img"]),
            "degraded_img_b64": cv2_to_b64(res["degraded_img"]),
            "denoised_input_b64": cv2_to_b64(res["denoised_input"]),
            "input_hist": res["input_hist"],
            "methods": serialized_methods,
            "rankings": res["rankings"],
            "hyperparams": res["hyperparams"]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch")
def run_batch(samples: int = Query(20, ge=1, le=100)):
    """Chạy benchmark hàng loạt trên tập mẫu Dataset và xuất báo cáo CSV trong worker thread."""
    try:
        batch_res = pipeline.run_batch_benchmark(num_samples=samples)
        return batch_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download_csv")
async def download_csv():
    """Tải xuống tệp CSV bảng so sánh benchmark."""
    csv_path = PROJECT_ROOT / "outputs" / "benchmark_results.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Chưa có dữ liệu benchmark. Hãy chạy Benchmark trước.")
    return FileResponse(
        str(csv_path),
        media_type="text/csv",
        filename="benchmark_results_xlas.csv"
    )


# Gắn thư mục tĩnh chứa giao diện web (HTML, CSS, JS)
WEB_DIR = PROJECT_ROOT / "web"
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


def launch_web_server(host: str = "127.0.0.1", port: int = 8501):
    """Khởi động Uvicorn Web Server."""
    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except OSError as e:
        if getattr(e, "winerror", None) == 10048 or "10048" in str(e):
            print("=" * 80)
            print(f"  ❌ [LỖI] Cổng {port} đang bị chiếm dụng bởi một tiến trình Python khác!")
            print("  👉 Bạn có thể tắt tiến trình cũ nhanh bằng lệnh PowerShell:")
            print(f"     Stop-Process -Id (Get-NetTCPConnection -LocalPort {port}).OwningProcess -Force")
            print("=" * 80)
        raise


if __name__ == "__main__":
    launch_web_server()

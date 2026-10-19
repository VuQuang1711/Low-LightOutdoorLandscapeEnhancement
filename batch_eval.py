"""
Batch Execution Pipeline: Offline Dataset Benchmark
batch_eval.py - Universal XAI & 3-Tier Blueprint
Runs automated offline comparative benchmarking across random samples from the dataset
and outputs a detailed CSV report with PSNR, SSIM, and NIQE scores for all 4 algorithms.

Usage:
    py batch_eval.py --samples 50 --output outputs/benchmark_results.csv
"""

import sys
import argparse
from pathlib import Path

# Đảm bảo Project root nằm trong sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Cấu hình UTF-8 cho Windows Terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from src.model_logic import ImageEnhancementComparisonPipeline
from src.config import AppConfig


def main():
    parser = argparse.ArgumentParser(description="Đánh giá diện rộng 4 thuật toán xử lý ảnh trên Dataset")
    parser.add_argument("--samples", type=int, default=30, help="Số lượng ảnh lấy mẫu ngẫu nhiên (mặc định: 30)")
    parser.add_argument("--output", type=str, default="outputs/benchmark_results.csv", help="Đường dẫn file CSV xuất ra")
    args = parser.parse_args()

    print("=" * 80)
    print("  🔬 BATCH BENCHMARK: SO SÁNH 4 THUẬT TOÁN XỬ LÝ ẢNH THIẾU SÁNG")
    print("=" * 80)
    print(f"  • Số lượng mẫu kiểm thử : {args.samples}")
    print(f"  • Tệp báo cáo xuất ra    : {args.output}")
    print("-" * 80)

    config = AppConfig()
    pipeline = ImageEnhancementComparisonPipeline(config)

    total_avail = pipeline.data_loader.get_total_images()
    print(f"  • Tổng số ảnh tìm thấy trong Dataset: {total_avail}")
    if total_avail == 0:
        print("  [Cảnh báo] Dataset rỗng! Sẽ sử dụng ảnh tổng hợp giả lập để kiểm thử logic.")

    print("\n  >> Đang tiến hành chạy thử nghiệm (quá trình có thể mất từ 1-3 phút)...")
    res = pipeline.run_batch_benchmark(num_samples=args.samples, output_csv_path=args.output)

    print("\n" + "=" * 80)
    print("  🏆 KẾT QUẢ ĐÁNH GIÁ TỔNG QUAN (BENCHMARK SUMMARY)")
    print("=" * 80)
    print(f"{'Thuật toán':<25} | {'PSNR TB (dB)':<15} | {'SSIM TB':<12} | {'NIQE TB':<12}")
    print("-" * 75)

    names = {
        "he": "Histogram Equalization (HE)",
        "clahe": "CLAHE (Contrast Limited)",
        "gamma": "Gamma Correction",
        "msr": "Multi-Scale Retinex (MSR)"
    }

    for k, avg in res["averages"].items():
        print(f"{names.get(k, k):<25} | {avg['avg_psnr']:<15} | {avg['avg_ssim']:<12} | {avg['avg_niqe']:<12}")

    print("-" * 75)
    print(f"  • Thời gian hoàn thành : {res['elapsed_seconds']} giây")
    print(f"  • Báo cáo chi tiết lưu tại : {res['output_csv']}")
    print("=" * 80)


if __name__ == "__main__":
    main()

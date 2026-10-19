"""
====================================================================================================
MODULE TIỆN ÍCH HỆ THỐNG ĐƯỜNG DẪN & XỬ LÝ ẢNH AN TOÀN (PATH_UTILS)
Tự động tìm kiếm thư mục dữ liệu, hỗ trợ đường dẫn Unicode tiếng Việt,
đọc/ghi file ảnh chống lỗi tuyệt đối trên Windows/Linux/macOS khi nén và gửi bài.
====================================================================================================
"""

import os
import sys
from pathlib import Path
from typing import Tuple, List, Optional, Union

import cv2
import numpy as np


def get_script_dir() -> Path:
    """Trả về thư mục chứa script đang thực thi một cách chính xác tuyệt đối."""
    return Path(__file__).resolve().parent


def get_project_root() -> Path:
    """
    Tự động dò tìm thư mục gốc của đồ án (Project Root):
    Tìm ngược lên các thư mục cha để nhận diện các dấu hiệu nhận biết như:
    AlgorithmCode/, dataset/, src/, requirements.txt, v.v.
    """
    current = Path(__file__).resolve().parent
    for p in [current, current.parent, current.parent.parent]:
        if (p / "AlgorithmCode").is_dir() or (p / "src").is_dir() or (p / "requirements.txt").is_file():
            return p
    return current.parent


def imread_unicode(img_path: Union[str, Path], flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """
    Đọc ảnh an toàn 100% trên mọi hệ điều hành (kể cả Windows khi thư mục/tên file chứa
    tiếng Việt có dấu, khoảng trắng, hoặc ký tự Unicode đặc biệt).
    Khắc phục triệt để lỗi cv2.imread() trả về None trên Windows.
    """
    if img_path is None:
        return None

    path_obj = Path(img_path).resolve()
    path_str = str(path_obj)

    if not path_obj.exists() or not path_obj.is_file():
        return None

    try:
        # Cách 1 (Khuyên dùng trên Windows): Đọc luồng byte bằng numpy rồi imdecode
        # Không bị ảnh hưởng bởi bảng mã ANSI của Windows C runtime fopen
        data = np.fromfile(path_str, dtype=np.uint8)
        if data.size > 0:
            img = cv2.imdecode(data, flags)
            if img is not None and img.size > 0:
                return img
    except Exception:
        pass

    try:
        # Cách 2: Fallback cv2.imread thông thường
        img = cv2.imread(path_str, flags)
        if img is not None and img.size > 0:
            return img
    except Exception:
        pass

    return None


def imwrite_unicode(save_path: Union[str, Path], img: np.ndarray, ext: str = ".jpg") -> bool:
    """
    Ghi ảnh an toàn 100% trên mọi hệ điều hành:
    - Tự động tạo toàn bộ thư mục cha nếu chưa tồn tại (parents=True).
    - Hỗ trợ đường dẫn tiếng Việt có dấu và Unicode.
    """
    if img is None or img.size == 0:
        return False

    try:
        p = Path(save_path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        suffix = p.suffix if p.suffix else ext
        success, encoded = cv2.imencode(suffix, img)
        if success:
            encoded.tofile(str(p))
            return True
    except Exception:
        pass

    try:
        return cv2.imwrite(str(save_path), img)
    except Exception:
        return False


def get_candidate_data_dirs() -> List[Path]:
    """
    Tự động quét danh sách toàn bộ các thư mục có khả năng chứa dữ liệu ảnh:
    Hỗ trợ cả trường hợp:
    - Chỉ giải nén thư mục AlgorithmCode độc lập.
    - Giải nén toàn bộ thư mục Project.
    - Chạy từ VS Code, PyCharm, Command Prompt, PowerShell ở bất kỳ thư mục làm việc nào.
    """
    script_dir = get_script_dir()
    proj_root = get_project_root()
    cwd = Path.cwd().resolve()

    candidates = [
        script_dir / "data",
        script_dir / "dataset",
        script_dir / "images",
        cwd / "data",
        cwd / "dataset",
        cwd / "AlgorithmCode" / "data",
        proj_root / "AlgorithmCode" / "data",
        proj_root / "dataset" / "dataset",
        proj_root / "dataset",
        proj_root / "data",
        script_dir,  # Đề phòng ảnh để cùng thư mục script
        cwd,
    ]

    # Loại bỏ thư mục trùng lặp và giữ nguyên thứ tự ưu tiên
    unique_dirs: List[Path] = []
    seen = set()
    for d in candidates:
        try:
            d_res = d.resolve()
            if d_res not in seen and d_res.is_dir():
                seen.add(d_res)
                unique_dirs.append(d_res)
        except Exception:
            continue

    return unique_dirs


def scan_all_images(dirs: Optional[List[Path]] = None) -> List[Path]:
    """Quét toàn bộ danh sách tệp ảnh hợp lệ trong các thư mục ứng viên."""
    if dirs is None:
        dirs = get_candidate_data_dirs()

    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
    images: List[Path] = []
    seen_paths = set()

    for d in dirs:
        if not d.exists() or not d.is_dir():
            continue
        try:
            for item in d.iterdir():
                if item.is_file() and item.suffix.lower() in valid_exts:
                    res_path = item.resolve()
                    if res_path not in seen_paths:
                        seen_paths.add(res_path)
                        images.append(res_path)
        except Exception:
            continue

    # Sắp xếp theo tên file để thứ tự luôn đồng nhất
    images.sort(key=lambda p: p.name.lower())
    return images


def generate_synthetic_landscape(width: int = 512, height: int = 512) -> np.ndarray:
    """Tạo ảnh phong cảnh nhân tạo dự phòng khi hoàn toàn không có ảnh nào trong dataset."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    half = height // 2
    # Bầu trời: Gradient xanh lam hoàng hôn
    for y in range(half):
        factor = y / half
        b = int(140 + 70 * factor)
        g = int(110 + 30 * factor)
        r = int(60 + 20 * factor)
        img[y, :] = [b, g, r]
    # Dãy núi và cánh đồng xanh: Gradient tự nhiên
    for y in range(half, height):
        factor = (y - half) / (height - half)
        b = int(25 + 15 * factor)
        g = int(75 + 25 * factor)
        r = int(15 + 15 * factor)
        img[y, :] = [b, g, r]
    return img


def find_sample_image(
    prefer_name_or_idx: Optional[str] = None
) -> Tuple[Optional[str], int, str, np.ndarray]:
    """
    HÀM TỰ ĐỘNG TÌM NẠP ẢNH ĐẦU VÀO THÔNG MINH & TOÀN DIỆN:
    1. Kiểm tra trực tiếp nếu người dùng truyền vào đường dẫn file cụ thể (tuyệt đối hoặc tương đối).
    2. Nếu truyền số nguyên (chỉ số index): lấy ảnh thứ i trong dataset.
    3. Nếu truyền từ khóa: tìm ảnh có tên chứa từ khóa đó.
    4. Tự động quét tất cả các thư mục dữ liệu cục bộ và dự án.
    5. Fallback tự tạo ảnh phong cảnh nhân tạo nếu không có bất kỳ file ảnh nào trên máy.

    Returns:
        (resolved_image_path, total_images_found, source_folder_path, loaded_img_bgr)
    """
    script_dir = get_script_dir()
    cwd = Path.cwd().resolve()
    candidate_dirs = get_candidate_data_dirs()
    all_imgs = scan_all_images(candidate_dirs)

    # -------------------------------------------------------------------------
    # TRƯỜNG HỢP 1: Người dùng truyền tham số đường dẫn file cụ thể
    # -------------------------------------------------------------------------
    if prefer_name_or_idx:
        raw_input = str(prefer_name_or_idx).strip().strip('"').strip("'")
        input_path = Path(raw_input)

        # Thử các vị trí khả dĩ của file được truyền
        direct_checks = [
            input_path,
            cwd / input_path,
            script_dir / input_path,
            script_dir / "data" / input_path,
            script_dir / "data" / input_path.name,
        ]

        for check_p in direct_checks:
            try:
                resolved_check = check_p.resolve()
                if resolved_check.exists() and resolved_check.is_file():
                    img = imread_unicode(resolved_check)
                    if img is not None and img.size > 0:
                        total_cnt = max(len(all_imgs), 1)
                        return str(resolved_check), total_cnt, str(resolved_check.parent), img
            except Exception:
                continue

        # Nếu tham số là một số nguyên (index)
        if raw_input.isdigit() and all_imgs:
            idx = int(raw_input) % len(all_imgs)
            target = all_imgs[idx]
            img = imread_unicode(target)
            if img is not None and img.size > 0:
                return str(target), len(all_imgs), str(target.parent), img

        # Nếu tham số là tên hoặc một phần tên file trong dataset
        if all_imgs:
            matches = [p for p in all_imgs if raw_input.lower() in p.name.lower()]
            if matches:
                target = matches[0]
                img = imread_unicode(target)
                if img is not None and img.size > 0:
                    return str(target), len(all_imgs), str(target.parent), img

    # -------------------------------------------------------------------------
    # TRƯỜNG HỢP 2: Lấy ảnh đầu tiên tìm thấy trong các thư mục dữ liệu
    # -------------------------------------------------------------------------
    for p in all_imgs:
        img = imread_unicode(p)
        if img is not None and img.size > 0:
            return str(p), len(all_imgs), str(p.parent), img

    # -------------------------------------------------------------------------
    # TRƯỜNG HỢP 3: Dự phòng khẩn cấp - Khởi tạo ảnh phong cảnh nhân tạo
    # -------------------------------------------------------------------------
    fallback_dir = script_dir / "data"
    fallback_dir.mkdir(parents=True, exist_ok=True)
    fallback_img = generate_synthetic_landscape()
    fallback_file = fallback_dir / "00000_sample_synthetic.jpg"
    imwrite_unicode(fallback_file, fallback_img)

    return str(fallback_file), 1, str(fallback_dir), fallback_img


def get_output_dir(sub_name: str = "output_demo") -> Path:
    """Tự động tìm và tạo thư mục xuất kết quả ra file."""
    out_dir = get_script_dir() / sub_name
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

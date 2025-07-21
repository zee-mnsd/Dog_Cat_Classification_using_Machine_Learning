import os
import cv2
import numpy as np
from PIL import Image, ImageFile
import warnings
import logging
from datetime import datetime
import shutil

# Cấu hình để suppress warnings
ImageFile.LOAD_TRUNCATED_IMAGES = True
warnings.filterwarnings("ignore")
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'

# Tắt OpenCV warnings
cv2.setLogLevel(0)

def check_image_with_opencv(image_path):
    """Kiểm tra ảnh bằng OpenCV và capture stderr để detect corrupt files"""
    try:
        # Redirect stderr để capture OpenCV warnings
        import sys
        from io import StringIO

        old_stderr = sys.stderr
        sys.stderr = captured_stderr = StringIO()

        # Thử đọc ảnh
        img = cv2.imread(image_path)

        # Lấy lại stderr
        sys.stderr = old_stderr
        error_output = captured_stderr.getvalue()

        # Kiểm tra xem có corrupt warning không
        corrupt_keywords = [
            'Corrupt JPEG data',
            'extraneous bytes',
            'unknown JFIF revision',
            'Premature end of JPEG',
            'Invalid JPEG'
        ]

        is_corrupt = any(keyword in error_output for keyword in corrupt_keywords)

        if img is None:
            return False, "Cannot read image"

        if is_corrupt:
            return False, f"Corrupt JPEG detected: {error_output.strip()}"

        # Kiểm tra kích thước
        height, width = img.shape[:2]
        if height < 10 or width < 10:
            return False, "Image too small"

        return True, "OK"

    except Exception as e:
        return False, f"Exception: {str(e)}"

def check_image_with_pil(image_path):
    """Kiểm tra ảnh bằng PIL"""
    try:
        with Image.open(image_path) as img:
            img.verify()

        # Thử load lại
        with Image.open(image_path) as img:
            img.load()
            if img.size[0] < 10 or img.size[1] < 10:
                return False, "Image too small"

        return True, "OK"
    except Exception as e:
        return False, f"PIL Error: {str(e)}"

def comprehensive_image_check(image_path):
    """Kiểm tra toàn diện một file ảnh"""
    # Kiểm tra file tồn tại
    if not os.path.exists(image_path):
        return False, "File not exists"

    # Kiểm tra kích thước file
    file_size = os.path.getsize(image_path)
    if file_size < 100:  # File quá nhỏ
        return False, "File too small"

    # Kiểm tra với OpenCV
    cv_ok, cv_msg = check_image_with_opencv(image_path)

    # Kiểm tra với PIL
    pil_ok, pil_msg = check_image_with_pil(image_path)

    # Quyết định cuối cùng
    if cv_ok and pil_ok:
        return True, "Both CV and PIL OK"
    elif cv_ok and not pil_ok:
        return False, f"CV OK but PIL failed: {pil_msg}"
    elif not cv_ok and pil_ok:
        return False, f"PIL OK but CV failed: {cv_msg}"
    else:
        return False, f"Both failed - CV: {cv_msg}, PIL: {pil_msg}"

def scan_dataset(input_folder):
    """Scan toàn bộ dataset và tìm file corrupt"""

    print(f"Scanning dataset: {input_folder}")
    print("=" * 60)

    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

    total_files = 0
    valid_files = 0
    corrupt_files = []
    error_summary = {}

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                total_files += 1
                image_path = os.path.join(root, filename)

                is_valid, message = comprehensive_image_check(image_path)

                if is_valid:
                    valid_files += 1
                    if total_files % 100 == 0:  # Progress update
                        print(f"Processed {total_files} files - Current: VALID - {filename}")
                else:
                    corrupt_files.append((image_path, message))
                    print(f"CORRUPT: {image_path}")
                    print(f"  Reason: {message}")

                    # Đếm loại lỗi
                    error_type = message.split(':')[0] if ':' in message else message
                    error_summary[error_type] = error_summary.get(error_type, 0) + 1

    print("\n" + "=" * 60)
    print("SCAN SUMMARY")
    print("=" * 60)
    print(f"Total image files found: {total_files}")
    print(f"Valid files: {valid_files}")
    print(f"Corrupt files: {len(corrupt_files)}")
    print(f"Success rate: {valid_files/total_files*100:.2f}%")

    print("\nError types:")
    for error_type, count in error_summary.items():
        print(f"  {error_type}: {count} files")

    return corrupt_files, valid_files, total_files

def create_clean_dataset(input_folder, output_folder, corrupt_files):
    """Tạo dataset sạch bằng cách copy file hợp lệ"""

    print(f"\nCreating clean dataset in: {output_folder}")

    # Tạo thư mục output
    os.makedirs(output_folder, exist_ok=True)

    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    corrupt_paths = set(path for path, _ in corrupt_files)

    copied_files = 0

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                src_path = os.path.join(root, filename)

                if src_path not in corrupt_paths:
                    # Tính toán đường dẫn đích
                    rel_path = os.path.relpath(src_path, input_folder)
                    dst_path = os.path.join(output_folder, rel_path)

                    # Tạo thư mục đích nếu chưa có
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

                    # Copy file
                    shutil.copy2(src_path, dst_path)
                    copied_files += 1

    print(f"Copied {copied_files} valid files to clean dataset")

def remove_corrupt_files(corrupt_files, backup_folder=None):
    """Xóa hoặc move các file corrupt"""

    if backup_folder:
        print(f"\nMoving corrupt files to backup folder: {backup_folder}")
        os.makedirs(backup_folder, exist_ok=True)
    else:
        print(f"\nRemoving {len(corrupt_files)} corrupt files...")

    for file_path, reason in corrupt_files:
        try:
            if backup_folder:
                # Move to backup
                filename = os.path.basename(file_path)
                backup_path = os.path.join(backup_folder, filename)

                # Đảm bảo tên file unique
                counter = 1
                while os.path.exists(backup_path):
                    name, ext = os.path.splitext(filename)
                    backup_path = os.path.join(backup_folder, f"{name}_{counter}{ext}")
                    counter += 1

                shutil.move(file_path, backup_path)
                print(f"Moved: {file_path} -> {backup_path}")
            else:
                # Delete file
                os.remove(file_path)
                print(f"Deleted: {file_path}")

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

# Script chính
if __name__ == "__main__":

    # Cấu hình đường dẫn
    input_folder = "01_VENV_Machine_learning_differentiate_dogs_cats/src/Pets"  # Thay đổi theo đường dẫn thực tế
    clean_dataset_folder = "01_VENV_Machine_learning_differentiate_dogs_cats/src/petsnew"
    backup_folder = "01_VENV_Machine_learning_differentiate_dogs_cats/src/backup"

    print("Starting comprehensive image corruption check...")
    print(f"Input folder: {input_folder}")

    # Bước 1: Scan và tìm file corrupt
    corrupt_files, valid_count, total_count = scan_dataset(input_folder)

    if len(corrupt_files) > 0:
        print(f"\nFound {len(corrupt_files)} corrupt files:")
        for i, (file_path, reason) in enumerate(corrupt_files[:10]):  # Show first 10
            print(f"{i+1}. {file_path}")
            print(f"   Reason: {reason}")

        if len(corrupt_files) > 10:
            print(f"... and {len(corrupt_files) - 10} more files")

        # Hỏi user muốn làm gì
        print(f"\nOptions:")
        print("1. Create clean dataset (copy valid files to new location)")
        print("2. Move corrupt files to backup folder")
        print("3. Delete corrupt files (DANGEROUS)")
        print("4. Just show the list (do nothing)")

        choice = input("Choose option (1-4): ").strip()

        if choice == "1":
            create_clean_dataset(input_folder, clean_dataset_folder, corrupt_files)
            print(f"\nClean dataset created at: {clean_dataset_folder}")
            print("You can now use this clean dataset for training")

        elif choice == "2":
            remove_corrupt_files(corrupt_files, backup_folder)
            print(f"Corrupt files moved to: {backup_folder}")

        elif choice == "3":
            confirm = input("Are you sure you want to DELETE corrupt files? (type 'DELETE' to confirm): ")
            if confirm == "DELETE":
                remove_corrupt_files(corrupt_files)
                print("Corrupt files deleted")
            else:
                print("Operation cancelled")

        elif choice == "4":
            print("No action taken")

    else:
        print("No corrupt files found! Dataset is clean.")

    # Lưu report
    report_file = f"corruption_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(f"Image Corruption Report\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Dataset: {input_folder}\n\n")
        f.write(f"Total files: {total_count}\n")
        f.write(f"Valid files: {valid_count}\n")
        f.write(f"Corrupt files: {len(corrupt_files)}\n\n")

        f.write("Corrupt Files List:\n")
        f.write("-" * 50 + "\n")
        for file_path, reason in corrupt_files:
            f.write(f"{file_path}\n")
            f.write(f"  Reason: {reason}\n\n")

    print(f"\nDetailed report saved to: {report_file}")

import os
import torch
import torch.nn as nn
import warnings
from PIL import ImageFile
import logging
from datetime import datetime

from SafeTransform import SafeTransform
from DogCatDataset import DogCatDataset
from torch.utils.data import DataLoader
from DogCatClassifier import DogCatClassifier
from train_model import train_model
from predict_image import predict_image



# Cấu hình PIL để xử lý file ảnh bị truncated
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Tắt các warning messages thuộc loại UserWarning
warnings.filterwarnings("ignore", category=UserWarning)

# Thiết lập logging để theo dõi các file bị lỗi, có trả về file log :)
logging.basicConfig(
    filename="training.log",
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":

    #kiểm tra thiết bị sẽ chạy code là GPU hay CPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logging.info(f"Sử dụng device: {device}")

    # cấu hình batch và epochs
    batch_size = 256 # 64, 256, 512
    epochs = 20 # 10, 20, 25, 50

    # Đọc thư mục chứa data gốc
    root_folder = "/Pets"

    # Dataset and DataLoader với error handling
    try:
        print("Đang tải dataset...")

        #Transform = biến đổi/xử lý ảnh để chuẩn bị cho model deep learning.
        transform = SafeTransform()
        dataset = DogCatDataset(root_folder, transform=transform)

        if len(dataset) == 0:
            raise ValueError("Không tìm thấy ảnh hợp lệ nào trong dataset!")

        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

                # num_workers=0 để tránh lỗi => Chỉ skip file lỗi, không crash toàn bộ
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

        # creat model
        model = DogCatClassifier()
        if torch.cuda.device_count() > 1:
            model = nn.DataParallel(model)
        model.to(device)

        # train model
        print("Đang train model...")
        train_model(model, train_loader, val_loader, device, epochs)

        # save model
        model_path = f"model_resnet50_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
        torch.save(model.state_dict(), model_path)
        print(f"Model đã được lưu tại: {model_path}")

        # Kiểm tra model bằng 1 tấm ảnh ở ngoài mô hình (ảnh bất kỳ)
        test_image_path = "source/Funny_Dog_H.jpg"
        if os.path.exists(test_image_path):
            test_result, test_confidence = predict_image(test_image_path, model, device)
            print(f"Kết quả dự đoán: {test_result}, độ tin cậy: {test_confidence}")
        else:
            print(f"File test {test_image_path} không tồn tại!")

    except Exception as e:
        logging.error(f"Error during dataset loading: {str(e)}")
        print(f"Lỗi trong quá trình tải dataset: {str(e)}")

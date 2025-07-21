## Chuẩn bị dữ liệu ảnh
- Đầu tiên cần thực hiện lấy ảnh từ kho Kaggel bằng 2 shell đầu tiên trong colab.ipynb
- Đợi tải xong thì tìm xem thư mục lưu trữ ở đâu, sau đó chuyển nó về thư mục chính /content

Đảm bảo cấu trúc thư mục /content như thế này:
/content/
├── Pets/
│   ├── dogs/
│   │   ├── dog1.jpg
│   │   ├── dog2.jpg
│   │   └── ...
│   └── cats/
│       ├── cat1.jpg
│       ├── cat2.jpg
│       └── ...
└── sample_data/

### Chạy mô hình
Để chạy được thì cần chạy với GPU T4 của Colab.<br>
1. Nếu dùng bản Colab free thì cần chú ý đến GPU RAM. <br>
- Điều chỉnh batch_size = 64 tại hàm main
- Điều chỉnh epochs = 10 tại hàm main

2. Chỉnh sửa đường dẫn tại những chỗ đã chỉ định trong code (mở code ra đọc là thấy)

3. Tải model về máy, tải log về máy để xem xét!

### Note
- Hiện chưa có ghi lại log
- Hiện chưa có hàm gọi lại model sau khi training
 + Code này chỉ có:<br>torch.save(model.state_dict(), model_path) - lưu model
 <br>predict_image() - dự đoán trên model đang chạy
 + Thiếu: Hàm torch.load() để load lại model đã lưu cho lần sử dụng sau.

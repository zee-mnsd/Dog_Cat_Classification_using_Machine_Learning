## Chuẩn bị dữ liệu ảnh
- Đầu tiên tải dữ liệu ảnh và ảnh cần kiểm tra lên Kaggel ở phần input.

Đảm bảo cấu trúc thư mục /content như thế này:
/input/
├── Pets/
│   ├── dogs/
│   │   ├── dog1.jpg
│   │   ├── dog2.jpg
│   │   └── ...
│   └── cats/
│       ├── cat1.jpg
│       ├── cat2.jpg
│       └── ...


### Chạy mô hình
Để chạy được thì cần chạy với 2 GPU T4 của Kaggel.<br>
1. Chỉnh sửa đường dẫn tại những chỗ đã chỉ định trong code (mở code ra đọc là thấy)

2. Chạy mô hình từ đầu.

3. Tải model về máy, tải log về máy để xem xét!

### Note
- Hiện chưa có ghi lại log
- Hiện chưa có hàm gọi lại model sau khi training

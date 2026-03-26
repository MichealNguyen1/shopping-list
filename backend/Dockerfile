# Dockerfile — Hướng dẫn Docker build image để chạy backend
#
# Image là gì? Giống như file .ipa của iOS app — snapshot môi trường chạy app.
# Container là gì? Instance đang chạy từ image — giống như app đang chạy trên device.

# Base image: Python 3.12 phiên bản slim (nhỏ hơn, không có các tool dev không cần thiết)
FROM python:3.12-slim

# Set working directory trong container
# Mọi lệnh RUN/COPY/CMD sau đây đều chạy từ /app
WORKDIR /app

# Copy requirements trước, copy code sau — tại sao?
# Docker cache layer: nếu requirements.txt không đổi, Docker tái sử dụng layer pip install.
# Chỉ khi code thay đổi mới cần rebuild từ bước COPY . .
# Nếu copy tất cả 1 lần, mỗi lần sửa 1 dòng code là phải pip install lại (rất chậm).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Port mà container lắng nghe (chỉ là documentation, không tự mở port)
EXPOSE 8000

# Lệnh chạy khi container start
# host=0.0.0.0: lắng nghe tất cả network interface (cần thiết trong container)
# port=$PORT: Render tự inject biến PORT, không hardcode
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

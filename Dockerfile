FROM alpine:latest

# تثبيت Nginx + FFmpeg + Python
RUN apk update && apk add --no-cache \
    nginx \
    ffmpeg \
    python3 \
    py3-pip \
    curl \
    openssl \
    && rm -rf /var/cache/apk/*

# تثبيت مكتبات Python
RUN pip3 install flask requests

# إنشاء مجلدات
RUN mkdir -p /tmp/hls /tmp/dash /var/log/nginx /app

# نسخ الملفات
COPY nginx.conf /etc/nginx/nginx.conf
COPY convert.py /app/convert.py
COPY start.sh /app/start.sh

# صلاحيات
RUN chmod +x /app/start.sh /app/convert.py

# منافذ
EXPOSE 8080

CMD ["/app/start.sh"]

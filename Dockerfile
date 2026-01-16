FROM alpine:latest

# تثبيت Nginx + FFmpeg + Python مع حزم apk
RUN apk update && apk add --no-cache \
    nginx \
    ffmpeg \
    python3 \
    py3-pip \
    curl \
    openssl \
    # إضافة حزم Python عبر apk
    py3-flask \
    py3-requests \
    && rm -rf /var/cache/apk/*

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

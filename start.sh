#!/bin/sh

# تشغيل محول DASH إلى HLS في الخلفية
python3 /app/convert.py &

# تشغيل Nginx
nginx -g "daemon off;"

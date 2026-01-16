#!/usr/bin/env python3
import os
import subprocess
import time
import threading
from flask import Flask, jsonify

app = Flask(__name__)

# إعدادات القنوات
CHANNELS = {
    "art-aflam": {
        "dash_url": "https://neacdnpop3-edge02.aws.playco.com/live/eds/ART_Aflam/DASH/ART_Aflam.mpd",
        "key_id": "264e7cb9dfd6b9e5c281c97db4c2b4fa",
        "key": "47425a7e8f7e4030d186559852ae97db",
        "hls_path": "/tmp/hls/art-aflam",
        "active": False
    }
}

def convert_dash_to_hls(channel_name, config):
    """تحويل DASH إلى HLS"""
    
    hls_path = config['hls_path']
    dash_url = config['dash_url']
    
    # إنشاء مجلد HLS
    os.makedirs(hls_path, exist_ok=True)
    
    # ملف مفاتيح DRM
    drm_key_file = f"/tmp/{channel_name}.key"
    with open(drm_key_file, 'w') as f:
        f.write(f"{config['key_id']}:{config['key']}")
    
    # أمر FFmpeg للتحويل
    cmd = [
        'ffmpeg',
        '-headers', 'User-Agent: Mozilla/5.0\r\n',
        '-i', dash_url,
        '-codec', 'copy',
        '-hls_time', '6',
        '-hls_list_size', '10',
        '-hls_flags', 'delete_segments+append_list',
        '-hls_segment_filename', f'{hls_path}/segment_%03d.ts',
        '-hls_key_info_file', drm_key_file,
        '-hls_base_url', f'/hls/{channel_name}/',
        f'{hls_path}/playlist.m3u8'
    ]
    
    print(f"Starting conversion for {channel_name}...")
    
    try:
        # تشغيل FFmpeg
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        CHANNELS[channel_name]['active'] = True
        CHANNELS[channel_name]['process'] = process
        
        # مراقبة العملية
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"[{channel_name}] {output.strip()}")
        
        CHANNELS[channel_name]['active'] = False
        
    except Exception as e:
        print(f"Error converting {channel_name}: {e}")
        CHANNELS[channel_name]['active'] = False

@app.route('/api/status')
def status():
    """حالة التحويل"""
    return jsonify({
        'channels': {
            name: {'active': config['active']} 
            for name, config in CHANNELS.items()
        }
    })

@app.route('/api/start/<channel_name>')
def start_channel(channel_name):
    """بدء تحويل قناة"""
    if channel_name in CHANNELS:
        if not CHANNELS[channel_name]['active']:
            thread = threading.Thread(
                target=convert_dash_to_hls,
                args=(channel_name, CHANNELS[channel_name])
            )
            thread.daemon = True
            thread.start()
            return jsonify({'status': 'started', 'channel': channel_name})
        else:
            return jsonify({'status': 'already_running', 'channel': channel_name})
    return jsonify({'status': 'not_found'}), 404

def start_all_channels():
    """بدء جميع القنوات"""
    for channel_name, config in CHANNELS.items():
        thread = threading.Thread(
            target=convert_dash_to_hls,
            args=(channel_name, config)
        )
        thread.daemon = True
        thread.start()
        time.sleep(2)

if __name__ == '__main__':
    # بدء جميع القنوات
    start_all_channels()
    
    # تشغيل خادم API
    app.run(host='0.0.0.0', port=5000, debug=False)

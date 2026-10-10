#!/usr/bin/env python3
"""
BETA SOLUTIONS BI SERVER (PORT 9091)
- Nguồn dữ liệu: sample-data/ngan_sach_phong_ban.xlsx
- Polling endpoint: /api/data (caching with mtime, phản hồi < 2ms)
- Export endpoint: /api/export-static (tạo file HTML tĩnh độc lập và đóng gói ZIP password 'beta2026')
- Download endpoint: /api/download-zip
- Brand Guideline: Ngân sách #7C3AED, Chi tiêu #06B6D4, Vượt ngân sách #F43F5E
- Tự động mở Google Chrome trên cổng 9091 khi khởi chạy
"""

import os
import sys
import json
import time
import datetime
import threading
import subprocess
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import pandas as pd

from export_beta_dashboard import (
    load_dataset,
    generate_static_dashboard,
    EXCEL_PATH,
    OUTPUT_DIR,
    ZIP_FILENAME,
    STATIC_HTML_FILENAME,
    PASSWORD
)

PORT = 9091
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_beta.html')

_cache = {
    'mtime': None,
    'data': None
}


def get_cached_data():
    global _cache
    target_path = EXCEL_PATH
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Không tìm thấy file Excel tại {target_path}")

    current_mtime = os.path.getmtime(target_path)
    if _cache['data'] is not None and _cache['mtime'] == current_mtime:
        return _cache['data']

    # Load fresh dataset
    data = load_dataset()
    _cache['mtime'] = current_mtime
    _cache['data'] = data
    return data


class BetaDashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Ẩn bớt log polling định kỳ 2s để console luôn gọn gàng
        if args and len(args) > 0 and isinstance(args[0], str) and '/api/data' in args[0]:
            return
        super().log_message(format, *args)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        url_path = self.path.split('?')[0]

        if url_path in ['/', '/index.html', '/dashboard_beta.html']:
            self.serve_dashboard()
        elif url_path == '/api/data':
            self.serve_api_data()
        elif url_path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'port': PORT, 'company': 'Beta Solutions'}).encode('utf-8'))
        elif url_path == '/api/download-zip':
            self.serve_download_zip()
        else:
            self.send_error(404, 'Not Found')

    def do_POST(self):
        url_path = self.path.split('?')[0]
        if url_path == '/api/export-static':
            self.handle_export_static()
        elif url_path == '/api/send-telegram':
            self.handle_send_telegram()
        else:
            self.send_error(404, 'Not Found')

    def serve_dashboard(self):
        if not os.path.exists(HTML_PATH):
            self.send_error(404, 'dashboard_beta.html not found')
            return

        with open(HTML_PATH, 'rb') as f:
            content = f.read()

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(content)

    def serve_api_data(self):
        try:
            data = get_cached_data()
            json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(json_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(json_bytes)
        except Exception as e:
            err_json = json.dumps({'error': str(e)}).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(err_json)

    def handle_export_static(self):
        try:
            print("📦 [Export API] Nhận yêu cầu xuất Dashboard tĩnh từ trình duyệt...")
            res = generate_static_dashboard()
            resp_payload = {
                'success': True,
                'password': res['password'],
                'static_html': STATIC_HTML_FILENAME,
                'zip_file': ZIP_FILENAME,
                'exported_at': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            json_bytes = json.dumps(resp_payload, ensure_ascii=False).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(json_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_bytes)
        except Exception as e:
            err_json = json.dumps({'success': False, 'error': str(e)}).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(err_json)

    def handle_send_telegram(self):
        try:
            from send_dashboard_telegram import send_dashboard_to_telegram
            print("📲 [Telegram API] Nhận yêu cầu gửi báo cáo qua Telegram...")
            res = send_dashboard_to_telegram()
            resp_payload = {
                'success': True,
                'message': 'Đã gửi thành công 2 file báo cáo vào Telegram!',
                'data': res
            }
            json_bytes = json.dumps(resp_payload, ensure_ascii=False).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(json_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_bytes)
        except Exception as e:
            print(f"❌ [Telegram API Error] {e}")
            err_json = json.dumps({'success': False, 'error': str(e)}).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(err_json)

    def serve_download_zip(self):
        zip_path = os.path.join(OUTPUT_DIR, ZIP_FILENAME)
        if not os.path.exists(zip_path):
            # Nếu chưa có, tự động tạo mới
            generate_static_dashboard()

        if not os.path.exists(zip_path):
            self.send_error(404, 'File ZIP không tồn tại')
            return

        with open(zip_path, 'rb') as f:
            content = f.read()

        self.send_response(200)
        self.send_header('Content-Type', 'application/zip')
        self.send_header('Content-Disposition', f'attachment; filename="{ZIP_FILENAME}"')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def open_browser():
    time.sleep(1.2)
    url = f"http://localhost:{PORT}"
    print(f"🚀 [Browser] Đang tự động mở trình duyệt tới: {url}...")
    try:
        res = subprocess.run(["open", "-a", "Google Chrome", url], capture_output=True)
        if res.returncode != 0:
            webbrowser.open(url)
    except Exception:
        webbrowser.open(url)


def run_server():
    server_address = ('', PORT)
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer(server_address, BetaDashboardHandler)

    print("=" * 70)
    print(f"  🏢 CÔNG TY BETA SOLUTIONS — EXECUTIVE BUDGET DASHBOARD SERVER")
    print(f"  🌐 URL: http://localhost:{PORT}")
    print(f"  📊 Dữ liệu: {EXCEL_PATH}")
    print(f"  🔄 Real-time Polling: 2 giây / lần")
    print(f"  🎨 Brand Guideline: Ngân sách #7C3AED | Chi tiêu #06B6D4 | Vượt NS #F43F5E")
    print(f"  🔒 Mật khẩu ZIP nộp bài: {PASSWORD}")
    print("=" * 70)

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng máy chủ Beta Solutions.")
        httpd.server_close()


if __name__ == '__main__':
    run_server()

#!/usr/bin/env python3
"""
ALPHA CORP BI SERVER
- Port: 9090
- Reads: sales_data.xlsx
- Polling endpoint: /api/data (caching with mtime)
- Brand Guideline: DT #1E3A8A, CP #EF4444
- Auto-opens Google Chrome on startup
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

PORT = 9090
EXCEL_PATH = os.path.join(os.path.dirname(__file__), 'sales_data.xlsx')
HTML_PATH = os.path.join(os.path.dirname(__file__), 'dashboard.html')

# In-memory cache for ultra-fast polling
_cache = {
    'mtime': None,
    'data': None
}

def load_sales_data():
    """
    Reads sales_data.xlsx and transforms into structured JSON for Dashboard BI.
    Utilizes file mtime caching to ensure sub-millisecond responses on 2s polling.
    """
    global _cache

    if not os.path.exists(EXCEL_PATH):
        # Fallback to sample-data if sales_data.xlsx is missing in root
        fallback_path = os.path.join(os.path.dirname(__file__), 'sample-data', 'DEMO_sales_data.xlsx')
        target_path = fallback_path if os.path.exists(fallback_path) else EXCEL_PATH
    else:
        target_path = EXCEL_PATH

    current_mtime = os.path.getmtime(target_path) if os.path.exists(target_path) else 0

    if _cache['data'] is not None and _cache['mtime'] == current_mtime:
        return _cache['data']

    # Read and aggregate Excel data
    df = pd.read_excel(target_path)

    # 1. Four Core KPIs
    tong_dt = int(df['Doanh_Thu'].sum())
    tong_cp = int(df['Tong_Chi_Phi'].sum())
    tong_ln = int(df['Loi_Nhuan'].sum())
    tong_dh = int(df['Ma_Don_Hang'].nunique() if 'Ma_Don_Hang' in df.columns else len(df))
    tong_sl = int(df['So_Luong'].sum())

    bien_ln = round((tong_ln / tong_dt * 100), 1) if tong_dt > 0 else 0
    ty_le_cp = round((tong_cp / tong_dt * 100), 1) if tong_dt > 0 else 0

    kpi = {
        'doanh_thu': tong_dt,
        'chi_phi': tong_cp,
        'loi_nhuan': tong_ln,
        'don_hang': tong_dh,
        'tong_so_luong': tong_sl,
        'bien_loi_nhuan': bien_ln,
        'ty_le_chi_phi': ty_le_cp
    }

    # 2. Line Chart: Trend by Month
    by_month_df = df.groupby('Thang')[['Doanh_Thu', 'Tong_Chi_Phi', 'Loi_Nhuan']].sum().reset_index().sort_values(by='Thang')
    by_month = []
    for _, row in by_month_df.iterrows():
        by_month.append({
            'thang': str(row['Thang']),
            'doanh_thu': int(row['Doanh_Thu']),
            'chi_phi': int(row['Tong_Chi_Phi']),
            'loi_nhuan': int(row['Loi_Nhuan'])
        })

    # 3. Bar Chart & Donut Chart: By Category
    by_cat_df = df.groupby('Danh_Muc_San_Pham')[['Doanh_Thu', 'Tong_Chi_Phi', 'Loi_Nhuan', 'So_Luong']].sum().reset_index().sort_values(by='Doanh_Thu', ascending=False)
    by_category = []
    for _, row in by_cat_df.iterrows():
        by_category.append({
            'danh_muc': str(row['Danh_Muc_San_Pham']),
            'doanh_thu': int(row['Doanh_Thu']),
            'chi_phi': int(row['Tong_Chi_Phi']),
            'loi_nhuan': int(row['Loi_Nhuan']),
            'so_luong': int(row['So_Luong'])
        })

    # 4. Top 10 Products
    top_df = df.groupby(['Ten_San_Pham', 'Danh_Muc_San_Pham'])[['So_Luong', 'Doanh_Thu', 'Tong_Chi_Phi', 'Loi_Nhuan']].sum().reset_index().sort_values(by='Doanh_Thu', ascending=False).head(10)
    top_products = []
    for _, row in top_df.iterrows():
        p_dt = int(row['Doanh_Thu'])
        p_ln = int(row['Loi_Nhuan'])
        p_bien = round((p_ln / p_dt * 100), 1) if p_dt > 0 else 0
        top_products.append({
            'ten_san_pham': str(row['Ten_San_Pham']),
            'danh_muc': str(row['Danh_Muc_San_Pham']),
            'so_luong': int(row['So_Luong']),
            'doanh_thu': p_dt,
            'chi_phi': int(row['Tong_Chi_Phi']),
            'loi_nhuan': p_ln,
            'bien_loi_nhuan': p_bien
        })

    response_data = {
        'kpi': kpi,
        'by_month': by_month,
        'by_category': by_category,
        'top_products': top_products,
        'metadata': {
            'total_rows': len(df),
            'mtime': current_mtime,
            'time_str': datetime.datetime.now().strftime('%H:%M:%S (%d/%m/%Y)'),
            'brand': 'Alpha Corp - DT #1E3A8A, CP #EF4444'
        }
    }

    _cache['mtime'] = current_mtime
    _cache['data'] = response_data
    return response_data


class AlphaDashboardHandler(BaseHTTPRequestHandler):
    """
    HTTP Handler for BI Dashboard & Realtime API
    """
    def log_message(self, format, *args):
        # Suppress routine 2s polling logs to keep stdout clean, log only errors or first load
        if '/api/data' in args[0]:
            return
        super().log_message(format, *args)

    def do_GET(self):
        url_path = self.path.split('?')[0]

        if url_path in ['/', '/index.html', '/dashboard.html']:
            self.serve_dashboard()
        elif url_path == '/api/data':
            self.serve_api()
        elif url_path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "port": 9090}')
        else:
            self.send_error(404, 'Not Found')

    def serve_dashboard(self):
        if not os.path.exists(HTML_PATH):
            self.send_error(404, 'Dashboard HTML file not found')
            return

        with open(HTML_PATH, 'rb') as f:
            content = f.read()

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(content)

    def serve_api(self):
        try:
            data = load_sales_data()
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


def open_browser():
    """Tự động mở Google Chrome tới http://localhost:9090"""
    time.sleep(1.2)
    url = f"http://localhost:{PORT}"
    print(f"🚀 [Browser] Đang mở trình duyệt tới {url}...")
    try:
        # Ưu tiên mở bằng Google Chrome trên macOS
        res = subprocess.run(["open", "-a", "Google Chrome", url], capture_output=True)
        if res.returncode != 0:
            webbrowser.open(url)
    except Exception:
        webbrowser.open(url)


def run_server():
    server_address = ('', PORT)
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer(server_address, AlphaDashboardHandler)

    print("=" * 65)
    print(f"  🏢 CÔNG TY TNHH ALPHA — EXECUTIVE BI DASHBOARD SERVER")
    print(f"  🌐 URL: http://localhost:{PORT}")
    print(f"  📊 Nguồn dữ liệu: {EXCEL_PATH}")
    print(f"  🔄 Chu kỳ Polling: 2 giây / lần")
    print(f"  🎨 Brand Guideline: DT #1E3A8A | CP #EF4444 (TUYỆT ĐỐI)")
    print("=" * 65)

    # Khởi chạy tiểu trình tự mở trình duyệt Chrome
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng server Alpha BI.")
        httpd.server_close()


if __name__ == '__main__':
    run_server()

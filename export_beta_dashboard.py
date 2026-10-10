#!/usr/bin/env python3
"""
EXPORT & ENCRYPTION PIPELINE — BETA SOLUTIONS BUDGET DASHBOARD
- Nguồn dữ liệu: sample-data/ngan_sach_phong_ban.xlsx
- Brand Guideline: Ngân sách #7C3AED, Chi tiêu #06B6D4, Vượt ngân sách #F43F5E
- Tạo Dashboard tĩnh độc lập: outputs/dashboards/Beta_Solutions_Dashboard_Static.html
- Đóng gói file ZIP bảo vệ bằng mật khẩu: outputs/dashboards/Beta_Solutions_Dashboard_Protected.zip (Password: beta2026)
"""

import os
import sys
import json
import subprocess
import datetime
import pandas as pd

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(WORKSPACE_DIR, 'sample-data', 'ngan_sach_phong_ban.xlsx')
HTML_TEMPLATE_PATH = os.path.join(WORKSPACE_DIR, 'dashboard_beta.html')
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, 'outputs', 'dashboards')
PASSWORD = "beta2026"

STATIC_HTML_FILENAME = "Beta_Solutions_Dashboard_Static.html"
ZIP_FILENAME = "Beta_Solutions_Dashboard_Protected.zip"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def load_dataset():
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"Không tìm thấy file Excel tại: {EXCEL_PATH}")

    df = pd.read_excel(EXCEL_PATH)

    # 1. KPIs
    tong_ns = int(df['Ngan_Sach_Du_Kien'].sum())
    tong_chi = int(df['Chi_Tieu_Thuc_Te'].sum())
    chenh_lech = int(df['Chenh_Lech'].sum())
    so_gd_vuot = int((df['Trang_Thai'] == 'Vượt ngân sách').sum())
    tong_so_gd = len(df)
    ty_le_vuot = round((so_gd_vuot / tong_so_gd * 100), 1) if tong_so_gd > 0 else 0
    ty_le_su_dung = round((tong_chi / tong_ns * 100), 1) if tong_ns > 0 else 0

    kpi = {
        'tong_ngan_sach': tong_ns,
        'tong_chi_tieu': tong_chi,
        'chenh_lech': chenh_lech,
        'so_gd_vuot': so_gd_vuot,
        'tong_so_gd': tong_so_gd,
        'ty_le_vuot': ty_le_vuot,
        'ty_le_su_dung': ty_le_su_dung
    }

    # 2. Theo Quý
    by_quy_df = df.groupby('Quy')[['Ngan_Sach_Du_Kien', 'Chi_Tieu_Thuc_Te', 'Chenh_Lech']].sum().reset_index()
    by_quy_df['sort_key'] = by_quy_df['Quy'].map({'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}).fillna(99)
    by_quy_df = by_quy_df.sort_values(by='sort_key')
    by_quy = []
    for _, r in by_quy_df.iterrows():
        by_quy.append({
            'quy': str(r['Quy']),
            'ngan_sach': int(r['Ngan_Sach_Du_Kien']),
            'chi_tieu': int(r['Chi_Tieu_Thuc_Te']),
            'chenh_lech': int(r['Chenh_Lech'])
        })

    # 3. Theo Phòng Ban
    by_pb_df = df.groupby('Phong_Ban')[['Ngan_Sach_Du_Kien', 'Chi_Tieu_Thuc_Te', 'Chenh_Lech']].sum().reset_index().sort_values(by='Chi_Tieu_Thuc_Te', ascending=False)
    by_phong_ban = []
    for _, r in by_pb_df.iterrows():
        pb_vuot = int(((df['Phong_Ban'] == r['Phong_Ban']) & (df['Trang_Thai'] == 'Vượt ngân sách')).sum())
        by_phong_ban.append({
            'phong_ban': str(r['Phong_Ban']),
            'ngan_sach': int(r['Ngan_Sach_Du_Kien']),
            'chi_tieu': int(r['Chi_Tieu_Thuc_Te']),
            'chenh_lech': int(r['Chenh_Lech']),
            'so_gd_vuot': pb_vuot
        })

    # 4. Danh sách toàn bộ giao dịch
    transactions = []
    for _, r in df.iterrows():
        transactions.append({
            'ma_gd': str(r['Ma_Giao_Dich']),
            'ngay': str(r['Ngay']),
            'quy': str(r['Quy']),
            'phong_ban': str(r['Phong_Ban']),
            'hang_muc': str(r['Hang_Muc']),
            'ngan_sach': int(r['Ngan_Sach_Du_Kien']),
            'chi_tieu': int(r['Chi_Tieu_Thuc_Te']),
            'chenh_lech': int(r['Chenh_Lech']),
            'trang_thai': str(r['Trang_Thai']),
            'phan_tram': float(r['Phan_Tram_Su_Dung'])
        })

    current_mtime = os.path.getmtime(EXCEL_PATH) if os.path.exists(EXCEL_PATH) else 0

    return {
        'kpi': kpi,
        'by_quy': by_quy,
        'by_phong_ban': by_phong_ban,
        'transactions': transactions,
        'metadata': {
            'mtime': current_mtime,
            'exported_at': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'company': 'Beta Solutions Co., Ltd',
            'brand': {
                'budget_color': '#7C3AED',
                'expense_color': '#06B6D4',
                'over_budget_color': '#F43F5E',
                'bg_color': '#0F172A'
            }
        }
    }


def generate_static_dashboard(data=None):
    """
    Tạo file HTML tĩnh chứa dữ liệu nhúng và đóng gói ZIP có mật khẩu.
    """
    ensure_dir(OUTPUT_DIR)

    if data is None:
        data = load_dataset()

    if not os.path.exists(HTML_TEMPLATE_PATH):
        raise FileNotFoundError(f"Không tìm thấy template HTML tại: {HTML_TEMPLATE_PATH}")

    with open(HTML_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Nhúng trực tiếp JSON snapshot
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    embedded_script = f"""
    <!-- STATIC SNAPSHOT EMBEDDED DATA -->
    <script>
      window.IS_STATIC_DASHBOARD = true;
      window.STATIC_DATA = {json_str};
    </script>
    """

    if "<!-- __STATIC_EMBED_ANCHOR__ -->" in html_content:
        static_html = html_content.replace("<!-- __STATIC_EMBED_ANCHOR__ -->", embedded_script)
    elif "/* __STATIC_EMBED_ANCHOR__ */" in html_content:
        static_html = html_content.replace("/* __STATIC_EMBED_ANCHOR__ */", embedded_script)
    else:
        static_html = html_content.replace("</head>", f"{embedded_script}\n</head>")

    static_file_path = os.path.join(OUTPUT_DIR, STATIC_HTML_FILENAME)
    with open(static_file_path, 'w', encoding='utf-8') as f:
        f.write(static_html)

    print(f"✅ [1/2] Đã xuất file HTML tĩnh tại: {static_file_path}")

    # Đóng gói ZIP với mật khẩu bằng lệnh zip native
    zip_dest = os.path.join(OUTPUT_DIR, ZIP_FILENAME)
    if os.path.exists(zip_dest):
        os.remove(zip_dest)

    cmd = [
        "zip",
        "-P", PASSWORD,
        "-j",
        zip_dest,
        static_file_path
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Lỗi khi nén ZIP: {res.stderr}")

    # Copy một bản ra thư mục gốc workspace để dễ nộp/truy cập
    root_zip = os.path.join(WORKSPACE_DIR, ZIP_FILENAME)
    root_static = os.path.join(WORKSPACE_DIR, STATIC_HTML_FILENAME)
    with open(static_file_path, 'r', encoding='utf-8') as f_src, open(root_static, 'w', encoding='utf-8') as f_dst:
        f_dst.write(f_src.read())

    cmd_root = [
        "zip",
        "-P", PASSWORD,
        "-j",
        root_zip,
        root_static
    ]
    subprocess.run(cmd_root, capture_output=True)

    print(f"🔒 [2/2] Đã đóng gói file ZIP bảo vệ bằng mật khẩu '{PASSWORD}':")
    print(f"   📁 {zip_dest}")
    print(f"   📁 {root_zip}")

    return {
        'static_html_path': static_file_path,
        'zip_path': zip_dest,
        'root_zip_path': root_zip,
        'password': PASSWORD
    }


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 BẮT ĐẦU XUẤT DASHBOARD QUẢN LÝ NGÂN SÁCH BETA SOLUTIONS")
    print("=" * 60)
    res = generate_static_dashboard()
    print("\n🎉 HOÀN TẤT!")
    print(f"🔑 MẬT KHẨU GIẢI NÉN: {res['password']}")

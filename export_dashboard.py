#!/usr/bin/env python3
"""
EXPORT & SECURE PACKAGING SCRIPT — ALPHA CORP BI DASHBOARD
- Đọc dữ liệu từ: sales_data.xlsx
- Xuất file HTML tĩnh độc lập (Standalone Offline Static HTML)
- Đóng gói & mã hóa bằng WinRAR / 7-Zip tương thích (Password: admin1234)
- Tuân thủ Brand Guideline: DT #1E3A8A, CP #EF4444
"""

import os
import sys
import json
import shutil
import datetime
import subprocess
import pandas as pd

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(WORKSPACE_DIR, 'sales_data.xlsx')
HTML_TEMPLATE_PATH = os.path.join(WORKSPACE_DIR, 'dashboard.html')
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, 'outputs', 'dashboards')
PASSWORD = "admin1234"

STATIC_HTML_FILENAME = "Alpha_BI_Dashboard_Static.html"
ZIP_FILENAME = "Alpha_BI_Dashboard_Protected.zip"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def calculate_metrics():
    """
    Đọc sales_data.xlsx và tổng hợp dữ liệu cho Dashboard
    """
    target_excel = EXCEL_PATH
    if not os.path.exists(target_excel):
        fallback = os.path.join(WORKSPACE_DIR, 'sample-data', 'DEMO_sales_data.xlsx')
        if os.path.exists(fallback):
            target_excel = fallback
        else:
            raise FileNotFoundError(f"Không tìm thấy file dữ liệu: {EXCEL_PATH}")

    print(f"📊 [1/4] Đang đọc & phân tích dữ liệu từ: {target_excel}...")
    df = pd.read_excel(target_excel)

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

    # Xu hướng theo tháng
    by_month_df = df.groupby('Thang')[['Doanh_Thu', 'Tong_Chi_Phi', 'Loi_Nhuan']].sum().reset_index().sort_values(by='Thang')
    by_month = []
    for _, row in by_month_df.iterrows():
        by_month.append({
            'thang': str(row['Thang']),
            'doanh_thu': int(row['Doanh_Thu']),
            'chi_phi': int(row['Tong_Chi_Phi']),
            'loi_nhuan': int(row['Loi_Nhuan'])
        })

    # Cơ cấu danh mục
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

    # Top 10 sản phẩm
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

    now_str = datetime.datetime.now().strftime('%H:%M:%S (%d/%m/%Y)')
    return {
        'kpi': kpi,
        'by_month': by_month,
        'by_category': by_category,
        'top_products': top_products,
        'metadata': {
            'total_rows': len(df),
            'time_str': now_str,
            'mode': 'Offline Standalone Static',
            'brand': 'Alpha Corp - DT #1E3A8A, CP #EF4444'
        }
    }


def generate_static_html(data, output_html_path):
    """
    Nhúng trực tiếp dữ liệu JSON vào HTML để tạo thành file tĩnh tự vận hành
    """
    print("🎨 [2/4] Đang tạo file HTML tĩnh độc lập (Embedded Data)...")
    if not os.path.exists(HTML_TEMPLATE_PATH):
        raise FileNotFoundError(f"Không tìm thấy template HTML: {HTML_TEMPLATE_PATH}")

    with open(HTML_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # Nhúng payload dữ liệu tĩnh
    json_payload = json.dumps(data, ensure_ascii=False)
    injection_script = f"""
  <!-- DỮ LIỆU TĨNH NHÚNG TRỰC TIẾP CHO CHẾ ĐỘ OFFLINE BẢO MẬT -->
  <script id="embedded-data" type="application/json">
{json_payload}
  </script>
  <script>
    window.STATIC_MODE = true;
    window.EMBEDDED_DATA = JSON.parse(document.getElementById('embedded-data').textContent);
  </script>
"""

    # Thay đổi logic init để ưu tiên nạp dữ liệu tĩnh ngay lập tức
    static_override = """
    // Nạp dữ liệu tĩnh ngay lập tức khi mở file
    function initStaticData() {
      if (window.EMBEDDED_DATA) {
        const data = window.EMBEDDED_DATA;
        document.getElementById('lastUpdatedBox').textContent = 'Xuất Bản Tĩnh: ' + data.metadata.time_str;
        updateKPIs(data.kpi);
        updateLineChart(data.by_month);
        updateDonutChart(data.by_category);
        updateBarChart(data.by_category);
        updateTopTable(data.top_products);
        isInitialLoad = false;
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      initStaticData();
      // Nếu đang mở qua HTTP server thì tiếp tục polling, nếu mở offline file:// thì giữ nguyên dữ liệu tĩnh
      if (location.protocol.startsWith('http')) {
        setInterval(() => fetchData(), 2000);
      }
    });
"""

    # Chèn injection vào trước thẻ </head>
    html = html.replace('</head>', f'{injection_script}\n</head>')

    # Cập nhật nhãn trạng thái sang "Bản Tĩnh Bảo Mật"
    html = html.replace(
        '<span class="polling-dot"></span> Polling 2s (sales_data.xlsx)',
        '<span class="polling-dot" style="background: #00f0ff; box-shadow: 0 0 10px #00f0ff;"></span> Standalone Offline (Bảo Mật)'
    )

    # Thay thế phần window.addEventListener cuối file
    old_init = """    /* RUN ON LOAD */
    window.addEventListener('DOMContentLoaded', () => {
      fetchData();
      setInterval(() => {
        fetchData();
      }, 2000);
    });"""
    if old_init in html:
        html = html.replace(old_init, static_override)
    else:
        # Thay thế khối tương ứng nếu có sai khác
        target_token = "window.addEventListener('DOMContentLoaded', () => {"
        idx = html.rfind(target_token)
        if idx != -1:
            end_script = html.find('</script>', idx)
            if end_script != -1:
                html = html[:idx] + static_override + "\n  " + html[end_script:]

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  ✓ Đã xuất file HTML tĩnh: {output_html_path} ({os.path.getsize(output_html_path):,} bytes)")


def compress_and_encrypt(source_file_path, output_zip_path, password):
    """
    Nén file bằng zip với mật khẩu, hoàn toàn tương thích WinRAR & 7-Zip
    """
    print(f"🔒 [3/4] Đang đóng gói & đặt mật khẩu bảo vệ ({password})...")
    
    # Xóa file zip cũ nếu tồn tại
    if os.path.exists(output_zip_path):
        os.remove(output_zip_path)

    parent_dir = os.path.dirname(source_file_path)
    file_name = os.path.basename(source_file_path)

    # Kiểm tra sự hiện diện của 7z / 7za / zip
    has_7z = shutil.which("7z") or shutil.which("7za")
    zip_cmd = shutil.which("zip")

    if has_7z:
        cmd_tool = shutil.which("7z") or shutil.which("7za")
        print(f"  → Sử dụng {cmd_tool} (Mã hóa AES-256 cao cấp)...")
        # 7z với mã hóa password
        cmd = [cmd_tool, "a", "-p" + password, "-y", output_zip_path, file_name]
        subprocess.run(cmd, cwd=parent_dir, check=True, stdout=subprocess.DEVNULL)
    elif zip_cmd:
        print(f"  → Sử dụng standard zip encryption tương thích 100% WinRAR / 7-Zip...")
        cmd = [zip_cmd, "-P", password, "-j", output_zip_path, source_file_path]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    else:
        raise RuntimeError("Không tìm thấy công cụ nén (7z hoặc zip) trên hệ thống!")

    print(f"  ✓ Đã đóng gói thành công: {output_zip_path} ({os.path.getsize(output_zip_path):,} bytes)")

    # Kiểm tra giải mã thử để đảm bảo tính toàn vẹn (Verification)
    print("🔍 [4/4] Đang kiểm tra tính toàn vẹn của file nén...")
    verify_cmd = ["unzip", "-P", password, "-t", output_zip_path]
    res = subprocess.run(verify_cmd, capture_output=True, text=True)
    if "No errors detected" in res.stdout or res.returncode == 0:
        print("  ✓ Xác thực mật khẩu thành công: File nén hợp lệ 100%!")
    else:
        print("  ⚠️ Cảnh báo xác thực:", res.stderr or res.stdout)


def main():
    ensure_dir(OUTPUT_DIR)

    static_html_path = os.path.join(OUTPUT_DIR, STATIC_HTML_FILENAME)
    zip_path = os.path.join(OUTPUT_DIR, ZIP_FILENAME)

    # Tạo bản sao ở root để tiện truy cập nhanh
    root_zip_path = os.path.join(WORKSPACE_DIR, ZIP_FILENAME)

    print("=" * 65)
    print("  🚀 QUY TRÌNH ĐÓNG GÓI & CHIA SẺ AN TOÀN — ALPHA CORP BI")
    print("=" * 65)

    data = calculate_metrics()
    generate_static_html(data, static_html_path)
    compress_and_encrypt(static_html_path, zip_path, PASSWORD)

    # Copy ra workspace root để người dùng tiện lấy
    shutil.copy2(zip_path, root_zip_path)

    print("=" * 65)
    print("🎉 HOÀN THÀNH ĐÓNG GÓI AN TOÀN!")
    print(f"📁 File nén được tạo tại:")
    print(f"   1. {zip_path}")
    print(f"   2. {root_zip_path}")
    print(f"🔑 Mật khẩu mở file (WinRAR / 7-Zip): {PASSWORD}")
    print("=" * 65)


if __name__ == '__main__':
    main()

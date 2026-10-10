#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEND BETA BI DASHBOARD TO TELEGRAM
- Tự động trích xuất và đồng bộ dữ liệu mới nhất
- Gửi 2 file tài liệu:
  1. Beta_Solutions_Dashboard_Protected.zip (Mật khẩu: beta2026)
  2. Beta_Solutions_Dashboard_Static.html (Bản tĩnh mở xem ngay)
- Kèm bản tin Executive Digest tóm tắt 3 KPI thương hiệu (🟣 🔵 🔴)
"""

import os
import sys
import json
import logging
from datetime import datetime
import requests
from dotenv import load_dotenv

from export_beta_dashboard import (
    generate_static_dashboard,
    load_dataset,
    OUTPUT_DIR,
    ZIP_FILENAME,
    STATIC_HTML_FILENAME,
    PASSWORD
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("BetaTelegramSender")

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def format_currency_vnd(amount):
    return f"{amount:,.0f}".replace(",", ".") + " ₫"


def send_dashboard_to_telegram():
    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError("Chưa cấu hình TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID trong file .env!")

    logger.info("📊 [1/3] Đang làm mới dữ liệu và đóng gói bản nộp bài...")
    res = generate_static_dashboard()
    data = load_dataset()
    kpi = data['kpi']

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Soạn caption Executive chuẩn Brand Guideline Beta Solutions
    caption_zip = (
        "🏢 <b>CÔNG TY BETA SOLUTIONS — BÁO CÁO NGÂN SÁCH DOANH NGHIỆP</b>\n"
        f"<i>Kỳ phân tích: Năm tài chính 2026 (Q1 - Q4) • Xuất bản lúc: {now_str}</i>\n\n"
        "<b>📊 TỔNG HỢP 3 CHỈ SỐ KPI CHỦ LỰC:</b>\n"
        f"🟣 <b>Ngân Sách Dự Kiến:</b> <code>{format_currency_vnd(kpi['tong_ngan_sach'])}</code> (96 danh mục)\n"
        f"🔵 <b>Chi Tiêu Thực Tế :</b> <code>{format_currency_vnd(kpi['tong_chi_tieu'])}</code> (Tỷ lệ: {kpi['ty_le_su_dung']}%)\n"
        f"🔴 <b>Giao Dịch Vượt NS :</b> <code>{kpi['so_gd_vuot']}</code> / {kpi['tong_so_gd']} GD ({kpi['ty_le_vuot']}%)\n\n"
        "<b>🔒 THÔNG TIN BẢO MẬT & NỘP BÀI:</b>\n"
        f"• File đính kèm: <code>{ZIP_FILENAME}</code>\n"
        f"• Mật khẩu giải nén: <code>{PASSWORD}</code>\n"
        "• Tiêu chuẩn mã hóa: WinRAR & 7-Zip Protected"
    )

    caption_html = (
        "🌐 <b>BẢN XEM TRỰC TIẾP OFFLINE (STANDALONE HTML)</b>\n"
        f"• File: <code>{STATIC_HTML_FILENAME}</code>\n"
        "• Bạn có thể tải về và nhấp đúp chuột để mở xem trực tiếp trên mọi trình duyệt mà không cần cài đặt phần mềm phụ trợ."
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

    # Gửi File 1: Protected ZIP
    zip_path = res['zip_path']
    logger.info(f"📤 [2/3] Đang gửi file ZIP bảo vệ '{ZIP_FILENAME}' tới Telegram...")
    with open(zip_path, 'rb') as f_zip:
        resp1 = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": caption_zip,
                "parse_mode": "HTML"
            },
            files={"document": (ZIP_FILENAME, f_zip, "application/zip")},
            timeout=30
        )
    
    if resp1.status_code != 200:
        raise RuntimeError(f"Lỗi khi gửi file ZIP: {resp1.text}")

    # Gửi File 2: Static HTML
    static_path = res['static_html_path']
    logger.info(f"📤 [3/3] Đang gửi file HTML tĩnh '{STATIC_HTML_FILENAME}' tới Telegram...")
    with open(static_path, 'rb') as f_html:
        resp2 = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": caption_html,
                "parse_mode": "HTML"
            },
            files={"document": (STATIC_HTML_FILENAME, f_html, "text/html")},
            timeout=30
        )

    if resp2.status_code != 200:
        raise RuntimeError(f"Lỗi khi gửi file HTML: {resp2.text}")

    logger.info("🎉 ĐÃ GỬI THÀNH CÔNG CẢ 2 FILE DASHBOARD TỚI TELEGRAM!")
    return {
        "success": True,
        "zip_file": ZIP_FILENAME,
        "static_html": STATIC_HTML_FILENAME,
        "password": PASSWORD,
        "chat_id": CHAT_ID,
        "sent_at": now_str
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 GỬI BÁO CÁO DASHBOARD BETA SOLUTIONS QUA TELEGRAM")
    print("=" * 60)
    try:
        result = send_dashboard_to_telegram()
        print("\n✅ KẾT QUẢ: Gửi thành công!")
        print(f"📁 File ZIP: {result['zip_file']}")
        print(f"📁 File HTML: {result['static_html']}")
        print(f"🔑 Mật khẩu: {result['password']}")
        print(f"⏱ Thời gian: {result['sent_at']}")
    except Exception as e:
        print(f"\n❌ LỖI: {e}", file=sys.stderr)
        sys.exit(1)

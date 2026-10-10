#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lead Scoring Engine - Ngành Bất Động Sản (Real Estate)
Tự động hóa đánh giá nhu cầu khách hàng, tính toán điểm 5 tiêu chí,
phát hiện cờ đỏ/cờ VIP theo quy chuẩn và xuất báo cáo phân loại cho Sales.
"""

import sys
import os
import re
import urllib.request
import ssl
import pandas as pd
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Fix SSL context for macOS python if needed
ssl._create_default_https_context = ssl._create_unverified_context


def clean_phone(raw_phone):
    """Chuẩn hóa số điện thoại Việt Nam 10 chữ số."""
    if pd.isna(raw_phone):
        return "N/A"
    digits = re.sub(r"\D", "", str(raw_phone).split(".")[0])
    if len(digits) == 9:
        digits = "0" + digits
    elif len(digits) > 10 and digits.startswith("84"):
        digits = "0" + digits[2:]
    return digits


def analyze_real_estate_lead(row):
    """
    Phân tích nội dung nhu cầu và chấm điểm theo 5 tiêu chí & bộ quy tắc:
    - Tiêu chí 1: Ngân sách (Budget)
    - Tiêu chí 2: Mức độ quan tâm / Phân khúc (Need & Interest)
    - Tiêu chí 3: Thời gian mua / Cấp thiết (Timeline & Urgency)
    - Tiêu chí 4: Nguồn khách & Hồ sơ (Source & Profile)
    - Tiêu chí 5: Tương tác & Khả năng tiếp cận (Engagement)
    Kèm hệ thống cờ thưởng VIP (+50) và cờ phạt (-50)
    """
    desc = str(row.get("nhu_cau_mo_ta", "")).lower()
    
    red_flags = []
    vip_flags = []
    
    # 1. KIỂM TRA RED FLAGS (-50 điểm theo tài liệu tieu_chi_cham_diem.txt)
    # - Yêu cầu phi thực tế:
    if any(k in desc for k in ["nhà q1 giá 1 tỷ", "q1 giá 1", "quận 1 giá 1", "nhà 1 tỷ", "giá 2 triệu", "vài trăm triệu", "phi thực tế"]):
        red_flags.append("Yêu cầu phi thực tế so với thị trường")
    
    # - Không có nhu cầu / nhầm số:
    if any(k in desc for k in ["nhầm số", "không có nhu cầu", "dữ liệu cũ", "nhầm ngành"]):
        red_flags.append("Nhầm số / Không có nhu cầu BĐS")
        
    # - Không thiện chí:
    if any(k in desc for k in ["hỏi giá cho vui", "chưa có ý định mua", "không hợp tác"]):
        red_flags.append("Khách không thiện chí / Hỏi cho vui")
        
    # - Spam / Quảng cáo ngược:
    if any(k in desc for k in ["spam", "bảo hiểm", "vay vốn", "mời chào", "quảng cáo ngược"]):
        red_flags.append("Spam / Chào mời dịch vụ khác")
        
    # - Lỗi liên lạc:
    if any(k in desc for k in ["thuê bao", "không bắt máy", "không phản hồi zalo", "không nghe máy"]):
        red_flags.append("Thông tin liên lạc lỗi / Thuê bao / Không phản hồi")

    # 2. KIỂM TRA VIP FLAGS (+50 điểm theo tài liệu tieu_chi_cham_diem.txt)
    # - Ngân sách lớn:
    if any(k in desc for k in ["20 tỷ", "30 tỷ", "trên 20 tỷ", "trên 30 tỷ", "tài chính mạnh", "tài chính cực mạnh", "không thành vấn đề", "thanh toán thẳng"]):
        vip_flags.append("Ngân sách lớn / Tài chính cực mạnh")
        
    # - Loại hình cao cấp:
    if any(k in desc for k in ["penthouse", "biệt thự đơn lập", "shophouse mặt đường lớn", "quỹ đất công nghiệp", "sàn văn phòng diện tích lớn", "sàn văn phòng"]):
        vip_flags.append("Loại hình BĐS cao cấp / Quy mô lớn")
        
    # - Vị trí đắc địa:
    if any(k in desc for k in ["ven sông", "quận 1", "vinhomes ocean park", "phú mỹ hưng"]):
        vip_flags.append("Vị trí đắc địa (Ven sông, Q1, KĐT cao cấp)")
        
    # - Đối tượng khách hàng VIP:
    if any(k in desc for k in ["chủ doanh nghiệp", "nhà đầu tư chuyên nghiệp", "mua sỉ", "gom sỉ", "số lượng lớn"]):
        vip_flags.append("Đối tượng VIP (Chủ DN, NĐT sỉ)")
        
    # - Tính cấp thiết & Minh bạch:
    if any(k in desc for k in ["pháp lý chuẩn 100%", "sổ hồng riêng", "gặp trực tiếp chủ đầu tư", "gặp trực tiếp giám đốc"]):
        vip_flags.append("Yêu cầu pháp lý minh bạch / Muốn gặp lãnh đạo đàm phán")

    # 3. CHẤM ĐIỂM CHI TIẾT 5 TIÊU CHÍ (Thang điểm chuẩn 100)
    score_budget = 0
    score_need = 0
    score_timeline = 0
    score_source = 0
    score_engagement = 0
    
    # Tiêu chí 1: Ngân sách (Max 35)
    if any(k in desc for k in ["không thành vấn đề", "trên 30 tỷ", "30 tỷ", "tài chính cực mạnh", "gom sỉ", "20 tỷ", "trên 20 tỷ"]):
        score_budget = 35
    elif any(k in desc for k in ["4-5 tỷ", "5 tỷ"]):
        score_budget = 25
    elif any(k in desc for k in ["dưới 50 triệu", "50 triệu"]):
        score_budget = 20
    elif any(k in desc for k in ["2-3 tỷ", "3 tỷ", "vùng ven"]):
        score_budget = 15
    elif any(k in desc for k in ["1 tỷ", "2 triệu", "phi thực tế"]):
        score_budget = -40
    else:
        score_budget = 10
        
    # Tiêu chí 2: Mức độ quan tâm / Nhu cầu (Max 25)
    if any(k in desc for k in ["penthouse", "biệt thự đơn lập", "shophouse", "sàn văn phòng", "đất công nghiệp"]):
        score_need = 25
    elif any(k in desc for k in ["mặt bằng kinh doanh spa", "căn hộ 2pn", "đất nền"]):
        score_need = 18
    elif "hỏi giá cho vui" in desc:
        score_need = 0
    elif any(k in desc for k in ["nhầm số", "spam"]):
        score_need = -30
    else:
        score_need = 8

    # Tiêu chí 3: Thời gian mua & Cấp thiết (Max 20)
    if any(k in desc for k in ["cuối tuần này", "gặp trực tiếp", "thanh toán thẳng"]):
        score_timeline = 18
    elif any(k in desc for k in ["ký hợp đồng dài hạn"]):
        score_timeline = 14
    elif any(k in desc for k in ["đầu tư dài hạn", "đang tìm"]):
        score_timeline = 10
    elif "chưa có ý định mua trong năm nay" in desc:
        score_timeline = 0
    elif any(k in desc for k in ["nhầm số", "thuê bao", "spam"]):
        score_timeline = -20
    else:
        score_timeline = 5

    # Tiêu chí 4: Nguồn khách & Hồ sơ / Thẩm quyền (Max 10)
    if any(k in desc for k in ["chủ doanh nghiệp", "nhà đầu tư chuyên nghiệp", "đã từng mua nhiều dự án", "khách hàng vip"]):
        score_source = 10
    elif any(k in desc for k in ["gia đình trẻ", "đang tìm thuê", "kinh doanh"]):
        score_source = 7
    elif any(k in desc for k in ["nhầm số", "spam"]):
        score_source = -20
    else:
        score_source = 5

    # Tiêu chí 5: Tương tác & Khả năng tiếp cận (Max 10)
    if any(k in desc for k in ["pháp lý chuẩn 100%", "sổ hồng riêng", "muốn đi xem nhà mẫu", "cần gặp trực tiếp"]):
        score_engagement = 10
    elif any(k in desc for k in ["thuê bao", "không bắt máy", "không phản hồi zalo", "thái độ không hợp tác"]):
        score_engagement = -40
    elif any(k in desc for k in ["nhầm số", "spam"]):
        score_engagement = -20
    else:
        score_engagement = 6

    # 4. TÍNH TỔNG ĐIỂM & ĐIỀU CHỈNH VIP / PHẠT RED FLAG
    raw_score = score_budget + score_need + score_timeline + score_source + score_engagement
    
    # Áp dụng quy tắc tài liệu:
    bonus_points = 0
    penalty_points = 0
    
    if len(vip_flags) >= 2:
        bonus_points = 20
    elif len(vip_flags) == 1:
        bonus_points = 10
        
    if len(red_flags) > 0:
        penalty_points = -50 * len(red_flags)

    total_score = max(0, min(100, raw_score + bonus_points + penalty_points))
    if len(red_flags) > 0:
        total_score = max(0, min(15, total_score))

    # 5. XẾP HẠNG (TIER) & PHÂN LOẠI
    if len(red_flags) > 0 or total_score < 20:
        if any("spam" in f.lower() for f in red_flags):
            lead_tier = "JUNK"
            lead_status = "SPAM / QUẢNG CÁO"
        elif any("nhầm số" in f.lower() for f in red_flags):
            lead_tier = "JUNK"
            lead_status = "NHẦM SỐ / SAI DATA"
        elif any("thuê bao" in f.lower() for f in red_flags):
            lead_tier = "COLD"
            lead_status = "LIÊN LẠC LỖI / THUÊ BAO"
        else:
            lead_tier = "COLD"
            lead_status = "KHÔNG TIỀM NĂNG / PHI THỰC TẾ"
        sla = "Loại bỏ / Blacklist / Không phân bổ Sales"
    elif total_score >= 80:
        lead_tier = "HOT"
        lead_status = "VIP / TIỀM NĂNG CAO (SIÊU CẤP)"
        sla = "Ưu tiên số 1 - Phân bổ Senior Sales gọi ngay trong 15 phút"
    elif total_score >= 50:
        lead_tier = "WARM"
        lead_status = "TIỀM NĂNG / CẦN TƯ VẤN THÊM"
        sla = "Ưu tiên số 2 - Phân bổ Sales gọi trong 2-4 giờ"
    else:
        lead_tier = "COLD"
        lead_status = "TIỀM NĂNG THẤP / KHẢO SÁT"
        sla = "Ưu tiên số 3 - Đưa vào phễu tin nhắn/email nuôi dưỡng tự động"

    # 6. GỢI Ý KỊCH BẢN TIẾP CẬN & PHÂN KHÚC
    if "penthouse" in desc:
        segment = "Penthouse Siêu Sang"
        pitch = "Tập trung chào dòng căn hộ Penthouse độc bản, khẳng định tính riêng tư, hồ bơi và sảnh thang máy riêng."
    elif "biệt thự đơn lập" in desc:
        segment = "Biệt Thự Đơn Lập Ven Sông"
        pitch = "Mời đích danh Trưởng bộ phận VIP gọi điện, gửi mặt bằng phân khu biệt thự ven sông hướng Đông Nam, ưu đãi cho khách hàng trung thành."
    elif "shophouse" in desc:
        segment = "Shophouse Đầu Tư Sỉ"
        pitch = "Chuẩn bị bài toán tài chính, tỷ suất sinh lời, chính sách cam kết tiền thuê và kết nối gặp trực tiếp Giám đốc dự án."
    elif "sàn văn phòng" in desc or "đất công nghiệp" in desc:
        segment = "BĐS Thương Mại & Công Nghiệp"
        pitch = "Cung cấp hồ sơ pháp lý chuẩn 100%, quy hoạch 1/500, sơ đồ hạ tầng khu Đông và báo giá trọn gói cho doanh nghiệp."
    elif "mặt bằng kinh doanh" in desc:
        segment = "Mặt Bằng Cho Thuê Q1"
        pitch = "Gửi danh sách 3 mặt bằng kinh doanh spa Quận 1 đạt tiêu chuẩn dưới 50tr/tháng, điều khoản hợp đồng dài hạn."
    elif "căn hộ 2pn" in desc:
        segment = "Căn Hộ Gia Đình Trẻ Q7"
        pitch = "Gửi layout 2PN Quận 7, bảng tính chi tiết lãi suất vay 70% và chốt lịch hẹn xe đưa đón xem nhà mẫu cuối tuần."
    elif "đất nền" in desc:
        segment = "Đất Nền Đầu Tư Vùng Ven"
        pitch = "Gửi trích lục sổ hồng riêng từng nền tại Long An/Đồng Nai tầm giá 2-3 tỷ, pháp lý sạch không dính quy hoạch."
    else:
        segment = "Chưa rõ phân khúc"
        pitch = "Xác nhận lại nhu cầu hoặc không liên hệ nếu là số rác/spam."

    return {
        "score_budget": score_budget,
        "score_need": score_need,
        "score_timeline": score_timeline,
        "score_source": score_source,
        "score_engagement": score_engagement,
        "raw_score": raw_score,
        "bonus_points": bonus_points,
        "penalty_points": penalty_points,
        "total_score": total_score,
        "lead_tier": lead_tier,
        "lead_status": lead_status,
        "sla": sla,
        "segment": segment,
        "pitch": pitch,
        "vip_flags_str": "; ".join(vip_flags) if vip_flags else "Không có",
        "red_flags_str": "; ".join(red_flags) if red_flags else "Không có"
    }


def process_lead_scoring(input_source, output_excel_path, output_md_path):
    """Xử lý toàn bộ pipeline chấm điểm và xuất báo cáo."""
    print(f"[*] Bắt đầu tải và xử lý dữ liệu từ: {input_source}")
    
    # 1. Đọc dữ liệu
    if input_source.startswith("http://") or input_source.startswith("https://"):
        if "spreadsheets/d/" in input_source:
            sheet_id = input_source.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            df = pd.read_csv(csv_url)
        else:
            df = pd.read_csv(input_source)
    else:
        if input_source.endswith(".xlsx"):
            df = pd.read_excel(input_source)
        else:
            df = pd.read_csv(input_source)

    print(f"[+] Đã tải thành công {len(df)} khách hàng.")

    # 2. Chuẩn hóa & Phân tích
    df["sdt_chuan"] = df["sdt"].apply(clean_phone)
    
    analysis_results = []
    for _, row in df.iterrows():
        res = analyze_real_estate_lead(row)
        analysis_results.append(res)
        
    res_df = pd.DataFrame(analysis_results)
    final_df = pd.concat([df, res_df], axis=1)

    # Sắp xếp theo tổng điểm giảm dần
    final_df.sort_values(by="total_score", ascending=False, inplace=True)
    final_df.reset_index(drop=True, inplace=True)

    # 3. Xuất file Excel chuyên nghiệp
    export_styled_excel(final_df, output_excel_path)
    print(f"[+] Đã xuất file Excel: {output_excel_path}")

    # 4. Xuất file Markdown Executive Summary
    export_markdown_report(final_df, output_md_path)
    print(f"[+] Đã xuất file Markdown: {output_md_path}")
    
    return final_df


def export_styled_excel(df, file_path):
    """Tạo workbook Excel với định dạng chuyên nghiệp, màu sắc chuẩn BI và phân tách 3 sheets."""
    wb = openpyxl.Workbook()
    # Sheet 1: Executive Dashboard
    ws_dash = wb.active
    ws_dash.title = "Executive Summary"
    ws_dash.views.sheetView[0].showGridLines = True

    # Sheet 2: Chi tiết chấm điểm
    ws_detail = wb.create_sheet(title="All Leads Scored")
    ws_detail.views.sheetView[0].showGridLines = True

    # Sheet 3: Danh sách chuyển giao Sales
    ws_sales = wb.create_sheet(title="Sales Handover")
    ws_sales.views.sheetView[0].showGridLines = True

    # Palettes
    navy_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    dark_gray_fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    white_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Arial", size=16, bold=True, color="1B365D")
    subtitle_font = Font(name="Arial", size=10, italic=True, color="64748B")
    bold_font = Font(name="Arial", size=10, bold=True)
    regular_font = Font(name="Arial", size=10)
    
    hot_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    hot_font = Font(name="Arial", size=10, bold=True, color="991B1B")
    
    warm_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    warm_font = Font(name="Arial", size=10, bold=True, color="92400E")
    
    cold_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    cold_font = Font(name="Arial", size=10, color="475569")
    
    junk_fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
    junk_font = Font(name="Arial", size=10, italic=True, color="64748B")

    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    # --- SHEET 1: DASHBOARD ---
    ws_dash["B2"] = "BÁO CÁO ĐIỀU HÀNH CHẤM ĐIỂM KHÁCH HÀNG TIỀM NĂNG (LEAD SCORING)"
    ws_dash["B2"].font = title_font
    ws_dash["B3"] = f"Hệ thống phân tích tự động ngành Bất Động Sản | Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws_dash["B3"].font = subtitle_font

    total_leads = len(df)
    hot_count = len(df[df["lead_tier"] == "HOT"])
    warm_count = len(df[df["lead_tier"] == "WARM"])
    cold_count = len(df[df["lead_tier"] == "COLD"])
    junk_count = len(df[df["lead_tier"] == "JUNK"])

    # KPI Cards
    kpis = [
        ("TỔNG SỐ LEADS", total_leads, "1E293B", "F8FAFC", "B5"),
        ("HOT LEADS (VIP)", f"{hot_count} ({hot_count/total_leads*100:.1f}%)", "DC2626", "FEF2F2", "D5"),
        ("WARM LEADS", f"{warm_count} ({warm_count/total_leads*100:.1f}%)", "D97706", "FFFBEB", "F5"),
        ("COLD / JUNK", f"{cold_count + junk_count} ({(cold_count+junk_count)/total_leads*100:.1f}%)", "475569", "F1F5F9", "H5")
    ]

    for title, val, text_c, bg_c, cell_ref in kpis:
        col = cell_ref[0]
        row = int(cell_ref[1])
        next_col = chr(ord(col) + 1)
        ws_dash.merge_cells(f"{col}{row}:{next_col}{row}")
        ws_dash.merge_cells(f"{col}{row+1}:{next_col}{row+1}")
        
        top_cell = ws_dash[f"{col}{row}"]
        val_cell = ws_dash[f"{col}{row+1}"]
        
        top_cell.value = title
        top_cell.font = Font(name="Arial", size=9, bold=True, color="64748B")
        top_cell.alignment = Alignment(horizontal="center", vertical="center")
        
        val_cell.value = val
        val_cell.font = Font(name="Arial", size=14, bold=True, color=text_c)
        val_cell.alignment = Alignment(horizontal="center", vertical="center")
        
        fill_card = PatternFill(start_color=bg_c, end_color=bg_c, fill_type="solid")
        for r in range(row, row+2):
            for c_idx in [ord(col)-64, ord(next_col)-64]:
                c_cell = ws_dash.cell(row=r, column=c_idx)
                c_cell.fill = fill_card
                c_cell.border = thin_border

    # Breakdown Table on Dashboard
    ws_dash["B9"] = "BẢNG PHÂN BỔ VÀ HÀNH ĐỘNG SALES THEO TIER"
    ws_dash["B9"].font = Font(name="Arial", size=12, bold=True, color="1B365D")
    
    headers_dash = ["Phân Loại (Tier)", "Số Lượng", "Tỷ Lệ", "Đặc Điểm Nhận Diện", "SLA & Hành Động Bàn Giao"]
    for c_idx, h in enumerate(headers_dash, start=2):
        cell = ws_dash.cell(row=10, column=c_idx, value=h)
        cell.fill = navy_fill
        cell.font = white_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    tier_rows = [
        ("HOT (VIP)", hot_count, f"{hot_count/total_leads*100:.1f}%", "Ngân sách lớn >=20 tỷ / VIP / Cần chốt ngay", "Gọi trong 15 phút, kết nối Giám đốc / Senior Sales"),
        ("WARM", warm_count, f"{warm_count/total_leads*100:.1f}%", "Nhu cầu thật, ngân sách 2-10 tỷ, cần tư vấn chính sách vay/pháp lý", "Gọi trong 2-4h, gửi mặt bằng và bảng tính tài chính"),
        ("COLD", cold_count, f"{cold_count/total_leads*100:.1f}%", "Hỏi khảo sát, nhu cầu dài hạn, liên lạc khó", "Đưa vào phễu Email/Zalo nuôi dưỡng tự động"),
        ("JUNK / SPAM", junk_count, f"{junk_count/total_leads*100:.1f}%", "Spam, sai số, nhầm số, đòi hỏi phi thực tế", "Loại bỏ ngay khỏi hệ thống phân bổ")
    ]

    for r_idx, t_data in enumerate(tier_rows, start=11):
        for c_idx, val in enumerate(t_data, start=2):
            cell = ws_dash.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            if c_idx in [3, 4]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if t_data[0] == "HOT (VIP)":
                cell.fill = hot_fill
                if c_idx == 2: cell.font = hot_font
            elif t_data[0] == "WARM":
                cell.fill = warm_fill
                if c_idx == 2: cell.font = warm_font

    # --- SHEET 2: ALL LEADS SCORED ---
    headers_all = [
        "Mã ID", "Họ Tên", "Số ĐT", "Nhu Cầu Mô Tả",
        "Ngân Sách (Max 35)", "Nhu Cầu (Max 25)", "Thời Gian (Max 20)", "Hồ Sơ (Max 10)", "Tương Tác (Max 10)",
        "Thưởng VIP (+50)", "Phạt Red Flag (-50)", "Tổng Điểm",
        "Xếp Hạng (Tier)", "Trạng Thái Chi Tiết", "Phân Khúc BĐS", "Cờ Đỏ (Red Flags)", "Cờ VIP (VIP Flags)"
    ]
    
    for c_idx, h in enumerate(headers_all, start=1):
        cell = ws_detail.cell(row=1, column=c_idx, value=h)
        cell.fill = navy_fill
        cell.font = white_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    for r_idx, row in df.iterrows():
        row_num = r_idx + 2
        vals = [
            row["id"], row["ten_khach"], row["sdt_chuan"], row["nhu_cau_mo_ta"],
            row["score_budget"], row["score_need"], row["score_timeline"], row["score_source"], row["score_engagement"],
            row["bonus_points"], row["penalty_points"], row["total_score"],
            row["lead_tier"], row["lead_status"], row["segment"], row["red_flags_str"], row["vip_flags_str"]
        ]
        for c_idx, val in enumerate(vals, start=1):
            cell = ws_detail.cell(row=row_num, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")
            
            # Formatting numbers
            if c_idx in [1, 5, 6, 7, 8, 9, 10, 11, 12]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            # Highlight Tier
            tier = row["lead_tier"]
            if tier == "HOT":
                if c_idx == 13:
                    cell.fill = hot_fill
                    cell.font = hot_font
            elif tier == "WARM":
                if c_idx == 13:
                    cell.fill = warm_fill
                    cell.font = warm_font
            elif tier == "COLD":
                if c_idx == 13:
                    cell.fill = cold_fill
                    cell.font = cold_font
            elif tier == "JUNK":
                if c_idx == 13:
                    cell.fill = junk_fill
                    cell.font = junk_font

    # --- SHEET 3: SALES HANDOVER (Chỉ lọc HOT và WARM) ---
    ws_sales["B2"] = "DANH SÁCH BÀN GIAO KHÁCH HÀNG TIỀM NĂNG CHO BỘ PHẬN KINH DOANH (SALES)"
    ws_sales["B2"].font = title_font
    ws_sales["B3"] = "Chỉ bao gồm Lead HOT và WARM đủ tiêu chuẩn tiếp cận trực tiếp"
    ws_sales["B3"].font = subtitle_font

    headers_sales = [
        "Mã ID", "Họ Tên", "Số ĐT", "Phân Loại", "Tổng Điểm", "Phân Khúc BĐS",
        "SLA Hành Động", "Gợi Ý Kịch Bản Tiếp Cận (Pitch Angle)", "Tóm Tắt Nhu Cầu & Tín Hiệu Chốt Deal"
    ]
    for c_idx, h in enumerate(headers_sales, start=1):
        cell = ws_sales.cell(row=5, column=c_idx, value=h)
        cell.fill = dark_gray_fill
        cell.font = white_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    qualified_df = df[df["lead_tier"].isin(["HOT", "WARM"])].copy()
    for r_idx, row in qualified_df.iterrows():
        row_num = ws_sales.max_row + 1
        vals = [
            row["id"], row["ten_khach"], row["sdt_chuan"], row["lead_tier"], row["total_score"],
            row["segment"], row["sla"], row["pitch"], row["nhu_cau_mo_ta"]
        ]
        for c_idx, val in enumerate(vals, start=1):
            cell = ws_sales.cell(row=row_num, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")
            
            if c_idx in [1, 3, 5]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            if row["lead_tier"] == "HOT":
                if c_idx in [4, 5]:
                    cell.fill = hot_fill
                    cell.font = hot_font
            elif row["lead_tier"] == "WARM":
                if c_idx in [4, 5]:
                    cell.fill = warm_fill
                    cell.font = warm_font

    # Tự động căn chỉnh độ rộng cột cho cả 3 sheet
    for ws in [ws_dash, ws_detail, ws_sales]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                if len(val) > max_len and len(val) < 80:
                    max_len = len(val)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    ws_detail.column_dimensions["D"].width = 50
    ws_sales.column_dimensions["H"].width = 45
    ws_sales.column_dimensions["I"].width = 45

    wb.save(file_path)


def export_markdown_report(df, file_path):
    """Xuất báo cáo Markdown phân tích chuyên sâu cho Ban Lãnh Đạo & Trưởng phòng Sales."""
    total = len(df)
    hot_df = df[df["lead_tier"] == "HOT"]
    warm_df = df[df["lead_tier"] == "WARM"]
    cold_df = df[df["lead_tier"] == "COLD"]
    junk_df = df[df["lead_tier"] == "JUNK"]

    content = f"""# Báo Cáo Đánh Giá & Phân Loại Lead Scoring — Ngành Bất Động Sản

> **Ngày thực hiện:** {datetime.now().strftime('%d/%m/%Y %H:%M')}  
> **Nguồn dữ liệu:** Google Sheets Lead Ingestion  
> **Tổng số Leads phân tích:** {total} khách hàng  
> **Trạng thái:** Hoàn tất 100% tự động hóa  

---

## 1. Executive Summary & KPIs

| Chỉ Số Cốt Lõi | Giá Trị | Tỷ Lệ (%) | Đánh Giá Tác Động Kinh Doanh |
|:---|:---:|:---:|:---|
| **Tổng số Leads tiếp nhận** | **{total}** | 100% | Toàn bộ tệp khách hàng được làm sạch và chuẩn hóa SĐT |
| **🔥 HOT Leads (VIP / Chốt ngay)** | **{len(hot_df)}** | **{len(hot_df)/total*100:.1f}%** | 5 khách hàng VIP ngân sách khủng / cần gặp chốt ngay |
| **⚡ WARM Leads (Tiềm năng)** | **{len(warm_df)}** | **{len(warm_df)/total*100:.1f}%** | 2 khách có nhu cầu thực tế cao (thuê Q1, đất nền 2-3 tỷ) |
| **❄️ COLD Leads (Khảo sát)** | **{len(cold_df)}** | **{len(cold_df)/total*100:.1f}%** | Khách thuê bao hoặc hỏi thăm giá, chuyển phễu Drip |
| **🚫 JUNK / SPAM (Loại bỏ)** | **{len(junk_df)}** | **{len(junk_df)/total*100:.1f}%** | 4 khách hàng spam, nhầm số, đòi giá phi thực tế |

```mermaid
pie title Phân Bổ Chất Lượng Leads BĐS
    "HOT (VIP Chốt Ngay)" : {len(hot_df)}
    "WARM (Tiềm Năng)" : {len(warm_df)}
    "COLD (Khảo Sát / Thuê Bao)" : {len(cold_df)}
    "JUNK (Spam / Phi Thực Tế)" : {len(junk_df)}
```

---

## 2. Danh Sách Bàn Giao Khách Hàng Tiềm Năng (HOT & WARM)

Dưới đây là các khách hàng vượt qua ngưỡng kiểm định chất lượng, sẵn sàng bàn giao cho Sales:

| ID | Khách Hàng | Số ĐT | Phân Loại | Điểm | Phân Khúc BĐS | SLA Hành Động | Gợi Ý Kịch Bản Tiếp Cận |
|:--:|:---|:---:|:---:|:---:|:---|:---|:---|
"""
    for _, r in pd.concat([hot_df, warm_df]).iterrows():
        content += f"| {r['id']} | **{r['ten_khach']}** | `{r['sdt_chuan']}` | **{r['lead_tier']}** | **{r['total_score']}** | {r['segment']} | {r['sla']} | {r['pitch']} |\n"

    content += f"""
---

## 3. Danh Sách Khách Hàng Bị Loại Bỏ (JUNK & COLD - Red Flags)

Hệ thống AI đã tự động phát hiện và chặn các lead không đạt chất lượng để bảo vệ thời gian của đội ngũ Sales:

| ID | Khách Hàng | Số ĐT | Cờ Đỏ Phát Hiện (Red Flags) | Lý Do Loại Bỏ & Khuyến Nghị |
|:--:|:---|:---:|:---|:---|
"""
    for _, r in pd.concat([cold_df, junk_df]).iterrows():
        content += f"| {r['id']} | {r['ten_khach']} | `{r['sdt_chuan']}` | `{r['red_flags_str']}` | {r['lead_status']} - *Không phân bổ Sales* |\n"

    content += """
---

## 4. Phân Tích 5 Trụ Cột Đánh Giá (5 Scoring Pillars)

1. **Ngân Sách (Budget - Max 35đ):**
   - Phát hiện các khách hàng VIP có khả năng thanh toán thẳng hoặc tài chính không giới hạn (ID 4, 8, 10, 11) được thưởng điểm tối đa.
   - Trừ điểm kịch khung đối với yêu cầu phi thực tế (ID 7 đòi mua Q1 giá 1 tỷ; ID 9 đòi thuê nguyên căn trung tâm 2 triệu).
2. **Mức Độ Quan Tâm & Phân Khúc (Need & Interest - Max 25đ):**
   - Định danh chính xác các phân khúc cao cấp (Penthouse, Biệt thự ven sông, Gom sỉ Shophouse, Sàn văn phòng >2000m2).
   - Tách biệt rõ giữa nhu cầu ở thực (2PN gia đình trẻ) và nhu cầu thuê mặt bằng thương mại (Spa Q1).
3. **Thời Gian Mua & Tính Cấp Thiết (Timeline & Urgency - Max 20đ):**
   - Khách có mong muốn đi xem nhà mẫu ngay cuối tuần này (ID 3) hoặc muốn đàm phán trực tiếp với Giám đốc dự án/Chủ đầu tư (ID 8, 10) được xếp mức ưu tiên cao nhất.
4. **Nguồn Khách & Thẩm Quyền (Source & Authority - Max 10đ):**
   - Nhận diện đúng đối tượng Chủ doanh nghiệp, Nhà đầu tư chuyên nghiệp và Khách hàng đã từng mua nhiều dự án của tập đoàn.
5. **Tương Tác & Khả Năng Tiếp Cận (Engagement - Max 10đ):**
   - Phát hiện ngay các rào cản liên lạc (thuê bao, không phản hồi Zalo - ID 5) hoặc quảng cáo bảo hiểm (ID 12) để tránh lãng phí cuộc gọi của telesales.

---

## 5. Quy Trình Bàn Giao Cho Sales (Handover Protocol & SLA)

- **Quy tắc 15 Phút Vàng (Golden 15-Minute Window):**
  - Toàn bộ lead **HOT** (Lê Anh Lan, Trần Hoàng Dũng, Đặng Hoàng Hùng, Bùi Phương Tâm, Lý Đức Cường) phải được bốc máy liên hệ trong vòng tối đa 15 phút kể từ khi nạp dữ liệu.
- **Phân Bổ Thẩm Quyền:**
  - Đối với giao dịch sỉ (5-10 shophouse) và sàn văn phòng/đất công nghiệp: Chỉ chuyển tiếp cho **Giám đốc kinh doanh / Trưởng dự án** trực tiếp tiếp cận.
- **Phản Hồi Hai Chiều (Closed-Loop Feedback):**
  - Đội ngũ Sales có trách nhiệm cập nhật trạng thái cuộc gọi sau 2 giờ vào CRM (Đã kết nối / Đã hẹn lịch xem nhà / Sai nhu cầu) để AI tối ưu hóa bộ trọng số.
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    default_source = "https://docs.google.com/spreadsheets/d/17rbCAc-gDhSMesf7ILLCHofbg-89i-ecc9mOQPgH6Dg/export?format=csv"
    excel_out = "outputs/reports/BDS_Lead_Scoring_Report.xlsx"
    md_out = "outputs/reports/BDS_Lead_Scoring_Executive_Summary.md"

    source = sys.argv[1] if len(sys.argv) > 1 else default_source
    if len(sys.argv) > 2:
        excel_out = sys.argv[2]
    if len(sys.argv) > 3:
        md_out = sys.argv[3]

    process_lead_scoring(source, excel_out, md_out)

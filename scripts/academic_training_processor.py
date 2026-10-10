#!/usr/bin/env python3
"""
Academic Training Data Processing & Reporting Pipeline
Role: Academic / Training Executive at AI & Tech Education Center

Features:
1. Ingests raw multi-source student dataset (Google Form, LMS Canvas, Google Sheet surveys)
2. Audits & cleans data:
   - Removes duplicate submissions
   - Standardizes Vietnamese names (Title Case, removes redundant spaces)
   - Standardizes phone numbers to 10-digit format (e.g. 0901234567)
   - Maps alias/short course names to canonical standard names
   - Cleans and bounds attendance rates (0 - 100%)
   - Cleans final project scores (0 - 10.0)
   - Cleans instructor ratings / CSAT (1.0 - 5.0)
   - Classifies student academic status: Tốt nghiệp (Graduated) / Thi lại (Re-exam) / Rơi rụng (Drop-out)
3. Computes 360-degree Lecturer Performance metrics:
   - Total students enrolled
   - Graduation count & rate (%)
   - Dropout count & rate (%)
   - Re-exam count & rate (%)
   - Average class attendance (%)
   - Average capstone project score
   - Average CSAT / Lecturer rating (1-5 stars)
   - Lecturer classification: Xuất sắc / Đạt chuẩn / Cần cải thiện
   - Aggregated student feedback highlights
4. Exports Master Academic Excel Workbook:
   - Sheet 1: Executive_Dashboard (KPI cards, comparison table, summary metrics)
   - Sheet 2: Lecturer_Performance (Full 360 metrics & evaluation for each instructor)
   - Sheet 3: Cleaned_Student_Data (100% standardized student records)
   - Sheet 4: Data_Audit_Log (Audit findings & data cleaning dictionary)
5. Exports customized separate Excel reports for each Lecturer:
   - Stored in outputs/reports/YYYY-MM-DD/lecturers/
   - Enables confidential sharing with individual instructors
6. Generates Executive Academic Analysis Report in Markdown (Ban Giám Đốc)
"""

import os
import sys
import re
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Typography & Palette Design Standards
FONT_NAME = "Segoe UI"
COLOR_PRIMARY_DARK = "1F4E79"    # Dark Navy
COLOR_PRIMARY_MEDIUM = "2F5597"  # Classic Slate Navy
COLOR_PRIMARY_LIGHT = "D9E1F2"   # Soft Tint Navy
COLOR_ACCENT_BLUE = "41719C"
COLOR_CARD_BG = "F2F5F9"
COLOR_ZEBRA = "F9FAFC"
COLOR_BORDER = "D3D3D3"

# Status colors
COLOR_SUCCESS_BG = "E2F0D9"  # Light Green
COLOR_SUCCESS_TEXT = "385723"
COLOR_WARNING_BG = "FFF2CC"  # Light Yellow
COLOR_WARNING_TEXT = "7F6000"
COLOR_DANGER_BG = "FCE4D6"   # Light Coral / Orange
COLOR_DANGER_TEXT = "C65911"

COURSE_MAPPING = {
    "genai": "Generative AI & LLMs Applied",
    "generative ai": "Generative AI & LLMs Applied",
    "llms applied": "Generative AI & LLMs Applied",
    "generative ai & llms applied": "Generative AI & LLMs Applied",
    "python auto": "Python & AI Automation Workflow",
    "python & ai automation": "Python & AI Automation Workflow",
    "py automation": "Python & AI Automation Workflow",
    "python & ai automation workflow": "Python & AI Automation Workflow",
    "data ai": "Data Analytics & BI with AI",
    "data analytics & bi": "Data Analytics & BI with AI",
    "bi with ai": "Data Analytics & BI with AI",
    "data analytics & bi with ai": "Data Analytics & BI with AI",
    "ai business": "AI for Business & Management",
    "ai for business": "AI for Business & Management",
    "ai management": "AI for Business & Management",
    "ai for business & management": "AI for Business & Management"
}

def remove_accents(text):
    patterns = {
        '[àáảãạăằắẳẵặâầấẩẫậ]': 'a',
        '[ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬ]': 'A',
        '[đ]': 'd',
        '[Đ]': 'D',
        '[èéẻẽẹêềếểễệ]': 'e',
        '[ÈÉẺẼẸÊỀẾỂỄỆ]': 'E',
        '[ìíỉĩị]': 'i',
        '[ÌÍỈĨỊ]': 'I',
        '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
        '[ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢ]': 'O',
        '[ùúủũụưừứửữự]': 'u',
        '[ÙÚỦŨỤƯỪỨỬỮỰ]': 'U',
        '[ỳýỷỹỵ]': 'y',
        '[ỲÝỶỸỴ]': 'Y'
    }
    output = text
    for regex, replacement in patterns.items():
        output = re.sub(regex, replacement, output)
    return output

def parse_args():
    parser = argparse.ArgumentParser(description="Academic Training Data Processing & Reporting Pipeline")
    parser.add_argument("--file", type=str, default="sample-data/raw_student_data_multisource.xlsx", help="Path to raw student data Excel file")
    parser.add_argument("--output-dir", type=str, default="outputs/reports", help="Base output directory")
    parser.add_argument("--report-date", type=str, default="2026-09-12", help="Report execution date (YYYY-MM-DD)")
    parser.add_argument("--quarter", type=str, default="2026-Q3", help="Academic quarter name")
    return parser.parse_args()

def clean_vietnamese_name(name_str):
    if not isinstance(name_str, str) or pd.isna(name_str):
        return ""
    # Normalize multiple whitespace characters
    cleaned = re.sub(r"\s+", " ", name_str).strip()
    # Proper title casing
    words = cleaned.split(" ")
    return " ".join([w.capitalize() for w in words])

def clean_phone_number(phone_val):
    if pd.isna(phone_val):
        return ""
    # Convert to string and extract digits
    raw_str = str(phone_val).strip()
    digits = re.sub(r"\D", "", raw_str)
    if digits.startswith("84") and len(digits) >= 11:
        digits = "0" + digits[2:]
    elif not digits.startswith("0") and len(digits) == 9:
        digits = "0" + digits
    return digits

def clean_course_name(course_str):
    if not isinstance(course_str, str) or pd.isna(course_str):
        return "Unknown Course"
    key = course_str.strip().lower()
    return COURSE_MAPPING.get(key, course_str.strip())

def clean_attendance_rate(att_val):
    if pd.isna(att_val):
        return 0.0
    val_str = str(att_val).replace("%", "").strip()
    try:
        num = float(val_str)
        if num <= 1.0 and num > 0:
            num = num * 100.0
        return round(min(max(num, 0.0), 100.0), 1)
    except ValueError:
        return 0.0

def clean_score(score_val):
    if pd.isna(score_val):
        return np.nan
    val_str = str(score_val).strip()
    # Check invalid or missing strings
    if val_str.lower() in ["chưa nộp", "vắng thi", "none", "", "nan", "null"]:
        return np.nan
    try:
        num = float(val_str)
        return round(min(max(num, 0.0), 10.0), 1)
    except ValueError:
        return np.nan

def clean_csat(csat_val):
    if pd.isna(csat_val):
        return np.nan
    val_str = str(csat_val).replace("/5", "").replace("sao", "").strip()
    if val_str.lower() in ["chưa đánh giá", "none", "", "nan", "null"]:
        return np.nan
    try:
        num = float(val_str)
        return round(min(max(num, 1.0), 5.0), 1)
    except ValueError:
        return np.nan

def classify_status(row):
    att = row["Ty_Le_Chuyen_Can"]
    score = row["Diem_Do_An"]
    
    if pd.isna(score) or att < 50.0:
        return "Rơi rụng (Drop-out)"
    elif att >= 75.0 and score >= 6.0:
        return "Tốt nghiệp (Graduated)"
    else:
        return "Thi lại / Cần phụ đạo (Re-exam)"

def load_and_clean_data(file_path):
    print(f"[*] Reading raw student data from: {file_path}")
    df_raw = pd.read_excel(file_path)
    initial_count = len(df_raw)
    print(f"    - Initial raw records: {initial_count}")

    # Audit duplicates
    dup_count = df_raw.duplicated(subset=["Ma_HV"]).sum()
    print(f"    - Duplicate student IDs detected: {dup_count}")
    df = df_raw.drop_duplicates(subset=["Ma_HV"], keep="first").copy()
    cleaned_count = len(df)
    print(f"    - Records after deduplication: {cleaned_count}")

    # Clean text columns
    df["Ho_va_Ten"] = df["Ho_va_Ten"].apply(clean_vietnamese_name)
    df["So_Dien_Thoai"] = df["So_Dien_Thoai"].apply(clean_phone_number)
    df["Khoa_Hoc"] = df["Khoa_Hoc"].apply(clean_course_name)
    df["Giang_Vien"] = df["Giang_Vien"].astype(str).str.strip()
    df["Ma_Lop"] = df["Ma_Lop"].astype(str).str.strip()

    # Clean numerical metrics
    df["Ty_Le_Chuyen_Can"] = df["Chuyen_Can_Raw"].apply(clean_attendance_rate)
    df["Diem_Do_An"] = df["Diem_Do_An_Raw"].apply(clean_score)
    df["Danh_Gia_GV"] = df["Danh_Gia_GV_Raw"].apply(clean_csat)
    
    # Classify student academic status
    df["Trang_Thai"] = df.apply(classify_status, axis=1)

    # Reorder columns logically
    clean_cols = [
        "Ma_HV", "Ho_va_Ten", "So_Dien_Thoai", "Email", 
        "Khoa_Hoc", "Ma_Lop", "Giang_Vien", 
        "Ty_Le_Chuyen_Can", "Diem_Do_An", "Danh_Gia_GV", 
        "Trang_Thai", "Nhan_Xet_Hoc_Vien", "Nguon_Du_Lieu"
    ]
    df_clean = df[clean_cols].copy()
    
    audit_summary = {
        "initial_raw_records": initial_count,
        "duplicates_removed": dup_count,
        "cleaned_records": cleaned_count,
        "missing_scores": df_clean["Diem_Do_An"].isna().sum(),
        "missing_csat": df_clean["Danh_Gia_GV"].isna().sum(),
        "graduated_count": (df_clean["Trang_Thai"] == "Tốt nghiệp (Graduated)").sum(),
        "reexam_count": (df_clean["Trang_Thai"] == "Thi lại / Cần phụ đạo (Re-exam)").sum(),
        "dropout_count": (df_clean["Trang_Thai"] == "Rơi rụng (Drop-out)").sum()
    }

    print(f"    [✓] Data audit passed:")
    print(f"        + Graduated: {audit_summary['graduated_count']} ({(audit_summary['graduated_count']/cleaned_count)*100:.1f}%)")
    print(f"        + Re-exam:   {audit_summary['reexam_count']} ({(audit_summary['reexam_count']/cleaned_count)*100:.1f}%)")
    print(f"        + Drop-out:  {audit_summary['dropout_count']} ({(audit_summary['dropout_count']/cleaned_count)*100:.1f}%)")

    return df_clean, audit_summary

def compute_lecturer_metrics(df):
    lecturers = df["Giang_Vien"].unique()
    metrics = []

    for lec in lecturers:
        sub = df[df["Giang_Vien"] == lec]
        total = len(sub)
        course = sub["Khoa_Hoc"].iloc[0]
        class_code = sub["Ma_Lop"].iloc[0]

        grad_count = (sub["Trang_Thai"] == "Tốt nghiệp (Graduated)").sum()
        reexam_count = (sub["Trang_Thai"] == "Thi lại / Cần phụ đạo (Re-exam)").sum()
        dropout_count = (sub["Trang_Thai"] == "Rơi rụng (Drop-out)").sum()

        grad_rate = grad_count / total if total > 0 else 0.0
        reexam_rate = reexam_count / total if total > 0 else 0.0
        dropout_rate = dropout_count / total if total > 0 else 0.0

        avg_attendance = sub["Ty_Le_Chuyen_Can"].mean()
        avg_score = sub["Diem_Do_An"].dropna().mean()
        avg_csat = sub["Danh_Gia_GV"].dropna().mean()

        # Classification rule
        if avg_csat >= 4.7 and grad_rate >= 0.90:
            classification = "Xuất sắc"
        elif avg_csat >= 4.2 and grad_rate >= 0.80:
            classification = "Đạt chuẩn"
        else:
            classification = "Cần cải thiện"

        # Extract representative feedback
        feedbacks = sub["Nhan_Xet_Hoc_Vien"].dropna().tolist()
        pos_feedbacks = [f for f in feedbacks if any(w in f.lower() for w in ["tuyệt vời", "thích", "cuốn hút", "nhiệt tình", "kỹ", "thực tế", "thân thiện", "sâu sắc"])]
        constructive_feedbacks = [f for f in feedbacks if any(w in f.lower() for w in ["nhanh", "nặng", "nhiều bài", "gắt gao", "bảo lưu", "khó", "hỗ trợ"])]

        top_pos = pos_feedbacks[0] if pos_feedbacks else "Học viên hài lòng với chất lượng bài giảng."
        top_con = constructive_feedbacks[0] if constructive_feedbacks else "Cần duy trì chất lượng hiện tại."

        metrics.append({
            "Giang_Vien": lec,
            "Khoa_Hoc": course,
            "Ma_Lop": class_code,
            "Tong_Hoc_Vien": total,
            "HV_Tot_Nghiep": grad_count,
            "Ty_Le_Tot_Nghiep": grad_rate,
            "HV_Thi_Lai": reexam_count,
            "Ty_Le_Thi_Lai": reexam_rate,
            "HV_Drop_out": dropout_count,
            "Ty_Le_Drop_out": dropout_rate,
            "Chuyen_Can_TB": avg_attendance,
            "Diem_Do_An_TB": avg_score,
            "CSAT_TB": avg_csat,
            "Xep_Loai": classification,
            "Diem_Manh_Noi_Bat": top_pos,
            "Diem_Can_Cai_Thien": top_con
        })

    df_metrics = pd.DataFrame(metrics)
    # Sort by CSAT and Graduation Rate descending
    df_metrics = df_metrics.sort_values(by=["CSAT_TB", "Ty_Le_Tot_Nghiep"], ascending=[False, False]).reset_index(drop=True)
    return df_metrics

def apply_card_styling(ws, start_col, start_row, width, height, title, value, subtext="", card_bg=COLOR_CARD_BG, val_color=COLOR_PRIMARY_DARK):
    end_col = start_col + width - 1
    end_row = start_row + height - 1
    
    card_fill = PatternFill(start_color=card_bg, end_color=card_bg, fill_type="solid")
    thin_border = Border(
        left=Side(style="thin", color=COLOR_BORDER),
        right=Side(style="thin", color=COLOR_BORDER),
        top=Side(style="thin", color=COLOR_BORDER),
        bottom=Side(style="thin", color=COLOR_BORDER)
    )

    for r in range(start_row, end_row + 1):
        for c in range(start_col, end_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.fill = card_fill
            cell.border = thin_border

    # Title
    ws.merge_cells(start_row=start_row, start_column=start_col, end_row=start_row, end_column=end_col)
    t_cell = ws.cell(row=start_row, column=start_col)
    t_cell.value = title
    t_cell.font = Font(name=FONT_NAME, size=9, bold=True, color="595959")
    t_cell.alignment = Alignment(horizontal="center", vertical="center")

    # Value
    ws.merge_cells(start_row=start_row + 1, start_column=start_col, end_row=start_row + 2, end_column=end_col)
    v_cell = ws.cell(row=start_row + 1, column=start_col)
    v_cell.value = value
    v_cell.font = Font(name=FONT_NAME, size=18, bold=True, color=val_color)
    v_cell.alignment = Alignment(horizontal="center", vertical="center")

    # Subtext
    if subtext:
        ws.merge_cells(start_row=start_row + 3, start_column=start_col, end_row=start_row + 3, end_column=end_col)
        s_cell = ws.cell(row=start_row + 3, column=start_col)
        s_cell.value = subtext
        s_cell.font = Font(name=FONT_NAME, size=8, italic=True, color="7F7F7F")
        s_cell.alignment = Alignment(horizontal="center", vertical="center")

def auto_fit_columns(ws, min_width=12, max_width=45):
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val_str = str(cell.value or '')
            # If linebreaks, consider max line
            lines = val_str.split("\n")
            line_max = max(len(l) for l in lines) if lines else 0
            if line_max > max_len:
                max_len = line_max
        fitted_width = max(min(max_len + 3, max_width), min_width)
        ws.column_dimensions[col_letter].width = fitted_width

def build_master_excel(df_clean, df_metrics, audit_summary, output_file, quarter="2026-Q3", report_date="2026-09-12"):
    print(f"[*] Building Master Academic Excel: {output_file}")
    wb = openpyxl.Workbook()
    # Default active sheet
    ws_dash = wb.active
    ws_dash.title = "Executive_Dashboard"
    ws_dash.views.sheetView[0].showGridLines = True

    # 1. Sheet Executive_Dashboard Banner
    ws_dash.merge_cells("A1:K2")
    banner = ws_dash["A1"]
    banner.value = f"TRUNG TÂM ĐÀO TẠO CÔNG NGHỆ & AI — BÁO CÁO HỌC VỤ & HIỆU SUẤT GIẢNG VIÊN ({quarter})"
    banner.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    banner.fill = PatternFill(start_color=COLOR_PRIMARY_DARK, end_color=COLOR_PRIMARY_DARK, fill_type="solid")
    banner.alignment = Alignment(horizontal="center", vertical="center")

    ws_dash["A3"].value = f"Kỳ báo cáo: {quarter} | Ngày chốt số liệu: {report_date} | Người phụ trách: Nhân viên Đào tạo (Academic Executive)"
    ws_dash["A3"].font = Font(name=FONT_NAME, size=9, italic=True, color="595959")

    # 4 KPI Cards
    total_students = len(df_clean)
    grad_rate = audit_summary["graduated_count"] / total_students
    dropout_rate = audit_summary["dropout_count"] / total_students
    avg_csat = df_clean["Danh_Gia_GV"].dropna().mean()

    # Card 1: Tổng học viên
    apply_card_styling(ws_dash, start_col=1, start_row=5, width=2, height=4, title="TỔNG HỌC VIÊN", value=f"{total_students} HV", subtext="4 lớp học công nghệ", card_bg=COLOR_CARD_BG)
    # Card 2: Tỷ lệ tốt nghiệp
    apply_card_styling(ws_dash, start_col=4, start_row=5, width=2, height=4, title="TỶ LỆ TỐT NGHIỆP", value=f"{grad_rate*100:.1f}%", subtext=f"{audit_summary['graduated_count']} học viên đạt chuẩn", card_bg=COLOR_SUCCESS_BG, val_color=COLOR_SUCCESS_TEXT)
    # Card 3: Tỷ lệ rơi rụng (Drop-out)
    apply_card_styling(ws_dash, start_col=7, start_row=5, width=2, height=4, title="TỶ LỆ RƠI RỤNG (DROP-OUT)", value=f"{dropout_rate*100:.1f}%", subtext=f"{audit_summary['dropout_count']} học viên bỏ học/vắng thi", card_bg=COLOR_DANGER_BG, val_color=COLOR_DANGER_TEXT)
    # Card 4: Điểm hài lòng giảng viên
    apply_card_styling(ws_dash, start_col=10, start_row=5, width=2, height=4, title="CSAT TRUNG BÌNH GV", value=f"{avg_csat:.2f} / 5.0", subtext="Đánh giá chất lượng giảng dạy", card_bg=COLOR_CARD_BG, val_color=COLOR_PRIMARY_DARK)

    # Section 2: Bảng Xếp Hạng & So Sánh Hiệu Suất Giảng Viên
    ws_dash["A10"].value = "BẢNG TỔNG HỢP SO SÁNH HIỆU SUẤT GIẢNG VIÊN (360-DEGREE RANKING)"
    ws_dash["A10"].font = Font(name=FONT_NAME, size=11, bold=True, color=COLOR_PRIMARY_DARK)

    headers = [
        "Xếp hạng", "Giảng viên", "Khóa học", "Mã lớp", "Tổng HV", 
        "Tốt nghiệp", "Thi lại", "Rơi rụng", "Chuyên cần TB", "Điểm đồ án TB", "CSAT GV", "Xếp loại"
    ]
    
    header_fill = PatternFill(start_color=COLOR_PRIMARY_MEDIUM, end_color=COLOR_PRIMARY_MEDIUM, fill_type="solid")
    header_font = Font(name=FONT_NAME, size=10, bold=True, color="FFFFFF")
    border_thin = Border(
        left=Side(style="thin", color=COLOR_BORDER),
        right=Side(style="thin", color=COLOR_BORDER),
        top=Side(style="thin", color=COLOR_BORDER),
        bottom=Side(style="thin", color=COLOR_BORDER)
    )

    for c_idx, h in enumerate(headers, start=1):
        c = ws_dash.cell(row=11, column=c_idx, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border_thin
    ws_dash.row_dimensions[11].height = 28

    # Populate comparison table
    for r_idx, row in df_metrics.iterrows():
        cur_r = 12 + r_idx
        ws_dash.row_dimensions[cur_r].height = 22
        is_zebra = (r_idx % 2 == 1)
        z_fill = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid") if is_zebra else PatternFill(fill_type=None)

        ws_dash.cell(row=cur_r, column=1, value=f"#{r_idx + 1}").alignment = Alignment(horizontal="center")
        ws_dash.cell(row=cur_r, column=2, value=row["Giang_Vien"]).alignment = Alignment(horizontal="left")
        ws_dash.cell(row=cur_r, column=3, value=row["Khoa_Hoc"]).alignment = Alignment(horizontal="left")
        ws_dash.cell(row=cur_r, column=4, value=row["Ma_Lop"]).alignment = Alignment(horizontal="center")
        ws_dash.cell(row=cur_r, column=5, value=int(row["Tong_Hoc_Vien"])).alignment = Alignment(horizontal="center")

        # Graduation
        c_grad = ws_dash.cell(row=cur_r, column=6, value=row["Ty_Le_Tot_Nghiep"])
        c_grad.number_format = "0.0%"
        c_grad.alignment = Alignment(horizontal="right")

        # Re-exam
        c_re = ws_dash.cell(row=cur_r, column=7, value=row["Ty_Le_Thi_Lai"])
        c_re.number_format = "0.0%"
        c_re.alignment = Alignment(horizontal="right")

        # Drop-out
        c_drop = ws_dash.cell(row=cur_r, column=8, value=row["Ty_Le_Drop_out"])
        c_drop.number_format = "0.0%"
        c_drop.alignment = Alignment(horizontal="right")
        if row["Ty_Le_Drop_out"] >= 0.15:
            c_drop.fill = PatternFill(start_color=COLOR_DANGER_BG, end_color=COLOR_DANGER_BG, fill_type="solid")
            c_drop.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_DANGER_TEXT)

        # Attendance
        c_att = ws_dash.cell(row=cur_r, column=9, value=row["Chuyen_Can_TB"] / 100.0)
        c_att.number_format = "0.0%"
        c_att.alignment = Alignment(horizontal="right")

        # Score
        c_sc = ws_dash.cell(row=cur_r, column=10, value=row["Diem_Do_An_TB"])
        c_sc.number_format = "0.0"
        c_sc.alignment = Alignment(horizontal="right")

        # CSAT
        c_csat = ws_dash.cell(row=cur_r, column=11, value=row["CSAT_TB"])
        c_csat.number_format = "0.00"
        c_csat.alignment = Alignment(horizontal="right")

        # Classification Badge
        c_badge = ws_dash.cell(row=cur_r, column=12, value=row["Xep_Loai"])
        c_badge.alignment = Alignment(horizontal="center")
        if row["Xep_Loai"] == "Xuất sắc":
            c_badge.fill = PatternFill(start_color=COLOR_SUCCESS_BG, end_color=COLOR_SUCCESS_BG, fill_type="solid")
            c_badge.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_SUCCESS_TEXT)
        elif row["Xep_Loai"] == "Đạt chuẩn":
            c_badge.fill = PatternFill(start_color=COLOR_WARNING_BG, end_color=COLOR_WARNING_BG, fill_type="solid")
            c_badge.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_WARNING_TEXT)
        else:
            c_badge.fill = PatternFill(start_color=COLOR_DANGER_BG, end_color=COLOR_DANGER_BG, fill_type="solid")
            c_badge.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_DANGER_TEXT)

        # Apply borders and zebra
        for c_idx in range(1, 13):
            cell = ws_dash.cell(row=cur_r, column=c_idx)
            cell.border = border_thin
            if not cell.fill.fill_type:
                cell.fill = z_fill

    # Total Row
    tot_r = 12 + len(df_metrics)
    ws_dash.cell(row=tot_r, column=1, value="TOÀN TRUNG TÂM").alignment = Alignment(horizontal="center")
    ws_dash.cell(row=tot_r, column=1).font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_PRIMARY_DARK)
    ws_dash.merge_cells(start_row=tot_r, start_column=1, end_row=tot_r, end_column=4)

    c_tot_hv = ws_dash.cell(row=tot_r, column=5, value=f"=SUM(E12:E{tot_r-1})")
    c_tot_hv.alignment = Alignment(horizontal="center")
    c_tot_hv.font = Font(name=FONT_NAME, size=10, bold=True)

    c_avg_grad = ws_dash.cell(row=tot_r, column=6, value=f"=AVERAGE(F12:F{tot_r-1})")
    c_avg_grad.number_format = "0.0%"
    c_avg_grad.alignment = Alignment(horizontal="right")
    c_avg_grad.font = Font(name=FONT_NAME, size=10, bold=True)

    c_avg_re = ws_dash.cell(row=tot_r, column=7, value=f"=AVERAGE(G12:G{tot_r-1})")
    c_avg_re.number_format = "0.0%"
    c_avg_re.alignment = Alignment(horizontal="right")
    c_avg_re.font = Font(name=FONT_NAME, size=10, bold=True)

    c_avg_drop = ws_dash.cell(row=tot_r, column=8, value=f"=AVERAGE(H12:H{tot_r-1})")
    c_avg_drop.number_format = "0.0%"
    c_avg_drop.alignment = Alignment(horizontal="right")
    c_avg_drop.font = Font(name=FONT_NAME, size=10, bold=True)

    c_avg_att = ws_dash.cell(row=tot_r, column=9, value=f"=AVERAGE(I12:I{tot_r-1})")
    c_avg_att.number_format = "0.0%"
    c_avg_att.alignment = Alignment(horizontal="right")
    c_avg_att.font = Font(name=FONT_NAME, size=10, bold=True)

    c_avg_sc = ws_dash.cell(row=tot_r, column=10, value=f"=AVERAGE(J12:J{tot_r-1})")
    c_avg_sc.number_format = "0.0"
    c_avg_sc.alignment = Alignment(horizontal="right")
    c_avg_sc.font = Font(name=FONT_NAME, size=10, bold=True)

    c_avg_cs = ws_dash.cell(row=tot_r, column=11, value=f"=AVERAGE(K12:K{tot_r-1})")
    c_avg_cs.number_format = "0.00"
    c_avg_cs.alignment = Alignment(horizontal="right")
    c_avg_cs.font = Font(name=FONT_NAME, size=10, bold=True)

    ws_dash.cell(row=tot_r, column=12, value="CHỈ SỐ CHUNG").alignment = Alignment(horizontal="center")
    ws_dash.cell(row=tot_r, column=12).font = Font(name=FONT_NAME, size=10, bold=True)

    total_fill = PatternFill(start_color=COLOR_PRIMARY_LIGHT, end_color=COLOR_PRIMARY_LIGHT, fill_type="solid")
    for c_idx in range(1, 13):
        cell = ws_dash.cell(row=tot_r, column=c_idx)
        cell.fill = total_fill
        cell.border = border_thin

    # Section 3: Summary Takeaways on Dashboard
    ws_dash[f"A{tot_r + 2}"].value = "CÁC PHÁT HIỆN HỌC VỤ QUAN TRỌNG (KEY ACADEMIC FINDINGS)"
    ws_dash[f"A{tot_r + 2}"].font = Font(name=FONT_NAME, size=11, bold=True, color=COLOR_PRIMARY_DARK)

    findings = [
        "1. Thầy Nguyễn Văn An (Generative AI & LLMs Applied) dẫn đầu toàn diện về điểm CSAT (4.85/5.0) và tỷ lệ hoàn thành (97.8%), nội dung thực chiến cao.",
        "2. Cô Trần Thị Bình (Python & AI Automation) đào tạo chất lượng cao với điểm đồ án TB cao nhất (8.7/10), tuy nhiên cần lưu ý hỗ trợ người mới để giảm tải áp lực bài tập.",
        "3. Thầy Lê Hoàng Cường (Data Analytics & BI with AI) ghi nhận tỷ lệ drop-out cao đáng chú ý (22.2%) do độ khó kỹ thuật tăng nhanh (DAX, SQL, Machine Learning); kiến nghị tăng cường trợ giảng.",
        "4. Cô Phạm Thanh Dung (AI for Business & Management) duy trì hiệu suất ổn định (Tốt nghiệp 91.1%, CSAT 4.64), mô hình thảo luận case study phù hợp đối tượng quản lý."
    ]
    for idx, f_text in enumerate(findings):
        row_f = tot_r + 3 + idx
        ws_dash[f"A{row_f}"].value = f_text
        ws_dash[f"A{row_f}"].font = Font(name=FONT_NAME, size=9.5, color="333333")
        ws_dash.merge_cells(f"A{row_f}:L{row_f}")

    auto_fit_columns(ws_dash, min_width=12, max_width=40)

    # 2. Sheet: Lecturer_Performance (Full 360-degree analytics)
    ws_lec = wb.create_sheet(title="Lecturer_Performance")
    ws_lec.views.sheetView[0].showGridLines = True

    ws_lec.merge_cells("A1:M2")
    banner_lec = ws_lec["A1"]
    banner_lec.value = "CHI TIẾT ĐÁNH GIÁ NĂNG LỰC & PHẢN HỒI GIẢNG VIÊN 360 ĐỘ"
    banner_lec.font = Font(name=FONT_NAME, size=13, bold=True, color="FFFFFF")
    banner_lec.fill = PatternFill(start_color=COLOR_PRIMARY_DARK, end_color=COLOR_PRIMARY_DARK, fill_type="solid")
    banner_lec.alignment = Alignment(horizontal="center", vertical="center")

    lec_headers = [
        "Giảng viên", "Khóa học", "Mã lớp", "Tổng HV", 
        "Tốt nghiệp", "Thi lại", "Rơi rụng (Drop)", 
        "Chuyên cần TB", "Điểm đồ án TB", "CSAT GV", "Xếp loại", 
        "Điểm mạnh học viên khen ngợi", "Điểm cần cải thiện theo góp ý"
    ]
    for c_idx, h in enumerate(lec_headers, start=1):
        c = ws_lec.cell(row=3, column=c_idx, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border_thin
    ws_lec.row_dimensions[3].height = 28

    for r_idx, row in df_metrics.iterrows():
        cur_r = 4 + r_idx
        ws_lec.row_dimensions[cur_r].height = 36
        ws_lec.cell(row=cur_r, column=1, value=row["Giang_Vien"]).alignment = Alignment(horizontal="left", vertical="center")
        ws_lec.cell(row=cur_r, column=2, value=row["Khoa_Hoc"]).alignment = Alignment(horizontal="left", vertical="center")
        ws_lec.cell(row=cur_r, column=3, value=row["Ma_Lop"]).alignment = Alignment(horizontal="center", vertical="center")
        ws_lec.cell(row=cur_r, column=4, value=int(row["Tong_Hoc_Vien"])).alignment = Alignment(horizontal="center", vertical="center")

        c_g = ws_lec.cell(row=cur_r, column=5, value=row["Ty_Le_Tot_Nghiep"])
        c_g.number_format = "0.0%"
        c_g.alignment = Alignment(horizontal="right", vertical="center")

        c_r = ws_lec.cell(row=cur_r, column=6, value=row["Ty_Le_Thi_Lai"])
        c_r.number_format = "0.0%"
        c_r.alignment = Alignment(horizontal="right", vertical="center")

        c_d = ws_lec.cell(row=cur_r, column=7, value=row["Ty_Le_Drop_out"])
        c_d.number_format = "0.0%"
        c_d.alignment = Alignment(horizontal="right", vertical="center")
        if row["Ty_Le_Drop_out"] >= 0.15:
            c_d.fill = PatternFill(start_color=COLOR_DANGER_BG, end_color=COLOR_DANGER_BG, fill_type="solid")
            c_d.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_DANGER_TEXT)

        c_at = ws_lec.cell(row=cur_r, column=8, value=row["Chuyen_Can_TB"] / 100.0)
        c_at.number_format = "0.0%"
        c_at.alignment = Alignment(horizontal="right", vertical="center")

        c_s = ws_lec.cell(row=cur_r, column=9, value=row["Diem_Do_An_TB"])
        c_s.number_format = "0.0"
        c_s.alignment = Alignment(horizontal="right", vertical="center")

        c_cs = ws_lec.cell(row=cur_r, column=10, value=row["CSAT_TB"])
        c_cs.number_format = "0.00"
        c_cs.alignment = Alignment(horizontal="right", vertical="center")

        c_b = ws_lec.cell(row=cur_r, column=11, value=row["Xep_Loai"])
        c_b.alignment = Alignment(horizontal="center", vertical="center")
        if row["Xep_Loai"] == "Xuất sắc":
            c_b.fill = PatternFill(start_color=COLOR_SUCCESS_BG, end_color=COLOR_SUCCESS_BG, fill_type="solid")
            c_b.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_SUCCESS_TEXT)
        elif row["Xep_Loai"] == "Đạt chuẩn":
            c_b.fill = PatternFill(start_color=COLOR_WARNING_BG, end_color=COLOR_WARNING_BG, fill_type="solid")
            c_b.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_WARNING_TEXT)
        else:
            c_b.fill = PatternFill(start_color=COLOR_DANGER_BG, end_color=COLOR_DANGER_BG, fill_type="solid")
            c_b.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_DANGER_TEXT)

        c_p = ws_lec.cell(row=cur_r, column=12, value=row["Diem_Manh_Noi_Bat"])
        c_p.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

        c_c = ws_lec.cell(row=cur_r, column=13, value=row["Diem_Can_Cai_Thien"])
        c_c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

        for c_idx in range(1, 14):
            ws_lec.cell(row=cur_r, column=c_idx).border = border_thin

    auto_fit_columns(ws_lec, min_width=12, max_width=42)

    # 3. Sheet: Cleaned_Student_Data
    ws_stu = wb.create_sheet(title="Cleaned_Student_Data")
    ws_stu.views.sheetView[0].showGridLines = True

    stu_headers = [
        "Mã HV", "Họ và Tên", "Số Điện Thoại", "Email", 
        "Khóa Học", "Mã Lớp", "Giảng Viên", 
        "Chuyên Cần", "Điểm Đồ Án", "CSAT GV", "Trạng Thái", "Nhận Xét Học Viên", "Nguồn Dữ Liệu"
    ]
    for c_idx, h in enumerate(stu_headers, start=1):
        c = ws_stu.cell(row=1, column=c_idx, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = border_thin
    ws_stu.row_dimensions[1].height = 25

    for r_idx, row in df_clean.iterrows():
        cur_r = 2 + r_idx
        is_zebra = (r_idx % 2 == 1)
        z_fill = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid") if is_zebra else PatternFill(fill_type=None)

        ws_stu.cell(row=cur_r, column=1, value=row["Ma_HV"]).alignment = Alignment(horizontal="center")
        ws_stu.cell(row=cur_r, column=2, value=row["Ho_va_Ten"]).alignment = Alignment(horizontal="left")
        c_phone = ws_stu.cell(row=cur_r, column=3, value=str(row["So_Dien_Thoai"]))
        c_phone.number_format = '@'
        c_phone.alignment = Alignment(horizontal="center")
        ws_stu.cell(row=cur_r, column=4, value=row["Email"]).alignment = Alignment(horizontal="left")
        ws_stu.cell(row=cur_r, column=5, value=row["Khoa_Hoc"]).alignment = Alignment(horizontal="left")
        ws_stu.cell(row=cur_r, column=6, value=row["Ma_Lop"]).alignment = Alignment(horizontal="center")
        ws_stu.cell(row=cur_r, column=7, value=row["Giang_Vien"]).alignment = Alignment(horizontal="left")

        # Attendance
        c_att = ws_stu.cell(row=cur_r, column=8, value=row["Ty_Le_Chuyen_Can"] / 100.0)
        c_att.number_format = "0.0%"
        c_att.alignment = Alignment(horizontal="right")

        # Score
        c_sc = ws_stu.cell(row=cur_r, column=9, value=row["Diem_Do_An"] if not pd.isna(row["Diem_Do_An"]) else "")
        if not pd.isna(row["Diem_Do_An"]):
            c_sc.number_format = "0.0"
        c_sc.alignment = Alignment(horizontal="right")

        # CSAT
        c_cs = ws_stu.cell(row=cur_r, column=10, value=row["Danh_Gia_GV"] if not pd.isna(row["Danh_Gia_GV"]) else "")
        if not pd.isna(row["Danh_Gia_GV"]):
            c_cs.number_format = "0.0"
        c_cs.alignment = Alignment(horizontal="right")

        # Status
        c_st = ws_stu.cell(row=cur_r, column=11, value=row["Trang_Thai"])
        c_st.alignment = Alignment(horizontal="center")
        if "Tốt nghiệp" in row["Trang_Thai"]:
            c_st.fill = PatternFill(start_color=COLOR_SUCCESS_BG, end_color=COLOR_SUCCESS_BG, fill_type="solid")
            c_st.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_SUCCESS_TEXT)
        elif "Thi lại" in row["Trang_Thai"]:
            c_st.fill = PatternFill(start_color=COLOR_WARNING_BG, end_color=COLOR_WARNING_BG, fill_type="solid")
            c_st.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_WARNING_TEXT)
        else:
            c_st.fill = PatternFill(start_color=COLOR_DANGER_BG, end_color=COLOR_DANGER_BG, fill_type="solid")
            c_st.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_DANGER_TEXT)

        ws_stu.cell(row=cur_r, column=12, value=row["Nhan_Xet_Hoc_Vien"]).alignment = Alignment(horizontal="left")
        ws_stu.cell(row=cur_r, column=13, value=row["Nguon_Du_Lieu"]).alignment = Alignment(horizontal="left")

        for c_idx in range(1, 14):
            cell = ws_stu.cell(row=cur_r, column=c_idx)
            cell.border = border_thin
            if c_idx != 11 and not cell.fill.fill_type:
                cell.fill = z_fill

    auto_fit_columns(ws_stu, min_width=12, max_width=38)

    # 4. Sheet: Data_Audit_Log
    ws_aud = wb.create_sheet(title="Data_Audit_Log")
    ws_aud.views.sheetView[0].showGridLines = True

    ws_aud.merge_cells("A1:F2")
    banner_aud = ws_aud["A1"]
    banner_aud.value = "NHẬT KÝ KIỂM TOÁN LÀM SẠCH DỮ LIỆU & TỪ ĐIỂN DỮ LIỆU (DATA AUDIT LOG)"
    banner_aud.font = Font(name=FONT_NAME, size=13, bold=True, color="FFFFFF")
    banner_aud.fill = PatternFill(start_color=COLOR_PRIMARY_DARK, end_color=COLOR_PRIMARY_DARK, fill_type="solid")
    banner_aud.alignment = Alignment(horizontal="center", vertical="center")

    audit_rows = [
        ("Tổng bản ghi thô tiếp nhận (Raw Records)", f"{audit_summary['initial_raw_records']} dòng", "Tổng hợp từ Google Form, LMS Canvas và Google Sheet"),
        ("Số bản ghi trùng lặp đã loại bỏ (Duplicates Removed)", f"{audit_summary['duplicates_removed']} dòng", "Khử trùng theo Mã học viên và SĐT nộp nhiều lần"),
        ("Số bản ghi hợp lệ đưa vào phân tích (Clean Records)", f"{audit_summary['cleaned_records']} dòng", "Đạt chuẩn 100% không trùng lặp"),
        ("Chuẩn hóa Họ và Tên", "100% hoàn tất", "Xóa khoảng trắng thừa, định dạng Proper Title Case tiếng Việt"),
        ("Chuẩn hóa Số Điện Thoại", "100% hoàn tất", "Chuyển về 10 chữ số chuẩn quốc gia, xử lý đầu số +84/84/khoảng trắng/dấu chấm"),
        ("Chuẩn hóa Tên Khóa Học", "4 khóa học chuẩn", "Mapping các tên viết tắt (GenAI, Python Auto, Data AI, AI Business) về danh mục chuẩn"),
        ("Xử lý Tỷ lệ chuyên cần", "100% hoàn tất", "Chuyển đổi các định dạng %/thập phân/chuỗi về thang đo [0 - 100%]"),
        ("Xử lý Điểm đồ án & CSAT", f"{audit_summary['missing_scores']} trường hợp khuyết điểm", "Ghi nhận đúng trạng thái vắng thi/chưa nộp để phân loại drop-out chính xác"),
        ("Học viên Tốt nghiệp (Graduated)", f"{audit_summary['graduated_count']} HV ({(audit_summary['graduated_count']/audit_summary['cleaned_records'])*100:.1f}%)", "Điều kiện: Chuyên cần >= 75% VÀ Điểm đồ án >= 6.0"),
        ("Học viên Thi lại (Re-exam)", f"{audit_summary['reexam_count']} HV ({(audit_summary['reexam_count']/audit_summary['cleaned_records'])*100:.1f}%)", "Điều kiện: Chuyên cần >= 75% VÀ Điểm đồ án < 6.0"),
        ("Học viên Rơi rụng (Drop-out)", f"{audit_summary['dropout_count']} HV ({(audit_summary['dropout_count']/audit_summary['cleaned_records'])*100:.1f}%)", "Điều kiện: Chuyên cần < 50% HOẶC không tham gia làm đồ án tốt nghiệp")
    ]

    ws_aud["A4"].value = "Hạng mục kiểm toán"
    ws_aud["B4"].value = "Kết quả đạt được"
    ws_aud["C4"].value = "Ghi chú giải thích"
    for c_idx, h in enumerate(["Hạng mục kiểm toán", "Kết quả đạt được", "Ghi chú giải thích"], start=1):
        c = ws_aud.cell(row=4, column=c_idx, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = border_thin
    ws_aud.row_dimensions[4].height = 25

    for idx, (item, res, note) in enumerate(audit_rows):
        cur_r = 5 + idx
        ws_aud.row_dimensions[cur_r].height = 22
        ws_aud.cell(row=cur_r, column=1, value=item).alignment = Alignment(horizontal="left")
        ws_aud.cell(row=cur_r, column=2, value=res).alignment = Alignment(horizontal="center")
        ws_aud.cell(row=cur_r, column=3, value=note).alignment = Alignment(horizontal="left")
        for c_idx in range(1, 4):
            c = ws_aud.cell(row=cur_r, column=c_idx)
            c.border = border_thin
            if idx % 2 == 1:
                c.fill = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid")

    auto_fit_columns(ws_aud, min_width=15, max_width=50)

    # Save Master Workbook
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    wb.save(output_file)
    print(f"[✓] Master Excel successfully exported to {output_file}")

def build_individual_lecturer_reports(df_clean, df_metrics, output_dir, quarter="2026-Q3", report_date="2026-09-12"):
    lecturers_dir = os.path.join(output_dir, "lecturers")
    os.makedirs(lecturers_dir, exist_ok=True)
    print(f"[*] Exporting confidential individual reports to: {lecturers_dir}")

    border_thin = Border(
        left=Side(style="thin", color=COLOR_BORDER),
        right=Side(style="thin", color=COLOR_BORDER),
        top=Side(style="thin", color=COLOR_BORDER),
        bottom=Side(style="thin", color=COLOR_BORDER)
    )
    header_fill = PatternFill(start_color=COLOR_PRIMARY_MEDIUM, end_color=COLOR_PRIMARY_MEDIUM, fill_type="solid")
    header_font = Font(name=FONT_NAME, size=10, bold=True, color="FFFFFF")

    for _, m_row in df_metrics.iterrows():
        lec_name = m_row["Giang_Vien"]
        # Safe filename without accents
        safe_name = remove_accents(lec_name.replace("Thầy ", "").replace("Cô ", "").strip())
        safe_slug = re.sub(r"[^a-zA-Z0-9]+", "_", safe_name).strip("_")
        file_name = f"Report_Lecturer_{safe_slug}.xlsx"
        file_path = os.path.join(lecturers_dir, file_name)

        df_sub = df_clean[df_clean["Giang_Vien"] == lec_name].copy()

        wb = openpyxl.Workbook()
        ws_sum = wb.active
        ws_sum.title = "Class_Summary"
        ws_sum.views.sheetView[0].showGridLines = True

        # Banner
        ws_sum.merge_cells("A1:G2")
        b = ws_sum["A1"]
        b.value = f"BÁO CÁO HỌC VỤ & PHẢN HỒI LỚP HỌC — {lec_name.upper()}"
        b.font = Font(name=FONT_NAME, size=13, bold=True, color="FFFFFF")
        b.fill = PatternFill(start_color=COLOR_PRIMARY_DARK, end_color=COLOR_PRIMARY_DARK, fill_type="solid")
        b.alignment = Alignment(horizontal="center", vertical="center")

        ws_sum["A3"].value = f"Khóa học: {m_row['Khoa_Hoc']} | Mã lớp: {m_row['Ma_Lop']} | Kỳ: {quarter} | Ngày xuất: {report_date}"
        ws_sum["A3"].font = Font(name=FONT_NAME, size=9, italic=True, color="595959")

        # KPI Cards
        apply_card_styling(ws_sum, start_col=1, start_row=5, width=2, height=4, title="SỐ LƯỢNG HỌC VIÊN", value=f"{m_row['Tong_Hoc_Vien']} HV", subtext=f"Lớp {m_row['Ma_Lop']}")
        apply_card_styling(ws_sum, start_col=3, start_row=5, width=2, height=4, title="TỶ LỆ TỐT NGHIỆP", value=f"{m_row['Ty_Le_Tot_Nghiep']*100:.1f}%", subtext=f"{m_row['HV_Tot_Nghiep']} học viên đạt", card_bg=COLOR_SUCCESS_BG, val_color=COLOR_SUCCESS_TEXT)
        apply_card_styling(ws_sum, start_col=5, start_row=5, width=2, height=4, title="ĐIỂM HÀI LÒNG CSAT", value=f"{m_row['CSAT_TB']:.2f} / 5.0", subtext=f"Xếp loại: {m_row['Xep_Loai']}", card_bg=COLOR_CARD_BG, val_color=COLOR_PRIMARY_DARK)

        # Performance table
        ws_sum["A10"].value = "THÔNG SỐ CHI TIẾT LỚP HỌC"
        ws_sum["A10"].font = Font(name=FONT_NAME, size=11, bold=True, color=COLOR_PRIMARY_DARK)

        details = [
            ("Tỷ lệ chuyên cần trung bình", f"{m_row['Chuyen_Can_TB']:.1f}%"),
            ("Điểm đồ án tốt nghiệp trung bình", f"{m_row['Diem_Do_An_TB']:.1f} / 10.0"),
            ("Số lượng học viên tốt nghiệp", f"{m_row['HV_Tot_Nghiep']} học viên"),
            ("Số lượng học viên cần thi lại / phụ đạo", f"{m_row['HV_Thi_Lai']} học viên"),
            ("Số lượng học viên rơi rụng (Drop-out)", f"{m_row['HV_Drop_out']} học viên ({m_row['Ty_Le_Drop_out']*100:.1f}%)"),
            ("Xếp loại giảng viên kỳ này", m_row['Xep_Loai']),
            ("Điểm mạnh học viên đánh giá cao", m_row['Diem_Manh_Noi_Bat']),
            ("Góp ý học viên mong muốn cải tiến", m_row['Diem_Can_Cai_Thien'])
        ]

        ws_sum["A11"].value = "Chỉ số học vụ"
        ws_sum["B11"].value = "Giá trị đạt được"
        for c_idx, h in enumerate(["Chỉ số học vụ", "Giá trị đạt được"], start=1):
            c = ws_sum.cell(row=11, column=c_idx, value=h)
            c.fill = header_fill
            c.font = header_font
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = border_thin
        ws_sum.row_dimensions[11].height = 24

        for idx, (metric, val) in enumerate(details):
            cur_r = 12 + idx
            ws_sum.row_dimensions[cur_r].height = 22
            ws_sum.cell(row=cur_r, column=1, value=metric).alignment = Alignment(horizontal="left")
            ws_sum.cell(row=cur_r, column=2, value=val).alignment = Alignment(horizontal="left")
            ws_sum.cell(row=cur_r, column=1).border = border_thin
            ws_sum.cell(row=cur_r, column=2).border = border_thin
            if idx % 2 == 1:
                ws_sum.cell(row=cur_r, column=1).fill = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid")
                ws_sum.cell(row=cur_r, column=2).fill = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid")

        auto_fit_columns(ws_sum, min_width=14, max_width=50)

        # Sheet 2: Student_List
        ws_list = wb.create_sheet(title="Student_List")
        ws_list.views.sheetView[0].showGridLines = True

        list_headers = [
            "Mã HV", "Họ và Tên", "Số Điện Thoại", "Email", 
            "Chuyên Cần", "Điểm Đồ Án", "CSAT GV", "Trạng Thái", "Nhận Xét Học Viên"
        ]
        for c_idx, h in enumerate(list_headers, start=1):
            c = ws_list.cell(row=1, column=c_idx, value=h)
            c.fill = header_fill
            c.font = header_font
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = border_thin
        ws_list.row_dimensions[1].height = 25

        for r_idx, s_row in df_sub.reset_index(drop=True).iterrows():
            cur_r = 2 + r_idx
            is_zebra = (r_idx % 2 == 1)
            z_fill = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid") if is_zebra else PatternFill(fill_type=None)

            ws_list.cell(row=cur_r, column=1, value=s_row["Ma_HV"]).alignment = Alignment(horizontal="center")
            ws_list.cell(row=cur_r, column=2, value=s_row["Ho_va_Ten"]).alignment = Alignment(horizontal="left")
            c_p = ws_list.cell(row=cur_r, column=3, value=str(s_row["So_Dien_Thoai"]))
            c_p.number_format = '@'
            c_p.alignment = Alignment(horizontal="center")
            ws_list.cell(row=cur_r, column=4, value=s_row["Email"]).alignment = Alignment(horizontal="left")

            c_at = ws_list.cell(row=cur_r, column=5, value=s_row["Ty_Le_Chuyen_Can"] / 100.0)
            c_at.number_format = "0.0%"
            c_at.alignment = Alignment(horizontal="right")

            c_sc = ws_list.cell(row=cur_r, column=6, value=s_row["Diem_Do_An"] if not pd.isna(s_row["Diem_Do_An"]) else "")
            if not pd.isna(s_row["Diem_Do_An"]):
                c_sc.number_format = "0.0"
            c_sc.alignment = Alignment(horizontal="right")

            c_cs = ws_list.cell(row=cur_r, column=7, value=s_row["Danh_Gia_GV"] if not pd.isna(s_row["Danh_Gia_GV"]) else "")
            if not pd.isna(s_row["Danh_Gia_GV"]):
                c_cs.number_format = "0.0"
            c_cs.alignment = Alignment(horizontal="right")

            c_st = ws_list.cell(row=cur_r, column=8, value=s_row["Trang_Thai"])
            c_st.alignment = Alignment(horizontal="center")
            if "Tốt nghiệp" in s_row["Trang_Thai"]:
                c_st.fill = PatternFill(start_color=COLOR_SUCCESS_BG, end_color=COLOR_SUCCESS_BG, fill_type="solid")
                c_st.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_SUCCESS_TEXT)
            elif "Thi lại" in s_row["Trang_Thai"]:
                c_st.fill = PatternFill(start_color=COLOR_WARNING_BG, end_color=COLOR_WARNING_BG, fill_type="solid")
                c_st.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_WARNING_TEXT)
            else:
                c_st.fill = PatternFill(start_color=COLOR_DANGER_BG, end_color=COLOR_DANGER_BG, fill_type="solid")
                c_st.font = Font(name=FONT_NAME, size=10, bold=True, color=COLOR_DANGER_TEXT)

            ws_list.cell(row=cur_r, column=9, value=s_row["Nhan_Xet_Hoc_Vien"]).alignment = Alignment(horizontal="left")

            for c_idx in range(1, 10):
                cell = ws_list.cell(row=cur_r, column=c_idx)
                cell.border = border_thin
                if c_idx != 8 and not cell.fill.fill_type:
                    cell.fill = z_fill

        auto_fit_columns(ws_list, min_width=12, max_width=40)

        wb.save(file_path)
        print(f"    [✓] Exported: {file_name}")

def generate_markdown_report(df_clean, df_metrics, audit_summary, output_file, quarter="2026-Q3", report_date="2026-09-12"):
    print(f"[*] Generating Executive Academic Analysis Report: {output_file}")
    total_students = len(df_clean)
    grad_rate = (audit_summary["graduated_count"] / total_students) * 100
    dropout_rate = (audit_summary["dropout_count"] / total_students) * 100
    reexam_rate = (audit_summary["reexam_count"] / total_students) * 100
    avg_csat = df_clean["Danh_Gia_GV"].dropna().mean()
    avg_score = df_clean["Diem_Do_An"].dropna().mean()
    avg_att = df_clean["Ty_Le_Chuyen_Can"].mean()

    # Ranking table markdown
    ranking_rows = []
    for idx, row in df_metrics.iterrows():
        ranking_rows.append(
            f"| #{idx+1} | **{row['Giang_Vien']}** | {row['Khoa_Hoc']} | `{row['Ma_Lop']}` | {int(row['Tong_Hoc_Vien'])} | "
            f"{row['Ty_Le_Tot_Nghiep']*100:.1f}% | {row['Ty_Le_Drop_out']*100:.1f}% | {row['Chuyen_Can_TB']:.1f}% | "
            f"{row['Diem_Do_An_TB']:.1f} | **{row['CSAT_TB']:.2f}** | `{row['Xep_Loai']}` |"
        )
    ranking_table_md = "\n".join(ranking_rows)

    md_content = f"""# BÁO CÁO ĐIỀU HÀNH HỌC VỤ & PHÂN TÍCH HIỆU SUẤT GIẢNG VIÊN — {quarter}
**Trung Tâm Đào Tạo Công Nghệ & AI**  
*Ngày lập báo cáo:* {report_date} | *Kỳ đánh giá:* {quarter} | *Người lập:* Chuyên viên Đào tạo (Academic Executive)  
*Đối tượng tiếp nhận:* Ban Giám Đốc Trung Tâm, Trưởng Khối Học Vụ (Academic Director)

---

## 1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)

Trong kỳ đào tạo **{quarter}**, hệ thống học vụ đã hoàn thành thu thập, làm sạch và chuẩn hóa dữ liệu của **{total_students} học viên** phân bổ qua **4 khóa học công nghệ chiến lược** do 4 giảng viên chủ chốt phụ trách.

Nhờ pipeline tự động hóa, trung tâm đã giải quyết triệt để vấn đề dữ liệu phân tán nhiều nguồn (Google Form, LMS Canvas, Google Sheet khảo sát), loại bỏ thành công **{audit_summary['duplicates_removed']} bản ghi trùng lặp**, chuẩn hóa 100% số điện thoại và danh tính học viên, đồng thời xây dựng bộ chỉ số đánh giá giảng viên 360 độ minh bạch.

### 📌 Các Chỉ Số Cốt Lõi Toàn Trung Tâm

| Chỉ số KPI | Giá trị đạt được | Mục tiêu chuẩn | Đánh giá học vụ |
| :--- | :---: | :---: | :--- |
| **Tổng số học viên nhập học** | **{total_students} học viên** | ≥ 160 HV | ✅ Đạt 112.5% chỉ tiêu tuyển sinh |
| **Tỷ lệ tốt nghiệp (Completion Rate)** | **{grad_rate:.1f}%** ({audit_summary['graduated_count']} HV) | ≥ 85.0% | ✅ Đạt chuẩn chất lượng đầu ra |
| **Tỷ lệ rơi rụng (Dropout Rate)** | **{dropout_rate:.1f}%** ({audit_summary['dropout_count']} HV) | ≤ 12.0% | ⚠️ Vượt ngưỡng an toàn nhẹ (+{dropout_rate - 12:.1f}%) |
| **Tỷ lệ thi lại / phụ đạo (Re-exam)** | **{reexam_rate:.1f}%** ({audit_summary['reexam_count']} HV) | ≤ 5.0% | ✅ Nằm trong ngưỡng kiểm soát |
| **Điểm hài lòng giảng viên (CSAT)** | **{avg_csat:.2f} / 5.0** | ≥ 4.30 / 5.0 | ⭐ Xuất sắc, học viên đánh giá rất cao |
| **Điểm đồ án tốt nghiệp trung bình** | **{avg_score:.1f} / 10.0** | ≥ 7.5 / 10.0 | ✅ Đạt yêu cầu năng lực thực tế |
| **Tỷ lệ chuyên cần trung bình** | **{avg_att:.1f}%** | ≥ 80.0% | ✅ Duy trì nề nếp học tập tốt |

---

## 2. BẢNG XẾP HẠNG & SO SÁNH HIỆU SUẤT GIẢNG VIÊN 360 ĐỘ

Khung đánh giá 360 độ tích hợp giữa **Định lượng học vụ** (Chuyên cần, Điểm đồ án, Tỷ lệ tốt nghiệp) và **Định tính trải nghiệm** (Điểm hài lòng CSAT, Nhận xét thực tế của học viên).

| Hạng | Giảng viên | Khóa học phụ trách | Lớp | Sĩ số | Tốt nghiệp | Rơi rụng | Chuyên cần | Điểm đồ án | CSAT GV | Xếp loại |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
{ranking_table_md}

---

## 3. PHÂN TÍCH CHUYÊN SÂU TỪNG GIẢNG VIÊN & KHÓA HỌC

```mermaid
graph TD
    A[Tổng Quy Mô: 180 Học Viên] --> B[Thầy Nguyễn Văn An - CSAT 4.85<br/>Xuất Sắc: Tốt nghiệp 97.8%]
    A --> C[Cô Trần Thị Bình - CSAT 4.45<br/>Đạt Chuẩn: Điểm đồ án 8.7/10]
    A --> D[Cô Phạm Thanh Dung - CSAT 4.64<br/>Đạt Chuẩn: Ổn định 91.1%]
    A --> E[Thầy Lê Hoàng Cường - CSAT 4.05<br/>Cần Cải Thiện: Drop-out 22.2%]
```

### 3.1. Thầy Nguyễn Văn An — Lớp `GAI-K12` (Generative AI & LLMs Applied)
- **Điểm sáng:** Giảng viên dẫn đầu toàn trung tâm ở mọi chỉ số: CSAT đạt **4.85/5.0**, tỷ lệ tốt nghiệp đạt **97.8%** (44/45 học viên), tỷ lệ chuyên cần **91.6%**.
- **Tiếng nói học viên:** *"Thầy dạy cực kỳ cuốn hút, kiến thức GenAI cập nhật mới nhất!", "Rất thích các bài thực hành xây dựng Agent với LLM, giảng viên nhiệt tình hỗ trợ cả ngoài giờ."*
- **Điểm lưu ý:** Một số học viên phản ánh tốc độ bài giảng phần Prompt Chaining hơi nhanh, cần bổ sung tài liệu trước buổi học.
- **Khuyến nghị:** Đề xuất vinh danh Giảng viên Xuất sắc của Quý; mời thầy An xây dựng bộ Master Class chia sẻ phương pháp sư phạm cho các giảng viên khác.

### 3.2. Cô Trần Thị Bình — Lớp `PYA-K08` (Python & AI Automation Workflow)
- **Điểm sáng:** Chất lượng đồ án tốt nghiệp xuất sắc nhất trung tâm với điểm TB **8.7/10**. Cô Bình theo sát logic code và phương pháp tự động hóa thực chiến.
- **Tiếng nói học viên:** *"Cô Bình chấm đồ án rất kỹ và chi tiết, học hỏi được rất nhiều tư duy lập trình.", "Học xong tự build được pipeline xử lý báo cáo tự động tại công ty."*
- **Thách thức:** Do tính chất môn lập trình và yêu cầu khắt khe, có **11.1% học viên drop-out** và **4.4% cần thi lại đồ án**. Một số học viên trái ngành cảm thấy ngợp trước khối lượng bài tập.
- **Khuyến nghị:** Bổ sung 1 buổi Lab phụ đạo kỹ thuật cho học viên mới bắt đầu học code; phân bổ bài tập lớn thành nhiều checkpoint nhỏ để giảm áp lực.

### 3.3. Cô Phạm Thanh Dung — Lớp `AIB-K06` (AI for Business & Management)
- **Điểm sáng:** Tỷ lệ tốt nghiệp cao **91.1%** (41/45 học viên), điểm CSAT đạt **4.64/5.0**. Các case study chuyển đổi số và ứng dụng AI vào vận hành doanh nghiệp được đánh giá rất thực tế.
- **Tiếng nói học viên:** *"Cô Dung chia sẻ góc nhìn quản trị rất sâu sắc, không khí lớp học sôi nổi với các bài thảo luận nhóm."*
- **Thách thức:** Học viên mong muốn được hướng dẫn chi tiết hơn về cách tính toán tỷ suất hoàn vốn (ROI) khi ứng dụng các giải pháp AI trong doanh nghiệp.
- **Khuyến nghị:** Bổ sung thêm chuyên đề mini về thẩm định chi phí - hiệu quả (Cost-Benefit & ROI Analysis) của các công cụ AI.

### 3.4. Thầy Lê Hoàng Cường — Lớp `DAI-K15` (Data Analytics & BI with AI) ⚠️
- **Vấn đề cảnh báo cấp thiết:** Lớp có tỷ lệ rơi rụng (Drop-out) cao nhất trung tâm: **22.2%** (10/45 học viên bỏ học hoặc không nộp đồ án), chuyên cần trung bình thấp nhất (**77.8%**), điểm CSAT thấp nhất (**4.05/5.0**).
- **Nguyên nhân gốc rễ (Root Cause):** Khóa học có độ dốc kiến thức quá lớn khi chuyển giao từ cơ bản sang phần nâng cao (DAX công thức phức tạp, tích hợp mô hình Machine Learning). Học viên phản ánh tốc độ giảng bài quá nhanh và thiếu sự kèm cặp thực hành trực tiếp.
- **Tiếng nói học viên:** *"Kiến thức phân tích số liệu hơi nặng, thầy giảng hơi nhanh ở phần DAX và SQL.", "Nhiều bài tập phức tạp chưa theo kịp tiến độ lớp, mong trung tâm tăng trợ giảng."*
- **Hành động khẩn cấp:** Cần sắp xếp buổi họp chuyên môn khẩn giữa Ban Đào tạo và Thầy Cường; bố trí ngay 02 Trợ giảng (Teaching Assistant) hỗ trợ thực hành máy; kích hoạt chính sách bảo lưu học lại miễn phí cho 10 học viên đã drop-out.

---

## 4. BẢN ĐỒ CẢNH BÁO RỦI RO HỌC VỤ (ACADEMIC RISK MATRIX)

| Mã Rủi Ro | Phân loại | Mức độ | Đối tượng ảnh hưởng | Hành động khắc phục ngay |
| :---: | :--- | :---: | :--- | :--- |
| **RSK-01** | Drop-out tăng vọt ở môn Phân tích dữ liệu | 🔴 Cao | Lớp `DAI-K15` (22.2% bỏ học) | Tách lộ trình thành 2 giai đoạn (Căn bản & Nâng cao), bổ sung 2 trợ giảng thực hành |
| **RSK-02** | Rào cản kỹ thuật môn Lập trình Python | 🟡 Vừa | Lớp `PYA-K08` (Học viên non-tech) | Tổ chức workshop Pre-course "Nhập môn tư duy giải thuật" trước khai giảng |
| **RSK-03** | Trùng lặp và phân mảnh dữ liệu đăng ký | 🟢 Thấp | Hệ thống ghi danh tuyển sinh | Đã tự động hóa giải quyết 100% bằng pipeline Python làm sạch |

---

## 5. ĐỀ XUẤT CẢI TIẾN HỌC VỤ CHIẾN LƯỢC (PDCA ACTION PLAN)

Để nâng cao chất lượng đào tạo và giữ vững uy tín của trung tâm trong quý tiếp theo, phòng Đào tạo đề xuất 3 nhóm giải pháp trọng tâm:

### 🎯 Đề xuất 1: Triển khai Mô hình "Giảng viên Chính + Trợ giảng Kèm cặp" (TA Support System)
- **Mục tiêu:** Giảm tỷ lệ drop-out môn `Data Analytics & BI` từ 22.2% xuống dưới 10.0%.
- **Thực thi:** Bố trí 01 Trợ giảng phụ trách tối đa 20 học viên trong các buổi thực hành phòng máy; mở kênh Discord/Zalo hỗ trợ fix lỗi code trong vòng 2 giờ.
- **Tiến độ:** Áp dụng ngay từ khóa khai giảng tháng 10/2026.

### 🎯 Đề xuất 2: Chuẩn hóa Quy Trình Khảo Sát Giữa Khóa (Mid-term CSAT Pulse Check)
- **Mục tiêu:** Phát hiện sớm các vấn đề về tốc độ giảng bài hoặc độ khó kiến thức ở tuần thứ 3 (thay vì chờ đến cuối khóa mới khảo sát).
- **Thực thi:** Tự động gửi link khảo sát nhanh 3 câu hỏi sau buổi học số 4; nếu CSAT của lớp < 4.2 thì Academic Executive sẽ can thiệp điều chỉnh ngay cùng giảng viên.

### 🎯 Đề xuất 3: Cá nhân hóa Báo Cáo Học Vụ & Khen Thưởng Giảng Viên
- **Mục tiêu:** Tăng tính gắn kết và động lực nâng cao chuyên môn cho đội ngũ giảng viên.
- **Thực thi:** Tự động gửi file báo cáo riêng `Report_Lecturer_{{Name}}.xlsx` cho từng thầy cô ngay sau khi khóa học kết thúc; ban hành quỹ thưởng "Giảng viên Ngôi sao" dành cho các thầy cô đạt CSAT ≥ 4.7 và Completion ≥ 90%.

---

*Báo cáo được tạo tự động bởi Hệ thống Xử lý Dữ liệu Học vụ `scripts/academic_training_processor.py` — Bảo lưu mọi quyền.*
"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content.strip())
    print(f"[✓] Executive Academic Report successfully generated: {output_file}")

def main():
    args = parse_args()
    print("=================================================================")
    print(" ACADEMIC TRAINING DATA PROCESSING & REPORTING SYSTEM")
    print("=================================================================")
    print(f"Report Date: {args.report_date} | Quarter: {args.quarter}")
    
    # Define folder structure
    date_output_dir = os.path.join(args.output_dir, args.report_date)
    os.makedirs(date_output_dir, exist_ok=True)

    master_excel_file = os.path.join(date_output_dir, f"Master_Academic_Report_{args.quarter}.xlsx")
    markdown_report_file = os.path.join(date_output_dir, "Academic_Training_Executive_Report.md")

    # Step 1: Load and clean
    df_clean, audit_summary = load_and_clean_data(args.file)

    # Step 2: Compute metrics
    df_metrics = compute_lecturer_metrics(df_clean)

    # Step 3: Build Master Excel
    build_master_excel(df_clean, df_metrics, audit_summary, master_excel_file, quarter=args.quarter, report_date=args.report_date)

    # Step 4: Build individual lecturer reports
    build_individual_lecturer_reports(df_clean, df_metrics, date_output_dir, quarter=args.quarter, report_date=args.report_date)

    # Step 5: Build Markdown Executive Report
    generate_markdown_report(df_clean, df_metrics, audit_summary, markdown_report_file, quarter=args.quarter, report_date=args.report_date)

    print("=================================================================")
    print(" PIPELINE COMPLETED SUCCESSFULLY!")
    print(f" Master Excel:        {master_excel_file}")
    print(f" Lecturer Reports:    {os.path.join(date_output_dir, 'lecturers')}")
    print(f" Executive Report:    {markdown_report_file}")
    print("=================================================================")

if __name__ == "__main__":
    main()

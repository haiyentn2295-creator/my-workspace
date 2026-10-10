#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Estate AI Lead Scoring Application (Streamlit)
Dựa theo skill lead-scoring và quy chuẩn tieu_chi_cham_diem.txt:
- Tự động hóa chấm điểm 5 tiêu chí (Ngân sách, Nhu cầu, Thời gian, Nguồn khách, Tương tác)
- Phát hiện Cờ VIP (+50đ) & Cờ Đỏ Red Flags (-50đ)
- Bảng tương tác st.data_editor cho phép Con người (Human-in-the-loop) duyệt trạng thái
- Handover package cho Sales với kịch bản cá nhân hóa & SLA thời gian vàng
"""

import os
import sys
import re
import io
import ssl
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
import gspread

# Fix SSL context for macOS
ssl._create_default_https_context = ssl._create_unverified_context


def get_gspread_client():
    """Khởi tạo gspread client từ st.secrets (Cloud) hoặc service_account.json (Local)"""
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict and isinstance(creds_dict["private_key"], str):
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            return gspread.service_account_from_dict(creds_dict)
    except Exception:
        pass

    if os.path.exists("service_account.json"):
        try:
            return gspread.service_account(filename="service_account.json")
        except Exception:
            pass

    return None


def sync_to_google_sheet(df, sheet_url, worksheet_title="Lead_Scored_Reviewed"):
    """Tạo hoặc cập nhật Tab Lead_Scored_Reviewed trên Google Sheet với dữ liệu đã được duyệt"""
    gc = get_gspread_client()
    if not gc:
        raise ValueError("Chưa tìm thấy cấu hình Service Account trong st.secrets hoặc service_account.json!")
    
    sh = gc.open_by_url(sheet_url)
    
    try:
        ws = sh.worksheet(worksheet_title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_title, rows=max(100, len(df) + 15), cols=max(20, len(df.columns) + 5))
        
    export_df = df.copy()
    export_df["Trạng Thái Duyệt"] = export_df["human_approved"].apply(lambda x: "ĐÃ DUYỆT" if x else "CHƯA DUYỆT")
    export_df["Cập Nhật Lúc"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    columns_map = {
        "id": "Mã ID",
        "Trạng Thái Duyệt": "Trạng Thái Duyệt",
        "ten_khach": "Họ Tên",
        "sdt_chuan": "Số ĐT",
        "total_score": "Điểm AI",
        "ai_tier": "AI Gợi Ý",
        "final_tier": "Tier Thực Tế",
        "sales_assignee": "Sales Phụ Trách",
        "segment": "Phân Khúc BĐS",
        "sla": "SLA Hành Động",
        "review_note": "Ghi Chú Thẩm Định",
        "pitch": "Kịch Bản Tiếp Cận",
        "vip_flags": "Cờ VIP",
        "red_flags": "Cờ Đỏ (Red Flags)",
        "nhu_cau_mo_ta": "Mô Tả Nhu Cầu",
        "Cập Nhật Lúc": "Thời Gian Cập Nhật"
    }
    
    cols_to_use = [k for k in columns_map.keys() if k in export_df.columns]
    export_df = export_df[cols_to_use].rename(columns=columns_map)
    
    values = [export_df.columns.tolist()] + export_df.fillna("").values.tolist()
    ws.clear()
    ws.update(values=values, range_name="A1")
    return sh.url, worksheet_title

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="AI Lead Scoring — Bất Động Sản",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho phong cách hiện đại chuẩn Executive UI
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .badge-hot {
        background-color: #FEE2E2;
        color: #DC2626;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
    }
    .badge-warm {
        background-color: #FEF3C7;
        color: #D97706;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
    }
    .badge-junk {
        background-color: #F1F5F9;
        color: #64748B;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 1. CORE AI SCORING AGENT LOGIC
# ==========================================

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


def run_ai_scoring_agent(desc_text):
    """
    Agent phân tích NLP tự động quét mô tả nhu cầu khách hàng:
    - Nhận diện Red Flags (-50đ theo tieu_chi_cham_diem.txt)
    - Nhận diện Cờ VIP (+50đ theo tieu_chi_cham_diem.txt)
    - Đánh giá 5 trụ cột (Ngân sách, Nhu cầu, Thời gian, Nguồn khách, Tương tác)
    - Trích xuất phân khúc BĐS & Đề xuất kịch bản chào mời (Pitch Angle)
    """
    desc = str(desc_text).lower() if desc_text else ""
    
    red_flags = []
    vip_flags = []
    
    # 1. Quét Red Flags (-50đ)
    if any(k in desc for k in ["nhà q1 giá 1 tỷ", "q1 giá 1", "quận 1 giá 1", "nhà 1 tỷ", "giá 2 triệu", "vài trăm triệu", "phi thực tế"]):
        red_flags.append("Yêu cầu phi thực tế so với thị trường")
    if any(k in desc for k in ["nhầm số", "không có nhu cầu", "dữ liệu cũ", "nhầm ngành"]):
        red_flags.append("Nhầm số / Không có nhu cầu BĐS")
    if any(k in desc for k in ["hỏi giá cho vui", "chưa có ý định mua", "không hợp tác"]):
        red_flags.append("Khách không thiện chí / Hỏi cho vui")
    if any(k in desc for k in ["spam", "bảo hiểm", "vay vốn", "mời chào", "quảng cáo ngược"]):
        red_flags.append("Spam / Chào mời dịch vụ khác")
    if any(k in desc for k in ["thuê bao", "không bắt máy", "không phản hồi zalo", "không nghe máy"]):
        red_flags.append("Thông tin liên lạc lỗi / Thuê bao / Không phản hồi")

    # 2. Quét VIP Flags (+50đ)
    if any(k in desc for k in ["20 tỷ", "30 tỷ", "trên 20 tỷ", "trên 30 tỷ", "tài chính mạnh", "tài chính cực mạnh", "không thành vấn đề", "thanh toán thẳng"]):
        vip_flags.append("Ngân sách lớn / Tài chính cực mạnh")
    if any(k in desc for k in ["penthouse", "biệt thự đơn lập", "shophouse mặt đường lớn", "quỹ đất công nghiệp", "sàn văn phòng diện tích lớn", "sàn văn phòng"]):
        vip_flags.append("Loại hình BĐS cao cấp / Quy mô lớn")
    if any(k in desc for k in ["ven sông", "quận 1", "vinhomes ocean park", "phú mỹ hưng"]):
        vip_flags.append("Vị trí đắc địa (Ven sông, Q1, KĐT cao cấp)")
    if any(k in desc for k in ["chủ doanh nghiệp", "nhà đầu tư chuyên nghiệp", "mua sỉ", "gom sỉ", "số lượng lớn"]):
        vip_flags.append("Đối tượng VIP (Chủ DN, NĐT sỉ)")
    if any(k in desc for k in ["pháp lý chuẩn 100%", "sổ hồng riêng", "gặp trực tiếp chủ đầu tư", "gặp trực tiếp giám đốc"]):
        vip_flags.append("Yêu cầu pháp lý minh bạch / Muốn gặp lãnh đạo đàm phán")

    # 3. Tính điểm 5 Trụ cột (Thang 100đ chuẩn)
    # P1: Ngân sách (Max 35)
    if any(k in desc for k in ["không thành vấn đề", "trên 30 tỷ", "30 tỷ", "tài chính cực mạnh", "gom sỉ", "20 tỷ", "trên 20 tỷ"]):
        s_budget = 35
    elif any(k in desc for k in ["4-5 tỷ", "5 tỷ"]):
        s_budget = 25
    elif any(k in desc for k in ["dưới 50 triệu", "50 triệu"]):
        s_budget = 20
    elif any(k in desc for k in ["2-3 tỷ", "3 tỷ", "vùng ven"]):
        s_budget = 15
    elif any(k in desc for k in ["1 tỷ", "2 triệu", "phi thực tế"]):
        s_budget = -40
    else:
        s_budget = 10

    # P2: Nhu cầu & Phân khúc (Max 25)
    if any(k in desc for k in ["penthouse", "biệt thự đơn lập", "shophouse", "sàn văn phòng", "đất công nghiệp"]):
        s_need = 25
    elif any(k in desc for k in ["mặt bằng kinh doanh spa", "căn hộ 2pn", "đất nền"]):
        s_need = 18
    elif "hỏi giá cho vui" in desc:
        s_need = 0
    elif any(k in desc for k in ["nhầm số", "spam"]):
        s_need = -30
    else:
        s_need = 8

    # P3: Thời gian mua & Cấp thiết (Max 20)
    if any(k in desc for k in ["cuối tuần này", "gặp trực tiếp", "thanh toán thẳng"]):
        s_timeline = 18
    elif any(k in desc for k in ["ký hợp đồng dài hạn"]):
        s_timeline = 14
    elif any(k in desc for k in ["đầu tư dài hạn", "đang tìm"]):
        s_timeline = 10
    elif "chưa có ý định mua trong năm nay" in desc:
        s_timeline = 0
    elif any(k in desc for k in ["nhầm số", "thuê bao", "spam"]):
        s_timeline = -20
    else:
        s_timeline = 5

    # P4: Nguồn khách & Hồ sơ (Max 10)
    if any(k in desc for k in ["chủ doanh nghiệp", "nhà đầu tư chuyên nghiệp", "đã từng mua nhiều dự án", "khách hàng vip"]):
        s_source = 10
    elif any(k in desc for k in ["gia đình trẻ", "đang tìm thuê", "kinh doanh"]):
        s_source = 7
    elif any(k in desc for k in ["nhầm số", "spam"]):
        s_source = -20
    else:
        s_source = 5

    # P5: Tương tác & Kết nối (Max 10)
    if any(k in desc for k in ["pháp lý chuẩn 100%", "sổ hồng riêng", "muốn đi xem nhà mẫu", "cần gặp trực tiếp"]):
        s_engagement = 10
    elif any(k in desc for k in ["thuê bao", "không bắt máy", "không phản hồi zalo", "thái độ không hợp tác"]):
        s_engagement = -40
    elif any(k in desc for k in ["nhầm số", "spam"]):
        s_engagement = -20
    else:
        s_engagement = 6

    # 4. Điểm điều chỉnh
    bonus_points = 20 if len(vip_flags) >= 2 else (10 if len(vip_flags) == 1 else 0)
    penalty_points = -50 * len(red_flags) if red_flags else 0
    raw_score = s_budget + s_need + s_timeline + s_source + s_engagement
    
    total_score = max(0, min(100, raw_score + bonus_points + penalty_points))
    if red_flags:
        total_score = max(0, min(15, total_score))

    # 5. Phân hạng Tier
    if red_flags or total_score < 20:
        if any("spam" in f.lower() for f in red_flags):
            tier = "JUNK"
            detail = "SPAM / QUẢNG CÁO"
        elif any("nhầm số" in f.lower() for f in red_flags):
            tier = "JUNK"
            detail = "NHẦM SỐ / SAI DATA"
        elif any("thuê bao" in f.lower() for f in red_flags):
            tier = "COLD"
            detail = "LIÊN LẠC LỖI / THUÊ BAO"
        else:
            tier = "COLD"
            detail = "KHÔNG TIỀM NĂNG / PHI THỰC TẾ"
        sla = "Loại bỏ / Blacklist / Không phân bổ Sales"
    elif total_score >= 80:
        tier = "HOT"
        detail = "VIP / TIỀM NĂNG CAO (SIÊU CẤP)"
        sla = "Ưu tiên số 1 - Phân bổ Senior Sales gọi ngay trong 15 phút"
    elif total_score >= 50:
        tier = "WARM"
        detail = "TIỀM NĂNG / CẦN TƯ VẤN THÊM"
        sla = "Ưu tiên số 2 - Phân bổ Sales gọi trong 2-4 giờ"
    else:
        tier = "COLD"
        detail = "TIỀM NĂNG THẤP / KHẢO SÁT"
        sla = "Ưu tiên số 3 - Đưa vào phễu tin nhắn/email nuôi dưỡng tự động"

    # 6. Phân khúc & Kịch bản chào mời
    if "penthouse" in desc:
        segment = "Penthouse Siêu Sang"
        pitch = "Tập trung chào dòng căn hộ Penthouse độc bản, khẳng định tính riêng tư, hồ bơi và sảnh thang máy riêng."
    elif "biệt thự đơn lập" in desc:
        segment = "Biệt Thự Đơn Lập Ven Sông"
        pitch = "Mời đích danh Trưởng bộ phận VIP gọi điện, gửi mặt bằng biệt thự ven sông hướng Đông Nam, ưu đãi khách VIP."
    elif "shophouse" in desc:
        segment = "Shophouse Đầu Tư Sỉ"
        pitch = "Chuẩn bị bài toán tài chính sỉ 5-10 căn, chính sách cam kết tiền thuê và kết nối gặp trực tiếp Giám đốc dự án."
    elif "sàn văn phòng" in desc or "đất công nghiệp" in desc:
        segment = "BĐS Thương Mại & KCN"
        pitch = "Cung cấp hồ sơ pháp lý chuẩn 100%, quy hoạch 1/500, sơ đồ hạ tầng khu Đông và báo giá trọn gói cho doanh nghiệp."
    elif "mặt bằng kinh doanh" in desc:
        segment = "Mặt Bằng Cho Thuê Q1"
        pitch = "Gửi danh sách 3 mặt bằng spa Quận 1 dưới 50tr/tháng, thỏa thuận điều khoản hợp đồng dài hạn."
    elif "căn hộ 2pn" in desc:
        segment = "Căn Hộ Gia Đình Trẻ Q7"
        pitch = "Gửi layout 2PN Quận 7, bảng tính chi tiết lãi suất vay 70% và chốt lịch xe đón xem nhà mẫu cuối tuần."
    elif "đất nền" in desc:
        segment = "Đất Nền Đầu Tư Vùng Ven"
        pitch = "Gửi trích lục sổ hồng riêng từng nền tại Long An/Đồng Nai tầm giá 2-3 tỷ, pháp lý sạch không dính quy hoạch."
    else:
        segment = "Chưa rõ phân khúc"
        pitch = "Xác nhận lại nhu cầu hoặc đưa vào danh sách lọc nếu có cờ đỏ."

    return {
        "score_budget": s_budget,
        "score_need": s_need,
        "score_timeline": s_timeline,
        "score_source": s_source,
        "score_engagement": s_engagement,
        "total_score": total_score,
        "ai_tier": tier,
        "lead_status": detail,
        "sla": sla,
        "segment": segment,
        "pitch": pitch,
        "vip_flags": "; ".join(vip_flags) if vip_flags else "Không",
        "red_flags": "; ".join(red_flags) if red_flags else "Không"
    }


def load_initial_data(url_or_path):
    """Tải và khởi tạo bảng dữ liệu với kết quả AI Scoring ban đầu."""
    try:
        if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
            if "spreadsheets/d/" in url_or_path:
                sheet_id = url_or_path.split("/d/")[1].split("/")[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                df = pd.read_csv(csv_url)
            else:
                df = pd.read_csv(url_or_path)
        else:
            if url_or_path.endswith(".xlsx"):
                df = pd.read_excel(url_or_path)
            else:
                df = pd.read_csv(url_or_path)
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return pd.DataFrame()

    df["sdt_chuan"] = df["sdt"].apply(clean_phone)
    
    # Chạy AI Scoring
    ai_results = []
    for _, row in df.iterrows():
        res = run_ai_scoring_agent(row.get("nhu_cau_mo_ta", ""))
        ai_results.append(res)
        
    res_df = pd.DataFrame(ai_results)
    combined_df = pd.concat([df, res_df], axis=1)

    # Thêm các cột phục vụ duyệt bởi con người (Human-in-the-loop)
    combined_df["human_approved"] = False
    combined_df["final_tier"] = combined_df["ai_tier"]
    combined_df["sales_assignee"] = combined_df["ai_tier"].apply(
        lambda t: "Trưởng phòng VIP / Giám đốc" if t == "HOT" else ("Senior Sales" if t == "WARM" else "Chưa phân bổ")
    )
    combined_df["review_note"] = ""

    return combined_df


# ==========================================
# 2. APPLICATION STATE MANAGEMENT
# ==========================================

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/17rbCAc-gDhSMesf7ILLCHofbg-89i-ecc9mOQPgH6Dg/export?format=csv"

if "leads_data" not in st.session_state:
    st.session_state["leads_data"] = load_initial_data(DEFAULT_SHEET_URL)


# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/942/942751.png", width=64)
    st.title("Điều Khiển Hệ Thống")
    st.caption("AI Agent Chấm Điểm & Phân Loại BĐS")

    st.markdown("---")
    st.subheader("📥 Nguồn Dữ Liệu")
    data_source_mode = st.radio(
        "Chọn nguồn:",
        ["Google Sheets Mặc Định", "Tải Lên File CSV / Excel", "Dữ Liệu Local Mẫu"],
        index=0
    )

    if data_source_mode == "Google Sheets Mặc Định":
        sheet_url_input = st.text_input(
            "Google Sheets URL:",
            value="https://docs.google.com/spreadsheets/d/17rbCAc-gDhSMesf7ILLCHofbg-89i-ecc9mOQPgH6Dg/edit?usp=sharing"
        )
        if st.button("🔄 Tải lại dữ liệu từ Sheet", use_container_width=True):
            with st.spinner("Đang kết nối Google Sheets & Quét AI Scoring..."):
                st.session_state["leads_data"] = load_initial_data(sheet_url_input)
                st.success("Đã đồng bộ dữ liệu thành công!")
                st.rerun()

    elif data_source_mode == "Tải Lên File CSV / Excel":
        uploaded_file = st.file_uploader("Chọn file CSV hoặc Excel", type=["csv", "xlsx"])
        if uploaded_file is not None:
            if st.button("🚀 Chạy AI Scoring File Này", use_container_width=True):
                with st.spinner("Đang đọc file và chấm điểm..."):
                    if uploaded_file.name.endswith(".xlsx"):
                        raw_df = pd.read_excel(uploaded_file)
                    else:
                        raw_df = pd.read_csv(uploaded_file)
                    # Chạy pipeline
                    raw_df["sdt_chuan"] = raw_df["sdt"].apply(clean_phone)
                    ai_results = [run_ai_scoring_agent(r.get("nhu_cau_mo_ta", "")) for _, r in raw_df.iterrows()]
                    res_df = pd.DataFrame(ai_results)
                    merged = pd.concat([raw_df, res_df], axis=1)
                    merged["human_approved"] = False
                    merged["final_tier"] = merged["ai_tier"]
                    merged["sales_assignee"] = merged["ai_tier"].apply(
                        lambda t: "Trưởng phòng VIP" if t == "HOT" else ("Senior Sales" if t == "WARM" else "Chưa phân bổ")
                    )
                    merged["review_note"] = ""
                    st.session_state["leads_data"] = merged
                    st.success(f"Đã xử lý {len(merged)} khách hàng!")
                    st.rerun()

    else:
        if st.button("📂 Nạp sample-data/real_estate_leads_raw.csv", use_container_width=True):
            local_path = "sample-data/real_estate_leads_raw.csv"
            if os.path.exists(local_path):
                st.session_state["leads_data"] = load_initial_data(local_path)
                st.success("Đã nạp file mẫu local!")
                st.rerun()
            else:
                st.error("Không tìm thấy file sample-data/real_estate_leads_raw.csv")

    st.markdown("---")
    st.subheader("⚡ Thao Tác Nhanh")
    if st.button("✨ Tự Động Phê Duyệt Toàn Bộ Theo AI", use_container_width=True):
        if not st.session_state["leads_data"].empty:
            st.session_state["leads_data"]["human_approved"] = True
            st.session_state["leads_data"]["final_tier"] = st.session_state["leads_data"]["ai_tier"]
            st.session_state["leads_data"]["review_note"] = "Tự động duyệt hàng loạt theo đề xuất AI"
            st.success("Đã phê duyệt 100% danh sách!")
            st.rerun()

    if st.button("🗑️ Reset Về Trạng Thái Chờ Duyệt", use_container_width=True):
        if not st.session_state["leads_data"].empty:
            st.session_state["leads_data"]["human_approved"] = False
            st.session_state["leads_data"]["review_note"] = ""
            st.info("Đã reset trạng thái duyệt về ban đầu.")
            st.rerun()

    st.markdown("---")
    st.subheader("🔐 Google Service Account")
    gc_test = get_gspread_client()
    if gc_test:
        st.success("🟢 Service Account: Đã kết nối")
        st.caption("`streamlit-lead-score@agent-expense-tracker.iam.gserviceaccount.com`")
    else:
        st.warning("🟡 Service Account: Chưa cấu hình (Chỉ xem)")
        st.caption("Cần cấu hình Secrets trên Streamlit Cloud để bật đồng bộ 2 chiều.")


# ==========================================
# 4. MAIN DASHBOARD CONTENT
# ==========================================

st.markdown('<div class="main-title">🏢 Hệ Thống Chấm Điểm & Thẩm Định Khách Hàng BĐS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Kết hợp AI Agent tự động hóa NLP với cơ chế Phê duyệt Con người (Human-in-the-Loop Review)</div>', unsafe_allow_html=True)

df_current = st.session_state["leads_data"]

if df_current.empty:
    st.warning("Chưa có dữ liệu khách hàng. Vui lòng kiểm tra lại nguồn dữ liệu trong Sidebar.")
    st.stop()

# 4.1. KPI SUMMARY CARDS
total_leads = len(df_current)
approved_count = int(df_current["human_approved"].sum())
hot_count = int((df_current["final_tier"] == "HOT").sum())
warm_count = int((df_current["final_tier"] == "WARM").sum())
cold_junk_count = total_leads - hot_count - warm_count

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Tổng Số Leads</div>
        <div class="kpi-value" style="color: #1E293B;">{total_leads}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Tiến Độ Duyệt</div>
        <div class="kpi-value" style="color: #2563EB;">{approved_count}/{total_leads} <span style="font-size: 1rem; color:#64748B;">({approved_count/total_leads*100:.0f}%)</span></div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🔥 HOT Leads (VIP)</div>
        <div class="kpi-value" style="color: #DC2626;">{hot_count}</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">⚡ WARM Leads</div>
        <div class="kpi-value" style="color: #D97706;">{warm_count}</div>
    </div>
    """, unsafe_allow_html=True)
with c5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">❄️ COLD / JUNK</div>
        <div class="kpi-value" style="color: #64748B;">{cold_junk_count}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# 4.2. TAB INTERFACE
tab_editor, tab_handover, tab_analytics, tab_playground, tab_rubric = st.tabs([
    "📋 Bảng Duyệt Trạng Thái (Data Editor)",
    "🎯 Danh Sách Bàn Giao Sales",
    "📊 Phân Tích & Biểu Đồ BI",
    "🤖 Thử Nghiệm AI Scoring Trực Tiếp",
    "📜 Tiêu Chuẩn & Ma Trận Điểm"
])

# ----------------------------------------------------
# TAB 1: DATA EDITOR (HUMAN-IN-THE-LOOP)
# ----------------------------------------------------
with tab_editor:
    st.markdown("### 📝 Thẩm Định & Phê Duyệt Trạng Thái Khách Hàng")
    st.caption("Quản lý và Sales Leader có thể chỉnh sửa trực tiếp cờ Duyệt (`human_approved`), Phân loại thực tế (`final_tier`), Người phụ trách (`sales_assignee`) và Ghi chú.")

    col_filter1, col_filter2 = st.columns([2, 2])
    with col_filter1:
        filter_status = st.multiselect(
            "Lọc theo Phân Hạng:",
            ["HOT", "WARM", "COLD", "JUNK"],
            default=["HOT", "WARM", "COLD", "JUNK"]
        )
    with col_filter2:
        filter_approved = st.radio(
            "Trạng thái duyệt:",
            ["Tất cả", "Chưa duyệt (Pending)", "Đã duyệt (Approved)"],
            horizontal=True
        )

    # Áp dụng bộ lọc view
    filtered_df = df_current[df_current["final_tier"].isin(filter_status)].copy()
    if filter_approved == "Chưa duyệt (Pending)":
        filtered_df = filtered_df[filtered_df["human_approved"] == False]
    elif filter_approved == "Đã duyệt (Approved)":
        filtered_df = filtered_df[filtered_df["human_approved"] == True]

    # Các cột hiển thị trong editor
    columns_for_editor = [
        "id", "human_approved", "ten_khach", "sdt_chuan", "nhu_cau_mo_ta",
        "total_score", "ai_tier", "final_tier", "sales_assignee", "review_note",
        "segment", "red_flags", "vip_flags"
    ]
    
    # Chỉ lấy các cột tồn tại
    columns_for_editor = [c for c in columns_for_editor if c in filtered_df.columns]

    # Cấu hình data_editor trực quan
    column_config = {
        "id": st.column_config.NumberColumn("Mã ID", width="small", disabled=True),
        "human_approved": st.column_config.CheckboxColumn(
            "Duyệt? (Approve)",
            help="Tích chọn để xác nhận hoàn tất phê duyệt chuyển giao Sales",
            default=False
        ),
        "ten_khach": st.column_config.TextColumn("Họ Tên", width="medium", disabled=True),
        "sdt_chuan": st.column_config.TextColumn("Số ĐT", width="small", disabled=True),
        "nhu_cau_mo_ta": st.column_config.TextColumn("Mô Tả Nhu Cầu Gốc", width="large", disabled=True),
        "total_score": st.column_config.ProgressColumn(
            "Điểm AI",
            format="%d",
            min_value=0,
            max_value=100,
            width="small"
        ),
        "ai_tier": st.column_config.TextColumn("AI Gợi Ý", width="small", disabled=True),
        "final_tier": st.column_config.SelectboxColumn(
            "Trạng Thái Thực Tế",
            options=["HOT", "WARM", "COLD", "JUNK"],
            help="Người quản lý có thể điều chỉnh lại Tier nếu AI nhận định chưa chuẩn",
            required=True,
            width="small"
        ),
        "sales_assignee": st.column_config.SelectboxColumn(
            "Sales Phụ Trách",
            options=["Trưởng phòng VIP / Giám đốc", "Senior Sales", "Account Executive", "Chưa phân bổ", "Đưa vào Drip Campaign"],
            width="medium"
        ),
        "review_note": st.column_config.TextColumn("Ghi Chú Thẩm Định", width="medium"),
        "segment": st.column_config.TextColumn("Phân Khúc BĐS", width="medium", disabled=True),
        "red_flags": st.column_config.TextColumn("Cờ Đỏ (Red Flags)", width="medium", disabled=True),
        "vip_flags": st.column_config.TextColumn("Cờ VIP", width="medium", disabled=True),
    }

    # Bảng tương tác data_editor
    edited_df = st.data_editor(
        filtered_df[columns_for_editor],
        column_config=column_config,
        disabled=["id", "ten_khach", "sdt_chuan", "nhu_cau_mo_ta", "total_score", "ai_tier", "segment", "red_flags", "vip_flags"],
        hide_index=True,
        use_container_width=True,
        key="leads_editor"
    )

    col_btn1, col_btn2, col_btn3 = st.columns([2.5, 3.5, 2.5])
    with col_btn1:
        if st.button("💾 Lưu Trạng Thái Duyệt", type="primary", use_container_width=True):
            for _, row in edited_df.iterrows():
                row_id = row["id"]
                match_idx = st.session_state["leads_data"][st.session_state["leads_data"]["id"] == row_id].index
                if len(match_idx) > 0:
                    idx = match_idx[0]
                    st.session_state["leads_data"].at[idx, "human_approved"] = row["human_approved"]
                    st.session_state["leads_data"].at[idx, "final_tier"] = row["final_tier"]
                    st.session_state["leads_data"].at[idx, "sales_assignee"] = row["sales_assignee"]
                    st.session_state["leads_data"].at[idx, "review_note"] = row["review_note"]
            st.success("✅ Đã lưu và cập nhật trạng thái phê duyệt!")
            st.rerun()

    with col_btn2:
        if st.button("☁️ Đồng Bộ Lên Google Sheet", use_container_width=True):
            # Lấy URL Google Sheet hiện tại từ sidebar
            target_sheet_url = sheet_url_input if "sheet_url_input" in locals() and sheet_url_input else DEFAULT_SHEET_URL
            with st.spinner("Đang kết nối Service Account và đẩy dữ liệu lên Google Sheet..."):
                try:
                    s_url, ws_title = sync_to_google_sheet(st.session_state["leads_data"], target_sheet_url, "Lead_Scored_Reviewed")
                    st.success(f"🎉 Đã đồng bộ thành công vào Tab **'{ws_title}'**!")
                    st.markdown(f"👉 [Mở Google Sheet để kiểm tra]({s_url})")
                except Exception as ex:
                    st.error(f"❌ Lỗi đồng bộ Google Sheet: {ex}")
                    st.caption("Hãy kiểm tra cấu hình Secrets trên Streamlit Cloud hoặc quyền chia sẻ của Google Sheet.")

    with col_btn3:
        # Xuất file Excel đã duyệt
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            st.session_state["leads_data"].to_excel(writer, sheet_name="Reviewed Leads", index=False)
        st.download_button(
            label="📥 Tải File Excel (.xlsx)",
            data=excel_buffer.getvalue(),
            file_name=f"BDS_Lead_Scoring_Reviewed_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ----------------------------------------------------
# TAB 2: SALES HANDOVER PACKAGE
# ----------------------------------------------------
with tab_handover:
    st.markdown("### 🎯 Danh Sách Bàn Giao Cho Bộ Phận Kinh Doanh (Sales)")
    st.caption("Chỉ hiển thị các khách hàng thuộc Tier HOT hoặc WARM đã được xác thực, kèm theo SLA tiếp cận và kịch bản mở đầu.")

    qualified_leads = df_current[df_current["final_tier"].isin(["HOT", "WARM"])].sort_values(by="total_score", ascending=False)

    if qualified_leads.empty:
        st.info("Hiện không có Lead nào thuộc nhóm HOT hoặc WARM.")
    else:
        for _, lead in qualified_leads.iterrows():
            tier_badge = "🔥 HOT (VIP)" if lead["final_tier"] == "HOT" else "⚡ WARM"
            card_border = "#EF4444" if lead["final_tier"] == "HOT" else "#F59E0B"
            approved_tag = "✅ ĐÃ PHÊ DUYỆT" if lead["human_approved"] else "⏳ CHỜ DUYỆT"
            
            with st.container():
                st.markdown(f"""
                <div style="border-left: 5px solid {card_border}; background-color: #FAFAFA; padding: 14px 20px; border-radius: 8px; margin-bottom: 12px; border-top: 1px solid #E5E7EB; border-right: 1px solid #E5E7EB; border-bottom: 1px solid #E5E7EB;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 1.15rem; font-weight: 700; color: #1E293B;">
                            #{lead['id']} — {lead['ten_khach']} &nbsp;
                            <span style="font-size: 0.95rem; font-weight: 600; color: #2563EB;">📞 {lead['sdt_chuan']}</span>
                        </span>
                        <div>
                            <span style="font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; background: {'#FEE2E2' if lead['final_tier']=='HOT' else '#FEF3C7'}; color: {'#991B1B' if lead['final_tier']=='HOT' else '#92400E'};">{tier_badge}</span>
                            &nbsp;
                            <span style="font-weight: 600; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; background: #E2E8F0; color: #475569;">Điểm AI: {lead['total_score']}</span>
                            &nbsp;
                            <span style="font-size: 0.8rem; font-weight: 600; color: {'#059669' if lead['human_approved'] else '#D97706'};">{approved_tag}</span>
                        </div>
                    </div>
                    <div style="font-size: 0.95rem; color: #334155; margin-bottom: 8px;">
                        <b>Phân khúc đề xuất:</b> <span style="color: #0369A1; font-weight: 600;">{lead['segment']}</span> &nbsp;|&nbsp; 
                        <b>Nhân sự phụ trách:</b> <span style="font-weight: 600;">{lead['sales_assignee']}</span> &nbsp;|&nbsp; 
                        <b>SLA:</b> <span style="color: #DC2626; font-weight: 600;">{lead['sla']}</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #475569; background: #FFFFFF; padding: 8px 12px; border-radius: 6px; border: 1px dashed #CBD5E1; margin-bottom: 6px;">
                        <b>💬 Kịch bản gợi ý mở đầu (Pitch Angle):</b> {lead['pitch']}
                    </div>
                    <div style="font-size: 0.85rem; color: #64748B;">
                        <i>Nhu cầu gốc: "{lead['nhu_cau_mo_ta']}"</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ----------------------------------------------------
# TAB 3: ANALYTICS & BI
# ----------------------------------------------------
with tab_analytics:
    st.markdown("### 📊 Phân Tích Thống Kê & Hiệu Suất Leads")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.subheader("Phân Bổ Tỷ Lệ Theo Final Tier")
        tier_counts = df_current["final_tier"].value_counts().reset_index()
        tier_counts.columns = ["Tier", "Số Lượng"]
        st.bar_chart(tier_counts.set_index("Tier"), color="#1E3A8A")

    with col_a2:
        st.subheader("Phân Bổ Theo Phân Khúc BĐS")
        seg_counts = df_current["segment"].value_counts().reset_index()
        seg_counts.columns = ["Phân Khúc", "Số Lượng"]
        st.dataframe(seg_counts, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Ma Trận Điểm Trung Bình 5 Tiêu Chí Theo Tier")
    pillar_summary = df_current.groupby("final_tier")[
        ["score_budget", "score_need", "score_timeline", "score_source", "score_engagement", "total_score"]
    ].mean().round(1)
    st.dataframe(pillar_summary, use_container_width=True)

# ----------------------------------------------------
# TAB 4: PLAYGROUND (AI TESTER)
# ----------------------------------------------------
with tab_playground:
    st.markdown("### 🤖 Thử Nghiệm AI Scoring Agent Với Khách Hàng Bất Kỳ")
    st.caption("Nhập tên, số điện thoại và mô tả nhu cầu thực tế để xem AI bóc tách và tính điểm 5 trụ cột ngay lập tức.")

    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        test_name = st.text_input("Tên khách hàng:", value="Trần Thị Bích")
        test_phone = st.text_input("Số điện thoại:", value="0988776655")
        test_desc = st.text_area(
            "Nội dung mô tả nhu cầu:",
            value="Quan tâm Penthouse ven sông Quận 1, yêu cầu có hồ bơi riêng. Tài chính trên 40 tỷ thanh toán thẳng. Muốn gặp trực tiếp Giám đốc dự án để đàm phán trong tuần này.",
            height=140
        )
        run_test_btn = st.button("⚡ Chấm Điểm Thử Nghiệm", use_container_width=True, type="primary")

    with col_p2:
        if run_test_btn or test_desc:
            test_res = run_ai_scoring_agent(test_desc)
            st.markdown(f"#### Kết Quả Đánh Giá: **{test_res['ai_tier']}** ({test_res['total_score']} Điểm)")
            
            p1, p2, p3, p4, p5 = st.columns(5)
            p1.metric("Ngân Sách (Max 35)", test_res["score_budget"])
            p2.metric("Nhu Cầu (Max 25)", test_res["score_need"])
            p3.metric("Thời Gian (Max 20)", test_res["score_timeline"])
            p4.metric("Hồ Sơ (Max 10)", test_res["score_source"])
            p5.metric("Tương Tác (Max 10)", test_res["score_engagement"])

            st.write(f"🚩 **Cờ VIP nhận diện:** `{test_res['vip_flags']}`")
            st.write(f"⚠️ **Cờ đỏ (Red Flags):** `{test_res['red_flags']}`")
            st.write(f"🏠 **Phân khúc BĐS:** **{test_res['segment']}**")
            st.write(f"⏱️ **SLA đề xuất:** {test_res['sla']}")
            st.info(f"💡 **Kịch bản mở đầu đề xuất:** {test_res['pitch']}")

            if st.button("➕ Thêm Khách Hàng Này Vào Danh Sách Quản Lý"):
                new_id = int(df_current["id"].max() + 1) if not df_current.empty else 1
                new_row = {
                    "id": new_id,
                    "ten_khach": test_name,
                    "sdt": test_phone,
                    "sdt_chuan": clean_phone(test_phone),
                    "nhu_cau_mo_ta": test_desc,
                    "human_approved": False,
                    "final_tier": test_res["ai_tier"],
                    "sales_assignee": "Trưởng phòng VIP / Giám đốc" if test_res["ai_tier"] == "HOT" else "Senior Sales",
                    "review_note": "Thêm mới từ AI Playground",
                    **test_res
                }
                st.session_state["leads_data"] = pd.concat([st.session_state["leads_data"], pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Đã thêm #{new_id} ({test_name}) vào hệ thống!")
                st.rerun()

# ----------------------------------------------------
# TAB 5: SCORING RUBRIC & CRITERIA
# ----------------------------------------------------
with tab_rubric:
    st.markdown("### 📜 Ma Trận Tiêu Chuẩn Nghiệp Vụ (tieu_chi_cham_diem.txt)")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.success("""
        #### 🌟 TIÊU CHÍ CỘNG 50 ĐIỂM (VIP / SIÊU TIỀM NĂNG)
        AI tự động nhận diện các yếu tố sau để cộng điểm và kích hoạt HOT Tier:
        - **Ngân sách lớn:** Từ 20 tỷ trở lên, "tài chính mạnh", "không thành vấn đề", thanh toán thẳng.
        - **Loại hình cao cấp:** Penthouse, Biệt thự đơn lập, Shophouse mặt đường lớn, Quỹ đất công nghiệp, Sàn văn phòng diện tích lớn.
        - **Vị trí đắc địa:** Quận 1, Ven sông, Vinhomes Ocean Park, Phú Mỹ Hưng.
        - **Đối tượng VIP:** Chủ doanh nghiệp, Nhà đầu tư chuyên nghiệp, Mua sỉ, Gom sỉ.
        - **Tính cấp thiết & Minh bạch:** Pháp lý chuẩn 100%, Sổ hồng riêng, Muốn gặp trực tiếp chủ đầu tư để đàm phán.
        """)

    with col_r2:
        st.error("""
        #### 🚫 TIÊU CHÍ TRỪ 50 ĐIỂM (KHÁCH HÀNG RÁC / BLACKLIST)
        AI tự động kích hoạt Red Flags và đưa vào nhóm JUNK / COLD:
        - **Yêu cầu phi thực tế:** Tìm mua giá thấp vô lý (nhà Q1 giá 1-2 tỷ, thuê trung tâm 2 triệu).
        - **Không có nhu cầu:** Nhầm số, dữ liệu cũ, nhầm ngành.
        - **Không thiện chí:** Hỏi giá cho vui, chưa có ý định mua, thái độ bất hợp tác.
        - **Spam / Quảng cáo:** Chào mời bảo hiểm, vay vốn, dịch vụ khác.
        - **Lỗi liên lạc:** Thuê bao, gọi nhiều lần không bắt máy, không phản hồi Zalo.
        """)

    st.info("""
    #### ⚖️ NHÓM TẦM TRUNG (GIỮ NGUYÊN ĐIỂM HOẶC CỘNG ÍT — WARM TIER: 50–79 ĐIỂM)
    - Khách hàng tìm mua chung cư, nhà phố tầm trung (3–10 tỷ).
    - Khách hàng cần vay ngân hàng, đang cân nhắc gói lãi suất.
    - Khách hàng thuê mặt bằng kinh doanh spa (dưới 50 triệu/tháng).
    - Khách hàng tìm đất nền vùng ven (Long An, Đồng Nai) giá 2–3 tỷ có sổ hồng riêng.
    """)

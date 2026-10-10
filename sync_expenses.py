#!/usr/bin/env python3
"""
sync_expenses.py
=============================================================================
HỆ THỐNG ĐỒNG BỘ CHI PHÍ & TỰ ĐỘNG DUYỆT HẠN MỨC (ACCOUNTING RPA)
Tích hợp Google Gemini AI Auditor: Tự động phân loại danh mục & sinh AI Note
Chạy trực tiếp từ Workspace với Python + Google Sheets API (gspread & OAuth 2.0)
=============================================================================
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import gspread
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Tải biến môi trường (GEMINI_API_KEY)
load_dotenv()

# CẤU HÌNH HỆ THỐNG KẾ TOÁN
CONFIG = {
    "EMPLOYEE_SPREADSHEET_ID": "1NszVybLflwlyv2GLkXjvP8lLLKoFMdoycGSV7nVpACs",
    "ADMIN_SPREADSHEET_ID": "1ALXLqnH5UlzkM0mNvM1e8P3Z4vQairDLC1hbkF9hR5I",
    "AUTO_APPROVAL_LIMIT": 500000,
    "STATUS_APPROVED": "Đã duyệt",
    "STATUS_PENDING": "Chờ duyệt",
    "SYNC_DONE": "Done",
    "CREDENTIALS_FILE": "Credentials.json",
    "TOKEN_FILE": "token.json",
    "GEMINI_MODEL": "gemini-2.5-flash",
}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_oauth_credentials():
    """Xác thực Google OAuth 2.0."""
    workspace_dir = Path(__file__).resolve().parent
    creds_path = workspace_dir / CONFIG["CREDENTIALS_FILE"]
    token_path = workspace_dir / CONFIG["TOKEN_FILE"]

    if not creds_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy tệp {CONFIG['CREDENTIALS_FILE']} tại: {workspace_dir}"
        )

    creds = None
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception as e:
            print(f"⚠️ Không thể đọc token cũ ({e}), tiến hành đăng nhập lại...")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            print("\n🔑 Mở trình duyệt để xác thực quyền truy cập Google Sheets...")
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())
        print(f"✅ Đã lưu phiên đăng nhập vào {CONFIG['TOKEN_FILE']}\n")

    return creds


def find_header_index(headers, aliases):
    """Tìm vị trí cột linh hoạt theo danh sách từ khóa tiêu đề."""
    clean_headers = [str(h).strip().lower() for h in headers]
    for i, h in enumerate(clean_headers):
        for alias in aliases:
            if h == alias or alias in h:
                return i
    return -1


def parse_numeric_amount(val):
    """Làm sạch và trích xuất giá trị số tiền (Amount)."""
    if isinstance(val, (int, float)):
        return float(val)
    if not val:
        return 0.0
    clean_str = re.sub(r"[^\d.-]", "", str(val).strip())
    try:
        return float(clean_str)
    except ValueError:
        return 0.0


def format_currency(amount):
    """Định dạng tiền tệ VNĐ hiển thị chuyên nghiệp."""
    return f"{int(amount):,} VNĐ".replace(",", ".")


def generate_ai_accounting_audit(items_list):
    """
    Sử dụng Gemini AI để đóng vai trò Chuyên viên Kế toán Trưởng:
    - Tự động phân loại danh mục (Category)
    - Tự động sinh nhận xét kiểm soát chứng từ và hạn mức (AI Note)
    Có cơ chế Fallback nếu mất kết nối mạng hoặc không có API Key.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ Không tìm thấy GEMINI_API_KEY trong .env. Sử dụng bộ quy tắc kế toán dự phòng.")
        return fallback_accounting_rules(items_list)

    print(f"🤖 Đang kết nối Gemini AI ({CONFIG['GEMINI_MODEL']}) phân tích nghiệp vụ kế toán cho {len(items_list)} khoản chi...")
    
    prompt_items = [
        {"employee": x["employee"], "item": x["item"], "amount": x["amount"]}
        for x in items_list
    ]

    prompt = f"""Bạn là Chuyên viên Kế toán Trưởng kiểm soát chi phí doanh nghiệp.
Hãy phân tích danh sách các khoản chi sau đây và sinh Category (Danh mục chi phí tiếng Việt có dấu) cùng AI Note (Ghi chú kế toán ngắn gọn, nhận xét về tính hợp lệ, hạn mức 500.000đ và chứng từ cần thiết).

Dữ liệu đầu vào:
{json.dumps(prompt_items, ensure_ascii=False, indent=2)}

Yêu cầu trả về JSON Array tương ứng chính xác theo thứ tự từng phần tử đầu vào, không thêm bất kỳ định dạng nào khác ngoài JSON:
[
  {{
    "category": "Tiếp khách",
    "ai_note": "Khoản chi lớn hơn 500.000đ, cần phê duyệt cấp quản lý và bổ sung chứng từ tiếp khách."
  }}
]
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{CONFIG['GEMINI_MODEL']}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    try:
        resp = requests.post(url, json=payload, timeout=25)
        if resp.status_code == 200:
            res_data = resp.json()
            raw_json = res_data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw_json)
            if isinstance(parsed, list) and len(parsed) == len(items_list):
                print("  ✅ Gemini AI đã phân tích thành công Category và AI Note cho toàn bộ bản ghi.")
                return parsed
        print(f"⚠️ Lỗi gọi Gemini API (Status {resp.status_code}). Chuyển sang quy tắc dự phòng.")
    except Exception as err:
        print(f"⚠️ Lỗi kết nối AI ({err}). Chuyển sang quy tắc dự phòng.")

    return fallback_accounting_rules(items_list)


def fallback_accounting_rules(items_list):
    """Quy tắc kế toán nội bộ dự phòng khi không gọi được Gemini API."""
    results = []
    for x in items_list:
        item_lower = x["item"].lower()
        amount = x["amount"]

        if any(k in item_lower for k in ["taxi", "grab", "uber", "xe", "xang"]):
            cat = "Di chuyển"
            note = "Chi phí đi lại/công tác, cần cung cấp hóa đơn hoặc biên lai điện tử."
        elif any(k in item_lower for k in ["tiep khach", "doi tac", "khach hang"]):
            cat = "Tiếp khách"
            if amount >= CONFIG["AUTO_APPROVAL_LIMIT"]:
                note = "Khoản chi lớn hơn 500.000đ, cần phê duyệt cấp quản lý và bổ sung chứng từ tiếp khách."
            else:
                note = "Chi phí tiếp khách trong hạn mức, cần hóa đơn GTGT."
        elif any(k in item_lower for k in ["cf", "cafe", "ca phe", "an toi", "an sang", "an trua", "team"]):
            cat = "Ăn uống"
            note = "Chi phí ăn uống nội bộ, mức chi nằm trong hạn mức cho phép."
        elif any(k in item_lower for k in ["vpp", "but", "giay"]):
            cat = "Văn phòng"
            note = "Mua sắm vật tư văn phòng, đầy đủ thông tin và mức chi hợp lý."
        else:
            cat = "Chi phí chung"
            note = "Cần theo dõi và bổ sung chứng từ thanh toán hợp lệ."

        results.append({"category": cat, "ai_note": note})
    return results


def run_expense_sync():
    """Quy trình đồng bộ 3 Nhịp chuẩn nghiệp vụ Kế toán kèm AI Note."""
    print("=" * 70)
    print("⚡ KHỞI ĐỘNG HỆ THỐNG ĐỒNG BỘ CHI PHÍ & AI AUDITOR")
    print("=" * 70)

    creds = get_oauth_credentials()
    gc = gspread.authorize(creds)

    print("📊 Đang kết nối tới 2 bảng tính Google Sheets...")
    try:
        source_sh = gc.open_by_key(CONFIG["EMPLOYEE_SPREADSHEET_ID"]).sheet1
        print(f"  • Source (Employee Data): OK ({source_sh.title})")
    except Exception as e:
        print(f"❌ Lỗi truy cập file Employee Data: {e}")
        return

    try:
        target_sh = gc.open_by_key(CONFIG["ADMIN_SPREADSHEET_ID"]).sheet1
        print(f"  • Target (Admin Expense Tracker): OK ({target_sh.title})")
    except Exception as e:
        print(f"❌ Lỗi truy cập file Admin Expense Tracker: {e}")
        return

    # -------------------------------------------------------------
    # NHỊP 1: QUÉT THÔNG MINH
    # -------------------------------------------------------------
    print("\n🔍 [NHỊP 1] Đang quét dữ liệu từ Employee Data...")
    source_rows = source_sh.get_all_values()
    if len(source_rows) <= 1:
        print("ℹ️ Bảng tính Employee Data không có dữ liệu chi phí nào!")
        return

    headers = source_rows[0]
    col_idx = {
        "date": find_header_index(headers, ["date", "ngày"]),
        "employee": find_header_index(headers, ["employee", "nhân viên", "người chi"]),
        "item": find_header_index(headers, ["item", "khoản chi", "nội dung"]),
        "amount": find_header_index(headers, ["amount", "số tiền", "chi phí"]),
        "category": find_header_index(headers, ["category", "danh mục", "loại chi phí"]),
        "status": find_header_index(headers, ["status", "trạng thái", "phê duyệt"]),
        "sync": find_header_index(headers, ["syncstatus", "sync status", "trạng thái đồng bộ"]),
        "synced_at": find_header_index(headers, ["syncedat", "synced at", "thời gian sync", "ngày sync"]),
    }

    if col_idx["amount"] == -1 or col_idx["sync"] == -1:
        print("❌ Lỗi cấu trúc: Không tìm thấy cột 'Amount' hoặc 'SyncStatus' trong Employee Data!")
        return

    rows_to_sync = []
    source_row_numbers = []

    force_sync = "--force" in sys.argv or "--all" in sys.argv
    if force_sync:
        print("⚠️ Đang kích hoạt chế độ FORCE SYNC: Đồng bộ tất cả bản ghi (bỏ qua kiểm tra 'Done').")

    for r_idx, row in enumerate(source_rows[1:], start=2):
        sync_val = str(row[col_idx["sync"]]).strip().lower() if col_idx["sync"] < len(row) else ""
        if sync_val == "done" and not force_sync:
            continue

        amount_raw = row[col_idx["amount"]] if col_idx["amount"] < len(row) else 0
        amount_num = parse_numeric_amount(amount_raw)
        item_text = row[col_idx["item"]] if (col_idx["item"] != -1 and col_idx["item"] < len(row)) else ""

        if amount_num == 0 and not item_text:
            continue

        # RÀNG BUỘC PHÊ DUYỆT HẠN MỨC
        if amount_num < CONFIG["AUTO_APPROVAL_LIMIT"]:
            approval_status = CONFIG["STATUS_APPROVED"]
        else:
            approval_status = CONFIG["STATUS_PENDING"]

        record = {
            "date": row[col_idx["date"]] if (col_idx["date"] != -1 and col_idx["date"] < len(row)) else "",
            "employee": row[col_idx["employee"]] if (col_idx["employee"] != -1 and col_idx["employee"] < len(row)) else "",
            "item": item_text,
            "amount": amount_num,
            "category": row[col_idx["category"]] if (col_idx["category"] != -1 and col_idx["category"] < len(row)) else "",
            "status": approval_status,
        }
        rows_to_sync.append(record)
        source_row_numbers.append(r_idx)

    # -------------------------------------------------------------
    # KIỂM TRA & CẬP NHẬT RIÊNG CỘT AI NOTE VÀO ADMIN NẾU ĐÃ CÓ DỮ LIỆU
    # -------------------------------------------------------------
    target_all_rows = target_sh.get_all_values()
    target_headers = target_all_rows[0] if target_all_rows else []
    target_col_count = max(len(target_headers), 7)

    target_col_idx = {
        "date": find_header_index(target_headers, ["date", "ngày"]),
        "employee": find_header_index(target_headers, ["employee", "nhân viên"]),
        "item": find_header_index(target_headers, ["item", "khoản chi", "nội dung"]),
        "amount": find_header_index(target_headers, ["amount", "số tiền"]),
        "category": find_header_index(target_headers, ["category", "danh mục"]),
        "status": find_header_index(target_headers, ["status", "trạng thái"]),
        "ai_note": find_header_index(target_headers, ["ai note", "ai_note", "ghi chú ai", "note ai"]),
    }

    # Nếu không có dòng mới từ Employee Data nhưng bảng Admin đang thiếu AI Note
    if len(rows_to_sync) == 0:
        if len(target_all_rows) > 1 and target_col_idx["ai_note"] != -1:
            # Kiểm tra xem có dòng nào trong Admin thiếu AI Note không
            empty_ai_note_rows = []
            for r_i, r in enumerate(target_all_rows[1:], start=2):
                ai_val = r[target_col_idx["ai_note"]] if target_col_idx["ai_note"] < len(r) else ""
                if not ai_val.strip():
                    item_val = r[target_col_idx["item"]] if target_col_idx["item"] < len(r) else ""
                    emp_val = r[target_col_idx["employee"]] if target_col_idx["employee"] < len(r) else ""
                    amt_val = parse_numeric_amount(r[target_col_idx["amount"]]) if target_col_idx["amount"] < len(r) else 0
                    empty_ai_note_rows.append({
                        "row_num": r_i,
                        "employee": emp_val,
                        "item": item_val,
                        "amount": amt_val
                    })

            if empty_ai_note_rows:
                print(f"💡 Phát hiện {len(empty_ai_note_rows)} dòng trong Admin Tracker đang thiếu 'AI Note' & 'Category'.")
                ai_results = generate_ai_accounting_audit(empty_ai_note_rows)
                
                cells_to_fix = []
                for idx, entry in enumerate(empty_ai_note_rows):
                    ai_info = ai_results[idx]
                    r_num = entry["row_num"]
                    if target_col_idx["category"] != -1:
                        cells_to_fix.append(gspread.Cell(row=r_num, col=target_col_idx["category"] + 1, value=ai_info["category"]))
                    if target_col_idx["ai_note"] != -1:
                        cells_to_fix.append(gspread.Cell(row=r_num, col=target_col_idx["ai_note"] + 1, value=ai_info["ai_note"]))
                
                target_sh.update_cells(cells_to_fix)
                print(f"✅ Đã cập nhật thành công AI Note & Category cho {len(empty_ai_note_rows)} dòng trong Admin Tracker!\n")
                return

        print("✅ Tất cả dữ liệu đã được đồng bộ trước đó. Không có bản ghi mới.")
        return

    # Sinh Category & AI Note bằng Gemini cho các dòng mới cần đồng bộ
    ai_insights = generate_ai_accounting_audit(rows_to_sync)
    for i, item in enumerate(rows_to_sync):
        item["category"] = ai_insights[i]["category"]
        item["ai_note"] = ai_insights[i]["ai_note"]

    # -------------------------------------------------------------
    # NHỊP 2: GHI NỐI TIẾP VÀO ADMIN TRACKER
    # -------------------------------------------------------------
    print("\n📤 [NHỊP 2] Ghi nối tiếp dữ liệu sang Admin Expense Tracker...")
    target_matrix = []
    for item in rows_to_sync:
        row_cells = [""] * target_col_count
        if target_col_idx["date"] != -1: row_cells[target_col_idx["date"]] = item["date"]
        if target_col_idx["employee"] != -1: row_cells[target_col_idx["employee"]] = item["employee"]
        if target_col_idx["item"] != -1: row_cells[target_col_idx["item"]] = item["item"]
        if target_col_idx["amount"] != -1: row_cells[target_col_idx["amount"]] = item["amount"]
        if target_col_idx["category"] != -1: row_cells[target_col_idx["category"]] = item["category"]
        if target_col_idx["status"] != -1: row_cells[target_col_idx["status"]] = item["status"]
        if target_col_idx["ai_note"] != -1: row_cells[target_col_idx["ai_note"]] = item["ai_note"]
        target_matrix.append(row_cells)

    target_sh.append_rows(target_matrix, value_input_option="USER_ENTERED")
    print(f"  ✅ Đã ghi thành công {len(target_matrix)} dòng vào cuối Admin Expense Tracker.")

    # -------------------------------------------------------------
    # NHỊP 3: CHỐNG TRÙNG LẶP
    # -------------------------------------------------------------
    print("\n🔒 [NHỊP 3] Cập nhật 'Done' vào cột SyncStatus trên Employee Data...")
    sync_col_one_based = col_idx["sync"] + 1
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cells_to_update = []
    for row_num in source_row_numbers:
        cells_to_update.append(
            gspread.Cell(row=row_num, col=sync_col_one_based, value=CONFIG["SYNC_DONE"])
        )
        if col_idx["synced_at"] != -1:
            cells_to_update.append(
                gspread.Cell(row=row_num, col=col_idx["synced_at"] + 1, value=now_str)
            )

    source_sh.update_cells(cells_to_update)
    print(f"  ✅ Đã khóa trạng thái 'Done' và ghi nhận thời gian cho {len(source_row_numbers)} dòng trong Employee Data.")

    print("\n" + "=" * 70)
    print("📋 BÁO CÁO HOÀN THÀNH QUY TRÌNH KẾ TOÁN CHI PHÍ & AI NOTE")
    print("=" * 70)
    for i, item in enumerate(rows_to_sync, start=1):
        print(f"{i:<2} | {item['employee']:<8} | {item['item'][:18]:<18} | {format_currency(item['amount']):<14} | {item['category']:<15} | {item['status']:<10} | {item['ai_note']}")
    print("=" * 70)
    print("✅ Đồng bộ hoàn tất 100% kèm AI Note nghiệp vụ!\n")


if __name__ == "__main__":
    try:
        run_expense_sync()
    except KeyboardInterrupt:
        print("\n⛔ Đã dừng chương trình theo yêu cầu người dùng.")
        sys.exit(0)
    except Exception as err:
        print(f"\n❌ Phát sinh lỗi: {err}", file=sys.stderr)
        sys.exit(1)

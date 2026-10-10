---
name: raw-converter-orchestrator
description: "Tự động điều phối các subagents chuyên biệt trong .agents/agents/ để quét và chuyển đổi toàn bộ tài liệu thô (.docx, .pdf, .xlsx, .txt) trong knowledge-base/raw/ thành Markdown chuẩn hóa lưu tại knowledge-base/processed/."
user-invocable: true
argument-hint: "[--dry-run] [--file <path>]"
category: workflow
keywords: [orchestrator, subagents, knowledge-base, raw-to-markdown, docx, pdf, excel, text]
---

# Raw to Markdown Agent Orchestrator

Kỹ năng điều phối đa tác tử (**Multi-Agent Orchestration**) chịu trách nhiệm quản lý, phân loại và nạp các tệp tài liệu thô từ `knowledge-base/raw/` tới các Agent chuyên biệt trong thư mục `.agents/agents/`.

---

## 1. Agent Chuyên Biệt Hợp Nhất (.agents/agents/)

Hệ thống sử dụng duy nhất một Agent toàn diện đa định dạng:
- **Tên Agent:** [agent-convert-raw-to-markdown.md](file:///Users/mac/Documents/Haiyentn2295/Agentic%20AI/my-workspace/.agents/agents/agent-convert-raw-to-markdown.md)
- **Vai trò:** Universal Raw Document to Markdown Ingestion Specialist
- **Định dạng hỗ trợ:** `.docx`, `.pdf`, `.xlsx`, `.xls`, `.csv`, `.txt`, `.log`
- **Cơ chế:** Tự động phát hiện extension của tệp tin đầu vào để kích hoạt engine xử lý tương ứng (MarkItDown, Mammoth, Pandas, Text Parser).

---

## 2. Quy Trình Điều Phối Chuẩn (Execution Protocol)

Khi người dùng gọi lệnh `/raw-converter` hoặc yêu cầu xử lý tài liệu trong `knowledge-base/raw/`:

### Bước 1: Quét tệp tin (Scanning)
- Kiểm tra danh sách các file trong `knowledge-base/raw/` (loại trừ thư mục `archive/`).

### Bước 2: Nạp Agent Hợp Nhất & Thực thi (Dispatching)
- Main Agent nạp bản hợp đồng từ `.agents/agents/agent-convert-raw-to-markdown.md` và thực thi:
  ```bash
  .venv/bin/python scripts/orchestrate_converters.py
  ```
- Hoặc khởi tạo Subagent độc lập thông qua `agy CLI`:
  ```bash
  agy --dangerously-skip-permissions -p "Đọc hướng dẫn trong .agents/agents/agent-convert-raw-to-markdown.md và chuyển đổi các file trong knowledge-base/raw/"
  ```

### Bước 3: Lưu trữ & Hoàn tất (Archival & Synthesis)
- Toàn bộ kết quả Markdown và ảnh được ghi nhận tại `knowledge-base/processed/<tên_tệp>/`.
- Tệp gốc tự động được chuyển vào `knowledge-base/raw/archive/` để tránh xử lý trùng lặp.
- Báo cáo tổng kết số lượng tệp tin đã xử lý cho người dùng.

---

## 3. Cú Pháp Sử Dụng
- **Xử lý toàn bộ tệp mới:** `/raw-converter`
- **Chế độ kiểm tra trước (Dry-run):** `/raw-converter --dry-run`
- **Chỉ định 1 tệp cụ thể:** `/raw-converter --file knowledge-base/raw/tailieu.docx`

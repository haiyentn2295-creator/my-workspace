# Subagent Task: Chuyển Đổi Toàn Diện Tài Liệu Thô Sang Markdown

Bạn đang đóng vai trò là **Universal Raw Document to Markdown Ingestion Specialist** theo hợp đồng nghiệp vụ tại file:
`file:///Users/mac/Documents/Haiyentn2295/Agentic AI/my-workspace/.agents/agents/agent-convert-raw-to-markdown.md`

## Nhiệm Vụ:
1. Đọc và tuân thủ tuyệt đối quy tắc nghiệp vụ trong:
   `.agents/agents/agent-convert-raw-to-markdown.md`
2. Kiểm tra các tệp tin hiện có trong `knowledge-base/raw/` (bỏ qua `knowledge-base/raw/archive/`).
3. Thực thi chuyển đổi toàn bộ tài liệu (.docx, .pdf, .xlsx, .csv, .txt, .log) sang Markdown tại `knowledge-base/processed/<tên_tệp>/` bằng cách kích hoạt pipeline:
   ```bash
   .venv/bin/python scripts/orchestrate_converters.py
   ```
4. Đảm bảo toàn bộ tệp gốc sau khi chuyển đổi thành công được lưu trữ vào `knowledge-base/raw/archive/`.
5. Báo cáo kết quả cuối cùng theo cấu trúc JSON Return Contract đã được quy định trong `agent-convert-raw-to-markdown.md`.

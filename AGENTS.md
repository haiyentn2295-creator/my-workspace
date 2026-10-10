# My Workspace — Quy Tắc Vận Hành

## Dự Án
**Personal Agentic Workspace** — Không gian làm việc AI cá nhân được xây dựng xuyên suốt khóa học Agentic AI with Google Antigravity.

## Chủ Sở Hữu
- **Tên:** {{ten_hoc_vien}}
- **Lĩnh vực:** {{linh_vuc_chuyen_mon}} _(VD: Marketing, Kế Toán, Nhân Sự, Kinh Doanh...)_
- **Mục tiêu tự động hóa:** {{muc_tieu_chinh}} _(VD: Tự động hóa báo cáo tuần, lên lịch nội dung, phân tích dữ liệu khách hàng...)_

## Sứ Mệnh Workspace
{{mo_ta_workspace}} _(VD: Workspace hỗ trợ tôi tự động hóa các công việc lặp lại trong [lĩnh vực], tạo ra các output chuyên nghiệp và có hệ thống.)_

## Quy Tắc Vận Hành (Rules)

### Quy tắc 1 — Tích lũy, không phá vỡ
Mỗi buổi học, tôi CHỈ thêm mới vào workspace. Không xóa bỏ hoặc thay thế các thành phần đã tạo trừ khi có lý do audit rõ ràng.

### Quy tắc 2 — PDCA bắt buộc
Mọi thay đổi quan trọng phải được ghi vào `docs/pdca-log.md`. Format: Plan → Do → Check → Act.

### Quy tắc 3 — Workspace checkpoint
Sau mỗi buổi học, tôi đọc bridge guide tương ứng và hoàn thành ít nhất 1 workspace checkpoint.

### Quy tắc 4 — Output vào đúng thư mục
- Draft content → `outputs/drafts/`
- Báo cáo → `outputs/reports/`
- Dữ liệu thực hành → `sample-data/`

### Quy tắc 5 — Bảo mật
Không đưa API key, mật khẩu, dữ liệu khách hàng thật vào workspace này.

## Lịch Sử Phát Triển

| Buổi | Ngày | Thêm gì vào workspace | Ghi chú |
|:----:|------|----------------------|---------|
| 1 | {{ngay}} | Tạo workspace, viết AGENTS.md | |
| 2 | 06/09/2026 | BA Sales Performance Dashboard (.xlsx), data cleaning & KPI analysis | Thực hành làm sạch dữ liệu, dashboard & PDCA log #01 |
| 3 | 06/09/2026 | cafe_quan1_data.xlsx, Market Research Summary & PDCA log #02 | Khảo sát 20 quán cafe Quận 1, đóng gói Excel & phân tích F&B |
| 4 | 06/09/2026 | top_10_khoa_hoc_ai.xlsx, EdTech Research Report & PDCA log #03 | Nghiên cứu Top 10 khóa học AI tại Việt Nam qua Grill-me session |
| 5 | 09/09/2026 | monthly_erp_processor.py, Report_Manager_*.xlsx, Company_Overview_2026-03.xlsx, Executive Report & PDCA #04 | Tự động hóa pipeline ERP hàng tháng cho Operations Analyst |
| 6 | 12/09/2026 | Skill `academic-training-reporter`, `academic_training_processor.py`, Master & Lecturer Reports, Executive MD & PDCA #05 | Tự động hóa báo cáo học vụ & phân tích hiệu suất giảng viên 360 độ cho Academic Executive |
| 7 | 13/09/2026 | OpenSlide Framework (`slides/`), 5 Agent Skills (`create-slide`, `slide-authoring`,...), dev/build pipeline | Khởi tạo workspace trình chiếu React 1920x1080 cho AI Agent & PDCA #06 |
| 8 | 13/09/2026 | `send_telegram.py`, `.env`, OIPO Telegram Bot AI News Pipeline (Professional Edition với Gemini 2.5 Flash) | Nâng cấp bot lấy 3 tin AI RSS, Gemini AI Editor dịch giữ nguyên tech terms, phân tích AI Trends/Insights, trích xuất Tech Vocabulary & gửi Telegram |
| 10 | 20/09/2026 | Skill `ai4a:build-dashboard-BI`, templates (tokens, count_up engine, demo HTML) | Thiết lập bộ tiêu chuẩn thiết kế BI Dashboard: Glassmorphism, Dark Mode, KPI layout, phối màu tương phản & hiệu ứng nhảy số |
| 11 | 20/09/2026 | `dashboard_beta.html`, `server_beta.py`, `export_beta_dashboard.py`, `Beta_Solutions_Dashboard_Protected.zip` | Xây dựng Dashboard Quản lý Ngân sách Beta Solutions (Dark Mode Glassmorphism, 2s Realtime, Xuất HTML tĩnh & nén ZIP password beta2026) |
| 12 | 20/09/2026 | Skill `convert-word-to-md` (`.agents/skills/convert-word-to-md/`) | Cài đặt skill chuyển đổi Word (.docx) sang Markdown với MarkItDown & trích xuất ảnh gốc |
| 13 | 20/09/2026 | Unified Ingestion Agent (`.agents/agents/agent-convert-raw-to-markdown.md`, `scripts/orchestrate_converters.py`, skill `raw-converter-orchestrator`) | Kiến trúc Orchestration nạp 1 Agent hợp nhất duy nhất chuyển đổi mọi tài liệu thô (.docx, .pdf, .xlsx, .txt) sang Markdown |
| 14 | 20/09/2026 | Subagent Runner & Registry (`scripts/run_subagent_convert.py`, `.agents/workflows/subagent_convert_prompt.md`, `logs/active/README.md`) | Thiết lập cơ chế Subagent độc lập, logging và prompt workflow cho agent-convert-raw-to-markdown |
| 15 | 11/10/2026 | Skill `lead-scoring` (`.agents/skills/lead-scoring/`), `app_lead_scoring.py` (Streamlit App với `st.data_editor`), `scripts/score_leads.py`, `BDS_Lead_Scoring_Report.xlsx`, `BDS_Lead_Scoring_Executive_Summary.md` & PDCA #17 | Bộ kỹ năng & ứng dụng Streamlit chấm điểm khách hàng tiềm năng Bất Động Sản (5 tiêu chí, cờ VIP +50đ / cờ Red Flag -50đ, phân loại HOT/WARM/COLD/JUNK, duyệt trạng thái Human-in-the-loop & handover Sales) |


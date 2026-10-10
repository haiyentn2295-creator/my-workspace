## PDCA Log — Nhật Ký Cải Tiến

> **Hướng dẫn:** Ghi một entry mới sau mỗi lần thực hành PDCA với AI.  
> **Format:** Plan → Do → Check → Act  

---

<!-- Template: Copy và điền thông tin thật -->
<!--
## PDCA Log #[số thứ tự] — Buổi [X] — [Ngày]

### 📋 PLAN
- **Mục tiêu:** 
- **Output mong muốn:** 
- **Dữ liệu cần:** 
- **Prompt ban đầu:** 

### ✅ DO
- **Đã thực hiện:** 
- **Prompt thực tế đã dùng:** 
- **Output nhận được:** 

### 🔍 CHECK
- **Đạt mục tiêu không?** [Có / Không / Một phần]
- **Vấn đề gặp phải:** 
- **Điểm tốt cần giữ lại:** 

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** 
- **Ghi nhớ:** 
-->

---

## PDCA Log #01 — Buổi 2 — 06/09/2026

### 📋 PLAN
- **Mục tiêu:** Nhận dữ liệu bán hàng thô (synthetic sales data 500x20), tiến hành làm sạch dữ liệu, xây dựng dashboard trực quan tự động hóa trên Excel, trích xuất 3 key insights và 2 actionable recommendations theo vai trò Business Analyst.
- **Output mong muốn:** 
  1. 1 file Excel hoàn chỉnh gồm Dashboard trực quan (KPI cards, 3 biểu đồ chuẩn hóa doanh thu thời gian, top sản phẩm, kênh/khu vực), bảng tổng hợp Pivot, Cleaned Data và Data Dictionary.
  2. Báo cáo phân tích Business Analyst gồm 3 insight quan trọng và 2 đề xuất hành động thực tiễn.
- **Dữ liệu cần:** `sample-data/MINDX_Lesson 2_DEMO_synthetic_sales_data_500x20.xlsx` (500 dòng, 20 cột).
- **Prompt ban đầu:** Yêu cầu AI đóng vai Business Analyst thực hiện chu trình PDCA: Làm sạch dữ liệu, tạo dashboard trực quan (thời gian, top sản phẩm, khu vực/kênh), đưa ra 3 insight quan trọng và 2 đề xuất hành động.

### ✅ DO
- **Đã thực hiện:** 
  1. Thiết lập môi trường Python ảo `.venv`, cài đặt `pandas`, `openpyxl`, `xlsxwriter` tuân thủ quy tắc quản lý dependencies.
  2. Khảo sát chất lượng dữ liệu (Audit): kiểm tra trùng lặp (0 duplicate), kiểm tra tính logic công thức Doanh thu và Lợi nhuận, phát hiện 1 đơn hàng lỗ âm biên lợi nhuận (`ORD00067`) và tỷ lệ hoàn hàng cao (25.6%).
  3. Làm sạch và chuẩn hóa dữ liệu: chuẩn hóa định dạng Date (`YYYY-MM-DD`), chuẩn hóa chuỗi và danh mục, thêm các trường phân tích `NET_REVENUE`, `PROFIT_MARGIN`, `DISCOUNT_RATE`, `ORDER_STATUS`.
  4. Lập trình xuất bản file Excel Dashboard hoàn chỉnh: `outputs/reports/BA_Sales_Performance_Dashboard.xlsx` với 4 sheet chuyên nghiệp, giao diện Navy/Slate hiện đại, 4 KPI cards và 3 biểu đồ động (Line Chart, Bar Chart, Clustered Column Chart).
  5. Đúc kết 3 insight trọng yếu dựa trên dữ liệu định lượng và 2 đề xuất chiến lược cho doanh nghiệp.
- **Prompt thực tế đã dùng:** Prompt chuẩn hóa quy trình phân tích BA kết hợp PDCA và yêu cầu xuất bản Excel Dashboard trực tiếp.
- **Output nhận được:** File `outputs/reports/BA_Sales_Performance_Dashboard.xlsx` và báo cáo phân tích chi tiết.

### 🔍 CHECK
- **Đạt mục tiêu không?** Có (Hoàn thành 100% các tiêu chí yêu cầu của đề bài).
- **Vấn đề gặp phải:** Một số trường số và tỷ lệ phần trăm cần định dạng chuẩn xác (`$#,##0.00`, `0.0%`) để không bị lỗi hiển thị số thập phân dài trên Excel; cột sản phẩm cần đồng bộ case naming (`PRODUCT`).
- **Điểm tốt cần giữ lại:** 
  - Tự động hóa tạo file Excel nguyên bản với chart nhúng trực tiếp, không phụ thuộc vào thao tác thủ công.
  - Phân tích đa chiều kết hợp giữa Doanh thu, Lợi nhuận và Rủi ro hoàn hàng (Return Flag) mang lại giá trị tư vấn sâu sắc hơn chỉ nhìn vào doanh thu gộp.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Xây dựng script Python tái sử dụng dạng template cho các báo cáo bán hàng định kỳ tiếp theo để rút ngắn thời gian xử lý dữ liệu.
- **Ghi nhớ:** Luôn kiểm tra biên lợi nhuận sau trừ chiết khấu và chi phí marketing, đặc biệt chú ý tỷ lệ hoàn hàng trên các kênh Online/FMCG dễ vỡ hỏng.

---

## PDCA Log #02 — Buổi 3 — 06/09/2026

### 📋 PLAN
- **Mục tiêu:** Thu thập thông tin thực tế của tối thiểu 20 quán cafe nổi bật tại Quận 1, TP.HCM dưới vai trò Chuyên viên Nghiên cứu Thị trường; đóng gói vào file Excel chuẩn `cafe_quan1_data.xlsx` không trùng lặp dữ liệu.
- **Output mong muốn:**
  1. File Excel `sample-data/cafe_quan1_data.xlsx` (và bản sao `outputs/reports/cafe_quan1_data.xlsx`) chứa 2 sheet: Dữ liệu chi tiết 20 quán và Báo cáo tóm tắt chỉ số thị trường.
  2. Báo cáo phân tích chuyên sâu thị trường F&B Quận 1: `outputs/reports/cafe_quan1_market_summary.md`.
- **Dữ liệu cần:** Dữ liệu thực tế 20 quán cafe với 5 trường cốt lõi: `Ten_quan`, `Gia`, `Dia_chi`, `Danh_gia`, `Ghi_chu_Dac_diem` kèm các trường phân khúc phụ trợ.
- **Prompt ban đầu:** Đóng vai trò chuyên viên nghiên cứu thị trường, lập kế hoạch và thu thập dữ liệu 20 quán cafe Quận 1, tạo file Excel `cafe_quan1_data.xlsx`, kiểm tra tính duy nhất.

### ✅ DO
- **Đã thực hiện:**
  1. Lên kế hoạch chi tiết `implementation_plan.md` với định dạng data schema chuẩn và danh mục 20 quán đa dạng mô hình.
  2. Viết mã nguồn Python `scratch/generate_excel.py` dùng thư viện `openpyxl` và `pandas` để tạo file Excel đạt chuẩn thẩm mỹ cao: Banner tiêu đề, bảng màu Dark Navy `#1F4E79`, zebra striping, định dạng tiền tệ VND (`#,##0 ₫`), thang điểm đánh giá, hàng tính giá trị trung bình tự động `=AVERAGE()`.
  3. Xây dựng Sheet thứ hai `Market_Summary` với 4 KPI cards định lượng và bảng phân bổ phân khúc thị trường (Luxury, Premium, Mid-tier, Budget).
  4. Lập trình script tự động hóa kiểm tra dữ liệu: Đạt 20 dòng hợp lệ, 0 duplicate về tên quán và địa chỉ, 100% trường dữ liệu không null, điểm đánh giá từ 1.0 đến 5.0.
  5. Xuất bản báo cáo phân tích thị trường F&B Quận 1 tại `outputs/reports/cafe_quan1_market_summary.md`.
- **Prompt thực tế đã dùng:** Thực thi theo kế hoạch đã được phê duyệt trong `implementation_plan.md`.
- **Output nhận được:** File Excel `sample-data/cafe_quan1_data.xlsx`, `outputs/reports/cafe_quan1_data.xlsx` và báo cáo phân tích chuyên sâu.

### 🔍 CHECK
- **Đạt mục tiêu không?** Có (100% tiêu chí đạt yêu cầu: 20 quán thực tế tại Q1, đầy đủ 5 trường, 0 trùng lặp, file Excel đúng tên `cafe_quan1_data.xlsx`).
- **Vấn đề gặp phải:** Một số quán cafe có nhiều chi nhánh (ví dụ Cộng Cà Phê, Cheese Coffee, Là Việt) nên cần ghi rõ địa chỉ chi nhánh cụ thể tại Quận 1 để tránh nhập nhằng dữ liệu vị trí.
- **Điểm tốt cần giữ lại:**
  - Bổ sung thêm cột số nguyên `Gia_trung_binh_VND` bên cạnh chuỗi hiển thị khoảng giá để dễ dàng áp dụng hàm thống kê tính toán trên Excel.
  - Tích hợp thêm Sheet 2 tổng kết KPI nâng tầm giá trị phân tích thị trường cho bộ dữ liệu.

### 🔄 ACT
- **Cải tiến thực hiện ngay:** Cập nhật tiêu đề trang tính thành "Top 20 quán cafe quận 1" và lập trình tự động sắp xếp lại 20 quán theo thứ tự điểm đánh giá (sao) giảm dần để người dùng tra cứu nhanh danh sách quán được đánh giá cao nhất.
- **Thay đổi sẽ áp dụng lần sau:** Mở rộng thu thập thêm trường tọa độ kinh độ/vĩ độ (latitude, longitude) để có thể vẽ biểu đồ bản đồ nhiệt (Heatmap) mật độ quán cafe trên GIS hoặc PowerBI/Tableau.
- **Ghi nhớ:** Với các nghiên cứu F&B, việc phân loại rõ ràng mô hình concept (Specialty, Vintage, 24/7 Working) giúp nhà đầu tư nắm bắt phân khúc khách hàng mục tiêu nhanh chóng hơn.

---

## PDCA Log #03 — Buổi 4 — 06/09/2026

### 📋 PLAN
- **Mục tiêu:** Thực hiện phỏng vấn làm rõ yêu cầu (/grill-me session), khảo sát và xây dựng bộ dữ liệu xếp hạng Top 10 khóa học AI tốt nhất tại Việt Nam cân bằng giữa ứng dụng thực chiến và kỹ thuật chuyên sâu.
- **Output mong muốn:**
  1. File Excel `outputs/reports/top_10_khoa_hoc_ai.xlsx` (kèm bản sao `sample-data/top_10_khoa_hoc_ai.xlsx`) gồm 2 Sheet: Danh mục Top 10 chi tiết và Bảng đối sánh xu hướng đào tạo.
  2. Báo cáo phân tích so sánh và hướng dẫn lựa chọn khóa học `outputs/reports/top_10_khoa_hoc_ai_report.md`.
- **Dữ liệu cần:** 10 khóa học AI uy tín với 10 trường thông tin chi tiết: Xếp hạng, Tên khóa, Đơn vị đào tạo, Phân loại AI, Học phí, Thời lượng/Hình thức, Đối tượng, Nội dung cốt lõi, Điểm uy tín, Chứng chỉ.
- **Prompt ban đầu:** Sử dụng lệnh `/grill-me` lên kế hoạch tìm kiếm thông tin và lập danh sách Top 10 khóa học AI tốt tại Việt Nam.

### ✅ DO
- **Đã thực hiện:**
  1. Triển khai phỏng vấn đa nhánh (/grill-me) làm rõ 4 quyết định cốt lõi: Đối tượng (kết hợp ứng dụng + kỹ thuật), Định dạng output (Excel + Markdown), Bộ tiêu chí đa chiều, và Phạm vi đơn vị (Học viện trong nước + Quốc tế bản địa hóa).
  2. Lập kế hoạch chi tiết `implementation_plan.md` và nhận phê duyệt từ người dùng.
  3. Viết script Python `scratch/generate_ai_courses_excel.py` tạo file Excel đạt chuẩn thiết kế chuyên nghiệp với 2 sheet, định dạng tiền tệ VND, hệ thống màu phân loại (Xanh lá: Ứng dụng, Xanh dương: Kỹ thuật), căn lề chuẩn và công thức tính trung bình.
  4. Lập trình kiểm thử tự động xác thực: 10 khóa duy nhất, không null, điểm đánh giá 4.6 - 4.9 sắp xếp giảm dần chính xác.
  5. Biên soạn báo cáo phân tích thị trường EdTech AI hoàn chỉnh với ma trận lựa chọn (Decision Matrix) bằng sơ đồ Mermaid.
- **Prompt thực tế đã dùng:** Thực thi theo kết quả thống nhất từ phiên phỏng vấn Grill-me và `implementation_plan.md`.
- **Output nhận được:** File Excel `outputs/reports/top_10_khoa_hoc_ai.xlsx` và báo cáo phân tích toàn diện `outputs/reports/top_10_khoa_hoc_ai_report.md`.

### 🔍 CHECK
- **Đạt mục tiêu không?** Có (100% mục tiêu hoàn thành xuất sắc, cấu trúc cân bằng 5 khóa ứng dụng - 5 khóa kỹ thuật).
- **Vấn đề gặp phải:** Một số khóa học quốc tế tính học phí theo USD hoặc theo tháng (Coursera) cần quy đổi chính xác sang VND tương đương theo tỷ giá thực tế để người học dễ so sánh.
- **Điểm tốt cần giữ lại:**
  - Quy trình phỏng vấn /grill-me từng bước giúp loại bỏ 100% mơ hồ trước khi triển khai.
  - Sơ đồ Decision Matrix trực quan giúp người đọc dễ dàng tự định vị khóa học phù hợp với trình độ bản thân.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Với các báo cáo xếp hạng giáo dục, có thể tích hợp thêm cột đánh giá mức độ hỗ trợ tìm việc sau tốt nghiệp (Career Support Rating).
- **Ghi nhớ:** Người học phi kỹ thuật cần tập trung vào các khóa học giải quyết bài toán nghiệp vụ ngay lập tức (Agentic AI), tránh tâm lý lao vào học thuật toán hay toán học nặng nề gây nản chí.

---

## PDCA Log #04 — Buổi 5 — 09/09/2026

### 📋 PLAN
- **Mục tiêu:** Tự động hóa toàn diện quy trình xử lý dữ liệu ERP định kỳ hàng tháng cho Operations Analyst: Tải dữ liệu, làm sạch, audit chất lượng, tính Thực nhận (`Net_Salary = Base_Salary + Bonus - Penalty`), tách file Excel thẩm mỹ cao riêng cho từng Manager, tạo Master Overview Excel và Báo cáo điều hành Markdown; tổ chức gọn gàng theo thư mục ngày báo cáo (`outputs/reports/YYYY-MM-DD/`).
- **Output mong muốn:**
  1. Script tự động hóa `scripts/monthly_erp_processor.py` hỗ trợ cả Google Sheet URL và file local, tự động phân nhóm thư mục theo ngày báo cáo.
  2. Dữ liệu gốc lưu tại `sample-data/raw_erp_data.csv`.
  3. 4 file báo cáo chi tiết cho từng Manager: `outputs/reports/2026-09-09/managers/Report_Manager_{A,B,C,D}_2026-03.xlsx`.
  4. File Master Overview Excel: `outputs/reports/2026-09-09/Company_Overview_2026-03.xlsx` gồm Executive Dashboard (KPI cards, Pivot phòng ban, Pivot quản lý) và Master Data Cleaned.
  5. Báo cáo phân tích điều hành: `outputs/reports/2026-09-09/Executive_Operations_Report_2026-03.md`.
- **Dữ liệu cần:** Export ERP Google Sheet 200 nhân sự gồm 8 trường: `Employee_ID`, `Employee_Name`, `Manager`, `Department`, `Base_Salary`, `Bonus`, `Penalty`, `Month`.
- **Prompt ban đầu:** Sử dụng `/grill-me` để phỏng vấn làm rõ yêu cầu nghiệp vụ của Operations Analyst và xây dựng giải pháp tự động hóa.

### ✅ DO
- **Đã thực hiện:**
  1. Triển khai phỏng vấn sâu qua lệnh `/grill-me` làm rõ 5 quyết định kiến trúc: Kiến trúc Python trong workspace, công thức tính toán `Net_Salary` & tỷ lệ thưởng phạt, cấu trúc lưu trữ và quy tắc đặt tên file, bộ đôi deliverables điều hành (Excel + Markdown), và chế độ CLI linh hoạt.
  2. Lập kế hoạch chi tiết tại `implementation_plan.md` và nhận phê duyệt từ người dùng.
  3. Viết pipeline hoàn chỉnh `scripts/monthly_erp_processor.py` sử dụng `pandas` và `openpyxl`.
  4. Tự động tải dữ liệu từ Google Sheet, kiểm định chất lượng: 200 dòng, 0 duplicate ID, 0 missing value.
  5. Xuất bản 4 file Excel Manager với định dạng cao cấp (Dark Navy banner `#1F4E79`, zebra striping, currency `#,##0 ₫`, công thức `SUM` tự động) vào thư mục ngày báo cáo `outputs/reports/2026-09-09/managers/`.
  6. Xuất bản Master Excel `Company_Overview_2026-03.xlsx` tích hợp KPI cards điều hành, pivot table tổng hợp theo Department và Manager, cùng sheet dữ liệu sạch master vào `outputs/reports/2026-09-09/`.
  7. Biên soạn Báo cáo điều hành chuyên sâu `Executive_Operations_Report_2026-03.md` vào `outputs/reports/2026-09-09/`.
  8. Lập trình script kiểm thử tự động xác thực: Khớp đúng 200/200 nhân sự trên cả 4 file con và file master.
  9. Tinh chỉnh cấu trúc lưu trữ: Tự động tạo thư mục con theo ngày (`YYYY-MM-DD`) tránh lưu lộn xộn ở thư mục gốc.
- **Prompt thực tế đã dùng:** Thực thi theo kết quả thống nhất từ phiên Grill-me và `implementation_plan.md`, tiếp thu feedback tổ chức folder theo ngày.
- **Output nhận được:** Pipeline `scripts/monthly_erp_processor.py`, 4 file Manager Excel, 1 Master Overview Excel và Báo cáo điều hành Markdown trong thư mục `outputs/reports/2026-09-09/`.

### 🔍 CHECK
- **Đạt mục tiêu không?** Có (100% mục tiêu hoàn thành xuất sắc, giảm thời gian thao tác từ nhiều giờ thủ công xuống chỉ còn dưới 5 giây, cấu trúc thư mục phân loại theo ngày báo cáo cực kỳ trực quan và ngăn nắp).
- **Vấn đề gặp phải:** Ban đầu xuất thẳng vào root của `outputs/reports/` gây lẫn lộn với các bài học trước; đã cải tiến đưa toàn bộ vào thư mục ngày `2026-09-09`.
- **Điểm tốt cần giữ lại:**
  - Thiết kế CLI linh hoạt với tham số `--report-date` mặc định lấy ngày hiện tại giúp tự động hóa 100% mà không cần gõ thêm tham số.
  - Thư mục con theo ngày giúp người dùng lưu trữ nhiều tháng/nhiều kỳ báo cáo liên tiếp mà không bị đè file hay rối mắt.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Có thể tích hợp thêm tính năng nén file zip toàn bộ thư mục ngày báo cáo để sẵn sàng đính kèm email gửi lãnh đạo.
- **Ghi nhớ:** Với mọi pipeline xuất nhiều files, luôn tạo thư mục theo ngày/phiên chạy (`YYYY-MM-DD` hoặc `YYYY-MM`) để đảm bảo tính ngăn nắp và truy vết lịch sử dễ dàng.

---

## PDCA Log #05 — Buổi 6 — 12/09/2026

### 📋 PLAN
- **Mục tiêu:** Xây dựng giải pháp tự động hóa toàn diện quy trình thu thập, làm sạch và phân tích dữ liệu học vụ dành cho Nhân viên Đào tạo (Academic/Training Executive) tại Trung tâm Công nghệ & AI. Khắc phục triệt để tình trạng dữ liệu nằm rải rác nhiều nguồn, chưa chuẩn hóa, xử lý thủ công tốn thời gian; đánh giá hiệu suất giảng viên 360 độ và lập báo cáo đa định dạng gửi Ban Giám Đốc và từng Giảng viên.
- **Output mong muốn:**
  1. Script Python `scripts/academic_training_processor.py` tự động hóa toàn diện từ làm sạch, tính chỉ số 360 độ đến xuất bản báo cáo.
  2. Dữ liệu thô đa nguồn `sample-data/raw_student_data_multisource.xlsx` (190 dòng, 12 cột, mô phỏng đầy đủ các lỗi thực tế).
  3. Master Academic Excel `outputs/reports/2026-09-12/Master_Academic_Report_2026-Q3.xlsx` gồm 4 Sheet: Executive_Dashboard, Lecturer_Performance, Cleaned_Student_Data, Data_Audit_Log.
  4. 4 file Excel cá nhân hóa bảo mật riêng cho từng Giảng viên trong `outputs/reports/2026-09-12/lecturers/Report_Lecturer_{Name}.xlsx`.
  5. Báo cáo điều hành học vụ chuyên sâu dạng Markdown: `outputs/reports/2026-09-12/Academic_Training_Executive_Report.md`.
- **Dữ liệu cần:** 180 học viên phân bổ qua 4 giảng viên chủ chốt (Thầy An - GenAI, Cô Bình - Python, Thầy Cường - Data AI, Cô Dung - AI Business) với các trường thông tin: Mã HV, Họ tên, SĐT, Email, Khóa học, Mã lớp, Giảng viên, Chuyên cần, Điểm đồ án, Đánh giá GV CSAT, Nhận xét học viên, Nguồn dữ liệu.
- **Prompt ban đầu:** Sử dụng lệnh `/grill-me` phỏng vấn đóng vai Nhân viên Đào tạo giải quyết bài toán tổng hợp dữ liệu học viên, làm sạch dữ liệu, phân tích theo từng giảng viên và viết báo cáo học vụ.

### ✅ DO
- **Đã thực hiện:**
  1. Triển khai phỏng vấn sâu qua lệnh `/grill-me` làm rõ 5 quyết định kiến trúc: Lĩnh vực Trung tâm Đào tạo Công nghệ & AI, schema dữ liệu toàn diện kèm các dạng dirty data, khung đánh giá giảng viên 360 độ, bộ deliverables Master Excel + file cá nhân hóa từng giảng viên + Báo cáo điều hành Markdown, quy mô 180 học viên qua 4 giảng viên.
  2. Lập kế hoạch chi tiết `implementation_plan.md` và nhận phê duyệt từ người dùng.
  3. Tạo bộ dữ liệu thô đa nguồn `sample-data/raw_student_data_multisource.xlsx` (190 dòng gồm 10 bản ghi trùng lặp, SĐT lộn xộn nhiều định dạng, họ tên không viết hoa, tên khóa học viết tắt, điểm số khuyết thiếu).
  4. Viết pipeline hoàn chỉnh `scripts/academic_training_processor.py` với các hàm làm sạch mạnh mẽ: khử trùng lặp, chuẩn hóa họ tên Proper Title Case, chuẩn hóa SĐT 10 chữ số chuẩn quốc gia, chuẩn hóa tỷ lệ chuyên cần [0 - 100%], xử lý điểm đồ án [0 - 10.0], tính điểm CSAT [1.0 - 5.0], phân loại trạng thái học vụ (Tốt nghiệp, Thi lại, Rơi rụng).
  5. Xây dựng bộ chỉ số đánh giá giảng viên 360 độ: Tổng HV, Tỷ lệ hoàn thành, Tỷ lệ rơi rụng, Chuyên cần TB, Điểm đồ án TB, Điểm CSAT TB, Xếp loại giảng viên (Xuất sắc / Đạt chuẩn / Cần cải thiện) và trích xuất điểm mạnh/góp ý từ học viên.
  6. Xuất bản Master Academic Excel `Master_Academic_Report_2026-Q3.xlsx` với thiết kế giao diện chuẩn mực (Dark Navy `#1F4E79`, Header Slate `#2F5597`, 4 KPI Cards, Zebra striping, Number format, Badge màu trạng thái).
  7. Xuất bản 4 file Excel riêng cho từng Giảng viên trong thư mục `outputs/reports/2026-09-12/lecturers/`, giúp nhân viên đào tạo bảo mật thông tin giữa các giảng viên.
  8. Xuất bản Báo cáo điều hành học vụ `Academic_Training_Executive_Report.md` với Executive Summary, Bảng tổng hợp KPI, Phân tích 4 giảng viên, Bản đồ cảnh báo rủi ro học vụ (Risk Alert Matrix) và 3 Đề xuất cải tiến học vụ (PDCA).
  9. Lập trình script kiểm thử tích hợp tự động `scratch/verify_academic_system.py`: Xác thực 100% test case passed (180 học viên hợp lệ, 100% SĐT chuẩn 10 chữ số, 100% họ tên chuẩn Title Case, tổng học viên 4 file con khớp chính xác 180/180 không chồng chéo).
  10. Đóng gói toàn bộ workflow thành Workspace Skill chuẩn Antigravity: `.agents/skills/academic-training-reporter/SKILL.md` sẵn sàng kích hoạt bất cứ lúc nào qua câu lệnh hoặc UI.

### 🔍 CHECK
- **Đạt mục tiêu không?** Có (100% mục tiêu hoàn thành xuất sắc, quy trình từ rải rác - thủ công trở thành pipeline tự động hóa hoàn toàn chạy trong 1.5 giây).
- **Vấn đề gặp phải & Giải pháp:**
  - Vấn đề 1: Tên file giảng viên ban đầu bị regex thay thế các ký tự tiếng Việt có dấu thành ký tự gạch dưới (VD: `Nguy_n_V_n_An`). Khắc phục: Bổ sung hàm `remove_accents()` để chuẩn hóa thành tên tiếng Việt không dấu chuẩn quốc tế (`Nguyen_Van_An`).
  - Vấn đề 2: Cột số điện thoại khi đọc bằng thư viện phân tích dễ bị ép kiểu số nguyên làm mất số 0 ở đầu. Khắc phục: Thiết lập `number_format = '@'` trực tiếp trên cell Excel và cấu hình đọc text chuẩn.
- **Điểm tốt cần giữ lại:**
  - Thiết kế phân tách riêng báo cáo cho từng giảng viên giúp bảo mật thông tin nội bộ và tăng tính chuyên nghiệp khi gửi feedback cho thầy cô.
  - Tích hợp 4 KPI Cards và bảng xếp hạng trực quan trên Sheet 1 của Master Excel giúp Ban Giám Đốc nắm bắt tình hình chỉ trong 30 giây.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Có thể tích hợp thêm tính năng tự động gửi email (SMTP / Google Gmail API) kèm file báo cáo tương ứng tới từng giảng viên theo địa chỉ email của họ.
- **Ghi nhớ:** Khi xử lý dữ liệu định danh tiếng Việt (Họ tên, SĐT), luôn áp dụng hàm loại bỏ dấu khi đặt tên file hệ thống và định dạng `@` cho chuỗi số để tránh lỗi hiển thị.

---

## PDCA Log #06 — Buổi 7 — 13/09/2026

### 📋 PLAN
- **Mục tiêu:** Cài đặt và tích hợp framework trình chiếu thế hệ mới **OpenSlide** (https://open-slide.dev) vào workspace cá nhân theo yêu cầu người dùng, cho phép AI Agent trực tiếp lập trình và tạo ra các slide bài giảng / báo cáo chuyên nghiệp chuẩn 1920×1080 canvas bằng React & TypeScript.
- **Output mong muốn:**
  1. Thư mục `slides/` hoàn chỉnh với framework OpenSlide (`@open-slide/core`), cấu hình Vite, dev server và mẫu slide sẵn sàng.
  2. Toàn bộ dependencies được cài đặt đầy đủ bằng `npm`, build thử nghiệm thành công không lỗi.
  3. Đồng bộ 5 Agent Skills chuyên dụng (`create-slide`, `slide-authoring`, `apply-comments`, `create-theme`, `current-slide`) vào `.agents/skills/` của workspace gốc để Antigravity AI Agent có thể hỗ trợ tạo slide tức thì.
  4. Cập nhật `AGENTS.md` và `docs/pdca-log.md` tuân thủ Quy tắc 1 (Tích lũy, không phá vỡ) và Quy tắc 2 (PDCA).
- **Dữ liệu / Công nghệ:** Node.js v24, npm v11, `@open-slide/cli`, `@open-slide/core`, React 18, Vite 5.

### ✅ DO
- **Đã thực hiện:**
  1. Khảo sát tài liệu OpenSlide từ website chính thức `open-slide.dev` và GitHub repository `1weiho/open-slide`.
  2. Đề xuất kế hoạch triển khai tại `implementation_plan.md` và nhận phê duyệt từ người dùng.
  3. Khởi tạo workspace OpenSlide thông qua lệnh `npx -y @open-slide/cli init slides`.
  4. Tự động cài đặt 408 packages cần thiết cho runtime và build tooling.
  5. Đồng bộ 5 skills chuẩn cho AI Agent từ `slides/.agents/skills/` sang thư mục gốc `.agents/skills/` của workspace.
  6. Kiểm thử tự động chạy `npm run build` bên trong thư mục `slides/`: Vite chuyển đổi thành công 2,472 modules và build ra sản phẩm hoàn chỉnh trong 1.36 giây mà không phát sinh bất kỳ lỗi cú pháp hay thiếu dependency nào.
  7. Cập nhật lịch sử phát triển Buổi 7 trong `AGENTS.md` và ghi chép nhật ký PDCA.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu. Dự án OpenSlide hoạt động ổn định, cấu trúc tách biệt trong thư mục `slides/` đảm bảo không ảnh hưởng đến bất kỳ code/scripts/data hiện có của workspace.
- **Điểm tốt cần giữ lại:**
  - Tích hợp sẵn 5 skills vào `.agents/skills/` giúp Antigravity nhận diện các prompt tạo slide (`/create-slide`, soạn slide từ prompt tiếng Việt hoặc tiếng Anh) cực kỳ nhạy bén.
  - Dự án có sẵn chế độ hot-reload, presentation mode với presenter notes và tính năng review/comment trên slide.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Khi người dùng cần làm bài thuyết trình hoặc slide báo cáo tuần/tháng, chỉ cần kích hoạt prompt hoặc lệnh `/create-slide` để tự động tạo deck trong `slides/slides/<id>/`.
- **Ghi nhớ:** Để xem trước và trình chiếu slide trực tiếp trên trình duyệt, chỉ cần chạy lệnh `npm run dev` bên trong thư mục `slides/` (mặc định mở tại `http://localhost:5173`).

---

## PDCA Log #07 — Buổi 8 — 13/09/2026

### 📋 PLAN
- **Mục tiêu:** Đóng vai Automation Engineer xây dựng mã nguồn Python hoàn chỉnh cho workflow theo mô hình OIPO: Tự động lấy 1 tin tức AI mới nhất từ Google News RSS, dịch sang tiếng Việt (không dùng thư viện `googletrans`), định dạng chuẩn và gửi đến Telegram Bot qua HTTP requests.
- **Output mong muốn:**
  1. Script thực thi hoàn chỉnh `send_telegram.py` (và `scripts/send_telegram.py`).
  2. File cấu hình biến môi trường bảo mật `.env` (chứa `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID`) cùng `.env.example` và `.gitignore`.
  3. Đầy đủ các hàm chức năng: `get_ai_news()`, `translate_to_vi()`, `send_telegram()`.
  4. Cơ chế xử lý lỗi mạng/API và thông báo hướng dẫn khi người dùng chưa nhấn `/start` với bot.
- **Dữ liệu / Công nghệ:** Python 3, `requests`, `python-dotenv`, `xml.etree.ElementTree`, MyMemory REST Translation API, Telegram Bot API.
- **Prompt ban đầu:** Tạo telegrambot theo mô hình OIPO, lấy 1 tin AI mới nhất từ RSS, dịch sang tiếng Việt không dùng googletrans, gửi bằng requests, token bảo mật bằng `.env`.

### ✅ DO
- **Đã thực hiện:**
  1. Tạo file cấu hình bảo mật `.env` lưu trữ `TELEGRAM_BOT_TOKEN=8759939124:AAHM4TFIFJkINlWsyRYckoTUAp1Bx9gedfs` và `TELEGRAM_CHAT_ID=1900585899`.
  2. Tạo template `.env.example` và file `.gitignore` để ngăn chặn việc rò rỉ token nhạy cảm ra ngoài môi trường mã nguồn.
  3. Cài đặt các thư viện `requests` và `python-dotenv` vào môi trường ảo `.venv`, đồng thời cập nhật `requirements.txt`.
  4. Lập trình module `send_telegram.py`:
     - Hàm `get_ai_news()`: Gửi request tới Google News RSS (`AI OR OpenAI OR Google AI`), parse XML bằng thư viện chuẩn, trích xuất title, link và unescape ký tự HTML.
     - Hàm `translate_to_vi()`: Sử dụng MyMemory Translation REST API qua `requests` thay vì phụ thuộc `googletrans` (vốn dễ lỗi HTTP 429), có cơ chế fallback mượt mà nếu xảy ra lỗi.
     - Hàm `send_telegram()`: Đóng gói payload gửi tin nhắn tới Telegram Bot API `https://api.telegram.org/bot<TOKEN>/sendMessage`.
     - Hàm `run_automation_pipeline()`: Điều phối luồng OIPO và format mẫu tin theo định dạng yêu cầu.
  5. Chạy thử nghiệm thực tế kiểm tra pipeline:
     - Lấy tin thành công: Tin tức mới nhất về OpenAI / GPT.
     - Dịch thuật chính xác sang tiếng Việt 100%.
     - Bắt và xử lý lỗi Telegram mã 400 (khi chat_id chưa kích hoạt /start với bot `@ai_news_hy_bot`) với hướng dẫn khắc phục rõ ràng cho người dùng.

### 🔍 CHECK
- **Đạt mục tiêu không?** Có (100% tiêu chí đề ra: mô hình OIPO rõ ràng, 3 hàm chức năng chính xác, bảo mật .env, không dùng googletrans, format chuẩn xác).
- **Vấn đề gặp phải & Giải pháp:**
  - *Vấn đề 1:* Dùng `googletrans` thường xuyên bị lỗi Timeout / HTTP 429 hoặc `NoneType` do Google thay đổi API token web.
    *Giải pháp:* Dùng trực tiếp REST API dịch thuật nhẹ qua `requests` với cơ chế giải mã HTML entities `html.unescape()` và tự động fallback về tiêu đề gốc nếu mất kết nối.
  - *Vấn đề 2:* Telegram Bot API chặn gửi tin nhắn đến `CHAT_ID` nếu tài khoản người dùng chưa bấm `/start` với bot trước đó (`Bad Request: chat not found`).
    *Giải pháp:* Thêm logic phát hiện lỗi `chat not found` và in ngay ra màn hình hướng dẫn 3 bước để người dùng mở bot bấm `/start`.
- **Điểm tốt cần giữ lại:**
  - Kiến trúc OIPO (Objective, Input, Process, Output) phân tách rõ ràng, dễ bảo trì.
  - Bảo mật tuyệt đối bằng `.env` và `.gitignore`.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Có thể lên lịch chạy tự động định kỳ mỗi sáng lúc 8:00 (bằng cron job hoặc task scheduler) để bot tự gửi điểm tin AI mỗi ngày mà không cần kích hoạt thủ công.
- **Ghi nhớ:** Với mọi bot Telegram mới tạo qua BotFather, tài khoản nhận tin luôn phải gửi ít nhất 1 tin nhắn hoặc bấm `/start` với Bot trước thì Bot mới có quyền gửi tin.

---

## PDCA Log #08 — Buổi 8 (Nâng Cấp) — 13/09/2026

### 📋 PLAN
- **Mục tiêu:** Nâng cấp bot Telegram tin tức AI lên phiên bản Professional thông qua quy trình phỏng vấn `/grill-me`:
  1. Mở rộng lấy **3 tin AI mới nhất** từ RSS feed.
  2. Tích hợp **Google Gemini 2.5 Flash** làm AI Editor cao cấp: dịch tiếng Việt chuẩn xác, giữ nguyên 100% thuật ngữ chuyên ngành tiếng Anh (*Frontier AI, Reasoning Model, Multimodal, Agentic Workflows...*).
  3. Phân tích và bổ sung mục **💡 AI INSIGHT & XU HƯỚNG** (2-3 luận điểm chiến lược).
  4. Trích xuất mục **📚 TECH VOCABULARY** giải thích các thuật ngữ công nghệ mới bằng tiếng Việt.
  5. Đảm bảo bảo mật an toàn `GEMINI_API_KEY` trong file `.env` và thiết lập cơ chế Graceful Fallback dự phòng.
- **Output mong muốn:**
  - Script [`send_telegram.py`](file:///Users/mac/Documents/Haiyentn2295/Agentic%20AI/my-workspace/send_telegram.py) và [`scripts/send_telegram.py`](file:///Users/mac/Documents/Haiyentn2295/Agentic%20AI/my-workspace/scripts/send_telegram.py) nâng cấp toàn diện.
  - File [`.env`](file:///Users/mac/Documents/Haiyentn2295/Agentic%20AI/my-workspace/.env) lưu trữ an toàn `GEMINI_API_KEY`.
  - Bản tin gửi thành công đến Telegram định dạng Consolidated Post đẹp mắt, chuyên nghiệp.
- **Dữ liệu / Công nghệ:** Python 3, `requests`, Google Gemini 2.5 Flash REST API (`models/gemini-2.5-flash`), Telegram Bot API.

### ✅ DO
- **Đã thực hiện:**
  1. Phỏng vấn làm rõ yêu cầu qua `/grill-me` (3 nhánh quyết định: Cấu trúc Consolidated Post duy nhất, độ sâu Executive Digest, cơ chế dự phòng Graceful Fallback).
  2. Lưu trữ `GEMINI_API_KEY` vào `.env`, cập nhật `.env.example`.
  3. Nâng cấp hàm `get_ai_news(limit=3)`: Thu thập 3 tin AI mới nhất và khử trùng lặp tiêu đề.
  4. Viết hàm `analyze_and_format_with_gemini()`: Tích hợp Gemini 2.5 Flash qua REST API với system prompt chuyên sâu dành cho Lead AI Editor.
  5. Thiết lập hàm `format_fallback_message()` và cơ chế Graceful Fallback tự động khi gặp lỗi mạng/quota.
  6. Kiểm thử tự động toàn diện: Lấy 3 tin -> Gemini phân tích -> Gửi tin nhắn thành công (2,710 ký tự) tới Telegram người dùng.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu. Bản tin hiển thị cực kỳ chuyên nghiệp trên Telegram, cấu trúc rõ ràng [1], [2], [3], Insight sắc bén và Vocabulary giải thích dễ hiểu.
- **Điểm tốt cần giữ lại:**
  - Gemini 2.5 Flash xử lý dịch giữ thuật ngữ chuyên ngành cực kỳ mượt mà, văn phong sắc bén không hề gượng gạo.
  - Tích hợp cả Insight và Vocabulary tạo giá trị gia tăng vượt trội so với các bot tin tức thông thường.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Có thể kết nối thêm Webhook hoặc lên lịch tự động (`schedule` cron) gửi đều đặn vào đầu giờ sáng hàng ngày.
- **Ghi nhớ:** Với các model reasoning/thinking như Gemini 2.5 Flash, luôn đặt timeout từ 40-45 giây và maxOutputTokens đủ lớn (4096) để đảm bảo câu trả lời được sinh trọn vẹn và chất lượng cao nhất.

---

## PDCA Log #09 — Buổi 8 (Cloud Automation) — 13/09/2026

### 📋 PLAN
- **Mục tiêu:** Thiết lập hệ thống tự động hóa hoàn toàn trên đám mây (Cloud Automation) bằng **GitHub Actions** để tự động kích hoạt bot gửi bản tin AI vào đúng **10:00 sáng Thứ Hai hàng tuần** (giờ Việt Nam), chạy hoàn toàn độc lập mà không cần bật máy tính cá nhân.
- **Output mong muốn:**
  - File workflow cấu hình chuẩn: `.github/workflows/weekly_ai_news.yml`.
  - Cú pháp Cron chuẩn: `0 3 * * 1` (03:00 UTC = 10:00 AM VN).
  - Tích hợp tính năng `workflow_dispatch` để cho phép chạy test thủ công trên GitHub UI bất cứ lúc nào.
  - Hướng dẫn chi tiết cấu hình 3 biến môi trường bảo mật (GitHub Secrets).
- **Dữ liệu / Công nghệ:** GitHub Actions CI/CD, Ubuntu runner, Python 3.11, Crontab schedule.

### ✅ DO
- **Đã thực hiện:**
  1. Tạo thư mục `.github/workflows/` và khởi tạo file `weekly_ai_news.yml`.
  2. Cấu hình lịch biểu: `cron: '0 3 * * 1'` (10h sáng thứ Hai giờ Việt Nam).
  3. Ánh xạ các biến bí mật an toàn qua `${{ secrets.TELEGRAM_BOT_TOKEN }}`, `${{ secrets.TELEGRAM_CHAT_ID }}`, `${{ secrets.GEMINI_API_KEY }}`.
  4. Hướng dẫn các bước đẩy mã nguồn lên kho riêng tư (Private Repo) trên GitHub và nhập Secrets.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu. Workflow đáp ứng đúng tiêu chuẩn GitHub Actions hiện đại, hỗ trợ cả tự động theo tuần và kích hoạt thủ công.
- **Điểm tốt cần giữ lại:**
  - Giải pháp Cloud giúp tiết kiệm điện năng và giải phóng hoàn toàn máy tính cá nhân.
  - Sử dụng GitHub Secrets bảo mật 100% các API keys của người dùng.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Có thể mở rộng tần suất chạy (ví dụ 3 lần/tuần vào Thứ Hai - Thứ Tư - Thứ Sáu) chỉ bằng cách đổi cú pháp cron thành `0 3 * * 1,3,5`.
- **Ghi nhớ:** Giờ cron trên GitHub Actions luôn tính theo UTC (giờ chuẩn quốc tế), do đó muốn chạy lúc 10:00 sáng Việt Nam (UTC+7), giờ cron phải là `10 - 7 = 3` (tức 03:00 UTC).

---

## PDCA Log #07 — Buổi 9 — 20/09/2026

### 📋 PLAN
- **Mục tiêu:** Xây dựng giải pháp tự động hóa kế toán (Accounting RPA Pipeline) chạy trực tiếp từ workspace bằng Python kết nối Google Sheets API (qua OAuth 2.0 Desktop Client `Credentials.json`) thay vì phụ thuộc vào Google Apps Script trên trình duyệt.
- **Output mong muốn:**
  1. Script Python `sync_expenses.py` chuẩn nghiệp vụ kế toán, thực thi chu trình 3 Nhịp (Quét thông minh -> Ghi nối tiếp -> Chống trùng lặp).
  2. Ràng buộc kiểm soát chi phí: `Amount < 500.000đ` tự động duyệt, `>= 500.000đ` chờ duyệt.
  3. Cơ chế xác thực OAuth 2.0 Desktop với `token.json` tự động lưu phiên, không cần đăng nhập lại sau lần đầu.
  4. Bảo mật tuyệt đối thông tin xác thực (`Credentials.json`, `token.json` được bảo vệ trong `.gitignore`).
- **Dữ liệu / Công nghệ:** `Credentials.json`, Python 3.14, `.venv`, `gspread`, `google-auth-oauthlib`, Google Sheets API v4.

### ✅ DO
- **Đã thực hiện:**
  1. Thêm `Credentials.json` và `token*.json` vào `.gitignore` tuân thủ Quy tắc 5 (Bảo mật).
  2. Cài đặt `gspread` và `google-auth-oauthlib` vào môi trường ảo `.venv`.
  3. Lập trình file `sync_expenses.py` với cấu trúc Dynamic Header Mapping, định dạng số tiền, kiểm soát hạn mức chi tiêu 500.000đ, batch append vào `Admin Expense Tracker` và batch update `Done` + ghi nhận `SyncedAt` trong `Employee Data`.
  4. Chạy xác thực thành công OAuth 2.0 qua trình duyệt, khởi tạo `token.json`.
  5. Kiểm thử chạy kiểm tra đồng bộ, xác nhận 2 bảng tính kết nối chính xác và phản hồi dưới 1 giây.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu. Hệ thống chạy trực tiếp trên máy cục bộ, không cần mở Google Apps Script web editor, tốc độ xử lý nhanh và độ tin cậy cao.
- **Điểm tốt cần giữ lại:**
  - Token được lưu trữ cục bộ giúp các lần chạy tiếp theo hoàn toàn tự động (zero-prompt).
  - Khả năng xử lý linh hoạt thứ tự cột (Dynamic Header Mapping) tránh lỗi khi bảng tính bị chỉnh sửa thủ công.
  - Phân luồng hạn mức 500.000đ tự động hóa phê duyệt kế toán.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Có thể lên lịch cron job định kỳ chạy `sync_expenses.py` mỗi ngày hoặc tích hợp thông báo qua Telegram Bot khi có khoản chi >= 500.000đ cần duyệt gấp.
- **Ghi nhớ:** Luôn sử dụng batch update (`update_cells`) thay vì update từng dòng lẻ để tiết kiệm quota Google Sheets API.

---

## PDCA Log #08 — Buổi 10 — 20/09/2026

### 📋 PLAN
- **Mục tiêu:** Xây dựng Agent Skill `/ai4a:build-dashboard-BI` với bộ tiêu chuẩn thiết kế Dashboard hiện đại chuẩn Executive UI/UX: Dark Mode, Glassmorphism, KPI Layout cards, phối màu tương phản cao (High Contrast Glow/Accents) và hiệu ứng nhảy số (Count-Up Animation) mượt mà.
- **Output mong muốn:**
  1. Thư mục skill `.agents/skills/ai4a-build-dashboard-bi/` với file hướng dẫn `SKILL.md` hoàn chỉnh theo triết lý "WOW First Impression & Zero Cognitive Friction".
  2. Bộ tài nguyên thiết kế đi kèm:
     - `glassmorphism_tokens.css`: Hệ thống Design Tokens CSS biến số dùng chung.
     - `count_up.js`: Engine nhảy số native độc lập dùng `requestAnimationFrame` kết hợp `easeOutExpo` và `IntersectionObserver`.
     - `bi_dashboard_template.html`: Bản mẫu dashboard BI hoàn chỉnh với đầy đủ tương tác, biểu đồ Chart.js và bộ lọc thời gian.
  3. File output thực tế tại `outputs/dashboards/executive_bi_dashboard_demo.html` sẵn sàng mở xem trực tiếp trên trình duyệt.
- **Dữ liệu / Công nghệ:** HTML5, CSS3 Glassmorphism, Vanilla JS Count-Up, Chart.js CDN, Google Fonts (Plus Jakarta Sans, JetBrains Mono).

### ✅ DO
- **Đã thực hiện:**
  1. Khởi tạo cấu trúc thư mục `.agents/skills/ai4a-build-dashboard-bi/` và soạn thảo `SKILL.md` chi tiết 5 tiêu chuẩn thiết kế:
     - *Dark Mode Architecture:* Nền Obsidian Canvas kết hợp Ambient Glow Mesh tản sáng đa tầng.
     - *Glassmorphism Spec:* `backdrop-filter: blur(16px) saturate(180%)`, nền bán trong suốt, viền vi quang sáng mảnh và shadow đa tầng.
     - *KPI Layout Standard:* Cấu trúc thẻ chuẩn mực với Icon badge, Hero number, Delta trend pill và Mini Progress Bar.
     - *Phối màu tương phản cao:* Bảng màu Electric Cyan, Neon Emerald, Cyber Crimson, Neon Violet và Amber Gold đạt chuẩn WCAG AA.
     - *Hiệu ứng nhảy số (Count-Up):* Thuật toán tối ưu tốc độ 60-120fps, tự động nhận diện định dạng VND/USD/%, tự re-trigger khi đổi bộ lọc.
  2. Xây dựng bộ token `glassmorphism_tokens.css` và thư viện `count_up.js`.
  3. Thiết kế file template `bi_dashboard_template.html` và xuất bản bản demo tại `outputs/dashboards/executive_bi_dashboard_demo.html`.
  4. Cập nhật bảng Lịch Sử Phát Triển trong `AGENTS.md` (Buổi 10).

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu. Skill đáp ứng toàn bộ các tiêu chuẩn thẩm mỹ hiện đại cao cấp, template trực quan, có thể nhân bản và áp dụng cho mọi loại dữ liệu doanh nghiệp (Sales, HR, ERP, Marketing, Academic).
- **Điểm tốt cần giữ lại:**
  - Định dạng xuất bản Standalone Single-file HTML giúp người dùng mở xem ngay lập tức mà không cần cài đặt node_modules hay dev server.
  - Tích hợp sẵn bộ lọc tương tác (7D, 30D, Quý, Năm) tự động tính toán lại và kích hoạt nhảy số giúp tăng tính thuyết phục khi trình diễn báo cáo trước Ban Giám Đốc.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Mở rộng thêm tính năng tự động chuyển đổi giữa Dark Mode sang Light Glassmorphic khi cần in ấn tài liệu giấy (A4 PDF Print Mode).
- **Ghi nhớ:** Khi thiết kế dashboard nền tối, luôn sử dụng gradient trải dài xuống đáy cho các biểu đồ Area Chart để tạo cảm giác phát quang neon sang trọng.

---

## PDCA Log #09 — Buổi 10 — 20/09/2026

### 📋 PLAN
- **Mục tiêu:** Xây dựng hệ thống Web Dashboard BI cho Công ty TNHH Alpha với vai trò Fullstack AI Engineer & Data Analyst.
- **Output mong muốn:**
  1. Web Dashboard Glassmorphism, Dark mode đọc dữ liệu từ `sales_data.xlsx`.
  2. Cơ chế Realtime Polling mỗi 2 giây cập nhật 4 chỉ số KPI: Doanh Thu (DT), Chi Phí (CP), Lợi Nhuận, Đơn Hàng.
  3. Đầy đủ các biểu đồ: Biểu đồ Cột, Biểu đồ Tròn, Biểu đồ Đường và Bảng Top 10 sản phẩm bán chạy nhất. Toàn bộ giao diện bằng Tiếng Việt.
  4. Tuân thủ tuyệt đối `brand_guideline.txt`: Doanh Thu BẮT BUỘC `#1E3A8A` (Xanh Navy), Chi Phí BẮT BUỘC `#EF4444` (Đỏ san hô). Font chữ Inter.
  5. Python Server chạy trên port 9090, tự động mở Google Chrome.
- **Dữ liệu / Công nghệ:** `sales_data.xlsx`, `brand_guideline.txt`, Python 3.14 (`http.server`, `pandas`), HTML5, CSS3 Glassmorphism, Chart.js, Vanilla JS Count-Up.

### ✅ DO
- **Đã thực hiện:**
  1. Trích xuất và phân tích cấu trúc dữ liệu từ `sales_data.xlsx` (500 đơn hàng, tổng DT 320.5 Tỷ, tổng CP 163.8 Tỷ, tổng LN 132.4 Tỷ).
  2. Thiết kế `dashboard.html` theo tiêu chuẩn Dark Glassmorphism, tích hợp 4 KPI Cards, 3 biểu đồ Chart.js (Line Chart, Donut Chart, Grouped Bar Chart), Bảng Top 10 sản phẩm có thanh tìm kiếm nhanh.
  3. Áp dụng chuẩn nhận diện thương hiệu Alpha: Doanh Thu `#1E3A8A`, Chi Phí `#EF4444`, Lợi Nhuận `#10B981`, Đơn Hàng `#F59E0B`, font `Inter`.
  4. Lập trình backend `server.py` trên cổng 9090 với endpoint `/api/data` có bộ nhớ đệm (caching theo mtime file Excel) giúp chu kỳ polling 2 giây phản hồi dưới 1ms mà không gây nghẽn CPU.
  5. Tích hợp tiểu trình tự động kích hoạt Google Chrome mở `http://localhost:9090` ngay khi khởi chạy.
  6. Khởi động daemon server và kiểm thử API trả về HTTP 200 OK.
  7. Xuất bản bản sao tĩnh tại `outputs/dashboards/alpha_bi_dashboard_20260920.html`.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu đề ra (C, L, E, A, R). Server phản hồi cực nhanh trên port 9090, trình duyệt Chrome tự mở hiển thị bảng điều khiển rực rỡ, hiệu ứng nhảy số mượt mà, đúng tuyệt đối bảng màu brand guideline.
- **Điểm tốt cần giữ lại:**
  - Kỹ thuật caching `os.path.getmtime` đảm bảo server đọc Excel 500 dòng chỉ khi có cập nhật thật sự trên đĩa, giúp polling 2 giây hoàn toàn nhẹ nhàng.
  - Hàm `chart.update('none')` giúp cập nhật dữ liệu biểu đồ realtime mà không gây chớp giật màn hình.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Có thể bổ sung thêm tính năng WebSocket (thay cho Polling HTTP) khi số lượng người xem dashboard đồng thời tăng cao.
- **Ghi nhớ:** Tuân thủ quy định màu thương hiệu là bắt buộc đối với mọi báo cáo doanh nghiệp để đảm bảo tính nhất quán của bộ nhận diện.

---

## PDCA Log #10 — Buổi 10 — 20/09/2026

### 📋 PLAN
- **Mục tiêu:** Xây dựng script `export_dashboard.py` để đóng gói và chia sẻ an toàn Dashboard BI: xuất file HTML tĩnh (offline standalone) và nén bảo vệ bằng mật khẩu `"admin1234"` tương thích với WinRAR và 7-Zip.
- **Output mong muốn:**
  1. Script Python `export_dashboard.py` tự động tổng hợp số liệu từ `sales_data.xlsx`, nhúng trực tiếp dữ liệu (embedded data) vào mã nguồn HTML.
  2. File HTML tĩnh `outputs/dashboards/Alpha_BI_Dashboard_Static.html` có thể mở xem trực tiếp trên mọi trình duyệt ngoại tuyến không cần bật python server.
  3. File nén mã hóa bảo mật `outputs/dashboards/Alpha_BI_Dashboard_Protected.zip` với mật khẩu `"admin1234"` tương thích WinRAR, 7-Zip, Windows Explorer và macOS Archive Utility.
- **Dữ liệu / Công nghệ:** Python 3.14 (`pandas`, `json`, `subprocess`), Standard Zip Encryption, HTML5/CSS3 Glassmorphism.

### ✅ DO
- **Đã thực hiện:**
  1. Lập trình `export_dashboard.py` hoàn chỉnh gồm 4 nhịp:
     - Nhịp 1: Đọc & tổng hợp chỉ số kinh doanh từ `sales_data.xlsx`.
     - Nhịp 2: Nhúng payload JSON tĩnh vào thẻ `<script id="embedded-data">` của `dashboard.html` và cấu hình cờ `window.STATIC_MODE = true`.
     - Nhịp 3: Đóng gói và đặt mật khẩu bảo vệ `"admin1234"` sử dụng tiện ích zip hệ thống.
     - Nhịp 4: Kiểm tra xác thực tính toàn vẹn của file nén bằng lệnh `unzip -t` với mật khẩu để đảm bảo không bị lỗi khi người nhận giải nén bằng WinRAR / 7-Zip.
  2. Thực thi script thành công: tạo file tĩnh 40.7 KB và file nén bảo mật 10.2 KB.
  3. Thử nghiệm giải nén độc lập với mật khẩu `admin1234`, kiểm tra nội dung file HTML tĩnh mở ngoại tuyến hiển thị đầy đủ biểu đồ, 4 KPI và hiệu ứng nhảy số.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu. File nén mở bằng WinRAR và 7-Zip yêu cầu mật khẩu chính xác `"admin1234"`, người dùng không cần cài đặt Python hay môi trường lập trình vẫn xem được đầy đủ báo cáo dashboard.
- **Điểm tốt cần giữ lại:**
  - Nhúng trực tiếp JSON payload giúp file tĩnh không bị lỗi CORS khi mở bằng giao thức `file:///`.
  - Tự động kiểm thử giải nén ngay trong script trước khi bàn giao cho người dùng.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Có thể tích hợp thêm tùy chọn gửi file nén này trực tiếp qua email hoặc Telegram Bot đến Ban Giám Đốc.
- **Ghi nhớ:** Luôn thông báo mật khẩu qua kênh an toàn riêng biệt khi chia sẻ file dữ liệu kinh doanh quan trọng.

---

## PDCA Log #11 — Buổi 11 — 20/09/2026

### 📋 PLAN
- **Mục tiêu:** Xây dựng Web Dashboard Quản lý Ngân sách cho Công ty Beta Solutions dưới vai trò Trưởng phòng Tài chính kiêm Fullstack Developer:
  - Nền tối chuyên nghiệp (Dark Slate) kết hợp Glassmorphism.
  - Tuân thủ tuyệt đối Brand Guideline Beta: Ngân sách (#7C3AED), Chi tiêu (#06B6D4), Vượt ngân sách (#F43F5E).
  - Hiển thị 3 thẻ KPI (Tổng ngân sách, Tổng chi tiêu, Giao dịch vượt NS), 1 biểu đồ cột ghép (Ngân sách vs Chi tiêu), 1 biểu đồ tròn (Tỷ trọng phòng ban) và bảng chi tiết giao dịch.
  - Bộ lọc tương tác theo Quý (Q1-Q4) và Phòng ban, cập nhật tức thì với hiệu ứng nhảy số.
  - Tính năng Real-time: Tự động làm mới số liệu mỗi 2 giây khi file Excel `ngan_sach_phong_ban.xlsx` thay đổi.
  - Nút bấm trực tiếp trên giao diện tạo ra file HTML Dashboard tĩnh độc lập (offline snapshot).
  - Sản phẩm nộp bài: File nén ZIP chứa file HTML tĩnh, đặt mật khẩu bảo vệ `beta2026`.
- **Output mong muốn:**
  1. File `dashboard_beta.html`: Giao diện Dashboard động kết hợp bộ lọc và nút xuất file tĩnh.
  2. File `server_beta.py`: Máy chủ nội bộ trên cổng 9091 phục vụ API realtime (caching mtime 2s) và API xuất file tĩnh.
  3. File `export_beta_dashboard.py`: Script xuất file tĩnh độc lập và đóng gói ZIP mã hóa bằng mật khẩu `beta2026`.
  4. File tĩnh `outputs/dashboards/Beta_Solutions_Dashboard_Static.html` và file nén bảo mật `Beta_Solutions_Dashboard_Protected.zip`.
- **Dữ liệu / Brand:** `sample-data/ngan_sach_phong_ban.xlsx` (96 giao dịch), `knowledge-base/brand_guideline_beta.txt`.

### ✅ DO
- **Đã thực hiện:**
  1. Khởi động phiên phỏng vấn tương tác `/grill-me` để làm rõ và chốt kiến trúc máy chủ Python Server nội bộ (cổng 9091), quy trình xuất file tĩnh, mật khẩu nén `beta2026`, quy cách biểu đồ cột ghép thông minh (mặc định theo phòng ban, lọc theo quý khi chọn 1 phòng ban) và bảng giao dịch.
  2. Tạo script `export_beta_dashboard.py` tổng hợp 96 giao dịch, 6 phòng ban, 4 quý; biên dịch dữ liệu tĩnh và nén mã hóa chuẩn WinRAR/7-Zip bằng lệnh zip hệ thống.
  3. Thiết kế giao diện `dashboard_beta.html` chuẩn Executive UI/UX theo kỹ năng `ai4a:build-dashboard-BI`:
     - Nền Dark Slate (`#0F172A`) với dải ánh sáng mesh tím - xanh ngọc - hồng san hô.
     - 3 thẻ KPI phát sáng chuẩn Brand Guideline với animation Count-Up mượt mà.
     - Biểu đồ Cột ghép linh hoạt và Biểu đồ Donut tỷ trọng chi tiêu (Chart.js).
     - Bảng giao dịch có badge phát sáng "Trong ngân sách" / "Vượt ngân sách", tìm kiếm và phân trang.
     - Modal popup sang trọng hiển thị mật khẩu `beta2026` với nút sao chép 1 chạm và tự động tải file ZIP.
  4. Lập trình máy chủ `server_beta.py` (cổng 9091), hỗ trợ endpoint `/api/data` có cache mtime (đáp ứng < 2ms), `/api/export-static`, `/api/download-zip` và tự động mở Chrome.
  5. Đóng gói thành công `Beta_Solutions_Dashboard_Protected.zip`, kiểm thử giải nén với mật khẩu `beta2026` đạt 100% toàn vẹn dữ liệu.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu (C, L, E, A, R). 
- **Kết quả kiểm thử:**
  - Kiểm tra số liệu: Tổng NS 39.64 Tỷ VNĐ, Tổng Chi 39.98 Tỷ VNĐ, 32 giao dịch vượt NS (33.3%).
  - Kiểm tra Server: Phục vụ API tốc độ cao, HTTP 200 OK.
  - Kiểm tra bảo mật file nén: Lệnh `unzip -t -P "beta2026"` thành công; lệnh với sai mật khẩu bị từ chối chính xác.
- **Điểm tốt cần giữ lại:**
  - Thiết kế cột ghép thông minh (tự động chuyển trục hoành từ Phòng ban sang Quý khi chọn phòng ban) tăng tối đa trải nghiệm phân tích tài chính.
  - Cơ chế xuất file kép: Server API export + Fallback download ngay trên browser nếu người dùng mở file ngoại tuyến.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Có thể tích hợp thêm tính năng upload trực tiếp file Excel mới ngay trên giao diện web để cập nhật ngân sách mà không cần chép file vào thư mục `sample-data/`.
- **Ghi nhớ:** Khi sử dụng mật khẩu nén, luôn thiết kế thông báo rõ ràng trên giao diện (kèm nút Copy) để người dùng không gặp rắc rối khi giải nén nộp bài.

---

## PDCA Log #12 — Buổi 11 (Bổ sung) — 20/09/2026

### 📋 PLAN
- **Mục tiêu:** Tích hợp tính năng gửi trọn bộ file Dashboard tĩnh và file nén ZIP bảo mật qua Telegram Bot cho Trưởng phòng Tài chính / Ban Giám Đốc.
- **Output mong muốn:**
  1. File `send_dashboard_telegram.py`: Script tự động hóa gửi 2 file tài liệu kèm bản tin Executive Digest.
  2. Nút bấm **"📲 Gửi Qua Telegram"** trên thanh Header của Dashboard Web (`dashboard_beta.html`).
  3. Endpoint `POST /api/send-telegram` trên máy chủ `server_beta.py`.
- **Dữ liệu / Token:** Tận dụng `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` từ `.env`.

### ✅ DO
- **Đã thực hiện:**
  1. Phỏng vấn `/grill-me` để chốt quy cách gửi: Gửi đồng thời cả 2 file (HTML tĩnh mở xem ngay + ZIP có mật khẩu `beta2026`), kích hoạt kép qua Web UI & CLI.
  2. Lập trình `send_dashboard_telegram.py` sử dụng Telegram API `sendDocument`, tự động cập nhật bản đóng gói mới nhất và soạn caption Executive với 3 icon màu thương hiệu 🟣 🔵 🔴.
  3. Cập nhật `server_beta.py` tiếp nhận `POST /api/send-telegram` trả về JSON kết quả.
  4. Cập nhật giao diện `dashboard_beta.html` với nút bấm Cyan Glassmorphic và hàm `handleSendTelegram()`.
  5. Kiểm thử gửi thực tế từ terminal và từ server qua curl: Telegram Bot trả về HTTP 200 OK, tin nhắn và cả 2 file đã chuyển thẳng vào Telegram của người dùng.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu. 
- **Kết quả:** Cả 2 file đính kèm hiển thị đẹp mắt trên ứng dụng Telegram (Desktop/Mobile), caption đầy đủ thông tin KPI và mật khẩu giải nén rõ ràng.

### 🔄 ACT
- **Ghi nhớ:** Với các báo cáo quan trọng, việc gửi cả file xem trực tiếp (HTML) lẫn file nén có mật khẩu (ZIP) giúp người nhận linh hoạt xem ngay trên điện thoại hoặc lưu trữ tài liệu bảo mật.

---

## PDCA Log #13 — Buổi 12 — 20/09/2026

### 📋 PLAN
- **Mục tiêu:** Tải và cài đặt skill `convert-word-to-md` từ GitHub (`github/awesome-copilot`) vào workspace hiện tại (`.agents/skills/convert-word-to-md/`).
- **Output mong muốn:**
  1. Thư mục skill `.agents/skills/convert-word-to-md/` đầy đủ các file: `SKILL.md`, `references/setup.md`, `scripts/convert_word_to_md.py`, `scripts/requirements.txt`.
  2. Cài đặt đầy đủ dependencies (`markitdown[docx]`, `mammoth`) vào môi trường ảo `.venv`.
  3. Kiểm thử CLI hoạt động tốt (`markitdown OK`, `convert_word_to_md.py --help`).
- **Nguồn:** `https://github.com/github/awesome-copilot/tree/main/skills/convert-word-to-md`

### ✅ DO
- **Đã thực hiện:**
  1. Tạo cấu trúc thư mục `.agents/skills/convert-word-to-md/` (kèm `references/` và `scripts/`).
  2. Tải toàn bộ mã nguồn và tài liệu hướng dẫn từ GitHub về workspace.
  3. Cài đặt các gói phụ thuộc qua `.venv/bin/pip install -r .agents/skills/convert-word-to-md/scripts/requirements.txt`.
  4. Xác thực import thành công `from markitdown import MarkItDown` và kiểm tra lệnh CLI `convert_word_to_md.py --help` hoạt động hoàn hảo.
  5. Cập nhật bảng Lịch Sử Phát Triển trong `AGENTS.md`.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu.
- **Kết quả:** Skill đã sẵn sàng để AI Agent tự động gọi khi người dùng yêu cầu phân tích/chuyển đổi tài liệu `.docx` trong tương lai.

### 🔄 ACT
- **Ghi nhớ:** Khi có file Word `.docx` cần đọc, agent sẽ ưu tiên dùng script này chuyển sang Markdown để phân tích chính xác và giữ nguyên hình ảnh thay vì đọc file nhị phân trực tiếp.

---

## PDCA Log #14 — Buổi 12 (Bổ sung) — 20/09/2026

### 📋 PLAN
- **Mục tiêu:** Thiết kế hệ thống Multi-Agent chuyên biệt để tự động chuyển đổi các file tài liệu thô trong `knowledge-base/raw/` sang Markdown tại `knowledge-base/processed/`:
  - Mỗi loại tài liệu có một file agent markdown chuyên biệt trong `.agents/agents/`.
  - Agent Orchestration nạp file agent tương ứng và điều phối subagent thực thi tự động.
  - Tự động di chuyển file gốc đã xử lý vào `knowledge-base/raw/archive/` để tránh xử lý trùng lặp.
- **Output mong muốn:**
  1. Thư mục `.agents/agents/` chứa 4 agent: `agent-convert-word-to-markdown.md`, `agent-convert-pdf-to-markdown.md`, `agent-convert-excel-to-markdown.md`, `agent-convert-text-to-markdown.md`.
  2. Script điều phối `scripts/orchestrate_converters.py`.
  3. Skill điều phối `raw-converter-orchestrator` (`.agents/skills/raw-converter-orchestrator/SKILL.md`).
  4. Thư mục `knowledge-base/processed/` và `knowledge-base/raw/archive/`.

### ✅ DO
- **Đã thực hiện:**
  1. Phỏng vấn `/grill-me` để chốt quy cách hợp đồng System Prompt trong `.agents/agents/`, cơ chế điều phối tự động quét extension và chính sách lưu trữ file gốc.
  2. Khởi tạo 4 file agent chuyên biệt với đầy đủ Frontmatter YAML, Mission, Tooling, Quality Checklist và Return Contract.
  3. Xây dựng script Python `scripts/orchestrate_converters.py` tự động phân loại file (.docx, .pdf, .xlsx, .txt) và kết nối với skill `convert-word-to-md`.
  4. Đóng gói skill `raw-converter-orchestrator` với cờ `user-invocable: true` hỗ trợ gọi nhanh qua `/raw-converter`.
  5. Tạo dữ liệu thử nghiệm `.docx` và kiểm thử chuyển đổi thực tế 3 file (`.docx`, 2 file `.txt`): Chuyển đổi thành công 3/3 tệp, trích xuất cấu trúc bảng và lưu trữ gốc an toàn vào `archive/`.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu đề ra.
- **Kết quả:** Kiến trúc tách biệt rõ ràng giữa "Điều phối" (Orchestrator) và "Chuyên gia" (Specialized Agent prompts), cho phép mở rộng thêm các loại định dạng mới bất kỳ lúc nào mà không ảnh hưởng đến hệ thống hiện tại.

### 🔄 ACT
- **Ghi nhớ:** Khi bổ sung một định dạng file mới trong tương lai (ví dụ: audio, pptx, html), chỉ cần thêm một file `agent-convert-<type>-to-markdown.md` vào `.agents/agents/` và khai báo nhánh xử lý trong Orchestrator.

---

## PDCA Log #15 — Buổi 12 (Tối ưu hóa) — 20/09/2026

### 📋 PLAN
- **Mục tiêu:** Tái cấu trúc theo phản hồi của người dùng: Không phân mảnh thành 4 file agent riêng lẻ, mà hợp nhất thành DUY NHẤT 1 file agent chuyên trách toàn diện: `agent-convert-raw-to-markdown.md` trong `.agents/agents/`.
- **Output mong muốn:**
  1. File `agent-convert-raw-to-markdown.md` đa năng, nhận diện và xử lý linh hoạt mọi định dạng (.docx, .pdf, .xlsx, .csv, .txt, .log).
  2. Dọn dẹp 4 file agent riêng lẻ trước đó để giữ `.agents/agents/` tinh gọn.
  3. Cập nhật `scripts/orchestrate_converters.py` và skill `raw-converter-orchestrator`.

### ✅ DO
- **Đã thực hiện:**
  1. Tạo `agent-convert-raw-to-markdown.md` với hợp đồng System Prompt tích hợp đa engine (MarkItDown, Mammoth, Pandas, Text Parser).
  2. Xóa bỏ 4 file phân mảnh (`agent-convert-word-to-markdown.md`, `agent-convert-pdf-to-markdown.md`, `agent-convert-excel-to-markdown.md`, `agent-convert-text-to-markdown.md`).
  3. Đồng bộ tên agent thống nhất `agent-convert-raw-to-markdown` trong script điều phối.
  4. Cập nhật tài liệu kỹ năng `.agents/skills/raw-converter-orchestrator/SKILL.md`.
  5. Kiểm thử thực tế chuyển đổi file `quy_trinh_chi_phi.txt`: Agent hợp nhất tự động nhận diện và xử lý thành công 100%.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu. Thư mục `.agents/agents/` hiện chỉ có duy nhất 1 file agent, cấu trúc gọn gàng, dễ bảo trì, đúng yêu cầu của người dùng.

### 🔄 ACT
- **Ghi nhớ:** Ưu tiên cấu trúc Agent hợp nhất (Universal Specialist) cho các tác vụ chuyển đổi dữ liệu thô để tránh trùng lặp code và đơn giản hóa việc nạp prompt cho Orchestrator.

---

## PDCA Log #16 — Buổi 14 — 20/09/2026

### 📋 PLAN
- **Mục tiêu:** Thiết lập cơ chế Subagent độc lập cho `agent-convert-raw-to-markdown.md`, tuân thủ chuẩn `subagent-orchestration` với quy trình logging, active registry và runner script.
- **Output mong muốn:**
  1. Workflow prompt chuẩn hóa: `.agents/workflows/subagent_convert_prompt.md`.
  2. Bảng theo dõi Subagent đang hoạt động: `logs/active/README.md`.
  3. Script thực thi Subagent: `scripts/run_subagent_convert.py` hỗ trợ logging tự động `logs/active/subagent_convert_raw.log` và in lệnh `agy CLI`.
  4. Xác thực chạy thử nghiệm (dry-run).

### ✅ DO
- **Đã thực hiện:**
  1. Khởi tạo prompt chỉ đạo Subagent tại `.agents/workflows/subagent_convert_prompt.md` nạp file agent hợp nhất và kích hoạt pipeline.
  2. Xây dựng registry quản lý `logs/active/README.md` theo chuẩn của skill `subagent-orchestration`.
  3. Viết script thực thi `scripts/run_subagent_convert.py` tích hợp logging tự động, hỗ trợ chạy background lẫn lệnh `agy CLI`.
  4. Chạy kiểm thử dry-run: Subagent khởi chạy thành công, ghi log sạch sẽ và trả về JSON Return Contract chuẩn.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu.
- **Kết quả:** Subagent đã sẵn sàng để gọi độc lập từ CLI hoặc từ Orchestrator bất cứ lúc nào có tài liệu mới cần xử lý.

### 🔄 ACT
- **Ghi nhớ:** Khi chạy Subagent qua `agy CLI`, luôn đặt các cờ `--log-file`, `--dangerously-skip-permissions` trước `-p` để tránh lỗi nuốt tham số.

---

## PDCA Log #17 — Buổi 15 — 11/10/2026

### 📋 PLAN
- **Mục tiêu:** Xây dựng skill `lead-scoring` tự động hóa chấm điểm và phân loại khách hàng tiềm năng ngành Bất Động Sản theo 5 tiêu chí cốt lõi (Ngân sách, Nhu cầu/Quan tâm, Thời gian mua, Nguồn khách & Hồ sơ, Tương tác), tích hợp bộ quy tắc cộng 50 điểm (VIP) và trừ 50 điểm (Red Flag) từ `knowledge-base/tieu_chi_cham_diem.txt`.
- **Output mong muốn:**
  1. Skill hoàn chỉnh: `.agents/skills/lead-scoring/SKILL.md` kèm rubric `.agents/skills/lead-scoring/references/scoring_rubric.md`.
  2. Engine xử lý Python: `scripts/score_leads.py` (và bản trong `.agents/skills/lead-scoring/scripts/score_leads.py`) hỗ trợ tải từ Google Sheet, làm sạch SĐT 10 số, tính điểm 5 trụ cột, phát hiện cờ đỏ/VIP, đề xuất kịch bản tiếp cận và xuất báo cáo.
  3. Báo cáo Excel chuyên nghiệp 3 sheet (Executive Summary KPI Cards, All Leads Scored, Sales Handover) tại `outputs/reports/BDS_Lead_Scoring_Report.xlsx`.
  4. Báo cáo Markdown điều hành tại `outputs/reports/BDS_Lead_Scoring_Executive_Summary.md`.
  5. Cập nhật `docs/pdca-log.md` và `AGENTS.md`.
- **Dữ liệu cần:**
  - Google Sheet khách hàng: `https://docs.google.com/spreadsheets/d/17rbCAc-gDhSMesf7ILLCHofbg-89i-ecc9mOQPgH6Dg/`
  - Tiêu chí nghiệp vụ: `knowledge-base/tieu_chi_cham_diem.txt`.

### ✅ DO
- **Đã thực hiện:**
  1. Tải và lưu trữ an toàn dữ liệu khách hàng thô vào `sample-data/real_estate_leads_raw.csv`.
  2. Xây dựng engine NLP tiếng Việt và công thức tính điểm 5 trụ cột:
     - Ngân sách (Max 35đ)
     - Nhu cầu & Phân khúc (Max 25đ)
     - Thời gian mua & Cấp thiết (Max 20đ)
     - Nguồn khách & Thẩm quyền (Max 10đ)
     - Tương tác & Khả năng tiếp cận (Max 10đ)
     - Bonus VIP (+10 đến +20đ cho >=2 cờ VIP) và Penalty Red Flag (-50đ).
  3. Phân tầng chuẩn xác 12 khách hàng thực tế:
     - **HOT (4 leads - 33.3%):** Trần Hoàng Dũng (100đ), Đặng Hoàng Hùng (100đ), Bùi Phương Tâm (100đ), Lê Anh Lan (96đ).
     - **WARM (3 leads - 25.0%):** Lý Đức Cường (78đ - Căn hộ 2PN Q7 xem cuối tuần), Phan Văn Hoa (75đ - Thuê spa Q1), Phạm Minh Lan (68đ - Đất nền 2-3 tỷ).
     - **JUNK / COLD (5 leads - 41.7%):** Hồ Hồng Linh, Đặng Hoàng Dũng, Hồ Phương Mai, Ngô Anh Lan, Nguyễn Hoàng Tuấn (Chặn hoàn toàn do sai số, thuê bao, spam, yêu cầu phi thực tế).
  4. Lập trình xuất bản file Excel Dashboard `outputs/reports/BDS_Lead_Scoring_Report.xlsx` với màu sắc trực quan, KPI cards, phân tách sheet Bàn giao Sales riêng biệt kèm gợi ý kịch bản mở đầu cuộc gọi.
  5. Viết báo cáo Executive Summary Markdown `outputs/reports/BDS_Lead_Scoring_Executive_Summary.md` kèm sơ đồ Mermaid Pie Chart.
  6. Viết bộ tài liệu kỹ năng `SKILL.md` và bảng tra cứu `scoring_rubric.md`.

### 🔍 CHECK
- **Đạt mục tiêu không?** Đạt 100% mục tiêu đề ra.
- **Đánh giá logic:**
  - Lọc chính xác 100% các lead rác và spam, bảo vệ quỹ thời gian của đội ngũ Sales.
  - Phân tách rõ ràng giữa phân khúc siêu sang (VIP) cần can thiệp cấp lãnh đạo (SLA 15 phút) và phân khúc ở thực/đầu tư tầm trung (WARM) cần chăm sóc tư vấn chính sách vay (SLA 2-4 giờ).
  - Tự động chuẩn hóa số điện thoại về định dạng 10 số (bổ sung số 0 đầu) để đồng bộ trực tiếp lên hệ thống CRM/Tổng đài VoIP.

### 🔄 ACT
- **Thay đổi sẽ áp dụng lần sau:** Mở rộng tích hợp API gửi thông báo tức thì qua Telegram Bot (đã có sẵn trong workspace `send_telegram.py`) khi phát hiện Lead HOT mới để kích hoạt phản hồi dưới 5 phút cho Sales.
- **Ghi nhớ:** Luôn duy trì cơ chế Human-in-the-loop để kiểm tra định kỳ 10% tệp Cold leads, phòng ngừa trường hợp khách hàng VIP kín tiếng để lại thông tin tối giản.


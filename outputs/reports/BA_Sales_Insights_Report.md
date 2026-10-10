# BÁO CÁO PHÂN TÍCH KINH DOANH & ĐỀ XUẤT CHIẾN LƯỢC (BA INSIGHTS REPORT)

> **Dự án:** Phân tích Dữ liệu Hiệu quả Bán hàng (Sales Performance Analytics)  
> **Người thực hiện:** Business Analyst (BA)  
> **Dữ liệu phân tích:** `sample-data/MINDX_Lesson 2_DEMO_synthetic_sales_data_500x20.xlsx` (500 giao dịch)  
> **File Dashboard Excel đi kèm:** [BA_Sales_Performance_Dashboard.xlsx](file:///Users/mac/Documents/Haiyentn2295/Agentic%20AI/my-workspace/outputs/reports/BA_Sales_Performance_Dashboard.xlsx)  
> **Thời gian phát hành:** 06/09/2026 | **Phương pháp:** PDCA Framework (Plan - Do - Check - Act)  

---

## I. TỔNG QUAN KẾT QUẢ KINH DOANH (EXECUTIVE SUMMARY)

| Chỉ số cốt lõi (Core KPIs) | Giá trị thực tế | Tỷ lệ / Đánh giá |
| :--- | :---: | :--- |
| **Tổng Doanh Thu Gộp (Gross Revenue)** | **$2,827,300** | 500 đơn hàng toàn hệ thống |
| **Doanh Thu Thuần Thực Nhận (Net Revenue)** | **$2,109,500** | Sau khi trừ 128 đơn hoàn trả |
| **Tổng Lợi Nhuận Ròng (Total Profit)** | **$718,896** | Biên lợi nhuận trung bình: **25.43%** |
| **Tổng Chiết Khấu (Discount)** | **$282,305** | Chiếm **9.98%** tổng doanh thu |
| **Tổng Chi Phí Marketing** | **$279,638** | Chiếm **9.89%** tổng doanh thu |
| **Giá Vốn Hàng Bán (COGS)** | **$1,546,461** | Chiếm **54.69%** tổng doanh thu |
| **Tỷ Lệ Hoàn Trả Hàng (Return Rate)** | **25.60%** | **128 đơn bị hoàn** (Mức báo động cao) |
| **Giá Trị Đơn Trung Bình (AOV)** | **$5,655 / đơn** | Trung bình mỗi đơn mua 6.1 sản phẩm |

---

## II. BA (03) INSIGHT QUAN TRỌNG

### 📌 Insight 1: Kênh Online có tỷ lệ hoàn hàng cao báo động (31.45%), xói mòn nghiêm trọng lợi nhuận thực tế
- **Cơ sở dữ liệu:**
  - Kênh **Online** đạt tổng doanh thu $875,750 (159 đơn hàng). Tuy nhiên, có tới **50 đơn bị khách hoàn trả**, tương đương tỷ lệ hoàn **31.45%**.
  - So sánh với các kênh khác:
    - Kênh **Distributor** (Đại lý): 19.28% (32 đơn hoàn / 166 đơn).
    - Kênh **Offline** (Cửa hàng): 26.29% (46 đơn hoàn / 175 đơn).
- **Phân tích rủi ro kinh doanh:**
  - Cứ gần 3 khách mua Online thì có 1 khách từ chối nhận/hoàn hàng. Doanh nghiệp không chỉ mất **$275,690** doanh thu thuần trên kênh Online mà còn phải gánh chịu chi phí logistics 2 chiều, chi phí đóng gói hư hao và lãng phí chi phí tiếp thị số (Digital Ads).

---

### 📌 Insight 2: Khu vực Central & South dẫn dắt tăng trưởng; Kênh Offline là trụ cột kinh doanh bền vững nhất
- **Cơ sở dữ liệu:**
  - **Theo khu vực:**
    - **Central (Miền Trung):** $1,024,030 doanh thu (36.2%), lợi nhuận $252,455.
    - **South (Miền Nam):** $1,000,910 doanh thu (35.4%), lợi nhuận $252,915.
    - **North (Miền Bắc):** $802,360 doanh thu (28.4%), lợi nhuận $213,526.
  - **Theo kênh bán:**
    - **Offline (Cửa hàng trực tiếp):** Doanh thu đạt **$1,115,440 (39.45%)**, lợi nhuận đạt **$278,958**.
- **Ý nghĩa kinh doanh:**
  - Kênh Offline là nguồn thu lớn và ổn định nhất, đặc biệt tại khu vực Central ($423,810) và South ($411,960).
  - Thị trường miền Bắc (North) đang bị tụt lại phía sau (thấp hơn Central tới hơn $221,000). Đây là khoảng trống thị trường lớn có thể khai thác nếu có chiến lược phân phối phù hợp.

---

### 📌 Insight 3: Nhóm hàng chất lỏng/gia dụng (Household & Beverage) chịu tỷ lệ hoàn trả kỷ lục & phát hiện đơn hàng bị âm lợi nhuận
- **Cơ sở dữ liệu:**
  - Danh mục **Household** có tỷ lệ hoàn cao nhất toàn bộ hệ thống (**33.33%** - 34/102 đơn), khiến biên lợi nhuận danh mục này rơi xuống mức thấp nhất công ty (**23.77%** so với trung bình 25.43%).
  - Top SKU có tỷ lệ hoàn trả cao nhất:
    1. **Detergent (Nước giặt):** Hoàn **48.00%** (12/25 đơn).
    2. **Soft Drink (Nước ngọt):** Hoàn **40.00%** (8/20 đơn).
    3. **Dish Soap (Nước rửa chén):** Hoàn **38.24%** (13/34 đơn).
  - **Phát hiện đơn hàng bất thường (Anomalies):** Đơn hàng `ORD00067` (Sản phẩm Lotion) bán doanh thu $7,500 nhưng bị **lỗ âm -$261.00** do cộng dồn Chiết khấu cao ($1,487.49 ~ 19.8%) và Chi phí Marketing ($1,122.21 ~ 15.0%) vượt qua biên lãi của giá vốn COGS ($5,151.30).
- **Nguyên nhân cốt lõi:**
  - Sản phẩm dạng lỏng, chai lọ nặng, dễ bị nứt vỡ, chảy tràn khi thời gian vận chuyển kéo dài từ 4 – 7 ngày (tỷ lệ hoàn các đơn giao từ 4-5 ngày chạm đỉnh 30.1% - 32.4%).
  - Thiếu chốt chặn kiểm soát chiết khấu tối đa khi kết hợp các chương trình marketing khuyến mại.

---

## III. HAI (02) ĐỀ XUẤT HÀNH ĐỘNG CHIẾN LƯỢC (ACTIONABLE RECOMMENDATIONS)

### 🚀 Đề xuất 1: Chuẩn hóa quy trình đóng gói hàng chất lỏng & Tích hợp xác thực đơn hàng tự động cho kênh Online
> **Mục tiêu:** Giảm tỷ lệ hoàn hàng kênh Online từ **31.45%** xuống dưới **18%** trong Quý 3/2024.

* **Giải pháp chi tiết:**
  1. **Quy chuẩn bao bì chống va đập (Packaging SOP):** Đối với nhóm hàng lỏng và dễ tràn (Detergent, Dish Soap, Soft Drink), bắt buộc bọc màng xốp khí (bubble wrap) tối thiểu 3 lớp, gia cố niêm phong nắp cổ chai và sử dụng thùng carton có vách ngăn giảm chấn.
  2. **Xác nhận đơn tự động (Automated Pre-dispatch Check):** Tích hợp hệ thống Callbot AI / tin nhắn Zalo ZNS tự động gọi/nhắn khách xác nhận địa chỉ và nhu cầu nhận hàng trong vòng 2 giờ sau khi đặt trên kênh Online; tự động hủy hoặc gắn cờ các đơn hàng có dấu hiệu ảo/bom hàng.
  3. **Tối ưu thời gian giao hàng (SLA Logistics):** Phối hợp với đối tác 3PL ưu tiên tuyến giao nhanh 24h - 48h, hạn chế tình trạng lưu kho kéo dài 5-7 ngày khiến khách đổi ý.
* **Hiệu quả dự kiến:** Tiết kiệm hơn **$100,000** giá trị hàng bị hoàn, giảm 40% chi phí vận chuyển bồi hoàn hai chiều.

---

### 🚀 Đề xuất 2: Thiết lập sàn kiểm soát biên lợi nhuận (Margin Floor) & Đẩy mạnh độ phủ kênh tại thị trường miền Bắc (North)
> **Mục tiêu:** Nâng biên lợi nhuận toàn hệ thống từ **25.43%** lên **27.5%**, thu hẹp khoảng cách doanh thu khu vực North.

* **Giải pháp chi tiết:**
  1. **Khóa mức chiết khấu trần (Discount Ceiling Policy):** Cài đặt luật tự động trên hệ thống ERP / POS: **Giới hạn mức chiết khấu tối đa không quá 15% doanh thu đơn hàng**. Tuyệt đối không cho phép áp dụng đồng thời mã giảm giá sâu với chi phí voucher marketing của sàn để triệt tiêu hoàn toàn rủi ro bán lỗ (loại bỏ dứt điểm các trường hợp như đơn `ORD00067`).
  2. **Tăng cường nguồn lực cho thị trường Miền Bắc:**
     - Điều chuyển 15% ngân sách marketing từ các chiến dịch Online không hiệu quả sang phát triển mạng lưới đại lý (Distributor) và hệ thống bán lẻ (Offline) tại Hà Nội, Hải Phòng và Quảng Ninh.
     - Nhân rộng công thức bán lẻ thành công của chuỗi điểm bán tại Miền Trung và Miền Nam ra thị trường miền Bắc.
* **Hiệu quả dự kiến:** Gia tăng doanh thu khu vực North thêm **15% - 20%** (tăng thêm ~$120,000 - $160,000), đồng thời đảm bảo 100% đơn hàng xuất kho đều đạt biên lợi nhuận dương.

---

## IV. BẢNG THEO DÕI & ĐO LƯỜNG TIẾN ĐỘ (PDCA TRACKING)

| Chỉ số KPI | Hiện tại | Mục tiêu Q3/2024 | Bộ phận chịu trách nhiệm |
| :--- | :---: | :---: | :--- |
| Tỷ lệ hoàn kênh Online | 31.45% | **< 18.0%** | E-commerce Team & Kho vận (Logistics) |
| Tỷ lệ hoàn ngành Household | 33.33% | **< 20.0%** | Quản lý chất lượng đóng gói (QA/QC) |
| Tỷ lệ đơn hàng âm lợi nhuận | 0.2% (1 đơn) | **0.0% (Triệt tiêu)** | Kế toán quản trị & Sales Admin |
| Doanh thu khu vực North | $802,360 | **> $920,000** | Giám đốc Kinh doanh Vùng Miền Bắc |
| Biên lợi nhuận gộp toàn hệ thống | 25.43% | **≥ 27.5%** | Ban Giám Đốc & Business Analyst |

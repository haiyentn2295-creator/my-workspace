# Real Estate Lead Scoring Rubric & Keyword Matrix

Tài liệu tham chiếu chi tiết bộ từ khóa và ma trận chấm điểm cho Lead Scoring Bất Động Sản.

---

## 1. Ma Trận Từ Khóa Phân Loại

### 1.1. Cờ VIP (+50 Điểm Thưởng / Kích Hoạt Tầng HOT)
Áp dụng khi khách hàng có các tín hiệu sau:
- **Ngân sách:** `"20 tỷ"`, `"30 tỷ"`, `"trên 20 tỷ"`, `"trên 30 tỷ"`, `"tài chính mạnh"`, `"tài chính cực mạnh"`, `"không thành vấn đề"`, `"thanh toán thẳng"`.
- **Loại hình:** `"biệt thự đơn lập"`, `"penthouse"`, `"shophouse mặt đường lớn"`, `"quỹ đất công nghiệp"`, `"sàn văn phòng diện tích lớn"`, `"sàn văn phòng"`.
- **Vị trí:** `"quận 1"`, `"ven sông"`, `"vinhomes ocean park"`, `"phú mỹ hưng"`.
- **Hồ sơ chủ thể:** `"chủ doanh nghiệp"`, `"nhà đầu tư chuyên nghiệp"`, `"mua sỉ"`, `"gom sỉ"`, `"số lượng lớn"`, `"đã từng mua nhiều dự án"`.
- **Tính cấp thiết & Pháp lý:** `"pháp lý chuẩn 100%"`, `"sổ hồng riêng"`, `"gặp trực tiếp chủ đầu tư"`, `"gặp trực tiếp giám đốc"`.

### 1.2. Cờ Đỏ Red Flags (-50 Điểm Phạt / Loại Bỏ Tầng JUNK)
Áp dụng khi khách hàng có các dấu hiệu tiêu cực:
- **Yêu cầu phi thực tế:** Tìm mua/thuê với mức giá bất khả thi (`"nhà q1 giá 1 tỷ"`, `"giá 2 triệu"`, `"vài trăm triệu"`, `"phi thực tế"`).
- **Không có nhu cầu:** `"nhầm số"`, `"không có nhu cầu"`, `"dữ liệu cũ"`, `"nhầm ngành"`.
- **Không thiện chí:** `"hỏi giá cho vui"`, `"chưa có ý định mua"`, `"thái độ không hợp tác"`.
- **Spam:** `"spam"`, `"bảo hiểm"`, `"vay vốn"`, `"mời chào"`.
- **Lỗi liên lạc:** `"thuê bao"`, `"không bắt máy"`, `"không phản hồi zalo"`, `"gọi nhiều lần không nghe máy"`.

### 1.3. Khách Hàng Tầm Trung (Nhóm WARM: 50 - 79 Điểm)
- Tìm mua chung cư, nhà phố tầm trung (3 - 10 tỷ).
- Cần hỗ trợ vay vốn ngân hàng, đang cân nhắc chính sách ưu đãi.
- Khách hàng thuê mặt bằng kinh doanh (ví dụ: spa, cửa hàng dưới 50 triệu/tháng).
- Khách đầu tư đất nền vùng ven (2 - 3 tỷ) có pháp lý rõ ràng.

---

## 2. Thang Điểm 5 Trụ Cột Chi Tiết

| Trụ Cột | Thang Điểm | Tiêu Chuẩn Đánh Giá |
|:---|:---:|:---|
| **1. Ngân Sách** | 0 - 35 | - >= 20 tỷ / Tài chính cực mạnh: 35đ<br>- 4 - 10 tỷ / Thuê thương mại > 30tr: 25đ<br>- 2 - 3 tỷ / Vùng ven: 18 - 20đ<br>- Mơ hồ: 10đ<br>- Phi thực tế: -50đ |
| **2. Nhu Cầu & Phân Khúc** | 0 - 25 | - Siêu sang / Sỉ / Văn phòng KCN: 25đ<br>- Nhu cầu ở thực rõ ràng / Thuê dài hạn: 18 - 20đ<br>- Tham khảo: 5 - 10đ<br>- Không có nhu cầu / Spam: -50đ |
| **3. Thời Gian Mua** | 0 - 20 | - Xem ngay cuối tuần / Đàm phán trực tiếp: 20đ<br>- 1 - 3 tháng / Trung hạn: 12 - 15đ<br>- Dài hạn > 6 tháng: 5đ<br>- Không mua trong năm: 0đ |
| **4. Nguồn Khách & Hồ Sơ** | 0 - 10 | - Chủ DN / NĐT chuyên nghiệp / Khách VIP: 10đ<br>- Gia đình trẻ / Hộ kinh doanh: 8đ<br>- Vãng lai: 5đ<br>- Tiếp thị ngược: -50đ |
| **5. Tương Tác** | 0 - 10 | - Sẵn sàng gặp / Đòi hỏi pháp lý minh bạch: 10đ<br>- Bắt máy bình thường: 6đ<br>- Thuê bao / Bất hợp tác: -50đ |

---

## 3. Công Thức Tính Điểm
$$\text{Total Score} = \text{Clamp}_{0}^{100} \left( \sum_{i=1}^5 \text{Pillar}_i + \text{Bonus}_{\text{VIP}} + \text{Penalty}_{\text{RedFlag}} \right)$$

Nếu $\text{Penalty}_{\text{RedFlag}} < 0$, Lead tự động rơi vào nhóm **JUNK** hoặc **COLD** với điểm số khống chế $\le 15$ điểm.

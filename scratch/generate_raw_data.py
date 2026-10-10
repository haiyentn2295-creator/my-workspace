import random
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import pandas as pd
import numpy as np

random.seed(42)

first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
middle_names = ["Văn", "Thị", "Hữu", "Đức", "Minh", "Quang", "Gia", "Thanh", "Ngọc", "Tuấn", "Hoàng", "Phương", "Anh", "Xuân", "Thành"]
last_names = ["An", "Bình", "Châu", "Dũng", "Em", "Giang", "Hải", "Khánh", "Linh", "Minh", "Nam", "Oanh", "Phúc", "Quân", "Sơn", "Tâm", "Uyên", "Việt", "Vinh", "Yến", "Thảo", "Hùng", "Trí", "Khoa", "Thịnh", "Trâm"]

courses = [
    {
        "code": "GAI-K12",
        "standard_name": "Generative AI & LLMs Applied",
        "aliases": ["GenAI", "Generative AI", "LLMs Applied", "Generative AI & LLMs Applied"],
        "lecturer": "Thầy Nguyễn Văn An",
        "profile": "star", # high completion, high CSAT, high attendance
        "count": 45
    },
    {
        "code": "PYA-K08",
        "standard_name": "Python & AI Automation Workflow",
        "aliases": ["Python Auto", "Python & AI Automation", "PY Automation", "Python & AI Automation Workflow"],
        "lecturer": "Cô Trần Thị Bình",
        "profile": "strict", # high score, medium-high attendance, good CSAT
        "count": 45
    },
    {
        "code": "DAI-K15",
        "standard_name": "Data Analytics & BI with AI",
        "aliases": ["Data AI", "Data Analytics & BI", "BI with AI", "Data Analytics & BI with AI"],
        "lecturer": "Thầy Lê Hoàng Cường",
        "profile": "struggling", # lower completion, more dropouts, needs slower pace
        "count": 45
    },
    {
        "code": "AIB-K06",
        "standard_name": "AI for Business & Management",
        "aliases": ["AI Business", "AI for Business", "AI Management", "AI for Business & Management"],
        "lecturer": "Cô Phạm Thanh Dung",
        "profile": "stable", # high completion, practical business use cases
        "count": 45
    }
]

feedbacks = {
    "Thầy Nguyễn Văn An": {
        "pos": [
            "Thầy dạy cực kỳ cuốn hút, kiến thức GenAI cập nhật mới nhất!",
            "Rất thích các bài thực hành xây dựng Agent với LLM, giảng viên nhiệt tình.",
            "Thầy An giảng rất dễ hiểu dù kiến thức AI chuyên sâu.",
            "Khóa học tuyệt vời, thầy hỗ trợ giải đáp cả ngoài giờ học.",
            "Project cuối khóa áp dụng ngay được vào công việc thực tế tại công ty."
        ],
        "constructive": [
            "Khóa học hơi nhanh ở phần Prompt Chaining, mong thầy cho thêm ví dụ.",
            "Tài liệu bài giảng nên gửi sớm trước buổi học 1 ngày.",
            "Cần thêm thời gian Q&A ở cuối buổi."
        ]
    },
    "Cô Trần Thị Bình": {
        "pos": [
            "Cô Bình chấm đồ án rất kỹ và chi tiết, học hỏi được rất nhiều tư duy lập trình.",
            "Bài tập Python thực chiến cao, logic rõ ràng.",
            "Cô giảng rất logic và bám sát thực tế tự động hóa văn phòng.",
            "Học xong tự build được pipeline xử lý báo cáo tự động, rất biết ơn cô.",
            "Kiến thức automation cực kỳ hữu ích cho công việc hàng ngày."
        ],
        "constructive": [
            "Cô giao nhiều bài tập quá, người mới bắt đầu lập trình hơi ngợp.",
            "Cô chấm điểm đồ án khá gắt gao, cần có buổi hướng dẫn sửa lỗi chung.",
            "Nên kéo dài thêm 1 buổi thực hành code trực tiếp trên lớp."
        ]
    },
    "Thầy Lê Hoàng Cường": {
        "pos": [
            "Thầy Cường rất thân thiện, hỗ trợ nhiệt tình khi học viên hỏi bài.",
            "Phần kết hợp PowerBI với AI rất hay và trực quan.",
            "Thầy có nhiều case study thực tế từ doanh nghiệp lớn."
        ],
        "constructive": [
            "Kiến thức phân tích số liệu hơi nặng, thầy giảng hơi nhanh ở phần DAX và SQL.",
            "Mong trung tâm tăng thêm trợ giảng hỗ trợ học viên thực hành trên máy.",
            "Nhiều bài tập phức tạp chưa theo kịp kịp tiến độ lớp.",
            "Cần tài liệu tóm tắt công thức từng buổi học."
        ]
    },
    "Cô Phạm Thanh Dung": {
        "pos": [
            "Cô Dung chia sẻ góc nhìn quản trị và ứng dụng AI vào vận hành doanh nghiệp rất sâu sắc.",
            "Không khí lớp học sôi nổi, nhiều thảo luận nhóm hấp dẫn.",
            "Rất phù hợp cho các cấp quản lý và trưởng nhóm muốn chuyển đổi số.",
            "Cô hướng dẫn tận tâm, bài tập tình huống thực tế.",
            "Slide bài giảng đẹp và hệ thống hóa rất bài bản."
        ],
        "constructive": [
            "Nên đi sâu hơn vào phần đo lường ROI của các dự án AI.",
            "Thời gian thảo luận nhóm hơi ngắn so với khối lượng bài tập tình huống."
        ]
    }
}

raw_records = []
student_id_counter = 1

sources = ["Google Form Đăng Ký", "LMS Điểm Danh Canvas", "Khảo sát cuối khóa Google Sheet"]

for course in courses:
    c_code = course["code"]
    c_std = course["standard_name"]
    c_aliases = course["aliases"]
    lecturer = course["lecturer"]
    profile = course["profile"]
    count = course["count"]
    
    for i in range(count):
        s_id = f"HV-2026-{student_id_counter:03d}"
        student_id_counter += 1
        
        # Name generation
        fn = random.choice(first_names)
        mn = random.choice(middle_names)
        ln = random.choice(last_names)
        full_name = f"{fn} {mn} {ln}"
        
        # Introduce dirty name cases (whitespace, all lowercase, extra spaces)
        r_case = random.random()
        if r_case < 0.2:
            dirty_name = f"  {full_name.lower()}  "
        elif r_case < 0.35:
            dirty_name = f"{fn.lower()}  {mn}   {ln.lower()}"
        elif r_case < 0.45:
            dirty_name = full_name.upper()
        else:
            dirty_name = full_name
            
        # Phone generation
        core_phone = f"{random.choice(['090', '091', '098', '097', '093', '088', '077', '039'])}{random.randint(1000000, 9999999)}"
        r_phone = random.random()
        if r_phone < 0.25:
            dirty_phone = f"+84{core_phone[1:]}"
        elif r_phone < 0.45:
            dirty_phone = f"{core_phone[:4]}.{core_phone[4:7]}.{core_phone[7:]}"
        elif r_phone < 0.65:
            dirty_phone = f"{core_phone[:4]} {core_phone[4:7]} {core_phone[7:]}"
        elif r_phone < 0.75:
            dirty_phone = f"84{core_phone[1:]}"
        else:
            dirty_phone = core_phone
            
        # Email
        email = f"student_{student_id_counter}@{random.choice(['gmail.com', 'outlook.com', 'fpt.edu.vn', 'company.vn'])}"
        
        # Dirty course name
        dirty_course = random.choice(c_aliases)
        
        # Profile-driven attendance, score, csat
        if profile == "star":
            is_dropout = (i == 44)
            if is_dropout:
                att_val = random.randint(30, 45)
                score_val = None
                csat_val = None
                fb = "Bận việc gia đình nên không tiếp tục theo học được."
            else:
                att_val = random.randint(80, 100)
                score_val = round(random.uniform(7.5, 9.8), 1)
                csat_val = round(random.choice([4.5, 4.8, 5.0, 5.0, 5.0]), 1)
                fb = random.choice(feedbacks[lecturer]["pos"] if random.random() > 0.15 else feedbacks[lecturer]["constructive"])
        elif profile == "strict":
            is_dropout = (i in [40, 41, 42, 43, 44])
            if is_dropout:
                att_val = random.randint(35, 48)
                score_val = None
                csat_val = random.choice([3.5, 4.0, None])
                fb = "Chương trình nặng, không kịp theo kịp tiến độ bài tập lập trình."
            else:
                att_val = random.randint(75, 95)
                if i in [38, 39]:
                    score_val = round(random.uniform(5.0, 5.8), 1)
                else:
                    score_val = round(random.uniform(7.8, 9.7), 1)
                csat_val = round(random.choice([4.0, 4.2, 4.5, 4.7, 5.0]), 1)
                fb = random.choice(feedbacks[lecturer]["pos"] if random.random() > 0.25 else feedbacks[lecturer]["constructive"])
        elif profile == "struggling":
            is_dropout = (i in range(35, 45))
            if is_dropout:
                att_val = random.randint(25, 48)
                score_val = None
                csat_val = random.choice([3.0, 3.5, 4.0, None])
                fb = "Kiến thức nâng cao khó tiếp thu, xin phép bảo lưu sang khóa sau."
            else:
                att_val = random.randint(70, 92)
                if i in [32, 33, 34]:
                    score_val = round(random.uniform(5.0, 5.8), 1)
                else:
                    score_val = round(random.uniform(6.5, 9.0), 1)
                csat_val = round(random.choice([3.5, 3.8, 4.0, 4.2, 4.5]), 1)
                fb = random.choice(feedbacks[lecturer]["constructive"] if random.random() > 0.4 else feedbacks[lecturer]["pos"])
        else:
            is_dropout = (i in [41, 42, 43, 44])
            if is_dropout:
                att_val = random.randint(30, 49)
                score_val = None
                csat_val = random.choice([4.0, None])
                fb = "Thay đổi lịch công tác đột xuất nên xin phép bảo lưu."
            else:
                att_val = random.randint(78, 98)
                score_val = round(random.uniform(7.0, 9.5), 1)
                csat_val = round(random.choice([4.3, 4.5, 4.7, 4.9, 5.0]), 1)
                fb = random.choice(feedbacks[lecturer]["pos"] if random.random() > 0.2 else feedbacks[lecturer]["constructive"])
                
        # Format attendance
        r_att = random.random()
        if r_att < 0.4:
            dirty_att = f"{att_val}%"
        elif r_att < 0.7:
            dirty_att = att_val
        else:
            dirty_att = f"{att_val / 100:.2f}"
            
        # Format score
        if score_val is None:
            dirty_score = random.choice(["", "Chưa nộp", "Vắng thi", "None"])
        else:
            dirty_score = str(score_val) if random.random() < 0.3 else score_val
            
        # Format CSAT
        if csat_val is None:
            dirty_csat = random.choice(["", "Chưa đánh giá"])
        else:
            r_csat = random.random()
            if r_csat < 0.2:
                dirty_csat = f"{csat_val}/5"
            elif r_csat < 0.35:
                dirty_csat = f"{csat_val} sao"
            else:
                dirty_csat = csat_val
                
        raw_records.append({
            "Ma_HV": s_id,
            "Ho_va_Ten": dirty_name,
            "So_Dien_Thoai": dirty_phone,
            "Email": email,
            "Khoa_Hoc": dirty_course,
            "Ma_Lop": c_code,
            "Giang_Vien": lecturer,
            "Chuyen_Can_Raw": dirty_att,
            "Diem_Do_An_Raw": dirty_score,
            "Danh_Gia_GV_Raw": dirty_csat,
            "Nhan_Xet_Hoc_Vien": fb,
            "Nguon_Du_Lieu": random.choice(sources)
        })

# Introduce 10 duplicate records
for dup_idx in [12, 35, 60, 85, 110, 135, 150, 165, 172, 178]:
    dup_row = raw_records[dup_idx].copy()
    dup_row["Nguon_Du_Lieu"] = "Google Form Đăng Ký (Gửi lại)"
    raw_records.append(dup_row)

df_raw = pd.DataFrame(raw_records)
output_path = "sample-data/raw_student_data_multisource.xlsx"
df_raw.to_excel(output_path, index=False, sheet_name="MultiSource_Raw_Data")

print(f"[✓] Created raw dataset: {output_path} with {len(df_raw)} records (including 10 duplicates).")

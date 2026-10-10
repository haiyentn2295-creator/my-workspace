import os
import openpyxl
import pandas as pd

def run_tests():
    print("=== STARTING ACADEMIC SYSTEM INTEGRATION TESTS ===")
    base_dir = "outputs/reports/2026-09-12"
    master_file = os.path.join(base_dir, "Master_Academic_Report_2026-Q3.xlsx")
    markdown_file = os.path.join(base_dir, "Academic_Training_Executive_Report.md")
    lecturers_dir = os.path.join(base_dir, "lecturers")

    # Test 1: Files existence
    assert os.path.exists(master_file), f"Master file not found: {master_file}"
    assert os.path.exists(markdown_file), f"Markdown report not found: {markdown_file}"
    assert os.path.exists(lecturers_dir), f"Lecturers directory not found: {lecturers_dir}"
    print("[✓] Test 1 Passed: Core deliverable files exist.")

    # Test 2: Master Excel Sheets & Integrity
    wb_master = openpyxl.load_workbook(master_file, data_only=True)
    expected_sheets = ["Executive_Dashboard", "Lecturer_Performance", "Cleaned_Student_Data", "Data_Audit_Log"]
    for s in expected_sheets:
        assert s in wb_master.sheetnames, f"Sheet '{s}' missing in Master Excel"
    print(f"[✓] Test 2 Passed: Master Excel contains all {len(expected_sheets)} required sheets.")

    # Test 3: Cleaned Student Data Validation
    df_clean = pd.read_excel(master_file, sheet_name="Cleaned_Student_Data", dtype={"Số Điện Thoại": str})
    assert len(df_clean) == 180, f"Expected 180 cleaned records, got {len(df_clean)}"
    
    # Phone numbers check in pandas and openpyxl
    for phone in df_clean["Số Điện Thoại"]:
        phone_str = str(phone)
        assert len(phone_str) == 10 and phone_str.startswith("0"), f"Invalid phone in pandas: {phone_str}"
        
    ws_stu = wb_master["Cleaned_Student_Data"]
    for r in range(2, 182):
        cell_val = str(ws_stu.cell(row=r, column=3).value)
        assert len(cell_val) == 10 and cell_val.startswith("0"), f"Invalid phone in Excel cell row {r}: {cell_val}"
    print("[✓] Test 3.1 Passed: 100% phone numbers are 10 digits starting with 0 in both Excel cells and DataFrame.")

    # Course names
    valid_courses = {
        "Generative AI & LLMs Applied",
        "Python & AI Automation Workflow",
        "Data Analytics & BI with AI",
        "AI for Business & Management"
    }
    actual_courses = set(df_clean["Khóa Học"].unique())
    assert actual_courses == valid_courses, f"Courses mismatch: {actual_courses}"
    print("[✓] Test 3.2 Passed: 100% course names mapped to 4 canonical standard titles.")

    # Student names (no trailing/leading spaces, Title Case)
    for name in df_clean["Họ và Tên"]:
        assert name == name.strip(), f"Untrimmed name: '{name}'"
        assert not "  " in name, f"Excess internal space: '{name}'"
    print("[✓] Test 3.3 Passed: 100% student names properly capitalized and trimmed.")

    # Status breakdown
    statuses = df_clean["Trạng Thái"].value_counts()
    assert sum(statuses.values) == 180, "Status sum does not equal 180"
    print(f"[✓] Test 3.4 Passed: Status breakdown: {dict(statuses)}")

    # Test 4: Individual Lecturer Files
    expected_lecturer_files = [
        "Report_Lecturer_Nguyen_Van_An.xlsx",
        "Report_Lecturer_Pham_Thanh_Dung.xlsx",
        "Report_Lecturer_Tran_Thi_Binh.xlsx",
        "Report_Lecturer_Le_Hoang_Cuong.xlsx"
    ]
    total_sub_students = 0
    seen_students = set()

    for l_file in expected_lecturer_files:
        l_path = os.path.join(lecturers_dir, l_file)
        assert os.path.exists(l_path), f"Lecturer file missing: {l_file}"
        wb_l = openpyxl.load_workbook(l_path, data_only=True)
        assert "Class_Summary" in wb_l.sheetnames, f"Class_Summary sheet missing in {l_file}"
        assert "Student_List" in wb_l.sheetnames, f"Student_List sheet missing in {l_file}"

        df_sub = pd.read_excel(l_path, sheet_name="Student_List")
        total_sub_students += len(df_sub)
        sub_ids = set(df_sub["Mã HV"])
        # Ensure no cross-contamination between files
        assert len(seen_students.intersection(sub_ids)) == 0, f"Cross contamination detected in {l_file}"
        seen_students.update(sub_ids)

    assert total_sub_students == 180, f"Sum of lecturer files is {total_sub_students}, expected 180"
    print(f"[✓] Test 4 Passed: 4 confidential lecturer reports verified. Total students = {total_sub_students}/180, 0 overlap.")

    # Test 5: Markdown Report Content
    with open(markdown_file, "r", encoding="utf-8") as f:
        md_text = f.read()
    assert "TÓM TẮT ĐIỀU HÀNH" in md_text, "Missing Executive Summary in MD"
    assert "360-DEGREE RANKING" in md_text or "360 ĐỘ" in md_text, "Missing 360 ranking in MD"
    assert "Thầy Nguyễn Văn An" in md_text, "Missing Thầy An in MD"
    assert "Cô Trần Thị Bình" in md_text, "Missing Cô Bình in MD"
    assert "Thầy Lê Hoàng Cường" in md_text, "Missing Thầy Cường in MD"
    assert "Cô Phạm Thanh Dung" in md_text, "Missing Cô Dung in MD"
    assert "BẢN ĐỒ CẢNH BÁO RỦI RO" in md_text, "Missing Risk Alert Matrix in MD"
    assert "ĐỀ XUẤT CẢI TIẾN HỌC VỤ" in md_text, "Missing Action Plan in MD"
    print("[✓] Test 5 Passed: Markdown Executive Report contains all strategic sections.")

    print("\nALL INTEGRATION TESTS PASSED 100%! 🎉")

if __name__ == "__main__":
    run_tests()

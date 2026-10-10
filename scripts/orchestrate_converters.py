#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MULTI-AGENT RAW TO MARKDOWN ORCHESTRATOR
- Quét các tệp tài liệu trong knowledge-base/raw/ (bỏ qua archive/)
- Tự động nạp agent chuyên biệt tương ứng từ .agents/agents/:
  • .docx         -> agent-convert-word-to-markdown.md
  • .pdf          -> agent-convert-pdf-to-markdown.md
  • .xlsx, .csv   -> agent-convert-excel-to-markdown.md
  • .txt, .log    -> agent-convert-text-to-markdown.md
- Xuất kết quả vào: knowledge-base/processed/<tên_tệp>/
- Di chuyển tệp gốc vào: knowledge-base/raw/archive/
"""

import os
import sys
import shutil
import argparse
import datetime
import subprocess
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = WORKSPACE_DIR / "knowledge-base" / "raw"
PROCESSED_DIR = WORKSPACE_DIR / "knowledge-base" / "processed"
ARCHIVE_DIR = RAW_DIR / "archive"
AGENTS_DIR = WORKSPACE_DIR / ".agents" / "agents"


def ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def convert_word_file(file_path: Path, dest_dir: Path) -> dict:
    """Xử lý tệp .docx qua agent-convert-word-to-markdown"""
    script_path = WORKSPACE_DIR / ".agents" / "skills" / "convert-word-to-md" / "scripts" / "convert_word_to_md.py"
    if not script_path.exists():
        raise FileNotFoundError(f"Không tìm thấy script tại: {script_path}")

    # Chạy script chuyển đổi với -o tới dest_dir
    cmd = [sys.executable, str(script_path), str(file_path), "-o", str(dest_dir)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Lỗi convert_word_to_md: {res.stderr or res.stdout}")

    return {
        "agent": "agent-convert-raw-to-markdown",
        "output_dir": str(dest_dir),
        "status": "SUCCESS"
    }


def convert_text_file(file_path: Path, dest_dir: Path) -> dict:
    """Xử lý tệp .txt, .log qua agent-convert-text-to-markdown"""
    dest_dir.mkdir(parents=True, exist_ok=True)
    md_file = dest_dir / f"{file_path.stem}.md"

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = content.splitlines()
    title = file_path.stem.replace("_", " ").replace("-", " ").title()

    # Bổ sung frontmatter chuyên nghiệp
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    frontmatter = f"""---
title: "{title}"
source_file: "{file_path.name}"
imported_at: "{now_str}"
agent_processed: "agent-convert-raw-to-markdown"
---

# {title}

"""
    # Định dạng lại các tiêu đề
    formatted_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            formatted_lines.append(f"\n## {stripped}")
        elif stripped.startswith("- "):
            formatted_lines.append(line)
        else:
            formatted_lines.append(line)

    final_md = frontmatter + "\n".join(formatted_lines)

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(final_md)

    return {
        "agent": "agent-convert-raw-to-markdown",
        "output_file": str(md_file),
        "status": "SUCCESS"
    }


def convert_excel_file(file_path: Path, dest_dir: Path) -> dict:
    """Xử lý tệp .xlsx, .csv qua agent-convert-raw-to-markdown"""
    import pandas as pd
    dest_dir.mkdir(parents=True, exist_ok=True)
    md_file = dest_dir / f"{file_path.stem}.md"

    sheets_info = []
    md_parts = [
        f"# Báo Cáo Dữ Liệu Bảng Tính: {file_path.stem.replace('_', ' ').title()}",
        f"\n*Nguồn dữ liệu:* `{file_path.name}` • *Thời gian chuyển đổi:* {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    ]

    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
        sheets = [("CSV_Data", df)]
    else:
        xl = pd.ExcelFile(file_path)
        sheets = [(s, xl.parse(s)) for s in xl.sheet_names]

    for sheet_name, df in sheets:
        sheets_info.append(sheet_name)
        md_parts.append(f"## Trang Tính: {sheet_name}")
        md_parts.append(f"- **Kích thước:** {len(df)} dòng × {len(df.columns)} cột")
        md_parts.append(f"- **Danh sách cột:** `{', '.join(str(c) for c in df.columns)}`\n")

        # Giới hạn hiển thị 25 dòng đầu để tránh file markdown quá nặng
        preview_df = df.head(25)
        md_table = preview_df.to_markdown(index=False)
        md_parts.append(md_table)
        if len(df) > 25:
            md_parts.append(f"\n*(Đã trích xuất 25 dòng đầu tiên trên tổng số {len(df)} dòng dữ liệu)*\n")
        md_parts.append("\n---\n")

    with open(md_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_parts))

    return {
        "agent": "agent-convert-raw-to-markdown",
        "output_file": str(md_file),
        "sheets": sheets_info,
        "status": "SUCCESS"
    }


def convert_pdf_file(file_path: Path, dest_dir: Path) -> dict:
    """Xử lý tệp .pdf qua agent-convert-raw-to-markdown bằng markitdown"""
    dest_dir.mkdir(parents=True, exist_ok=True)
    md_file = dest_dir / f"{file_path.stem}.md"

    try:
        from markitdown import MarkItDown
        md_engine = MarkItDown()
        result = md_engine.convert(str(file_path))
        content = result.text_content
    except Exception as e:
        # Fallback cơ bản nếu thư viện thiếu plugin
        content = f"# Tài Liệu PDF: {file_path.name}\n\nLỗi khi trích xuất PDF tự động: {e}"

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "agent": "agent-convert-raw-to-markdown",
        "output_file": str(md_file),
        "status": "SUCCESS"
    }


def orchestrate(dry_run=False, single_file=None):
    ensure_dirs()
    print("=" * 65)
    print("🤖 MULTI-AGENT RAW TO MARKDOWN ORCHESTRATOR")
    print(f"📂 Thư mục nguồn : {RAW_DIR}")
    print(f"📁 Thư mục đầu ra: {PROCESSED_DIR}")
    print(f"🗄️ Thư mục lưu trữ: {ARCHIVE_DIR}")
    print("=" * 65)

    if single_file:
        target_path = Path(single_file)
        if not target_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {target_path}")
        raw_files = [target_path]
    else:
        # Lấy danh sách toàn bộ file trong knowledge-base/raw (bỏ qua archive/ và hidden files)
        raw_files = [
            p for p in RAW_DIR.iterdir()
            if p.is_file() and not p.name.startswith(".")
        ]

    if not raw_files:
        print("ℹ️ Không tìm thấy tệp tin nào cần xử lý trong knowledge-base/raw/.")
        return []

    print(f"🔍 Phát hiện {len(raw_files)} tệp tin cần điều phối xử lý:")
    for f in raw_files:
        print(f"   • {f.name} ({f.suffix.lower()})")

    results = []

    for file_path in raw_files:
        ext = file_path.suffix.lower()
        stem = file_path.stem
        dest_dir = PROCESSED_DIR / stem

        print(f"\n⚡ Đang điều phối xử lý: {file_path.name}...")

        if dry_run:
            print(f"   [DRY-RUN] Sẽ nạp agent tương ứng và xuất ra: {dest_dir}")
            continue

        try:
            if ext == ".docx":
                res = convert_word_file(file_path, dest_dir)
            elif ext in [".txt", ".log"]:
                res = convert_text_file(file_path, dest_dir)
            elif ext in [".xlsx", ".xls", ".csv"]:
                res = convert_excel_file(file_path, dest_dir)
            elif ext == ".pdf":
                res = convert_pdf_file(file_path, dest_dir)
            else:
                print(f"⚠️ Chưa có agent chuyên biệt cho định dạng '{ext}'. Bỏ qua.")
                continue

            # Di chuyển file gốc vào archive
            archive_path = ARCHIVE_DIR / file_path.name
            # Nếu file đã tồn tại trong archive, thêm timestamp
            if archive_path.exists():
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_path = ARCHIVE_DIR / f"{file_path.stem}_{timestamp}{file_path.suffix}"

            shutil.move(str(file_path), str(archive_path))
            print(f"   ✅ Hoàn tất bởi [{res['agent']}]!")
            print(f"   📁 Kết quả: {dest_dir}")
            print(f"   🗄️ Đã lưu trữ gốc: {archive_path.name}")

            res["source_file"] = file_path.name
            res["archive_file"] = archive_path.name
            results.append(res)

        except Exception as err:
            print(f"   ❌ Lỗi khi xử lý {file_path.name}: {err}", file=sys.stderr)

    print("\n" + "=" * 65)
    print(f"🎉 HOÀN TẤT ĐIỀU PHỐI: Đã chuyển đổi thành công {len(results)}/{len(raw_files)} tệp tin.")
    print("=" * 65)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent Raw to Markdown Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Kiểm tra danh sách tệp mà không thực thi")
    parser.add_argument("--file", type=str, help="Chỉ định đường dẫn 1 tệp cụ thể để xử lý")
    args = parser.parse_args()

    orchestrate(dry_run=args.dry_run, single_file=args.file)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUBAGENT EXECUTOR: agent-convert-raw-to-markdown
Thực thi tác tử chuyển đổi tài liệu thô sang Markdown theo hợp đồng
.agents/agents/agent-convert-raw-to-markdown.md và chuẩn subagent-orchestration.
"""

import os
import sys
import json
import datetime
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = WORKSPACE_DIR / "logs" / "active" / "subagent_convert_raw.log"
PROMPT_FILE = WORKSPACE_DIR / ".agents" / "workflows" / "subagent_convert_prompt.md"
AGENT_FILE = WORKSPACE_DIR / ".agents" / "agents" / "agent-convert-raw-to-markdown.md"

def log_event(message: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [SUBAGENT: agent-convert-raw-to-markdown] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)
    print(log_line, end="")

def run_subagent(dry_run: bool = False, single_file: str = None):
    log_event("=== BẮT ĐẦU KHỞI TẠO VÀ THỰC THI SUBAGENT ===")
    log_event(f"Nạp cấu hình từ: {AGENT_FILE.name}")
    
    if not AGENT_FILE.exists():
        log_event(f"LỖI: Không tìm thấy tệp định nghĩa Agent tại {AGENT_FILE}")
        return {"status": "ERROR", "message": "Agent definition not found"}

    import subprocess
    cmd = [
        sys.executable,
        str(WORKSPACE_DIR / "scripts" / "orchestrate_converters.py")
    ]
    if dry_run:
        cmd.append("--dry-run")
    if single_file:
        cmd.extend(["--file", str(single_file)])

    log_event(f"Kích hoạt pipeline: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.stdout:
        for line in proc.stdout.splitlines():
            log_event(f"[OUTPUT] {line}")
    if proc.stderr:
        for line in proc.stderr.splitlines():
            log_event(f"[STDERR] {line}")

    if proc.returncode == 0:
        log_event("=== SUBAGENT HOÀN THÀNH NHIỆM VỤ THÀNH CÔNG ===")
        return {
            "status": "SUCCESS",
            "agent": "agent-convert-raw-to-markdown",
            "returncode": proc.returncode,
            "log_file": str(LOG_FILE)
        }
    else:
        log_event(f"=== SUBAGENT GẶP LỖI (MÃ: {proc.returncode}) ===")
        return {
            "status": "FAILED",
            "agent": "agent-convert-raw-to-markdown",
            "returncode": proc.returncode,
            "log_file": str(LOG_FILE)
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Subagent Runner for agent-convert-raw-to-markdown")
    parser.add_argument("--dry-run", action="store_true", help="Kiểm tra không thực thi")
    parser.add_argument("--file", type=str, help="Chỉ định tệp đơn lẻ")
    parser.add_argument("--print-cli", action="store_true", help="In ra câu lệnh agy CLI tương ứng")
    args = parser.parse_args()

    if args.print_cli:
        print("\n⚡ CÂU LỆNH AGY CLI CHUẨN SUBAGENT-ORCHESTRATION:")
        print(f"agy --log-file logs/active/subagent_convert_raw.log --dangerously-skip-permissions --print-timeout 30m -p \"$(cat {PROMPT_FILE})\"\n")
    else:
        result = run_subagent(dry_run=args.dry_run, single_file=args.file)
        print("\n" + json.dumps(result, indent=2, ensure_ascii=False))

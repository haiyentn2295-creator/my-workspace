#!/usr/bin/env python3
"""
send_to_sheet.py
Script to send expense data JSON (via stdin, arguments, or default data.json)
to the Google Apps Script Web App for Google Sheets logging.
"""

import sys
import json
import ssl
import urllib.request
import urllib.error

# Google Apps Script Web App Endpoint
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxd1uxK19TJbrB-7GDjRYbLTu7f5oBtisnIjmf-3mH-3Se-0JxHDa0f5o6OmFa-Er4RGg/exec"


def get_ssl_context():
    """Create SSL context with fallback for macOS certificate issues."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        # Fallback to unverified context to bypass missing root CA bundle on macOS system Python
        try:
            return ssl._create_unverified_context()
        except Exception:
            return ssl.create_default_context()


def load_input_data():
    """Load JSON data from stdin, argv, or fallback data.json."""
    raw_text = ""
    # 1. Check stdin if piped
    if not sys.stdin.isatty():
        raw_text = sys.stdin.read().strip()

    # 2. Check arguments if stdin was empty
    if not raw_text and len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            raw_text = f.read().strip()

    # 3. Fallback to data.json in current directory
    if not raw_text:
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                raw_text = f.read().strip()
        except FileNotFoundError:
            pass

    if not raw_text:
        raise ValueError("Không tìm thấy dữ liệu đầu vào từ stdin, đối số dòng lệnh hoặc data.json.")

    data = json.loads(raw_text)

    # Normalize structure to {"expenses": [...]} if a raw list is passed
    if isinstance(data, list):
        data = {"expenses": data}

    return data


def send_to_sheet(payload):
    """Post JSON payload to Google Apps Script endpoint and return the response."""
    # Attempt using requests if available
    try:
        import requests
        resp = requests.post(WEB_APP_URL, json=payload, timeout=30)
        return resp.text
    except ImportError:
        pass

    # Fallback to standard urllib with SSL handling
    ctx = get_ssl_context()
    json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        WEB_APP_URL,
        data=json_bytes,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.read().decode("utf-8")


def main():
    try:
        data = load_input_data()
        result_text = send_to_sheet(data)
        # Parse and print pretty JSON or plain text
        try:
            res_json = json.loads(result_text)
            print(json.dumps(res_json, ensure_ascii=False))
        except Exception:
            print(result_text)
    except Exception as err:
        error_resp = {"success": False, "error": str(err)}
        print(json.dumps(error_resp, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()

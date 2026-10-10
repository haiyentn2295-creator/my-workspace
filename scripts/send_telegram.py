#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Automation Workflow: AI News Telegram Bot - Professional Edition (OIPO Model)
=============================================================================
Role: Automation Engineer
Description:
  Tự động thu thập 3 tin tức trí tuệ nhân tạo (AI) mới nhất từ Google News RSS,
  sử dụng Google Gemini 2.5 Flash làm AI Editor để:
    1. Dịch chuẩn xác sang tiếng Việt, giữ nguyên thuật ngữ kỹ thuật tiếng Anh chuyên ngành.
    2. Tóm tắt điểm cốt lõi từng bài viết và đánh số thứ tự [1], [2], [3].
    3. Phân tích nhận xét chuyên sâu (AI Trends & Insights).
    4. Trích xuất giải thích thuật ngữ chuyên môn mới (Tech Vocabulary).
  Gửi bản tin Executive Digest hoàn chỉnh vào Telegram Bot.
  Tích hợp cơ chế Graceful Fallback dự phòng khi mạng/API gặp sự cố.

Mô hình OIPO:
  - [O] Objective: Nâng cấp bot gửi 3 tin AI chọn lọc, có Insight xu hướng và Tech Vocabulary.
  - [I] Input    : RSS feed, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY (từ .env).
  - [P] Process  : Thu thập 3 tin -> Gemini 2.5 Flash phân tích & format -> Dự phòng nếu lỗi.
  - [O] Output   : Bản tin Consolidated Digest chuyên nghiệp gửi lên Telegram.
=============================================================================
"""

import os
import sys
import html
import logging
from datetime import datetime
import xml.etree.ElementTree as ET
import requests
from dotenv import load_dotenv

# Thiết lập logging chuẩn hóa
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("TelegramAIBotPro")

# =============================================================================
# [I] INPUT: Nạp cấu hình bảo mật từ file .env
# =============================================================================
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_RSS_QUERY = os.getenv("RSS_KEYWORDS", "AI OR OpenAI OR Google AI")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# =============================================================================
# [P] PROCESS: Các hàm chức năng chính
# =============================================================================

def get_ai_news(query: str = DEFAULT_RSS_QUERY, limit: int = 3) -> list:
    """
    Lấy danh sách các tin AI mới nhất từ Google News RSS (mặc định lấy 3 tin duy nhất).
    
    Args:
        query: Từ khóa tìm kiếm tin tức trên Google News RSS.
        limit: Số lượng tin tức cần lấy.
        
    Returns:
        list[dict]: Danh sách dict chứa 'title', 'link', 'published'.
    """
    rss_url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    
    try:
        logger.info(f"Đang kết nối Google News RSS với từ khóa: '{query}'...")
        response = requests.get(rss_url, headers=headers, timeout=12)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        items = root.findall("./channel/item")
        
        if not items:
            logger.warning("Không tìm thấy bài viết nào trong RSS feed.")
            return []
            
        news_list = []
        seen_titles = set()
        
        for item in items:
            raw_title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            
            clean_title = html.unescape(raw_title).strip()
            
            # Khử trùng lặp tiêu đề
            if clean_title and clean_title not in seen_titles:
                seen_titles.add(clean_title)
                news_list.append({
                    "title": clean_title,
                    "link": link.strip(),
                    "published": pub_date
                })
                
            if len(news_list) >= limit:
                break
                
        logger.info(f"Đã thu thập thành công {len(news_list)} tin tức AI mới nhất.")
        return news_list
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi khi gửi HTTP request tới Google News RSS: {e}")
        return []
    except ET.ParseError as e:
        logger.error(f"Lỗi khi parse dữ liệu XML từ RSS feed: {e}")
        return []
    except Exception as e:
        logger.error(f"Lỗi không xác định trong get_ai_news: {e}")
        return []


def analyze_and_format_with_gemini(news_list: list, api_key: str = None) -> str:
    """
    Sử dụng Gemini 2.5 Flash làm AI Editor chuyên nghiệp:
    1. Dịch tiêu đề & tóm tắt 3 tin sang tiếng Việt, giữ nguyên thuật ngữ kỹ thuật tiếng Anh.
    2. Viết nhận xét sắc bén về xu hướng AI (AI Insights).
    3. Trích xuất và giải thích thuật ngữ chuyên ngành mới (Tech Vocabulary).
    4. Format định dạng Telegram chuẩn, rõ ràng, thẩm mỹ cao.
    
    Args:
        news_list: Danh sách 3 tin bài từ RSS.
        api_key: Gemini API Key (mặc định đọc từ .env).
        
    Returns:
        str: Nội dung bản tin hoàn chỉnh sẵn sàng gửi vào Telegram.
    """
    key = api_key or GEMINI_API_KEY
    if not key:
        logger.warning("Không tìm thấy GEMINI_API_KEY trong .env. Chuyển sang chế độ Fallback.")
        return None
        
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={key}"
    
    # Chuẩn bị context dữ liệu 3 tin tức
    news_context = ""
    for i, item in enumerate(news_list, 1):
        news_context += f"Tin {i}:\n- Tiêu đề: {item['title']}\n- Link nguồn: {item['link']}\n- Thời gian: {item['published']}\n\n"
        
    today_str = datetime.now().strftime("%d/%m/%Y")
    
    system_prompt = f"""
Bạn là Trưởng ban Biên tập Công nghệ & Chuyên gia Phân tích AI cao cấp (Lead AI Tech Editor & Analyst).
Nhiệm vụ của bạn là biên soạn 1 bản tin điểm tin AI chuyên nghiệp gửi trên Telegram cho các chuyên gia và lãnh đạo công nghệ.

Ngày phát hành: {today_str}

Dữ liệu đầu vào gồm các tin tức AI sau:
{news_context}

YÊU CẦU BIÊN TẬP VÀ NGÔN NGỮ (RẤT QUAN TRỌNG):
1. Ngôn ngữ chính: Tiếng Việt tự nhiên, chuẩn xác, văn phong cô đọng và chuyên nghiệp.
2. Giữ nguyên 100% thuật ngữ/term công nghệ tiếng Anh chuyên ngành (Ví dụ: Agentic AI, Autonomous Agents, Reasoning Model, LLM, Fine-tuning, Prompt Caching, Latency, Multimodal, Benchmark, Framework, Workflow, Zero-shot, RAG...). Tuyệt đối không dịch gượng gạo các từ này sang tiếng Việt.
3. Trình bày số thứ tự [1], [2], [3] rõ ràng. Mỗi tin gồm:
   - Tiêu đề dịch chuẩn (giữ terms)
   - 1-2 câu tóm tắt điểm cốt lõi/tính năng nổi bật
   - Link nguồn bài viết
4. Thêm mục "💡 AI INSIGHT & XU HƯỚNG":
   - 2-3 gạch đầu dòng phân tích sắc bén về bức tranh tổng thể: Động thái thị trường, sự chuyển dịch công nghệ hoặc tác động thực tiễn đằng sau 3 tin trên.
5. Thêm mục "📚 TECH VOCABULARY":
   - Chọn lọc 2-3 thuật ngữ kỹ thuật tiếng Anh nổi bật xuất hiện trong các tin trên và giải thích ngắn gọn trong 1 câu dễ hiểu bằng tiếng Việt.
6. Hashtags ở cuối: #AI #ArtificialIntelligence #TechNews #Gemini

CẤU TRÚC MẪU FORMAT TELEGRAM BẮT BUỘC:
🧠 ĐIỂM TIN AI CHUYÊN SÂU - {today_str}
━━━━━━━━━━━━━━━━━━━━

[1] [Tiêu đề tiếng Việt giữ nguyên term tiếng Anh]
• [Tóm tắt điểm cốt lõi 1-2 câu]
🔗 Nguồn: [link 1]

[2] [Tiêu đề tiếng Việt giữ nguyên term tiếng Anh]
• [Tóm tắt điểm cốt lõi 1-2 câu]
🔗 Nguồn: [link 2]

[3] [Tiêu đề tiếng Việt giữ nguyên term tiếng Anh]
• [Tóm tắt điểm cốt lõi 1-2 câu]
🔗 Nguồn: [link 3]

━━━━━━━━━━━━━━━━━━━━
💡 AI INSIGHT & XU HƯỚNG:
• [Phân tích xu hướng 1]
• [Phân tích xu hướng 2]

━━━━━━━━━━━━━━━━━━━━
📚 TECH VOCABULARY:
• [Term 1]: [Giải thích ngắn 1 câu]
• [Term 2]: [Giải thích ngắn 1 câu]

#AI #ArtificialIntelligence #TechNews #Gemini

Lưu ý: Chỉ trả về nội dung hoàn chỉnh của bản tin theo đúng cấu trúc trên, không thêm lời chào mở đầu hay ghi chú ngoài lề.
"""

    payload = {
        "contents": [{
            "parts": [{"text": system_prompt}]
        }],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 4096
        }
    }
    
    try:
        logger.info(f"Đang phân tích và biên tập bản tin bằng Google Gemini ({GEMINI_MODEL})...")
        response = requests.post(endpoint, json=payload, timeout=45)
        response.raise_for_status()
        
        result_json = response.json()
        candidates = result_json.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts and "text" in parts[0]:
                content = parts[0]["text"].strip()
                logger.info(f"✅ Gemini AI Editor đã biên tập bản tin thành công ({len(content)} ký tự)!")
                return content
                
        logger.warning("Không lấy được nội dung text từ response của Gemini.")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi khi gọi Gemini API ({e}). Kích hoạt Fallback.")
        return None
    except Exception as e:
        logger.error(f"Lỗi xử lý response từ Gemini ({e}). Kích hoạt Fallback.")
        return None


def translate_to_vi_fallback(text: str) -> str:
    """Hàm dịch dự phòng đơn giản qua MyMemory API khi không có Gemini."""
    if not text:
        return ""
    try:
        url = "https://api.mymemory.translated.net/get"
        res = requests.get(url, params={"q": text, "langpair": "en|vi"}, timeout=8)
        if res.status_code == 200:
            tr = res.json().get("responseData", {}).get("translatedText")
            if tr:
                return html.unescape(tr).strip()
    except Exception:
        pass
    return text


def format_fallback_message(news_list: list) -> str:
    """Format bản tin dự phòng khi Gemini không khả dụng."""
    today_str = datetime.now().strftime("%d/%m/%Y")
    lines = [
        f"🧠 ĐIỂM TIN AI HÔM NAY - {today_str}",
        "━━━━━━━━━━━━━━━━━━━━\n"
    ]
    
    for i, item in enumerate(news_list, 1):
        vi_title = translate_to_vi_fallback(item["title"])
        lines.append(f"[{i}] {vi_title}")
        lines.append(f"🔗 Nguồn:\n{item['link']}\n")
        
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("💡 AI INSIGHT: (Đang cập nhật từ hệ thống AI chuyên sâu)")
    lines.append("#AI #TinCongNghe #AIBot")
    return "\n".join(lines)


def send_telegram(message: str, bot_token: str = None, chat_id: str = None) -> bool:
    """
    Gửi tin nhắn định dạng văn bản tới Telegram Chat ID thông qua Bot API bằng requests.
    """
    token = bot_token or BOT_TOKEN
    cid = chat_id or CHAT_ID
    
    if not token or not cid:
        logger.error("Lỗi: Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID trong .env!")
        return False
        
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": cid,
        "text": message,
        "disable_web_page_preview": False
    }
    
    try:
        logger.info(f"Đang gửi tin nhắn tới Telegram Chat ID: {cid}...")
        response = requests.post(api_url, json=payload, timeout=20)
        res_data = response.json()
        
        if response.status_code == 200 and res_data.get("ok"):
            logger.info("✅ Gửi tin nhắn Telegram thành công!")
            return True
        else:
            error_code = res_data.get("error_code")
            desc = res_data.get("description", "Unknown error")
            logger.error(f"❌ Gửi Telegram thất bại (Mã {error_code}): {desc}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi mạng khi kết nối Telegram API: {e}")
        return False
    except Exception as e:
        logger.error(f"Lỗi không xác định trong send_telegram: {e}")
        return False


# =============================================================================
# [O] OUTPUT: Workflow tổng thể thực thi OIPO
# =============================================================================

def run_automation_pipeline():
    """
    Thực thi toàn bộ quy trình OIPO Professional:
    1. [I] Thu thập 3 tin AI mới nhất từ RSS.
    2. [P] Dùng Gemini 2.5 Flash biên tập (Dịch giữ term + Insight + Vocabulary).
           Tự động fallback nếu có sự cố.
    3. [O] Gửi tin nhắn Executive Digest tới Telegram.
    """
    print("\n" + "="*65)
    print("🚀 BẮT ĐẦU WORKFLOW TỰ ĐỘNG HÓA TIN TỨC AI - BẢN NÂNG CẤP (OIPO)")
    print("="*65)
    
    # 1. Thu thập 3 tin AI mới nhất
    news_items = get_ai_news(limit=3)
    if not news_items:
        logger.error("Không thể lấy tin tức AI từ RSS. Dừng workflow.")
        return False
        
    # 2. Xử lý biên tập thông minh qua Gemini 2.5 Flash
    final_message = analyze_and_format_with_gemini(news_items)
    
    # 3. Graceful Fallback nếu Gemini không khả dụng
    if not final_message:
        logger.warning("Sử dụng cơ chế Fallback để định dạng bản tin...")
        final_message = format_fallback_message(news_items)
        
    print("\n--- [NỘI DUNG BẢN TIN EXECUTIVE DIGEST] ---")
    print(final_message)
    print("-------------------------------------------\n")
    
    # 4. Gửi vào Telegram
    success = send_telegram(final_message)
    
    if success:
        print("\n🎉 Hoàn thành xuất sắc: Bản tin AI chuyên nghiệp đã được gửi đến Telegram!\n")
    else:
        print("\n⚠️ Gửi tin thất bại. Vui lòng kiểm tra log lỗi.\n")
        
    return success


if __name__ == "__main__":
    run_automation_pipeline()

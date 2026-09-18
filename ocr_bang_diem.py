# -*- coding: utf-8 -*-
"""
Đọc bảng điểm từ ảnh/PDF học sinh tải lên, qua model đọc ảnh (vision) trên
OpenRouter. Kết quả CHỈ để điền sẵn vào form — học sinh luôn xem lại/sửa
trước khi nộp, không tự động tin tuyệt đối kết quả OCR.

Dùng chung OPENROUTER_API_KEY với llm_narrative.py; model riêng
(OPENROUTER_VISION_MODEL) vì cần model có khả năng đọc ảnh, mặc định chọn
loại rẻ nhất còn đáng tin trên OpenRouter.
"""
import os
import json
import base64
import urllib.request
import urllib.error

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_VISION_MODEL = os.environ.get("OPENROUTER_VISION_MODEL", "google/gemini-2.5-flash-lite")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TIMEOUT_SECONDS = 30
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10MB

SYSTEM_PROMPT = (
    "Bạn đọc ảnh/PDF bảng điểm học sinh Việt Nam và trích ra điểm trung bình "
    "từng môn học. Chỉ lấy điểm TRUNG BÌNH MÔN (hoặc điểm tổng kết môn) nếu "
    "có nhiều loại điểm (miệng/15p/1 tiết/thi...) — không lấy điểm thành phần. "
    "Giữ nguyên tên môn học như trong ảnh (viết hoa chữ cái đầu, tiếng Việt có dấu). "
    "Nếu không đọc rõ hoặc không chắc một môn, BỎ QUA môn đó thay vì đoán bừa. "
    "Chỉ trả về đúng một khối JSON, không kèm chữ nào khác."
)

USER_PROMPT = (
    'Trích bảng điểm trong ảnh/PDF này thành JSON đúng schema: '
    '{"diem": [["Tên môn", 8.5], ["Tên môn khác", 7.0]]}. '
    "Điểm là số thực (thang 10), làm tròn 1 chữ số thập phân nếu ảnh có nhiều số lẻ hơn."
)


def _guess_mime(filename: str, content_type: str | None) -> str:
    if content_type and content_type.startswith(("image/", "application/pdf")):
        return content_type
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        return "application/pdf"
    if name.endswith(".png"):
        return "image/png"
    if name.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if name.endswith(".webp"):
        return "image/webp"
    return "application/octet-stream"


def extract_diem_tu_file(file_bytes: bytes, filename: str, content_type: str | None) -> dict:
    """Trả về {"ok": True, "diem": [[mon, diem], ...]} hoặc {"ok": False, "loi": "..."}."""
    if not OPENROUTER_API_KEY:
        return {"ok": False, "loi": "Server chưa cấu hình OPENROUTER_API_KEY — không đọc được ảnh tự động."}
    if len(file_bytes) > MAX_FILE_BYTES:
        return {"ok": False, "loi": "File quá lớn (giới hạn 10MB)."}

    mime = _guess_mime(filename, content_type)
    if not (mime.startswith("image/") or mime == "application/pdf"):
        return {"ok": False, "loi": "Chỉ hỗ trợ ảnh (JPG/PNG/WEBP) hoặc PDF."}

    b64 = base64.b64encode(file_bytes).decode("ascii")
    data_uri = f"data:{mime};base64,{b64}"

    if mime == "application/pdf":
        file_block = {"type": "file", "file": {"filename": filename or "bang_diem.pdf", "file_data": data_uri}}
    else:
        file_block = {"type": "image_url", "image_url": {"url": data_uri}}

    body = json.dumps({
        "model": OPENROUTER_VISION_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": USER_PROMPT},
                file_block,
            ]},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 2000,
    }).encode("utf-8")

    req = urllib.request.Request(
        OPENROUTER_URL, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://truongvietanh.com",
            "X-Title": "Huong nghiep 3 chieu - OCR bang diem",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        rows = parsed.get("diem")
        if not isinstance(rows, list):
            return {"ok": False, "loi": "Không đọc được bảng điểm từ file này, hãy nhập tay."}
        cleaned = []
        for row in rows:
            if isinstance(row, list) and len(row) == 2:
                mon, diem = row
                try:
                    diem_f = round(float(diem), 1)
                except (TypeError, ValueError):
                    continue
                if isinstance(mon, str) and mon.strip() and 0 <= diem_f <= 10:
                    cleaned.append([mon.strip(), diem_f])
        if not cleaned:
            return {"ok": False, "loi": "Không nhận diện được môn/điểm nào, hãy nhập tay hoặc thử ảnh rõ hơn."}
        return {"ok": True, "diem": cleaned}
    except urllib.error.HTTPError as e:
        return {"ok": False, "loi": f"Lỗi gọi dịch vụ đọc ảnh (mã {e.code}), hãy nhập tay."}
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError):
        return {"ok": False, "loi": "Không đọc được file này (lỗi/timeout), hãy nhập tay."}

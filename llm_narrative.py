# -*- coding: utf-8 -*-
"""
Lớp làm giàu nội dung PDF bằng LLM qua OpenRouter — TÙY CHỌN.

Toàn bộ chấm điểm/xếp hạng/tổ hợp vẫn ra từ luật cố định trong engine.py —
module này KHÔNG được tự đổi mã Holland, thứ hạng giá trị nghề, điểm số hay
tổ hợp đã tính. Nó chỉ viết lại phần LỜI VĂN diễn giải cho cụ thể/chi tiết
hơn bản mẫu câu rule-based (giống văn phong một chuyên gia tư vấn viết tay
thay vì ghép câu mẫu). Nếu không có OPENROUTER_API_KEY, hoặc gọi API
lỗi/timeout/JSON hỏng/thiếu field, hàm trả về None — nơi gọi PHẢI dùng lại
bản rule-based cho (các) field bị thiếu, không bao giờ chặn việc xuất PDF.
"""
import os
import json
import urllib.request
import urllib.error

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-v4.1-flash")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TIMEOUT_SECONDS = 45

SYSTEM_PROMPT = (
    "Bạn là chuyên gia tư vấn hướng nghiệp cho học sinh THPT Việt Nam, đang viết "
    "lời văn cho MỘT PHẦN của hồ sơ định hướng đã có sẵn số liệu (chấm bằng luật "
    "cố định, không phải do bạn tính). Nhiệm vụ DUY NHẤT của bạn là diễn giải các "
    "con số/nhãn đã cho thành lời văn cụ thể, cá nhân hóa theo đúng dữ liệu của em "
    "học sinh này — TUYỆT ĐỐI KHÔNG được đổi mã Holland, thứ hạng giá trị nghề, "
    "điểm số, tên tổ hợp hay mức phù hợp đã cho. Không bịa số liệu thị trường lao "
    "động (lương, tỉ lệ thất nghiệp...). Giọng văn ấm áp, cụ thể, như một người "
    "hiểu rõ hồ sơ này, tránh câu sáo rỗng lặp lại giữa các mục. "
    "Luôn trả lời bằng đúng MỘT khối JSON hợp lệ, không kèm chữ hay markdown nào khác."
)


def _build_user_prompt(ctx: dict) -> str:
    return (
        "DỮ LIỆU ĐÃ CHẤM SẴN BẰNG LUẬT (không được đổi số liệu/nhãn, chỉ viết lời văn):\n"
        f"- Học sinh: {ctx['ho_ten']}, lớp {ctx['lop']}\n"
        f"- Điểm 6 nhóm Holland: {ctx['scores']}\n"
        f"- 3 nhóm trội (theo đúng thứ tự ưu tiên): {ctx['top3_labeled']}\n"
        f"- 3 nhóm còn lại (điểm thấp hơn): {ctx['low_labeled']}\n"
        f"- Giá trị nghề trội theo hạng (hạng 1 là quan trọng nhất): {ctx['gia_tri_troi']}\n"
        f"- Bảng điểm học tập: {ctx['diem_mon']}\n"
        f"- Tổ hợp xét tuyển được xếp ưu tiên (mã, môn, tổng điểm, nhãn ưu tiên, khối ngành mở ra mặc định): {ctx['to_hop_uu_tien']}\n"
        f"- Gợi ý ngành nghề nền tảng (nhóm ngành, nghề tiêu biểu, công việc thực tế, mức phù hợp): {ctx['nganh_nghe_nen']}\n\n"
        "Hãy trả về đúng JSON theo schema sau (tiếng Việt, không markdown, không thêm field khác):\n"
        "{\n"
        '  "holland_detail_html": "3-4 câu (ngăn bằng <br/>) diễn giải CỤ THỂ ý nghĩa từng nhóm trội theo đúng điểm số, và một câu tổng kết chân dung sở thích — văn phong như ví dụ: một câu riêng cho từng nhóm trội, giải thích nó nói lên điều gì về cách em thích làm việc",\n'
        '  "nhan_xet_nl": "2-3 câu nhận xét tổng quan bảng điểm, chỉ rõ môn nào ăn khớp với nhóm Holland trội, không liệt kê lại toàn bộ bảng",\n'
        '  "nhan_xet_th": "2-3 câu giải thích vì sao tổ hợp ưu tiên số 1 hợp lý, có thể nhắc tổ hợp phụ/dự phòng dùng để làm gì",\n'
        '  "to_hop_mo_ta": {"MÃ_TỔ_HỢP": "1 câu mô tả khối ngành mở ra RIÊNG cho tổ hợp này (không dùng chung 1 câu cho mọi tổ hợp)"},\n'
        '  "nganh_nghe": [["Tên nhóm ngành cụ thể", "Nghề tiêu biểu cụ thể", "Công việc thực tế 1 câu", "Rất phù hợp|Phù hợp|Cân nhắc"]],\n'
        '  "nhan_xet_nn": "2-3 câu tổng kết vì sao nhóm ngành đầu bảng khớp cả ba chiều (thích/coi trọng/làm được)",\n'
        '  "phan_tich_chi_tiet": [\n'
        '    ["Điểm đồng thuận", "3-4 câu chỉ rõ ba chiều (Holland, giá trị nghề, điểm số) cùng chỉ về đâu, trích đúng số liệu"],\n'
        '    ["Điểm cần cân nhắc", "2-3 câu chỉ ra chỗ lệch/cần lưu ý giữa ba chiều, nếu có, dựa đúng số liệu — nếu không có gì lệch thì nói rõ ba chiều khá đồng nhất"],\n'
        '    ["Gợi ý hành động", "2-3 câu gợi ý hành động cụ thể, thực tế cho học sinh THPT Việt Nam (môn tự chọn, câu lạc bộ, trải nghiệm...), không chung chung"]\n'
        "  ]\n"
        "}\n"
        "nganh_nghe: dựa trên 'Gợi ý ngành nghề nền tảng' đã cho, có thể viết lại lời văn cụ thể hơn và/hoặc "
        "thêm tối đa 2 ngành/nghề khác phù hợp, nhưng KHÔNG được đổi mức phù hợp một cách vô căn cứ. "
        "to_hop_mo_ta: bắt buộc có đủ key cho MỌI mã tổ hợp xuất hiện trong dữ liệu tổ hợp ưu tiên ở trên."
    )


def generate_narrative(ctx: dict) -> dict | None:
    """ctx cần có: ho_ten, lop, scores, top3_labeled, low_labeled, gia_tri_troi,
    diem_mon, to_hop_uu_tien, nganh_nghe_nen.
    Trả về dict theo schema ở trên, hoặc None nếu gọi API/parse thất bại."""
    if not OPENROUTER_API_KEY:
        return None

    body = json.dumps({
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(ctx)},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
        "max_tokens": 6000,
        "reasoning": {"max_tokens": 400},
    }).encode("utf-8")

    req = urllib.request.Request(
        OPENROUTER_URL, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://truongvietanh.com",
            "X-Title": "Huong nghiep 3 chieu",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        required = {"holland_detail_html", "nhan_xet_nl", "nhan_xet_th", "nhan_xet_nn"}
        if not required.issubset(parsed.keys()):
            return None
        parsed.setdefault("to_hop_mo_ta", {})
        parsed.setdefault("nganh_nghe", None)
        parsed.setdefault("phan_tich_chi_tiet", None)
        return parsed
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError):
        return None

# Hướng nghiệp 3 chiều — App tự host

App độc lập, KHÔNG cần Claude/n8n/Netlify để chạy. Học sinh làm test ngay trên
web (frontend `static/index.html`), backend FastAPI chấm điểm bằng luật cố định
(`engine.py`, dữ liệu ở `data.py`), lưu vào DB (`db.py`), và xuất PDF
(`pdf_gen.py` + `radar_gen.py`, dùng lại đúng thiết kế của skill gốc).

**Điểm số, mã Holland, tổ hợp, thứ hạng giá trị nghề luôn do luật cố định
tính — không bao giờ do AI quyết định.** Có thể bật thêm LLM (qua OpenRouter,
`llm_narrative.py`) để viết LỜI VĂN nhận xét/diễn giải chi tiết, cá nhân hóa
hơn bản câu mẫu mặc định — hoàn toàn tùy chọn, tắt đi app vẫn chạy đầy đủ.

## Chạy nhanh bằng Docker (khuyến nghị)

```bash
docker build -t huongnghiep3chieu .
docker run -d -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  --name huongnghiep3chieu huongnghiep3chieu
```

Mở `http://<ip-server>:8000` — mặc định dùng SQLite (`data/data.db`), không cần
cài thêm gì.

## Dùng Postgres thay vì SQLite

Đặt biến môi trường `DATABASE_URL` khi chạy container, ví dụ:

```bash
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/dbname" \
  --name huongnghiep3chieu huongnghiep3chieu
```

Schema tương ứng cũng có ở file `huongnghiep3chieu_schema.sql` (đã gửi trước
đó) nếu bạn muốn tự tạo bảng trước bằng tay — nhưng KHÔNG bắt buộc: app tự
tạo bảng khi khởi động (`init_db()` trong `db.py`) nếu bảng chưa tồn tại.

## Bật làm giàu nội dung PDF bằng LLM (tùy chọn)

Mặc định app chạy 100% bằng luật, không gọi ra ngoài internet. Muốn phần lời
văn (nhận xét học tập, giải thích tổ hợp, gợi ý ngành nghề, đối chiếu ba
chiều) chi tiết/cá nhân hóa hơn, đặt 2 biến môi trường trỏ tới
[OpenRouter](https://openrouter.ai):

```bash
docker run -d -p 8000:8000 \
  -e OPENROUTER_API_KEY="sk-or-..." \
  -e OPENROUTER_MODEL="deepseek/deepseek-v4.1-flash" \
  --name huongnghiep3chieu huongnghiep3chieu
```

Lưu ý:
- Chỉ ảnh hưởng LỜI VĂN diễn giải — điểm số/mã Holland/tổ hợp/mức phù hợp vẫn
  do `engine.py` tính bằng luật, LLM không được đổi.
- Nếu không đặt `OPENROUTER_API_KEY`, hoặc gọi API lỗi/timeout, app tự dùng
  lại câu mẫu rule-based — không bao giờ chặn việc xuất PDF.
- Mỗi lượt nộp bài sẽ tốn một khoản phí nhỏ trên tài khoản OpenRouter (dữ
  liệu học sinh có được gửi ra ngoài tới OpenRouter/nhà cung cấp model khi
  bật tính năng này — cân nhắc trước khi bật với dữ liệu thật).
- Model reasoning (như DeepSeek) có thể tốn ~15-20 giây/lượt do model "suy
  nghĩ" trước khi trả JSON — đã tăng `max_tokens`/giới hạn `reasoning.max_tokens`
  trong `llm_narrative.py` để tránh bị cắt giữa chừng.

## Chạy không cần Docker (Python trực tiếp)

Cần cài font DejaVu để xuất PDF tiếng Việt có dấu đúng:

```bash
# Ubuntu/Debian
sudo apt-get install -y fonts-dejavu-core fonts-dejavu-extra

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Cấu trúc thư mục

```
main.py         - FastAPI app: API + phục vụ frontend tĩnh
data.py         - Ngân hàng 36 câu Holland + 3 nhóm giá trị + bảng ánh xạ ngành nghề
engine.py       - Chấm điểm + tam giác hóa (rule-based) + gọi llm_narrative.py làm giàu lời văn (tùy chọn)
llm_narrative.py - Gọi OpenRouter viết lại lời văn nhận xét chi tiết hơn; tự tắt nếu không có OPENROUTER_API_KEY
radar_gen.py    - Vẽ biểu đồ radar RIASEC (matplotlib)
pdf_gen.py      - Xuất PDF hồ sơ định hướng (reportlab)
db.py           - SQLAlchemy models (hoc_sinh, luot_test, diem_holland, gia_tri_nghe, bang_diem, ho_so_dinh_huong)
static/index.html - Frontend: bài test 6 chặng + xếp hạng giá trị + nhập điểm + tải PDF
```

## API chính

- `GET  /api/quiz` — trả về toàn bộ câu hỏi (frontend tự render, không hardcode)
- `POST /api/submit` — nộp bài, backend chấm + lưu DB + xuất PDF, trả về `pdf_url`
- `GET  /api/result/{id}` — xem lại kết quả JSON
- `GET  /api/result/{id}/pdf` — tải file PDF

## Giới hạn hiện tại (điểm nên nâng cấp tiếp)

- Bảng ánh xạ ngành nghề/tổ hợp trong `data.py` đã mở rộng thêm các tổ hợp
  chương trình 2018 và vài ngành "xu hướng 2026" (AI, bán dẫn, digital
  marketing...), nhưng đây vẫn là ảnh chụp tại một thời điểm — thị trường lao
  động thay đổi theo năm, nên rà soát lại định kỳ.
- Chưa có xác thực/đăng nhập cho giáo viên xem danh sách cả lớp — hiện mỗi lượt
  test chỉ trả PDF trực tiếp cho người vừa làm bài.
- Chưa tự động gửi email PDF cho `email_gvcn` — trường này mới chỉ được lưu vào
  DB, muốn gửi email cần thêm SMTP (ví dụ dùng `smtplib` hoặc dịch vụ ngoài).

# Hướng nghiệp 3 chiều — App tự host

App độc lập, KHÔNG cần Claude/n8n/Netlify để chạy. Học sinh làm test ngay trên
web (frontend `static/index.html`), backend FastAPI chấm điểm bằng luật cố định
(`engine.py`, dữ liệu ở `data.py`), lưu vào DB (`db.py`), và xuất PDF
(`pdf_gen.py` + `radar_gen.py`, dùng lại đúng thiết kế của skill gốc).

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
engine.py       - Chấm điểm + tam giác hóa (rule-based, không gọi AI)
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

- Bảng ánh xạ ngành nghề/tổ hợp trong `data.py` chỉ bao phủ các tổ hợp/khối phổ
  biến nhất (A00, A01, B00, C00, D01...) — có thể mở rộng thêm theo
  `references/to-hop-nganh.md` trong bộ skill gốc.
- Chưa có xác thực/đăng nhập cho giáo viên xem danh sách cả lớp — hiện mỗi lượt
  test chỉ trả PDF trực tiếp cho người vừa làm bài.
- Chưa tự động gửi email PDF cho `email_gvcn` — trường này mới chỉ được lưu vào
  DB, muốn gửi email cần thêm SMTP (ví dụ dùng `smtplib` hoặc dịch vụ ngoài).

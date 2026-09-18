# -*- coding: utf-8 -*-
import os
import datetime
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import init_db, get_session, HocSinh, LuotTest, DiemHolland, GiaTriNghe, BangDiem, HoSoDinhHuong
from data import HOLLAND_QUESTIONS, GIA_TRI_GROUPS
from engine import cham_holland, build_ho_so
from radar_gen import generate_radar
from pdf_gen import generate_pdf
from ocr_bang_diem import extract_diem_tu_file

OUTPUT_DIR = os.environ.get('OUTPUT_DIR', './output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="Hướng nghiệp 3 chiều — Trường Việt Anh")


@app.on_event("startup")
def _startup():
    init_db()


# ---------------------------------------------------------------
# API: dữ liệu bài test (để frontend tự render, không cần hardcode)
# ---------------------------------------------------------------
@app.get("/api/quiz")
def get_quiz():
    return {"holland": HOLLAND_QUESTIONS, "gia_tri_groups": GIA_TRI_GROUPS}


# ---------------------------------------------------------------
# API: nộp bài test -> chấm -> lưu DB -> xuất PDF
# ---------------------------------------------------------------
class SubmitPayload(BaseModel):
    ho_ten: str
    lop: str
    email_gvcn: str | None = None
    holland_answers: dict          # { "1": 3, "2": 4, ... }
    gia_tri_rankings: dict         # { "0": {"thu_nhap":1,...}, "1": {...}, "2": {...} }
    diem_mon: dict                 # { "Toán": 8.5, "Ngữ văn": 7, ... }


@app.post("/api/submit")
def submit(payload: SubmitPayload, db: Session = Depends(get_session)):
    hs = HocSinh(ho_ten=payload.ho_ten, lop=payload.lop, email_gvcn=payload.email_gvcn)
    db.add(hs)
    db.flush()

    lt = LuotTest(hoc_sinh_id=hs.id, trang_thai='hoan_thanh')
    db.add(lt)
    db.flush()

    h = cham_holland(payload.holland_answers)
    db.add(DiemHolland(luot_test_id=lt.id, r=h["scores"]["R"], i=h["scores"]["I"],
                        a=h["scores"]["A"], s=h["scores"]["S"], e=h["scores"]["E"],
                        c=h["scores"]["C"], ma_holland=h["ma_holland"]))
    lt.do_tin_cay = h["do_tin_cay"]

    for mon, diem in payload.diem_mon.items():
        db.add(BangDiem(luot_test_id=lt.id, mon_hoc=mon, diem=float(diem)))

    ngay = datetime.date.today().strftime("%d/%m/%Y")
    radar_path = os.path.join(OUTPUT_DIR, f"radar_{lt.id}.png")
    generate_radar(h["scores"], radar_path)

    ho_so_data = build_ho_so(payload.ho_ten, payload.lop, ngay,
                              payload.holland_answers, payload.gia_tri_rankings,
                              payload.diem_mon, radar_path)

    for gi, hang in enumerate(ho_so_data["gia_tri"]):
        db.add(GiaTriNghe(luot_test_id=lt.id, ten_gia_tri=hang[0], hang=int(hang[1])))

    pdf_path = os.path.join(OUTPUT_DIR, f"ho_so_{lt.id}.pdf")
    generate_pdf(ho_so_data, pdf_path)

    db.add(HoSoDinhHuong(luot_test_id=lt.id, du_lieu=ho_so_data, pdf_path=pdf_path))
    db.commit()

    return {
        "luot_test_id": lt.id,
        "ma_holland": h["ma_holland"],
        "do_tin_cay": h["do_tin_cay"],
        "pdf_url": f"/api/result/{lt.id}/pdf",
    }


# ---------------------------------------------------------------
# API: đọc bảng điểm từ ảnh/PDF tải lên (chỉ điền sẵn form, không tự nộp)
# ---------------------------------------------------------------
@app.post("/api/ocr-bang-diem")
async def ocr_bang_diem(file: UploadFile = File(...)):
    content = await file.read()
    return extract_diem_tu_file(content, file.filename, file.content_type)


@app.get("/api/result/{luot_test_id}")
def get_result(luot_test_id: int, db: Session = Depends(get_session)):
    ho_so = db.query(HoSoDinhHuong).filter_by(luot_test_id=luot_test_id).first()
    if not ho_so:
        raise HTTPException(404, "Không tìm thấy kết quả")
    return ho_so.du_lieu


@app.get("/api/result/{luot_test_id}/pdf")
def get_pdf(luot_test_id: int, db: Session = Depends(get_session)):
    ho_so = db.query(HoSoDinhHuong).filter_by(luot_test_id=luot_test_id).first()
    if not ho_so or not ho_so.pdf_path or not os.path.exists(ho_so.pdf_path):
        raise HTTPException(404, "Không tìm thấy file PDF")
    return FileResponse(ho_so.pdf_path, media_type="application/pdf",
                         filename=f"Ho_so_dinh_huong_{luot_test_id}.pdf")


# ---------------------------------------------------------------
# Frontend tĩnh
# ---------------------------------------------------------------
app.mount("/", StaticFiles(directory="static", html=True), name="static")

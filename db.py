# -*- coding: utf-8 -*-
import os
import datetime
from sqlalchemy import (create_engine, Column, Integer, String, Text, Boolean,
                         ForeignKey, DateTime, Numeric, JSON, UniqueConstraint, CheckConstraint)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./data.db')

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class HocSinh(Base):
    __tablename__ = 'hoc_sinh'
    id = Column(Integer, primary_key=True)
    ho_ten = Column(Text, nullable=False)
    lop = Column(Text, nullable=False)
    email_gvcn = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    luot_test = relationship('LuotTest', back_populates='hoc_sinh', cascade='all, delete-orphan')


class LuotTest(Base):
    __tablename__ = 'luot_test'
    id = Column(Integer, primary_key=True)
    hoc_sinh_id = Column(Integer, ForeignKey('hoc_sinh.id', ondelete='CASCADE'), nullable=False)
    ngay_test = Column(DateTime, default=datetime.datetime.utcnow)
    trang_thai = Column(Text, nullable=False, default='dang_lam')
    do_tin_cay = Column(Boolean)
    ghi_chu = Column(Text)

    hoc_sinh = relationship('HocSinh', back_populates='luot_test')
    diem_holland = relationship('DiemHolland', back_populates='luot_test', uselist=False, cascade='all, delete-orphan')
    gia_tri = relationship('GiaTriNghe', back_populates='luot_test', cascade='all, delete-orphan')
    bang_diem = relationship('BangDiem', back_populates='luot_test', cascade='all, delete-orphan')
    ho_so = relationship('HoSoDinhHuong', back_populates='luot_test', uselist=False, cascade='all, delete-orphan')


class DiemHolland(Base):
    __tablename__ = 'diem_holland'
    luot_test_id = Column(Integer, ForeignKey('luot_test.id', ondelete='CASCADE'), primary_key=True)
    r = Column(Integer, default=0)
    i = Column(Integer, default=0)
    a = Column(Integer, default=0)
    s = Column(Integer, default=0)
    e = Column(Integer, default=0)
    c = Column(Integer, default=0)
    ma_holland = Column(Text)

    luot_test = relationship('LuotTest', back_populates='diem_holland')


class GiaTriNghe(Base):
    __tablename__ = 'gia_tri_nghe'
    id = Column(Integer, primary_key=True)
    luot_test_id = Column(Integer, ForeignKey('luot_test.id', ondelete='CASCADE'), nullable=False)
    ten_gia_tri = Column(Text, nullable=False)
    hang = Column(Integer, nullable=False)  # hạng 1 trong từng nhóm giá trị (có thể có nhiều dòng hạng 1, mỗi dòng thuộc 1 nhóm khác nhau)

    luot_test = relationship('LuotTest', back_populates='gia_tri')


class BangDiem(Base):
    __tablename__ = 'bang_diem'
    id = Column(Integer, primary_key=True)
    luot_test_id = Column(Integer, ForeignKey('luot_test.id', ondelete='CASCADE'), nullable=False)
    mon_hoc = Column(Text, nullable=False)
    diem = Column(Numeric(4, 2), nullable=False)
    nhan_xet = Column(Text)

    luot_test = relationship('LuotTest', back_populates='bang_diem')


class HoSoDinhHuong(Base):
    __tablename__ = 'ho_so_dinh_huong'
    id = Column(Integer, primary_key=True)
    luot_test_id = Column(Integer, ForeignKey('luot_test.id', ondelete='CASCADE'), unique=True, nullable=False)
    du_lieu = Column(JSON, nullable=False)
    pdf_path = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    luot_test = relationship('LuotTest', back_populates='ho_so')


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

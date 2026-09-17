# -*- coding: utf-8 -*-
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                 Table, TableStyle, Image, Flowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = os.environ.get('FONT_DIR', '/usr/share/fonts/truetype/dejavu')
_FONTS_REGISTERED = False


def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont('Sans', FONT_DIR + '/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('Sans-B', FONT_DIR + '/DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Sans-I', FONT_DIR + '/DejaVuSans-Oblique.ttf'))
    pdfmetrics.registerFont(TTFont('Serif-B', FONT_DIR + '/DejaVuSerif-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Serif', FONT_DIR + '/DejaVuSerif.ttf'))
    _FONTS_REGISTERED = True


TEAL = colors.HexColor('#0F5C4D')
TEAL_D = colors.HexColor('#0A3F35')
AMBER = colors.HexColor('#B26B2C')
AMBER_L = colors.HexColor('#E8B96B')
CREAM = colors.HexColor('#FAF7F0')
SAND = colors.HexColor('#F0E9DA')
INK = colors.HexColor('#2B2A26')
MUTE = colors.HexColor('#6E6A5F')
LINE = colors.HexColor('#DED6C4')


def PS(name, **kw):
    kw.setdefault('fontName', 'Sans')
    return ParagraphStyle(name, **kw)


class SectionHead(Flowable):
    def __init__(self, num, title):
        Flowable.__init__(self)
        self.num = num
        self.title = title
        self.height = 17 * mm

    def wrap(self, aw, ah):
        self.width = aw
        return (aw, self.height)

    def draw(self):
        c = self.canv
        c.setFont('Serif-B', 30)
        c.setFillColor(AMBER)
        c.drawString(0, 4 * mm, self.num)
        c.setFont('Serif-B', 15)
        c.setFillColor(TEAL_D)
        c.drawString(15 * mm, 6.5 * mm, self.title)
        c.setStrokeColor(AMBER)
        c.setLineWidth(2)
        c.line(15 * mm, 3.5 * mm, 41 * mm, 3.5 * mm)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(45 * mm, 3.5 * mm, self.width, 3.5 * mm)


class Hero(Flowable):
    def __init__(self, hs):
        Flowable.__init__(self)
        self.hs = hs
        self.height = 34 * mm

    def wrap(self, aw, ah):
        self.width = aw
        return (aw, self.height)

    def draw(self):
        c = self.canv
        w = self.width
        h = self.height
        c.setFillColor(TEAL)
        c.roundRect(0, 0, w, h, 3 * mm, fill=1, stroke=0)
        c.setFont('Sans-B', 8)
        c.setFillColor(AMBER_L)
        c.drawString(9 * mm, h - 9 * mm, 'HỒ SƠ ĐỊNH HƯỚNG NGHỀ NGHIỆP')
        c.setFont('Serif-B', 19)
        c.setFillColor(CREAM)
        c.drawString(9 * mm, h - 19 * mm, self.hs['ho_ten'])
        c.setFont('Sans', 9)
        c.setFillColor(colors.HexColor('#CDE3DB'))
        c.drawString(9 * mm, h - 25.5 * mm, 'Lớp %s   ·   Ngày phân tích %s' % (self.hs['lop'], self.hs['ngay']))
        bw = 42 * mm
        c.setFillColor(TEAL_D)
        c.roundRect(w - bw - 8 * mm, 7 * mm, bw, h - 14 * mm, 2 * mm, fill=1, stroke=0)
        c.setFont('Sans-B', 7.5)
        c.setFillColor(AMBER_L)
        c.drawCentredString(w - bw / 2 - 8 * mm, h - 13 * mm, 'MÃ HOLLAND')
        c.setFont('Serif-B', 20)
        c.setFillColor(CREAM)
        c.drawCentredString(w - bw / 2 - 8 * mm, h - 23.5 * mm, self.hs['ma_holland'])


def _styled_table(data, colWidths, header_bg=TEAL, align_center_cols=None):
    t = Table(data, colWidths=colWidths)
    cmds = [('BACKGROUND', (0, 0), (-1, 0), header_bg), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SAND]),
            ('LINEBELOW', (0, 1), (-1, -2), 0.4, LINE), ('BOX', (0, 0), (-1, -1), 0.5, LINE),
            ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 7), ('RIGHTPADDING', (0, 0), (-1, -1), 7)]
    if align_center_cols:
        for cidx in align_center_cols:
            cmds.append(('ALIGN', (cidx, 0), (cidx, -1), 'CENTER'))
    t.setStyle(TableStyle(cmds))
    return t


def generate_pdf(hs: dict, out_path: str):
    _register_fonts()

    lead = PS('lead', fontSize=10.5, textColor=MUTE, leading=15.5, spaceAfter=2)
    cell = PS('cell', fontSize=9, textColor=INK, leading=12.5)
    cellb = PS('cellb', fontName='Sans-B', fontSize=9, textColor=INK, leading=12.5)
    hdr = PS('hdr', fontName='Sans-B', fontSize=8.5, textColor=CREAM, leading=11)
    note = PS('note', fontName='Sans-I', fontSize=9, textColor=MUTE, leading=13, spaceBefore=6)
    foot = PS('foot', fontSize=8, textColor=MUTE, leading=11)
    pa_h = PS('pa_h', fontName='Sans-B', fontSize=10, textColor=TEAL_D, leading=14, spaceBefore=6, spaceAfter=1)
    pa_b = PS('pa_b', fontSize=9.5, textColor=INK, leading=14.5, spaceAfter=5)

    def hc(t): return Paragraph(t, hdr)
    def bc(t): return Paragraph(t, cell)
    def bcb(t): return Paragraph(t, cellb)
    def tag(t, col): return Paragraph('<font color="%s"><b>%s</b></font>' % (col, t), cell)

    def decorate(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(CREAM)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, 0, 7 * mm, A4[1], fill=1, stroke=0)
        canvas.setFillColor(AMBER)
        canvas.rect(0, A4[1] - 60 * mm, 7 * mm, 32 * mm, fill=1, stroke=0)
        canvas.setFont('Sans', 7.5)
        canvas.setFillColor(MUTE)
        canvas.drawRightString(A4[0] - 16 * mm, 10 * mm, 'Hướng nghiệp 3 chiều · Trang %d' % doc.page)
        canvas.setFillColor(TEAL)
        canvas.drawString(16 * mm, 10 * mm, 'HỒ SƠ ĐỊNH HƯỚNG')
        canvas.restoreState()

    doc = BaseDocTemplate(out_path, pagesize=A4, topMargin=16 * mm, bottomMargin=16 * mm,
                           leftMargin=18 * mm, rightMargin=16 * mm)
    frame = Frame(18 * mm, 15 * mm, A4[0] - 18 * mm - 16 * mm, A4[1] - 16 * mm - 15 * mm, id='main',
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='all', frames=[frame], onPage=decorate)])
    story = []

    story.append(Hero(hs))
    story.append(Spacer(1, 7 * mm))

    story.append(SectionHead('01', 'Trắc nghiệm định hướng'))
    story.append(Paragraph('Kết quả bài test đầu vào gồm sở thích nghề (Holland / RIASEC) và giá trị nghề nghiệp em coi trọng.', lead))
    radar = Image(hs['radar_img'], width=80 * mm, height=84 * mm)
    htxt = Paragraph('<font color="#0A3F35"><b>Sở thích nghề (Holland / RIASEC)</b></font><br/>Mã nổi trội: <b>' + hs['ma_holland'] + '</b><br/><br/>' + hs['holland_detail'], cell)
    trow = Table([[radar, htxt]], colWidths=[84 * mm, 86 * mm])
    trow.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (0, 0), 6)]))
    story.append(trow)
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph('<font color="#0A3F35"><b>Giá trị nghề nghiệp</b></font>', PS('gv', fontName='Sans-B', fontSize=10.5, spaceAfter=4)))
    gv = [[hc('Giá trị trội'), hc('Hạng'), hc('Ý nghĩa')]]
    for a, b, cc in hs['gia_tri']:
        gv.append([bcb(a), bc(b), bc(cc)])
    story.append(_styled_table(gv, [45 * mm, 16 * mm, 113 * mm], header_bg=AMBER, align_center_cols=[1]))

    story.append(Spacer(1, 3 * mm))
    story.append(SectionHead('02', 'Đánh giá năng lực học thuật'))
    story.append(Paragraph('Năng lực thực tế qua bảng điểm — cho biết em <i>làm được</i> tổ hợp nào và ngành nào vừa sức.', lead))
    dd = [[hc('Môn học'), hc('Điểm'), hc('Nhận xét')]]
    for a, b, cc in hs['diem']:
        dd.append([bcb(a), bc(b), bc(cc)])
    story.append(_styled_table(dd, [40 * mm, 20 * mm, 114 * mm], header_bg=TEAL, align_center_cols=[1]))
    story.append(Paragraph('Nhận xét chung: ' + hs['nhan_xet_nl'], note))

    story.append(Spacer(1, 3 * mm))
    story.append(SectionHead('03', 'Đối chiếu ba chiều'))
    story.append(Paragraph('Đặt ba nguồn cạnh nhau để tìm hướng đồng thuận và điểm cần lưu ý:', lead))
    tg = [[hc('Chiều'), hc('Kết quả'), hc('Chỉ về')]]
    for a, b, cc in hs['tam_giac']:
        tg.append([bcb(a), bc(b), bc(cc)])
    story.append(_styled_table(tg, [42 * mm, 62 * mm, 70 * mm], header_bg=TEAL))
    story.append(Spacer(1, 3 * mm))
    for td, nd in hs['phan_tich_chi_tiet']:
        story.append(Paragraph(td, pa_h))
        story.append(Paragraph(nd, pa_b))

    story.append(Spacer(1, 2 * mm))
    story.append(SectionHead('04', 'Tổ hợp xét tuyển đề xuất'))
    UT = {'Chính': '#0F5C4D', 'Phụ': '#B26B2C', 'Dự phòng': '#6E6A5F'}
    th = [[hc('Tổ hợp'), hc('Môn'), hc('Tổng\nđiểm'), hc('Ưu tiên'), hc('Khối ngành mở ra')]]
    for a, b, tong, ut, khoi in hs['to_hop']:
        th.append([bcb(a), bc(b), bc(tong), tag(ut, UT.get(ut, '#2B2A26')), bc(khoi)])
    story.append(_styled_table(th, [18 * mm, 34 * mm, 16 * mm, 22 * mm, 84 * mm], header_bg=TEAL, align_center_cols=[2, 3]))
    story.append(Paragraph('Nhận xét: ' + hs['nhan_xet_th'], note))

    story.append(Spacer(1, 2 * mm))
    story.append(SectionHead('05', 'Nhóm ngành & nghề gợi ý'))
    MP = {'Rất phù hợp': '#2E7D5B', 'Phù hợp': '#2C6E8F', 'Cân nhắc': '#B26B2C'}
    nn = [[hc('Nhóm ngành'), hc('Nghề tiêu biểu'), hc('Công việc thực tế'), hc('Mức\nphù hợp')]]
    for a, b, cv, mp in hs['nganh_nghe']:
        nn.append([bcb(a), bc(b), bc(cv), tag(mp, MP.get(mp, '#2B2A26'))])
    story.append(_styled_table(nn, [40 * mm, 40 * mm, 66 * mm, 28 * mm], header_bg=TEAL, align_center_cols=[3]))
    story.append(Paragraph('Nhận xét: ' + hs['nhan_xet_nn'], note))

    story.append(Spacer(1, 2 * mm))
    story.append(SectionHead('06', 'Lưu ý'))
    for ly in hs['luu_y']:
        story.append(Paragraph('<font color="#B26B2C">▸</font>  ' + ly,
                                PS('bl', fontSize=9.5, textColor=INK, leading=14, leftIndent=6, spaceAfter=4)))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        'Hồ sơ được lập từ Quy trình Hướng nghiệp 3 chiều (sở thích Holland · giá trị nghề · năng lực học thuật). '
        'Đây là tài liệu định hướng tham khảo, không thay thế tư vấn chuyên sâu hoặc quyết định của gia đình.', foot))

    doc.build(story)
    return out_path

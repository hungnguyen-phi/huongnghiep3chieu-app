# -*- coding: utf-8 -*-
"""
Engine tam giác hóa: Holland + Giá trị nghề + Bảng điểm -> hồ sơ định hướng.
Toàn bộ chạy bằng luật (rule-based), không gọi AI/Claude — để chạy độc lập
trên server tự host.
"""
from data import (
    HOLLAND_LABEL, TO_HOP, KHOI_NGANH, GIA_TRI_MOI_TRUONG, BAY_PAIRS,
)


def cham_holland(answers: dict) -> dict:
    """answers: {question_id(int): diem(0-4)}. Trả về điểm 6 nhóm + mã Holland."""
    from data import HOLLAND_QUESTIONS
    scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    for q in HOLLAND_QUESTIONS:
        v = int(answers.get(str(q["id"]), answers.get(q["id"], 0)) or 0)
        scores[q["nhom"]] += v

    # câu bẫy: nếu CẢ HAI cặp lệch >=3 -> cảnh báo độ tin cậy
    do_tin_cay = True
    for a, b in BAY_PAIRS:
        va = int(answers.get(str(a), answers.get(a, 0)) or 0)
        vb = int(answers.get(str(b), answers.get(b, 0)) or 0)
        if abs(va - vb) >= 3:
            do_tin_cay = False
        else:
            do_tin_cay = do_tin_cay and True
    # chỉ hạ cờ khi CẢ HAI cặp lệch mạnh
    lech = []
    for a, b in BAY_PAIRS:
        va = int(answers.get(str(a), answers.get(a, 0)) or 0)
        vb = int(answers.get(str(b), answers.get(b, 0)) or 0)
        lech.append(abs(va - vb) >= 3)
    do_tin_cay = not all(lech)

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    top3 = ranked[:3]
    ma_holland = " · ".join(k for k, _ in top3)

    chi_tiet = []
    for k, v in top3:
        chi_tiet.append(f"{k} ({HOLLAND_LABEL[k]}) = {v}/24")
    lows = ranked[3:]
    if lows:
        chi_tiet.append(
            "Ba nhóm còn lại thấp hơn ("
            + ", ".join(f"{k}={v}" for k, v in lows)
            + ") → chân dung sở thích tương đối rõ."
            if (top3[0][1] - lows[0][1]) >= 4
            else "Điểm các nhóm khá gần nhau → sở thích còn trải rộng, nên trải nghiệm thêm trước khi chốt."
        )
    holland_detail = "<br/>".join(chi_tiet)

    return {
        "scores": scores,
        "ma_holland": ma_holland,
        "top3": [k for k, _ in top3],
        "holland_detail": holland_detail,
        "do_tin_cay": do_tin_cay,
    }


def cham_gia_tri(rankings: dict) -> list:
    """rankings: {group_index: {item_key: hang(1|2|3)}}. Trả về list giá trị trội (hạng 1) theo 3 nhóm."""
    from data import GIA_TRI_GROUPS
    out = []
    for gi, group in enumerate(GIA_TRI_GROUPS):
        ranks = rankings.get(str(gi), rankings.get(gi, {}))
        # tìm item có hạng 1 trong nhóm này
        hang1_key = None
        for item in group["items"]:
            hang = int(ranks.get(item["key"], 0) or 0)
            if hang == 1:
                hang1_key = item
                break
        if hang1_key:
            y_nghia = {
                "Thu nhập": "Muốn công việc mang lại đời sống vật chất tốt.",
                "Ổn định": "Ưu tiên sự chắc chắn, an toàn nghề nghiệp lâu dài.",
                "Danh tiếng": "Coi trọng vị thế và sự công nhận của xã hội.",
                "Sáng tạo": "Muốn được tự do nghĩ và làm điều mới.",
                "Tự chủ": "Muốn tự quyết định cách làm việc của mình.",
                "Thử thách": "Muốn liên tục học hỏi, phát triển bản thân.",
                "Giúp người": "Muốn công việc tạo tác động tích cực lên con người/xã hội.",
                "Cân bằng": "Ưu tiên có thời gian riêng ngoài công việc.",
                "Môi trường": "Coi trọng làm việc trong môi trường yêu thích.",
            }.get(hang1_key["gia_tri"], "")
            out.append([hang1_key["gia_tri"], "1", y_nghia])
    return out


def tinh_to_hop(diem_mon: dict) -> list:
    """diem_mon: {ten_mon: diem(float)}. Trả về danh sách tổ hợp tính được điểm, sắp theo tổng điểm giảm dần."""
    ket_qua = []
    for ma, info in TO_HOP.items():
        mons = info["mon"]
        if all(m in diem_mon for m in mons):
            tong = sum(float(diem_mon[m]) for m in mons)
            ket_qua.append({
                "ma": ma, "mon": ", ".join(mons), "tong": round(tong, 1),
                "khoi": info["khoi"], "holland": info["holland"],
            })
    ket_qua.sort(key=lambda x: -x["tong"])
    return ket_qua


def xep_uu_tien(to_hop_list: list, top3_holland: list) -> list:
    """Gắn nhãn Chính/Phụ/Dự phòng: ưu tiên tổ hợp vừa điểm cao vừa khớp Holland top3."""
    if not to_hop_list:
        return []
    scored = []
    for th in to_hop_list:
        match = len(set(th["holland"]) & set(top3_holland))
        scored.append((th, match))
    scored.sort(key=lambda x: (-x[1], -x[0]["tong"]))
    nhan = ["Chính", "Phụ", "Dự phòng"]
    out = []
    for i, (th, _match) in enumerate(scored[:3]):
        out.append([th["ma"], th["mon"], str(th["tong"]),
                    nhan[i] if i < len(nhan) else "Tham khảo",
                    KHOI_NGANH[th["khoi"]]["nhom_nganh"]])
    return out


def goi_y_nganh_nghe(top3_holland: list, gia_tri_troi: list, to_hop_list: list) -> list:
    """Gộp nhóm ngành theo khối của các tổ hợp khả thi nhất, đánh dấu mức phù hợp."""
    khoi_gap = {}
    for th in to_hop_list[:3]:
        khoi_gap.setdefault(th["khoi"], 0)
        khoi_gap[th["khoi"]] += 1

    out = []
    for khoi, _cnt in sorted(khoi_gap.items(), key=lambda x: -x[1]):
        info = KHOI_NGANH.get(khoi)
        if not info:
            continue
        for nhom_nganh, nghe, cv in info["nghe"]:
            match_holland = len(set(TO_HOP_KHOI_HOLLAND(khoi)) & set(top3_holland))
            muc = "Rất phù hợp" if match_holland >= 2 else ("Phù hợp" if match_holland == 1 else "Cân nhắc")
            out.append([nhom_nganh, nghe, cv, muc])
    return out[:4] if out else []


def TO_HOP_KHOI_HOLLAND(khoi: str) -> list:
    hset = set()
    for info in TO_HOP.values():
        if info["khoi"] == khoi:
            hset.update(info["holland"])
    return list(hset)


def bang_tam_giac(top3_holland: list, gia_tri_troi: list, to_hop_list: list) -> list:
    """3 hàng bảng 'Đối chiếu ba chiều': [Chiều, Kết quả, Chỉ về]."""
    ten_gt = [g[0] for g in gia_tri_troi]
    row1 = [
        f"Thích gì ({' · '.join(top3_holland)})",
        ", ".join(HOLLAND_LABEL[k] for k in top3_holland),
        "Nhóm nghề khớp mã Holland trên",
    ]
    row2 = [
        "Coi trọng gì",
        ", ".join(ten_gt) if ten_gt else "Chưa xác định rõ",
        "; ".join(GIA_TRI_MOI_TRUONG.get(g, "") for g in ten_gt) if ten_gt else "",
    ]
    if to_hop_list:
        top_mons = ", ".join(f"{t['ma']} ({t['tong']}đ)" for t in to_hop_list[:2])
        row3 = ["Làm được gì", top_mons, "Các tổ hợp khả thi theo điểm hiện tại"]
    else:
        row3 = ["Làm được gì", "Chưa đủ dữ liệu điểm", "Cần nhập bảng điểm đầy đủ hơn"]
    return [row1, row2, row3]


def phan_tich_mau_thuan(top3_holland: list, gia_tri_troi: list, to_hop_list: list) -> list:
    """Sinh 3 mục 'Đối chiếu ba chiều' (điểm đồng thuận / cần cân nhắc / gợi ý hành động)."""
    ten_gt = [g[0] for g in gia_tri_troi]
    dong_thuan = (
        f"Nhóm sở thích trội ({' · '.join(top3_holland)}) và giá trị nghề "
        f"({', '.join(ten_gt) if ten_gt else 'chưa rõ'}) "
    )
    if to_hop_list:
        best = to_hop_list[0]
        dong_thuan += f"khớp khá tốt với năng lực học tập hiện tại (tổ hợp mạnh nhất: {best['ma']}, {best['tong']} điểm)."
    else:
        dong_thuan += "nhưng chưa đủ dữ liệu điểm các môn để tính tổ hợp cụ thể — cần bổ sung bảng điểm đầy đủ hơn."

    can_nhac = (
        "Sở thích (Holland) và giá trị nghề cho biết em NÊN đi hướng nào; bảng điểm cho biết em ĐI ĐƯỢC tổ hợp nào. "
        "Nếu hai chiều lệch nhau (thích một hướng nhưng điểm chưa đủ, hoặc điểm mạnh một môn nhưng không thích), "
        "nên ưu tiên sở thích/giá trị và có lộ trình cải thiện điểm, thay vì chọn ngành chỉ vì \"học được\"."
    )

    hanh_dong = (
        "Trải nghiệm thực tế (tham quan, hoạt động ngoại khóa, tình nguyện) đúng nhóm ngành gợi ý bên dưới "
        "trong năm học tới để kiểm chứng hứng thú trước khi chốt ngành, đồng thời theo dõi đề án tuyển sinh "
        "thực tế của trường đại học mục tiêu vì tổ hợp xét tuyển có thể thay đổi theo năm."
    )

    return [
        ["Điểm đồng thuận", dong_thuan],
        ["Điểm cần cân nhắc", can_nhac],
        ["Gợi ý hành động", hanh_dong],
    ]


def build_ho_so(ho_ten: str, lop: str, ngay: str,
                 holland_answers: dict, gia_tri_rankings: dict,
                 diem_mon: dict, radar_img_path: str) -> dict:
    """Hàm chính: build toàn bộ dict HS đúng schema hs_data_mau.json cho tao_pdf.py."""
    h = cham_holland(holland_answers)
    gia_tri_troi = cham_gia_tri(gia_tri_rankings)
    to_hop_list = tinh_to_hop(diem_mon)
    to_hop_uu_tien = xep_uu_tien(to_hop_list, h["top3"])
    nganh_nghe = goi_y_nganh_nghe(h["top3"], gia_tri_troi, to_hop_list)
    tam_giac = bang_tam_giac(h["top3"], gia_tri_troi, to_hop_list)
    phan_tich_chi_tiet = phan_tich_mau_thuan(h["top3"], gia_tri_troi, to_hop_list)

    diem_rows = []
    for mon, d in diem_mon.items():
        d = float(d)
        nhan_xet = "Mạnh" if d >= 8 else ("Khá" if d >= 6.5 else "Cần cải thiện")
        diem_rows.append([mon, str(d), nhan_xet])

    manh = [m for m, d in diem_mon.items() if float(d) >= 8]
    yeu = [m for m, d in diem_mon.items() if float(d) < 6.5]
    nhan_xet_nl = "Nền học tập "
    nhan_xet_nl += ("đều và vững" if not yeu else f"cần lưu ý ở {', '.join(yeu)}")
    if manh:
        nhan_xet_nl += f"; nổi trội ở {', '.join(manh)}."
    else:
        nhan_xet_nl += "."

    nhan_xet_th = (
        f"Tổ hợp {to_hop_uu_tien[0][0]} là lựa chọn ưu tiên vì cân bằng giữa điểm số và mã Holland "
        f"({h['ma_holland']})." if to_hop_uu_tien else
        "Chưa đủ dữ liệu điểm để xếp ưu tiên tổ hợp — hãy nhập đầy đủ hơn bảng điểm các môn tổ hợp phổ biến."
    )
    nhan_xet_nn = (
        "Nhóm ngành đầu bảng khớp cả sở thích lẫn năng lực; các nhóm 'Cân nhắc' cần trải nghiệm thêm trước khi quyết định."
    )

    luu_y = [
        "Đây là gợi ý định hướng dựa trên dữ liệu test + điểm; quyết định cuối thuộc về em và gia đình.",
        "Tổ hợp xét tuyển mỗi trường mỗi khác và thay đổi theo năm — kiểm chứng lại với đề án tuyển sinh trường đích.",
    ]
    if not h["do_tin_cay"]:
        luu_y.insert(0, "Một số câu trả lời chưa nhất quán (câu kiểm chứng lệch nhiều) — nên trò chuyện thêm với học sinh trước khi dùng kết quả này.")

    return {
        "ho_ten": ho_ten,
        "lop": lop,
        "ngay": ngay,
        "ma_holland": h["ma_holland"],
        "radar_img": radar_img_path,
        "holland_detail": h["holland_detail"],
        "gia_tri": gia_tri_troi,
        "diem": diem_rows,
        "nhan_xet_nl": nhan_xet_nl,
        "tam_giac": tam_giac,
        "phan_tich_chi_tiet": phan_tich_chi_tiet,
        "to_hop": to_hop_uu_tien,
        "nhan_xet_th": nhan_xet_th,
        "nganh_nghe": nganh_nghe,
        "nhan_xet_nn": nhan_xet_nn,
        "luu_y": luu_y,
        "_scores": h["scores"],
        "_do_tin_cay": h["do_tin_cay"],
    }

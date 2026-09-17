# -*- coding: utf-8 -*-
"""
Ngân hàng câu hỏi + bảng ánh xạ nghề nghiệp, rút từ SKILL huong-nghiep-3-chieu.
Không phụ thuộc Claude — mọi logic ở đây chạy độc lập.
"""

# ---------------------------------------------------------------
# 36 câu Holland, chia 6 chặng x 6 câu (đã trộn nhóm theo skill gốc)
# nhom: R I A S E C
# ---------------------------------------------------------------
HOLLAND_QUESTIONS = [
    {"id": 1,  "chang": 1, "nhom": "R", "text": "Lắp ráp hoặc sửa một món đồ điện, máy móc bị hỏng."},
    {"id": 2,  "chang": 1, "nhom": "I", "text": "Giải một câu đố logic hoặc bài toán khó hóc búa."},
    {"id": 3,  "chang": 1, "nhom": "A", "text": "Viết một câu chuyện, bài thơ, hoặc kịch bản."},
    {"id": 4,  "chang": 1, "nhom": "S", "text": "Giúp một người bạn đang buồn cảm thấy khá hơn."},
    {"id": 5,  "chang": 1, "nhom": "E", "text": "Thuyết phục cả nhóm làm theo kế hoạch của em."},
    {"id": 6,  "chang": 1, "nhom": "C", "text": "Sắp xếp lại toàn bộ tài liệu, dữ liệu cho gọn gàng, ngăn nắp."},
    {"id": 7,  "chang": 2, "nhom": "R", "text": "Tự tay chế tạo, lắp ráp một thứ gì đó (mô hình, đồ dùng)."},
    {"id": 8,  "chang": 2, "nhom": "I", "text": "Tìm hiểu tận gốc vì sao một hiện tượng khoa học xảy ra."},
    {"id": 9,  "chang": 2, "nhom": "A", "text": "Vẽ, thiết kế, chỉnh ảnh, hoặc trang trí."},
    {"id": 10, "chang": 2, "nhom": "S", "text": "Hướng dẫn, chỉ bài lại cho em nhỏ hoặc bạn bè."},
    {"id": 11, "chang": 2, "nhom": "E", "text": "Bày ra và tổ chức một hoạt động, sự kiện nhỏ."},
    {"id": 12, "chang": 2, "nhom": "C", "text": "Lập kế hoạch chi tiết cho một việc và theo dõi tiến độ."},
    {"id": 13, "chang": 3, "nhom": "R", "text": "Vận hành thiết bị, chơi thể thao, hoạt động ngoài trời."},
    {"id": 14, "chang": 3, "nhom": "I", "text": "Làm thí nghiệm, phân tích số liệu, kiểm chứng giả thuyết."},
    {"id": 15, "chang": 3, "nhom": "A", "text": "Chơi nhạc, hát, quay dựng video, làm nội dung sáng tạo."},
    {"id": 16, "chang": 3, "nhom": "S", "text": "Tham gia tình nguyện, giúp đỡ cộng đồng."},
    {"id": 17, "chang": 3, "nhom": "E", "text": "Tranh luận để giành phần thắng, đặt mục tiêu cạnh tranh."},
    {"id": 18, "chang": 3, "nhom": "C", "text": "Kiểm tra kỹ để mọi thứ chính xác đến từng chi tiết."},
    {"id": 19, "chang": 4, "nhom": "R", "text": "Xử lý một sự cố kỹ thuật thực tế (điện, nước, máy tính)."},
    {"id": 20, "chang": 4, "nhom": "I", "text": "Nghiên cứu một chủ đề khó đến khi hiểu thật sâu."},
    {"id": 21, "chang": 4, "nhom": "A", "text": "Nghĩ ra ý tưởng mới, cách làm khác lạ chưa ai làm."},
    {"id": 22, "chang": 4, "nhom": "S", "text": "Lắng nghe và hòa giải khi bạn bè có mâu thuẫn."},
    {"id": 23, "chang": 4, "nhom": "E", "text": "Đứng trước lớp trình bày, hùng biện, dẫn dắt."},
    {"id": 24, "chang": 4, "nhom": "C", "text": "Quản lý sổ sách, con số, tài chính một cách chính xác."},
    {"id": 25, "chang": 5, "nhom": "R", "text": "Làm việc với dụng cụ, máy móc hơn là với giấy tờ."},
    {"id": 26, "chang": 5, "nhom": "I", "text": "Tìm quy luật ẩn sau các con số và sự việc."},
    {"id": 27, "chang": 5, "nhom": "A", "text": "Được tự do thể hiện cá tính, không thích khuôn mẫu cứng."},
    {"id": 28, "chang": 5, "nhom": "S", "text": "Chăm sóc sức khỏe, tinh thần cho người khác."},
    {"id": 29, "chang": 5, "nhom": "E", "text": "Khởi xướng một dự án mới và chịu trách nhiệm về nó."},
    {"id": 30, "chang": 5, "nhom": "C", "text": "Làm việc theo quy trình, quy tắc rõ ràng, ổn định."},
    {"id": 31, "chang": 6, "nhom": "R", "text": "Thích tháo lắp, tìm hiểu cấu tạo bên trong của thiết bị."},
    {"id": 32, "chang": 6, "nhom": "I", "text": "Say mê đọc và tìm hiểu kiến thức mới chuyên sâu."},
    {"id": 33, "chang": 6, "nhom": "A", "text": "Có gu thẩm mỹ, để ý cái đẹp trong mọi thứ xung quanh."},
    {"id": 34, "chang": 6, "nhom": "S", "text": "Được người khác tin tưởng tâm sự, tìm đến khi cần giúp."},
    {"id": 35, "chang": 6, "nhom": "E", "text": "Dám nhận việc khó, thích dẫn dắt và tạo ảnh hưởng."},
    {"id": 36, "chang": 6, "nhom": "C", "text": "Thoải mái với công việc lặp lại, cần sự tỉ mỉ, kiên nhẫn."},
]

# Cặp câu bẫy kiểm chứng độ tin cậy (cùng nhóm, khác diễn đạt)
BAY_PAIRS = [(1, 19), (14, 26)]

# ---------------------------------------------------------------
# 3 nhóm giá trị nghề, mỗi nhóm 3 ý, HS xếp hạng 1-2-3
# ---------------------------------------------------------------
GIA_TRI_GROUPS = [
    {
        "nhom": "Điều em mong nghề nghiệp mang lại",
        "items": [
            {"key": "thu_nhap",  "label": "Thu nhập cao, đời sống vật chất tốt", "gia_tri": "Thu nhập"},
            {"key": "on_dinh",   "label": "Công việc ổn định, chắc chắn, ít rủi ro", "gia_tri": "Ổn định"},
            {"key": "danh_tieng","label": "Được xã hội tôn trọng, có địa vị", "gia_tri": "Danh tiếng"},
        ],
    },
    {
        "nhom": "Cách em muốn làm việc",
        "items": [
            {"key": "sang_tao",  "label": "Được tự do sáng tạo, nghĩ và làm điều mới", "gia_tri": "Sáng tạo"},
            {"key": "tu_chu",    "label": "Được tự quyết, chủ động cách làm của mình", "gia_tri": "Tự chủ"},
            {"key": "thu_thach", "label": "Liên tục được thử thách, học hỏi, phát triển", "gia_tri": "Thử thách"},
        ],
    },
    {
        "nhom": "Ý nghĩa em tìm kiếm",
        "items": [
            {"key": "giup_nguoi", "label": "Giúp ích cho con người, cho cộng đồng", "gia_tri": "Giúp người"},
            {"key": "can_bang",   "label": "Cân bằng công việc và cuộc sống, có thời gian riêng", "gia_tri": "Cân bằng"},
            {"key": "moi_truong", "label": "Làm việc trong môi trường mình yêu thích", "gia_tri": "Môi trường"},
        ],
    },
]

# ---------------------------------------------------------------
# Mô tả 6 nhóm Holland (dùng để build câu văn "holland_detail")
# ---------------------------------------------------------------
HOLLAND_LABEL = {
    "R": "Kỹ thuật (Realistic)", "I": "Nghiên cứu (Investigative)",
    "A": "Sáng tạo (Artistic)", "S": "Xã hội (Social)",
    "E": "Quản lý (Enterprising)", "C": "Quy củ (Conventional)",
}

# ---------------------------------------------------------------
# Tổ hợp xét tuyển phổ biến: mã -> (danh sách môn, khối, nhóm Holland hợp)
# ---------------------------------------------------------------
TO_HOP = {
    "A00": {"mon": ["Toán", "Vật lí", "Hóa học"], "khoi": "A", "holland": ["I", "R", "C"]},
    "A01": {"mon": ["Toán", "Vật lí", "Tiếng Anh"], "khoi": "A", "holland": ["I", "R", "C"]},
    "A02": {"mon": ["Toán", "Vật lí", "Sinh học"], "khoi": "A", "holland": ["I", "R"]},
    "B00": {"mon": ["Toán", "Hóa học", "Sinh học"], "khoi": "B", "holland": ["I", "S", "R"]},
    "B08": {"mon": ["Toán", "Sinh học", "Tiếng Anh"], "khoi": "B", "holland": ["I", "S"]},
    "C00": {"mon": ["Ngữ văn", "Lịch sử", "Địa lí"], "khoi": "C", "holland": ["S", "A", "E"]},
    "C14": {"mon": ["Ngữ văn", "Toán", "GDKT&PL"], "khoi": "C", "holland": ["S", "E"]},
    "D01": {"mon": ["Toán", "Ngữ văn", "Tiếng Anh"], "khoi": "D", "holland": ["E", "C", "A", "S"]},
    "D07": {"mon": ["Toán", "Hóa học", "Tiếng Anh"], "khoi": "D", "holland": ["I", "C"]},
    "D08": {"mon": ["Toán", "Sinh học", "Tiếng Anh"], "khoi": "D", "holland": ["I", "S"]},
    "D09": {"mon": ["Toán", "Lịch sử", "Tiếng Anh"], "khoi": "D", "holland": ["E", "C"]},
    "D14": {"mon": ["Ngữ văn", "Lịch sử", "Tiếng Anh"], "khoi": "D", "holland": ["S", "A"]},
}

# ---------------------------------------------------------------
# Khối -> nhóm ngành / nghề tương lai (mục 2, to-hop-nganh.md)
# ---------------------------------------------------------------
KHOI_NGANH = {
    "A": {
        "nhom_nganh": "Kỹ thuật, Công nghệ thông tin, Khoa học dữ liệu / AI, Vật lí kỹ thuật, Kinh tế - Tài chính",
        "nghe": [
            ("Kỹ thuật & Công nghệ", "Kỹ sư phần mềm / AI / dữ liệu, kỹ sư cơ khí-điện-xây dựng",
             "Thiết kế, lập trình, vận hành hệ thống kỹ thuật hoặc phần mềm"),
            ("Tài chính - Kinh tế lượng", "Chuyên viên phân tích tài chính, kiểm toán định lượng",
             "Phân tích số liệu, mô hình hóa rủi ro, đầu tư"),
        ],
    },
    "B": {
        "nhom_nganh": "Y khoa, Dược, Điều dưỡng, Công nghệ sinh học, Nông - Lâm - Thủy sản",
        "nghe": [
            ("Y - Dược - Chăm sóc sức khỏe", "Bác sĩ, dược sĩ, điều dưỡng, kỹ thuật viên xét nghiệm",
             "Khám chữa bệnh, tư vấn dùng thuốc, chăm sóc người bệnh"),
            ("Khoa học sự sống", "Nghiên cứu viên sinh học, kỹ sư công nghệ sinh học",
             "Nghiên cứu phòng lab, phát triển sản phẩm sinh học"),
        ],
    },
    "C": {
        "nhom_nganh": "Luật, Báo chí - Truyền thông, Sư phạm, Tâm lí học, Công tác xã hội",
        "nghe": [
            ("Sư phạm - Tâm lí - CTXH", "Giáo viên, chuyên viên tâm lí học đường, cán bộ CTXH",
             "Giảng dạy, tư vấn tâm lí, hỗ trợ nhóm yếu thế"),
            ("Luật - Truyền thông", "Luật sư, nhà báo, chuyên viên truyền thông/PR",
             "Tư vấn pháp lý, sản xuất nội dung, quan hệ công chúng"),
        ],
    },
    "D": {
        "nhom_nganh": "Kinh tế, Quản trị kinh doanh, Marketing, Ngôn ngữ, Du lịch - Khách sạn",
        "nghe": [
            ("Kinh doanh - Marketing", "Chuyên viên marketing, kinh doanh, tài chính - ngân hàng",
             "Xây dựng thương hiệu, bán hàng, tư vấn tài chính"),
            ("Ngôn ngữ - Quốc tế", "Biên - phiên dịch, giáo viên ngoại ngữ, quản lí du lịch",
             "Dịch thuật, giảng dạy ngoại ngữ, điều hành tour/khách sạn"),
        ],
    },
}

# ---------------------------------------------------------------
# Giá trị trội -> môi trường/ngành nghiêng về (mục 6, to-hop-nganh.md)
# ---------------------------------------------------------------
GIA_TRI_MOI_TRUONG = {
    "Thu nhập":   "Tài chính, CNTT, y dược, kinh doanh",
    "Ổn định":    "Sư phạm, công chức, kế toán, kỹ thuật hạ tầng, y tế công",
    "Danh tiếng": "Y, luật, ngoại giao, ngành top cạnh tranh",
    "Sáng tạo":   "Thiết kế, truyền thông, kiến trúc, R&D, khởi nghiệp",
    "Tự chủ":     "Khởi nghiệp, nghề tự do, chuyên gia, freelance sáng tạo",
    "Thử thách":  "Công nghệ, nghiên cứu, khởi nghiệp, tư vấn",
    "Giúp người": "Y, điều dưỡng, sư phạm, công tác xã hội, tâm lí, luật",
    "Cân bằng":   "Hành chính, kế toán, một số nghề kỹ thuật, giáo dục",
    "Môi trường": "Tùy sở thích cụ thể (con người / dữ liệu / thiên nhiên)",
}

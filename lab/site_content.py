"""Nội dung tri thức có cấu trúc cho trang sơ đồ cây của Phòng R&D (bản nghiên cứu nền W46/2026).
Mỗi nút: id (ASCII), title, kind, agent (người phụ trách), html (chi tiết), links, children.
Báo cáo tuần mới trong reports/ được lab/site.py tự thêm vào cây, không cần sửa file này."""


def N(id, title, kind="topic", agent=None, html="", links=None, children=None, summary=""):
    return {"id": id, "title": title, "kind": kind, "agent": agent, "html": html.strip(),
            "links": links or [], "children": children or [], "summary": summary}


TEAM = [
    {"key": "director", "name": "Minh", "role": "Trưởng phòng – Điều phối & Tổng hợp",
     "task": "Duyệt lộ trình nghiên cứu 5 giai đoạn",
     "look": {"skin": "#E9B98F", "hair": "#2B2118", "style": "side", "shirt": "#1F3A5F", "glasses": True}},
    {"key": "standards", "name": "Lan", "role": "Tiêu chuẩn & Kiến trúc DT",
     "task": "Đọc CIGRE TB 995 và ISO/IEC 30173",
     "look": {"skin": "#F1C7A1", "hair": "#3A2A20", "style": "bun", "shirt": "#3E7C74", "glasses": False}},
    {"key": "physics", "name": "Hùng", "role": "Mô hình vật lý thiết bị",
     "task": "Hiệu chỉnh mô hình nhiệt IEC 60076-7",
     "look": {"skin": "#D9A27A", "hair": "#1C1A17", "style": "short", "shirt": "#B5651D", "glasses": True}},
    {"key": "data_ai", "name": "Vy", "role": "Dữ liệu & AI",
     "task": "Thiết kế Health Index v1 (CIGRE TB 761)",
     "look": {"skin": "#F3CDAA", "hair": "#4A2E22", "style": "long", "shirt": "#6B5BA6", "glasses": False}},
    {"key": "ot_cyber", "name": "Tuấn", "role": "Hạ tầng OT/IoT & An ninh mạng",
     "task": "Lập danh mục tín hiệu IEC 61850 / 104",
     "look": {"skin": "#C99470", "hair": "#141414", "style": "buzz", "shirt": "#2F4F4F", "glasses": False}},
    {"key": "substation", "name": "Nam", "role": "Substation DT (trạm 110 kV)",
     "task": "Dựng mô hình trạm từ file SCD",
     "look": {"skin": "#E2AE86", "hair": "#2A1E16", "style": "short", "shirt": "#48709A", "glasses": False}},
    {"key": "benchmark", "name": "Thảo", "role": "Benchmark quốc tế & trong nước",
     "task": "Lập battlecard 12 hãng Transformer DT",
     "look": {"skin": "#F0C29C", "hair": "#2E1F18", "style": "bob", "shirt": "#9A4D6A", "glasses": True}},
    {"key": "vn_market", "name": "Hà", "role": "Thị trường, Chính sách & Triển khai VN",
     "task": "Rà soát Luật Dữ liệu và hồ sơ mời thầu EVN",
     "look": {"skin": "#E6B48C", "hair": "#3B2618", "style": "long", "shirt": "#5E7D3A", "glasses": False}},
]

CIGRE995 = ("CIGRE TB 995 (Electra 08/2026)",
            "https://electra.cigre.org/347-august-2026/technical-brochures/digital-twins-for-power-transformers-concept-and-future-perspectives")

# ---------------------------------------------------------------- Báo cáo #1
summary = N("bc1-tom-tat", "Tóm tắt điều hành", "section", "director", """
<p><b>Kết luận:</b> DT cho thiết bị điện, nhất là máy biến áp, đã là thị trường thương mại. Ở Việt Nam đã có nhu cầu thật và đã có hãng ngoại chiếm vị trí. Cơ hội của VTI nằm ở <b>lớp mô hình và phân tích trung lập với hãng thiết bị, triển khai on-premise</b>.</p>""", children=[
    N("k1-thi-truong", "Thị trường ~3,1 tỷ USD, tăng ~9%/năm", "finding", "benchmark", """
<p>Thị trường hệ thống giám sát MBA khoảng 3,10 tỷ USD năm 2025, dự báo tăng khoảng 9,2%/năm. Châu Á – Thái Bình Dương tăng nhanh nhất (khoảng 10,3%/năm). DGA chiếm 48% giá trị, đơn vị điện lực chiếm 62%.</p>""",
      [("Straits Research", "https://straitsresearch.com/de/report/transformer-monitoring-systems-market")]),
    N("k2-hang-lon", "Hãng lớn đều đã có sản phẩm", "finding", "benchmark", """
<p>Hitachi Energy, Siemens Energy, Reinhausen, GE Vernova, Camlin, Qualitrol, Dynamic Ratings và Weidmann đều bán gói cảm biến + thiết bị thu thập + phần mềm APM. Chỉ số ít có mô hình vật lý riêng cho từng máy (Siemens Sensformer Advanced). Phần lớn dừng ở mức chẩn đoán.</p>"""),
    N("k3-tien-le-vn", "Việt Nam đã có tiền lệ (GE tại EVNNPT)", "finding", "vn_market", """
<p>EVNNPT đã lắp GE MS3000 cho MBA 500 kV tại Phú Lâm, Pleiku 2, Đà Nẵng và Hiệp Hòa, quản lý tập trung qua Perception Server. Nhiệt điện Vũng Áng 1 đã mời chào hệ thống giám sát online kèm quản lý tài sản MBA.</p>""",
      [("Tạp chí Công Thương", "https://tapchicongthuong.vn/evnnpt-giam-sat--chan-doan-tinh-trang-may-bien-ap-bang-cong-nghe-tien-tien-63062.htm"),
       ("PV Power – Vũng Áng 1", "https://pvpower.vn/pow-media/24/5/dinh-kem-1---pvcv-va-yckt-he-thong-giam-sat-mba.pdf")]),
    N("k4-lap-luan", "Lập luận thuyết phục từ CIGRE/IEEE", "finding", "standards", """
<ul><li>CIGRE TB 642: MBA trạm hỏng khoảng 0,53%/năm, tức 1–2 máy mỗi năm trên 200 máy. Cuộn dây, OLTC và sứ xuyên là nguồn chính.</li>
<li>IEEE C57.143: có phương pháp chi phí – lợi ích cho đầu tư giám sát.</li>
<li>CIGRE TB 995: khung định nghĩa và cấp năng lực DT.</li></ul>"""),
    N("k5-kha-thi", "Khả thi TRUNG BÌNH – CAO", "finding", "director", """
<p>Kỹ thuật và thị trường thuận lợi. Điểm nghẽn là dữ liệu lịch sử, chuyên gia mô hình hóa, và thuyết phục khách hàng trả tiền cho phần mềm.</p>"""),
    N("k6-de-xuat", "Đề xuất: nghiên cứu 5 giai đoạn, 6–9 tháng", "decision", "director", """
<p>Thứ tự: hiểu hệ thống và tiêu chuẩn → mổ xẻ đối thủ → làm chủ mô hình trên dữ liệu thật → định hình sản phẩm và hồ sơ thuyết phục → pilot. Chưa cam kết mốc triển khai với khách hàng trước cổng giai đoạn 3.</p>"""),
])

components = [
    ("c1-cam-bien", "1. Tài sản & cảm biến", "Nhiệt độ điểm nóng, DGA, PD, sứ xuyên (tanδ/C), OLTC, làm mát, tải, môi trường. Đây là phần VTI đã làm."),
    ("c2-du-lieu", "2. Kết nối & dữ liệu", "IEC 61850, IEC 60870-5-104, Modbus; cơ sở dữ liệu chuỗi thời gian; thí nghiệm offline; hồ sơ thiết kế và biên bản heat-run."),
    ("c3-mo-hinh", "3. Mô hình (độ thông minh)", "Vật lý (IEC 60076-7, lão hóa, ẩm) · Quy tắc chuyên gia (IEC 60599, Duval) · Dữ liệu/AI (bất thường, xác suất hỏng) · Lai (vật lý + hiệu chỉnh theo dữ liệu)."),
    ("c4-ung-dung", "4. Dịch vụ / ứng dụng", "Health Index, cảnh báo sớm, giới hạn tải động, tuổi thọ còn lại, mô phỏng what-if, kế hoạch bảo dưỡng."),
    ("c5-vong-quyet-dinh", "5. Vòng quyết định", "Người vận hành hoặc hệ thống tác động lại thiết bị: giảm tải, điều khiển làm mát, lập lệnh công tác. Đây là chiều \"ảo → thật\"."),
]
levels = [
    ("l1-mo-ta", "Mức 1 · Mô tả (Descriptive)", "Hiển thị trạng thái real-time. Trả lời: đang là bao nhiêu?"),
    ("l2-chan-doan", "Mức 2 · Chẩn đoán (Diagnostic)", "Diễn giải nguyên nhân: DGA theo IEC 60599/Duval, tương quan tải – nhiệt. Trả lời: vì sao?"),
    ("l3-du-bao", "Mức 3 · Dự báo (Predictive)", "Dự báo điểm nóng, tuổi thọ còn lại, xác suất hỏng. Trả lời: sắp tới ra sao?"),
    ("l4-khuyen-nghi", "Mức 4 · Khuyến nghị (Prescriptive)", "Đề xuất giới hạn tải, thời điểm bảo dưỡng, thứ tự ưu tiên thay thế. Trả lời: nên làm gì?"),
    ("l5-tu-hanh", "Mức 5 · Tự hành (Autonomous)", "Tự tối ưu và phối hợp với tài sản khác."),
]
system = N("bc1-hieu-he-thong", "Hiểu hệ thống: DT gồm những gì", "section", "standards", """
<p>Theo CIGRE TB 995, DT là biểu diễn ảo của tài sản hoặc hệ thống. Nó được cập nhật liên tục từ dữ liệu thiết bị thật, có khả năng dự báo, và hỗ trợ ra quyết định. Cốt lõi là <b>tương tác hai chiều</b>: dữ liệu đi từ thật lên ảo, quyết định đi từ ảo về thật.</p>""",
    [CIGRE995], children=[
    N("ht-thanh-phan", "Năm thành phần", "group", "standards", "<p>Một DT thiết bị điện gồm 5 lớp chức năng.</p>",
      children=[N(i, t, "concept", "standards", f"<p>{d}</p>") for i, t, d in components]),
    N("ht-cap-nang-luc", "Thang năng lực DT", "group", "standards",
      "<p>TB 995 xếp DT từ mức mô tả đến tự hành. Ba mức giữa là cách phòng chia để đo tiến độ, cần đối chiếu với bản gốc của TB 995.</p>",
      [CIGRE995], children=[N(i, t, "concept", "standards", f"<p>{d}</p>") for i, t, d in levels]),
    N("ht-so-sanh", "Giám sát online khác DT thế nào", "concept", "standards", """
<table><tr><th>Tiêu chí</th><th>Giám sát online</th><th>Digital Twin</th></tr>
<tr><td>Câu hỏi</td><td>Đang là bao nhiêu? Vượt ngưỡng chưa?</td><td>Vì sao? Sắp tới ra sao? Nên làm gì?</td></tr>
<tr><td>Cốt lõi</td><td>Cảm biến + ngưỡng cố định</td><td>Mô hình riêng từng máy, hiệu chỉnh bằng dữ liệu thật</td></tr>
<tr><td>Dữ liệu</td><td>Số đo online</td><td>Online + thí nghiệm + thiết kế + lịch sử</td></tr>
<tr><td>Đầu ra</td><td>Dashboard, báo động</td><td>Health Index, xác suất hỏng, tải động, what-if</td></tr></table>"""),
    N("ht-tb783", "Cảnh báo: DGA online lệch ±20–30%", "risk", "physics", """
<p>CIGRE TB 783 ghi nhận độ lệch hệ thống giữa thiết bị DGA online và phòng thí nghiệm có thể vượt ±20–30% cho từng khí. Trước quyết định lớn, cần lấy mẫu dầu để xác minh. DT tốt phải có bước hiệu chỉnh độ lệch này.</p>""",
      [("Transformers Magazine 2026", "https://hrcak.srce.hr/file/501125")]),
])

layers = N("bc1-ba-tang", "Ba tầng DT trong ngành điện", "section", "director", """
<p>Tầng tài sản và tầng trạm khớp với năng lực của VTI. Tầng lưới là sân chơi của các hãng phần mềm EMS/ADMS, chưa nên theo đuổi.</p>""", children=[
    N("tang-tai-san", "Asset DT (MBA, GIS, cáp)", "concept", "physics", """
<p><b>Giá trị:</b> tránh sự cố, quá tải có kiểm soát, tuổi thọ còn lại, bảo dưỡng theo tình trạng.<br><b>Ví dụ:</b> Siemens Sensformer Advanced (Basslink), Hitachi TXpert + APM Edge, MR ETOS + TESSA.<br><b>Phù hợp VTI:</b> rất cao.</p>"""),
    N("tang-tram", "Substation DT (toàn trạm)", "concept", "substation", """
<p><b>Giá trị:</b> trạm không người trực, tổng hợp cảnh báo, kiểm tra thao tác, đào tạo, vòng đời.<br><b>Ví dụ:</b> State Grid/PowerChina dùng Bentley iTwin cho trạm 220–500 kV; Siemens Electrification X.<br><b>Phù hợp VTI:</b> cao, khớp mục tiêu trạm không người trực của EVN.</p>"""),
    N("tang-luoi", "Grid DT (lưới)", "concept", "benchmark", """
<p><b>Giá trị:</b> quy hoạch, tích hợp năng lượng tái tạo.<br><b>Ví dụ:</b> National Grid Triton (giảm 70% thời gian ra quyết định), TwinEU (11 nước), GE Vernova GridOS.<br><b>Phù hợp VTI:</b> thấp; chỉ cần xuất dữ liệu theo CIM.</p>"""),
    N("tang-vi-sao-mba", "Vì sao bắt đầu từ MBA", "decision", "director", """
<ul><li>Tài sản đắt nhất trạm, thời gian thay thế dài.</li><li>Có nhiều tiêu chuẩn mô hình hóa nhất: IEC 60076-7, IEC 60599, IEEE C57.91/C57.104, CIGRE TB 761.</li>
<li>Ba vị trí hỏng hàng đầu (cuộn dây, OLTC, sứ xuyên) đều giám sát được.</li></ul>""",
      [("EB Magazine – TXpert", "https://www.ebmag.com/txpert-ecosystem-for-the-digitalization-of-transformers/")]),
])

refs_groups = [
    ("ref-rui-ro", "1 · Rủi ro có thật", [
        N("ref-tb642", "CIGRE TB 642 – Transformer reliability survey", "reference", "standards", """
<p>964 sự cố lớn, 58 đơn vị điện lực, 21 nước, giai đoạn 1996–2010. MBA trạm hỏng 0,53%/năm, MBA tăng áp máy phát 0,95%/năm. Với MBA trạm, cuộn dây chiếm 38% số vụ hỏng và OLTC chiếm 31%.</p><p><b>Dùng để:</b> chứng minh sự cố là điều chắc chắn xảy ra với đội máy lớn.</p>""",
          [("e-cigre TB 642", "https://e-cigre.org/publication/642-transformer-reliability-survey"),
           ("VDE – survey", "https://www.vde-verlag.de/proceedings-en/454310004.html"),
           ("Modern Power Systems", "https://modernpowersystems.com/?p=12257")])]),
    ("ref-phuong-phap", "2 · Phương pháp đã chuẩn hóa", [
        N("ref-tb995", "CIGRE TB 995 – Digital twins for power transformers", "reference", "standards",
          "<p>Định nghĩa DT, thành phần, các loại mô hình, thang năng lực, khảo sát ngành, rào cản. <b>Dùng để:</b> khẳng định DT là khái niệm đã chuẩn hóa.</p>",
          [CIGRE995]),
        N("ref-c57143", "IEEE C57.143 – Monitoring guide", "reference", "physics",
          "<p>Thông số cần giám sát cho từng cơ chế hỏng; phân tích rủi ro – lợi ích. <b>Dùng để:</b> tính ROI. Đã có case ROI cho MBA 40/63 MVA.</p>",
          [("IEEE tutorial 2025", "https://grouper.ieee.org/groups/transformers/meetings/F2025-BonitaSprings/Documents/F25-Tutorial-IEEEC57.143-AbstractR2.pdf"),
           ("ROI online DGA", "https://hrcak.srce.hr/file/372842")]),
        N("ref-tb783", "CIGRE TB 783 + TB 771 – DGA monitoring", "reference", "physics",
          "<p>So sánh công nghệ DGA online, quy trình kiểm định độ chính xác, ngưỡng điển hình và tiền sự cố. <b>Dùng để:</b> đưa yêu cầu độ chính xác vào hồ sơ mời thầu.</p>",
          [("e-cigre TB 783", "https://www.e-cigre.org/publication/783-dga-monitoring-systems")]),
        N("ref-mo-hinh", "IEC 60076-7 · IEC 60599 · IEEE C57.91/C57.104 · CIGRE TB 761", "reference", "physics",
          "<p>Mô hình nhiệt và quá tải động, diễn giải DGA, đánh giá tình trạng. <b>Dùng để:</b> chứng minh thuật toán dựa trên tiêu chuẩn, không phải hộp đen.</p>"),
        N("ref-tich-hop", "IEC 61850-7-4 · IEC 62443 · ISO/IEC 30173 · IEC 63278", "reference", "ot_cyber",
          "<p>Logical node SIML, SPDC, STMP, YPTR; an ninh mạng; thuật ngữ và AAS. <b>Dùng để:</b> chứng minh không khóa hãng và đáp ứng an ninh khi đấu nối.</p>"),
    ]),
    ("ref-da-lam", "3 · Đã có người làm thành công", [
        N("ref-evnnpt", "EVNNPT – GE MS3000 cho MBA 500 kV", "case", "vn_market",
          "<p>4 trạm 500 kV kết nối WAN, quản lý tập trung bằng Perception Server. Tiền lệ trong nước cho bảo dưỡng theo tình trạng.</p>",
          [("Tạp chí Công Thương", "https://tapchicongthuong.vn/evnnpt-giam-sat--chan-doan-tinh-trang-may-bien-ap-bang-cong-nghe-tien-tien-63062.htm")]),
        N("ref-basslink", "Siemens Energy – Basslink HVDC", "case", "benchmark",
          "<p>DT mô phỏng ứng suất nhiệt, dự báo tải cho MBA và đường dây 400 kV giữa Victoria và Tasmania.</p>",
          [("Siemens Energy", "https://www.siemens-energy.com/global/en/offerings/references/digital-twin-operation-system-hvdc-transformer.html")]),
        N("ref-triton", "National Grid Triton · TwinEU", "case", "benchmark",
          "<p>Triton giảm 70% thời gian ra quyết định quy hoạch. TwinEU liên kết DT cục bộ 11 nước theo mô hình federated.</p>",
          [("GMI", "https://www.gminsights.com/industry-analysis/digital-twin-in-energy-and-power-market"),
           ("Enlit – TwinEU", "https://www.enlit.world/library/revolutionising-the-european-energy-landscape-twineu-s-digital-twin-ambition")]),
    ]),
    ("ref-chinh-sach", "4 · Phù hợp chính sách Việt Nam", [
        N("ref-nq57", "NQ 57 · Luật Điện lực 2024 · QĐ 538", "policy", "vn_market",
          "<p>NQ 57-NQ/TW coi dữ liệu là tư liệu sản xuất chính. Luật Điện lực 61/2024/QH15 hiệu lực từ 01/02/2025. QĐ 538 đặt mục tiêu 100% trạm 220 kV không người trực giai đoạn 2025–2030.</p>",
          [("Thời báo KTSG", "https://thesaigontimes.vn/saigontimes/cai-cach-thi-truong-dien-viet-nam-2-0-nhin-tu-su-tuong-ho-giua-cac-chu-truong-chinh-sach-lon/")]),
        N("ref-luat-du-lieu", "Luật Dữ liệu 60/2024/QH15", "policy", "vn_market",
          "<p>Hiệu lực 01/7/2025. Chuyển dữ liệu cốt lõi và quan trọng ra nước ngoài phải đánh giá tác động. <b>Ý nghĩa:</b> DT on-premise trong nước có lợi thế so với SaaS cloud nước ngoài.</p>",
          [("LuatVietnam", "https://luatvietnam.vn/thong-tin/luat-du-lieu-2024-so-60-2024-qh15-380165-d1.html"),
           ("CaseLaw", "https://caselaw.vn/bai-viet/quan-ly-chuyen-du-lieu-xuyen-bien-gioi-ket-hop-quy-dinh-tu-luat-du-lieu-2024-va-nghi-dinh-13-2023-nd-cp")]),
    ]),
]
refs = N("bc1-tai-lieu", "Tài liệu tham chiếu thuyết phục khách hàng", "section", "standards", """
<p>Lập luận đi theo 4 bước: <b>rủi ro có thật → phương pháp đã chuẩn hóa → đã có người làm → phù hợp chính sách VN</b>. Lưu ý: con số \"giảm rủi ro tới 70%\" của TESSA APM là tuyên bố của nhà cung cấp, không phải số liệu độc lập.</p>""",
    children=[N(i, t, "group", "standards", "", children=c) for i, t, c in refs_groups])

vendors = [
    ("v-hitachi", "Hitachi Energy – TXpert + APM Edge", "Dự báo",
     "TXpert Hub (CoreTec 5), CoreSense DGA, APM Edge (Lumada APM), dịch vụ từ xa.",
     "Hãng sản xuất MBA; xác suất hỏng liên tục; nhận cảm biến bên thứ ba; phát triển theo IEC 62443-4-1.",
     "Hệ sinh thái riêng; chi phí cao; thuật toán độc quyền.", "Chưa xác minh với dòng DT.",
     [("Hitachi APM Edge", "https://www.hitachienergy.com/test-pages/ak/apm-edge")]),
    ("v-siemens-energy", "Siemens Energy – Sensformer Advanced", "Dự báo – Khuyến nghị (nhiệt)",
     "Cảm biến tích hợp, gateway, cloud, DT nhiệt – thủy lực multi-mass cho từng máy.",
     "Mô hình vật lý sâu nhất, từ dữ liệu thiết kế; mô phỏng tải 24 giờ tới; dự báo quá tải; tổn thất tuổi thọ.",
     "Chạy trên cloud; cần dữ liệu thiết kế của hãng; khó dùng cho MBA hãng khác.", "Chưa xác minh.",
     [("Transformer Technology", "https://transformer-technology.com/article-hub/digital-twin-technology-of-sensformer-advanced-a-significant-step-in-the-digitalization-of-transformers/")]),
    ("v-siemens-ex", "Siemens SI – Electrification X Asset Mgmt", "Mô tả – Chẩn đoán (cấp trạm)",
     "SaaS cloud, SICAM GridEdge, tích hợp TESSA APM.", "Một màn hình cho toàn trạm; thuê bao theo module.",
     "Tập trung trung/hạ áp; cloud nước ngoài vướng Luật Dữ liệu.", "Chưa xác minh.",
     [("Siemens", "https://assets.new.siemens.com/siemens/assets/api/uuid:c8d68e9a-1aa6-40ec-8a8f-41d82abbf0c7/Electrification-X-Asset-Management.pdf")]),
    ("v-mr", "Reinhausen (MR) – ETOS + TESSA APM", "Chẩn đoán – Khuyến nghị",
     "ETOS (điều khiển và giám sát tại MBA, có DT), TESSA APM, cảm biến MSENSE/MESSKO.",
     "Dẫn đầu OLTC (nguồn 31% sự cố); gộp online + offline; Duval, Rogers, IEC 60599; khuyến nghị hành động.",
     "Mạnh nhất khi dùng OLTC của MR; giấy phép phần mềm.", "OLTC MR phổ biến; TESSA chưa xác minh.",
     [("MR Digital Switch", "https://www.reinhausen.com/cn/digital-switch")]),
    ("v-ge", "GE Vernova – Kelman + Perception Fleet", "Chẩn đoán",
     "DGA 900/PLUS (9 khí, sứ xuyên, PD, camera nhiệt), TAPTRANS, MINITRANS, MS3000, Perception Fleet.",
     "Mạnh nhất về DGA (PAS, hãng công bố >15.000 bộ); IEC 61850 Ed.2.",
     "Lấy DGA làm trung tâm; mô hình vật lý đơn giản.", "ĐÃ CÓ: EVNNPT (500 kV), Thủy điện Sông Bung.",
     [("GE Kelman DGA 900 PLUS", "https://www.gevernova.com/electrification/sites/default/files/resources/products/brochures/Kelman_DGA900PLUS-brochure-EN-33152-202606-A4-R010.pdf")]),
    ("v-camlin", "Camlin Energy – TOTUS", "Chẩn đoán",
     "Một thiết bị gộp DGA, PD, sứ xuyên, dòng sự cố xuyên qua; TOTUSPRO Web.",
     "Gọn trong một thiết bị; >1.700 bộ đã lắp; có dịch vụ chuyên gia.", "Ít mô hình vật lý riêng.", "Chưa xác minh.",
     [("Camlin", "https://camlingroup.com/en-us/scandinavia_landing-2-2")]),
    ("v-qualitrol", "Qualitrol – QTMS + SmartSUB", "Mô tả – Chẩn đoán",
     "Tủ giám sát dạng module (làm mát, sợi quang, DGA, LTC, PD, sứ xuyên), phần mềm doanh nghiệp.",
     "Linh hoạt, nhận cảm biến bên thứ ba.", "Phân tích mỏng hơn các hãng sản xuất MBA.", "Chưa xác minh.",
     [("Qualitrol QTMS", "https://www.qualitrolcorp.com/wp-content/uploads/2017/06/AP-M40-01L-02E_QTMS.pdf")]),
    ("v-weidmann", "Weidmann – InsuLogix + VAULT + OPM", "Chẩn đoán – Dự báo (tải)",
     "Giám sát cách điện, Health Index, phần mềm tải tối ưu dùng biên bản heat-run.",
     "Chuyên sâu cách điện rắn; giới hạn tải và kịch bản.", "Quy mô nhỏ.", "Chưa xác minh.",
     [("T&D World", "https://www.tdworld.com/test-and-measurement/article/20970968/transformer-monitoring")]),
    ("v-dynamic", "Dynamic Ratings – C50 / E3", "Chẩn đoán",
     "Nhiệt, sứ xuyên, OLTC, làm mát, DGA, ẩm, PD, dòng sự cố xuyên qua.", "Đủ thông số; hợp cả công nghiệp.",
     "Ít tập trung vào DT.", "Chưa xác minh.",
     [("Electricity Forum", "https://electricityforum.com/catalog/dynamic-ratings/c50-series-transformer-monitor")]),
    ("v-doble", "Doble – Asset Health Index", "Chẩn đoán",
     "Health Index theo tiêu chuẩn, so sánh với kho hàng triệu kết quả thí nghiệm.", "Dữ liệu thí nghiệm offline rất lớn.",
     "Thiên về thí nghiệm offline.", "Thiết bị thí nghiệm phổ biến; phần mềm chưa xác minh.",
     [("Transformers Magazine", "https://hrcak.srce.hr/file/363218")]),
    ("v-china", "Nhà cung cấp Trung Quốc (hệ State Grid)", "Mô tả – Chẩn đoán",
     "Thiết bị giám sát tích hợp MBA/GIS, PD 250 MHz, nền tảng DT 3D cho trạm.", "Giá cạnh tranh; trọn gói toàn trạm.",
     "Theo chuẩn riêng State Grid; chất lượng phân tích cần đánh giá từng hãng.", "Có mặt ở thiết bị giám sát; cần khảo sát.",
     [("EP China", "https://www.epchinashow.com/EP/suppliersprofile/eng?c=319046")]),
    ("v-bentley", "Bentley – iTwin", "Mô tả",
     "DT 3D/BIM cho thiết kế, xây dựng, vận hành trạm.", "Mạnh vòng đời và xây dựng (dự án 500 kV tiết kiệm 2,84 triệu CNY).",
     "Không có mô hình tình trạng thiết bị.", "Chưa xác minh.",
     [("Bentley", "https://bentley.com/yii/project/xianning-chibi-500kv-substation-project")]),
]


def vendor_node(v):
    i, t, lvl, comp, plus, minus, vn, links = v
    html = (f"<p><span class='pill'>Mức DT: {lvl}</span></p><dl><dt>Thành phần</dt><dd>{comp}</dd>"
            f"<dt>Điểm mạnh</dt><dd>{plus}</dd><dt>Điểm yếu / giới hạn</dt><dd>{minus}</dd>"
            f"<dt>Hiện diện tại VN</dt><dd>{vn}</dd></dl>")
    return N(i, t, "vendor", "benchmark", html, links)


market = N("bc1-san-pham", "Đánh giá sản phẩm thị trường (12 dòng)", "section", "benchmark", """
<p>Phần lớn sản phẩm là giám sát đa thông số cộng phần mềm APM quản lý đội máy. Mức DT là đánh giá của phòng từ tài liệu công khai, cần kiểm chứng bằng demo.</p>
<ol><li>Khoảng trống lớn nhất: mô hình trung lập với hãng thiết bị.</li><li>Giá trị nằm ở phần mềm, bán theo giấy phép hoặc thuê bao.</li><li>Cloud nước ngoài là điểm yếu tại Việt Nam.</li></ol>""",
    children=[vendor_node(v) for v in vendors])

compete = N("bc1-canh-tranh", "Khả năng cạnh tranh của VTI", "section", "vn_market", """
<p><b>Định vị:</b> lớp DT trung lập, on-premise, đặt trên cảm biến của bất kỳ hãng nào, kèm dịch vụ kỹ thuật tại chỗ của đội thí nghiệm – hiệu chỉnh 500 kV.</p>""", children=[
    N("ct-oem", "vs. Hãng sản xuất MBA / OLTC", "competitor", "benchmark",
      "<p><b>VTI thua:</b> thương hiệu, dữ liệu thiết kế gốc, kho dữ liệu sự cố toàn cầu.<br><b>VTI thắng:</b> trung lập đa hãng, on-premise, phản ứng nhanh, tiếng Việt, chi phí.</p>"),
    N("ct-monitor", "vs. Hãng chuyên giám sát", "competitor", "benchmark",
      "<p><b>VTI thua:</b> số thiết bị đã lắp, chứng nhận.<br><b>VTI thắng:</b> tích hợp SCADA và trạm số EVN, hiểu quy trình thí nghiệm – nghiệm thu trong nước.</p>"),
    N("ct-platform", "vs. Nền tảng phần mềm", "competitor", "benchmark",
      "<p><b>VTI thua:</b> quy mô nền tảng, 3D/BIM.<br><b>VTI thắng:</b> hiểu vật lý thiết bị cao áp, không phụ thuộc cloud nước ngoài.</p>"),
    N("ct-china", "vs. Nhà cung cấp Trung Quốc", "competitor", "benchmark",
      "<p><b>VTI thua:</b> giá phần cứng, trọn gói toàn trạm.<br><b>VTI thắng:</b> phân tích IEC/CIGRE minh bạch, an ninh mạng trong nước, hậu mãi.</p>"),
    N("ct-swot", "SWOT", "group", "director", "", children=[
        N("swot-s", "Điểm mạnh", "swot-s", "director", "<p>Đội thí nghiệm đến 500 kV; giám sát nhiệt không dây; tích hợp SCADA trạm 110 kV không người trực; quan hệ với các đơn vị điện lực.</p>"),
        N("swot-w", "Điểm yếu", "swot-w", "director", "<p>Chưa có hồ sơ năng lực phần mềm phân tích; dữ liệu lịch sử ít; thiếu chuyên gia mô hình hóa và học máy.</p>"),
        N("swot-o", "Cơ hội", "swot-o", "director", "<p>NQ 57 và Luật Dữ liệu ưu tiên on-premise trong nước; EVNNPC: 100% trạm 110 kV giám sát nhiệt online đến 2030; APAC tăng ~10%/năm; thiết bị ngoại đã lắp là nguồn dữ liệu.</p>"),
        N("swot-t", "Thách thức", "swot-t", "director", "<p>Thói quen mua thương hiệu ngoại; hãng ngoại có thể đóng giao thức; đơn vị điện lực có thể tự làm qua CNTT nội bộ.</p>"),
    ]),
])

feas = [
    ("kt-ky-thuat", "Kỹ thuật – CAO", "Mô hình nhiệt và DGA đã chuẩn hóa; VTI có cảm biến và hạ tầng thu thập; phòng đã có code IEC 60076-7, Duval, đọc SCD.", "Biên bản heat-run và 3–6 tháng dữ liệu liên tục."),
    ("kt-du-lieu", "Dữ liệu – TRUNG BÌNH", "Dữ liệu rải rác giữa SCADA, phần mềm quản lý, Excel và thiết bị ngoại; DGA online lệch ±20–30%.", "Chuẩn hóa dữ liệu; quyền đọc thiết bị hãng khác."),
    ("kt-phap-ly", "Pháp lý & an ninh – TRUNG BÌNH, thuận lợi", "Luật Dữ liệu yêu cầu đánh giá khi chuyển dữ liệu ra nước ngoài; EVN dùng data diode tách OT/IT.", "On-premise; IEC 62443; đọc một chiều."),
    ("kt-kinh-te", "Kinh tế – TRUNG BÌNH đến CAO", "Tỉ lệ hỏng 0,53%/năm × giá trị MBA và thiệt hại mất điện; DGA chiếm 48% thị trường giám sát.", "ROI theo IEEE C57.143 cho từng nhóm MBA."),
    ("kt-to-chuc", "Tổ chức & con người – THẤP đến TRUNG BÌNH", "NPT nhận định thách thức lớn nhất là thay đổi thói quen; VTI thiếu nhân sự mô hình hóa.", "Đào tạo; hợp tác ĐHBK Hà Nội, ĐH Điện lực; quy trình chuyên gia duyệt AI."),
    ("kt-canh-tranh", "Thị trường – TRUNG BÌNH", "GE đã có mặt ở EVNNPT; chủ đầu tư nguồn điện đã mời thầu giám sát + quản lý tài sản.", "Định vị trung lập; có pilot tham chiếu đầu tiên."),
]
feasibility = N("bc1-kha-thi", "Tính khả thi tại Việt Nam", "section", "vn_market", """
<p><b>TRUNG BÌNH – CAO.</b> Công nghệ và nhu cầu sẵn sàng; nghẽn ở dữ liệu, con người và mô hình kinh doanh phần mềm.</p>""",
    children=[N(i, t, "feasibility", "vn_market", f"<dl><dt>Căn cứ</dt><dd>{a}</dd><dt>Điều kiện cần</dt><dd>{b}</dd></dl>") for i, t, a, b in feas]
    + [N("kt-khach-hang", "Thứ tự nhóm khách hàng", "decision", "vn_market",
         "<ol><li>Nhà máy điện và doanh nghiệp công nghiệp lớn (MBA tăng áp hỏng 0,95%/năm, quyết định nhanh).</li><li>Các tổng công ty điện lực, cho trạm 110 kV.</li><li>EVNNPT, trạm 220–500 kV (khó nhất vì hãng ngoại đã có mặt).</li></ol>")])

phases = [
    ("gd1", "GĐ1 · Nền tảng tri thức", "11/11 – 20/12/2026 (6 tuần)", "standards",
     "Đọc và tóm tắt 15 tài liệu lõi; bảng thuật ngữ Việt – Anh; bản đồ tiêu chuẩn.",
     "Sổ tay DT ngành điện khoảng 40 trang; bộ câu hỏi tự kiểm tra.",
     "Anh trình bày DT trong 15 phút và trả lời 10 câu hỏi khó của khách hàng."),
    ("gd2", "GĐ2 · Mổ xẻ thị trường", "07/12/2026 – 24/01/2027 (7 tuần)", "benchmark",
     "Datasheet, brochure, case study 12 hãng; xin demo; giá từ hồ sơ mời thầu công khai; phỏng vấn 5 kỹ sư vận hành.",
     "Ma trận tính năng; battlecard từng đối thủ; bản đồ dự án đã triển khai tại VN.",
     "Chốt 3 điểm khác biệt của VTI có bằng chứng."),
    ("gd3", "GĐ3 · Làm chủ mô hình", "25/01 – 18/04/2027 (10 tuần, trừ Tết)", "physics",
     "Hiệu chỉnh mô hình nhiệt trên dữ liệu VTI; DGA + tốc độ sinh khí; Health Index v1; mô hình trạm từ SCD; thử hybrid.",
     "Prototype offline; báo cáo độ chính xác.",
     "Sai số θh ≤ ±3 K (đề xuất); Health Index được chuyên gia đồng thuận ≥ 80%."),
    ("gd4", "GĐ4 · Định hình sản phẩm & hồ sơ", "19/04 – 30/05/2027 (6 tuần)", "director",
     "Kiến trúc sản phẩm; business case theo IEEE C57.143; whitepaper; tiêu chuẩn kỹ thuật mẫu; hồ sơ an ninh mạng.",
     "Bộ hồ sơ chào hàng; mô hình giá.", "Lãnh đạo VTI duyệt go / no-go."),
    ("gd5", "GĐ5 · Pilot", "Từ 06/2027", "director",
     "Triển khai thử tại 1 trạm hoặc nhà máy.", "Trường hợp tham chiếu đầu tiên.", "Khách hàng xác nhận giá trị."),
]
roadmap = N("bc1-lo-trinh", "Lộ trình nghiên cứu 5 giai đoạn", "section", "director", """
<p>Mục tiêu giai đoạn này là <b>hiểu đủ sâu để tự thiết kế và bảo vệ được giải pháp</b>, chưa phải bán hàng. Mỗi giai đoạn kết thúc bằng một cổng do anh Khương duyệt.</p>""",
    children=[N(i, t, "phase", a, f"<p><span class='pill'>{when}</span></p><dl><dt>Nội dung</dt><dd>{what}</dd><dt>Đầu ra</dt><dd>{out}</dd><dt>Cổng đánh giá</dt><dd>{gate}</dd></dl>")
              for i, t, when, a, what, out, gate in phases])

questions = N("bc1-cau-hoi", "Câu hỏi mở", "section", "director", """
<ul><li>VTI có quyền truy xuất dữ liệu thiết bị GE (MS3000, Kelman) đã lắp ở VN không? Qua giao thức nào?</li>
<li>Giá tham khảo phần mềm APM ngoại trên mỗi MBA mỗi năm?</li>
<li>EVN đã có quy định kỹ thuật cho giám sát online và Health Index chưa?</li>
<li>Dữ liệu vận hành MBA có thuộc \"dữ liệu quan trọng\" theo nghị định hướng dẫn Luật Dữ liệu không?</li>
<li>VTI có bao nhiêu MBA có dữ liệu liên tục ≥ 6 tháng cho GĐ3?</li></ul>""")

report1 = N("bao-cao-1", "Báo cáo #1 · Nghiên cứu nền (10/11/2026)", "report", "director", """
<p>Báo cáo nghiên cứu nền về giải pháp DT ngành điện: hiểu hệ thống, tài liệu tham chiếu, sản phẩm thị trường, khả năng cạnh tranh, tính khả thi và lộ trình nghiên cứu. Bản đầy đủ, có bình luận được, nằm trong tài liệu Claude Docs.</p>""",
    [("Mở báo cáo đầy đủ", "https://claude.ai/artifact/J3XcTGN2Xi99ESDhCzmUKu")],
    [summary, system, layers, refs, market, compete, feasibility, roadmap, questions])

# ---------------------------------------------------------------- Báo cáo kế hoạch
plan = N("bao-cao-ke-hoach", "Báo cáo kế hoạch W46 (bản đầu)", "report", "director", """
<p>Bản kế hoạch đầu tiên theo hướng triển khai Q1/2027. <b>Đã điều chỉnh ngày 10/11:</b> anh Khương chuyển ưu tiên sang nghiên cứu, hiểu hệ thống trước; lộ trình triển khai Q1 tạm gác và thay bằng lộ trình nghiên cứu ở Báo cáo #1.</p>""",
    [("Mở báo cáo kế hoạch", "https://claude.ai/artifact/Bsmd2mNe1rweDP3o3yU7bA")], [
    N("kh-kien-truc", "Kiến trúc DT 5 lớp", "concept", "standards",
      "<ol><li>Thiết bị, cảm biến</li><li>Kết nối, edge (IEC 61850, 104, MQTT)</li><li>Nền tảng dữ liệu (time-series, CIM/AAS)</li><li><b>Mô hình DT</b> (IEC 60076-7, IEC 60599, PD, SCL)</li><li>Ứng dụng (Health Index, cảnh báo, tải động)</li></ol><p>An ninh mạng IEC 62443/62351 xuyên suốt.</p>"),
    N("kh-hai-luong", "Hai luồng song song", "decision", "director",
      "<p>Transformer DT và Substation DT 110 kV chạy song song, dùng chung nền tảng dữ liệu.</p>"),
    N("kh-lo-trinh-q1", "Lộ trình Q1/2027 (tạm gác)", "risk", "director",
      "<p>G0 22/11 · G1 27/12 · G2 FAT 22/01/2027 · Tết · G3 SAT 07/03 · Nghiệm thu 31/03/2027. Giữ lại để tham khảo khi bước sang GĐ5 Pilot.</p>"),
])

# ---------------------------------------------------------------- Công cụ
tools = N("cong-cu", "Công cụ & hạ tầng của phòng", "report", "ot_cyber", """
<p>Bộ công cụ <code>DT-RnD-Lab</code> chạy local trên MacBook 16 GB bằng Qwen qua Ollama, mã nguồn trên GitHub.</p>""",
    [("GitHub – DT-RnD-Lab", "https://github.com/khuongvh-vti/DT-RnD-Lab")], [
    N("cc-local", "Model local: qwen3.5:9b", "tool", "ot_cyber",
      "<p>Embedding <code>qwen3-embedding:0.6b</code>, kho tài liệu RAG trong SQLite, mọi câu trả lời trích [S#] từ <code>library/</code>.</p>"),
    N("cc-cloud", "Cloud miễn phí trước, trả phí tắt", "tool", "ot_cyber",
      "<ol><li>Alibaba Model Studio (Singapore): ~1M token free mỗi model, 90 ngày, xoay vòng 6 model, dừng ở 90%.</li><li>OpenRouter <code>:free</code>: 50 req/ngày (1.000 nếu từng nạp ≥ 10 USD).</li><li>Trả phí: tắt mặc định.</li><li>Local: phương án cuối; bắt buộc với dữ liệu khách hàng.</li></ol>",
      [("Model Studio free quota", "https://www.alibabacloud.com/help/en/model-studio/new-free-quota")]),
    N("cc-vat-ly", "Lõi kỹ thuật: nhiệt, DGA, SCD", "tool", "physics",
      "<p><code>transformer_thermal.py</code> (IEC 60076-7, lão hóa, tải tối đa) · <code>dga.py</code> (Duval 1, IEC 60599) · <code>scl.py</code> (đọc SCD IEC 61850-6, lọc LN giám sát tình trạng).</p>"),
    N("cc-web", "Trang sơ đồ cây (trang này)", "tool", "director",
      "<p>Chạy local: <code>python3 dtlab.py serve</code> rồi mở http://localhost:8765. Mỗi báo cáo mới trong <code>reports/</code> tự thành một nhánh của cây.</p>"),
    N("cc-lich", "Lịch báo cáo", "tool", "director",
      "<p>Sáng thứ Hai hằng tuần: Qwen local chạy vòng nghiên cứu (launchd 8:00) và Claude tổng hợp nghiên cứu web (7:37), đẩy lên GitHub và Project.</p>"),
])

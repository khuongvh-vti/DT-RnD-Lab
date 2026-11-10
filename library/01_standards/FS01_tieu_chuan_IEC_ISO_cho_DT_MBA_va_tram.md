# Fact sheet 01 – Tiêu chuẩn IEC/ISO dùng cho Transformer DT & Substation DT

Nguồn: tra cứu trực tiếp IEC Webstore và cơ sở dữ liệu tiêu chuẩn quốc gia ngày 10/11/2026. Đây là **tóm tắt phạm vi do Phòng R&D tự viết**, không phải nội dung gốc của tiêu chuẩn. Nội dung kỹ thuật chi tiết (công thức, bảng giới hạn) chỉ có trong bản tiêu chuẩn có bản quyền – cần mua và đưa vào thư mục library/01_standards.

## IEC 60076-7:2018 – Loading guide for mineral-oil-immersed power transformers
- Phiên bản: Edition 2.0, phát hành 12/01/2018, TC 14, 89 trang (bản RLV 190 trang). Thay thế IEC 60076-7:2005 (Ed 1). Chưa có bản sửa đổi; ngày ổn định (stability date) theo IEC Webstore là 2026 (bản chuẩn) / 2029 (bản RLV) → có thể sắp được rà soát, cần theo dõi.
- Phạm vi: hướng dẫn xác định và vận hành MBA dầu khoáng theo nhiệt độ vận hành và lão hóa nhiệt; khuyến nghị mang tải vượt định mức; hướng dẫn chọn thông số định mức cho lắp đặt mới.
- Thay đổi chính so với 2005: (a) đổi tên sang "mineral-oil-immersed"; (b) cập nhật tuổi thọ cách điện theo nghiên cứu mới; (c) rà soát giới hạn nhiệt độ, khuyến nghị nhiệt độ lõi tối đa; (d) khuyến nghị số lượng cảm biến sợi quang cho thử nghiệm độ tăng nhiệt; (e) xét đến hệ số Q, S, H; (f) mô hình nhiệt viết lại dạng toán học tổng quát; (g) bàn về dòng cảm ứng địa từ (GIC) và giới hạn nhiệt kèm theo.
- Vai trò trong DT: là "lõi vật lý" của Transformer DT mức Descriptive/Diagnostic – tính hot-spot θh, top-oil θo, tốc độ lão hóa tương đối V và loss of life; dự báo khả năng mang tải (dynamic rating).
- Lưu ý ứng dụng: chỉ áp dụng cho dầu khoáng; dầu este dùng IEC 60076-14. Các hãng lớn (Siemens Energy Sensformer Advanced) công bố mô hình riêng multi-mass/thermo-hydraulic chính xác hơn mô hình IEC tiêu chuẩn → mô hình IEC là chuẩn tối thiểu, không phải trần.
- Nguồn: https://webstore.iec.ch/publication/34351 ; https://webstore.iec.ch/publication/62459

## IEC 60599:2022 – Interpretation of dissolved and free gases analysis
- Phiên bản: Edition 4.0, phát hành 25/05/2022, TC 10, 80 trang (bản CMV 122 trang). Thay thế IEC 60599:2015 (Ed 3.0).
- Phạm vi: diễn giải nồng độ khí hòa tan/khí tự do để chẩn đoán tình trạng thiết bị điện chứa dầu khoáng, cách điện giấy/pressboard, và đề xuất hành động. Thông tin cho MBA, kháng, sứ xuyên, thiết bị đóng cắt, cáp dầu chỉ mang tính hướng dẫn trong phụ lục ứng dụng. Có thể áp dụng thận trọng cho hệ cách điện lỏng–rắn khác. Kết quả chỉ là hướng dẫn, hành động phải dựa trên phán đoán kỹ thuật.
- Vai trò trong DT: lớp Diagnostic cho DGA (ratio method, Duval Triangle 1 trong phụ lục). Công cụ DGA của DT-RnD-Lab đang dùng tỷ số IEC 60599 + Duval Triangle 1.
- CẦN KIỂM CHỨNG: danh sách thay đổi chi tiết Ed 4.0 so với Ed 3.0 (chỉ có trong bản CMV).
- Nguồn: https://webstore.iec.ch/publication/76192 ; https://webstore.iec.ch/en/publication/66491

## IEC 61850-7-4:2010+AMD1:2020 (Ed 2.1) – Logical node classes
- Phiên bản hợp nhất Ed 2.1 phát hành 02/2020, 490 trang, TC 57.
- Định nghĩa các logical node (LN) và data object. Nhóm "S" (supervision) dùng cho giám sát tình trạng: SIML (giám sát môi chất cách điện lỏng – DGA, độ ẩm), SIMG (khí cách điện – SF6), SPDC (phóng điện cục bộ), STMP (nhiệt độ), SLTC (bộ điều áp dưới tải), SPTR (giám sát MBA), SCBR (máy cắt), SOPM (cơ cấu truyền động), SSWI (dao cách ly), SVBR (rung), SARC (hồ quang).
- Amendment 1:2020 bổ sung LN cho giám sát theo IEC 62271, power quality, thống kê/lịch sử.
- Vai trò trong DT: chuẩn hóa tên tín hiệu giám sát → Substation DT đọc được từ file SCD; là cơ sở để DT "vendor-neutral".
- Nguồn: https://webstore.iec.ch/en/publication/66551

## IEC TR 61850-90-3:2016 – Using IEC 61850 for condition monitoring diagnosis and analysis
- Technical Report Ed 1.0, 12/05/2016, khoảng 210 trang, đã gộp Corrigendum 11/2020. TC 57.
- Nội dung: use case giám sát–chẩn đoán (CMD) cho GIS, MBA, bộ điều áp (LTC), cáp ngầm, đường dây, hệ thống điện tự dùng; yêu cầu truyền thông; trao đổi với hệ thống quản lý tài sản (asset management); đề xuất LN và khoảng 200 data object mới.
- Diễn biến 2026: theo blog chuyên gia IEC 61850 (nettedautomation, 06/08/2026), TC 57 đang soạn PAS 61850-90-3 ED1 (bản nháp khoảng 287 trang), bổ sung LN cho MBA như SLTC, SVAM (giám sát rung–âm OLTC), SDBR (bình thở hút ẩm), SPRD (van an toàn áp suất). → CẦN THEO DÕI vì ảnh hưởng trực tiếp mô hình dữ liệu Transformer DT.
- Nguồn: https://webstore.iec.ch/publication/24777 ; https://blog.nettedautomation.com/search/label/IEC%2061850-90-3

## IEC 61850-6 – SCL (Substation Configuration Language)
- File SCD/ICD/CID mô tả trạm, IED, LN. Là "bản vẽ số" để dựng Substation DT tự động (single-line + tín hiệu).
- Bản hiện hành: Ed 2.1 (IEC 61850-6:2009+AMD1:2018) – CẦN KIỂM CHỨNG trên IEC Webstore trước khi trích dẫn cho khách hàng.

## ISO/IEC 30173:2023 – Digital twin: Concepts and terminology
- Ed 1.0, phát hành 11/2023, 28 trang, ISO/IEC JTC 1/SC 41.
- Nội dung: thuật ngữ DT; khái niệm (bối cảnh hệ thống DT, vòng đời, các loại DT); functional view; các bên liên quan; so sánh DT với simulation, cyber-physical system, AAS, IoT.
- Dùng để: thống nhất định nghĩa "Digital Twin" khi viết hồ sơ cho khách hàng (tránh gọi một hệ giám sát online đơn thuần là DT).
- Nguồn: https://scc-ccn.ca/standardsdb/standards/8187952

## ISO/IEC 30172:2023 – Digital twin use cases (TR)
- Tập hợp use case DT, phát hành 2023, JTC 1/SC 41.

## ISO/IEC 30188 – Digital twin reference architecture
- Đang xây dựng (JTC 1/SC 41/WG 6), dùng hướng dẫn ISO/IEC/IEEE 42010. Khung khái niệm: target entity ↔ digital entity, đồng bộ (synchronization), observable elements. CẦN KIỂM CHỨNG trạng thái phát hành mới nhất.
- Liên quan: ISO/IEC 30186 (maturity model), ISO/IEC 30153 (hướng dẫn mô hình hóa digital entity).

## IEC 63278-1:2023 – Asset Administration Shell (AAS) structure
- Ed 1.0, 14/12/2023, TC 65, 149 trang.
- Định nghĩa cấu trúc biểu diễn số chuẩn hóa của tài sản (AAS) để các phần mềm trao đổi thông tin tin cậy, an toàn. Phạm vi: tài sản công nghiệp trong toàn bộ vòng đời; tài sản vật lý, số hoặc vô hình.
- Ý nghĩa cho VTI: có thể dùng AAS làm "hộ chiếu số" (nameplate, heat-run, FAT/SAT, lịch sử DGA) cho MBA – xu hướng châu Âu; chưa phổ biến trong ngành điện Việt Nam (GIẢ ĐỊNH, cần khảo sát).
- Nguồn: https://webstore.iec.ch/en/publication/65628

## ISO 23247 (1–4):2021 – Digital twin framework for manufacturing
- Khung DT cho sản xuất (dựa trên kiến trúc IoT ISO/IEC 30141). Tham khảo cách chia lớp kiến trúc, không áp dụng trực tiếp cho lưới điện.

## IEC 62443 – Industrial cybersecurity
- 62443-4-1: quy trình phát triển sản phẩm an toàn; 62443-4-2: yêu cầu kỹ thuật cho thành phần. Hitachi Energy TXpert Hub công bố chứng nhận IEC 62443-4-2, đội phát triển đạt 62443-4-1 và ISO 27001 → đây là "ngưỡng cạnh tranh" về an ninh mạng mà sản phẩm VTI phải tính tới.

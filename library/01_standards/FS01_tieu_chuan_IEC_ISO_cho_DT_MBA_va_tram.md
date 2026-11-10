# Fact sheet 01 – Tiêu chuẩn IEC/ISO cho Transformer DT & Substation DT (đã đối chiếu bản gốc)

Cập nhật 10/11/2026. ✅ = đã đọc bản gốc trong library/01_standards. 🌐 = tra cứu web. Tóm tắt bằng lời của Phòng R&D; số liệu bảng ghi kèm số hiệu bảng/mục để tra lại.

## ✅ IEC 60076-7:2018 (Ed 2.0) – Loading guide for mineral-oil-immersed power transformers
- Phát hành 12/01/2018, TC 14, thay bản 2005. Áp dụng cho MBA dầu khoáng; MBA dùng vật liệu cách điện cấp nhiệt cao hơn thì theo IEC 60076-14.
- **Tốc độ lão hóa tương đối V** (mục 6.3), chỉ phụ thuộc nhiệt độ điểm nóng θh:
  - Giấy thường: V = 2^((θh − 98)/6), nên V = 1 tại 98 °C.
  - Giấy nâng cấp nhiệt: V = exp(15000/(110+273) − 15000/(θh+273)), nên V = 1 tại 110 °C.
  - Bảng 1: ở 140 °C, V = 128 với giấy thường và 17,2 với giấy nâng cấp; ở 80 °C, V = 0,125 và 0,036.
- **Hao mòn tuổi thọ**: L = Σ Vn·tn (mục 6.4). Bước thời gian phải nhỏ hơn một nửa hằng số thời gian cuộn dây τw. Annex A trình bày cách tính đồng thời ẩm, oxy và axit (Hình 4–5: tuổi thọ kỳ vọng theo độ ẩm 0,5–3,5 % và oxy, tiêu chí kết thúc là DP còn 200).
- **Bảng 2 – Giới hạn nhiệt độ khi mang tải vượt định mức** (MBA cỡ trung và lớn):
  | Chế độ | Điểm nóng cuộn dây | Kim loại khác | Lõi | Dầu đỉnh |
  |---|---|---|---|---|
  | Chu kỳ bình thường | 120 °C | 140 °C | 130 °C | 105 °C |
  | Sự cố dài hạn | 140 °C | 160 °C | 140 °C | 115 °C |
  | Sự cố ngắn hạn | 160 °C | 180 °C | 160 °C | 115 °C |
- **Bảng 3 – Giới hạn dòng (pu)**:
  | Chế độ | MBA nhỏ | MBA cỡ trung | MBA lớn |
  |---|---|---|---|
  | Chu kỳ bình thường | 1,5 | 1,5 | 1,3 |
  | Sự cố dài hạn | 1,8 | 1,5 | 1,3 |
  | Sự cố ngắn hạn | 2,0 | 1,8 | 1,5 |
  Ghi chú: khả năng cắt của bộ điều áp giới hạn ở 2 lần dòng định mức (theo IEC 60214-1).
- **Bảng 4 – Đặc tính nhiệt khuyến nghị** (MBA cỡ trung/lớn, loại không hạn chế lưu thông dầu):
  | Làm mát | x | y | k11 | k21 | k22 | τo (phút) | τw (phút) |
  |---|---|---|---|---|---|---|---|
  | ONAN | 0,8 | 1,3 | 0,5 | 2,0 | 2,0 | 210 | 10 |
  | ONAF | 0,8 | 1,3 | 0,5 | 2,0 | 2,0 | 150 | 7 |
  | OF | 1,0 | 1,3 | 1,0 | 1,3 | 1,0 | 90 | 7 |
  | OD | 1,0 | 2,0 | 1,0 | 1,0 | 1,0 | 90 | 7 |
  Với cuộn dây làm mát kiểu zigzag bị hạn chế lưu thông dầu: k21 = 3,0 (ONAN/ONAF) và 1,45 (OF). Công cụ nhiệt độ trong DT-RnD-Lab đang dùng đúng các giá trị trên.
- Thay đổi so với bản 2005: cập nhật tuổi thọ cách điện; khuyến nghị nhiệt độ lõi tối đa; số cảm biến sợi quang khi thử phát nóng; hệ số Q, S, H; viết lại mô hình nhiệt dạng toán học tổng quát; bàn về GIC.
- TB 995 nhận xét: mô hình này dễ áp dụng (chỉ cần tải và nhiệt độ môi trường), nhưng chỉ cho 1 cuộn dây, 1 pha, nấc cố định, 1 cấp làm mát. Nên hiệu chỉnh thông số bằng thử phát nóng mở rộng hoặc dữ liệu vận hành.

## ✅ IEC 60599:2022 (Ed 4.0) – Interpretation of dissolved and free gases analysis
- **Bảng 1 – tỷ số khí** (C2H2/C2H4; CH4/H2; C2H4/C2H6), NS = không có ý nghĩa:
  | Lỗi | C2H2/C2H4 | CH4/H2 | C2H4/C2H6 |
  |---|---|---|---|
  | PD | NS | < 0,1 | < 0,2 |
  | D1 | > 1 | 0,1–0,5 | > 1 |
  | D2 | 0,6–2,5 | 0,1–1 | > 2 |
  | T1 (< 300 °C) | NS | > 1 | < 1 |
  | T2 (300–700 °C) | < 0,1 | > 1 | 1–4 |
  | T3 (> 700 °C) | < 0,2 | > 1 | > 4 |
  Bảng 2 (sơ đồ giản lược): C2H2/C2H4 < 0,2 thì là PD hoặc T, > 0,2 thì là D. Annex B có biểu diễn đồ họa (tam giác Duval).
- **CO2/CO** (mục 5.5): CO cao (ví dụ 1000 ppm) kèm CO2/CO < 3 cho thấy có thể có giấy tham gia sự cố. CO2 > 10 000 ppm kèm CO2/CO > 10 cho thấy có thể quá nhiệt nhẹ giấy (< 160 °C) hoặc oxy hóa dầu. Không kết luận giấy bị ảnh hưởng chỉ dựa vào CO/CO2.
- **Quy trình (Điều 9)**:
  a) Loại bỏ giá trị bất thường, tính tốc độ tăng. Nếu mọi khí dưới giá trị điển hình thì kết luận "DGA bình thường". Nếu có khí vượt thì tính tỷ số theo Bảng 1.
  b) Kiểm tra ngưỡng báo động, xem lỗi có tiến triển không, giấy có tham gia không.
  c) Hành động: tăng tần suất lấy mẫu, thử nghiệm bổ sung (âm học, điện, hồng ngoại), giảm tải, xem xét đưa máy ra kiểm tra.
- **Bảng A.2 – dải giá trị điển hình 90 % trên MBA lực** (µl/l): H2 50–150; CH4 30–130; C2H4 60–280; C2H6 20–90; CO 400–600; CO2 3800–14000; C2H2 là 2–20 (không có OLTC thông dầu) hoặc 60–280 (có OLTC thông dầu).
- **Bảng A.3 – tốc độ tăng điển hình 90 %** (µl/l/năm, MBA dầu > 5000 l): H2 35–132; CH4 10–120; C2H4 32–146; C2H6 5–90; CO 260–1060; CO2 1700–10000; C2H2 0–4 (không OLTC) hoặc 21–37 (có OLTC thông dầu).
- Khuyến nghị mỗi công ty điện tự tính giá trị điển hình của đội máy mình. Công cụ DGA của DT-RnD-Lab dùng cận trên Bảng A.2 để kiểm tra bước a).

## ✅ IEC TR 61850-90-3:2016 (+ Cor.1:2020) – Using IEC 61850 for condition monitoring diagnosis and analysis
- Use case giám sát–chẩn đoán (CMD) cho GIS, MBA, bộ điều áp (LTC), cáp ngầm, đường dây, hệ thống điện tự dùng; kèm yêu cầu truyền thông và liên kết với hệ quản lý tài sản.
- **LN cho MBA** (mục 6.4):
  - SIML: khí và ẩm trong dầu;
  - SPDC: phóng điện cục bộ;
  - SPTR: giám sát tổng thể MBA;
  - SIMS: lão hóa cách điện rắn;
  - SSTP: nhiệt độ bão hòa/sinh bọt, thay SBTP;
  - SBSH: sứ;
  - SCGR: nhóm làm mát;
  - cảm biến phụ: TFLW (lưu lượng), TLVL (mức), TPRS (áp suất), TTMP (nhiệt độ), TGSN (cảm biến chung).
- **LTC** (chương 7): đặc tính thao tác, số lần chuyển nấc, mòn tiếp điểm, nhiệt độ dầu LTC, bộ lọc dầu → SLTC.
- 🌐 Diễn biến 2026: TC 57 đang soạn PAS 61850-90-3 ED1, bổ sung SVAM (rung–âm OLTC), SDBR (bình thở), SPRD (van áp suất).
- Ý nghĩa: đây là "từ điển dữ liệu" để Substation DT đọc tín hiệu giám sát theo cách không phụ thuộc hãng.

## ✅ IEC 61850-7-4:2010+AMD1:2020 (Ed 2.1) – Compatible logical node classes and data object classes
Bản hợp nhất 490 trang. Nhóm LN "S" (supervision): SARC, SCBR, SIMG, SIML, SLTC, SOPM, SPDC, SPTR, SSWI, STMP, SVBR… Amendment 1 bổ sung LN giám sát theo IEC 62271, power quality, dữ liệu thống kê/lịch sử.

## ✅ Đặc tả AAS của IDTA – "Specification of the Asset Administration Shell Part 1: Metamodel" (IDTA-01001-3-0)
- Bộ đặc tả miễn phí của Industrial Digital Twin Association, nội dung tương ứng IEC 63278-1:2023 (bản IEC phải mua).
- Định nghĩa metamodel của AAS và các submodel, định danh, kiểm soát truy cập, ánh xạ sang XML, JSON, RDF, AutomationML, OPC UA. Phần 2 (API), phần 3a (IEC 61360), phần 4 (bảo mật), phần 5 (gói AASX) tải tại industrialdigitaltwin.org.
- Ứng dụng tiềm năng: "hộ chiếu số" của MBA (nameplate, FAT, heat-run, SCD, lịch sử DGA) để trao đổi giữa nhà chế tạo, công ty điện và VTI. Khớp với khuyến nghị dùng tiêu chuẩn mở của TB 995.

## 🌐 IEC 63278-1:2023 – AAS structure (Ed 1.0, 14/12/2023, TC 65, 149 trang)
## 🌐 ISO/IEC 30173:2023 – Digital twin: Concepts and terminology (11/2023, 28 trang, JTC 1/SC 41)
## 🌐 ISO/IEC 30188 – Digital twin reference architecture (đang soạn tại JTC 1/SC 41/WG 6)
## 🌐 IEC 62443-4-1 / 4-2 – An ninh mạng cho quy trình phát triển và thành phần
Hitachi Energy TXpert Hub có chứng nhận IEC 62443-4-2.
## 🌐 IEC 61850-6 – SCL (SCD/ICD/CID)
Bản Ed 2.1 (2009+AMD1:2018), CẦN KIỂM CHỨNG trước khi trích dẫn cho khách hàng.

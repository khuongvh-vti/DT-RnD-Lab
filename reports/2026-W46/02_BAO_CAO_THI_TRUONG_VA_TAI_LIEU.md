# Báo cáo #2 – Đánh giá sản phẩm thị trường từ nguồn chính hãng, kiểm chứng tiêu chuẩn & danh mục tài liệu cần bổ sung

Ngày 10/11/2026 · Phòng R&D Digital Twin · Giai đoạn GĐ1 – Nền tảng tri thức

## 1. Vì sao các câu trả lời trước chưa chuẩn – và đã sửa gì
| Nguyên nhân | Hậu quả | Đã sửa |
|---|---|---|
| Kho tài liệu `library/` trên máy anh **trống** (0 tài liệu) | Qwen không có căn cứ, trả lời chung chung, tự ghi "GIẢ ĐỊNH" | Viết 9 fact sheet có nguồn (tiêu chuẩn, CIGRE/IEEE, 10 hãng, Việt Nam) đưa vào kho; server tự nạp khi khởi động |
| Trưởng phòng trả lời mọi câu hỏi theo **khuôn báo cáo tuần** | Câu hỏi "so sánh Siemens – Hitachi" lại nhận về "Báo cáo tuần…" | Viết lại chức năng hỏi đáp: trả lời thẳng, cấu trúc Trả lời ngắn → Chi tiết → Độ tin cậy → Tài liệu còn thiếu, bắt buộc trích [S#] |
| Một số thông tin cũ trong Báo cáo #1 | Trích dẫn lỗi thời | Đính chính ở mục 2 |

## 2. Đính chính & cập nhật so với Báo cáo #1 (đã kiểm chứng trên nguồn chính thức)
- **IEEE C57.143**: bản hiện hành là **C57.143-2024** (phát hành 20/05/2025, 177 trang), thay bản 2012. Có phụ lục mới về PD, đo trực tiếp nhiệt độ cuộn dây, phân tích dữ liệu DGA online.
- **CIGRE TB 995** (JWG A2/D2.65, 108 trang, tóm tắt trên Electra 08/2026): xác nhận đúng là tài liệu "Digital twins for power transformers". Có khung năng lực từ Descriptive tới Autonomous và **checklist VVUQ** cho dự án Transformer DT. Đây là tham chiếu chính để thuyết phục khách hàng.
- **IEC 60599**: bản hiện hành **Ed 4.0 (2022)**. **IEC 60076-7**: **Ed 2.0 (2018)**, IEC Webstore ghi stability date 2026 → có thể sắp được rà soát.
- **IEC 61850**: 7-4 bản hợp nhất **Ed 2.1 (2020)**. TR 61850-90-3:2016 đang được nâng thành **PAS 61850-90-3**, theo blog chuyên gia IEC 61850 (08/2026); bản nháp bổ sung các LN cho MBA: SLTC, SVAM, SDBR, SPRD.
- **CIGRE TB 642**: suất sự cố MBA trạm 0,53 %/năm, GSU 0,95 %/năm (964 sự cố, 167.459 MBA-năm, 58 công ty, 21 nước). Đã kiểm chứng.
- **CIGRE TB 783**: sai lệch DGA online so với phòng thí nghiệm có thể vượt ±20–30 % mỗi khí. CIGRE WG A2/D1.67 đang soạn hướng dẫn DGA online.

## 3. So sánh sản phẩm thị trường (đọc từ trang/brochure chính hãng)
| Hãng | Sản phẩm chủ lực | Đo / chức năng | Mô hình & phân tích | Mức TB 995 (đánh giá của Phòng) | Tính mở | Hiện diện tại VN |
|---|---|---|---|---|---|---|
| Hitachi Energy | TXpert Hub (CoreTec 5), APM Edge, Lumada/Hitachi Energy APM | Cảm biến TXpert Ready nhiều hãng: nhiệt, DGA, sứ… | Hơn 175 mô hình dựng sẵn; xác suất hư hỏng; APM + EAM + FSM; IDC Leader 2025–26 | Diagnostic → Predictive (đội máy), một phần Prescriptive | Mở với cảm biến bên thứ 3; IEC 62443-4-2 | CẦN KHẢO SÁT |
| Siemens Energy | Sensformer / Sensformer Advanced | IoT gateway: mức dầu, nhiệt dầu đỉnh, dòng hạ áp, GPS (+ DGA tùy chọn) | DT riêng từng máy từ dữ liệu thiết kế, thermo-hydraulic multi-mass; mô phỏng tải 24 h; quá tải chủ động; tuổi thọ | Descriptive + Predictive (nhiệt) rất mạnh | Gắn với MBA Siemens Energy; cloud | CẦN KHẢO SÁT |
| GE Vernova | Kelman DGA 900 / PLUS / TAPTRANS, MS 3000, Perception Fleet | 9 khí + ẩm (PAS); sứ, PD, OLTC, làm mát, camera nhiệt | Risk Index 1–5, xếp hạng đội máy, tốc độ khí theo đoạn | Diagnostic + Predictive (đội máy) | Modbus, DNP3, IEC 61850, SCADA | **Có**: EVNNPT 4 trạm 500 kV + Perception Server; Thủy điện Sông Bung 4 |
| Reinhausen (MR) | ETOS, ETOS ED, MSENSE, TESSA | DGA, sứ, rung–âm OLTC, sợi quang, ẩm | Thuật toán MR hoặc của khách; có **điều khiển** OLTC & làm mát | Diagnostic + điều khiển cục bộ (gần vòng kín) | Mở cảm biến bên thứ 3 | OLTC MR phổ biến (CẦN KHẢO SÁT số lượng) |
| Qualitrol | QTMS, Serveron TM8 | Module tới 196 DI; TM8 sắc ký khí (GC) 8 khí | Dựa luật (Duval 1/4/5, Pentagon, Rogers) | Descriptive + Diagnostic | IEC 61850 Ed 2 có chứng nhận, DNP3, Modbus, 104 | CẦN KHẢO SÁT |
| OMICRON | MONTRANO, MONTESTO 200, OMS 605 | Điện dung/tanδ sứ, PD, quá điện áp | Tách nhiễu, nhận dạng nguồn PD | Diagnostic chuyên sâu (điện môi) | Dùng được cảm biến hãng khác | Thiết bị thử nghiệm phổ biến (CẦN KHẢO SÁT phần monitoring) |
| Doble | Calisto R9, Calisto T1 / doblePRIME, INSIDEVIEW | DGA DIPAS, tự hiệu chuẩn bằng hơi nước; sứ IDD; PD | Health index đội máy (dữ liệu dầu, thí nghiệm) | Diagnostic + Predictive (đội máy) | Không cần cloud độc quyền (tuyên bố của hãng) | CẦN KHẢO SÁT |
| Camlin | TOTUS | DGA, PD, sứ, dòng sự cố xuyên qua | Phân tích nhúng tại thiết bị; Connected Insights | Diagnostic | Nhận dữ liệu online/offline | CẦN KHẢO SÁT |
| Dynamic Ratings | C50, E3, B100, DTM | Nhiệt, sứ, OLTC, làm mát, DGA, ẩm, PD | **Dynamic rating**: mô hình nhiệt tự hiệu chỉnh (bằng sáng chế) | Predictive (nhiệt/tải) | — | Có đại lý (TTECH) |
| Schneider Electric | EcoStruxure Transformer Expert | Đầu dò van dầu: ẩm, nhiệt, PD, rung, H2 | Cloud; thuật toán theo IEEE/IEC/CIGRE; thuê bao | Descriptive + Diagnostic | 3G/4G → cloud Schneider | CẦN KHẢO SÁT |

Ghi chú: cột "Mức TB 995" là đánh giá của Phòng dựa trên mô tả công khai của hãng, chưa đối chiếu bản đầy đủ TB 995.

## 4. Nhận định cạnh tranh
1. **Thị trường chia hai lớp**: (a) phần cứng giám sát chất lượng cao (GE, Qualitrol, Doble, MR, OMICRON, Camlin) và (b) phần mềm APM/DT đội máy (Hitachi Energy, GE Perception, Doble). Chỉ Siemens Energy có DT vật lý đúng nghĩa từ dữ liệu thiết kế, nhưng chủ yếu cho MBA của chính hãng.
2. **Chưa hãng nào vừa độc lập thiết bị, vừa có mô hình vật lý hiệu chỉnh theo dữ liệu từng máy, vừa lưu dữ liệu tại Việt Nam.** Đây là khoảng trống VTI có thể nhắm tới. Đánh giá này cần kiểm chứng thêm với khách hàng.
3. **Ngưỡng hồ sơ thầu** mà sản phẩm VTI phải đạt nếu cạnh tranh:
   - IEC 61850 Ed 2 có chứng nhận (như Qualitrol QTMS);
   - an ninh mạng IEC 62443-4-2 (như Hitachi TXpert Hub);
   - mô hình nhiệt theo IEC 60076-7, có khả năng hiệu chỉnh.
4. **GE đã có hạ tầng tại EVNNPT cấp 500 kV.** Chiến lược hợp lý là không thay thiết bị mà đọc dữ liệu từ thiết bị sẵn có để làm lớp DT phía trên. Hướng này cần xác minh xem EVNNPT có cho phép truy cập dữ liệu Perception Server không và qua giao thức nào.
5. **Bài học mô hình kinh doanh**: Doble bán hợp đồng giám sát trọn gói 10 năm, Schneider bán sensor-as-a-service. VTI có thể bán dịch vụ DT theo năm thay vì chỉ bán thiết bị.

## 5. Danh mục tài liệu anh cần upload bổ sung (theo mức ưu tiên)
Cách upload: tab **📚 Kho tài liệu** → chọn thư mục → kéo thả PDF → bấm **Nạp vào kho**. PDF bản quyền chỉ nằm trên máy anh, không lên GitHub.

| Ưu tiên | Tài liệu | Thư mục | Vì sao cần | Cách có |
|---|---|---|---|---|
| 1 | **CIGRE TB 995** – Digital twins for power transformers (2026) | 02_cigre_ieee | Tham chiếu chính về DT MBA; khung năng lực; checklist VVUQ | Miễn phí cho hội viên CIGRE (VTI/EVN có thể có tài khoản); không phải hội viên mua tại e-cigre.org |
| 1 | **IEC 60076-7:2018** | 01_standards | Công thức mô hình nhiệt, lão hóa, giới hạn nhiệt độ | IEC Webstore hoặc Tổng cục TCĐLCL; EVN thường có bản |
| 1 | **IEC 60599:2022** | 01_standards | Bảng tỷ số, giới hạn điển hình, Duval | IEC Webstore |
| 1 | **IEEE C57.104-2019** và **C57.143-2024** | 02_cigre_ieee | Giới hạn DGA theo phân vị 90/95; hướng dẫn chọn thiết bị giám sát | IEEE Xplore |
| 2 | CIGRE **TB 630, 761, 771, 783, 642** | 02_cigre_ieee | Kiến trúc giám sát thông minh, health index, DGA online, thống kê sự cố | e-cigre.org (miễn phí cho hội viên) |
| 2 | **IEC 61850-7-4 Ed 2.1** + **TR 61850-90-3** (+ bản nháp PAS nếu có) | 01_standards | Tên LN/DO chuẩn cho Substation DT | IEC Webstore |
| 2 | Brochure/datasheet chi tiết: TXpert Hub, APM Edge, Sensformer Advanced, ETOS/TESSA, QTMS, Calisto T1, TOTUS, MONTRANO | 03_vendor | Thông số kỹ thuật, giao thức, giới hạn – bản đầy đủ thường phải đăng ký mới tải được | Anh đăng ký trên web hãng, hoặc xin qua đại lý/đối tác |
| 2 | Bài Transformers Magazine: "Sensformer: Powering the future…" (2023), bài DT Sensformer Advanced (2022) | 05_papers | Chi tiết mô hình DT Siemens | Bản PDF 2023 tải được miễn phí tại hrcak.srce.hr |
| 3 | **ISO/IEC 30173:2023**, **IEC 63278-1:2023** | 01_standards | Định nghĩa DT chuẩn quốc tế; AAS | ISO/IEC store |
| 3 | Quy định EVN/EVNNPT về TBA không người trực, giám sát online; HSMT có hạng mục giám sát MBA | 04_vietnam | Tiêu chí kỹ thuật & thương mại thực tế tại VN | Anh có sẵn từ các gói thầu (ví dụ E1.20 Thanh Xuân) |
| 3 | Dữ liệu 1 MBA thật: nameplate, biên bản heat-run test, lịch sử DGA, file SCD | 06_vti_data (chỉ local) | Hiệu chỉnh mô hình nhiệt, thử Health Index | Khách hàng / dự án VTI |

## 6. Việc tiếp theo của Phòng
- Khi anh upload nhóm Ưu tiên 1: chạy lại các câu hỏi cũ để so sánh chất lượng trả lời trước và sau.
- Lập bảng đánh giá chi tiết theo checklist VVUQ của TB 995. Việc này cần bản gốc TB 995.
- Khảo sát thực tế tại Việt Nam: hãng nào đang có thiết bị trên MBA 110–220 kV của các Tổng công ty Điện lực; anh cung cấp thông tin từ thực tế thầu.

## Nguồn chính (đã truy cập 10/11/2026)
- IEC Webstore: 60076-7 (pub 34351), 60599 (pub 76192/66491), 61850-7-4 CSV (pub 66551), TR 61850-90-3 (pub 24777), 63278-1 (pub 65628)
- e-cigre.org: TB 995, 642, 783; Electra 347 (08/2026); CIGRE ToR JWG A2/D2.65 & A2/D1.67
- IEEE C57.143-2024: IEEE PES Transformers Committee F2025 tutorial; standards.ie; en-standard.eu
- Trang hãng: hitachienergy.com (TXpert Hub, APM Edge), siemens-energy.com, gevernova.com (brochure DGA 900/PLUS/TAPTRANS, Perception Fleet), reinhausen.com, qualitrolcorp.com, doble.com, camlingroup.com, se.com, dynamicratings (electricityforum), OMICRON (TDWorld)
- Việt Nam: tapchicongthuong.vn (EVNNPT MS 3000; Thủy điện Sông Bung 4)

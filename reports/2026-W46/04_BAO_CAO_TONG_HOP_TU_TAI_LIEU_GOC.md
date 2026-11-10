# Báo cáo #3 – Tổng hợp kiến thức Digital Twin máy biến áp từ tài liệu gốc & kiến trúc tham chiếu cho VTI

Ngày 10/11/2026 · Phòng R&D Digital Twin · GĐ1 – Nền tảng tri thức · Căn cứ: 26 tài liệu gốc anh Khương đã đưa vào thư mục library, cộng tra cứu web cho phần còn thiếu.

## 1. Tóm tắt điều hành
- **Định nghĩa chuẩn để dùng với khách hàng** (CIGRE TB 995): DT là biểu diễn ảo của MBA, được cập nhật động bằng dữ liệu thật, có khả năng dự báo, hỗ trợ ra quyết định, tương tác hai chiều. Một hệ giám sát online chỉ hiển thị số liệu mới đạt **cấp 1 (Descriptive)** trong 5 cấp, chưa phải DT đầy đủ.
- **Thực trạng thế giới**: trong 70 chuyên gia khảo sát (2024–2025), 60 % tổ chức có dự án DT nhưng chỉ khoảng 24 % số dự án đã vận hành. 64 % đạt cấp 1, đa số đặt mục tiêu cấp 2 trong 3 năm. Rào cản số 1 là chất lượng dữ liệu (hơn 84 %), số 2 là tích hợp hệ thống (khoảng 71 %). → **Thị trường còn sớm, VTI chưa bị bỏ xa.**
- **Với lưới 110 kV Việt Nam** (TB 642, nhóm 100–200 kV): suất sự cố 0,43 %/năm. Vị trí sự cố: cuộn dây 43,5 %, **OLTC 34,2 %**, sứ 13 %. → DT 110 kV nên ưu tiên OLTC, cuộn dây (DGA + nhiệt) và sứ.
- **Lõi kỹ thuật có thể tự làm ngay**: mô hình nhiệt và lão hóa IEC 60076-7 (đủ bảng thông số), quy trình DGA IEC 60599 Điều 9 (giá trị điển hình, tỷ số, CO2/CO), mô hình dữ liệu IEC 61850-90-3 (SIML, SPDC, SPTR, SIMS, SSTP, SBSH, SCGR, SLTC), cùng checklist VVUQ của TB 995 làm tiêu chí nghiệm thu.
- **Lợi thế pháp lý cho giải pháp xử lý tại Việt Nam**:
  - Luật Dữ liệu 60/2024/QH15, Điều 23, coi việc *dùng nền tảng đặt ngoài lãnh thổ để xử lý* dữ liệu quan trọng/cốt lõi là chuyển dữ liệu xuyên biên giới.
  - Nghị định 165/2025/NĐ-CP yêu cầu lập báo cáo đánh giá tác động trước khi chuyển.
  - Cần xác minh dữ liệu vận hành lưới điện có nằm trong danh mục "dữ liệu quan trọng" hay không.

## 2. Tài liệu đã đọc và mức sử dụng
| Nhóm | Tài liệu gốc trong kho | Dùng cho |
|---|---|---|
| Khung DT | CIGRE TB 995 (2026) | Định nghĩa, 5 cấp năng lực, khảo sát, VVUQ, khuyến nghị → Fact sheet 03 |
| Nhiệt & lão hóa | IEC 60076-7:2018 | Công thức V, L; Bảng 2–4 (giới hạn nhiệt, giới hạn dòng, thông số nhiệt) |
| DGA | IEC 60599:2022; CIGRE TB 771, TB 783 | Bảng 1, A.2, A.3; tiểu loại lỗi S/O/C/T3-H; phân loại monitor M1–M9, độ chính xác |
| Mô hình dữ liệu | IEC TR 61850-90-3:2016 + Cor.1; IEC 61850-7-4 Ed 2.1; đặc tả AAS của IDTA | LN cho MBA/LTC; "hộ chiếu số" AAS |
| Đánh giá tình trạng | CIGRE TB 761, 630, 343, 298, 445 | Chỉ số đánh giá MBA (TAI) 5 bước; kiến trúc TICM; dữ liệu vòng đời |
| Độ tin cậy | CIGRE TB 642 | Suất sự cố và vị trí sự cố theo cấp điện áp |
| Thị trường | Brochure GE (DGA 900 PLUS, TAPTRANS, Perception Fleet), doblePRIME, Siemens PR 2019; bài Sensformer (Sherekar & Pandya) | Đối chiếu tính năng hãng |
| Bài báo | Das & Grisaru 2026 (cảnh báo DGA online); Das (APM Edge); Sparling (đánh giá tài sản dựa trên bằng chứng); arXiv 1909.02451 (Dominion) | Thực hành vận hành |
| Pháp lý | Luật Dữ liệu (bản tiếng Anh) | Điều 23 xuyên biên giới, phân loại dữ liệu |

**Phần còn thiếu đã bù bằng tra cứu web (mức tin cậy thấp hơn bản gốc)**:
- IEEE C57.104-2019, C57.143-2024, C57.91-2025: phạm vi, phiên bản, cách phân trạng thái DGA;
- CIGRE TB 962 và TB 659;
- Nghị định 165/2025/NĐ-CP, Luật BVDLCN 91/2025;
- tính năng Hitachi, MR, Qualitrol, OMICRON, Camlin, Schneider (từ trang hãng).

## 3. Đính chính sau khi đọc bản gốc
| Trước đây | Đúng theo bản gốc / nguồn mới |
|---|---|
| "TB 783: DGA online lệch ±20–30 % so với phòng thí nghiệm" | TB 783 kết luận: đa số khoảng 20 monitor thử nghiệm đạt ±15 % (yêu cầu IEC), một số không đạt. Dưới 10 ppm sai số thường trên 50 %, chẩn đoán vô nghĩa. Con số ±20–30 % là của bài báo Das & Grisaru (2026). |
| IEEE C57.91-2011 | Bản hiện hành **C57.91-2025** (phát hành 05/03/2026, có mã nguồn mở) |
| CIGRE TB 445 (bảo dưỡng) | Đã được thay bằng **TB 962 (2025)** |
| Tên các cấp TB 995 "CẦN KIỂM CHỨNG" | Đã xác nhận: Descriptive → Diagnostic → Predictive → Prescriptive → Autonomous |
| TB 642 chỉ có số liệu chung | Có số liệu riêng nhóm 100–200 kV: suất sự cố 0,43 %, OLTC 34,2 % |
| Công cụ nhiệt trong app có lựa chọn "OFAF/ODAF" (gây lỗi) | Sửa thành ONAN/ONAF/OF/OD đúng như Bảng 4 IEC 60076-7 |

## 4. Kiến trúc tham chiếu Transformer DT 110 kV (đề xuất của Phòng, bám TB 995)
| Cấp TB 995 | Chức năng cho MBA 110 kV | Căn cứ tiêu chuẩn | Dữ liệu cần |
|---|---|---|---|
| 1 Descriptive | Hiển thị thời gian thực tải, θo, θh (đo hoặc tính), DGA, trạng thái làm mát, nấc OLTC | IEC 61850-90-3 (SIML, SPTR, SCGR, SLTC, TTMP…); IEC 61850-7-4 | SCADA/IED, monitor DGA, cảm biến nhiệt |
| 2 Diagnostic | Kiểm tra DGA theo giá trị điển hình và tốc độ tăng → tỷ số/Duval (gồm Duval 2 cho OLTC); CO2/CO; so sánh θ đo với θ mô hình để phát hiện lỗi làm mát | IEC 60599 Điều 9, Bảng A.2/A.3; TB 771; TB 783 (biết giới hạn của loại monitor M1–M9) | DGA online + phòng thí nghiệm, lịch sử bảo dưỡng |
| 3 Predictive | Mô hình nhiệt IEC 60076-7 hiệu chỉnh theo heat-run/dữ liệu vận hành (grey-box); lão hóa V, L; dự báo θh 24 h theo dự báo tải; xu hướng khí; chỉ số TAI | IEC 60076-7 (Bảng 2–4); TB 995 mục 5.3; TB 761 | Biên bản heat-run test, nameplate, dự báo tải, thời tiết |
| 4 Prescriptive | Gợi ý giới hạn tải theo kịch bản what-if (có khoảng bất định); thời điểm lọc dầu/bảo dưỡng OLTC | IEC 60076-7 Bảng 2–3; TB 962; TB 995 mục 7 | Kế hoạch vận hành, chi phí |
| 5 Autonomous | (Chưa đặt mục tiêu: 52 % ngành không định làm) | – | – |

**Tiêu chí nghiệm thu đề xuất** (từ TB 995 mục 7.12 và 8.5):
- Sai số θo/θh của mô hình theo MAE (ngưỡng thỏa thuận với khách hàng);
- Kiểm chứng monitor DGA bằng mẫu chuẩn gas-in-oil và đối chiếu phòng thí nghiệm;
- Audit trail mọi lần hiệu chỉnh mô hình;
- Chạy song song DT offline trước khi đưa vào dùng;
- DT vẫn chạy ở chế độ suy giảm khi mất cảm biến;
- Kết quả trình bày dạng khoảng, không chỉ một con số.

## 5. Định vị thị trường theo 5 cấp (cập nhật từ brochure gốc)
- **GE Vernova**:
  - DGA 900 PLUS/TAPTRANS có add-on mô hình nhiệt (thermal models), giám sát làm mát, OLTC, sứ (tới 9 sứ), PD.
  - Chuẩn: Modbus RS485/TCP và DNP3 TCP/IP; IEC 61850 Ed 2 là tùy chọn; có webserver https.
  - Perception Fleet tính Risk Index 1–5 dựa trên các tiêu chuẩn IEC, IEEE, ASTM, ISO, DIN, CIGRE, EPRI; tốc độ khí tính theo từng đoạn tuyến tính (piecewise linear).
  - Mức: cấp 2–3 ở cấp đội máy.
  - Tại Việt Nam: EVNNPT đã có MS 3000 + Perception Server ở 4 trạm 500 kV.
- **Siemens Energy Sensformer Advanced**: DT nhiệt dựng từ dữ liệu thiết kế (multi-mass), quá tải chủ động, tuổi thọ. Gateway IoT gửi dữ liệu lên cloud qua GSM/LAN, bảo mật theo ISO/IEC 27001. Mức: cấp 3 về nhiệt. Phụ thuộc cloud → vướng Điều 23 Luật Dữ liệu nếu dữ liệu thuộc loại quan trọng.
- **Doble doblePRIME**: gói Essential → Advanced+ (DGA Calisto, sứ IDD, PD, GIC, dữ liệu vận hành); hợp đồng trọn gói dobleASSURANCE. Mức: cấp 2–3.
- **Hitachi Energy, Reinhausen, Qualitrol, OMICRON, Camlin, Schneider**: xem Báo cáo #2 (nguồn web). Cần brochure đầy đủ để đánh giá sâu hơn.
- **Khoảng trống cho VTI** (khớp với khuyến nghị TB 995 về tiêu chuẩn mở và grey-box cho MBA cũ):
  - lớp DT độc lập hãng, đọc dữ liệu từ thiết bị có sẵn qua IEC 61850/Modbus/DNP3;
  - mô hình nhiệt grey-box hiệu chỉnh theo từng máy;
  - DGA theo IEC 60599 và TB 771/783 có kiểm soát độ chính xác thiết bị;
  - xử lý dữ liệu tại Việt Nam;
  - giao diện tiếng Việt.

## 6. Hàm ý cho lộ trình nghiên cứu
- **GĐ2 (12/2026–01/2027)**: lập bảng đánh giá 10 hãng theo 5 cấp TB 995 và checklist VVUQ. Cần brochure/datasheet đầy đủ của Hitachi, MR, Qualitrol, Camlin.
- **GĐ3 (01–04/2027)**:
  - hoàn thiện cấp 1–3 trên DT-RnD-Lab với dữ liệu 1 MBA thật (heat-run + DGA + SCD);
  - hiệu chỉnh mô hình nhiệt và đo MAE;
  - xây ma trận TAI theo TB 761;
  - thêm Duval 2 cho OLTC và Duval 4/5/Pentagon theo TB 771.
- **GĐ4**: hồ sơ thuyết phục khách hàng dựa trên TB 995 (định nghĩa, cấp năng lực, VVUQ), TB 642 (số liệu 110 kV) và Luật Dữ liệu (lợi thế xử lý tại Việt Nam).

## 7. Tài liệu còn thiếu – ưu tiên tải tiếp
| Ưu tiên | Tài liệu | Lý do | Cách có |
|---|---|---|---|
| 1 | **CIGRE TB 659** – Transformer thermal modelling (2016) | TB 995 dẫn chiếu cho mô hình nhiệt; THNM | **Miễn phí** (trên 3 năm) – e-cigre.org |
| 1 | **CIGRE TB 962** – Guide for transformer maintenance (2025) | Thay TB 445 | Hội viên CIGRE hoặc mua |
| 1 | **IEEE C57.104-2019** | Bảng phân vị 90/95, trạng thái DGA 1/2/3 | IEEE Xplore (khoảng 114 USD) |
| 2 | IEEE C57.91-2025, C57.143-2024 | Mô hình nhiệt IEEE, hướng dẫn chọn thiết bị giám sát | IEEE |
| 2 | IEC 60076-2:2011 (độ tăng nhiệt) | TB 995 lưu ý hệ số mũ khác 60076-7 | IEC Webstore |
| 2 | CIGRE TB 443, 676, 755, 939 | DGA OLTC/dầu este; PD; độ tin cậy sứ; độ tin cậy MBA AC mới | e-cigre.org (phần lớn miễn phí) |
| 2 | Brochure đầy đủ: Hitachi TXpert Hub/APM Edge, MR ETOS/TESSA, Qualitrol QTMS, Camlin TOTUS, OMICRON MONTRANO | Đánh giá cấp năng lực | Đăng ký trên web hãng |
| 3 | Nghị định 165/2025/NĐ-CP; Quyết định danh mục dữ liệu quan trọng/cốt lõi | Xác định dữ liệu lưới điện có thuộc diện không | thuvienphapluat.vn / Công báo |
| 3 | Dữ liệu 1 MBA 110 kV thật (nameplate, heat-run, DGA nhiều năm, SCD) | Hiệu chỉnh mô hình (cấp 3) | Dự án VTI / khách hàng → thư mục 06_vti_data |

## 8. Cải tiến đã làm trên DT-RnD-Lab trong đợt này
- Kho tri thức: thêm Fact sheet 03 (TB 995). Viết lại Fact sheet 01, 02 và 20 theo bản gốc, đánh dấu ✅ (đã đọc bản gốc) hoặc 🌐 (nguồn web).
- Hỏi đáp: Trưởng phòng sinh thêm từ khóa tiếng Anh để tìm trong tài liệu gốc tiếng Anh; mỗi câu lấy 12 đoạn tham khảo; tăng tốc tìm kiếm cho kho lớn (khoảng 3.600 đoạn).
- Công cụ DGA: thêm bước kiểm tra giá trị điển hình (IEC 60599 Bảng A.2), nhập CO/CO2 để xét CO2/CO, tùy chọn OLTC thông dầu; cập nhật lưu ý độ chính xác theo TB 783.
- Công cụ nhiệt: sửa lỗi kiểu làm mát (OF/OD).

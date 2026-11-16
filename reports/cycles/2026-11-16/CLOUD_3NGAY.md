# Báo cáo 3 ngày Phòng R&D (Claude) – 16/11/2026

> Chu kỳ 14–16/11/2026. Module **active**: 🧬 Digital Twin (GĐ1 – Nền tảng tri thức, ngày 6/40) và 📊 Thị trường (GĐ1 – Bản đồ khách hàng & kênh thông tin, ngày 6/51). Module **standby**: 📡 Monitoring (GĐ1 theo lịch đã bắt đầu từ 15/11 nhưng chưa được kích hoạt), 🩺 Asset Health, 🔋 BESS. Vẫn chưa có `BAO_CAO_3_NGAY.md` của Qwen local trong `reports/cycles/`. Đã đối chiếu với `CLOUD_3NGAY.md` 13/11 và bản tin 14–16/11 để tránh lặp: các tin đã đưa (EVNNPT kế hoạch 2027, BESS EVNNPC 530 MW, hội thảo EVN–ULSE, khung giá LNG/ĐMT, Siemens Energy mua Camlin, TBA 500 kV Nam Định/Điện Biên…) không nhắc lại, trừ khi có chi tiết mới.

## Tóm tắt điều hành – điểm mới trong 3 ngày

1. **[🧬 DT – Tiêu chuẩn] Phát hiện 2 dự án tiêu chuẩn IEEE nhắm thẳng vào phạm vi của VTI:** **IEEE PC57.145** – Guide for Digital Twin Modeling and Analysis of Power Transformers 69–161 kV (PAR duyệt 05/06/2023, đang soạn) – trùng đúng cấp MBA 110 kV; và **IEEE P3575** – Guide for Construction of Digital Twin Substation, Part 1 (TBA AC/DC >110 kV, PAR 13/02/2025). Đây là hai khung tham chiếu cần bám bên cạnh CIGRE TB 995 và ISO/IEC 30188.
2. **[🧬 DT – Mô hình vật lý] Đã đọc được toàn văn Part I loạt bài "Beyond fixed limits" (Das & Grisaru, Transformers Magazine 05/2026)** – bộ quy tắc cảnh báo DGA online theo baseline riêng từng MBA + phân vị quần thể + ROC, có bảng ngưỡng sàng lọc ppm hai mức. Đây là "bản nháp ngưỡng" dùng ngay được cho câu hỏi thường trực DGA của chuyên viên physics (và cho module 📡 khi kích hoạt).
3. **[🧬 DT – Data/AI] PINN cho top‑oil (UQ, PESGM 2026) cho số liệu so sánh cụ thể:** MAE 1,45 K / R² 0,93 so với mô hình IEEE 2,49 K / 0,82 trên MBA 1,4 MVA; nhưng mọi mô hình đều ước lượng thấp đỉnh nhiệt và chưa thử ở quá tải. Kết hợp với kết quả TenneT/Statnett chu kỳ trước → kiến trúc lai vật lý + ML là hướng đúng, nhưng lớp vật lý (IEC 60076‑7) vẫn phải là "lưới an toàn" ở vùng quá tải.
4. **[🧬 DT – Benchmark] Thêm 2 case "đội MBA" của utility:** POWERGRID (CIGRE A2‑10255, DT học máy từ DGA + dữ liệu thời gian thực + thí nghiệm định kỳ, huấn luyện trên MBA đã hỏng) và **PG&E × Camlin** (nền tảng condition assessment + prescriptive analytics + DT cho MBA trọng yếu, trình bày tại DTECH 03/2027). Hitachi Energy HMAX Energy (04/2026) công bố giảm 50% sự cố MBA nhờ phát hiện sớm – số liệu tự công bố của hãng.
5. **[📊 Thị trường] Bản đồ khách hàng: thêm tín hiệu nhu cầu từ EVNNPT và EVNCPC** – TBA 500 kV Đức Hòa đã lắp online DGA cho AT2 và số hóa 100% dữ liệu thiết bị lên PMIS; PTC2 nghiệm thu đề tài giám sát an toàn TBA bằng RTK + camera AI; PC Huế (EVNCPC) tự phát triển robot tuần tra TBA 110 kV không người trực. → Các đơn vị đang tự làm lớp "giám sát", khoảng trống còn lại là lớp **phân tích/DT/Risk Index** tích hợp PMIS. Chưa có kết quả gói BESS GĐ3‑G06 (314 tỷ).

## Mới nghiên cứu / bổ sung theo từng module

### 🧬 Digital Twin ngành điện

**Giai đoạn:** GĐ1 – Nền tảng tri thức (11/11 → 20/12/2026), ngày 6/40. Tiến độ ước tính ~18% (chu kỳ trước ~10%): bổ sung lớp tiêu chuẩn IEEE đang soạn, bộ ngưỡng DGA có cấu trúc, số liệu PINN và 2 case utility. Chưa làm được: bảng ánh xạ tín hiệu → LN IEC 61850‑90‑3 (đang chờ bản PAS), repo Python TenneT (không tìm thấy link công khai).

**Chuyên viên Mô hình vật lý thiết bị (physics)**
- *DGA cảnh báo sớm – Das & Grisaru Part I (Transformers Magazine Vol.13 SE1, 07/05/2026, Hrčak, truy cập mở)* [W1][W2]:
  - Baseline riêng từng MBA từ 30–90 ngày vận hành ổn định, bỏ giai đoạn đóng điện/xử lý dầu; dùng trung vị và phân vị 10/90 thay vì trung bình; đánh giá lại phân vị 90 mỗi 12–24 tháng.
  - Phân tầng cảnh báo: ≤ P90 riêng → bình thường; > P90 riêng nhưng < IEEE 90% → theo dõi; > cả hai và ROC tăng → Alert; > IEEE 95% + ROC tăng → Alarm L1; ≈ mức CIGRE Level 2 → Alarm L2.
  - Ngưỡng sàng lọc tạm (ppm, L1/L2): H₂ 100/250, CH₄ 120/180, C₂H₆ 150/300, C₂H₄ 80/200, **C₂H₂ 5/40**, CO 1200/2000, CO₂ 13000/20000 – chỉ cho dầu khoáng, phải chỉnh lại sau khi có baseline.
  - ROC: ưu tiên cửa sổ cố định theo ngày (nửa đêm – nửa đêm), tránh kích hoạt theo ROC 1 ngày/7 ngày vì khuếch đại nhiễu; xác nhận bằng vượt ngưỡng kéo dài 7–14 ngày; chỉ áp Duval/Rogers/IEC ratio sau khi xu hướng bất thường được xác nhận; không trộn dữ liệu online với PTN khi chưa biết độ lệch (TB 783: tới ±20–30% từng khí).
  - Lưu ý: bài có chỗ tự mâu thuẫn (Bảng 1 coi "vượt P90 kéo dài" là chỉ theo dõi, Bảng 3 xếp vào Alert) → cần đọc Part II (phần tính ROC) trước khi đưa vào sản phẩm.
- *PINN cho nhiệt độ dầu đỉnh (UQ – PESGM 2026)* [W3]: ANN 2 lớp ẩn + hàm loss vật lý theo mô hình Susa; dữ liệu MBA inverter 1,4 MVA, mẫu 15 phút, ~20 tháng. Kết quả: PINN MAE 1,45 / RMSE 2,00 / R² 0,93; ANN 1,99 / 2,60 / 0,88; mô hình IEEE 2,49 / 3,23 / 0,82. Hạn chế: chỉ dự báo top‑oil (chưa hot‑spot), ước lượng thấp đỉnh, chưa thử quá tải/sự cố. (Link đã có trong bản tin 10/11, chu kỳ này mới đọc nội dung.)
- Repo Python mở của TenneT (A2‑10270): chưa tìm thấy link công khai qua tìm kiếm; trang e‑CIGRE không dẫn link → cần đọc toàn văn bài (mua) để lấy địa chỉ repo. [W4]

**Chuyên viên Substation DT (trạm 110 kV)**
- *IEEE P3575 – Guide for Construction of Digital Twin Substation, Part 1: General Provisions* (TBA AC/DC >110 kV; yêu cầu cơ bản, khung tổng thể, đặc tả tích hợp; PAR 13/02/2025, đang soạn) – khung gần nhất với câu hỏi "dựng Substation DT 110 kV thế nào". [W5]
- *Hệ sinh thái mã nguồn mở IEC 61850 (LF Energy)*: OpenSCD (soạn SCL), CoMPAS (module cấu hình), SEAPATH (hypervisor TBA số), libiec61850 (C, GPL v3). Tác giả nhận xét chưa có cách dựng "virtual substation" nhẹ cho phát triển và các dự án chưa ghép thành một stack hoàn chỉnh → đúng khoảng trống công cụ "SCD → topology → DT" mà VTI có thể lấp. (Bài 09/2025, không mới nhưng chưa có trong kho.) [W6]
- *Curtin University (Energies 19(3):703, 01/2026, truy cập mở)*: relay quá dòng ảo IEC 61850 trên Raspberry Pi 5 + libiec61850 (SV, GOOSE, MMS report), GOOSE 0,2–1,9 ms (<4 ms theo 61850‑8‑1); ICD chạy được trên Schneider CET850 nhưng không nhập được vào ABB PCM600 → bằng chứng thực tế về rủi ro tương thích công cụ khi VTI tự sinh file SCL. [W7]
- *CIGRE D2‑12215 (2026, EPM/UNAL/ITM – Colombia)*: mô hình an ninh mạng cho TBA số IEC 61850 theo NIST SP 800‑82r3 + IEC 62443 + ISO/IEC 27019; 4 kịch bản rủi ro cao (giả mạo GOOSE, DoS đồng bộ thời gian, truy cập SCADA trái phép, thao túng SV) giảm còn 1 mức trung bình (−75%). Bổ sung cho "cyber layer" (CyberTwin D2‑10667 chu kỳ trước). [W8]

**Khối dùng chung – Tiêu chuẩn & Kiến trúc**
- **IEEE PC57.145** – DT cho MBA 69–161 kV: phạm vi gồm triển khai thu thập dữ liệu, quản lý dữ liệu, kiến trúc thông tin, xử lý dữ liệu cho mô hình số, dịch vụ ứng dụng, cấu trúc dữ liệu không gian‑thời gian và "chỉ số tự động hóa TBA DT". PAR 05/06/2023, Active PAR. [W9]
- **IEEE P3988** – DT đường dây trên không và cột trong thời tiết cực đoan (PAR 26/03/2026) – ghi nhận cho tương lai (DLR/ĐZ). [W10]
- IEC 61850‑90‑3 Ed1 PAS: chưa thấy thông tin ban hành mới ngoài blog NettedAutomation 06/08/2026. [W11]

**Khối dùng chung – Dữ liệu & AI**
- Từ Das & Grisaru: baseline theo phân vị + ROC là giải pháp "cold start" thực dụng (30–90 ngày) – ngắn hơn yêu cầu ≥3 tháng của Neural ODE (Statnett). Gợi ý thiết kế: giai đoạn đầu pilot dùng luật thống kê + IEC 60076‑7, sau ≥3 tháng mới bật lớp ML. [W2]

**Khối dùng chung – OT/An ninh mạng**
- D2‑12215 cho danh mục 4 kịch bản tấn công mẫu và bộ kiểm soát theo IEC 62443 – dùng làm checklist khi thiết kế kết nối DT ↔ hệ thống IEC 61850 của trạm. [W8]

**Khối dùng chung – Benchmark**
- POWERGRID **A2‑10255 (2026)**: DT học máy kết hợp DGA + dữ liệu thời gian thực + thí nghiệm định kỳ, chọn thuật toán trên dữ liệu lịch sử của MBA đã hỏng (case POWERGRID thứ 3 sau A2‑10207, A3‑10816). [W12]
- **PG&E × Camlin (DTECH 2027, 04/03/2027)**: hợp nhất dữ liệu bảo dưỡng + mang tải + cảm biến online → đánh giá sức khỏe đội MBA có xếp hạng ưu tiên, chẩn đoán suy giảm và khuyến nghị hành động; nhấn mạnh phương pháp HI truyền thống hụt khi NLTT làm thay đổi kiểu mang tải. Camlin nay thuộc Siemens Energy. [W13]
- **Hitachi Energy HMAX Energy (24/04/2026)**: "Plan – Predict – Prevent", DT làm nền; hãng công bố giảm 50% sự cố MBA và tới 75% chi phí sửa chữa (chưa có kiểm chứng độc lập). [W14]

**Trả lời câu hỏi nghiên cứu (cập nhật)**
- *Kiến trúc cho trạm 110 kV không người trực:* bổ sung 2 khung IEEE (PC57.145 cho MBA 69–161 kV, P3575 cho TBA >110 kV) → đề xuất VTI thiết kế theo 3 lớp: thu thập (IEC 61850/104, có checklist IEC 62443) → DT vật lý + luật thống kê DGA → Risk Index/khuyến nghị tích hợp PMIS của EVN.
- *Mức DT trong 12 tháng:* Descriptive + Diagnostic khả thi ngay từ ngày đầu pilot (luật baseline DGA, IEC 60076‑7); Predictive (PINN/Neural ODE) chỉ sau ≥3 tháng dữ liệu.

### 📊 Thị trường, Đấu thầu & Cơ hội VTI

**Giai đoạn:** GĐ1 – Bản đồ khách hàng & kênh thông tin (11/11 → 31/12/2026), ngày 6/51. Tiến độ ~15%: thêm hồ sơ hiện trạng số hóa tại EVNNPT (Đức Hòa, PTC2) và EVNCPC (PC Huế); làm rõ cấu trúc gói BESS EVNNPC.

**Chuyên viên Phân tích đấu thầu**
- Gói BESS GĐ3‑G06 (Bắc Ninh, Thái Nguyên, >314 tỷ): **chưa có kết quả LCNT** công bố trên Báo Đấu thầu tính đến 16/11. [W15]
- Làm rõ cấu trúc gói EVNNPC (Báo Đấu thầu 13/10): GĐ2 >1.337 tỷ (G05 Bắc Ninh–Thái Nguyên 122,3 tỷ/5 nhà thầu; G06 Phú Thọ–Tuyên Quang 159,4 tỷ/5; G07 Hà Tĩnh 175,1 tỷ/4; G10 Nghệ An 156,7 tỷ/3); GĐ3 ~724 tỷ (G06 >314 tỷ; G05 Hưng Yên–Thanh Hóa–Ninh Bình ~275 tỷ, đóng thầu 24/10). Lưu ý **mã G06 trùng giữa GĐ2 và GĐ3** – khi theo dõi phải ghi kèm giai đoạn. GĐ1: 22 hệ/145 MW đã đóng điện đến 28/09. [W15]
- Hai TBMT sửa chữa TBA 110 kV (EVNSPC – Bình Đại/Giao Long…) vẫn không truy cập được trên dauthau.asia; phát hiện thêm TBMT tương tự "sửa chữa kiến trúc TBA 110 kV Duyên Trà, Cầu Ngang, Long Đức" – tên gói cho thấy là xây lắp/kiến trúc, khả năng có hạng mục giám sát thấp. [W16]

**Chuyên viên Theo dõi đối thủ & đối tác**
- Nhà thầu BESS: Á Châu (Kỹ thuật Công nghiệp Á Châu) thắng G08 (~205,7 tỷ, 14/15 nhà thầu bị loại về năng lực/kỹ thuật) và G11 (~206,6 tỷ); nhà thầu ngoại tham gia GĐ2: Resource Electric Tianjin, CYG Sunri, Guangzhou Renepoly → hàng rào kỹ thuật cao, đối tác nội nắm thế. [W15]
- Hitachi Energy (HMAX Energy) và Siemens Energy (+Camlin) đều đóng gói "DT + AI + dịch vụ chuyên gia" cho đội MBA → đối thủ trực tiếp của sản phẩm Transformer DT VTI ở phân khúc cao; lợi thế VTI phải là tích hợp PMIS/SCADA EVN, chi phí và hỗ trợ tại chỗ. [W13][W14]

**Hồ sơ khách hàng – cập nhật**
- **EVNNPT – TBA 500 kV Đức Hòa (03/09/2026; đơn vị quản lý trực tiếp cần xác nhận, dự kiến PTC4):** online DGA trên AT2; 100% dữ liệu thiết bị trên PMIS; MDMS V2; camera; Istation; báo cáo 48 chu kỳ/ngày tự động bằng Excel → PMIS là "nguồn sự thật" mà DT phải kết nối. [W17]
- **EVNNPT/PTC2 (28/08/2026):** nghiệm thu đề tài giám sát & cảnh báo an toàn TBA (RTK + camera AI), dự kiến nhân rộng toàn EVNNPT. [W18]
- **EVNCPC/PC Huế (02/2026):** robot tự hành tuần tra TBA 110 kV không người trực (camera, nhiệt, âm thanh, IoT + AI). [W19]

## Tài liệu nên bổ sung vào kho

| Tài liệu | Module | Nguồn/giá | Ghi chú |
|---|---|---|---|
| Das & Grisaru – "Beyond fixed limits… Online DGA alarm strategy" Part I (Transformers Magazine 2026) | 🧬 physics / 📡 | **Miễn phí** (Hrčak): https://hrcak.srce.hr/file/501125 – trang: https://hrcak.srce.hr/en/347231 | Ưu tiên cao; tìm Part II trên Hrčak |
| Bhattarai et al. – Physics‑informed NN for Transformer Thermal Modelling (PESGM 2026) | 🧬 physics / data_ai | **Miễn phí**: https://index.mirasmart.com/PESGM2026/PDFfiles/PESGM2026-001074.pdf | `05_papers` |
| Lopez et al. – Programmable DT via IEC 61850 (Energies 19(3):703) | 🧬 substation | **Miễn phí** (CC BY): https://www.mdpi.com/1996-1073/19/3/703 | Tham chiếu libiec61850 |
| CIGRE A2‑10255 (2026) – ML DT of a power transformer (POWERGRID) | 🧬 benchmark | 30 € (20 € hội viên) | |
| CIGRE D2‑12215 (2026) – Cybersecurity model for digital substations | 🧬 ot_cyber | 30 € (20 € hội viên) | |
| IEEE PC57.145 / IEEE P3575 (bản dự thảo) | 🧬 standards | Chưa ban hành – chỉ thành viên WG xem được dự thảo | Theo dõi; cân nhắc tham gia WG |

Tổng chi đợt này (nếu duyệt): 2 bài CIGRE ≈ 60 € (≈40 € hội viên), cộng dồn với đề xuất chu kỳ trước (≈180 € + CHF 159) chưa có quyết định.

## Cơ hội & tin đáng chú ý cho VTI

- **[🧬/📊] "Lớp phân tích trên PMIS" cho EVNNPT:** Đức Hòa đã có online DGA + PMIS số hóa 100% nhưng chưa có lớp chẩn đoán/Risk Index → đề xuất PoC Transformer DT đọc dữ liệu PMIS + DGA online cho 1–2 MBA 500/220 kV tại Đức Hòa, áp bộ luật baseline/ROC (Das & Grisaru) ngay từ ngày đầu.
- **[🧬 substation/📊] Hợp tác với đơn vị tự phát triển ở EVNCPC/EVNNPT:** robot tuần tra (PC Huế) và giám sát an toàn RTK + AI (PTC2) là nguồn dữ liệu đầu vào cho Substation DT; VTI có thể đóng vai tích hợp nền tảng thay vì cạnh tranh.
- **[🧬 standards] Tham gia nhóm soạn IEEE PC57.145 / P3575:** tham gia WG giúp tiếp cận dự thảo sớm và tạo uy tín khi chào hàng EVN.
- **[📡 standby – nếu kích hoạt]** Bộ ngưỡng DGA online hai mức + quy trình xác nhận 7–14 ngày là nội dung có thể đóng gói thành "DGA alarm policy" kèm thiết bị cho các gói PV Power (Cà Mau 2) và MBA 500 kV mới.
- **[🩺 standby – nếu kích hoạt]** Case PG&E × Camlin cho thấy HI truyền thống hụt khi kiểu mang tải thay đổi do NLTT – lý lẽ tốt cho Health Index động tại VN.
- **[🔋 standby – nếu kích hoạt]** Cạnh tranh BESS rất gắt (G08: 14/15 nhà thầu bị loại) → VTI chỉ nên vào ở vai trò thầu phụ giám sát/EMS cho Á Châu và các nhà thầu nội.

## Rủi ro, mâu thuẫn & điều cần kiểm chứng

- **Das & Grisaru Part I tự mâu thuẫn** giữa Bảng 1 và Bảng 3 về mức xử lý khi vượt P90 kéo dài; ngưỡng là "provisional", chỉ cho dầu khoáng → không đưa vào hồ sơ chào hàng trước khi đọc Part II và đối chiếu IEEE C57.104‑2019, CIGRE TB 771.
- **IEEE PC57.145 và P3575 mới là Active PAR**, chưa có nội dung công khai; PAR PC57.145 từ 2023 → có thể sắp hết hạn/gia hạn – kiểm tra trang IEEE SA định kỳ.
- **Số liệu HMAX (−50% sự cố, −75% chi phí sửa chữa)** do Hitachi tự công bố, không nêu điều kiện so sánh.
- **PINN UQ** thử trên MBA 1,4 MVA của nhà máy PV, điều kiện vận hành bình thường → chưa suy ra cho MBA 110 kV quá tải mùa khô.
- Tên viết tắt "ACIT" chưa được xác nhận trong nguồn (Báo Đấu thầu ghi tên đầy đủ "Kỹ thuật Công nghiệp Á Châu") – các báo cáo trước dùng "ACIT", cần thống nhất.
- Mã gói G06 trùng giữa BESS GĐ2 và GĐ3 của EVNNPC – nguy cơ nhầm khi theo dõi.
- dauthau.asia tiếp tục không truy cập được từ môi trường chạy → hai TBMT EVNSPC cần anh/em kiểm tra thủ công.
- Chưa có báo cáo Qwen local để phản biện chéo (chu kỳ thứ 2 liên tiếp).

## Quyết định cần anh Khương duyệt

1. **Kích hoạt module 📡 Monitoring ngay** (GĐ1 theo lịch đã bắt đầu 15/11): đã có nội dung sẵn (bộ ngưỡng DGA online, TB 783) và cơ hội thị trường cụ thể (PV Power Cà Mau 2, MBA 500 kV mới). Đề xuất lặp lại từ chu kỳ trước.
2. **Duyệt mua tài liệu** (gộp 2 chu kỳ): 8 bài CIGRE 2026 (≈240 €; ≈160 € hội viên) + ISO/IEC 30188:2026 (CHF 159). Nếu cắt giảm: A2‑10270, A2‑10207, ISO/IEC 30188. Kèm đề xuất cân nhắc đăng ký hội viên CIGRE (giảm giá + truy cập).
3. **Cho phép đăng ký theo dõi/tham gia IEEE WG PC57.145 và P3575** (cần một thành viên VTI có tài khoản IEEE SA).
4. **Chọn EVNNPT (TBA 500 kV Đức Hòa) làm ứng viên PoC thứ hai** bên cạnh EVNSPC – soạn one‑pager "Lớp phân tích Transformer DT trên PMIS".
5. **Module 🔋 BESS:** giữ standby đến 01/12 như lịch, nhưng giao 📊 Thị trường theo dõi kết quả G05/G06 GĐ3 (đổi so với đề xuất kích hoạt sớm ở chu kỳ trước, vì chưa có tin mới tạo khác biệt).

## Kế hoạch 3 ngày tới (17–19/11/2026)

**🧬 Digital Twin**
- *physics:* tìm Part II Das & Grisaru trên Hrčak, lấy công thức ROC; soạn bản nháp "DGA alarm policy" cho MBA 110 kV (baseline + 2 mức ngưỡng + xác nhận 7–14 ngày), đối chiếu IEEE C57.104‑2019; tiếp tục tìm repo TenneT.
- *substation:* thử dựng pipeline SCD → topology bằng OpenSCD/libiec61850 trên file SCD mẫu; lập danh mục chức năng Substation DT theo khung P3575 (khi có mô tả công khai).
- *standards:* theo dõi IEEE SA (PC57.145, P3575) và IEC webstore (61850‑90‑3 PAS); bắt đầu ánh xạ tín hiệu MBA → LN theo TR 2016 trong lúc chờ PAS.
- *data_ai:* thiết kế "cold‑start ladder": luật thống kê (ngày 0) → IEC 60076‑7 hiệu chỉnh (tháng 1) → PINN/Neural ODE (≥ tháng 3).
- *ot_cyber:* chuyển 4 kịch bản D2‑12215 thành checklist IEC 62443 cho kết nối DT.
- *benchmark:* bổ sung POWERGRID A2‑10255, PG&E–Camlin, Hitachi HMAX vào bảng so sánh utility/vendor.

**📊 Thị trường**
- *tender_analyst:* kết quả BESS GĐ3 G05/G06; kết quả gọi vốn EVNNPT (hạn 17/11); HSMT TBA 500 kV Nam Định Gói 6.
- *competitor_watch:* hồ sơ Á Châu (đối tác BESS), xác nhận tên/viết tắt; tìm nhà cung cấp online DGA tại TBA 500 kV Đức Hòa.
- *vn_market:* hồ sơ đơn vị quản lý TBA Đức Hòa và PTC2 (đầu mối kỹ thuật, PMIS); liệt kê các đơn vị EVN có sáng kiến robot/AI tại TBA làm đối tác dữ liệu.

## Nguồn

- [W1] Hrčak – Das & Grisaru, Beyond fixed limits… Part I (trang bài): https://hrcak.srce.hr/en/347231
- [W2] Hrčak – toàn văn PDF Part I: https://hrcak.srce.hr/file/501125
- [W3] Bhattarai et al., Physics‑informed Neural Network for Transformer Thermal Modelling, IEEE PESGM 2026: https://index.mirasmart.com/PESGM2026/PDFfiles/PESGM2026-001074.pdf
- [W4] CIGRE A2‑10270 (2026) – DTR on large three‑winding transformers (TenneT): https://www.e-cigre.org/publications/detail/a2-10270-2026-dynamic-transformer-rating-dtr-on-large-three-winding-power-transformers-in-the-transmission-grid-of-the-netherlands.html
- [W5] IEEE P3575 – Guide for Construction of Digital Twin Substation, Part 1: https://standards.ieee.org/ieee/3575/11942/
- [W6] LF Energy – Digital substation pt. 2 insights: https://lfenergy.org/digital-substation-pt-2-insights/
- [W7] Lopez et al., Development of Programmable Digital Twin via IEC‑61850 Communication, Energies 19(3):703: https://www.mdpi.com/1996-1073/19/3/703
- [W8] CIGRE D2‑12215 (2026) – Mitigating cyberattack risks in digital substations: https://www.e-cigre.org/publications/detail/d2-12215-2026-mitigating-cyberattack-risks-in-digital-substations-using-a-cybersecurity-model.html
- [W9] IEEE PC57.145 – Guide for DT Modeling and Analysis of Power Transformers 69–161 kV: https://standards.ieee.org/ieee/C57.145/11280/
- [W10] IEEE P3988 – Guide for DT Modeling of Overhead Transmission Lines and Towers: https://standards.ieee.org/ieee/3988/12531/
- [W11] NettedAutomation blog (06/08/2026) – IEC 61850‑90‑3: https://blog.nettedautomation.com/2026/08/iec-61850-90-3-using-iec-61850-for.html
- [W12] CIGRE A2‑10255 (2026) – Predictive analysis using ML modelling of DT of a power transformer: https://www.e-cigre.org/publications/detail/a2-10255-2026-predictive-analysis-using-machine-learning-modelling-of-digital-twin-of-a-power-transformer.html
- [W13] DTECH 2027 – PG&E/Camlin session: https://www.distributech.com/2027-event-agenda/integration-of-power-transformer-maintenance-information-with-online-monitoring-data-for-advanced-asset-health-diagnostics-and-digital-twin-modelling
- [W14] EE Power (24/04/2026) – Hitachi Energy launches AI‑powered suite (HMAX Energy): https://eepower.com/new-industry-products/hitachi-energy-launches-ai-powered-suite-for-infrastructure/
- [W15] Báo Đấu thầu (13/10/2026) – Cuộc đua mới trên thị trường năng lượng: https://baodauthau.vn/cuoc-dua-moi-tren-thi-truong-nang-luong-post209753.html
- [W16] dauthau.asia – TBMT sửa chữa kiến trúc TBA 110 kV Duyên Trà, Cầu Ngang, Long Đức: https://dauthau.asia/thongbao/moithau/cung-cap-vat-tu-thiet-bi-va-thi-cong-sua-chua-kien-truc-cac-tram-bien-ap-110kv-duyen-tra-cau-ngang-long-duc-1757946.html
- [W17] Tạp chí Công Thương (03/09/2026) – Chuyển đổi số tại TBA 500 kV Đức Hòa: https://tapchicongthuong.vn/chuyen-doi-so-nang-cao-hieu-qua-quan-ly--van-hanh-tai-tram-bien-ap-500kv-duc-hoa-546937.htm
- [W18] Tạp chí Công Thương (28/08/2026) – EVNNPT nghiệm thu đề tài giám sát và cảnh báo an toàn TBA: https://tapchicongthuong.vn/evnnpt-nghiem-thu-nhiem-vu-de-tai-khoa-hoc--nghien-cuu--xay-dung-he-thong-giam-sat-va-canh-bao-an-toan-tai-tram-bien-ap-545313.htm
- [W19] Tạp chí KH&CN Việt Nam A (02/2026) – Robot tự hành giám sát TBA không người trực: https://vjol.info.vn/khcn/article/view/131077

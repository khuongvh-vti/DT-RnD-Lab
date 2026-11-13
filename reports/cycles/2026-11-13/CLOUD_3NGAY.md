# Báo cáo 3 ngày Phòng R&D (Claude) – 13/11/2026

> Chu kỳ 3 ngày đầu tiên theo mô hình module (11–13/11/2026). Module **active**: 🧬 Digital Twin (GĐ1 – Nền tảng tri thức, ngày 3/40) và 📊 Thị trường (GĐ1 – Bản đồ khách hàng & kênh thông tin). Module **standby**: 📡 Monitoring, 🩺 Asset Health, 🔋 BESS. Chưa có báo cáo 3 ngày trước đó trong `reports/cycles/` (Qwen local chưa tạo `BAO_CAO_3_NGAY.md`), nên đối chiếu tránh lặp với 4 bản tin `reports/news/` (10–13/11) và bộ báo cáo `reports/2026-W46/`. Nội dung đã nêu trong bản tin (CIGRE A2‑10385, A2‑11489, A2‑11862, A2‑11984, D1‑11225, arXiv 2601.03673, 2609.20214, TBA số EVNHANOI, khung giá BESS…) không nhắc lại.

## Tóm tắt điều hành – điểm mới trong 3 ngày

1. **[🧬 DT – Tiêu chuẩn] IEC 61850-90-3 đang được nâng thành PAS Ed1 (~287 trang)**, mở rộng mô hình dữ liệu condition monitoring cho MBA, thiết bị đóng cắt, cáp, ĐZ và rung động; riêng MBA khoảng 17 logical node (SLTC, SBHR, SPTR…). Bộ ánh xạ tín hiệu của Transformer DT nên bám bản mới này thay vì chỉ TR 2016. Đồng thời **ISO/IEC 30188:2026 (Digital twin – Reference architecture) đã ban hành 07/2026** (29 trang, CHF 159).
2. **[🧬 DT – Mô hình vật lý] Có bằng chứng thực địa hiệu chỉnh mô hình nhiệt IEC 60076-7:** TenneT (CIGRE A2‑10270) mở rộng mô hình cho MBA 3 cuộn dây, mã nguồn Python mở; top‑oil sai lệch ~2–6 K, hot‑spot thiên về ước lượng cao (an toàn); nâng tải N‑1 từ ~50% lên ~65–70%. SINTEF/Statnett (arXiv 2608.13260) dùng Neural ODE làm "virtual sensor" trên 15 MBA: MAE trung vị ~2 °C nhưng **cần ≥3 tháng dữ liệu** – ràng buộc quan trọng cho pilot "cold start".
3. **[🧬 DT – Benchmark] POWERGRID Ấn Độ là tham chiếu gần VN nhất:** "Digital Mirror" cho đội MBA/kháng (lai vật lý + ML → Risk Index), dự báo khả dụng 99,80% → 99,91%, giảm 25% thời gian cắt điện can thiệp (A2‑10207); kiến trúc 4 lớp dùng IEC 61850‑90‑3 + IEEE 1588 (A3‑10816).
4. **[🧬 DT – Substation] Ba mẫu Substation DT mới:** Hitachi Energy DT tương tác thiết bị đóng cắt ↔ hệ giám sát để cấu hình/thử ảo và nghiệm thu tự động (D2‑12403); Transelectrica "CyberTwin" gắn dữ liệu an ninh OT lên DT trạm 400/110/20 kV (D2‑10667); HMV Colombia DT hỗ trợ vận hành trạm cao áp, khuyến nghị triển khai từng bước (B3‑12207).
5. **[📊 Thị trường] EVNSPC: 245/245 TBA 110 kV vận hành không người trực, đã áp dụng CBM/RCM và phát hiện sớm 862 bất thường (2024–2025)** – đây là khách hàng có "đất" cho Transformer/Substation DT nhất. Song song, gói BESS EVNNPC GĐ3‑G06 (314 tỷ) có 3 nhà thầu (Á Châu, Chint, liên danh TQ) – nhà thầu nội tiếp tục áp đảo BESS GĐ2 (ACIT 4/6 gói).

## Mới nghiên cứu / bổ sung theo từng module

### 🧬 Digital Twin ngành điện

**Giai đoạn:** GĐ1 – Nền tảng tri thức (11/11 → 20/12/2026), đang ở ngày 3. Tiến độ ước tính ~10%: đã có tóm tắt CIGRE TB 995, danh mục tài liệu, nay bổ sung lớp tiêu chuẩn kiến trúc (ISO/IEC 30188, IEC 61850‑90‑3 PAS) và các case utility.

**Chuyên viên Mô hình vật lý thiết bị (physics)**
- *Hiệu chỉnh IEC 60076-7 từ số đo thực:* TenneT kiểm chứng mô hình với heat‑run nhà máy của MBA 370 MVA và dữ liệu SCADA lịch sử; có xử lý chuyển chế độ ONAN/ONAF và nấc OLTC; mô hình ước lượng cao hot‑spot và lệch lớn hơn ở pha nguội → đây là "bài mẫu" cho quy trình hiệu chỉnh của VTI (dùng biên bản heat‑run + SCADA EVN). [W1]
- *Virtual sensor bằng Neural ODE:* 15 MBA Statnett, lấy mẫu 15 phút; Neural ODE thắng LSTM ở 14/15 MBA về R², 15/15 về MAE; dự báo ngắn hạn 1–7 ngày kém (R² trung vị âm); hiệu năng bão hòa sau ~1 năm dữ liệu. Bài không so trực tiếp với IEC 60076‑7 → đề xuất VTI làm phép so này trong GĐ3. [W2]
- *DGA cảnh báo sớm:* Transformer Magazine có loạt bài 2 phần "baseline‑driven, trend‑focused online DGA alarm strategy" (đặt ngưỡng theo nền + xu hướng thay vì giới hạn cố định) – trang bị chặn truy cập tự động, **chưa đọc được nội dung**, cần tải thủ công. [W3][W4]

**Chuyên viên Substation DT (trạm 110 kV)**
- Hitachi Energy (D2‑12403): DT của thiết bị đóng cắt và DT của chính hệ thống giám sát tương tác nhau → cấu hình, thử nghiệm ảo và kiểm tra khi nghiệm thu với mức tự động cao; đề xuất nhúng mô hình máy cắt và khí SF₆ vào phân tích health. Ý tưởng "DT của hệ giám sát" khớp đúng khoảng trống EVNHANOI (cấu hình/xử lý sự cố còn phụ thuộc nhà thầu). [W5]
- Transelectrica + Enevo + TIAB (D2‑10667): ghép giám sát an ninh OT thụ động vào DT trạm 400/110/20 kV, ánh xạ lỗ hổng và phụ thuộc truyền thông lên tài sản/không gian/chức năng, không ảnh hưởng vận hành. Gợi ý module "cyber layer" cho Substation DT (liên quan IEC 62443/62351). [W6]
- HMV Colombia (B3‑12207): DT kết hợp mô hình số có cấu trúc + dữ liệu SCADA + lịch sử/mô phỏng để phân tích tải, nhiệt và thao tác đóng cắt; nêu rõ hạn chế về độ sẵn có/độ tin cậy dữ liệu. [W7]
- Công cụ sinh SCD/topology: Aucotec Engineering Base 2026 và Kalkitech (sinh SCD theo quy tắc từ CSDL kỹ thuật) – đối tượng benchmark cho công cụ "SCD → topology" của VTI; chưa đánh giá chi tiết. [W8][W9]

**Khối dùng chung – Tiêu chuẩn & Kiến trúc**
- IEC 61850‑90‑3: bản "PRECD PAS 61850‑90‑3 ED1" (~287 trang), phạm vi MBA, thiết bị đóng cắt, cáp ngầm, ĐZ, rung động; ~17 LN cho MBA. Chưa có ngày ban hành. [W10]
- ISO/IEC 30188:2026 Ed1, 07/2026, 29 trang; giá ISO CHF 159 (DIN Media 182 EUR gồm VAT). [W11][W12]

**Khối dùng chung – Benchmark**
- POWERGRID: A2‑10207 "Digital Mirror" (EAM + SCADA + online sensor + thí nghiệm định kỳ → mô hình hot‑spot, lão hóa, hồ sơ hư hỏng + ML → Risk Index = PoF × tác động) [W13]; A3‑10816 kiến trúc 4 lớp (sensing → IEC 61850‑90‑3/IEEE 1588 → PINN twin → AI prognostics), F1 phân loại sự cố MBA >0,92, DLR tăng 5–35%. [W14]
- Hitachi Energy (21/10/2026) dựng mô phỏng hệ thống điện trên NVIDIA Omniverse/OpenUSD cho AI factory (grid‑to‑rack, 800 VDC) – xu hướng DT 3D + trợ lý AI ngôn ngữ tự nhiên; chưa áp dụng cho TBA. [W15]

**Trả lời câu hỏi nghiên cứu (cập nhật)**
- *Kiến trúc cho trạm 110 kV không người trực:* xu hướng hội tụ về mô hình lai (vật lý IEC 60076‑7 + ML) với dữ liệu chuẩn hóa IEC 61850‑90‑3, đầu ra là Risk Index phục vụ CBM (POWERGRID, Hydro‑Québec). Kiến nghị sơ bộ: lớp edge thu IEC 61850/104 → lớp DT vật lý có hiệu chỉnh → lớp risk/HI.
- *Mức DT đạt được trong 12 tháng:* các case 2026 chủ yếu ở mức Descriptive/Diagnostic, một phần Predictive (dự báo nhiệt, RUL). Ràng buộc "≥3 tháng dữ liệu" của Neural ODE cho thấy pilot GĐ5 cần thu dữ liệu sớm.

### 📊 Thị trường, Đấu thầu & Cơ hội VTI

**Giai đoạn:** GĐ1 – Bản đồ khách hàng & kênh thông tin (11/11 → 31/12/2026). Tiến độ ~10%: đã có bản tin hằng ngày; bổ sung hồ sơ EVNSPC và dữ liệu giá trúng thầu BESS.

**Chuyên viên Phân tích đấu thầu**
- EVNNPC BESS GĐ3, gói NPCBA1.BESS.GĐ3.G06 (cung cấp, lắp đặt BESS tại TBA 110 kV Bắc Ninh, Thái Nguyên), giá gói 314,144 tỷ; 3 nhà thầu nộp HSDT; bài đăng 28/10, chưa nêu giá dự thầu. [W16]
- EVNNPC BESS GĐ2: phê duyệt 14/10/2026, 6/7 gói có kết quả; ACIT trúng 4 gói (tổng 722,257 tỷ), ENTEC 1, CYG Sunri 1; giá trúng gần sát dự toán (chênh ~0,1–0,2%, tự tính). [W17]
- EVNNPT TBA 220 kV Chân Mây (220/110/22 kV, lắp 1×125 MVA), mục tiêu đóng điện 11/2026; trạm ~95% (13/10) → hạng mục thiết bị đã mua, chỉ còn cơ hội dịch vụ/giám sát bổ sung sau đóng điện. [W18]
- Đầu mối cần kiểm tra thủ công: dauthau.asia có TBMT "cung cấp VTTB và thi công sửa chữa các TBA 110 kV" (Bình Đại – Giao Long; Bình Thạnh – Mỏ Cày – Chợ Lách, khu vực Bến Tre/Vĩnh Long – EVNSPC) – không tải được trang, **chưa rõ có hạng mục giám sát hay không**. [W19][W20]

**Chuyên viên Theo dõi đối thủ & đối tác**
- BESS: nhà thầu nội (ACIT, ENTEC) áp đảo; đối thủ TQ (Chint, CYG Sunri, liên danh Renepoly/Relangy/Zhongjun) đang vào. Với VTI, đối tác tiềm năng là ACIT/ENTEC ở phần giám sát/EMS/tích hợp SCADA.
- Hitachi Energy đẩy mạnh DT (switchgear monitoring twin, Omniverse). Doble × MR hợp tác DGA online từ 12/2023 – không phải tin mới, ghi nhận để hoàn thiện bản đồ đối thủ. [W21]

**Hồ sơ khách hàng mới – EVNSPC:** 245 TBA 110 kV không người trực; CBM/RCM; 862 bất thường phát hiện sớm 2024–2025; 22/22 nhiệm vụ chuyển đổi số đến 2026 hoàn thành (09/2026); định hướng 2027–2030 "Một hạ tầng – Một cơ sở dữ liệu". [W22]

## Tài liệu nên bổ sung vào kho

| Tài liệu | Module | Nguồn/giá | Ghi chú |
|---|---|---|---|
| arXiv 2608.13260 – Virtual Temperature Sensors… Neural ODE (SINTEF/Statnett) | 🧬 physics | Miễn phí: https://arxiv.org/pdf/2608.13260 | Đưa vào `05_papers` |
| CIGRE A2‑10270 (2026) – DTR MBA 3 cuộn dây, TenneT | 🧬 physics | 30 € (20 € hội viên) | Có code Python mở – tìm link repo |
| CIGRE A2‑10207 (2026) – Digital Mirror POWERGRID | 🧬 benchmark | 30 € | Tham chiếu Risk Index |
| CIGRE A3‑10816 (2026) – DT/IoT/AI POWERGRID | 🧬 standards | 30 € | Kiến trúc 4 lớp |
| CIGRE D2‑12403 (2026) – Interacting DT switchgear (Hitachi) | 🧬 substation | 30 € | |
| CIGRE D2‑10667 (2026) – DigiTEL CyberTwin | 🧬 substation / ot_cyber | 30 € | |
| CIGRE B3‑12207 (2026) – DT vận hành trạm cao áp (HMV) | 🧬 substation | 30 € | Ưu tiên thấp hơn |
| ISO/IEC 30188:2026 – DT Reference architecture | 🧬 standards | CHF 159 (ISO) | Ưu tiên cao |
| IEC PAS 61850‑90‑3 Ed1 | 🧬 standards | Chưa ban hành – theo dõi webstore IEC | |
| Transformer Magazine – "Beyond fixed limits… online DGA alarm strategy" Part I & II | 🧬 physics / 📡 | Cần tải thủ công (trang chặn bot) | |

Tổng chi phí đề xuất mua đợt này: 6 bài CIGRE ≈ 180 € (≈120 € nếu có tư cách hội viên) + ISO/IEC 30188 CHF 159.

## Cơ hội & tin đáng chú ý cho VTI

- **[📊/🧬] EVNSPC – khách hàng pilot tiềm năng số 1 cho Transformer DT:** 100% TBA 110 kV không người trực và đã chạy CBM/RCM → nhu cầu chuyển từ "phát hiện bất thường" sang "dự báo & Risk Index" (đúng hướng POWERGRID). Đề xuất chuẩn bị one‑pager "Transformer DT cho TBA 110 kV không người trực" gửi Ban Kỹ thuật/CNTT EVNSPC.
- **[🧬 substation] Dịch vụ "DT của hệ giám sát/hệ thống bảo vệ" cho TBA số:** ý tưởng Hitachi D2‑12403 (cấu hình – thử ảo – nghiệm thu tự động) bổ trợ trực tiếp cho cơ hội EVNHANOI đã nêu trong bản tin 13/11.
- **[📊/🔋] BESS EVNNPC:** ACIT/ENTEC thắng phần lớn gói → tiếp cận làm thầu phụ giám sát nhiệt/khí, EMS, tích hợp SCADA cho các gói GĐ3 (G06 314 tỷ đang chấm).
- **[🔋 standby – tin nếu kích hoạt]** Tốc độ giải ngân BESS tại TBA 110 kV (GĐ2 đã trao, GĐ3 đang chấm) cùng khung giá BESS 2026 cho thấy module BESS có cơ sở kích hoạt sớm hơn mốc 01/12.

## Rủi ro, mâu thuẫn & điều cần kiểm chứng

- **IEC 61850‑90‑3:** nguồn duy nhất là blog NettedAutomation (06/08/2026) mô tả bản dự thảo PAS; chưa xác nhận trên IEC webstore → không trích là "đã ban hành".
- **Số liệu POWERGRID (99,80% → 99,91%, −25%)** là dự báo của tác giả ở giai đoạn đầu triển khai, lấy từ tóm tắt – cần đọc toàn văn trước khi dùng trong hồ sơ chào hàng.
- **TenneT "50% → 65–70%"** đặc thù vận hành N‑1 lưới Hà Lan; không suy trực tiếp cho EVN.
- **Neural ODE:** không so với IEC 60076‑7, dự báo ngắn hạn kém → không thay thế mô hình vật lý, chỉ bổ trợ.
- Giá trúng BESS GĐ2 sát dự toán (chênh ~0,1–0,2%) – tỷ lệ tự tính từ số liệu báo; giá dự thầu G06 GĐ3 chưa công bố.
- Hai TBMT sửa chữa TBA 110 kV (EVNSPC) chỉ có tiêu đề; trang dauthau.asia không truy cập được.
- Chưa có `BAO_CAO_3_NGAY.md` của Qwen local → chưa phản biện chéo được giữa hai luồng.

## Quyết định cần anh Khương duyệt

1. **Mua tài liệu đợt 1:** 6 bài CIGRE 2026 (≈180 €) + ISO/IEC 30188:2026 (CHF 159). Ưu tiên A2‑10270, A2‑10207, ISO/IEC 30188 nếu cần cắt giảm.
2. **Chọn EVNSPC làm khách hàng mục tiêu chính** cho kiến trúc Transformer DT (song song EVNHANOI cho Substation DT) và cho phép soạn one‑pager tiếp cận.
3. **Kích hoạt sớm module 🔋 BESS** (từ 16/11 thay vì 01/12) với phạm vi hẹp: giám sát an toàn + EMS/SCADA, phục vụ tiếp cận ACIT/ENTEC. Nếu chưa muốn mở thêm, giữ standby nhưng cho phép module 📊 theo dõi gói BESS.
4. **Module 📡 Monitoring** theo lịch sẽ vào GĐ1 từ 15/11 – đề nghị anh bấm "Kích hoạt" để chu kỳ tới chạy nghiên cứu (đặc biệt chủ đề DGA alarm theo xu hướng đang chồng lấn với 🧬 physics).

## Kế hoạch 3 ngày tới (14–16/11/2026)

**🧬 Digital Twin**
- *physics:* tìm repo Python mở của TenneT; dựng phép so IEC 60076‑7 vs Neural ODE trên dữ liệu mẫu; tải thủ công loạt bài DGA alarm strategy.
- *substation:* đọc tóm tắt/so sánh công cụ SCD → topology (Aucotec, Kalkitech, mã nguồn mở); phác thảo danh mục chức năng Substation DT 110 kV (topology, cảnh báo tổng hợp, cyber layer).
- *standards:* lập bảng ánh xạ tín hiệu MBA → LN IEC 61850‑90‑3 (SPTR, SLTC, SBHR, SIML, STMP…); đọc ISO/IEC 30188 khi có.
- *benchmark:* hoàn thiện bảng so sánh utility case: POWERGRID, Hydro‑Québec, TenneT, Statnett, Transelectrica.

**📊 Thị trường**
- *tender_analyst:* theo dõi kết quả G06 BESS GĐ3; xác nhận 2 TBMT sửa chữa TBA 110 kV EVNSPC; mốc EVNNPT gọi vốn 17/11 và 27/11.
- *competitor_watch:* hồ sơ năng lực ACIT, ENTEC, CYG Sunri; tìm nhà thầu đã cung cấp hệ giám sát online cho các TBA không người trực EVNSPC.
- *vn_market:* hồ sơ khách hàng EVNSPC (đầu mối, hệ thống SCADA/CBM đang dùng).

## Nguồn

- [W1] CIGRE A2‑10270 (2026) – DTR on large three‑winding power transformers, TenneT: https://www.e-cigre.org/publications/detail/a2-10270-2026-dynamic-transformer-rating-dtr-on-large-three-winding-power-transformers-in-the-transmission-grid-of-the-netherlands.html
- [W2] arXiv 2608.13260 – Virtual Temperature Sensors in Power Transformers Using Neural ODEs: https://arxiv.org/pdf/2608.13260
- [W3] Transformer Magazine – Beyond fixed limits… Part I: https://transformer-magazine.com/magazine/beyond-fixed-limits-baseline-driven-trend-focused-online-dga-alarm-strategy-part-i/
- [W4] Transformer Magazine – Part II: https://transformer-magazine.com/news/beyond-fixed-limits-baseline-driven-trend-focused-online-dga-alarm-strategy-part-ii/
- [W5] CIGRE D2‑12403 (2026) – Interacting digital twins for HV switchgear monitoring: https://www.e-cigre.org/publications/detail/d2-12403-2026-evolution-of-interacting-digital-twins-for-high-voltage-switchgear-monitoring.html
- [W6] CIGRE D2‑10667 (2026) – DigiTEL CyberTwin: https://www.e-cigre.org/publications/detail/d2-10667-2026-digitel-cybertwin-integrating-digital-twin-and-cybersecurity-for-enhanced-situational-awareness-in-critical-electrical-substations.html
- [W7] CIGRE B3‑12207 (2026) – DT for operational optimization of HV substations: https://www.e-cigre.org/publications/detail/b3-12207-2026-digital-twin-for-operational-optimization-of-high-voltage-electrical-substations.html
- [W8] Aucotec – Engineering Base 2026 & digital substation: https://bulkinside.com/news/aucotec-at-the-vde-congress-schutz-und-leittechnik-2026-in-leipzig-turning-the-digital-substation-into-reality/
- [W9] Kalkitech – Automatic generation of IEC 61850 SCD: https://kalkitech.com/automatic-generation-of-iec-61850-engineering-files-scd-for-the-european-utility-using-custom-engineering-db-defined-rules/
- [W10] NettedAutomation blog (06/08/2026) – IEC 61850‑90‑3: https://blog.nettedautomation.com/2026/08/iec-61850-90-3-using-iec-61850-for.html
- [W11] ISO – ISO/IEC 30188:2026: https://www.iso.org/standard/53308.html
- [W12] DIN Media – ISO/IEC 30188: https://www.dinmedia.de/en/standard/iso-iec-30188/405120162
- [W13] CIGRE A2‑10207 (2026) – Digital Mirror, POWERGRID: https://www.e-cigre.org/publications/detail/a2-10207-2026-development-of-a-digital-mirror-for-power-transformers-and-reactors.html
- [W14] CIGRE A3‑10816 (2026) – DT, IoT & AI for HV T&D assets, POWERGRID: https://www.e-cigre.org/publications/detail/a3-10816-2026-a-data-driven-paradigm-digital-twins-iot-and-ai-for-predictive-management-of-high-voltage-td-assets.html
- [W15] Hitachi Energy (21/10/2026) – Power system simulation with NVIDIA Omniverse: https://www.hitachienergy.com/news-and-events/press-releases/2026/10/hitachi-energy-develops-power-system-simulation-with-nvidia-omniverse-libraries-to-help-accelerate-ai-factory-deployment
- [W16] Báo Đấu thầu (28/10/2026) – 03 nhà thầu cạnh tranh gói BESS TBA 110 kV Bắc Ninh, Thái Nguyên: https://baodauthau.vn/03-nha-thau-canh-tranh-goi-thau-bess-cho-cac-tba-110kv-tinh-bac-ninh-thai-nguyen-tri-gia-314-ty-dong-post211126.html
- [W17] Báo Đấu thầu (21/10/2026) – Nhà thầu nội chiếm ưu thế tại các gói thầu BESS: https://baodauthau.vn/nha-thau-noi-chiem-uu-the-tai-cac-goi-thau-bess-post210524.html
- [W18] Tạp chí Công Thương (14/10/2026) – TBA 220 kV Chân Mây: https://tapchicongthuong.vn/day-nhanh-du-an-tram-bien-ap-220kv-chan-may--phan-dau-dong-dien-trong-thang-11-2026-557949.htm
- [W19] dauthau.asia – TBMT sửa chữa TBA 110 kV Bình Đại, Giao Long: https://dauthau.asia/thongbao/moithau/cung-cap-vat-tu-thiet-bi-va-thi-cong-sua-chua-cac-tram-bien-ap-110kv-binh-dai-giao-long-1774060.html
- [W20] dauthau.asia – TBMT sửa chữa TBA 110 kV Bình Thạnh, Mỏ Cày, Chợ Lách: https://dauthau.asia/thongbao/moithau/cung-cap-vat-tu-thiet-bi-va-thi-cong-sua-chua-cac-tram-bien-ap-110kv-binh-thanh-mo-cay-va-cho-lach-1774066.html
- [W21] Doble – Doble & MR collaborate on online DGA monitoring: https://www.doble.com/news/doble-engineering-and-maschinenfabrik-reinhausen-collaborate-to-enhance-online-condition-monitoring-for-dissolved-gas-analysis/
- [W22] Tạp chí Công Thương (15/10/2026) – EVNSPC hướng tới doanh nghiệp số thông minh: https://tapchicongthuong.vn/thuc-hien-nghi-quyet-so-57-nq-tw--evnspc-huong-toi-doanh-nghiep-so-thong-minh-558214.htm

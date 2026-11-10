# Fact sheet 02 – CIGRE Technical Brochures & IEEE Guides cho giám sát và DT máy biến áp (đã đối chiếu bản gốc)

Cập nhật 10/11/2026. Các mục đánh dấu ✅ là đã đọc bản gốc trong library/02_cigre_ieee. Các mục đánh dấu 🌐 là tra cứu web, chưa có bản gốc. Toàn bộ là tóm tắt bằng lời của Phòng R&D. Tóm tắt chi tiết TB 995 xem Fact sheet 03.

## ✅ CIGRE TB 995 (2026) – Digital twins for power transformers
JWG A2/D2.65, 108 trang. Định nghĩa DT, 5 cấp năng lực (Descriptive → Diagnostic → Predictive → Prescriptive → Autonomous), khảo sát 70 chuyên gia, mô hình đa trạng thái, checklist VVUQ, khuyến nghị. → Xem FS03.

## ✅ CIGRE TB 642 (2015) – Transformer reliability survey (WG A2.37)
- 964 sự cố lớn giai đoạn 1996–2010, tổng 167.459 MBA-năm, 56 công ty điện (bảng số liệu ghi 58), 21 nước.
- Suất sự cố MBA trạm theo cấp điện áp: 69–100 kV 0,94 %; **100–200 kV (nhóm 110 kV VN) 0,43 %**; 200–300 kV 0,50 %; 300–500 kV 0,60 %; 500–700 kV 0,57 %; ≥ 700 kV 0,33 %; chung 0,53 %/năm. MBA tăng áp (GSU) chung 0,95 %; riêng GSU 300–500 kV là 1,32 %, nhóm duy nhất vượt 1 %.
- Vị trí khởi phát sự cố, MBA nhóm 100–200 kV: cuộn dây 43,5 %, **bộ điều áp dưới tải 34,2 %**, sứ 13,0 %, lõi 2,9 %, đầu ra dây 2,9 %. Toàn bộ mẫu (không tính loại "không rõ"): cuộn dây 47,4 %, OLTC 23,2 %, sứ 14,4 %, đầu ra dây 6,3 %, lõi 3,8 %. Với U ≥ 100 kV, hơn 50 % sự cố cuộn dây xuất phát từ cuộn cao áp.
- Tỷ trọng sứ và đầu ra dây tăng theo cấp điện áp; tỷ trọng OLTC giảm theo cấp điện áp. 95 % MBA trạm bị sự cố có OLTC.
- Sự cố bắt nguồn từ sứ thường gây cháy/nổ. Sự cố cuộn dây thường dẫn tới loại bỏ MBA. Sự cố OLTC và sứ thường sửa được.
- Đường cong nguy cơ không có dạng "bồn tắm" rõ ràng; với 2 nhóm, nguy cơ tăng lên khoảng 1 % sau 30–40 năm rồi đi ngang. **Kết luận của WG: bảo dưỡng theo thời gian không hiệu quả với MBA trạm, nên bảo dưỡng theo tình trạng.**
- Ý nghĩa cho VTI (110 kV): ưu tiên giám sát OLTC (34 %) và cuộn dây (44 %) → DGA (gồm DGA ngăn OLTC), rung–âm OLTC, giám sát sứ.

## ✅ CIGRE TB 783 (2019) – DGA monitoring systems (JWG D1/A2.47)
- Phân loại monitor theo khí đo:
  - M1/M1* (chỉ H2 hoặc tín hiệu tổng hợp), M2 (H2, CO): chỉ phát hiện lỗi, không nhận diện được loại lỗi nào; có thể bỏ sót D1/D2 ở giai đoạn sớm.
  - M3 (CH4, C2H4, C2H2), M5 (H2, CH4, C2H4, C2H2, CO): nhận diện được 6 lỗi cơ bản.
  - M6/M7 và M8/M9 (đủ khí, có CO2, O2, N2): nhận diện được cả 10 loại lỗi/ứng suất, gồm các tiểu loại S, O, C, T3-H.
- Công nghệ: GC (giống phòng thí nghiệm, cần khí mang và bình hiệu chuẩn); hồng ngoại/quang âm (không cần khí tiêu hao, nhưng một số mẫu bị nhiễm hơi dầu/chất gây nhiễu → trôi); cảm biến chất rắn H2/CO.
- **Độ chính xác (kết luận chương 7)**: khoảng 20 monitor được CIGRE thử từ 2003. Đa số đạt yêu cầu độ chính xác ±15 % của IEC, một số ít không đạt. Ở nồng độ thấp (< 10 ppm) sai số trên 50 % là phổ biến (dưới 5 ppm có thể ≥ 75 %), khi đó chẩn đoán bằng tam giác Duval là không thể. Ở nồng độ thường gặp (> 10 ppm), sai số khoảng 30 % vẫn hay gặp, nhất là phương pháp head-space, kể cả ở phòng thí nghiệm.
- Sai số hệ thống của monitor làm **sai cả tốc độ tăng khí** (ví dụ +50 % thì tốc độ cũng lệch +50 %) → báo động giả hoặc bỏ sót.
- Khuyến nghị: kiểm chứng độ chính xác monitor và phòng thí nghiệm bằng mẫu chuẩn gas-in-oil (Phụ lục F); yêu cầu phòng thí nghiệm theo ISO 17025/17034 và đưa yêu cầu độ chính xác vào hợp đồng.
- ĐÍNH CHÍNH: con số "sai lệch ±20–30 %" mà Phòng trích trước đây lấy từ bài báo của B. Das & M. Grisaru (Transformers Magazine 2026), không phải nguyên văn TB 783.

## ✅ CIGRE TB 771 (2019) – Advances in DGA interpretation (JWG D1/A2.47)
- Ngoài 6 lỗi cơ bản (PD, D1, D2, T1, T2, T3), phân biệt các tiểu loại:
  - S: stray gassing, sinh khí tự nhiên của dầu < 200 °C;
  - O: quá nhiệt < 250 °C;
  - C: có thể cacbon hóa giấy > 300 °C;
  - T3-H: T3 chỉ trong dầu.
  Các tiểu loại này nhận diện bằng Duval Triangles 4, 5 và Pentagon 2.
- Lỗi ít đáng lo: S, T3-H. Lỗi nguy hiểm hơn: C (giấy cacbon hóa ở dây dẫn ra, trên cuộn dây, giữa các vòng), D1 trong giấy, D2 trong cuộn dây.
- Cung cấp giá trị điển hình theo loại lỗi; DGA cho OLTC bằng Duval Triangle 2.

## ✅ CIGRE TB 761 (2019) – Condition assessment of power transformers (WG A2.49)
- Chỉ số đánh giá MBA (Transformer Assessment Index – TAI), xây dựng theo 5 bước:
  1. Xác định mục đích (sàng lọc đội máy hay đánh giá chi tiết; chỉ số thay thế hay chỉ số đại tu);
  2. Xác định các dạng hỏng (failure modes) đưa vào chỉ số;
  3. Cách đánh giá từng dạng hỏng;
  4. Ma trận chấm điểm đã hiệu chuẩn;
  5. Tính điểm TAI cho từng máy.
- Nguyên tắc: không đánh giá một dạng hỏng nhiều lần; tách dạng hỏng khắc phục được (OLTC, sứ) khỏi chỉ số thay thế; xử lý dữ liệu bất định hoặc thiếu (chương 4); vai trò thiết bị online (chương 5); chỉ số mức độ quan trọng (criticality, chương 6); ước tính xác suất hỏng (chương 7). Có ma trận chấm điểm cho phần tác dụng, sứ, OLTC, làm mát, thùng, dầu (Annex A).

## ✅ CIGRE TB 630 (2015) – Guide on TICM systems (WG A2.44)
- Phương pháp luận cho hệ giám sát tình trạng thông minh: mô hình chức năng và mô hình thông tin MBA chung; chọn thuật toán chẩn đoán; kiến trúc và luồng dữ liệu; chuẩn hóa dữ liệu giám sát để tích hợp về sau; khía cạnh kinh tế–chiến lược.
- Thách thức: người dùng phải xác định chức năng/lỗi cần giám sát; thuật toán cần giao diện chuẩn, mô-đun hóa (có thể từ nhiều nhà cung cấp); tổ chức phải sẵn sàng (quy trình, đào tạo). Khuyến nghị hướng tới các LN giám sát–chẩn đoán trong IEC 61850.

## ✅ CIGRE TB 445 (2011) → 🌐 đã được thay bằng **TB 962 (2025) – Guide for transformer maintenance** (WG A2.69, 190 trang)
TB 962 cập nhật toàn bộ các chương và có khảo sát mới về thực hành bảo dưỡng. Cần tải TB 962 thay cho TB 445 (miễn phí cho hội viên CIGRE; người ngoài hội viên phải mua cho tới khi tài liệu đủ 3 năm).

## ✅ CIGRE TB 343 (2008) – Recommendations for condition monitoring and condition assessment facilities for transformers (WG A2.27)
## ✅ CIGRE TB 298 (2006) – Guide on transformer lifetime data management (WG A2.23)
TB 995 liệt kê TB 298 là tài liệu nền về khía cạnh dữ liệu.

## 🌐 CIGRE TB 659 (2016) – Transformer thermal modelling (WG A2.38, 197 trang)
THNM, CFD, mô phỏng chuẩn một cuộn dây thực, mô hình động, thực hành đo trực tiếp. Đã trên 3 năm → **tải miễn phí** tại e-cigre.org. Nên bổ sung vào kho (TB 995 dẫn chiếu cho mô hình nhiệt).

## 🌐 IEEE C57.143-2024 – Guide for Application of Monitoring Equipment to Liquid-Immersed Transformers and Components
Phát hành 20/05/2025, 177 trang, thay bản 2012. Phạm vi: thông số giám sát, phân tích rủi ro/lợi ích, ứng dụng cảm biến và hệ thống; không gồm diễn giải kết quả. Phụ lục: PD, đo trực tiếp nhiệt độ cuộn dây, phân tích dữ liệu DGA online.

## 🌐 IEEE C57.104-2019 – Guide for the Interpretation of Gases Generated in Mineral Oil-Immersed Transformers
- 98 trang, xây dựng từ dữ liệu khoảng 1 triệu mẫu DGA. Giới hạn theo phân vị 90th và 95th, phân nhóm theo tỷ số O2/N2 (≤ 0,2 hoặc > 0,2) và tuổi MBA.
- Ba mức trạng thái:
  - DGA Status 1: dưới phân vị 90 về nồng độ, delta và tốc độ;
  - Status 2: nằm giữa phân vị 90 và 95;
  - Status 3: vượt phân vị 95, hoặc delta/tốc độ vượt ngưỡng.
- Tốc độ tăng tính bằng hồi quy tuyến tính trên 3–6 mẫu.
- Một số nghiên cứu (Indonesia) cho rằng ngưỡng delta/tốc độ khá chặt, dễ xếp nhầm vào Status 2/3. Cần bản gốc để lấy bảng số liệu.

## 🌐 IEEE C57.91-2025 – Guide for Loading Mineral-Oil-Immersed Transformers and Step-Voltage Regulators
- Phát hành 05/03/2026, 123 trang, thay bản C57.91-2011.
- Có phương pháp tính có và không xét hiệu ứng dầu trong rãnh làm mát (duct oil); kèm mã nguồn mở trên IEEE Open-Source Platform.
- TB 995 ghi nhận mô hình IEEE cho thêm nhiệt độ đáy thùng và đỉnh rãnh cuộn dây nhưng cần nhiều thông số hơn mô hình IEC.

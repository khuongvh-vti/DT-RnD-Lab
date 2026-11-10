# Fact sheet 20 – Thị trường & bối cảnh Việt Nam cho giám sát online / Digital Twin MBA

Cập nhật 10/11/2026 (lần 2). Mức tin cậy ghi rõ từng dòng.

## Hệ thống đã triển khai (ĐÃ KIỂM CHỨNG qua báo chí ngành)
- EVNNPT: dự án "Trang bị 4 bộ giám sát, đánh giá tổng quan bản thể MBA 500 kV" tại các trạm 500 kV Phú Lâm, Pleiku 2, Đà Nẵng, Hiệp Hòa. Thiết bị GE MS 3000 (sản xuất tại Đức); PTC3 thay mặt EVNNPT quản lý dự án; Công ty CP 3C là nhà thầu, nghiệm thu và đóng điện bộ cuối cùng (AT1 Hiệp Hòa). Dữ liệu qua mạng WAN EVNNPT về phần mềm Perception Server (đã đầu tư từ dự án giám sát dầu online cho MBA và kháng 500 kV trước đó). Báo chí ghi đây là lần đầu EVNNPT thí điểm loại thiết bị giám sát tổng quan này. Nguồn: tapchicongthuong.vn (bài 63062, 64749).
- Thủy điện Sông Bung 4: lắp GE MS3000 + Kelman DGA900, giám sát PD, DGA, áp suất, nhiệt độ, chẩn đoán thời gian thực. Nguồn: tapchicongthuong.vn (bài 131592).
- Đại lý trong nước đã chào bán thiết bị Dynamic Ratings (TTECH). Nguồn: parts.ttech.vn.

## Hàm ý thị trường (PHÂN TÍCH của Phòng R&D – cần kiểm chứng thêm)
- Cấp 500 kV của EVNNPT đã có hạ tầng GE (MS 3000 + Perception). Đối thủ có lợi thế cài đặt sẵn; cơ hội cho VTI nằm ở lớp phần mềm DT độc lập hãng đọc dữ liệu từ thiết bị sẵn có, hoặc ở cấp 110–220 kV, trạm không người trực, nhà máy thủy điện/năng lượng tái tạo.
- Nhà tích hợp trong nước (ví dụ 3C) đóng vai trò triển khai → đối tác hoặc đối thủ tiềm năng của VTI.

## Pháp lý về dữ liệu (✅ đã đọc bản tiếng Anh Luật Dữ liệu trong library/04_vietnam; 🌐 nghị định tra cứu web)
- ✅ **Luật Dữ liệu số 60/2024/QH15**, thông qua 30/11/2024, hiệu lực 01/7/2025.
  - Phân loại: dữ liệu cốt lõi, dữ liệu quan trọng, dữ liệu khác. Dữ liệu quan trọng là dữ liệu có thể ảnh hưởng quốc phòng–an ninh, đối ngoại, kinh tế vĩ mô, ổn định xã hội, sức khỏe cộng đồng, nằm trong danh mục do Thủ tướng ban hành. Dữ liệu cốt lõi là phần dữ liệu quan trọng tác động trực tiếp tới các lĩnh vực đó.
  - **Điều 23 – chuyển, xử lý dữ liệu xuyên biên giới** với dữ liệu cốt lõi/quan trọng gồm 3 trường hợp:
    - chuyển dữ liệu lưu tại Việt Nam sang hệ thống lưu trữ ở nước ngoài;
    - chuyển cho tổ chức, cá nhân nước ngoài;
    - **dùng nền tảng đặt ngoài lãnh thổ để xử lý**.
  - Điều 25: chủ quản dữ liệu phải đánh giá và quản lý rủi ro xử lý dữ liệu.
- 🌐 **Nghị định 165/2025/NĐ-CP** (30/06/2025, hiệu lực 01/7/2025) hướng dẫn Luật Dữ liệu: trước khi chuyển dữ liệu cốt lõi/quan trọng ra nước ngoài phải lập báo cáo đánh giá tác động; với dữ liệu cốt lõi, hồ sơ gửi Bộ Công an hoặc Bộ Quốc phòng.
- 🌐 Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 (hiệu lực 01/01/2026) và Nghị định 356/2025/NĐ-CP. Dữ liệu vận hành MBA thường không phải dữ liệu cá nhân.
- 🌐 Dự thảo Luật An ninh dữ liệu (dự kiến hiệu lực 01/12/2027).
- **Hàm ý cho DT (PHÂN TÍCH, cần luật sư xác nhận)**: nếu dữ liệu vận hành lưới truyền tải/trạm của EVN được xếp vào danh mục dữ liệu quan trọng, thì giải pháp DT xử lý trên cloud nước ngoài (Siemens Sensformer cloud, Schneider EcoStruxure qua 3G/4G, APM SaaS…) phải đánh giá tác động trước khi chuyển dữ liệu. Giải pháp xử lý tại Việt Nam (on-premise, local) có lợi thế tuân thủ. CẦN KIỂM CHỨNG danh mục dữ liệu quan trọng/cốt lõi do Thủ tướng ban hành có bao gồm dữ liệu vận hành hệ thống điện hay không.
- Luật Điện lực 2024 và Nghị quyết 57-NQ/TW: CẦN đối chiếu văn bản gốc.

## Tài liệu Việt Nam còn thiếu (cần anh Khương bổ sung)
- Quy định/hướng dẫn của EVN, EVNNPT về trạm biến áp không người trực, hệ thống điều khiển máy tính, giám sát online thiết bị (quy trình, đặc tính kỹ thuật mẫu).
- Hồ sơ mời thầu (HSMT) gần đây có hạng mục giám sát online MBA (110–500 kV) – để biết tiêu chí kỹ thuật & giá trần.
- Thống kê sự cố MBA của EVN/EVNNPT (nếu có báo cáo nội bộ).

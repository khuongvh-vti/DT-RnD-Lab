# Fact sheet hãng – GE Vernova: Kelman™ DGA, MS 3000, Perception™ Fleet

Nguồn: brochure gevernova.com (DGA 900, DGA 900 PLUS R010 06/2026, TAPTRANS, MULTITRANS, Perception Fleet 2025/2026), báo Công Thương (EVNNPT). Tra cứu 10/11/2026.

- **Kelman DGA 900**: thế hệ thứ 4 công nghệ quang âm PAS của GE; đo 9 khí + độ ẩm; "Rapid Mode" cho khí nguy hiểm khoảng 30 phút; hỗ trợ dầu khoáng và este; I/O mở rộng; báo động TDCG và 7 tỷ số khí do người dùng định nghĩa, theo mức tuyệt đối và tốc độ thay đổi (ROC). Kết nối DS-Agile, Grid APM, Perception, historian, SCADA. Hãng nêu kinh nghiệm hơn 15 năm PAS và hơn 15.000 thiết bị lắp đặt.
- **DGA 900 PLUS**: thành hệ giám sát MBA (TMS) với add-on: sứ xuyên (C1, tanδ; tới 9 sứ ở bản 2026), PD (dùng chung adapter sứ; HFCT + PRPD phân biệt PD trong/ngoài), OLTC, làm mát, mô hình hệ cách điện (nhiệt độ dầu, dòng tải, độ ẩm…), camera nhiệt IRT tương quan với xu hướng khí (bản 2026).
- **DGA 900 TAPTRANS**: DGA riêng cho ngăn chính và ngăn selector/diverter OLTC. **MULTITRANS**: một máy cho 3 MBA một pha. **MINITRANS**: bản giá thấp. Brochure GE nêu phân bố vị trí sự cố: OLTC 35 %, thùng chính 30 %, sứ 15 %, làm mát 5 %, khác 15 % (số liệu do hãng nêu, không ghi nguồn khảo sát → CẦN KIỂM CHỨNG trước khi trích).
- **Perception Fleet**: phần mềm quản lý rủi ro đội MBA, chạy web; thuật toán theo tiêu chuẩn tính Risk Index 1–5 và risk score để xếp hạng; phân tích tốc độ tăng khí theo Piecewise Linear Rate of Change; dashboard toàn đội máy.
- **MS 3000**: hệ giám sát tổng quan bản thể MBA (IED tổng hợp nhiều cảm biến, nhiều MBA).

## Tại Việt Nam (đã kiểm chứng qua báo chí)
- EVNNPT trang bị **4 bộ MS 3000** cho MBA 500 kV tại trạm Phú Lâm, Pleiku 2, Đà Nẵng, Hiệp Hòa; PTC3 quản lý dự án; nhà thầu tích hợp **Công ty CP 3C**; kết nối qua WAN EVNNPT về **Perception Server** (đã đầu tư trong dự án giám sát dầu online cho MBA và kháng 500 kV). Đây là lần đầu EVNNPT thí điểm loại thiết bị này.
- Thủy điện Sông Bung 4 dùng **MS3000 + DGA900** của GE (giám sát PD, DGA, áp suất, nhiệt độ).
→ GE có **lợi thế cài đặt sẵn (installed base)** lớn nhất tại EVNNPT cấp 500 kV.

## Đánh giá (Phòng R&D)
- Mức năng lực TB 995: Descriptive + Diagnostic mạnh (DGA), Predictive ở cấp đội máy (risk index). Chưa thấy mô hình DT vật lý chi tiết kiểu Siemens.
- Cơ hội cho VTI: tích hợp/đọc dữ liệu Perception & DGA 900 sẵn có của EVNNPT (Modbus/DNP3/IEC 61850) để làm lớp DT phía trên thay vì thay thiết bị → GIẢ ĐỊNH, cần xác minh giao thức thực tế đang dùng.

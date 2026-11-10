# Fact sheet hãng – Hitachi Energy: TXpert™ Ecosystem, CoreTec™, Lumada APM / APM Edge

Nguồn: trang hitachienergy.com (TXpert Hub, APM Edge), thông cáo báo chí 2020/2023/2026, CISA advisory ICSA-23-089-01. Tra cứu 10/11/2026.

## Danh mục
- **TXpert™ Ecosystem** (ra mắt 09/2020): bộ sản phẩm, phần mềm, dịch vụ số hóa MBA; mở, tích hợp thiết bị hãng khác.
- **TXpert™ Hub** – "trái tim" hệ sinh thái: thiết bị giám sát–chẩn đoán–kết nối đặt tại MBA, tổng hợp dữ liệu cảm biến "TXpert Ready" của nhiều hãng; truy cập tại chỗ hoặc qua cloud. Thế hệ mới (02/2023) chạy trên nền **CoreTec™ 5** (trước đó CoreTec 4). Áp dụng cho MBA dầu hoặc khô, mới hoặc cải tạo, mọi hãng (hạn chế với MBA HVDC).
- Biến thể: Distribution Transformer Basic / Basic+; Power Transformer Basic / Basic+ / Advanced; Dry Basic+ (tuabin gió). Kết hợp với APM Edge, TXpert Remote Services, TXpert Services.
- Ví dụ ứng dụng hãng nêu: trạm TSO (giảm cử người ra hiện trường), nhà máy điện, trung tâm dữ liệu, trạm sạc xe điện, nhà máy luyện kim (đánh giá khả năng quá tải ngắn hạn).
- Dữ liệu được chuyển thành thông tin hành động dựa trên tiêu chuẩn IEC, IEEE + kinh nghiệm chế tạo/bảo dưỡng của hãng.
- **An ninh mạng**: chứng nhận IEC 62443-4-2, phù hợp IEEE 1686, hỗ trợ tuân thủ NERC-CIP; đội phát triển đạt IEC 62443-4-1 và ISO 27001.
- Truyền thông: có ngăn xếp **IEC 61850 MMS server** (xác nhận qua CISA advisory 2023: CVE-2022-3353 ảnh hưởng TXpert Hub CoreTec 4 v2.0–3.0 và CoreTec 5 v3.0 – đã có bản vá). Các CVE khác 2022 trên CoreTec 4 v2.0–2.2 (command injection, xác thực) → bài học: thiết bị biên DT phải có quy trình vá lỗi & PSIRT.
- **APM Edge**: phần mềm APM gọn cho MBA, từ 1 máy đến toàn doanh nghiệp; thuật toán có bằng sáng chế, liên tục tính xác suất hư hỏng; tương thích thiết bị đa số hãng, plug-and-play với TXpert.
- **Lumada APM / Hitachi Energy APM** (enterprise): modules health, reliability, optimization (thế hệ mới 10/2023); hơn 175 mô hình dựng sẵn cho MBA, máy cắt, tài sản trạm; tích hợp EAM + FSM. IDC MarketScape 2025–2026 xếp Leader về APM cho ngành điện (công bố 17/02/2026). Đã triển khai cho Inner Mongolia Power (dự án bảo dưỡng MBA).

## Đánh giá theo khung CIGRE TB 995 (Phòng R&D)
- Mức năng lực: Descriptive → Diagnostic → Predictive (xác suất hư hỏng, mô phỏng rủi ro theo tải) ở cấp đội máy; có Prescriptive một phần (ưu tiên bảo dưỡng/thay thế). GIẢ ĐỊNH dựa trên mô tả của hãng.
- Điểm mạnh: hệ sinh thái đầy đủ thiết bị → APM doanh nghiệp; kinh nghiệm hãng sản xuất MBA lớn; an ninh mạng được chứng nhận.
- Điểm yếu/rủi ro với khách hàng VN: chi phí và phụ thuộc hãng; dữ liệu có thể đưa lên cloud (cần đối chiếu Luật Dữ liệu VN); giá không công bố.

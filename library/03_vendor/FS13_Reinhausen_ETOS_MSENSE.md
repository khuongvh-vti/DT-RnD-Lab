# Fact sheet hãng – Maschinenfabrik Reinhausen (MR): ETOS®, MSENSE®, TESSA®

Nguồn: reinhausen.com (ETOS, ETOS ED), tạp chí onload của MR ("The Digital Triad" 12/2018), thông cáo Doble–MR. Tra cứu 10/11/2026.

- **ETOS® (Embedded Transformer Operating System)**: MR gọi là hệ điều hành mở đầu tiên cho MBA thông minh; giám sát, điều khiển, điều chỉnh MBA; độc lập hãng MBA; tích hợp mới hoặc cải tạo, từ 1 máy tới cả đội máy. Gom "tất cả công nghệ thứ cấp vào một hệ" (thay nhiều tủ điều khiển). MR quảng bá "không làm tăng tổng chi phí hệ thống" (tuyên bố của hãng).
- Kiến trúc 3 tầng: (1) **Process level** – cảm biến MSENSE®, thiết bị bảo vệ, mở cho cảm biến bên thứ 3; (2) **Field level** – ETOS phân tích bằng thuật toán MR hoặc thuật toán của khách hàng; 6 gói chức năng: giám sát MBA, giám sát OLTC, DGA online, điều khiển–giám sát làm mát, giám sát sứ…; (3) **Control level** – **TESSA®** giám sát đội máy.
- **ETOS ED**: tích hợp bộ truyền động OLTC + giám sát trong một vỏ; gửi dữ liệu về trung tâm qua giao thức mạng trên cáp quang; có thể kèm điều chỉnh điện áp và điều khiển làm mát.
- Dòng cảm biến **MSENSE®**: DGA, BM (sứ), VAM (rung–âm OLTC), FO (nhiệt độ sợi quang), độ ẩm/BDV; MESSKO MTRAB (bình thở không cần bảo dưỡng); MLOG (giám sát vận chuyển).
- MR làm đại lý bán lại **Doble Calisto R9** và cung cấp tích hợp ETOS + Calisto R9.
- Hợp tác PSI Software: dùng dữ liệu ETOS tối ưu vận hành MBA, giảm chi phí redispatch.
- MR nêu 26 % sự cố MBA bắt nguồn từ bất thường OLTC (số liệu hãng).

## Đánh giá (Phòng R&D)
- Mức năng lực TB 995: Descriptive + Diagnostic; điểm khác biệt là **điều khiển** (OLTC, làm mát) → tiến gần vòng kín DT (Prescriptive/Autonomous ở mức cục bộ).
- Điểm mạnh: thống trị thị trường OLTC → hiện diện sẵn trên rất nhiều MBA tại VN (GIẢ ĐỊNH cần khảo sát số lượng); kiến trúc mở.
- Bài học cho VTI: DT không chỉ "nhìn" mà còn tác động (điều khiển làm mát theo mô hình nhiệt) – hướng phát triển cấp cao.

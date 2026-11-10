# Fact sheet hãng – Siemens Energy: Sensformer® / Sensformer® Advanced

Nguồn: thông cáo Siemens (Hannover Messe 2018, 2019 PR2019040210GPEN), siemens-energy.com (500th Sensformer – ISA CTEEP), bài Transformer Technology (02/2022) và Transformers Magazine (11/2023, Sherekar & Pandya). Tra cứu 10/11/2026.

- **Sensformer (2018)**: chuyển toàn bộ danh mục MBA sang "digital transformer" từ 06/2018. Mỗi máy có IoT gateway đo trực tiếp: mức dầu, nhiệt độ dầu đỉnh, dòng cuộn hạ áp, vị trí GPS; tối thiểu hóa số đo vật lý, tránh thiết bị IT thừa tại trạm. Ứng dụng cloud (ban đầu trên MindSphere) hiển thị trạng thái; mở rộng cho cả MBA không phải của Siemens Energy.
- **Sensformer Advanced (Hannover Messe 2019)**: DT mô phỏng thời gian thực; active overload manager, full temperature view, phân tích tiêu hao tuổi thọ.
- **Mô hình DT của Siemens Energy**: dựng riêng cho từng MBA từ dữ liệu thiết kế; tiếp cận thermo-hydraulic, **multi-mass** có dòng chảy dầu, tính phân bố tổn hao trong phần tác dụng theo tỷ số biến và vị trí nấc; không dùng hằng số thời gian nhiệt cố định như mô hình IEC; bao phủ mọi cuộn dây và các chế độ làm mát. Hãng công bố so sánh: mô hình DT bám nhiệt độ dầu đỉnh đo được tốt hơn mô hình IEC tiêu chuẩn.
- Ba kịch bản: mô phỏng chu kỳ tải và nhiệt độ môi trường 24 giờ tới; dự báo quá tải; tính lão hóa tương đối theo công thức IEC loading guide trong 24 h, 30 ngày và từ khi vận hành. Tính năng khác: mixed reality view, load simulation, lifetime prediction, tích hợp DGA/multigas. Bảo mật theo ISO/IEC 27001.
- Định hướng (2022): bổ sung mô hình độ ẩm và suy giảm cách điện để thành "DT hoàn chỉnh".
- Quy mô: giao chiếc Sensformer thứ 500 cho ISA CTEEP (Brazil); khách hàng đánh giá cao chức năng quá tải có kiểm soát.

## Đánh giá (Phòng R&D)
- Mức năng lực TB 995: Descriptive + Predictive (nhiệt/quá tải) rất mạnh; Diagnostic DGA phụ thuộc cảm biến tích hợp.
- Điểm mạnh: mô hình vật lý từ dữ liệu thiết kế của chính hãng → độ chính xác cao; "born connected".
- Hạn chế: lợi thế lớn nhất chỉ có với MBA Siemens Energy (có dữ liệu thiết kế); với MBA hãng khác phải dùng mô hình đơn giản hơn – GIẢ ĐỊNH, cần kiểm chứng. Phụ thuộc cloud.
- Bài học cho VTI: muốn cạnh tranh về mô hình nhiệt phải có dữ liệu heat-run test + thông số thiết kế; nên hiệu chỉnh tham số mô hình IEC theo dữ liệu đo (giống cách Dynamic Ratings làm).

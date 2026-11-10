# Fact sheet 03 – CIGRE TB 995 (2026) "Digital twins for power transformers – Concept and future perspectives" – tóm tắt từ bản gốc

Nguồn: bản PDF TB 995 trong library/02_cigre_ieee (JWG A2/D2.65, 108 trang). Tóm tắt do Phòng R&D viết bằng lời của mình, đã đối chiếu bản gốc ngày 10/11/2026. Số chương/mục ghi trong ngoặc để tra lại.

## 1. Định nghĩa (mục 2.2)
- Digital twin (DT) của MBA = biểu diễn ảo của tài sản/hệ thống, được cập nhật động bằng dữ liệu từ đối tượng thật, có khả năng dự báo và hỗ trợ ra quyết định để tạo giá trị. Tương tác HAI CHIỀU ảo ↔ thực là cốt lõi.
- Vòng phản hồi: dữ liệu thật → mô hình hóa/phân tích/dự báo → hành động → DT được cập nhật suốt đời tài sản.
- **Reality gap** (khoảng cách thực tế): độ lệch giữa hành vi của DT và MBA thật. Nguyên nhân: mô hình chưa đúng, dữ liệu hạn chế, hoặc thay đổi ở tài sản mà mô hình chưa tính đến. Quản lý reality gap là thước đo độ tin cậy của DT.
- Lịch sử (mục 2.3): khái niệm do M. Grieves đề xuất năm 2002; tên "digital twin" được NASA dùng năm 2010; Industry 4.0 khoảng 2016; khoảng 2020 bắt đầu chuẩn hóa trong ISO/IEC JTC 1/SC 41. Với MBA, đa số vẫn ở mức pilot/prototype.

## 2. Thành phần của Transformer DT (mục 2.4, theo TB 630)
1. Cảm biến: nhiệt độ, khí hòa tan, dòng đầu sứ (bushing tap), thông số OLTC, rung, PD, dòng/áp.
2. Hạ tầng truyền thông: có dây, không dây hoặc kết hợp.
3. Hệ thu thập dữ liệu: thu, lưu, tiền xử lý, bảo đảm toàn vẹn dữ liệu.
4. Mô hình hóa, mô phỏng, phân tích (ML): nhận dạng mẫu, phát hiện bất thường, dự báo.
5. Trực quan hóa / giao diện người dùng (dashboard; có thể 3D, AR/VR – mục 2.5).
- Dữ liệu ngoài vận hành: dữ liệu thiết kế, kết quả FAT/SAT (kể cả thử nghiệm phát nóng của máy cùng loại), hồ sơ bảo dưỡng, dữ liệu môi trường.

## 3. Kỹ thuật diễn giải (2.6) và loại mô hình (2.7)
- Ba loại đầu ra: phát hiện bất thường (anomaly detection) → chẩn đoán nguyên nhân (diagnosis; thường cần thêm thử nghiệm offline để xác nhận) → tiên lượng (prognosis; tuổi thọ còn lại RUL).
- Bốn loại mô hình: physics-based (từ CFD/FEM chi tiết tới mạch nhiệt thông số tập trung); data-driven (ML; thiếu dữ liệu sự cố vì MBA rất tin cậy); knowledge-based (luật chuyên gia, ontology, knowledge graph); hybrid (kết hợp ≥ 2 loại – được khuyến nghị khi thiếu dữ liệu thiết kế độc quyền).

## 4. Năm cấp năng lực DT (mục 2.8, Bảng 2.1)
| Cấp | Tên | Năng lực chính |
|---|---|---|
| 1 | Descriptive | Biểu diễn số thời gian thực; giám sát từ xa, hiển thị trạng thái |
| 2 | Diagnostic | Phát hiện lỗi, nhận biết bất thường sớm (nhiệt tăng bất thường, khí bất thường, PD, suy giảm cách điện, lỗi làm mát) |
| 3 | Predictive | Dự báo trạng thái, RUL, xác suất hư hỏng, phân tích lão hóa, lập kế hoạch bảo dưỡng chủ động |
| 4 | Prescriptive | Khuyến nghị tối ưu (thời điểm xử lý dầu, bảo dưỡng OLTC, kiểm tra mục tiêu) dựa trên phân tích "what-if" có định lượng độ bất định |
| 5 | Autonomous | Tự thực hiện một số chức năng điều khiển (giới hạn tải, khởi động bảo dưỡng), phối hợp với hệ thống quản lý lưới và các DT khác |

## 5. Khảo sát ngành (chương 3) – 70 chuyên gia, 10/2024–02/2025
- Đối tượng: 33 % công ty điện/vận hành lưới, 33 % nhà chế tạo, 16 % viện/trường; theo vùng: châu Âu 33 %, châu Á 19 %, Bắc Mỹ 13 %. 87 % quen thuộc với khái niệm DT.
- 60 % tổ chức (42/70) đang có dự án DT cho MBA. Trong các dự án: khoảng 43 % ở giai đoạn pilot/prototype, 33 % ở giai đoạn ý tưởng/khả thi, chỉ 24 % đã vận hành.
- 64 % đã đạt cấp 1. Phần lớn kỳ vọng đạt cấp 2 trong 3 năm tới. 19 % không định làm cấp 4 và 52 % không định làm cấp 5.
- 92 % dự báo DT có tác động từ trung bình đến cao (49 % cho rằng tăng mạnh trong 10 năm).
- Rào cản lớn nhất: dữ liệu thiếu hoặc kém chất lượng (hơn 84 % đánh giá quan trọng/rất quan trọng); tiếp theo là tích hợp hệ thống (khoảng 71 %); sau đó an ninh mạng, kỹ năng.
- Tiêu chuẩn: 47 % cho là then chốt, 41 % cho là quan trọng. Lý do: giảm phụ thuộc nhà cung cấp (vendor lock-in) và chi phí tích hợp.
- Năng lực: chỉ khoảng 21 % tự phát triển DT được; 67 % có hợp tác bên ngoài (49 % với viện/trường, 31 % với nhà chế tạo, 30 % với đơn vị dịch vụ).
- Ngân sách: 56 % đã có ngân sách (23 % có dòng ngân sách riêng).

## 6. Dữ liệu (chương 4)
- Nhóm dữ liệu: thiết kế–chế tạo; FAT/SAT; thử nghiệm/kiểm tra hiện trường; giám sát online; vận hành; cuối đời (post-mortem); cơ sở dữ liệu ngoài.
- Quản lý dữ liệu: truyền thông/lưu trữ/truy cập; quản trị dữ liệu (data governance); an ninh mạng.
- **Mô hình đa trạng thái (multi-state)** (mục 4.4): biểu diễn sức khỏe MBA qua các trạng thái suy giảm rời rạc, từ bình thường qua các mức suy giảm tới hỏng. Trạng thái xác định từ FMEA và chỉ số quan sát hoặc suy luận (virtual sensor). Chuyển trạng thái được mô hình hóa tất định (vật lý) hoặc xác suất. Cho phép chạy song song nhiều mô hình chẩn đoán (ensemble).

## 7. Mô hình vật lý (chương 5) – trọng tâm nhiệt
- Ba mức: mạch nhiệt thông số tập trung (loading guide) → mô hình mạng nhiệt-thủy lực (THNM) → CFD. Nhà chế tạo dùng CFD/THNM; công ty điện thường dùng mô hình đơn giản (chi tiết ở CIGRE TB 659; WG A2.60 đang làm về hành vi nhiệt động).
- Mô hình IEC 60076-7:2018 dùng phương trình vi phân thường, chỉ cần chuỗi nhiệt độ môi trường và hệ số tải. IEEE C57.91-2025 cho thêm nhiệt độ đáy thùng và đỉnh rãnh làm mát cuộn dây nhưng cần nhiều thông số đặc thù hơn.
- Lưu ý: hệ số mũ dầu/cuộn dây mặc định của IEC 60076-2:2011 và IEC 60076-7:2018 khác nhau; bộ của 60076-2 bảo thủ hơn.
- **Hiệu chỉnh thông số**:
  - Với MBA mới: chỉ định thử phát nóng mở rộng (extended temperature rise test) để rút ra thông số riêng.
  - Với MBA đang vận hành: học thông số từ dữ liệu đo θo/θh, cực tiểu sai số dự báo. Thông số học được chỉ đúng trong dải vận hành của dữ liệu học.
  - Không hiệu chỉnh các đại lượng đo trực tiếp ở định mức (tỷ số tổn hao, độ tăng nhiệt định mức).
- Hạn chế của mô hình loading guide: chỉ 1 cuộn dây, 1 pha, nấc cố định, 1 cấp làm mát; sai lệch khi môi trường rất lạnh, khi đổi chế độ làm mát, khi đổi nấc, khi tải rất thấp → THNM động khắc phục.
- Các mô hình khác: điện từ, suy giảm điện môi (đa vật lý), cơ học, thành phần (OLTC, sứ, hệ làm mát).

## 8. Mô hình dữ liệu và lai (chương 6)
- Quy trình dữ liệu: thu thập, làm sạch, phát hiện ngoại lai, xử lý thiếu/mất cân bằng dữ liệu, tích hợp, biến đổi, giảm chiều, chia tập.
- Hybrid: grey-box, PINN (physics-informed neural network), ensemble. Ví dụ ứng dụng: chẩn đoán lỗi, đánh giá tình trạng, quản lý tải nhiệt.

## 9. Độ tin cậy & VVUQ (chương 7)
- Độ tin cậy của DT = khả năng đưa ra kết quả đúng hạn trong giới hạn sai số đã thỏa thuận, đồng thời liên tục theo dõi và thu hẹp reality gap. Đây là đặc tính thay đổi theo thời gian, không cố định.
- Cập nhật mô hình sau "sự kiện thay đổi đời sống" của MBA (life-changing events: thay linh kiện, lọc/thay dầu…).
- **Checklist VVUQ (mục 7.12)**:
  1. Verification: kiểm tra dữ liệu đầu vào (đúng dải); độ tin cậy cảm biến (hiệu chuẩn, phát hiện trôi/hỏng); kiểm chứng thuật toán trên dữ liệu thử phủ miền thiết kế; kiểm chứng từng DT thành phần (sứ, OLTC…) riêng và khi ghép.
  2. Validation: đánh giá reality gap so với đo thực trong biên sai số chấp nhận; quy trình kiểm định ngoài với dữ liệu chuẩn (ground truth); cập nhật sau sự kiện lớn; audit trail mọi quyết định/thay đổi.
  3. UQ: theo dõi thống kê sai số (trung bình, độ lệch chuẩn…); phân tích độ nhạy; truyền đạt rõ độ bất định và giới hạn mô hình; hiệu chỉnh liên tục.
  4. Sẵn sàng vận hành: tần suất cập nhật dữ liệu đủ; đào tạo người dùng; đầu ra rõ ràng, truy ngược được về dữ liệu đầu vào.
- DT tự hành hoàn toàn hiện còn hiếm; luôn cần con người giám sát suốt vòng đời DT.

## 10. Khuyến nghị (chương 8) & kết luận (chương 9)
- Đầu tư sớm vào chất lượng và tích hợp dữ liệu (số hóa hồ sơ cũ, tích hợp SCADA, thiết kế, FAT, bảo dưỡng, môi trường). Dùng kỹ thuật phát hiện ngoại lai (k-NN), xử lý thiếu dữ liệu, sinh dữ liệu cân bằng (SMOTE).
- Dùng tiêu chuẩn mở để tránh vendor lock-in. Kiến trúc thu thập linh hoạt, mở rộng được (đồng bộ thời gian, gắn time-stamp).
- Theo dõi reality gap bằng chỉ số đơn giản như MAE. Triển khai theo pha, chạy "DT offline song song" trước khi dùng thật. Hiệu chuẩn cảm biến định kỳ. DT phải chạy được ở chế độ suy giảm khi hỏng cảm biến (ước lượng trạng thái).
- Hợp nhất dữ liệu đa miền (nhiệt, DGA MBA và OLTC, điện) để giảm báo động giả. Chọn mô hình: white-box (dữ liệu thiết kế) cho MBA mới, grey-box tham số hóa bằng đo hiện trường cho MBA cũ/cải tạo.
- Quản trị dữ liệu: thỏa thuận quyền sở hữu dữ liệu giữa nhà chế tạo, công ty điện, cơ quan quản lý; bảo mật (mã hóa, tokenization, differential privacy).
- Tài liệu hướng dẫn sử dụng DT (giả định, giới hạn, miền hiệu lực); giải thích mô hình (SHAP, LIME). Không dùng "accuracy" cho bài toán mất cân bằng: một mô hình luôn đoán "bình thường" vẫn đạt khoảng 99 % accuracy nhưng vô dụng. Nên dùng Matthews Correlation Coefficient.
- Tổ chức: xác định mục tiêu và tiêu chí thành công trước; bắt đầu từ use case giá trị cao (giám sát–chẩn đoán, bảo dưỡng dự báo, tối ưu vòng đời); nâng dần qua 5 cấp; đào tạo và hợp tác bên ngoài.
- Kết luận: tiếp cận theo pha, pilot trên tài sản đại diện, chỉ mở rộng khi reality gap đã kiểm soát được trong giới hạn thỏa thuận. Kết quả nên trình bày dạng khoảng (bounded ranges) thay vì một con số.

## 11. Tài liệu CIGRE liên quan được TB 995 liệt kê (mục 2.9) – để tìm đọc tiếp
TB 414, 443, 676, 761, 771, 779, 812, **962 (Guide for transformer maintenance – thay TB 445)**, 630, 783, 735, 738, 755, 577, **659 (Transformer thermal modelling)**, 944, 900–902, 298, 529, 939 (Analysis of AC transformer reliability).
WG đang hoạt động (05/2026): D2.52 (AI), A2.60 (nhiệt động MBA), A2/D1.67 (DGA online), A2.73 (trao đổi thông tin MBA qua số hóa), A2/D1.74 (độ ẩm online), A2.75 (OLTC), A2.78 (sứ), A3/D2.52 (DT thiết bị đóng cắt), B4.104 (DT HVDC).

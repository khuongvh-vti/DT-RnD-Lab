# Fact sheet 02 – CIGRE Technical Brochures & IEEE Guides cho DT và giám sát MBA

Nguồn: tra cứu e-cigre.org, Electra, IEEE PES Transformers Committee, các cơ sở dữ liệu tiêu chuẩn, ngày 10/11/2026. Tóm tắt do Phòng R&D tự viết. Bản đầy đủ: CIGRE TB miễn phí cho hội viên CIGRE (non-member khoảng 230 €/TB); IEEE guide cần mua.

## CIGRE TB 995 (2026) – Digital twins for power transformers – Concept and future perspectives
- Nhóm soạn: JWG A2/D2.65, convenor Patrick Picher (Canada). 108 trang. Tóm tắt đăng trên Electra số 347 (08/2026). Đề cương nhóm (ToR) lập 02/2022, hạn báo cáo cuối 12/2025.
- Định nghĩa CIGRE: DT là biểu diễn ảo của tài sản/hệ thống, được cập nhật động bằng dữ liệu từ đối tượng vật lý, có khả năng dự báo và hỗ trợ ra quyết định để tạo giá trị; tương tác hai chiều ảo–thực là cốt lõi.
- Khung năng lực (capability framework) theo cấp: từ Descriptive (hiển thị trạng thái thời gian thực) → … → Autonomous (tối ưu thời gian thực tự động, tích hợp với tài sản tự hành khác). CẦN KIỂM CHỨNG tên đầy đủ các cấp trung gian trong bản gốc (dự kiến: Diagnostic, Predictive, Prescriptive).
- Mục lục đáng chú ý: thành phần & tích hợp dữ liệu của Transformer DT; trực quan hóa; kỹ thuật diễn giải dữ liệu; các loại mô hình; khảo sát ngành (lợi ích, rào cản, mức sẵn sàng dữ liệu); chương 7 về VVUQ (Verification, Validation & Uncertainty Quantification) kèm checklist cho dự án Transformer DT; khuyến nghị về chất lượng dữ liệu, chuẩn hóa, tính linh hoạt, độ tin cậy.
- Kết quả khảo sát: ứng dụng DT hiện tập trung ở cấp tài sản (asset-level).
- Ý nghĩa cho VTI: đây là tài liệu tham chiếu số 1 để thuyết phục khách hàng – dùng khung cấp năng lực để định vị sản phẩm VTI và đối thủ; dùng checklist VVUQ làm tiêu chí nghiệm thu pilot.
- Nguồn: https://www.e-cigre.org/publications/detail/995-digital-twins-for-power-transformers-concept-and-future-perspectives.html ; https://electra.cigre.org/347-august-2026/technical-brochures/digital-twins-for-power-transformers-concept-and-future-perspectives

## CIGRE TB 630 (2015) – Guide on Transformer Intelligent Condition Monitoring (TICM) systems
- WG A2.44, 09/2015, 140 trang. Nội dung: mô hình thông tin MBA, cấu trúc nút thông minh TICM, health & risk indexing, thuật toán diễn giải (chương 4), cảm biến thông minh, giám sát từng bộ phận MBA; Annex A ví dụ FMEA các phân hệ chính.
- Vai trò: nền tảng kiến trúc giám sát thông minh – tiền thân trực tiếp của Transformer DT.

## CIGRE TB 761 (2019) – Condition assessment of power transformers
- WG A2.49, 163 trang. Phương pháp đánh giá tình trạng tổng thể (health index). Được TB 995 liệt kê là đầu vào.

## CIGRE TB 771 (2019) – Advances in DGA interpretation
- JWG D1/A2.47, 76 trang. Các loại lỗi và mức độ nghiêm trọng; phương pháp Duval Triangles và Duval Pentagons; cung cấp các dải giá trị điển hình / trung gian / trước sự cố cho cả nồng độ tuyệt đối và tốc độ tăng.

## CIGRE TB 783 (2019) – DGA monitoring systems
- JWG D1/A2.47 (SC A2 & D1), ISBN 978-2-85873-485-6.
- Phân loại thiết bị DGA online theo số khí đo (M1 … M9) và loại lỗi mỗi loại phát hiện được; đánh giá hiệu năng một số thiết bị ra thị trường từ 2010 trên MBA thực (Appendix F, Table 6.2); thủ tục kiểm tra độ chính xác và thực hành triển khai.
- Cảnh báo quan trọng: kết quả DGA online và phòng thí nghiệm có sai lệch hệ thống, có thể vượt ±20–30% với từng khí → không trộn dữ liệu online với lab khi chưa đặc trưng hóa sai lệch (bias).
- Hiện chưa có một tiêu chuẩn quốc tế tổng thể về hiệu năng thiết bị DGA online. CIGRE WG A2/D1.67 đang soạn "Guidelines for online DGA monitoring" (hướng dẫn chọn thiết bị, kiểm chứng kết quả, tiêu chí đánh giá, bảo trì).

## CIGRE TB 642 (2015) – Transformer reliability survey
- WG A2.37, 122 trang. Thu thập 964 sự cố lớn giai đoạn 1996–2010, 167.459 MBA-năm, 58 công ty điện, 21 quốc gia.
- Suất sự cố: MBA trạm 0,53 %/năm, MBA tăng áp nhà máy (GSU) 0,95 %/năm (đều < 1 %).
- Vị trí sự cố chính: cuộn dây, bộ điều áp, sứ xuyên, tiếp theo là đầu ra dây dẫn. Với MBA trạm, dạng sự cố điện môi chiếm nhiều nhất, sau đó là cơ khí và điện; GSU có tỷ lệ sự cố nhiệt và điện môi cao hơn.
- Không thấy đường cong bồn tắm rõ rệt; không suy ra được tuổi nào cần thay → luận cứ cho bảo dưỡng theo tình trạng (CBM) thay vì theo tuổi.

## CIGRE TB 343 (2008) – Recommendations for condition monitoring and condition assessment facilities for transformers (WG A2.27)
## CIGRE TB 445 (2011) – Guide for transformer maintenance (WG A2.34)
## CIGRE TB 298 (2006) – Guide on transformer lifetime data management (WG A2.23)

## IEEE C57.143-2024 – Guide for Application of Monitoring Equipment to Liquid-Immersed Transformers and Components
- Bản sửa đổi của C57.143-2012. Phát hành 20/05/2025, 177 trang. DOI 10.1109/IEEESTD.2025.11007247. ISBN 979-8-8557-1673-3.
- Phạm vi: các thông số giám sát chính; phân tích rủi ro/lợi ích (cost–benefit); ứng dụng cảm biến và hệ thống giám sát; cân nhắc khi lập đặc tính kỹ thuật phần cứng, phần mềm, truyền thông. KHÔNG bao gồm diễn giải kết quả giám sát.
- Phụ lục mới đáng chú ý: Annex C (PD), Annex D (đo trực tiếp nhiệt độ cuộn dây), Annex E (phương pháp phân tích dữ liệu DGA online). Bổ sung nhiều về giám sát độ ẩm và sứ xuyên.
- ĐÍNH CHÍNH: các tài liệu trước của Phòng ghi "IEEE C57.143-2012" → từ nay trích dẫn bản 2024.

## IEEE C57.104-2019 – Guide for the Interpretation of Gases Generated in Mineral Oil-Immersed Transformers
- Dùng giới hạn theo phân vị 90th/95th cho từng khí và tốc độ tăng; bổ sung Duval Triangles/Pentagons. Thay thế bản 2008. (CẦN mua bản gốc để lấy bảng giới hạn.)

## IEEE C57.91-2011 – Guide for Loading Mineral-Oil-Immersed Transformers and Step-Voltage Regulators
- Tương đương IEC 60076-7 bên hệ IEEE (mô hình nhiệt Clause 7 và Annex G).

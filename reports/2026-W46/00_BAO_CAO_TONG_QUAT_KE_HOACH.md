# Báo cáo tổng quát kế hoạch – Phòng R&D Digital Twin (W46/2026, 10/11/2026)

Bản đầy đủ có sơ đồ và để bình luận: https://claude.ai/artifact/Bsmd2mNe1rweDP3o3yU7bA

## 1. Quyết định đã chốt
- Chạy **song song 2 luồng**: Transformer DT và Substation DT cho trạm 110 kV không người trực. Pilot triển khai và nghiệm thu tại khách hàng **trước 31/03/2027**.
- Phòng có 8 AI agent: Trưởng phòng và 7 chuyên viên `standards`, `physics`, `data_ai`, `ot_cyber`, `substation`, `benchmark`, `vn_market`.
- Model local `qwen3.5:9b` (MacBook 16 GB) và embedding `qwen3-embedding:0.6b`. Chế độ **hybrid** dùng `qwen3-max` cloud (Alibaba Model Studio) cho 5 vai trò cần suy luận sâu. Dữ liệu khách hàng luôn chạy local. Trần chi phí 10 USD/tháng.

## 2. Lộ trình & cổng
| Cổng | Ngày | Tiêu chí |
| --- | --- | --- |
| G0 | 22/11/2026 | Khách hàng ký URS; chốt trạm và MBA pilot; có file SCD, biên bản heat-run test, lịch sử DGA |
| G1 | 27/12/2026 | Demo trên dữ liệu thật: θh mô hình sai ±3 K (đề xuất); Health Index v1; sơ đồ một sợi từ SCD có trạng thái thật |
| G2 | 22/01/2027 | FAT đạt; hồ sơ an ninh mạng IEC 62443 được duyệt; chốt danh mục tín hiệu |
| (Tết) | 01–14/02/2027 | Nghỉ |
| G3 | 07/03/2027 | SAT đạt, dữ liệu chạy liên tục, đẩy được lên SCADA |
| Nghiệm thu | 31/03/2027 | Vận hành thử ≥ 3 tuần; xuất tự động báo cáo tình trạng MBA và rủi ro toàn trạm |

## 3. Kiến trúc 5 lớp
Thiết bị/cảm biến → Kết nối & Edge (IEC 61850, IEC 60870-5-104, MQTT) → Nền tảng dữ liệu (time-series, CIM/AAS) → **Mô hình DT** (IEC 60076-7, IEC 60599/Duval, PD, SCL topology) → Ứng dụng (Health Index, cảnh báo, quá tải động, sơ đồ một sợi số, báo cáo tự động). An ninh mạng theo IEC 62443/62351 áp dụng xuyên suốt các lớp.

## 4. Việc tuần W47 (11–22/11)
- [ ] `vn_market`: chốt khách hàng và trạm pilot (ứng viên: TBA 110 kV E1.20 Thanh Xuân); soạn URS.
- [ ] `substation`: nhận file SCD, dựng mô hình trạm bằng `dtlab.py scl`.
- [ ] `physics`: lấy biên bản heat-run test, hiệu chỉnh tham số IEC 60076-7.
- [ ] `ot_cyber`: danh mục tín hiệu tối thiểu, sơ đồ phân vùng OT/IT.
- [ ] `data_ai`: thiết kế Health Index v1 (CIGRE TB 761).
- [ ] `benchmark`: so sánh sản phẩm Transformer/Substation DT thương mại.
- [ ] Anh Khương: chuyển repo sang private; nạp tiêu chuẩn vào `library/`; tạo API key Model Studio (nếu dùng cloud).

## Nguồn chính
- CIGRE TB 995 (2026): https://electra.cigre.org/347-august-2026/technical-brochures/digital-twins-for-power-transformers-concept-and-future-perspectives
- TwinEU: https://www.enlit.world/library/revolutionising-the-european-energy-landscape-twineu-s-digital-twin-ambition
- EVNNPC chuyển đổi số: https://daibieunhandan.vn/evnnpc-day-manh-ung-dung-khoa-hoc-cong-nghe-doi-moi-sang-tao-va-chuyen-doi-so-trong-quan-ly-van-hanh-he-thong-dien-10384040.html
- ISO/IEC DT standards: https://sirris.be/en/inspiration/look-latest-standardisation-projects-field-digital-twins
- GMI Digital Twin in Energy & Power: https://www.gminsights.com/industry-analysis/digital-twin-in-energy-and-power-market
- Qwen pricing: https://eesel.ai/blog/qwen-pricing

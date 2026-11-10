# DT-RnD-Lab – Phòng R&D Digital Twin ngành điện (VTICorp)

Phòng nghiên cứu gồm 8 AI agent chạy **hoàn toàn local** trên máy anh bằng **Qwen + Ollama**. Mục tiêu hiện tại là
**nghiên cứu để hiểu sâu hệ thống Digital Twin ngành điện** (Transformer DT và Substation DT) theo lộ trình 5 giai đoạn.

## Nhân sự (config/team.yaml)
| Agent | Vai trò |
| --- | --- |
| `director` | Trưởng phòng: lập kế hoạch tuần, giao việc, phản biện, tổng hợp báo cáo |
| `standards` | Tiêu chuẩn & Kiến trúc DT (ISO/IEC 30173, IEC 63278, IEC 61850, CIM) |
| `physics` | Mô hình vật lý: nhiệt IEC 60076-7, DGA IEC 60599, PD IEC 60270 |
| `data_ai` | Dữ liệu & AI: Health Index, anomaly detection, hybrid physics-ML |
| `substation` | Substation DT trạm 110 kV: SCL/SCD, topology, máy cắt/GIS, tổng hợp cảnh báo |
| `ot_cyber` | OT/IoT & an ninh mạng: IEC 61850/104, MQTT, IEC 62443/62351 |
| `benchmark` | Benchmark vendor/utility quốc tế và trong nước |
| `vn_market` | Thị trường, chính sách, đấu thầu, kế hoạch pilot tại VN |

## Cài đặt (macOS Apple Silicon)
```bash
cd ~/Documents/DT-RnD-Lab
bash scripts/install_mac.sh        # tạo venv, tải model Qwen theo RAM, nạp kho tài liệu, chạy test
```
Chọn model tự động theo RAM (`config/settings.yaml` → `chat_model: auto`):
16 GB → `qwen3.5:9b` (máy anh hiện tại) · 32 GB → `qwen3.6:27b` · ≥ 48 GB → `qwen3.6:35b-a3b`. Embedding: `qwen3-embedding:0.6b`.

## Sử dụng
```bash
source .venv/bin/activate
python3 dtlab.py doctor                                  # kiểm tra máy/Ollama/model/kho
python3 dtlab.py ingest                                  # nạp tài liệu mới trong library/
python3 dtlab.py week --focus "Chốt danh mục tín hiệu MVP"  # 1 vòng nghiên cứu tuần → reports/YYYY-Www/
python3 dtlab.py ask "Ngưỡng cảnh báo DGA cho MBA 110 kV?"
python3 dtlab.py thermal --load 1.2 --ambient 35 --cooling ONAF
python3 dtlab.py scl tests/data/sample.scd                 # khung Substation DT từ file SCD
python3 dtlab.py dga --h2 100 --ch4 120 --c2h2 1 --c2h4 50 --c2h6 65
```
Chạy tự động 8:00 thứ Hai: xem hướng dẫn trong `scripts/com.vticorp.dtlab.weekly.plist`.

## Ứng dụng web trên Chrome (giống EnglishCoach) – http://localhost:8766
- **Mở nhanh:** nhấp đúp `Mo DT-RnD-Lab.command` (tự bật Ollama + server nếu chưa chạy, rồi mở Chrome).
- **Luôn chạy nền khi đăng nhập Mac + vòng nghiên cứu 08:00 thứ Hai:** `bash scripts/install_app.sh` (gỡ: `--uninstall`).
- Hoặc từ Terminal: `python3 dtlab.py serve`.

| Tab | Chức năng |
|---|---|
| 🏠 Hôm nay | Giai đoạn hiện tại & % tiến độ, phòng làm việc minh họa (bấm người để hỏi), số liệu kho, báo cáo mới nhất, nút chạy vòng tuần |
| 🌳 Sơ đồ cây | Cây tri thức: bấm nút để xem chi tiết; mọi `.md` trong `reports/` tự thành nhánh |
| 🤖 Hỏi phòng R&D | Hỏi Trưởng phòng hoặc từng chuyên viên (RAG + Qwen), lưu lịch sử, xuất từng câu trả lời hoặc toàn bộ ra Word |
| 📑 Báo cáo | Đọc mọi báo cáo tuần, nút **📄 Xuất Word** (.docx A4, header, số trang, bảng, danh sách) |
| 👥 Nhân sự | 8 thành viên: phạm vi, tài liệu gốc, câu hỏi thường trực |
| 🧮 Công cụ | Nhiệt MBA IEC 60076-7 (đồ thị θh/θo, loss of life), DGA Duval/IEC 60599, đọc SCD IEC 61850-6 |
| 📚 Kho tài liệu | Kéo thả PDF vào `library/`, nạp embedding |
| ⚙️ Hệ thống | Trạng thái Ollama, model, cloud miễn phí |

Port 8766 (EnglishCoach dùng 8765 nên hai app chạy song song được). Server chỉ nghe `127.0.0.1`.

## Chế độ hybrid – ưu tiên model MIỄN PHÍ
Model local (`qwen3.5:9b`) có giới hạn suy luận. Vì vậy các vai trò cần suy luận sâu (`director`, `physics`, `standards`,
`substation`, `data_ai`) gọi cloud theo chuỗi ưu tiên sau:

1. **Alibaba Model Studio (Singapore), quota miễn phí:** mỗi model Qwen có khoảng 1M token free trong 90 ngày.
   Code xoay vòng `qwen3.8-max → qwen3.7-max → qwen3.7-plus → qwen3.6-plus → qwen3-max → qwen3.8-flash`, dừng ở 90% quota mỗi model.
2. **OpenRouter `:free`:** khoảng 50 request/ngày (1.000/ngày nếu từng nạp ≥ 10 USD). Lệnh `dtlab.py free-models` liệt kê model free hiện có.
3. **Trả phí:** chỉ chạy khi `allow_paid: true` (mặc định **tắt**), có trần ngân sách tháng.
4. **Local Ollama:** luôn là phương án cuối, và là bắt buộc với dữ liệu khách hàng (`library/06_vti_data`).

```bash
export DASHSCOPE_API_KEY="sk-..."      # thêm vào ~/.zshrc
export OPENROUTER_API_KEY="sk-or-..."
# config/settings.yaml → cloud.enabled: true ; sửa cloud.providers[0].expires = ngày kích hoạt + 90
python3 dtlab.py doctor                # xem quota đã dùng của từng model và engine kế tiếp
```
Mỗi báo cáo mảng ghi rõ engine đã dùng. Thống kê token nằm trong `data/cloud_usage.json`.

## Cấu trúc
```
config/      settings.yaml (model, đường dẫn, deadline) · team.yaml (vai trò, tiêu chuẩn, câu hỏi thường trực)
lab/         llm.py (Ollama) · cloud.py (cloud + định tuyến hybrid) · knowledge.py (RAG SQLite) · team.py (Trưởng phòng + chuyên viên) · hardware.py
lab/physics/ transformer_thermal.py (IEC 60076-7) · dga.py (Duval 1, IEC 60599) · scl.py (đọc SCD IEC 61850-6)
library/     kho tài liệu (không đẩy PDF bản quyền lên git)
reports/     báo cáo tuần + báo cáo theo yêu cầu
tests/       kiểm thử offline (pytest)
```

## Nguyên tắc
- Dữ liệu và tài liệu ở lại máy anh; GitHub chỉ lưu code, cấu hình và báo cáo.
- Mọi nhận định phải trích nguồn [S#] từ kho; điều chưa kiểm chứng ghi là GIẢ ĐỊNH.
- Mô hình vật lý dùng tham số mặc định chỉ để thử; khi dùng thật phải lấy từ biên bản heat-run test của máy.

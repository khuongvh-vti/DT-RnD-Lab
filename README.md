# VTI R&D Lab – Phòng R&D Năng lượng & Công nghệ (VTICorp) · repo DT-RnD-Lab

Phòng nghiên cứu gồm các AI agent chạy **local** trên máy anh bằng **Qwen + Ollama**, tổ chức theo **MODULE nghiên cứu**.
Digital Twin là module đầu tiên; anh mở thêm module bất kỳ lúc nào bằng form **➕ Mở module mới** trong tab 🧩 Module.

## Tổ chức
```
Trưởng phòng (director) ── điều phối mọi module, báo cáo 3 ngày/lần
├─ Khối dùng chung (config/team.yaml): standards · data_ai · ot_cyber · benchmark · vn_market
└─ Module (config/modules.yaml) – mỗi module có mục tiêu, lộ trình, chuyên viên riêng, thư mục library/m_<module>/
   ├─ 🧬 dt            Digital Twin ngành điện          physics, substation                  [Đang nghiên cứu]
   ├─ 📡 monitoring    Online Monitoring & Chẩn đoán     pd_expert, dga_oil, sensors_thermal  [Chờ kích hoạt]
   ├─ 🩺 asset_health  Asset Management & Health Index   health_index, maintenance_strategy   [Chờ kích hoạt]
   ├─ 🔋 bess          BESS & Tích hợp NLTT              bess_tech, grid_integration          [Chờ kích hoạt]
   └─ 📊 market        Thị trường, Đấu thầu & Cơ hội VTI tender_analyst, competitor_watch     [Đang nghiên cứu]
```
- **Đang nghiên cứu** (active): được đưa vào chu kỳ báo cáo. **Chờ kích hoạt** (standby): đã dựng khung, chờ anh đưa nội dung rồi bấm ▶️ Kích hoạt. **Tạm dừng** (paused).
- **Mở module mới:** tab 🧩 Module → ➕ Mở module mới → nhập tên, mục tiêu, phạm vi, câu hỏi, tiêu chuẩn, hạn. Trưởng phòng (Qwen) tự thiết kế 2–4 chuyên viên riêng + lộ trình + từ khóa, tạo `library/m_<module>/` và bài giới thiệu trong `reports/modules/<module>/`. Ollama chưa chạy → dùng khung mặc định.
- **Báo cáo 3 ngày:** server tự chạy sau 07:00 mỗi 3 ngày (khi Ollama đang chạy; chỉnh trong `config/settings.yaml → cycle`) → `reports/cycles/<ngày>/BAO_CAO_3_NGAY.md` gồm: điểm mới, mới nghiên cứu theo từng module, tài liệu mới vào kho, cơ hội từ bản tin, quyết định cần duyệt, kế hoạch 3 ngày tới. Chạy tay: nút **🗓 Chạy chu kỳ ngay** hoặc `python3 dtlab.py cycle`.

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
python3 dtlab.py modules                                 # liệt kê module & trạng thái
python3 dtlab.py module-status bess active               # kích hoạt / tạm dừng module
python3 dtlab.py cycle --modules dt,market --focus "..." # 1 chu kỳ nghiên cứu → reports/cycles/<ngày>/
python3 dtlab.py ask "Ngưỡng cảnh báo DGA cho MBA 110 kV?"
python3 dtlab.py thermal --load 1.2 --ambient 35 --cooling ONAF
python3 dtlab.py scl tests/data/sample.scd                 # khung Substation DT từ file SCD
python3 dtlab.py dga --h2 100 --ch4 120 --c2h2 1 --c2h4 50 --c2h6 65
```
Chạy tự động: `bash scripts/install_app.sh` (server luôn chạy nền và tự làm báo cáo 3 ngày/lần).

## Ứng dụng web trên Chrome (giống EnglishCoach) – http://localhost:8766
- **Mở nhanh:** nhấp đúp `Mo DT-RnD-Lab.command` (tự bật Ollama + server nếu chưa chạy, rồi mở Chrome).
- **Luôn chạy nền khi đăng nhập Mac + vòng nghiên cứu 08:00 thứ Hai:** `bash scripts/install_app.sh` (gỡ: `--uninstall`).
- Hoặc từ Terminal: `python3 dtlab.py serve`.

| Tab | Chức năng |
|---|---|
| 🏠 Hôm nay | Thẻ tiến độ từng module, phòng làm việc minh họa (bấm người để hỏi), số liệu kho, cơ hội hôm nay, báo cáo 3 ngày mới nhất |
| 🧩 Module | Danh sách module, chi tiết (lộ trình, câu hỏi, chuyên viên riêng + mượn chung), Kích hoạt/Tạm dừng, chạy chu kỳ riêng, form ➕ Mở module mới |
| 🌳 Sơ đồ cây | Cây tri thức: bấm nút để xem chi tiết; mọi `.md` trong `reports/` tự thành nhánh |
| 🤖 Hỏi phòng R&D | Chọn module (hoặc cả phòng) rồi hỏi Trưởng phòng hoặc từng chuyên viên (RAG + Qwen), lưu lịch sử, xuất Word |
| 📰 Tin tức & Cơ hội | Tự tổng hợp 06:30 mỗi sáng (Google News VN/quốc tế, RSS, arXiv): dự án, đấu thầu, kế hoạch triển khai, bài báo, nghiên cứu ngành năng lượng; lọc **🎯 Cơ hội VTI**, Qwen gợi ý hành động; nút "Cập nhật ngay", xuất Word. Cấu hình nguồn/từ khóa: `config/news.yaml`; dữ liệu lưu `data/news/` (không đưa lên git) |
| 📑 Báo cáo | Đọc mọi báo cáo tuần, nút **📄 Xuất Word** (.docx A4, header, số trang, bảng, danh sách) |
| 👥 Nhân sự | Ban điều phối, khối dùng chung và chuyên viên từng module: phạm vi, tài liệu gốc, câu hỏi thường trực |
| 🧮 Công cụ | Nhiệt MBA IEC 60076-7 (đồ thị θh/θo, loss of life), DGA Duval/IEC 60599, đọc SCD IEC 61850-6 |
| 📚 Kho tài liệu | Kéo thả PDF vào `library/`, nạp embedding |
| ⚙️ Hệ thống | Trạng thái Ollama, model, cloud miễn phí |

Port 8766 (EnglishCoach dùng 8765 nên hai app chạy song song được). Mặc định server chỉ nghe `127.0.0.1`.

**Mở trên điện thoại:** `bash scripts/enable_phone.sh` → server mở cho mạng (yêu cầu mã truy cập), in link `http://<tên-mac>.local:8766/?key=…`. Điện thoại cùng Wi-Fi mở link 1 lần là nhớ. Ra ngoài: cài Tailscale trên Mac + điện thoại. Tắt: `bash scripts/enable_phone.sh --off`.

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
config/      settings.yaml (model, chu kỳ) · team.yaml (Trưởng phòng + khối dùng chung) · modules.yaml (module) · news.yaml
lab/         llm.py (Ollama) · cloud.py (hybrid) · knowledge.py (RAG SQLite) · team.py (Trưởng phòng, chu kỳ 3 ngày) · modules.py (module) · news.py
lab/physics/ transformer_thermal.py (IEC 60076-7) · dga.py (Duval 1, IEC 60599) · scl.py (đọc SCD IEC 61850-6)
library/     kho tài liệu (không đẩy PDF bản quyền lên git)
reports/     cycles/ (báo cáo 3 ngày) · modules/ (giới thiệu module) · news/ (bản tin) · báo cáo nghiên cứu
tests/       kiểm thử offline (pytest)
```

## Nguyên tắc
- Dữ liệu và tài liệu ở lại máy anh; GitHub chỉ lưu code, cấu hình và báo cáo.
- Mọi nhận định phải trích nguồn [S#] từ kho; điều chưa kiểm chứng ghi là GIẢ ĐỊNH.
- Mô hình vật lý dùng tham số mặc định chỉ để thử; khi dùng thật phải lấy từ biên bản heat-run test của máy.

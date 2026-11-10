"""Chẩn đoán DGA: Duval Triangle 1 và phương pháp tỷ số IEC 60599.
Chỉ áp dụng khi nồng độ khí vượt mức điển hình (typical values) – kiểm tra trước khi diễn giải."""
from __future__ import annotations

FAULTS = {
    "PD": "Phóng điện cục bộ (partial discharge)",
    "D1": "Phóng điện năng lượng thấp",
    "D2": "Phóng điện năng lượng cao",
    "T1": "Quá nhiệt < 300 °C",
    "T2": "Quá nhiệt 300–700 °C",
    "T3": "Quá nhiệt > 700 °C",
    "DT": "Hỗn hợp nhiệt và điện",
}


def duval_triangle_1(ch4: float, c2h4: float, c2h2: float) -> tuple[str, dict]:
    s = ch4 + c2h4 + c2h2
    if s <= 0:
        raise ValueError("Tổng CH4 + C2H4 + C2H2 phải > 0")
    m, e, a = 100 * ch4 / s, 100 * c2h4 / s, 100 * c2h2 / s
    pct = {"CH4": round(m, 1), "C2H4": round(e, 1), "C2H2": round(a, 1)}
    if m >= 98:
        z = "PD"
    elif a < 4 and e < 20:
        z = "T1"
    elif a < 4 and e < 50:
        z = "T2"
    elif a < 15 and e >= 50:
        z = "T3"
    elif a >= 13 and e < 23:
        z = "D1"
    elif e >= 23 and (a >= 29 or (a >= 13 and e < 40)):
        z = "D2"
    else:
        z = "DT"
    return z, pct


def iec60599_ratio(h2, ch4, c2h2, c2h4, c2h6) -> tuple[str, dict]:
    eps = 1e-9
    r1 = c2h2 / (c2h4 + eps)   # C2H2/C2H4
    r2 = ch4 / (h2 + eps)      # CH4/H2
    r5 = c2h4 / (c2h6 + eps)   # C2H4/C2H6
    r = {"C2H2/C2H4": round(r1, 3), "CH4/H2": round(r2, 3), "C2H4/C2H6": round(r5, 3)}
    if r2 < 0.1 and r5 < 0.2:
        return "PD", r
    if r1 > 1 and 0.1 <= r2 <= 0.5 and r5 > 1:
        return "D1", r
    if 0.6 <= r1 <= 2.5 and 0.1 <= r2 <= 1 and r5 > 2:
        return "D2", r
    if r1 < 0.2 and r2 > 1 and r5 > 4:
        return "T3", r
    if r1 < 0.1 and r2 > 1 and 1 <= r5 <= 4:
        return "T2", r
    if r2 > 1 and r5 < 1:
        return "T1", r
    return "ND", r  # không xác định – dùng Duval để bổ trợ


# IEC 60599:2022 Bảng A.2 – dải giá trị điển hình 90 % (µl/l) quan sát trên MBA lực (dùng CẬN TRÊN làm ngưỡng
# "điển hình"; mỗi công ty điện nên tự tính giá trị điển hình của đội máy mình – Annex A khuyến nghị).
TYPICAL_A2 = {"H2": (50, 150), "CH4": (30, 130), "C2H4": (60, 280), "C2H6": (20, 90), "CO": (400, 600),
              "CO2": (3800, 14000), "C2H2_no_oltc": (2, 20), "C2H2_oltc": (60, 280)}


def typical_check(h2, ch4, c2h2, c2h4, c2h6, co=None, co2=None, oltc_communicating=False) -> dict:
    """Bước a) Điều 9 IEC 60599: nếu mọi khí dưới giá trị điển hình → 'DGA bình thường', không cần chẩn đoán lỗi."""
    vals = {"H2": h2, "CH4": ch4, "C2H4": c2h4, "C2H6": c2h6, "CO": co, "CO2": co2,
            ("C2H2_oltc" if oltc_communicating else "C2H2_no_oltc"): c2h2}
    above = [{"gas": g.split("_")[0], "value": v, "typical_upper": TYPICAL_A2[g][1]}
             for g, v in vals.items() if v is not None and v > TYPICAL_A2[g][1]]
    note = None
    if co and co2 and co > 0:
        r = co2 / co
        if r < 3 and co >= 1000:
            note = f"CO2/CO = {r:.1f} < 3 và CO cao → có thể có giấy cách điện tham gia sự cố (IEC 60599 mục 5.5), cần xác nhận bằng khí khác / furan."
        elif r > 10 and co2 > 10000:
            note = f"CO2/CO = {r:.1f} > 10 và CO2 > 10 000 → có thể quá nhiệt nhẹ giấy (< 160 °C) hoặc oxy hóa dầu (IEC 60599 mục 5.5)."
    return {"status": "above_typical" if above else "normal", "above": above, "paper_note": note}


def diagnose(h2, ch4, c2h2, c2h4, c2h6, co=None, co2=None, oltc_communicating=False) -> dict:
    z, pct = duval_triangle_1(ch4, c2h4, c2h2)
    rz, ratios = iec60599_ratio(h2, ch4, c2h2, c2h4, c2h6)
    return {"duval": z, "duval_desc": FAULTS.get(z), "duval_pct": pct,
            "iec60599": rz, "iec60599_desc": FAULTS.get(rz, "Không xác định"), "ratios": ratios,
            "agree": z == rz, "typical": typical_check(h2, ch4, c2h2, c2h4, c2h6, co, co2, oltc_communicating)}

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


def diagnose(h2, ch4, c2h2, c2h4, c2h6) -> dict:
    z, pct = duval_triangle_1(ch4, c2h4, c2h2)
    rz, ratios = iec60599_ratio(h2, ch4, c2h2, c2h4, c2h6)
    return {"duval": z, "duval_desc": FAULTS.get(z), "duval_pct": pct,
            "iec60599": rz, "iec60599_desc": FAULTS.get(rz, "Không xác định"), "ratios": ratios,
            "agree": z == rz}

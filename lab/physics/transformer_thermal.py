"""Mô hình nhiệt MBA theo IEC 60076-7:2018 (phương pháp phương trình vi phân, giải bằng difference equations)
và tốc độ lão hóa tương đối / tổn thất tuổi thọ.

Ghi chú kỹ thuật:
- Các hệ số mặc định theo bảng thermal characteristics của IEC 60076-7 cho MBA lực (power transformer).
- Δθor, Δθhr (gradient × H) PHẢI lấy từ biên bản thử nghiệm phát nóng (heat-run test) của chính máy.
  Giá trị mặc định dưới đây chỉ để thử nghiệm, KHÔNG dùng cho kết luận vận hành.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

COOLING_DEFAULTS = {
    #        x    y    k11  k21  k22  tau_o(min) tau_w(min)
    "ONAN": (0.8, 1.3, 0.5, 2.0, 2.0, 210.0, 10.0),
    "ONAF": (0.8, 1.3, 0.5, 2.0, 2.0, 150.0, 7.0),
    "OF":   (1.0, 1.3, 1.0, 1.3, 1.0, 90.0, 7.0),
    "OD":   (1.0, 2.0, 1.0, 1.0, 1.0, 90.0, 7.0),
}


@dataclass
class ThermalParams:
    cooling: str = "ONAF"
    R: float = 6.0              # tỷ số tổn hao có tải / không tải ở dòng định mức
    d_theta_or: float = 45.0    # độ tăng nhiệt dầu đỉnh định mức (K) – lấy từ heat-run test
    d_theta_hr: float = 35.0    # độ chênh điểm nóng - dầu đỉnh định mức (K) = H·gr
    thermally_upgraded_paper: bool = True

    def coeffs(self):
        return COOLING_DEFAULTS[self.cooling]


def relative_ageing_rate(theta_h: float, upgraded: bool = True) -> float:
    """V theo IEC 60076-7: giấy thường 2^((θh-98)/6); giấy nâng cấp nhiệt exp(15000/383 - 15000/(θh+273))."""
    if upgraded:
        return math.exp(15000 / (110 + 273) - 15000 / (theta_h + 273))
    return 2 ** ((theta_h - 98) / 6)


def simulate(load_pu: list[float], ambient_c: list[float], dt_min: float, p: ThermalParams,
             theta_o0: float | None = None):
    """Mô phỏng theo bước thời gian dt_min (khuyến nghị dt ≤ τw/2).
    Trả về list dict: t_min, K, θa, θo (dầu đỉnh), θh (điểm nóng), V, loss_of_life_h (lũy kế)."""
    x, y, k11, k21, k22, tau_o, tau_w = p.coeffs()
    if dt_min > tau_w / 2:
        raise ValueError(f"dt_min={dt_min} quá lớn, cần ≤ τw/2 = {tau_w/2}")
    th_a0 = ambient_c[0]
    K0 = load_pu[0]
    # khởi tạo ở trạng thái xác lập với tải đầu
    th_o = theta_o0 if theta_o0 is not None else th_a0 + ((1 + K0**2 * p.R) / (1 + p.R)) ** x * p.d_theta_or
    dh1 = k21 * K0**y * p.d_theta_hr
    dh2 = (k21 - 1) * K0**y * p.d_theta_hr
    lol = 0.0
    out = []
    for i, (K, th_a) in enumerate(zip(load_pu, ambient_c)):
        d_th_o = dt_min / (k11 * tau_o) * (((1 + K**2 * p.R) / (1 + p.R)) ** x * p.d_theta_or - (th_o - th_a))
        d_dh1 = dt_min / (k22 * tau_w) * (k21 * p.d_theta_hr * K**y - dh1)
        d_dh2 = dt_min / (tau_o / k22) * ((k21 - 1) * p.d_theta_hr * K**y - dh2)
        th_o += d_th_o
        dh1 += d_dh1
        dh2 += d_dh2
        th_h = th_o + dh1 - dh2
        V = relative_ageing_rate(th_h, p.thermally_upgraded_paper)
        lol += V * dt_min / 60.0
        out.append({"t_min": i * dt_min, "K": K, "theta_a": th_a, "theta_o": th_o,
                    "theta_h": th_h, "V": V, "loss_of_life_h": lol})
    return out


def steady_state_hotspot(K: float, theta_a: float, p: ThermalParams) -> float:
    x, y, *_ = p.coeffs()
    return theta_a + ((1 + K**2 * p.R) / (1 + p.R)) ** x * p.d_theta_or + p.d_theta_hr * K**y


def max_load_for_hotspot(theta_h_limit: float, theta_a: float, p: ThermalParams) -> float:
    """Tải xác lập tối đa (pu) để θh không vượt giới hạn – dùng cho cảnh báo khả năng quá tải động."""
    lo, hi = 0.0, 3.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if steady_state_hotspot(mid, theta_a, p) > theta_h_limit:
            hi = mid
        else:
            lo = mid
    return lo

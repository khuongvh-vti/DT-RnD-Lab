"""Đọc file SCL/SCD (IEC 61850-6) để dựng khung Substation DT:
- Topology: Substation → VoltageLevel → Bay → ConductingEquipment (+ PowerTransformer)
- IED → LDevice → LN (prefix+lnClass+inst) và LNode gắn thiết bị nhất thứ với chức năng
Kết quả là dict JSON-able để nạp vào asset registry / hiển thị sơ đồ."""
from __future__ import annotations

import xml.etree.ElementTree as ET


def _ln(tag: str) -> str:
    return tag.split("}")[-1]


def _children(el, name):
    return [c for c in el if _ln(c.tag) == name]


def _lnodes(el):
    return [f"{n.get('iedName','')}/{n.get('ldInst','')}/{n.get('prefix','')}{n.get('lnClass','')}{n.get('lnInst','')}"
            for n in _children(el, "LNode")]


def parse_scl(path: str) -> dict:
    root = ET.parse(path).getroot()
    subs = []
    for s in _children(root, "Substation"):
        sd = {"name": s.get("name"), "transformers": [], "voltage_levels": []}
        for pt in _children(s, "PowerTransformer"):
            sd["transformers"].append({"name": pt.get("name"),
                                       "windings": [w.get("name") for w in _children(pt, "TransformerWinding")],
                                       "lnodes": _lnodes(pt)})
        for vl in _children(s, "VoltageLevel"):
            v = _children(vl, "Voltage")
            vd = {"name": vl.get("name"), "voltage": (v[0].text if v else None),
                  "multiplier": (v[0].get("multiplier") if v else None), "bays": []}
            for bay in _children(vl, "Bay"):
                vd["bays"].append({"name": bay.get("name"),
                                   "equipment": [{"name": ce.get("name"), "type": ce.get("type"),
                                                  "lnodes": _lnodes(ce)} for ce in _children(bay, "ConductingEquipment")],
                                   "transformers": [pt.get("name") for pt in _children(bay, "PowerTransformer")]})
            sd["voltage_levels"].append(vd)
        subs.append(sd)
    ieds = []
    for ied in _children(root, "IED"):
        lns = []
        for ld in ied.iter():
            if _ln(ld.tag) == "LDevice":
                for ln in ld:
                    if _ln(ln.tag) in ("LN", "LN0"):
                        lns.append(f"{ld.get('inst')}/{ln.get('prefix','')}{ln.get('lnClass')}{ln.get('inst','')}")
        ieds.append({"name": ied.get("name"), "manufacturer": ied.get("manufacturer"), "logical_nodes": lns})
    return {"substations": subs, "ieds": ieds}


# LN liên quan giám sát tình trạng thiết bị (IEC 61850-7-4) – dùng để lọc tín hiệu cho DT
CONDITION_LN = {"SIML": "Giám sát cách điện chất lỏng (DGA, độ ẩm)", "SPDC": "Phóng điện cục bộ",
                "STMP": "Nhiệt độ", "SARC": "Hồ quang", "SIMG": "Giám sát khí cách điện (SF6)",
                "YPTR": "Máy biến áp lực", "YLTC": "Bộ điều áp dưới tải", "XCBR": "Máy cắt", "XSWI": "Dao cách ly",
                "SCBR": "Giám sát máy cắt", "SOPM": "Giám sát cơ cấu truyền động", "MMXU": "Đo lường"}


def condition_signals(model: dict) -> list[dict]:
    out = []
    for ied in model["ieds"]:
        for ln in ied["logical_nodes"]:
            for cls, desc in CONDITION_LN.items():
                if cls in ln.split("/")[-1]:
                    out.append({"ied": ied["name"], "ln": ln, "class": cls, "meaning": desc})
    return out

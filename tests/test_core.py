"""Kiểm thử offline (không cần Ollama): physics + luồng phòng R&D với LLM giả."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from lab.knowledge import KnowledgeBase  # noqa: E402
from lab.physics import dga, transformer_thermal as th  # noqa: E402
from lab.team import Director  # noqa: E402


def test_ageing_rate_reference():
    assert abs(th.relative_ageing_rate(110, upgraded=True) - 1.0) < 1e-9
    assert abs(th.relative_ageing_rate(98, upgraded=False) - 1.0) < 1e-9
    assert abs(th.relative_ageing_rate(104, upgraded=False) - 2.0) < 1e-9


def test_thermal_converges_to_steady_state():
    p = th.ThermalParams(cooling="ONAN")
    n = int(24 * 60 / 3)
    res = th.simulate([1.0] * n, [20.0] * n, 3.0, p, theta_o0=20.0)
    ss = th.steady_state_hotspot(1.0, 20.0, p)
    assert abs(res[-1]["theta_h"] - ss) < 0.5


def test_max_load_monotonic():
    p = th.ThermalParams()
    assert th.max_load_for_hotspot(120, 40, p) < th.max_load_for_hotspot(120, 20, p)


def test_duval_zones():
    assert dga.duval_triangle_1(99, 0.5, 0.5)[0] == "PD"
    assert dga.duval_triangle_1(80, 10, 1)[0] == "T1"
    assert dga.duval_triangle_1(20, 75, 5)[0] == "T3"
    assert dga.duval_triangle_1(40, 10, 50)[0] == "D1"
    assert dga.duval_triangle_1(20, 40, 40)[0] == "D2"


class FakeLLM:
    def chat(self, system, user, think=False, **kw):
        return "## Kết luận\nNội dung giả lập [S1]."

    def chat_json(self, system, user, **kw):
        if "members" in user and "Chọn" in user:
            return {"members": ["physics"]}
        return [{"member": "physics", "title": "Mô hình nhiệt", "question": "IEC 60076-7?"}]

    def embed(self, texts):
        raise RuntimeError("no embed")  # buộc dùng fallback BM25


def test_director_week(tmp_path):
    s = yaml.safe_load((ROOT / "config/settings.yaml").read_text(encoding="utf-8"))
    t = yaml.safe_load((ROOT / "config/team.yaml").read_text(encoding="utf-8"))
    s["paths"]["reports"] = str(tmp_path / "reports")
    lib = tmp_path / "lib"; lib.mkdir()
    (lib / "iec60076_7_note.md").write_text("Hot-spot temperature IEC 60076-7 thermal model ONAF " * 20)
    kb = KnowledgeBase(str(tmp_path / "kb.sqlite"), FakeLLM())
    assert kb.ingest(str(lib), log=lambda *_: None) > 0
    assert kb.search("hot-spot thermal model")
    boss = Director(t, s, FakeLLM(), kb)
    path = boss.run_week("test")
    assert path.exists()
    plan = json.loads((path.parent / "00_ke_hoach_tuan.json").read_text(encoding="utf-8"))
    assert {p["member"] for p in plan} == set(t["members"])  # ai cũng có việc
    assert "Báo cáo tuần" in path.read_text(encoding="utf-8")


def test_scl_parse():
    from lab.physics import scl
    m = scl.parse_scl(str(ROOT / "tests/data/sample.scd"))
    sub = m["substations"][0]
    assert sub["name"] == "TBA110_DEMO" and sub["transformers"][0]["name"] == "T1"
    assert sub["voltage_levels"][0]["bays"][0]["equipment"][0]["type"] == "CBR"
    classes = {s["class"] for s in scl.condition_signals(m)}
    assert {"SIML", "STMP", "SPDC"} <= classes


def test_hybrid_routing_and_sensitive_guard(tmp_path, monkeypatch):
    from lab.cloud import HybridLLM, is_sensitive

    class Local(FakeLLM):
        def chat(self, system, user, **kw):
            return "LOCAL"

    class Cloud:
        last_usage = {"prompt_tokens": 1000, "completion_tokens": 500}

        def chat(self, system, user, **kw):
            return "CLOUD"

    cfg = {"enabled": True, "roles": ["director"], "monthly_budget_usd": 10,
           "base_url": "x", "model": "m", "api_key_env": "TEST_KEY"}
    monkeypatch.setenv("TEST_KEY", "k")
    h = HybridLLM(Local(), cfg, str(tmp_path), log=lambda *_: None)
    h.cloud = Cloud()
    assert h.chat("s", "u", role="director") == "CLOUD"
    assert h.chat("s", "u", role="director", sensitive=True) == "LOCAL"   # dữ liệu nhạy cảm không lên cloud
    assert h.chat("s", "u", role="benchmark") == "LOCAL"                  # vai trò không cấu hình cloud
    assert h.ledger.month_cost() > 0
    cfg["monthly_budget_usd"] = 0                                         # chạm ngân sách → local
    assert h.chat("s", "u", role="director") == "LOCAL"
    assert is_sensitive(["/x/library/06_vti_data/a.pdf"], ["library/06_vti_data"])
    assert not is_sensitive(["/x/library/01_standards/a.pdf"], ["library/06_vti_data"])

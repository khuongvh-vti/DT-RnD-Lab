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
    from lab import modules as M
    mods = M.load()
    boss = Director(t, s, FakeLLM(), kb, modules=mods)
    boss.web_get = lambda *a, **k: (_ for _ in ()).throw(OSError("offline"))  # không ra mạng trong test
    path = boss.run_cycle("test", new_docs=["01_standards/x.pdf"], highlights="- tin A")
    assert path.exists() and path.name == "BAO_CAO_3_NGAY.md"
    plan = json.loads((path.parent / "00_ke_hoach.json").read_text(encoding="utf-8"))
    active = [m for m, v in mods.items() if v["status"] == "active"]
    assert set(plan) == set(active)  # chỉ module đang nghiên cứu
    for mid in active:  # chuyên viên riêng nào của module cũng có việc
        assert set(mods[mid]["members"]) <= {p["member"] for p in plan[mid]}
        assert (path.parent / mid).is_dir()
    text = path.read_text(encoding="utf-8")
    assert "Báo cáo 3 ngày" in text and "Trạng thái các module" in text
    # chỉ chạy 1 module theo yêu cầu
    p2 = boss.run_cycle(modules=["bess"], day="2026-11-13")
    assert json.loads((p2.parent / "00_ke_hoach.json").read_text(encoding="utf-8")).keys() == {"bess"}


def test_modules_roster_and_create(tmp_path):
    from lab import modules as M
    t = yaml.safe_load((ROOT / "config/team.yaml").read_text(encoding="utf-8"))
    mods = M.load()
    r = M.roster(t, mods)
    assert "physics" in r and r["physics"]["module"] == "dt" and r["standards"]["module"] == "shared"
    assert len(r) == len(set(r))  # key duy nhất
    assert M.phase_now(mods["dt"], "2027-02-01")["code"] == "GĐ3"
    path = tmp_path / "modules.yaml"
    M.save(mods, path)
    # không có Qwen → khung mặc định
    mid = M.create({"name": "Điện gió ngoài khơi", "goal": "Hiểu OWF", "questions": "Q1?\nQ2?", "references": "IEC 61400-25",
                    "deadline": "2027-06-30"}, t, llm=None, log=lambda *_: None, path=path, root=tmp_path)
    assert mid == "dien_gio_ngoai_khoi"
    m2 = M.load(path)[mid]
    assert len(m2["members"]) == 2 and len(m2["phases"]) == 3 and m2["phases"][-1]["end"] == "2027-06-30"
    assert (tmp_path / "library" / f"m_{mid}" / "README.md").exists()
    assert (tmp_path / "reports" / "modules" / mid / "00_GIOI_THIEU_MODULE.md").exists()

    class L:  # Qwen trả JSON có key trùng → phải đổi tên
        def chat_json(self, *a, **k):
            return {"members": {"physics": {"name": "Chuyên viên X", "scope": "s", "references": ["IEC 1"], "standing_questions": ["q"]},
                                "wind_grid": {"name": "Chuyên viên Y", "scope": "s2"}},
                    "phases": [{"code": "GĐ1", "name": "A", "start": "2026-12-01", "end": "2027-01-01"}],
                    "questions": ["Q?"], "keywords": ["offshore wind"], "shared": ["standards", "khong_co"]}
    mid2 = M.create({"name": "Điện gió ngoài khơi", "goal": "g"}, t, llm=L(), log=lambda *_: None, path=path, root=tmp_path)
    m3 = M.load(path)[mid2]
    assert mid2 == "dien_gio_ngoai_khoi_2" and "physics" not in m3["members"] and f"{mid2}_physics" in m3["members"]
    assert m3["shared"] == ["standards"] and m3["keywords"] == ["offshore wind"]
    M.set_status(mid2, "paused", path)
    assert M.load(path)[mid2]["status"] == "paused"


def test_scl_parse():
    from lab.physics import scl
    m = scl.parse_scl(str(ROOT / "tests/data/sample.scd"))
    sub = m["substations"][0]
    assert sub["name"] == "TBA110_DEMO" and sub["transformers"][0]["name"] == "T1"
    assert sub["voltage_levels"][0]["bays"][0]["equipment"][0]["type"] == "CBR"
    classes = {s["class"] for s in scl.condition_signals(m)}
    assert {"SIML", "STMP", "SPDC"} <= classes


def test_free_first_rotation_and_guards(tmp_path, monkeypatch):
    from lab.cloud import HybridLLM, QuotaExceeded, is_sensitive

    class Local(FakeLLM):
        def chat(self, system, user, **kw):
            return "LOCAL"

    calls = []

    class FakeClient:
        def __init__(self, name, fail_models=()):
            self.name, self.fail = name, set(fail_models)

        def chat(self, model, system, user):
            calls.append(f"{self.name}/{model}")
            if model in self.fail:
                raise QuotaExceeded(model)
            return f"{self.name}/{model}", {"prompt_tokens": 800_000, "completion_tokens": 150_000}

    cfg = {"enabled": True, "roles": ["director"], "allow_paid": False, "providers": []}
    h = HybridLLM(Local(), cfg, str(tmp_path), log=lambda *_: None)
    free = {"name": "ms", "models": ["max", "plus"], "token_quota_per_model": 1_000_000, "quota_safety": 0.9}
    orf = {"name": "or", "models": ["q:free"], "daily_requests": 1}
    h.providers = [(free, FakeClient("ms", fail_models={"plus"})), (orf, FakeClient("or"))]

    assert h.chat("s", "u", role="director") == "ms/max"          # model free mạnh nhất trước
    assert h.chat("s", "u", role="director") == "or/q:free"       # max đã 1M ≥ 90% → plus hết quota(429) → OpenRouter
    assert h.chat("s", "u", role="director") == "LOCAL"           # OpenRouter hết lượt/ngày → local
    assert h.chat("s", "u", role="director", sensitive=True) == "LOCAL"
    assert h.chat("s", "u", role="benchmark") == "LOCAL"
    assert h.ledger.month_cost() == 0.0                            # không phát sinh phí
    assert is_sensitive(["/x/library/06_vti_data/a.pdf"], ["library/06_vti_data"])
    assert not is_sensitive(["/x/library/01_standards/a.pdf"], ["library/06_vti_data"])

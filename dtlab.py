#!/usr/bin/env python3
"""CLI Phòng R&D Digital Twin – chạy local bằng Qwen qua Ollama.

  python3 dtlab.py doctor                 # kiểm tra máy, Ollama, model
  python3 dtlab.py setup                  # tải model Qwen phù hợp RAM + embedding
  python3 dtlab.py ingest                 # nạp tài liệu trong library/ vào kho tri thức
  python3 dtlab.py week [--focus "..."]   # chạy 1 vòng tuần: giao việc → nghiên cứu → tổng hợp
  python3 dtlab.py ask "câu hỏi"          # hỏi nhanh, Trưởng phòng định tuyến tới chuyên viên
  python3 dtlab.py thermal --load 1.2 --ambient 35   # thử mô hình nhiệt IEC 60076-7
  python3 dtlab.py scl path/to/station.scd   # dựng khung Substation DT từ file SCD (IEC 61850-6)
  python3 dtlab.py free-models            # liệt kê model ':free' hiện có trên OpenRouter
  python3 dtlab.py dga --h2 100 --ch4 120 --c2h2 1 --c2h4 50 --c2h6 65
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lab.hardware import recommend_model, total_ram_gb  # noqa: E402
from lab.knowledge import KnowledgeBase  # noqa: E402
from lab.llm import OllamaClient  # noqa: E402
from lab.physics import dga, transformer_thermal as th  # noqa: E402


def load_cfg():
    s = yaml.safe_load((ROOT / "config/settings.yaml").read_text(encoding="utf-8"))
    t = yaml.safe_load((ROOT / "config/team.yaml").read_text(encoding="utf-8"))
    for k in ("library", "index_db", "reports"):
        s["paths"][k] = str(ROOT / s["paths"][k])
    return s, t


def make_llm(s) -> OllamaClient:
    o = s["ollama"]
    model = o["chat_model"]
    if model == "auto":
        model, _ = recommend_model()
    local = OllamaClient(o["host"], model, o["embed_model"], o["temperature"], o["num_ctx"], o["timeout_s"])
    from lab.cloud import HybridLLM
    return HybridLLM(local, s.get("cloud", {}), str(ROOT / "data"))


def git_sync(s, msg: str):
    if not s["git"]["auto_commit"] or not (ROOT / ".git").exists():
        return
    subprocess.run(["git", "-C", str(ROOT), "add", "reports", "config"], check=False)
    subprocess.run(["git", "-C", str(ROOT), "commit", "-m", msg], check=False)
    if s["git"]["auto_push"]:
        subprocess.run(["git", "-C", str(ROOT), "push"], check=False)


def main():
    ap = argparse.ArgumentParser(description="Phòng R&D Digital Twin (local, Qwen/Ollama)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    sub.add_parser("setup")
    sub.add_parser("ingest")
    w = sub.add_parser("week"); w.add_argument("--focus", default=""); w.add_argument("--backlog", default="")
    a = sub.add_parser("ask"); a.add_argument("question")
    t = sub.add_parser("thermal")
    t.add_argument("--load", type=float, default=1.0); t.add_argument("--ambient", type=float, default=30)
    t.add_argument("--hours", type=float, default=8); t.add_argument("--cooling", default="ONAF")
    sc = sub.add_parser("scl"); sc.add_argument("path")
    sub.add_parser("free-models")
    d = sub.add_parser("dga")
    for g in ("h2", "ch4", "c2h2", "c2h4", "c2h6"):
        d.add_argument(f"--{g}", type=float, required=True)
    args = ap.parse_args()
    s, team = load_cfg()

    if args.cmd == "doctor":
        ram = total_ram_gb(); rec, note = recommend_model(ram)
        llm = make_llm(s); models = llm.list_models()
        print(f"RAM: {ram:.0f} GB → đề xuất {rec} ({note})")
        print(f"Ollama: {'OK' if models else 'KHÔNG KẾT NỐI được – chạy `ollama serve`'}")
        print(f"Model đã có: {', '.join(models) or '(chưa có)'}")
        print(f"Model chat dùng: {llm.chat_model} | embedding: {llm.embed_model}")
        print("Kho tri thức:", KnowledgeBase(s['paths']['index_db']).stats())
        c = s.get("cloud", {})
        if llm.cloud:
            print(f"Cloud: BẬT cho {', '.join(c['roles'])} | trả phí: {'cho phép' if c.get('allow_paid') else 'KHÔNG'}"
                  f" | chi phí tháng ≈ ${llm.ledger.month_cost():.2f}")
            print("\n".join(llm.status()))
            print("Engine kế tiếp cho director:", llm.route("director", False))
        else:
            print("Cloud: TẮT (enabled=false hoặc chưa đặt API key) → mọi agent chạy local")
    elif args.cmd == "setup":
        llm = make_llm(s)
        for m in (llm.local.chat_model, llm.local.embed_model):
            print(f"ollama pull {m}"); subprocess.run(["ollama", "pull", m], check=False)
    elif args.cmd == "ingest":
        llm = make_llm(s)
        kb = KnowledgeBase(s["paths"]["index_db"], llm, s["rag"]["chunk_chars"], s["rag"]["overlap_chars"])
        n = kb.ingest(s["paths"]["library"]); print(f"Đã nạp {n} đoạn. {kb.stats()}")
    elif args.cmd in ("week", "ask"):
        from lab.team import Director
        llm = make_llm(s)
        kb = KnowledgeBase(s["paths"]["index_db"], llm, s["rag"]["chunk_chars"], s["rag"]["overlap_chars"])
        boss = Director(team, s, llm, kb)
        if args.cmd == "week":
            p = boss.run_week(args.focus, args.backlog)
            git_sync(s, f"Báo cáo tuần {p.parent.name}")
        else:
            print(boss.ask(args.question))
    elif args.cmd == "thermal":
        p = th.ThermalParams(cooling=args.cooling)
        n = int(args.hours * 60 / 3)
        res = th.simulate([args.load] * n, [args.ambient] * n, 3.0, p)
        last = res[-1]
        print(f"Sau {args.hours} h ở K={args.load} pu, θa={args.ambient} °C ({args.cooling}): "
              f"θo={last['theta_o']:.1f} °C, θh={last['theta_h']:.1f} °C, "
              f"tổn thất tuổi thọ ≈ {last['loss_of_life_h']:.1f} h")
        print(f"Tải xác lập tối đa để θh ≤ 120 °C: {th.max_load_for_hotspot(120, args.ambient, p):.2f} pu")
        print("Lưu ý: tham số mặc định chỉ để thử – cần Δθor, Δθhr từ heat-run test của máy thật.")
    elif args.cmd == "free-models":
        # Liệt kê model miễn phí hiện có trên OpenRouter để cập nhật config (danh mục free thay đổi thường xuyên)
        import json, urllib.request
        with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=30) as r:
            models = json.loads(r.read())["data"]
        free = [m for m in models if m["id"].endswith(":free")]
        for m in sorted(free, key=lambda m: -(m.get("context_length") or 0)):
            print(f"{m['id']:<55} ctx={m.get('context_length')}")
        print(f"\n{len(free)} model free. Qwen: " + ", ".join(m["id"] for m in free if "qwen" in m["id"]))
    elif args.cmd == "scl":
        import json
        from lab.physics import scl
        m = scl.parse_scl(args.path)
        print(json.dumps(m["substations"], ensure_ascii=False, indent=2))
        print("Tín hiệu giám sát tình trạng (IEC 61850-7-4):")
        for x in scl.condition_signals(m):
            print(f"  {x['ied']}/{x['ln']}  [{x['class']}] {x['meaning']}")
    elif args.cmd == "dga":
        r = dga.diagnose(args.h2, args.ch4, args.c2h2, args.c2h4, args.c2h6)
        for k, v in r.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()

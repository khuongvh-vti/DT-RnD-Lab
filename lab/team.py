"""Phòng R&D AI: Trưởng phòng giao việc → chuyên viên nghiên cứu (RAG) → Trưởng phòng phản biện, tổng hợp."""
from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from pathlib import Path

from .cloud import is_sensitive
from .knowledge import KnowledgeBase, format_context


@dataclass
class Task:
    member: str
    title: str
    question: str


@dataclass
class MemberReport:
    member: str
    name: str
    task: Task
    body: str
    sources: list[str] = field(default_factory=list)
    sensitive: bool = False
    engine: str = "local"


class Member:
    def __init__(self, key: str, spec: dict, common_rules: str, llm, kb: KnowledgeBase, top_k: int = 8,
                 sensitive_paths: list[str] | None = None):
        self.key, self.spec, self.llm, self.kb, self.top_k = key, spec, llm, kb, top_k
        self.sensitive_paths = sensitive_paths or []
        self.system = (f"{common_rules}\n\nVai trò của bạn: {spec['name']}.\nPhạm vi: {spec['scope']}.\n"
                       f"Tiêu chuẩn/tài liệu nền cần bám: {', '.join(spec['references'])}.")

    def work(self, task: Task, context_note: str = "") -> MemberReport:
        hits = self.kb.search(f"{task.title}. {task.question}", k=self.top_k)
        prompt = (f"NHIỆM VỤ TUẦN: {task.title}\nCÂU HỎI: {task.question}\n{context_note}\n\n"
                  f"TÀI LIỆU THAM KHẢO:\n{format_context(hits)}\n\n"
                  "Viết báo cáo mảng của bạn (markdown, ≤ 600 từ) gồm: 1) Kết luận chính; 2) Phân tích kỹ thuật "
                  "có trích [S#]; 3) Đề xuất áp dụng cho MVP Q1/2027; 4) Câu hỏi mở / dữ liệu cần bổ sung.")
        sens = is_sensitive([h.source for h in hits], self.sensitive_paths)
        engine = self.llm.route(self.key, sens) if hasattr(self.llm, "route") else "local"
        body = self.llm.chat(self.system, prompt, role=self.key, sensitive=sens)
        srcs = [f"[S{i}] {Path(h.source).name} – tr.{h.page}" for i, h in enumerate(hits, 1)]
        return MemberReport(self.key, self.spec["name"], task, body, srcs, sens, engine)


class Director:
    def __init__(self, cfg_team: dict, settings: dict, llm, kb: KnowledgeBase):
        self.team, self.settings, self.llm, self.kb = cfg_team, settings, llm, kb
        d = cfg_team["director"]
        self.system = f"{cfg_team['common_rules']}\n\nVai trò của bạn: {d['name']}.\n{d['mission']}"
        top_k = settings["rag"]["top_k"]
        sens_paths = (settings.get("cloud") or {}).get("sensitive_paths", [])
        self.members = {k: Member(k, v, cfg_team["common_rules"], llm, kb, top_k, sens_paths)
                        for k, v in cfg_team["members"].items()}

    # 1) Lập kế hoạch tuần
    def plan_week(self, focus: str = "", backlog: str = "") -> list[Task]:
        roster = "\n".join(f"- {k}: {m.spec['name']} – {m.spec['scope']}; câu hỏi thường trực: "
                           f"{'; '.join(m.spec.get('standing_questions', []))}" for k, m in self.members.items())
        proj = self.settings["project"]
        prompt = (f"Dự án: {proj['name']}, hạn {proj['deadline']}, giai đoạn hiện tại: {proj['current_phase']}.\n"
                  f"Trọng tâm tuần do anh Khương giao: {focus or '(không có – tự đề xuất theo lộ trình)'}\n"
                  f"Tồn đọng tuần trước:\n{backlog or '(không có)'}\n\nNhân sự:\n{roster}\n\n"
                  'Giao đúng 1 nhiệm vụ cụ thể, đo được cho MỖI thành viên. Trả JSON dạng '
                  '[{"member":"<key>","title":"...","question":"..."}]')
        try:
            items = self.llm.chat_json(self.system, prompt, role="director")
            tasks = [Task(i["member"], i["title"], i["question"]) for i in items if i.get("member") in self.members]
        except Exception:
            tasks = []
        # đảm bảo ai cũng có việc
        have = {t.member for t in tasks}
        for k, m in self.members.items():
            if k not in have:
                q = (m.spec.get("standing_questions") or [m.spec["scope"]])[0]
                tasks.append(Task(k, f"Nghiên cứu thường trực – {m.spec['name']}", q))
        return tasks

    # 2) Giao việc + 3) phản biện + 4) tổng hợp
    def run_week(self, focus: str = "", backlog: str = "", log=print) -> Path:
        week = dt.date.today().isocalendar()
        out_dir = Path(self.settings["paths"]["reports"]) / f"{week[0]}-W{week[1]:02d}"
        out_dir.mkdir(parents=True, exist_ok=True)
        tasks = self.plan_week(focus, backlog)
        (out_dir / "00_ke_hoach_tuan.json").write_text(
            json.dumps([t.__dict__ for t in tasks], ensure_ascii=False, indent=2), encoding="utf-8")
        reports: list[MemberReport] = []
        for t in tasks:
            log(f"→ {t.member}: {t.title}")
            r = self.members[t.member].work(t)
            reports.append(r)
            (out_dir / f"{t.member}.md").write_text(
                f"# {r.name}\n\n**Nhiệm vụ:** {t.title}\n\n**Câu hỏi:** {t.question}\n\n"
                f"_Engine: {r.engine}{' · dữ liệu nhạy cảm → local' if r.sensitive else ''}_\n\n{r.body}\n\n"
                "## Nguồn trong kho\n" + "\n".join(f"- {s}" for s in r.sources), encoding="utf-8")
        summary = self.synthesize(reports)
        path = out_dir / "BAO_CAO_TUAN.md"
        path.write_text(summary, encoding="utf-8")
        log(f"✓ Báo cáo tuần: {path}")
        return path

    def synthesize(self, reports: list[MemberReport]) -> str:
        body = "\n\n".join(f"### {r.name}\nNhiệm vụ: {r.task.title}\n{r.body}" for r in reports)
        sections = "\n".join(f"## {s}" for s in self.team["director"]["report_sections"])
        prompt = (f"Dưới đây là báo cáo của các chuyên viên.\n\n{body}\n\n"
                  "Phản biện: chỉ ra nhận định thiếu nguồn hoặc mâu thuẫn giữa các mảng. Sau đó viết BÁO CÁO TUẦN "
                  f"gửi anh Khương theo đúng các mục:\n{sections}\nCuối báo cáo thêm mục '## Phản biện nội bộ'.")
        sens = any(r.sensitive for r in reports)
        text = self.llm.chat(self.system, prompt, role="director", sensitive=sens)
        today = dt.date.today().isoformat()
        return f"# Báo cáo tuần Phòng R&D Digital Twin – {today}\n\n{text}\n"

    # Hỏi nhanh: Trưởng phòng định tuyến tới chuyên viên phù hợp
    def ask(self, question: str) -> str:
        keys = ", ".join(f"{k} ({m.spec['scope']})" for k, m in self.members.items())
        try:
            route = self.llm.chat_json(self.system, role="director", user=f"Câu hỏi: {question}\nChọn 1–2 chuyên viên phù hợp nhất "
                                       f"trong: {keys}. Trả JSON {{\"members\":[\"key\"]}}")
            chosen = [k for k in route.get("members", []) if k in self.members][:2] or ["standards"]
        except Exception:
            chosen = ["standards"]
        parts = [self.members[k].work(Task(k, "Câu hỏi của anh Khương", question)) for k in chosen]
        return self.synthesize(parts)

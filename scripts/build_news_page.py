"""Tạo trang đọc bản tin năng lượng cho điện thoại: web/dist/news.html
Dùng: python3 scripts/build_news_page.py  (lấy tối đa 14 bản tin mới nhất trong reports/news/)"""
import sys, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.site import md_to_html

def main():
    files = sorted((ROOT / "reports/news").glob("*.md"), reverse=True)[:14]
    items = []
    for f in files:
        md = f.read_text(encoding="utf-8")
        m = re.match(r"#\s*(.+)", md)
        items.append({"day": f.name[:10], "title": m.group(1) if m else f.stem,
                      "html": md_to_html(re.sub(r"^#.*\n", "", md, count=1))})
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__DATA__", data)
    out = ROOT / "web/dist/news.html"; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8"); print(out)

TEMPLATE = """<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bản tin năng lượng & Cơ hội VTI</title>
<style>
:root{--g:linear-gradient(135deg,#5B4BF5,#8B5CF6 55%,#EC4899);--bg:#f6f5ff;--card:#fff;--tx:#1f1d3a;--mut:#6b6894;--bd:#e6e3ff}
@media(prefers-color-scheme:dark){:root{--bg:#14132a;--card:#1d1c38;--tx:#ecebff;--mut:#a5a2cc;--bd:#2e2c55}}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--tx);line-height:1.55;font-size:16px}
header{background:var(--g);color:#fff;padding:18px 16px 14px}
header h1{margin:0;font-size:20px}header p{margin:4px 0 0;opacity:.9;font-size:13px}
.days{display:flex;gap:8px;overflow-x:auto;padding:10px 12px;background:var(--card);border-bottom:1px solid var(--bd);position:sticky;top:0}
.days button{border:1px solid var(--bd);background:transparent;color:var(--tx);border-radius:999px;padding:6px 12px;white-space:nowrap;font-size:14px}
.days button.on{background:var(--g);color:#fff;border-color:transparent}
main{max-width:860px;margin:0 auto;padding:12px}
article{background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:4px 16px 16px}
h2{font-size:18px;margin:20px 0 8px;padding-bottom:4px;border-bottom:2px solid #8B5CF6}
blockquote{margin:12px 0;padding:8px 12px;border-left:4px solid #EC4899;background:rgba(236,72,153,.07);border-radius:6px;color:var(--mut);font-size:14px}
.tw{overflow-x:auto}table{border-collapse:collapse;font-size:14px;min-width:640px}
th,td{border:1px solid var(--bd);padding:6px 8px;vertical-align:top}th{background:rgba(139,92,246,.12);text-align:left}
a{color:#8B5CF6;word-break:break-word}li{margin:4px 0}
footer{text-align:center;color:var(--mut);font-size:12px;padding:16px}
</style></head><body>
<header><h1>📰 Bản tin năng lượng & 🎯 Cơ hội VTI</h1><p>Phòng R&D Digital Twin · cập nhật mỗi sáng</p></header>
<nav class="days" id="days"></nav>
<main><article id="doc"></article></main>
<footer>Tổng hợp từ nguồn công khai – kiểm tra lại HSMT trước khi quyết định dự thầu.</footer>
<script>
const NEWS=__DATA__;
const days=document.getElementById('days'),doc=document.getElementById('doc');
function show(i){[...days.children].forEach((b,j)=>b.classList.toggle('on',i===j));
 const n=NEWS[i];doc.innerHTML='<h2 style="border:0">'+n.title+'</h2>'+n.html;
 doc.querySelectorAll('table').forEach(t=>{const w=document.createElement('div');w.className='tw';t.replaceWith(w);w.appendChild(t)});
 doc.querySelectorAll('a').forEach(a=>{a.target='_blank';a.rel='noopener'});scrollTo(0,0)}
NEWS.forEach((n,i)=>{const b=document.createElement('button');const d=n.day.split('-');b.textContent=d[2]+'/'+d[1];b.onclick=()=>show(i);days.appendChild(b)});
if(NEWS.length)show(0);else doc.textContent='Chưa có bản tin.';
</script></body></html>"""
if __name__ == "__main__":
    main()

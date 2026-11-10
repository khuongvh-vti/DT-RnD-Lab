"""Xuất markdown (báo cáo của phòng R&D) ra file Word .docx – chỉ dùng thư viện chuẩn Python.

Hỗ trợ: tiêu đề #..####, đoạn văn, **đậm**, *nghiêng*, `code`, [liên kết](url) và URL trần, danh sách
gạch đầu dòng / đánh số (lồng nhau theo thụt lề), bảng | a | b |, khối code ```, trích dẫn >, đường kẻ ---.
Trang A4, lề 2 cm, font Arial (hiển thị tiếng Việt tốt), header tên dự án, footer "Trang X / Y".
"""
from __future__ import annotations

import datetime as dt
import io
import re
import zipfile
from xml.sax.saxutils import escape

FONT = "Arial"
MONO = "Consolas"
ACCENT = "4B3FD6"      # tím đậm (cùng tông giao diện) cho tiêu đề
HEAD_FILL = "EEEBFF"   # nền hàng tiêu đề bảng
PAGE_W, MARGIN = 11906, 1134  # A4, lề 2 cm (twip)
TEXT_W = PAGE_W - 2 * MARGIN


def _x(s: str) -> str:
    return escape(s, {'"': "&quot;"})


class _Doc:
    def __init__(self):
        self.body: list[str] = []
        self.links: list[str] = []   # URL của hyperlink → rId
        self.nums: list[tuple[int, int]] = []  # (numId, abstractId) cho từng danh sách

    # ---------------------------------------------------------------- inline
    def rid(self, url: str) -> str:
        if url not in self.links:
            self.links.append(url)
        return f"rIdL{self.links.index(url) + 1}"

    def runs(self, text: str, base: str = "") -> str:
        """Chuyển chuỗi markdown inline thành các <w:r> (và <w:hyperlink>)."""
        out = []
        pat = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\(https?://[^)\s]+\)|https?://[^\s)<>]+|(?<![*\w])\*[^*\s][^*]*\*(?!\*))")
        pos = 0
        for m in pat.finditer(text):
            if m.start() > pos:
                out.append(self.run(text[pos:m.start()], base))
            tok = m.group(0)
            if tok.startswith("**"):
                out.append(self.run(tok[2:-2], base + "<w:b/>"))
            elif tok.startswith("`"):
                out.append(self.run(tok[1:-1], base + f'<w:rFonts w:ascii="{MONO}" w:hAnsi="{MONO}" w:cs="{MONO}"/>'
                                    '<w:shd w:val="clear" w:color="auto" w:fill="F3F2FB"/>'))
            elif tok.startswith("["):
                lm = re.match(r"\[([^\]]+)\]\((\S+)\)", tok)
                out.append(self.link(lm.group(1), lm.group(2), base))
            elif tok.startswith("http"):
                url = tok.rstrip(".,;:")
                out.append(self.link(url, url, base))
                if len(url) < len(tok):
                    out.append(self.run(tok[len(url):], base))
            else:
                out.append(self.run(tok[1:-1], base + "<w:i/>"))
            pos = m.end()
        if pos < len(text):
            out.append(self.run(text[pos:], base))
        return "".join(out)

    @staticmethod
    def run(t: str, rpr: str = "") -> str:
        if not t:
            return ""
        return f'<w:r>{f"<w:rPr>{rpr}</w:rPr>" if rpr else ""}<w:t xml:space="preserve">{_x(t)}</w:t></w:r>'

    def link(self, label: str, url: str, base: str = "") -> str:
        return (f'<w:hyperlink r:id="{self.rid(url)}" w:history="1">'
                + self.run(label, base + '<w:rStyle w:val="Hyperlink"/>') + "</w:hyperlink>")

    # ---------------------------------------------------------------- block
    def para(self, inner: str, style: str = "", ppr: str = "") -> None:
        p = (f'<w:pStyle w:val="{style}"/>' if style else "") + ppr
        self.body.append(f"<w:p>{f'<w:pPr>{p}</w:pPr>' if p else ''}{inner}</w:p>")

    def new_list(self, ordered: bool) -> int:
        num_id = len(self.nums) + 1
        self.nums.append((num_id, 1 if ordered else 0))
        return num_id

    def table(self, head: list[str], rows: list[list[str]]) -> None:
        n = max(len(head), *(len(r) for r in rows)) if rows else len(head)
        # độ rộng cột theo độ dài nội dung (tối thiểu 8%)
        clean = lambda c: re.sub(r"[*`]|\[([^\]]+)\]\([^)]+\)", r"\1", c)
        cells = lambda i: [clean(r[i]) for r in [head] + rows if i < len(r)]
        # bề rộng tối thiểu = từ dài nhất (≈110 twip/ký tự ở cỡ 9,5 pt + lề ô) để không ngắt giữa chữ
        mins = [min(max([len(w) for c in cells(i) for w in c.split()] or [3]) * 110 + 240, TEXT_W // 3) for i in range(n)]
        want = [max(min(sum(len(c) for c in cells(i)) / max(1, len(cells(i))), 80), 4) for i in range(n)]
        want = [w ** 0.7 for w in want]  # cân bằng hơn giữa cột dài/ngắn
        spare = max(0, TEXT_W - sum(mins))
        widths = [int(mins[i] + spare * want[i] / sum(want)) for i in range(n)]
        if sum(mins) > TEXT_W:  # quá nhiều cột: chia tỷ lệ
            widths = [int(TEXT_W * m / sum(mins)) for m in mins]
        b = '<w:{0} w:val="single" w:sz="4" w:space="0" w:color="C9C6E3"/>'
        borders = "".join(b.format(s) for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
        x = [f'<w:tbl><w:tblPr><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders>'
             '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>'
             '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'
             + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"]
        for ri, r in enumerate([head] + rows):
            hdr = ri == 0
            x.append("<w:tr>" + ('<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' if hdr else '<w:trPr><w:cantSplit/></w:trPr>'))
            for ci in range(n):
                cell = r[ci] if ci < len(r) else ""
                shade = f'<w:shd w:val="clear" w:color="auto" w:fill="{HEAD_FILL}"/>' if hdr else ""
                x.append(f'<w:tc><w:tcPr><w:tcW w:w="{widths[ci]}" w:type="dxa"/>{shade}</w:tcPr>'
                         f'<w:p><w:pPr><w:pStyle w:val="TableText"/></w:pPr>{self.runs(cell, "<w:b/>" if hdr else "")}</w:p></w:tc>')
            x.append("</w:tr>")
        x.append("</w:tbl>")
        self.body.append("".join(x))
        self.para("", "Spacer")


def markdown_to_body(doc: _Doc, md: str) -> None:
    lines, i = md.splitlines(), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        # bảng
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            doc.table(head, rows)
            continue
        # tiêu đề
        m = re.match(r"^(#{1,6})\s+(.*)", ln)
        if m:
            level = min(len(m.group(1)), 4)
            doc.para(doc.runs(m.group(2)), {1: "Title", 2: "Heading1", 3: "Heading2", 4: "Heading3"}[level])
            i += 1
            continue
        # đường kẻ
        if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", ln):
            doc.para("", "Rule")
            i += 1
            continue
        # khối code
        if ln.startswith("```"):
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                doc.para(doc.run(lines[i] or " ", ""), "Code")
                i += 1
            i += 1
            continue
        # trích dẫn
        if ln.lstrip().startswith(">"):
            q = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                q.append(lines[i].lstrip()[1:].strip())
                i += 1
            doc.para(doc.runs(" ".join(q)), "Quote")
            continue
        # danh sách (lồng theo thụt lề)
        if re.match(r"^\s*([-*+]|\d+[.)])\s+", ln):
            ids: dict[tuple[int, bool], int] = {}
            while i < len(lines) and re.match(r"^\s*([-*+]|\d+[.)])\s+", lines[i]):
                raw = lines[i]
                lvl = min((len(raw) - len(raw.lstrip())) // 2, 2)
                ordered = bool(re.match(r"^\s*\d+[.)]", raw))
                key = (lvl, ordered)
                if key not in ids:
                    ids[key] = doc.new_list(ordered)
                for k in [k for k in ids if k[0] > lvl]:  # danh sách con kết thúc → đánh số lại lần sau
                    del ids[k]
                t = re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", raw)
                t = re.sub(r"^\[( |x|X)\]\s*", lambda mm: "☑ " if mm.group(1).lower() == "x" else "☐ ", t)
                i += 1
                while i < len(lines) and lines[i].startswith("   ") and lines[i].strip() and \
                        not re.match(r"^\s*([-*+]|\d+[.)])\s+", lines[i]):
                    t += " " + lines[i].strip()
                    i += 1
                doc.para(doc.runs(t), "ListParagraph",
                         f'<w:numPr><w:ilvl w:val="{lvl}"/><w:numId w:val="{ids[key]}"/></w:numPr>')
            continue
        # đoạn văn
        para = [ln.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(\s*#|\s*\||\s*[-*+]\s|\s*\d+[.)]\s|```|\s*>)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        doc.para(doc.runs(" ".join(para)))


# ------------------------------------------------------------------ package parts
def _styles() -> str:
    def ps(sid, name, ppr="", rpr="", based="Normal", nxt="Normal", extra=""):
        return (f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/><w:basedOn w:val="{based}"/>'
                f'<w:next w:val="{nxt}"/>{extra}<w:qFormat/><w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')
    color = f'<w:color w:val="{ACCENT}"/>'
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:eastAsia="{FONT}" w:cs="{FONT}"/>'
        '<w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="vi-VN"/></w:rPr></w:rPrDefault>'
        '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
        '<w:pPr><w:jc w:val="both"/></w:pPr></w:style>'
        + ps("Title", "Title", '<w:spacing w:after="80"/><w:jc w:val="left"/>', f'<w:b/><w:sz w:val="36"/><w:szCs w:val="36"/>{color}')
        + ps("Subtitle", "Subtitle", '<w:spacing w:after="240"/><w:pBdr><w:bottom w:val="single" w:sz="12" w:space="6" '
             f'w:color="{ACCENT}"/></w:pBdr><w:jc w:val="left"/>', '<w:color w:val="6B6B85"/><w:sz w:val="20"/>')
        + ps("Heading1", "heading 1", '<w:keepNext/><w:spacing w:before="320" w:after="120"/><w:jc w:val="left"/><w:outlineLvl w:val="0"/>',
             f'<w:b/><w:sz w:val="30"/><w:szCs w:val="30"/>{color}')
        + ps("Heading2", "heading 2", '<w:keepNext/><w:spacing w:before="240" w:after="80"/><w:jc w:val="left"/><w:outlineLvl w:val="1"/>',
             '<w:b/><w:sz w:val="26"/><w:szCs w:val="26"/><w:color w:val="1E1B3A"/>')
        + ps("Heading3", "heading 3", '<w:keepNext/><w:spacing w:before="200" w:after="60"/><w:jc w:val="left"/><w:outlineLvl w:val="2"/>',
             '<w:b/><w:i/><w:sz w:val="23"/><w:color w:val="1E1B3A"/>')
        + ps("ListParagraph", "List Paragraph", '<w:spacing w:after="60"/><w:ind w:left="720"/><w:contextualSpacing/>')
        + ps("TableText", "Table Text", '<w:spacing w:after="0" w:line="252" w:lineRule="auto"/><w:jc w:val="left"/>',
             '<w:sz w:val="19"/><w:szCs w:val="19"/>')
        + ps("Code", "Code", '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/><w:jc w:val="left"/>'
             '<w:shd w:val="clear" w:color="auto" w:fill="F3F2FB"/><w:ind w:left="284"/>',
             f'<w:rFonts w:ascii="{MONO}" w:hAnsi="{MONO}" w:cs="{MONO}"/><w:sz w:val="18"/>')
        + ps("Quote", "Quote", f'<w:ind w:left="567"/><w:pBdr><w:left w:val="single" w:sz="18" w:space="8" w:color="8B5CF6"/></w:pBdr>',
             '<w:i/><w:color w:val="44405E"/>')
        + ps("Rule", "Rule", '<w:spacing w:after="120"/><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="C9C6E3"/></w:pBdr>')
        + ps("Spacer", "Spacer", '<w:spacing w:after="60" w:line="120" w:lineRule="exact"/>')
        + ps("Header", "header", '<w:jc w:val="left"/><w:spacing w:after="0"/>', '<w:sz w:val="16"/><w:color w:val="6B6B85"/>')
        + ps("Footer", "footer", '<w:jc w:val="right"/><w:spacing w:after="0"/>', '<w:sz w:val="16"/><w:color w:val="6B6B85"/>')
        + '<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/>'
          '<w:rPr><w:color w:val="2563EB"/><w:u w:val="single"/></w:rPr></w:style>'
        '</w:styles>')


def _numbering(nums: list[tuple[int, int]]) -> str:
    bullets = ["•", "–", "▪"]
    fmts = [("decimal", "%1."), ("lowerLetter", "%2)"), ("lowerRoman", "%3.")]

    def lvls(ordered):
        out = []
        for l in range(3):
            ind = f'<w:pPr><w:ind w:left="{720 + 360 * l}" w:hanging="360"/></w:pPr>'
            if ordered:
                fmt, txt = fmts[l]
                out.append(f'<w:lvl w:ilvl="{l}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/><w:lvlText w:val="{txt}"/>'
                           f'<w:lvlJc w:val="left"/>{ind}</w:lvl>')
            else:
                out.append(f'<w:lvl w:ilvl="{l}"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="{bullets[l]}"/>'
                           f'<w:lvlJc w:val="left"/>{ind}<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/></w:rPr></w:lvl>')
        return "".join(out)
    absn = "".join(f'<w:abstractNum w:abstractNumId="{a}"><w:multiLevelType w:val="hybridMultilevel"/>{lvls(a == 1)}</w:abstractNum>'
                   for a in (0, 1))
    insts = "".join(f'<w:num w:numId="{n}"><w:abstractNumId w:val="{a}"/>'
                    + ("".join(f'<w:lvlOverride w:ilvl="{l}"><w:startOverride w:val="1"/></w:lvlOverride>' for l in range(3)) if a == 1 else "")
                    + "</w:num>" for n, a in nums)
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">{absn}{insts}</w:numbering>')


NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')


def _fld(instr: str) -> str:
    return (f'<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r>')


def markdown_to_docx(md: str, title: str | None = None, subtitle: str = "", header: str = "Phòng R&D Digital Twin – VTICorp",
                     author: str = "DT-RnD-Lab") -> bytes:
    """Trả về nội dung file .docx (bytes)."""
    doc = _Doc()
    text = md
    if title is None:
        m = re.search(r"^#\s+(.+)$", md, re.M)
        title = m.group(1).strip() if m else "Báo cáo"
        if m:
            text = md[:m.start()] + md[m.end():]
    doc.para(doc.runs(title), "Title")
    doc.para(doc.run(subtitle or f"Xuất ngày {dt.date.today().strftime('%d/%m/%Y')} · {header}"), "Subtitle")
    markdown_to_body(doc, text)

    sect = (f'<w:sectPr><w:headerReference w:type="default" r:id="rIdH"/><w:footerReference w:type="default" r:id="rIdF"/>'
            f'<w:pgSz w:w="{PAGE_W}" w:h="16838"/><w:pgMar w:top="{MARGIN}" w:right="{MARGIN}" w:bottom="{MARGIN}" '
            f'w:left="{MARGIN}" w:header="567" w:footer="567" w:gutter="0"/></w:sectPr>')
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {NS}><w:body>'
                + "".join(doc.body) + sect + "</w:body></w:document>")
    hdr = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:hdr {NS}><w:p><w:pPr><w:pStyle w:val="Header"/>'
           f'</w:pPr>{doc.run(header)}</w:p></w:hdr>')
    ftr = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr {NS}><w:p><w:pPr><w:pStyle w:val="Footer"/></w:pPr>'
           + doc.run("Trang ") + _fld("PAGE") + doc.run(" / ") + _fld("NUMPAGES") + "</w:p></w:ftr>")
    if not doc.nums:
        doc.new_list(False)  # numbering.xml cần ít nhất một num
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rIdS" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            '<Relationship Id="rIdN" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
            '<Relationship Id="rIdH" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>'
            '<Relationship Id="rIdF" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
            '<Relationship Id="rIdT" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
            + "".join(f'<Relationship Id="rIdL{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" '
                      f'Target="{_x(u)}" TargetMode="External"/>' for i, u in enumerate(doc.links, 1))
            + "</Relationships>")
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
            '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
            '<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
            '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
            '</Types>'),
        "_rels/.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '</Relationships>'),
        "docProps/core.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f'<dc:title>{_x(title)}</dc:title><dc:creator>{_x(author)}</dc:creator>'
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>'),
        "word/document.xml": document,
        "word/styles.xml": _styles(),
        "word/numbering.xml": _numbering(doc.nums),
        "word/settings.xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                              '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                              '<w:defaultTabStop w:val="720"/><w:compat>'
                              '<w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>'
                              '</w:compat></w:settings>'),
        "word/header1.xml": hdr,
        "word/footer1.xml": ftr,
        "word/_rels/document.xml.rels": rels,
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    return buf.getvalue()

"""把 results/final_report.md 导出为 A4 PDF（Markdown → HTML → Edge headless 打印）。

用法：
    python experiments/export_report_pdf.py

只读 final_report.md 与 results/figures/，输出：
    results/final_report.html（中间文件）
    results/final_report.pdf
"""

from __future__ import annotations

import base64
import html
import os
import re
import shutil
import subprocess
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "results" / "final_report.md"
HTML_PATH = ROOT / "results" / "final_report.html"
PDF_PATH = ROOT / "results" / "final_report.pdf"

# 可用环境变量 EDGE_PATH 指定浏览器；否则自动查找 Edge / Chrome。
EDGE_CANDIDATES = [
    Path(os.environ.get("EDGE_PATH", "")),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
]

CSS = """
@page { size: A4; margin: 15mm 14mm 15mm 14mm; }
* { box-sizing: border-box; }
body {
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
  font-size: 10.2pt; line-height: 1.62; color: #111827; margin: 0;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
h1, h2, h3, h4 { font-weight: 700; color: #0f172a; page-break-after: avoid; }
h1 { font-size: 23pt; margin: 0 0 6px; }
h2 { font-size: 15.5pt; margin: 22px 0 8px; padding-bottom: 4px; border-bottom: 1.5px solid #d1d5db; }
h3 { font-size: 12.5pt; margin: 16px 0 6px; }
h4 { font-size: 11pt; margin: 12px 0 4px; }
p { margin: 6px 0; }
ul, ol { margin: 6px 0 6px 1.4em; padding: 0; }
li { margin: 3px 0; }
a { color: #1d4ed8; text-decoration: none; }
strong { color: #0f172a; }
code {
  font-family: Consolas, "Cascadia Mono", monospace; font-size: 9pt;
  background: #f3f4f6; padding: 1px 4px; border-radius: 3px;
}
pre {
  background: #f6f8fa; border: 1px solid #e5e7eb; border-radius: 4px;
  padding: 8px 10px; overflow: auto; page-break-inside: avoid;
}
pre code { background: none; padding: 0; font-size: 8.6pt; }
blockquote {
  margin: 8px 0; padding: 6px 10px; border-left: 3px solid #6b7280;
  background: #f9fafb; color: #374151;
}
hr { border: none; border-top: 1px solid #e5e7eb; margin: 14px 0; }
table {
  width: 100%; border-collapse: collapse; margin: 8px 0 10px;
  font-size: 8.6pt; page-break-inside: avoid;
}
th, td { border: 0.6px solid #d1d5db; padding: 3px 5px; vertical-align: top; text-align: left; }
th { background: #f3f4f6; font-weight: 600; }
tr:nth-child(even) td { background: #fbfbfc; }
img {
  display: block; max-width: 100%; max-height: 150mm;
  margin: 8px auto; page-break-inside: avoid;
}
figure { margin: 8px 0; page-break-inside: avoid; }
em { color: #4b5563; }
.cover {
  height: 250mm; display: flex; flex-direction: column; justify-content: center;
  page-break-after: always; text-align: left;
}
.cover .title { font-size: 30pt; font-weight: 700; color: #0f172a; line-height: 1.25; }
.cover .subtitle { font-size: 14pt; color: #374151; margin-top: 10px; }
.cover .meta { font-size: 10.5pt; color: #4b5563; margin-top: 40px; line-height: 1.9; }
.cover .rule { width: 60mm; height: 3px; background: #2563eb; margin: 22px 0; }
"""


def image_to_data_uri(path: Path) -> str:
    """把 PNG 内嵌成 data URI，避免 headless 打印时相对路径失效。"""
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def embed_images(md_text: str) -> str:
    def repl(match: re.Match) -> str:
        alt, src = match.group(1), match.group(2)
        if src.startswith("http"):
            return match.group(0)
        path = (MD_PATH.parent / src).resolve()
        uri = image_to_data_uri(path)
        return f"![{alt}]({uri})" if uri else match.group(0)

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl, md_text)


def find_edge() -> Path:
    for name in ("msedge", "google-chrome", "chromium"):
        found = shutil.which(name)
        if found:
            return Path(found)
    for p in EDGE_CANDIDATES:
        if str(p) not in ("", ".") and p.is_file():
            return p
    raise SystemExit(
        "Edge/Chrome not found; set EDGE_PATH to the browser executable"
    )


def main() -> None:
    md_text = MD_PATH.read_text(encoding="utf-8")
    lines = md_text.splitlines()
    title = lines[0].lstrip("# ").strip() if lines else "BBN 最终报告"
    body_md = "\n".join(lines[1:]).lstrip()
    # 封面已经包含元信息，正文从第一个二级标题开始，避免重复
    head_idx = body_md.find("## ")
    if head_idx > 0 and "版本：" in body_md[:head_idx]:
        body_md = body_md[head_idx:]

    body_html = markdown.markdown(
        embed_images(body_md),
        extensions=["tables", "fenced_code", "sane_lists"],
    )

    cover = f"""
    <div class="cover">
      <div class="title">{html.escape(title)}</div>
      <div class="rule"></div>
      <div class="subtitle">机制筛查、负结果与边界</div>
      <div class="meta">
        版本：v0.22.0-phase7-recurrent-ei<br/>
        日期：2026-10-23<br/>
        范围：Phase 0–5（P0–P5）、Phase 6a、Phase 7a（2–22 细胞）<br/>
        预注册：HANDOFF.md · docs/parameter_policy.md<br/>
        数据与图：results/ · results/figures/<br/>
        仓库：本仓库根目录
      </div>
    </div>
    """

    html_doc = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<title>{html.escape(title)}</title>
<style>{CSS}</style></head>
<body>
{cover}
{body_html}
</body></html>
"""
    HTML_PATH.write_text(html_doc, encoding="utf-8")

    edge = find_edge()
    cmd = [
        str(edge),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_PATH}",
        HTML_PATH.as_uri(),
    ]
    subprocess.run(cmd, check=True, timeout=300)
    print(f"wrote {HTML_PATH}")
    print(f"wrote {PDF_PATH} ({PDF_PATH.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

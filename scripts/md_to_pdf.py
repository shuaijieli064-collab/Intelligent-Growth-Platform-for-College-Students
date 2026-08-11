"""Markdown 转 PDF 转换脚本.

使用 markdown + weasyprint 将 Markdown 文件转换为高质量 PDF。
"""
import sys
import markdown
from weasyprint import HTML
from pathlib import Path


def md_to_pdf(md_path: str, pdf_path: str | None = None) -> str:
    """将 Markdown 文件转换为 PDF.

    Args:
        md_path: Markdown 文件路径
        pdf_path: 输出 PDF 路径（可选，默认与 md 同名）

    Returns:
        生成的 PDF 文件路径
    """
    md_file = Path(md_path).resolve()
    if not md_file.exists():
        print(f"错误：文件不存在 {md_file}")
        sys.exit(1)

    if pdf_path is None:
        pdf_path = str(md_file.with_suffix(".pdf"))

    # 读取 Markdown
    with md_file.open("r", encoding="utf-8") as f:
        md_content = f.read()

    # 转换为 HTML，支持表格、代码高亮等扩展
    html_body = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "toc", "attr_list", "nl2br"],
    )

    # 完整 HTML 文档，带专业排版 CSS
    html_full = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
@page {{
    size: A4;
    margin: 2.5cm 2cm 2.5cm 2cm;
    @bottom-center {{
        content: "第 " counter(page) " 页 / 共 " counter(pages) " 页";
        font-size: 9pt;
        color: #999;
        font-family: "Microsoft YaHei", "SimSun", sans-serif;
    }}
    @top-right {{
        content: "大学生智能成长平台";
        font-size: 8pt;
        color: #bbb;
        font-family: "Microsoft YaHei", "SimSun", sans-serif;
    }}
}}

@page :first {{
    @top-right {{
        content: "";
    }}
}}

body {{
    font-family: "Microsoft YaHei", "SimSun", "Helvetica", sans-serif;
    font-size: 10.5pt;
    line-height: 1.8;
    color: #333;
    max-width: 100%;
}}

h1 {{
    font-size: 22pt;
    color: #1a3a6b;
    text-align: center;
    margin-top: 60pt;
    margin-bottom: 30pt;
    padding-bottom: 15pt;
    border-bottom: 2pt solid #1a3a6b;
    page-break-after: always;
}}

h2 {{
    font-size: 15pt;
    color: #1a3a6b;
    margin-top: 25pt;
    margin-bottom: 12pt;
    padding-bottom: 6pt;
    border-bottom: 1pt solid #ccc;
    page-break-after: avoid;
}}

h3 {{
    font-size: 12pt;
    color: #2c5282;
    margin-top: 18pt;
    margin-bottom: 8pt;
    page-break-after: avoid;
}}

p {{
    margin: 6pt 0;
    text-align: justify;
}}

strong {{
    color: #1a3a6b;
}}

ul, ol {{
    margin: 6pt 0;
    padding-left: 24pt;
}}

li {{
    margin: 3pt 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}}

th {{
    background-color: #1a3a6b;
    color: white;
    font-weight: bold;
    text-align: center;
    padding: 6pt 8pt;
    border: 1pt solid #1a3a6b;
}}

td {{
    padding: 5pt 8pt;
    border: 1pt solid #ddd;
    text-align: left;
    vertical-align: top;
}}

tr:nth-child(even) {{
    background-color: #f7f9fc;
}}

tr {{
    page-break-inside: avoid;
}}

code {{
    background-color: #f4f4f4;
    padding: 1pt 4pt;
    border-radius: 3pt;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 9.5pt;
    color: #c0392b;
}}

pre {{
    background-color: #2d2d2d;
    color: #f8f8f2;
    padding: 10pt 14pt;
    border-radius: 5pt;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.5;
}}

pre code {{
    background: none;
    color: inherit;
    padding: 0;
}}

hr {{
    border: none;
    border-top: 1pt solid #ddd;
    margin: 18pt 0;
}}

blockquote {{
    border-left: 4pt solid #1a3a6b;
    margin: 10pt 0;
    padding: 5pt 15pt;
    background-color: #f7f9fc;
    color: #555;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # 转换为 PDF
    print(f"正在生成 PDF...")
    HTML(string=html_full).write_pdf(pdf_path)
    print(f"PDF 已生成：{pdf_path}")

    return pdf_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/md_to_pdf.py <input.md> [output.pdf]")
        sys.exit(1)

    md_path = sys.argv[1]
    pdf_path = sys.argv[2] if len(sys.argv) > 2 else None
    md_to_pdf(md_path, pdf_path)

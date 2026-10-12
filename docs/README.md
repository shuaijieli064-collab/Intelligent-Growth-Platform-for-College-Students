# 文档目录

本目录存放项目的所有说明文档。

| 文档 | 说明 |
|------|------|
| [手动启动指南.md](手动启动指南.md) | 本机启动步骤：桌面版 / Web 版一键与手动启动、依赖安装、数据库初始化 |
| [项目计划书.md](项目计划书.md) | 课程设计项目计划书（源文件，Markdown 格式） |
| 项目计划书.docx | 项目计划书 Word 版（由 `scripts/generate_plan_docx.py` 生成） |
| 项目计划书.pdf | 项目计划书 PDF 版（由 `scripts/generate_plan_pdf.py` 生成） |
| [design/](design/) | Web 前端界面设计稿 |

## 再生成计划书

如需更新 Word / PDF 版本：

```bash
python scripts/generate_plan_docx.py
python scripts/generate_plan_pdf.py
```

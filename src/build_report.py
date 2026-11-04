"""Render out/report.html (standalone) and out/artifact.html (body only, for hosting) from out/results.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "out" / "results.json").read_text())
tpl = (ROOT / "src" / "report_template.html").read_text()
body = tpl.replace("/*DATA*/", json.dumps(data).replace("</", "<\\/"))
(ROOT / "out" / "artifact.html").write_text(body)
(ROOT / "out" / "report.html").write_text(
    '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    + body.replace("<div class=\"wrap\">", "</head><body>\n<div class=\"wrap\">", 1) + "\n</body></html>\n")
print("wrote out/report.html and out/artifact.html")

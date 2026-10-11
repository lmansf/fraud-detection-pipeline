"""Wraps animation.html into artifact.html (player controls + page chrome) for publishing as a claude.ai artifact."""
from pathlib import Path

here = Path(__file__).parent
src = (here / "animation.html").read_text()
svg = src[src.index("<svg"):src.index("</svg>") + 6]
js = src[src.index("<script>") + 8:src.index("// Live preview when opened")]
svg = svg.replace('<svg id="stage"', '<svg id="stage" role="img" aria-label="Animated walkthrough: an Owl Park checkout is scored in real time by Model 1, events land in Supabase raw tables, Databricks refines them through bronze, silver and gold layers, and gold feeds Model 1, the Model 2 safety net and self-service dashboards."', 1)
head, tail = (here / "artifact_template.html").read_text().split("<!--SPLIT-->")
page = head.replace("<!--SVG-->", svg) + js + tail
(here / "artifact.html").write_text(page)
print("wrote artifact.html", len(page))

import markdown
import pathlib

src = pathlib.Path("content/ebook-toxina-botulinica.md")
out = pathlib.Path("content/ebook-toxina-botulinica.html")

text = src.read_text(encoding="utf-8")

md = markdown.Markdown(
    extensions=["tables", "toc", "fenced_code", "sane_lists", "attr_list"],
    extension_configs={"toc": {"title": "Conteúdo", "permalink": False}},
)
body = md.convert(text)
toc = md.toc

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Toxina Botulínica — Conteúdo extraído</title>
<style>
  :root {{
    --bg: #fafaf9; --fg: #1f2937; --muted: #6b7280; --line: #e5e7eb;
    --accent: #4f46e5; --accent-soft: #eef2ff; --warn-bg: #fff7ed; --warn-line: #fdba74;
    --code-bg: #fee2e2; --code-fg: #b91c1c; --maxw: 820px;
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    margin: 0; background: var(--bg); color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.65; font-size: 17px;
  }}
  .wrap {{ display: flex; gap: 32px; max-width: 1200px; margin: 0 auto; padding: 24px 20px 80px; }}
  nav.toc {{
    flex: 0 0 260px; position: sticky; top: 16px; align-self: flex-start;
    max-height: calc(100vh - 32px); overflow-y: auto; font-size: 14px;
    border: 1px solid var(--line); border-radius: 12px; background: #fff; padding: 14px 16px;
  }}
  nav.toc .toctitle {{ font-weight: 700; font-size: 13px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); margin-bottom: 8px; }}
  nav.toc ul {{ list-style: none; margin: 0; padding-left: 0; }}
  nav.toc ul ul {{ padding-left: 14px; }}
  nav.toc li {{ margin: 3px 0; }}
  nav.toc a {{ color: var(--fg); text-decoration: none; }}
  nav.toc a:hover {{ color: var(--accent); }}
  main {{ flex: 1 1 auto; max-width: var(--maxw); background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 36px 44px; }}
  h1 {{ font-size: 30px; line-height: 1.25; margin: 0 0 6px; }}
  h2 {{ font-size: 23px; margin: 38px 0 12px; padding-top: 14px; border-top: 2px solid var(--accent-soft); }}
  h3 {{ font-size: 19px; margin: 26px 0 8px; color: #374151; }}
  p {{ margin: 10px 0; }}
  a {{ color: var(--accent); }}
  table {{ border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 15px; }}
  th, td {{ border: 1px solid var(--line); padding: 8px 11px; text-align: left; vertical-align: top; }}
  th {{ background: var(--accent-soft); }}
  tr:nth-child(even) td {{ background: #fafafa; }}
  blockquote {{ margin: 16px 0; padding: 12px 16px; background: var(--warn-bg); border-left: 4px solid var(--warn-line); border-radius: 0 8px 8px 0; color: #7c2d12; }}
  blockquote p {{ margin: 6px 0; }}
  code {{ background: var(--code-bg); color: var(--code-fg); padding: 1px 6px; border-radius: 5px; font-size: 14px; font-weight: 600; }}
  hr {{ border: none; border-top: 1px solid var(--line); margin: 26px 0; }}
  ul, ol {{ padding-left: 22px; }}
  li {{ margin: 4px 0; }}
  .banner {{ background: var(--accent-soft); border: 1px solid #c7d2fe; border-radius: 12px; padding: 12px 16px; font-size: 14px; color: #3730a3; margin-bottom: 22px; }}
  @media (max-width: 860px) {{
    .wrap {{ flex-direction: column; padding: 14px 12px 60px; }}
    nav.toc {{ position: static; flex: none; max-height: none; }}
    main {{ padding: 22px 18px; border-radius: 12px; }}
    body {{ font-size: 16px; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <nav class="toc">{toc}</nav>
  <main>
    <div class="banner">Prévia do conteúdo extraído — visual neutro, só para leitura/revisão. O app final terá identidade própria.</div>
    {body}
  </main>
</div>
</body>
</html>
"""

out.write_text(html, encoding="utf-8")
print("Wrote", out, f"({len(html):,} bytes)")

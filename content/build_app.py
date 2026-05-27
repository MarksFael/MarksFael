"""Gera um app web de página única (arquivo HTML autocontido) a partir do
manuscrito consolidado. Curso navegável + consulta rápida + busca + progresso."""
import json
import re
import pathlib
import markdown

SRC = pathlib.Path("content/ebook-toxina-botulinica.md")
OUT = pathlib.Path("app/index.html")
OUT.parent.mkdir(parents=True, exist_ok=True)


def slug(s, i):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return f"{i:02d}-{s[:40] or 'sec'}"


def render(md_text):
    md = markdown.Markdown(extensions=["tables", "sane_lists", "fenced_code", "attr_list"])
    return md.convert(md_text.strip())


def strip_tags(html):
    return re.sub(r"<[^>]+>", " ", html)


# --- Parse manuscript into intro + parts(sections) -------------------------
lines = SRC.read_text(encoding="utf-8").splitlines()
intro_lines, parts = [], []
cur_part = None
cur_sec = None
seen_part = False

for ln in lines:
    if ln.startswith("# ") and not ln.startswith("## "):
        continue  # doc H1
    if ln.startswith("## "):
        seen_part = True
        cur_part = {"title": ln[3:].strip(), "intro": [], "sections": []}
        cur_sec = None
        parts.append(cur_part)
        continue
    if ln.startswith("### ") and cur_part is not None:
        cur_sec = {"title": ln[4:].strip(), "body": []}
        cur_part["sections"].append(cur_sec)
        continue
    if not seen_part:
        intro_lines.append(ln)
    elif cur_sec is not None:
        cur_sec["body"].append(ln)
    else:
        cur_part["intro"].append(ln)

# --- Build flat page list + sidebar groups ---------------------------------
pages = []  # {id,title,part,html,text}
groups = []  # {part, items:[{id,title}]}
idx = 0

intro_html = render("\n".join(intro_lines))
pages.append({"id": "inicio", "title": "Início", "part": "", "html": intro_html,
              "text": strip_tags(intro_html)})

for p in parts:
    part_title = p["title"]
    intro_md = "\n".join(p["intro"]).strip()
    items = []
    if p["sections"]:
        for si, s in enumerate(p["sections"]):
            idx += 1
            sid = slug(s["title"], idx)
            body_md = "\n".join(s["body"]).strip()
            if si == 0 and intro_md:
                body_md = intro_md + "\n\n" + body_md
            html = render(body_md)
            pages.append({"id": sid, "title": s["title"], "part": part_title,
                          "html": html, "text": strip_tags(html)})
            items.append({"id": sid, "title": s["title"]})
    else:
        idx += 1
        sid = slug(part_title, idx)
        html = render(intro_md)
        pages.append({"id": sid, "title": part_title, "part": part_title,
                      "html": html, "text": strip_tags(html)})
        items.append({"id": sid, "title": part_title})
    groups.append({"part": part_title, "items": items})

# --- Consulta rápida: cartões sintetizados (valores [revisar]) -------------
consulta = {
    "doses": [
        ["Testa (frontal)", "10–30 U / ponto", "45°", "1 cm da sobrancelha; 1–2 cm entre pontos"],
        ["Glabela", "20–50 U / ponto", "45° / 90°", "Nunca com a ponta voltada ao olho"],
        ["Periorbital (orbicular do olho)", "2–4 U / ponto", "45° / 90°", "Sobre base óssea; 1 cm / 1 dedo do olho"],
        ["Levantador do lábio / LLSAN", "10–20 U / ponto", "90°", "1 cm horizontal a partir da asa do nariz"],
    ],
    "conversao": [
        "1 unidade americana = 2,5 unidades Speywood (Dysport)",
        "Dysport 300 ≈ 120 U americanas",
        "Dysport 500 ≈ 200 U americanas",
        "Equivalência recomendada: 2,5 : 1",
    ],
    "links": [
        ["Reconstituição (seca × tradicional)", "reconstitui"],
        ["Contagem nas seringas (30U/50U/100U)", "seringa"],
        ["Marcas autorizadas no Brasil", "marca"],
        ["Suplementação (Fitase e Zinco)", "suplementa"],
    ],
}

DATA = json.dumps({"pages": pages, "groups": groups, "consulta": consulta},
                  ensure_ascii=False)

# --- Shell (CSS + JS) ------------------------------------------------------
SHELL = r"""<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Toxina Botulínica — App (protótipo)</title>
<style>
:root{--bg:#f7f7f6;--panel:#fff;--fg:#1f2937;--muted:#6b7280;--line:#e5e7eb;
--accent:#4f46e5;--soft:#eef2ff;--warn-bg:#fff7ed;--warn-line:#fdba74;
--code-bg:#fee2e2;--code-fg:#b91c1c;--ok:#16a34a;}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font-size:16px;line-height:1.62;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{position:sticky;top:0;z-index:20;background:var(--panel);border-bottom:1px solid var(--line);
display:flex;align-items:center;gap:12px;padding:10px 16px}
header .brand{font-weight:700;font-size:15px;white-space:nowrap}
header .brand small{display:block;font-weight:500;color:var(--muted);font-size:11px}
#search{flex:1;max-width:520px;padding:9px 12px;border:1px solid var(--line);border-radius:10px;font-size:14px}
.btn{border:1px solid var(--line);background:#fff;border-radius:10px;padding:8px 12px;font-size:13px;cursor:pointer}
.btn.menu{display:none}
.progress{font-size:12px;color:var(--muted);white-space:nowrap}
.progress b{color:var(--accent)}
.layout{display:flex;gap:0;max-width:1240px;margin:0 auto}
aside{flex:0 0 290px;border-right:1px solid var(--line);background:var(--panel);
height:calc(100vh - 57px);position:sticky;top:57px;overflow-y:auto;padding:14px 12px}
aside .quick{display:block;width:100%;text-align:left;background:var(--soft);border:1px solid #c7d2fe;
color:#3730a3;font-weight:600;border-radius:10px;padding:10px 12px;cursor:pointer;margin-bottom:12px}
.grp{margin:10px 4px 4px;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);font-weight:700}
.nav a{display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:8px;color:var(--fg);
text-decoration:none;font-size:14px;cursor:pointer}
.nav a:hover{background:var(--soft)}
.nav a.active{background:var(--accent);color:#fff}
.nav a .dot{width:7px;height:7px;border-radius:50%;background:transparent;flex:0 0 auto}
.nav a.done .dot{background:var(--ok)}
.nav a.active .dot{background:#fff}
.nav a.hidden{display:none}
main{flex:1;min-width:0;padding:26px 36px 90px}
article{max-width:780px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:30px 38px}
.crumb{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}
h1.t{font-size:25px;margin:0 0 14px}
.markme{display:inline-flex;align-items:center;gap:7px;font-size:13px;color:var(--muted);cursor:pointer;
border:1px solid var(--line);border-radius:20px;padding:5px 12px;margin-bottom:18px}
.markme.on{background:#dcfce7;border-color:#86efac;color:#15803d}
.content :is(h2,h3){scroll-margin-top:70px}
.content h2{font-size:21px;margin:26px 0 10px}
.content h3{font-size:18px;margin:20px 0 8px;color:#374151}
.content p{margin:9px 0}
.content table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
.content th,.content td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
.content th{background:var(--soft)}
.content tr:nth-child(even) td{background:#fafafa}
.content blockquote{margin:14px 0;padding:11px 15px;background:var(--warn-bg);border-left:4px solid var(--warn-line);
border-radius:0 8px 8px 0;color:#7c2d12}
.content code{background:var(--code-bg);color:var(--code-fg);padding:1px 6px;border-radius:5px;font-size:13px;font-weight:600}
.content ul,.content ol{padding-left:22px}.content hr{border:none;border-top:1px solid var(--line);margin:22px 0}
mark{background:#fde68a;padding:0 2px;border-radius:3px}
.nextprev{display:flex;justify-content:space-between;gap:10px;margin-top:24px;max-width:780px}
.nextprev button{flex:1;text-align:left;border:1px solid var(--line);background:#fff;border-radius:10px;padding:11px 14px;cursor:pointer}
.nextprev button:last-child{text-align:right}.nextprev button:disabled{opacity:.4;cursor:default}
.nextprev small{display:block;color:var(--muted);font-size:11px}
.cards{display:grid;gap:16px;max-width:780px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 22px}
.card h3{margin:0 0 10px;font-size:17px}
.card.warn{background:var(--warn-bg);border-color:var(--warn-line)}
.card ul{margin:0;padding-left:20px}.card li{margin:5px 0}
.qlink{display:inline-block;margin:5px 8px 0 0;background:var(--soft);border:1px solid #c7d2fe;color:#3730a3;
border-radius:20px;padding:6px 13px;font-size:13px;cursor:pointer}
.empty{color:var(--muted);padding:20px}
@media(max-width:880px){.btn.menu{display:block}
aside{position:fixed;left:0;top:57px;z-index:30;transform:translateX(-105%);transition:.2s;box-shadow:0 10px 30px rgba(0,0,0,.15)}
aside.open{transform:translateX(0)}
main{padding:18px 14px 80px}article{padding:20px 18px}header .brand small{display:none}}
</style></head><body>
<header>
<button class="btn menu" id="menuBtn">☰</button>
<div class="brand">Toxina Botulínica<small>protótipo — visual neutro</small></div>
<input id="search" placeholder="Buscar (doses, músculos, marcas…)">
<span class="progress" id="prog"></span>
</header>
<div class="layout">
<aside id="aside">
<button class="quick" id="quickBtn">⚡ Consulta rápida</button>
<div class="nav" id="nav"></div>
</aside>
<main id="main"></main>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
const PAGES=D.pages, GROUPS=D.groups, CONS=D.consulta;
const byId=Object.fromEntries(PAGES.map(p=>[p.id,p]));
const order=PAGES.map(p=>p.id);
const norm=s=>(s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
const KEY='tb_progress';
let done=JSON.parse(localStorage.getItem(KEY)||'{}');
const saveDone=()=>localStorage.setItem(KEY,JSON.stringify(done));

function buildNav(){
  const nav=document.getElementById('nav');nav.innerHTML='';
  GROUPS.forEach(g=>{
    if(g.part){const h=document.createElement('div');h.className='grp';h.textContent=g.part;nav.appendChild(h);}
    g.items.forEach(it=>{
      const a=document.createElement('a');a.dataset.id=it.id;
      a.innerHTML='<span class="dot"></span><span class="lbl">'+it.title+'</span>';
      a.onclick=()=>show(it.id);nav.appendChild(a);
    });
  });
  // item "Início" no topo (antes dos grupos)
  const a=document.createElement('a');a.dataset.id='inicio';
  a.innerHTML='<span class="dot"></span><span class="lbl">Início</span>';
  a.onclick=()=>show('inicio');nav.insertBefore(a,nav.firstChild);
  refreshNav();
}
function refreshNav(){
  document.querySelectorAll('.nav a').forEach(a=>{
    a.classList.toggle('done',!!done[a.dataset.id]);
  });
  const total=PAGES.length,d=PAGES.filter(p=>done[p.id]).length;
  document.getElementById('prog').innerHTML='Progresso: <b>'+d+'/'+total+'</b>';
}
function setActive(id){document.querySelectorAll('.nav a').forEach(a=>a.classList.toggle('active',a.dataset.id===id));}

let current=null;
function show(id){
  const p=byId[id];if(!p)return;current=id;
  const i=order.indexOf(id);
  const prev=order[i-1],next=order[i+1];
  const m=document.getElementById('main');
  m.innerHTML=
    '<article>'+
    (p.part?'<div class="crumb">'+p.part+'</div>':'')+
    '<h1 class="t">'+p.title+'</h1>'+
    '<span class="markme'+(done[id]?' on':'')+'" id="mark">'+
      '<span>'+(done[id]?'✓ Lido':'Marcar como lido')+'</span></span>'+
    '<div class="content">'+p.html+'</div>'+
    '</article>'+
    '<div class="nextprev">'+
    '<button '+(prev?'':'disabled')+' id="bprev">'+(prev?'<small>Anterior</small>'+byId[prev].title:'')+'</button>'+
    '<button '+(next?'':'disabled')+' id="bnext">'+(next?'<small>Próximo</small>'+byId[next].title:'')+'</button>'+
    '</div>';
  document.getElementById('mark').onclick=()=>{done[id]=!done[id];saveDone();refreshNav();show(id);};
  if(prev)document.getElementById('bprev').onclick=()=>show(prev);
  if(next)document.getElementById('bnext').onclick=()=>show(next);
  setActive(id);window.scrollTo(0,0);closeAside();
  const q=document.getElementById('search').value.trim();if(q)highlight(q);
}

function showConsulta(){
  current=null;setActive('');
  let doses='<table><thead><tr><th>Região</th><th>Dose média*</th><th>Ângulo</th><th>Observação</th></tr></thead><tbody>'+
    CONS.doses.map(r=>'<tr><td>'+r[0]+'</td><td><b>'+r[1]+'</b></td><td>'+r[2]+'</td><td>'+r[3]+'</td></tr>').join('')+
    '</tbody></table>';
  let conv='<ul>'+CONS.conversao.map(x=>'<li>'+x+'</li>').join('')+'</ul>';
  let links=CONS.links.map(l=>'<span class="qlink" data-q="'+l[1]+'">'+l[0]+'</span>').join('');
  document.getElementById('main').innerHTML=
    '<div class="cards">'+
    '<div class="card"><h3>⚡ Consulta rápida</h3><p style="color:var(--muted);margin:0">Atalhos para os dados mais usados. Toque num atalho para abrir o capítulo completo.</p></div>'+
    '<div class="card"><h3>Doses por região</h3>'+doses+'<p style="font-size:12px;color:var(--muted)">*Valores médios extraídos do material — <b>confira no original antes de aplicar</b>.</p></div>'+
    '<div class="card"><h3>Conversão de unidades</h3>'+conv+'</div>'+
    '<div class="card warn"><h3>Ir para tabelas completas</h3>'+links+'</div>'+
    '</div>';
  document.querySelectorAll('.qlink').forEach(el=>el.onclick=()=>{
    const t=norm(el.dataset.q);const hit=PAGES.find(p=>norm(p.title).includes(t));if(hit)show(hit.id);
  });
  window.scrollTo(0,0);closeAside();
}

function highlight(q){
  const nq=norm(q);if(!nq)return;
  document.querySelectorAll('.content').forEach(c=>{
    const walk=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);const nodes=[];
    while(walk.nextNode())nodes.push(walk.currentNode);
    nodes.forEach(n=>{
      if(norm(n.nodeValue).includes(nq)&&n.parentNode){
        const span=document.createElement('span');
        span.innerHTML=n.nodeValue.replace(new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>');
        n.parentNode.replaceChild(span,n);
      }
    });
  });
}

function doSearch(){
  const q=document.getElementById('search').value.trim();const nq=norm(q);
  document.querySelectorAll('.nav a').forEach(a=>{
    const p=byId[a.dataset.id];const hit=!nq||norm(p.title).includes(nq)||norm(p.text).includes(nq);
    a.classList.toggle('hidden',!hit);
  });
  if(current)highlight(q);
}

function closeAside(){document.getElementById('aside').classList.remove('open');}
document.getElementById('menuBtn').onclick=()=>document.getElementById('aside').classList.toggle('open');
document.getElementById('quickBtn').onclick=showConsulta;
document.getElementById('search').addEventListener('input',doSearch);

buildNav();showConsulta();
</script>
</body></html>
"""

OUT.write_text(SHELL.replace("__DATA__", DATA), encoding="utf-8")
print("Wrote", OUT, f"({OUT.stat().st_size:,} bytes)", "| pages:", len(pages), "| groups:", len(groups))

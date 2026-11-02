"""흉배 라벨링 매뉴얼: hyungbae/manual/src/*.md → HTML 페이지 (hanboklab.com/hyungbae/manual/)
사용: python3 scripts/make_manual.py   (저장소 맨 위 폴더에서 실행)
필요한 패키지: pip install markdown

src/index.md     → hyungbae/manual/index.html
src/<이름>.md    → hyungbae/manual/<이름>/index.html
사이트 공통 스타일은 ontology/index.html의 <style>을 가져다 쓴다.
"""
import os, re, html
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "hyungbae", "manual", "src")
OUT = os.path.join(ROOT, "hyungbae", "manual")

# 메뉴 순서: (원고 파일 이름, 메뉴 이름)
PAGES = [("index", "작업 매뉴얼"), ("reference", "판별 참고 도감")]

base_css = re.search(r"<style>(.*?)</style>",
                     open(os.path.join(ROOT, "ontology", "index.html"), encoding="utf-8").read(), re.S).group(1)
base_css = base_css.replace("url(../images/", "url(/images/")

CSS = base_css + """
/* 매뉴얼 */
.subnav{display:flex;gap:8px;flex-wrap:wrap;margin-top:28px}
.subnav a{border:1px solid var(--line);background:var(--bg2);padding:7px 16px;font-size:13.5px;color:var(--ink-2)}
.subnav a:hover{border-color:var(--gold);color:var(--ivory);text-decoration:none}
.subnav a[aria-current]{border-color:var(--gold);color:var(--ivory)}
.doc{max-width:900px;padding-bottom:20px}
.doc h2{padding-top:52px;margin-bottom:16px;scroll-margin-top:90px}
.doc p,.doc li{font-size:15px}
.doc ul,.doc ol{padding-left:1.3em} .doc li{margin:4px 0}
.doc strong{font-weight:500;color:var(--ivory)}
.doc table{margin:14px 0 18px}
.doc td em{color:var(--muted);font-style:normal;font-size:13px}
.doc th:first-child:nth-last-child(2),.doc th:last-child:nth-child(2){width:50%}
.doc td img{display:block;max-width:100%;max-height:340px;margin-bottom:6px}
.doc blockquote{margin:18px 0;padding:12px 18px;background:var(--bg2);border-left:3px solid var(--gold);color:var(--ink-2);font-size:14px}
.doc blockquote p{margin:0}
.doc code{background:#1d1a20;padding:1px 6px;border-radius:3px}
"""

HEAD = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>{title} · HanbokLab</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,500;0,600;1,400;1,600&family=Jost:wght@300;400;500&family=Noto+Serif+KR:wght@200;300;400;600&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="eaves" role="img" aria-label="붉은 단청 처마 무늬"></div>
<header><div class="in">
  <a class="mark" href="/">Hanbok<em>Lab</em></a>
  <nav class="site-nav" aria-label="사이트"><a href="/#about">About</a><a href="/#projects" aria-current="page">Projects</a><a href="/#data">Data</a><a href="/ontology/">Ontology</a></nav>
</div></header>
<main>
<div class="top">
  <div class="kicker"><span class="inlay"></span>{kicker}</div>
  <h1>{title}</h1>
  <p class="lead">{lead}</p>
  <dl class="meta"><dt>프로젝트</dt><dd>조선시대 흉배 연구의 디지털 전환</dd><dt>작성</dt><dd>이윤서</dd><dt>고친 날</dt><dd>{updated}</dd></dl>
  <nav class="subnav" aria-label="매뉴얼">{subnav}</nav>
</div>
<article class="doc">
{body}
</article>
</main>
"""

FOOT = """
<footer>
  <div class="in">
    <span>© 2026 이윤서 Yunseo Isabel Lee</span>
    <span><a href="mailto:lisabelys@gmail.com">lisabelys@gmail.com</a><span class="sep">·</span><a href="https://isabel.co.kr/">isabel.co.kr</a></span>
  </div>
  <div class="giant nacre" aria-hidden="true">HanbokLab</div>
  <div class="eaves bottom" aria-hidden="true"></div>
</footer>

<button class="to-top" type="button" aria-label="맨 위로">
  <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M7 12.5V2M2.5 6.5 7 2l4.5 4.5"/></svg>
</button>

<script>
  (function(){
    var btn=document.querySelector('.to-top');
    var reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
    function onScroll(){btn.classList.toggle('show',window.scrollY>600)}
    window.addEventListener('scroll',onScroll,{passive:true});
    onScroll();
    btn.addEventListener('click',function(){
      window.scrollTo({top:0,behavior:reduce.matches?'auto':'smooth'});
      document.querySelector('.mark').focus({preventScroll:true});
    });
  })();
</script>
</body>
</html>
"""


def read_page(name):
    text = open(os.path.join(SRC, name + ".md"), encoding="utf-8").read()
    meta = {}
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
        text = text[m.end():]
    body = markdown.markdown(text, extensions=["tables", "attr_list", "toc"])
    body = body.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
    return meta, body


def url(name):
    return "/hyungbae/manual/" if name == "index" else f"/hyungbae/manual/{name}/"


for name, label in PAGES:
    meta, body = read_page(name)
    subnav = "".join(
        f'<a href="{url(n)}"{" aria-current=page" if n == name else ""}>{html.escape(l)}</a>'
        for n, l in PAGES)
    page = HEAD.format(css=CSS, title=html.escape(meta["title"]), kicker=html.escape(meta.get("kicker", "")),
                       lead=html.escape(meta.get("lead", "")), updated=html.escape(meta.get("updated", "")),
                       subnav=subnav, body=body) + FOOT
    folder = OUT if name == "index" else os.path.join(OUT, name)
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, "index.html"), "w", encoding="utf-8").write(page)
    print("→", os.path.relpath(os.path.join(folder, "index.html"), ROOT))

"""프로젝트 페이지 만들기 (hanboklab.com/projects/)
사용: python3 scripts/make_projects.py   (저장소 맨 위 폴더에서 실행)
필요한 패키지: pip install markdown

1) /projects/ 목록: 첫 화면(index.html)의 프로젝트 칸을 그대로 가져와 따로 한 페이지로 만든다.
   카드 내용을 고치려면 첫 화면 index.html을 고친 뒤 이 스크립트를 다시 돌린다.
2) 흉배 라벨링 매뉴얼: hyungbae/manual/src/*.md → HTML
   manual.md    → /hyungbae/manual/
   reference.md → /hyungbae/manual/reference/
   원고의 images/파일 은 /hyungbae/manual/images/파일 로 바뀐다.
   흉배 프로젝트 소개(/hyungbae/index.html)는 이 스크립트가 만들지 않는다.
   사이트 공통 스타일은 ontology/index.html의 <style>을 가져다 쓴다.
"""
import os, re, html
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "hyungbae", "manual", "src")
IMG = "/hyungbae/manual/images/"

# 메뉴 순서: (원고 파일 이름, 메뉴 이름, 주소)
PAGES = [("manual", "작업 매뉴얼", "/hyungbae/manual/"),
         ("reference", "판별 참고 도감", "/hyungbae/manual/reference/")]
PROJECT = ("흉배 프로젝트 소개", "/hyungbae/")   # 메뉴 맨 앞에 붙는 링크

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
.doc td figure{display:inline-block;vertical-align:top;margin:0 10px 10px 0;max-width:100%}
.doc td figure img{margin:0}
.doc td figcaption{font-size:12.5px;color:var(--ink-2);margin-top:4px}
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
{robots}
<title>{title} · HanbokLab</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,500;0,600;1,400;1,600&family=Jost:wght@300;400;500&family=Noto+Serif+KR:wght@200;300;400;600&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="eaves" role="img" aria-label="붉은 단청 처마 무늬"></div>
<header><div class="in">
  <a class="mark" href="/">Hanbok<em>Lab</em></a>
  <nav class="site-nav" aria-label="사이트"><a href="/#about">About</a><a href="/projects/" aria-current="page">Projects</a><a href="/#data">Data</a><a href="/ontology/">Ontology</a></nav>
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
    body = body.replace('src="images/', f'src="{IMG}')
    # 표 칸 안의 이미지 + 뒤따르는 글 → 그림과 설명
    body = re.sub(r"(<img [^>]*>)([^<]*)",
                  lambda m: f"<figure>{m.group(1)}" + (f"<figcaption>{m.group(2).strip()}</figcaption>" if m.group(2).strip() else "") + "</figure>",
                  body)
    return meta, body


# ── 1) /projects/ 목록
home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
section = re.search(r'<section id="projects".*?</section>', home, re.S).group(0)
head_end = home.index("<main>")
foot_start = home.index("</main>")
plist = (home[:head_end] + "<main>\n  " + section + "\n\n" + home[foot_start:])
plist = re.sub(r"<title>.*?</title>", "<title>프로젝트 · HanbokLab</title>", plist, count=1)
plist = plist.replace('<link rel="canonical" href="https://hanboklab.com/">', '<link rel="canonical" href="https://hanboklab.com/projects/">')
plist = plist.replace('content="https://hanboklab.com/">', 'content="https://hanboklab.com/projects/">')
plist = plist.replace('src="images/', 'src="/images/').replace("url(images/", "url(/images/")
plist = plist.replace('href="#about"', 'href="/#about"').replace('href="#data"', 'href="/#data"')
plist = plist.replace('<a href="/projects/">Projects</a>', '<a href="/projects/" aria-current="page">Projects</a>')
os.makedirs(os.path.join(ROOT, "projects"), exist_ok=True)
open(os.path.join(ROOT, "projects", "index.html"), "w", encoding="utf-8").write(plist)
print("→ projects/index.html")


# ── 2) 흉배 라벨링 매뉴얼
for name, label, url in PAGES:
    meta, body = read_page(name)
    subnav = f'<a href="{PROJECT[1]}">← {PROJECT[0]}</a>' + "".join(
        f'<a href="{u}"{" aria-current=page" if n == name else ""}>{html.escape(l)}</a>'
        for n, l, u in PAGES)
    page = HEAD.format(robots='<meta name="robots" content="noindex">', css=CSS, title=html.escape(meta["title"]), kicker=html.escape(meta.get("kicker", "")),
                       lead=html.escape(meta.get("lead", "")), updated=html.escape(meta.get("updated", "")),
                       subnav=subnav, body=body) + FOOT
    folder = os.path.join(ROOT, url.strip("/"))
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, "index.html"), "w", encoding="utf-8").write(page)
    print("→", os.path.relpath(os.path.join(folder, "index.html"), ROOT))

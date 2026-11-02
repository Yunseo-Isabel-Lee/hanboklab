"""기술규칙.dctap.csv + 어휘설명.csv → 사람이 읽는 HTML 문서 (hanboklab.com/ontology/)
사용: python3 make_docs.py <CSV·TTL 폴더> <출력 폴더>
"""
import csv, sys, os, shutil, html

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
tap = list(csv.DictReader(open(os.path.join(src, "기술규칙.dctap.csv"), encoding="utf-8-sig")))
voc = list(csv.DictReader(open(os.path.join(src, "어휘설명.csv"), encoding="utf-8-sig")))
V = {r["termID"]: r for r in voc}
NS = {r["termID"].rstrip(":"): r["definition"] for r in voc if r["termType"] == "Namespace"}
e = lambda s: html.escape(s or "")

def anchor(term):
    return term.replace(":", "-")

def link(term):
    """용어를 문서 안 설명으로 연결"""
    if term in V and V[term]["termType"] != "Namespace":
        return f'<a href="#{anchor(term)}"><code>{e(term)}</code></a>'
    return f"<code>{e(term)}</code>"

SHAPE_INFO = {
    "crm:E22_Human-Made_Object": ("흉배 유물", "통합 기술 단위. 기관마다 다른 기록을 공통 칸으로 정리한 흉배 한 점.", "이윤서 그래프"),
    "crm:E31_Document": ("기관 레코드", "소장처나 통합 플랫폼이 작성한 유물 기록 한 건. 기관이 적은 값은 원문 그대로 둔다.", "기관 그래프"),
    "crm:E39_Actor": ("소장처", "유물을 소장하거나 기록을 작성·공개한 기관 또는 개인.", ""),
    "crm:E54_Dimension": ("치수", "세로 또는 가로 한 값.", ""),
    "skos:Concept": ("개념", "통제어휘의 항목 하나.", ""),
    "skos:ConceptScheme": ("개념체계", "개념을 묶는 통제어휘 하나.", ""),
}

# ── 기술규칙 표
shape_html = []
order = []
for r in tap:
    if r["shapeID"] not in order:
        order.append(r["shapeID"])
for sid in order:
    lab, desc, graph = SHAPE_INFO[sid]
    rows = [r for r in tap if r["shapeID"] == sid]
    tr = []
    for r in rows:
        kind = r["valueNodeType"].lower()
        val = r["valueShape"] or r["valueDataType"] or ("IRI" if kind == "iri" else "글자")
        val_html = link(val) if r["valueShape"] else f"<code>{e(val)}</code>"
        tr.append(
            f"<tr><td><b>{e(r['propertyLabel'])}</b><div class='pid'>{link(r['propertyID'])}</div></td>"
            f"<td class='c'>{'<span class=req>필수</span>' if r['mandatory'].upper()=='TRUE' else '선택'}</td>"
            f"<td class='c'>{'여러 개' if r['repeatable'].upper()=='TRUE' else '하나'}</td>"
            f"<td>{val_html}</td><td class='note'>{e(r['note'])}</td></tr>")
    g = f"<span class='graph'>{graph}</span>" if graph else ""
    shape_html.append(f"""
<div class="shape" id="shape-{anchor(sid)}">
  <div class="shape-h"><h3>{lab}</h3>{link(sid)}{g}</div>
  <p class="shape-d">{desc}</p>
  <div class="tw"><table>
    <thead><tr><th style="width:21%">칸</th><th class="c" style="width:7%">필수</th><th class="c" style="width:8%">개수</th><th style="width:18%">값</th><th>설명</th></tr></thead>
    <tbody>{''.join(tr)}</tbody>
  </table></div>
</div>""")

# ── 개념체계 카드
schemes = [r for r in voc if r["termType"] == "ConceptScheme"]
scheme_html = "".join(
    f"""<div class="scheme" id="{anchor(r['termID'])}"><div class="sc-h"><b>{e(r['label_ko'])}</b><span>{e(r['label_en'])}</span></div>
<code>{e(r['termID'])}</code><p>{e(r['definition'])}</p><p class="u">{e(r['usage'])}</p>{f"<p class='ex'>예: {e(r['example'])}</p>" if r['example'] else ''}</div>"""
    for r in schemes)

# ── 어휘 설명 (클래스, 속성)
def term_block(r):
    own = r["vocabulary"] == "한복 아카이브 자체"
    dom = ", ".join(link(x.strip()) for x in r["domain"].split(",") if x.strip())
    rng = link(r["range"]) if r["range"] else ""
    meta = ""
    if dom or rng:
        meta = f"<div class='dr'>{'<span>도메인</span>'+dom if dom else ''}{'<span>레인지</span>'+rng if rng else ''}</div>"
    full = NS[r["termID"].split(":")[0]] + r["termID"].split(":", 1)[1]
    return f"""<div class="term{' own' if own else ''}" id="{anchor(r['termID'])}">
<div class="t-h"><b>{e(r['label_ko'])}</b><code>{e(r['termID'])}</code>{'<span class="badge-own">자체 정의</span>' if own else f'<span class="src">{e(r["vocabulary"])}</span>'}</div>
<div class="uri">{e(full)}</div>
<p><span class="k">정의</span>{e(r['definition'])}</p>
{f"<p><span class='k'>쓰는 법</span>{e(r['usage'])}</p>" if r['usage'] else ''}
{meta}{f"<p class='ex'>예: {e(r['example'])}</p>" if r['example'] else ''}</div>"""

classes = "".join(term_block(r) for r in voc if r["termType"] == "Class")
props = "".join(term_block(r) for r in voc if r["termType"] == "Property")
ns_rows = "".join(
    f"<tr><td><code>{e(r['termID'])}</code></td><td><code>{e(r['definition'])}</code></td><td>{e(r['usage'] or r['label_ko'])}</td></tr>"
    for r in voc if r["termType"] == "Namespace")

n_req = sum(1 for r in tap if r["mandatory"].upper() == "TRUE")

page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>흉배 온톨로지 · 기술규칙과 어휘설명 · HanbokLab</title>
<meta name="description" content="HanbokLab 흉배 온톨로지 v0.1 — 흉배 실물 유물의 기술규칙(DCTAP·SHACL)과 어휘설명. CIDOC CRM과 SKOS 기반이며, 나중에 한복 온톨로지로 합칠 예정입니다.">
<link rel="canonical" href="{NS['hanbok']}">
<link rel="alternate" type="text/turtle" href="어휘설명.ttl">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,500;0,600;1,400;1,600&family=Jost:wght@300;400;500&family=Noto+Serif+KR:wght@200;300;400;600&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0b0a0c;--bg2:#121013;--ivory:#eee8db;--ink-2:#c9c1b3;--muted:#9a9286;--line:rgba(200,164,100,.24);--line-2:rgba(238,232,219,.1);--gold:#c8a464;--gold-2:#e6d3a8;--red:#c4452b;--rose:#e9c9c4;--abalone:url(../images/nacre-cloud.jpg);--pearl:url(../images/nacre-fur.jpg);--display:"Bodoni Moda","Noto Serif KR",serif;--serif:"Noto Serif KR",serif;--sans:"Noto Sans KR",system-ui,sans-serif;--mono:ui-monospace,Menlo,Consolas,monospace;--geo:"Jost","Noto Sans KR",sans-serif;--gutter:clamp(20px,5vw,64px)}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth;scroll-padding-top:90px}}
body{{margin:0;word-break:keep-all;background:var(--bg);color:var(--ivory);font-family:var(--sans);font-weight:300;line-height:1.75;font-size:15px;-webkit-font-smoothing:antialiased}}
a{{color:var(--gold-2);text-decoration:none}} a:hover{{color:#fff;text-decoration:underline}}
code{{font-family:var(--mono);font-size:12.5px;color:var(--ivory)}} a code{{color:inherit}}
/* 자개 질감 */
.nacre{{background-image:var(--abalone);background-size:300px auto;background-position:0 50%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:shimmer 18s linear infinite alternate}}
.inlay{{display:block;height:3px;background:var(--abalone) 0 50%/260% auto;animation:shimmer 12s ease-in-out infinite alternate}}
@keyframes shimmer{{to{{background-position:100% 50%}}}}
/* 처마 띠 */
.eaves{{height:clamp(72px,8.5vw,122px);background:#1c2554 url(../images/eaves-band.jpg) 0 0/auto 100% repeat-x;border-bottom:2px solid var(--red)}}
.eaves.bottom{{border-bottom:0;border-top:2px solid var(--red)}}
/* 머리 */
header{{position:sticky;top:0;z-index:30;border-bottom:1px solid var(--line);background:rgba(11,10,12,.86);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px)}}
header .in{{max-width:1200px;margin:0 auto;padding:0 var(--gutter);height:72px;display:flex;align-items:center;justify-content:space-between;gap:20px}}
.mark{{font-family:var(--geo);font-weight:500;font-size:20px;letter-spacing:.02em;color:var(--ivory)}} .mark em{{font-style:normal;font-weight:300;color:var(--gold)}} .mark:hover{{text-decoration:none;color:var(--ivory)}}
.site-nav{{display:flex;gap:44px;margin-right:-.28em;font-family:var(--geo);font-weight:400;font-size:12px;letter-spacing:.28em;text-transform:uppercase}}
.site-nav a{{color:var(--muted);padding-bottom:2px;border-bottom:1px solid transparent}} .site-nav a:hover{{color:var(--ivory);text-decoration:none}}
.site-nav a[aria-current]{{color:var(--ivory);border-bottom-color:var(--gold)}}
main{{max-width:1200px;margin:0 auto;padding:0 var(--gutter)}}
.scope{{max-width:720px;margin:0 0 28px;padding:16px 20px;background:var(--bg2);border:1px solid var(--line);font-size:14px;color:var(--ink-2)}}
.scope b{{font-weight:500;color:var(--ivory)}}
.toc{{display:flex;flex-wrap:wrap;gap:8px 28px;margin-top:28px;padding-top:18px;border-top:1px solid var(--line);font-size:14px}}
.toc a{{color:var(--ink-2)}} .toc a:hover{{color:var(--ivory)}}
.top{{padding:64px 0 40px;border-bottom:1px solid var(--line)}}
.kicker{{display:flex;align-items:center;gap:14px;font-family:var(--geo);font-size:12px;letter-spacing:.32em;color:var(--gold);text-transform:uppercase;margin-bottom:16px}}
.kicker .inlay{{width:40px}}
h1{{font-family:var(--serif);font-weight:200;font-size:clamp(30px,4vw,44px);letter-spacing:.06em;margin:0 0 22px;line-height:1.35}}
.lead{{color:var(--ink-2);max-width:720px;margin:0 0 24px}}
.meta{{display:grid;grid-template-columns:110px 1fr;gap:6px 16px;font-size:13.5px;max-width:720px}}
.meta dt{{color:var(--muted)}} .meta dd{{margin:0}}
.dl{{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}}
.dl a{{border:1px solid var(--line);background:var(--bg2);padding:7px 14px;font-size:13px;color:var(--ivory)}}
.dl a:hover{{border-color:var(--gold);text-decoration:none}}
.dl a b{{font-weight:500;color:var(--gold);margin-right:6px}}
section{{padding:56px 0 8px}}
h2{{font-family:var(--serif);font-weight:300;font-size:26px;letter-spacing:.04em;margin:0 0 6px}}
.sec-d{{color:var(--ink-2);margin:0 0 24px;max-width:760px}}
.stats{{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 26px}}
.stats div{{background:var(--bg2);border:1px solid var(--line);padding:10px 18px;font-size:13px;color:var(--muted)}}
.stats b{{display:block;font-family:var(--display);font-style:italic;font-weight:600;font-size:30px;line-height:1.15;background-image:var(--abalone);background-size:300px auto;-webkit-background-clip:text;background-clip:text;color:transparent}}
/* 모델 그림 */
.diagram{{background:var(--bg2);border:1px solid var(--line);padding:18px;overflow-x:auto}}
.diagram svg{{display:block;min-width:860px;width:100%;height:auto}}
.legend{{display:flex;gap:18px;flex-wrap:wrap;font-size:12.5px;color:var(--ink-2);margin-top:12px}}
.legend i{{display:inline-block;width:12px;height:12px;vertical-align:-1px;margin-right:6px;border:1px solid}}
/* 표 */
.tw{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;background:var(--bg2);border:1px solid var(--line);font-size:13.5px}}
th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line-2);vertical-align:top}}
th{{font-weight:500;font-size:12px;letter-spacing:.04em;color:var(--gold);background:#17141a}}
td.c,th.c{{text-align:center}} td.note{{color:var(--ink-2);font-size:13px}}
.pid{{margin-top:2px}} .pid code{{font-size:11.5px;color:var(--muted)}} .pid a code{{color:var(--gold-2)}}
.req{{background:var(--rose);color:#5a2b24;font-size:11.5px;padding:1px 8px;border-radius:999px;white-space:nowrap}}
.shape{{margin:0 0 36px}}
.shape-h{{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}}
.shape-h h3{{font-family:var(--serif);font-weight:400;font-size:19px;margin:0}}
.graph{{font-size:11.5px;border:1px solid var(--gold);color:var(--gold-2);padding:0 8px;border-radius:999px}}
.shape-d{{color:var(--ink-2);margin:4px 0 12px;font-size:14px}}
/* 개념체계 */
.schemes{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
.scheme{{background:var(--bg2);border:1px solid var(--line);padding:16px 18px;scroll-margin-top:90px}}
.sc-h{{display:flex;justify-content:space-between;align-items:baseline;gap:10px}}
.sc-h b{{font-family:var(--serif);font-weight:400;font-size:17px}} .sc-h span{{font-size:12px;color:var(--muted)}}
.scheme code{{font-size:11.5px;color:var(--muted)}}
.scheme p{{margin:8px 0 0;font-size:13.5px}} .scheme p.u{{color:var(--ink-2)}}
.ex{{font-size:12.5px;color:var(--muted)}}
/* 용어 */
.terms{{display:grid;gap:12px}}
.term{{position:relative;background:var(--bg2);border:1px solid var(--line);padding:16px 20px;scroll-margin-top:90px}}
.term.own{{padding-left:24px}}
.term.own::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--abalone) center/cover}}
.term:target{{outline:2px solid var(--gold)}}
.t-h{{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}}
.t-h b{{font-family:var(--serif);font-weight:400;font-size:17px}}
.src{{font-size:11.5px;color:var(--muted);margin-left:auto}}
.badge-own{{font-size:11.5px;font-weight:500;background:var(--pearl) center/cover;color:#1a1712;padding:1px 9px;border-radius:999px;margin-left:auto}}
.uri{{font-family:var(--mono);font-size:11.5px;color:var(--muted);margin:2px 0 6px;word-break:break-all}}
.term p{{margin:6px 0 0;font-size:14px}}
.k{{display:inline-block;width:62px;color:var(--muted);font-size:12.5px}}
.dr{{display:flex;gap:6px 16px;flex-wrap:wrap;margin-top:8px;font-size:13px}}
.dr span{{color:var(--muted);font-size:12px;margin-right:6px}}
h3.sub{{font-family:var(--serif);font-weight:400;font-size:18px;margin:30px 0 12px}}
/* 꼬리 */
footer{{overflow:hidden;margin-top:80px;border-top:1px solid var(--line)}}
footer .in{{max-width:1200px;margin:0 auto;padding:20px var(--gutter) 24px;display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:2px 24px;font-size:13px;color:var(--muted)}}
footer a{{color:#d9c79f}} footer a:hover{{color:#fff;text-decoration:none}}
footer .sep{{margin:0 10px}}
.giant{{margin:0 0 -.08em;font-family:var(--display);font-weight:600;font-size:clamp(72px,17vw,250px);line-height:.82;text-align:center;white-space:nowrap;user-select:none;pointer-events:none}}
/* 맨 위로 */
.to-top{{position:fixed;right:clamp(16px,3vw,36px);bottom:clamp(16px,3vw,36px);z-index:30;width:46px;height:46px;padding:0;display:grid;place-items:center;border-radius:50%;background:rgba(11,10,12,.8);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);border:1px solid var(--gold);color:var(--gold-2);cursor:pointer;overflow:hidden;opacity:0;visibility:hidden;transform:translateY(10px);transition:opacity .35s,transform .35s,visibility .35s,color .25s}}
.to-top::before{{content:"";position:absolute;inset:0;background:var(--pearl) center/cover;opacity:0;transition:opacity .3s}}
.to-top svg{{position:relative;width:14px;height:14px}}
.to-top.show{{opacity:1;visibility:visible;transform:none}}
.to-top:hover{{color:#1a1712}}
.to-top:hover::before{{opacity:1}}
.to-top:focus-visible{{outline:2px solid var(--gold-2);outline-offset:3px}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}} .nacre,.inlay{{animation:none}} .to-top{{transition:none}}}}
@media (max-width:960px){{.site-nav{{gap:24px;letter-spacing:.2em;margin-right:-.2em}}}}
@media (max-width:720px){{
  html{{scroll-padding-top:110px}}
  header .in{{height:auto;flex-wrap:wrap;gap:0;padding-top:12px;padding-bottom:10px}}
  .mark{{font-size:17px}}
  .site-nav{{width:100%;justify-content:space-between;gap:0;margin:8px -.14em 0 0;font-size:10.5px;letter-spacing:.14em}}
  .meta{{grid-template-columns:90px 1fr}}
}}
</style>
</head>
<body>
<div class="eaves" role="img" aria-label="붉은 단청 처마 무늬"></div>
<header><div class="in">
  <a class="mark" href="/">Hanbok<em>Lab</em></a>
  <nav class="site-nav" aria-label="사이트"><a href="/#about">About</a><a href="/#projects">Projects</a><a href="/#data">Data</a><a href="/ontology/" aria-current="page">Ontology</a></nav>
</div></header>
<main>
<div class="top">
  <div class="kicker"><i class="inlay"></i>Rank Badge Ontology · v0.1</div>
  <h1>흉배 온톨로지<br>기술규칙과 어휘설명</h1>
  <p class="scope">한복 온톨로지는 복식별 온톨로지를 모아 만들어 갑니다. 이 문서는 그중 <b>흉배</b>를 다루는 온톨로지이며, 다른 복식의 온톨로지와 함께 나중에 하나의 한복 온톨로지로 합칠 예정입니다.</p>
  <p class="lead">흉배 유물 데이터를 어떤 칸으로 기술하고 각 칸에 무엇을 적는지 정한 기술규칙과, 그 칸에 쓰는 클래스·속성·개념체계의 설명입니다. CIDOC CRM과 SKOS를 바탕으로 하며, 기관이 적은 기록은 원문 그대로 두고 이 아카이브가 정리한 값은 따로 기술합니다.</p>
  <dl class="meta">
    <dt>소속</dt><dd>한복 온톨로지 (통합 예정)</dd>
    <dt>네임스페이스</dt><dd><code>{e(NS['hanbok'])}</code></dd>
    <dt>작성</dt><dd>이윤서 Yunseo Isabel Lee</dd>
    <dt>버전</dt><dd>0.1 · 2026-11-03</dd>
    <dt>기반</dt><dd>CIDOC CRM 7.1.3 · SKOS · DCMI Terms</dd>
    <dt>범위</dt><dd>단독 흉배 실물 유물. 단령·초상화 속 흉배와 법전 규정은 다음 단계</dd>
    <dt>라이선스</dt><dd><a href="https://creativecommons.org/licenses/by/4.0/deed.ko">CC BY 4.0</a></dd>
  </dl>
  <div class="dl">
    <a href="기술규칙.dctap.csv"><b>CSV</b>기술규칙 (DCTAP)</a>
    <a href="기술규칙.ttl"><b>TTL</b>기술규칙 (SHACL)</a>
    <a href="어휘설명.csv"><b>CSV</b>어휘설명</a>
    <a href="어휘설명.ttl"><b>TTL</b>어휘설명</a>
  </div>
  <nav class="toc" aria-label="이 문서의 차례"><a href="#model">모델</a><a href="#ns">네임스페이스</a><a href="#rules">기술규칙</a><a href="#schemes">개념체계</a><a href="#vocab">어휘</a></nav>
</div>

<section id="model">
  <h2>모델 한눈에 보기</h2>
  <p class="sec-d">기관 레코드는 기관이 적은 그대로 두고(기관 그래프), 흉배 유물에는 공통 칸으로 정리한 값을 둡니다(이윤서 그래프). 문양·시기·국적 같은 값은 글자가 아니라 통제어휘의 개념에 연결합니다.</p>
  <div class="stats">
    <div><b>{len(order)}</b>기술 대상</div>
    <div><b>{len(tap)}</b>칸</div>
    <div><b>{n_req}</b>필수 칸</div>
    <div><b>{len(schemes)}</b>개념체계</div>
  </div>
  <div class="diagram">
  <svg viewBox="0 0 960 430" role="img" aria-label="모델 구조도: 기관 레코드가 흉배 유물을 기록하고, 흉배 유물은 소장처·치수·개념에 연결된다">
    <defs>
      <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#b3ab9e"/></marker>
    </defs>
    <style>
      .bx{{fill:#1a171d;stroke:#eee8db;stroke-width:1.2}} .bx.inst{{fill:#221c14;stroke:#c8a464}} .bx.con{{fill:#16181d;stroke:#8e9bb0}}
      .t1{{font:500 15px "Noto Sans KR",sans-serif;fill:#eee8db}} .t2{{font:11.5px ui-monospace,Menlo,monospace;fill:#9a9286}}
      .ln{{stroke:#b3ab9e;stroke-width:1.2;fill:none;marker-end:url(#ar)}} .lb{{font:11.5px ui-monospace,Menlo,monospace;fill:#c9c1b3}}
      .zone{{font:12px "Noto Sans KR",sans-serif;fill:#c8a464}}
    </style>
    <text class="zone" x="20" y="24">기관 그래프 (원문)</text>
    <text class="zone" x="300" y="24">이윤서 그래프 (통합)</text>
    <line x1="270" y1="12" x2="270" y2="420" stroke="rgba(200,164,100,.3)" stroke-dasharray="4 4"/>
    <!-- 기관 레코드 -->
    <rect class="bx inst" x="20" y="150" width="210" height="64" rx="4"/>
    <text class="t1" x="36" y="176">기관 레코드</text><text class="t2" x="36" y="198">crm:E31_Document</text>
    <!-- 흉배 유물 -->
    <rect class="bx" x="330" y="150" width="220" height="64" rx="4" stroke-width="2"/>
    <text class="t1" x="346" y="176">흉배 유물</text><text class="t2" x="346" y="198">crm:E22_Human-Made_Object</text>
    <!-- 소장처 -->
    <rect class="bx" x="330" y="330" width="220" height="64" rx="4"/>
    <text class="t1" x="346" y="356">소장처 (기관·개인)</text><text class="t2" x="346" y="378">crm:E39_Actor</text>
    <!-- 치수 -->
    <rect class="bx" x="330" y="40" width="220" height="64" rx="4"/>
    <text class="t1" x="346" y="66">치수 (세로·가로)</text><text class="t2" x="346" y="88">crm:E54_Dimension</text>
    <!-- 개념 -->
    <rect class="bx con" x="730" y="150" width="220" height="64" rx="4"/>
    <text class="t1" x="746" y="176">개념</text><text class="t2" x="746" y="198">skos:Concept</text>
    <rect class="bx con" x="730" y="330" width="220" height="64" rx="4"/>
    <text class="t1" x="746" y="356">개념체계 (8개)</text><text class="t2" x="746" y="378">skos:ConceptScheme</text>
    <!-- 선 -->
    <path class="ln" d="M230 182 L328 182"/><text class="lb" x="240" y="174">P70</text>
    <path class="ln" d="M125 214 L125 362 L328 362"/><text class="lb" x="135" y="352">dcterms:publisher</text>
    <path class="ln" d="M440 214 L440 328"/><text class="lb" x="448" y="276">P50 소장처</text>
    <path class="ln" d="M440 150 L440 106"/><text class="lb" x="448" y="132">P43 치수</text>
    <path class="ln" d="M550 182 L728 182"/>
    <text class="lb" x="556" y="140">P2 자료 구분·문양</text>
    <text class="lb" x="556" y="154">dcterms:temporal 시기</text>
    <text class="lb" x="556" y="168">dcterms:spatial 국적</text>
    <text class="lb" x="556" y="234">P45 재질 · P101 착용 맥락</text>
    <text class="lb" x="556" y="248">dcterms:license 이용조건</text>
    <path class="ln" d="M550 72 L835 72 L835 148"/><text class="lb" x="580" y="64">P2 측정 종류 · P91 단위</text>
    <path class="ln" d="M835 214 L835 328"/><text class="lb" x="843" y="276">skos:inScheme</text>
    <path d="M940 170 C 956 170, 956 196, 940 196" stroke="#8e9bb0" fill="none" stroke-width="1.2" marker-end="url(#ar)"/>
    <text class="lb" x="843" y="236">broader · related</text>
  </svg>
  </div>
  <div class="legend"><span><i style="background:#221c14;border-color:#c8a464"></i>기관이 적은 기록</span><span><i style="background:#1a171d;border-color:#eee8db"></i>통합 기술</span><span><i style="background:#16181d;border-color:#8e9bb0"></i>통제어휘</span></div>
</section>

<section id="ns">
  <h2>네임스페이스</h2>
  <p class="sec-d">이 문서와 데이터에서 쓰는 접두어입니다.</p>
  <div class="tw"><table><thead><tr><th style="width:12%">접두어</th><th style="width:45%">주소</th><th>내용</th></tr></thead><tbody>{ns_rows}</tbody></table></div>
</section>

<section id="rules">
  <h2>기술규칙</h2>
  <p class="sec-d">기술 대상마다 어떤 칸을 쓰고, 필수인지, 몇 개까지 쓸 수 있는지, 값은 무엇인지 정합니다. 칸 이름 아래의 용어를 누르면 어휘 설명으로 갑니다.</p>
  {''.join(shape_html)}
</section>

<section id="schemes">
  <h2>개념체계</h2>
  <p class="sec-d">값을 글자로 적지 않고 고르는 통제어휘입니다. 이번 버전은 체계의 이름과 범위만 정했고, 체계 안의 개념(쌍학, 19세기 등)은 다음 단계에서 채웁니다.</p>
  <div class="schemes">{scheme_html}</div>
</section>

<section id="vocab">
  <h2>어휘 설명</h2>
  <p class="sec-d">기술규칙에 나오는 클래스와 속성입니다. 외부 표준 용어는 정의를 다시 하지 않고 이 아카이브에서의 이름과 쓰는 법만 붙였으며, <b style="font-weight:500;color:#e6d3a8">자체 정의</b> 표시가 있는 용어는 이 아카이브가 정의합니다.</p>
  <h3 class="sub">클래스</h3><div class="terms">{classes}</div>
  <h3 class="sub">속성</h3><div class="terms">{props}</div>
</section>
</main>
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
  (function(){{
    var btn=document.querySelector('.to-top');
    var reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
    function onScroll(){{btn.classList.toggle('show',window.scrollY>600)}}
    window.addEventListener('scroll',onScroll,{{passive:true}});
    onScroll();
    btn.addEventListener('click',function(){{
      window.scrollTo({{top:0,behavior:reduce.matches?'auto':'smooth'}});
      document.querySelector('.mark').focus({{preventScroll:true}});
    }});
  }})();
</script>
</body>
</html>"""
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)

# 데이터 파일 복사
for f in ["기술규칙.dctap.csv", "기술규칙.ttl", "어휘설명.csv", "어휘설명.ttl"]:
    shutil.copy(os.path.join(src, f), out)

# 자체 속성 주소(https://hanboklab.com/ontology/beginYear)가 열리도록 이동 페이지
for r in voc:
    if r["termType"] == "Property" and r["vocabulary"] == "한복 아카이브 자체":
        local = r["termID"].split(":", 1)[1]
        dd = os.path.join(out, local); os.makedirs(dd, exist_ok=True)
        target = f"../#{anchor(r['termID'])}"
        open(os.path.join(dd, "index.html"), "w", encoding="utf-8").write(
            f'<!doctype html><meta charset="utf-8"><title>{e(r["label_ko"])}</title>'
            f'<meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{NS["hanbok"]}{local}">'
            f'<p><a href="{target}">{e(r["label_ko"])} ({e(r["termID"])})</a></p>')
print("ok:", out)

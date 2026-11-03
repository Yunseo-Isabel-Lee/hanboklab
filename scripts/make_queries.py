"""질문–SPARQL 예시 (그라운딩 ④). 샘플데이터+개념에 실제로 돌려 결과를 함께 적는다.
사용: python3 make_queries.py <grounding 폴더> <어휘설명.csv 폴더>
"""
import csv, sys, os
from rdflib import Graph

g_dir, voc_dir = sys.argv[1], sys.argv[2]
P = """PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX hanbokc: <https://hanboklab.com/concept/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""
Q = [
 ("상업적으로 쓸 수 있는 쌍학 흉배 보여줘",
  "S4 · 질문 속 단어를 이칭(altLabel)으로 찾고, 이용조건은 상위 개념 「상업 이용 가능」으로 묶는다",
  """SELECT ?item ?title WHERE {
  ?motif skos:prefLabel|skos:altLabel ?w . FILTER(STR(?w) = "쌍학")
  ?ok skos:prefLabel "상업 이용 가능"@ko .
  ?item crm:P2_has_type ?motif ;
        dcterms:license/skos:broader ?ok ;
        dcterms:title ?title . FILTER(LANG(?title) = "ko")
}"""),
 ("쌍학문 흉배 다 보여줘",
  "이칭으로 찾기 · '쌍학문'은 「쌍학」의 altLabel",
  """SELECT ?item ?title WHERE {
  ?motif skos:altLabel "쌍학문"@ko .
  ?item crm:P2_has_type ?motif ; dcterms:title ?title . FILTER(LANG(?title) = "ko")
}"""),
 ("학 흉배를 전부 보여줘",
  "상위 문양으로 찾기 · 학 아래의 쌍학·단학·운학·백학까지 skos:broader* 로 함께",
  """SELECT ?item ?title ?motifLabel WHERE {
  hanbokc:hak ^skos:broader* ?motif .
  ?item crm:P2_has_type ?motif ; dcterms:title ?title . FILTER(LANG(?title) = "ko")
  ?motif skos:prefLabel ?motifLabel . FILTER(LANG(?motifLabel) = "ko")
}"""),
 ("국립중앙박물관의 호랑이 흉배",
  "소장처 + 상위 문양",
  """SELECT ?item ?title WHERE {
  ?keeper rdfs:label "국립중앙박물관"@ko .
  hanbokc:horangi ^skos:broader* ?motif .
  ?item crm:P50_has_current_keeper ?keeper ; crm:P2_has_type ?motif ;
        dcterms:title ?title . FILTER(LANG(?title) = "ko")
}"""),
 ("19세기 흉배",
  "시기 개념 계층 · 19세기 전반·후반에 연결된 유물도 함께",
  """SELECT ?item ?title ?periodLabel WHERE {
  hanbokc:c19 ^skos:broader* ?p .
  ?item dcterms:temporal ?p ; dcterms:title ?title . FILTER(LANG(?title) = "ko")
  ?p skos:prefLabel ?periodLabel . FILTER(LANG(?periodLabel) = "ko")
}"""),
 ("조선 말기 흉배",
  "관련 개념까지 넓혀 찾기 · 「조선 말기」에 직접 연결된 유물 + skos:related 로 이어진 세기(19·20세기)에 연결된 유물. 결과에 '관련으로 찾음' 표시가 필요",
  """SELECT ?item ?title ?how WHERE {
  { ?item dcterms:temporal hanbokc:joseonEnd . BIND("직접" AS ?how) }
  UNION
  { hanbokc:joseonEnd skos:related ?c . ?c ^skos:broader* ?p .
    ?item dcterms:temporal ?p . BIND("관련으로 찾음" AS ?how) }
  ?item dcterms:title ?title . FILTER(LANG(?title) = "ko")
}"""),
 ("1734년 이전의 한국 흉배",
  "S1 · 기관이 연도를 적은 유물은 dcterms:date(EDTF)의 끝 연도로, 아니면 1734년 이전임이 확실한 세기(15~17세기)로 찾는다. 18세기 전반처럼 1734년에 걸치는 구간은 넣지 않는다",
  """SELECT DISTINCT ?item ?title WHERE {
  ?item dcterms:spatial hanbokc:korea ; dcterms:title ?title . FILTER(LANG(?title) = "ko")
  { ?item dcterms:date ?d .
    BIND(xsd:integer(IF(CONTAINS(STR(?d), "/"), STRAFTER(STR(?d), "/"), STR(?d))) AS ?end)
    FILTER(?end < 1734) }
  UNION
  { VALUES ?c { hanbokc:c15 hanbokc:c16 hanbokc:c17 }
    ?c ^skos:broader* ?p . ?item dcterms:temporal ?p .
    FILTER NOT EXISTS { ?item dcterms:date ?d2 } }
}"""),
 ("가로가 20cm 넘는 한국 흉배",
  "치수 노드 · 측정 종류 「가로」의 값",
  """SELECT ?item ?title ?w WHERE {
  ?item dcterms:spatial hanbokc:korea ; dcterms:title ?title . FILTER(LANG(?title) = "ko")
  ?item crm:P43_has_dimension ?d .
  ?d crm:P2_has_type hanbokc:width ; crm:P90_has_value ?w .
  FILTER(?w > 20)
} ORDER BY DESC(?w)"""),
 ("관복에 달았던 것으로 확인된 흉배",
  "착용 맥락",
  """SELECT ?item ?title WHERE {
  ?item crm:P101_had_as_general_use hanbokc:gwanbok ;
        dcterms:title ?title . FILTER(LANG(?title) = "ko")
}"""),
 ("소장처별로 한국 흉배가 몇 점씩 있어?",
  "집계 · 중국 흉배는 국적으로 뺀다",
  """SELECT ?keeperName (COUNT(?item) AS ?n) WHERE {
  ?item crm:P2_has_type hanbokc:hyungbae ; dcterms:spatial hanbokc:korea ;
        crm:P50_has_current_keeper ?k .
  ?k rdfs:label ?keeperName . FILTER(LANG(?keeperName) = "ko")
} GROUP BY ?keeperName ORDER BY DESC(?n)"""),
]

data = Graph()
data.parse(os.path.join(g_dir, "샘플데이터.ttl")); data.parse(os.path.join(g_dir, "개념.ttl"))
rows, report = [], []
for i, (q, note, body) in enumerate(Q, 1):
    res = list(data.query(P + body))
    vals = []
    for row in res:
        vals.append(" · ".join(str(x).replace("https://hanboklab.com/object/", "hanboko:") for x in row))
    rows.append([f"Q{i:02d}", q, note, body, len(res), " / ".join(vals)])
    report.append(f"Q{i:02d} {q} → {len(res)}건\n   " + "\n   ".join(vals))
with open(os.path.join(g_dir, "질문예시.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["id", "질문", "설명", "SPARQL (PREFIX 생략)", "샘플 결과 건수", "샘플 결과"]); w.writerows(rows)
# 쿼리 파일도 따로 (복사해 바로 돌릴 수 있게)
with open(os.path.join(g_dir, "질문예시.rq"), "w", encoding="utf-8") as f:
    for i, (q, note, body) in enumerate(Q, 1):
        f.write(f"# Q{i:02d} {q}\n# {note}\n{P}{body}\n\n")
print("\n".join(report))

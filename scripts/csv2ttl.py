"""기술규칙.dctap.csv → 기술규칙.ttl (SHACL), 어휘설명.csv → 어휘설명.ttl
사용: python3 csv2ttl.py <작업폴더>
CSV를 고친 뒤 다시 돌리면 TTL이 새로 만들어진다.
"""
import csv, sys, os
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD, OWL, SKOS, DCTERMS, FOAF
from rdflib.collection import Collection

d = sys.argv[1]
SH = Namespace("http://www.w3.org/ns/shacl#")
VANN = Namespace("http://purl.org/vocab/vann/")

# ── 네임스페이스는 어휘설명.csv의 Namespace 행에서 읽는다
voc = list(csv.DictReader(open(os.path.join(d, "어휘설명.csv"), encoding="utf-8-sig")))
NS = {r["termID"].rstrip(":"): r["definition"] for r in voc if r["termType"] == "Namespace"}
NS["rdf"] = str(RDF)
NS["sh"] = str(SH)
NS["vann"] = str(VANN)
HB = Namespace(NS["hanbok"]); HBC = Namespace(NS["hanbokc"])
ONT = URIRef(NS["hanbok"])

def q(curie):
    p, l = curie.split(":", 1)
    return URIRef(NS[p] + l)

def bind(g):
    for p, u in NS.items():
        g.bind(p, Namespace(u))

def header(g, title, desc):
    g.add((ONT, RDF.type, OWL.Ontology))
    g.add((ONT, DCTERMS.title, Literal(title, lang="ko")))
    g.add((ONT, DCTERMS.description, Literal(desc, lang="ko")))
    g.add((ONT, DCTERMS.creator, Literal("이윤서", lang="ko")))
    g.add((ONT, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))
    g.add((ONT, OWL.versionInfo, Literal("0.1")))
    g.add((ONT, DCTERMS.modified, Literal("2026-11-03", datatype=XSD.date)))
    g.add((ONT, VANN.preferredNamespacePrefix, Literal("hanbok")))
    g.add((ONT, VANN.preferredNamespaceUri, Literal(NS["hanbok"])))

# ═════ 1. 기술규칙 → SHACL ═════
SHAPE_NAME = {
    "crm:E22_Human-Made_Object": "HyungbaeShape",
    "crm:E31_Document": "RecordShape",
    "crm:E39_Actor": "ActorShape",
    "crm:E54_Dimension": "DimensionShape",
    "skos:Concept": "ConceptShape",
    "skos:ConceptScheme": "ConceptSchemeShape",
}
# 같은 속성(P2)이 개념체계에 따라 나뉘는 행: propertyLabel → 개념체계
QUALIFIED = {"자료 구분": "hanbokc:objectType", "문양": "hanbokc:motif", "측정 종류": "hanbokc:measurement"}

tap = list(csv.DictReader(open(os.path.join(d, "기술규칙.dctap.csv"), encoding="utf-8-sig")))
g = Graph(); bind(g)
header(g, "한복 아카이브 기술규칙", "흉배 아카이브 데이터의 기술규칙(SHACL). 기술규칙.dctap.csv에서 변환.")
shapes = {}
for r in tap:
    sid = r["shapeID"]
    if sid not in shapes:
        s = HB[SHAPE_NAME[sid]]
        shapes[sid] = s
        g.add((s, RDF.type, SH.NodeShape))
        g.add((s, SH.targetClass, q(sid)))
        g.add((s, RDFS.label, Literal(r["shapeLabel"], lang="ko")))
        g.add((s, RDFS.isDefinedBy, ONT))
    s = shapes[sid]
    p = BNode()
    g.add((s, SH.property, p))
    g.add((p, SH.path, q(r["propertyID"])))
    g.add((p, SH.name, Literal(r["propertyLabel"], lang="ko")))
    if r["note"]:
        g.add((p, SH.description, Literal(r["note"], lang="ko")))
    mand = r["mandatory"].upper() == "TRUE"
    rep = r["repeatable"].upper() == "TRUE"
    lab = r["propertyLabel"]
    if sid == "crm:E22_Human-Made_Object" and lab in QUALIFIED or (sid == "crm:E54_Dimension" and lab in QUALIFIED):
        # 같은 경로(P2)를 개념체계별로 나눠 센다
        vs = BNode()
        g.add((p, SH.qualifiedValueShape, vs))
        inner = BNode()
        g.add((vs, SH.property, inner))
        g.add((inner, SH.path, SKOS.inScheme))
        g.add((inner, SH.hasValue, q(QUALIFIED[lab])))
        if mand: g.add((p, SH.qualifiedMinCount, Literal(1)))
        if not rep: g.add((p, SH.qualifiedMaxCount, Literal(1)))
    else:
        if mand: g.add((p, SH.minCount, Literal(1)))
        if not rep: g.add((p, SH.maxCount, Literal(1)))
    kind = r["valueNodeType"].lower()
    if kind == "literal":
        g.add((p, SH.nodeKind, SH.Literal))
    elif kind == "iri":
        g.add((p, SH.nodeKind, SH.IRI))
    if r["valueDataType"]:
        g.add((p, SH.datatype, q(r["valueDataType"])))
    if r["valueShape"]:
        g.add((p, SH["class"], q(r["valueShape"])))
    if r["propertyID"] == "skos:prefLabel":
        g.add((p, SH.uniqueLang, Literal(True)))
g.serialize(os.path.join(d, "기술규칙.ttl"), format="turtle")
print("기술규칙.ttl:", len(g), "triples")

# ═════ 2. 어휘설명 → RDF ═════
v = Graph(); bind(v)
header(v, "한복 아카이브 어휘설명", "흉배 아카이브가 쓰는 클래스·속성·개념체계의 설명. 어휘설명.csv에서 변환.")
VOCAB_NS = {"RDF": "rdf", "CIDOC CRM 7.1.3": "crm", "DCMI Metadata Terms": "dcterms", "SKOS": "skos",
            "FOAF": "foaf", "RDF Schema": "rdfs", "OWL": "owl"}
for r in voc:
    t = r["termType"]
    if t == "Namespace":
        continue
    s = q(r["termID"])
    own = r["vocabulary"] == "한복 아카이브 자체"
    if t == "ConceptScheme":
        v.add((s, RDF.type, SKOS.ConceptScheme))
        v.add((s, SKOS.prefLabel, Literal(r["label_ko"], lang="ko")))
        v.add((s, SKOS.prefLabel, Literal(r["label_en"], lang="en")))
        v.add((s, SKOS.definition, Literal(r["definition"], lang="ko")))
        if r["usage"]: v.add((s, SKOS.scopeNote, Literal(r["usage"], lang="ko")))
        if r["example"]: v.add((s, SKOS.example, Literal(r["example"], lang="ko")))
        v.add((s, RDFS.isDefinedBy, ONT))
        continue
    if own:
        # 자체 용어는 정의까지 이 파일이 책임진다
        v.add((s, RDF.type, RDF.Property))
        if r["range"].startswith("xsd:"): v.add((s, RDF.type, OWL.DatatypeProperty))
        v.add((s, RDFS.label, Literal(r["label_ko"], lang="ko")))
        v.add((s, RDFS.label, Literal(r["label_en"], lang="en")))
        v.add((s, RDFS.comment, Literal(r["definition"], lang="ko")))
        v.add((s, RDFS.isDefinedBy, ONT))
        for dm in [x.strip() for x in r["domain"].split(",") if x.strip()]:
            v.add((s, RDFS.domain, q(dm)))
        if r["range"] and ":" in r["range"]:
            v.add((s, RDFS.range, q(r["range"])))
    else:
        # 외부 용어는 정의를 다시 하지 않고, 이 아카이브에서의 이름·쓰임만 단다
        v.add((s, RDFS.label, Literal(r["label_ko"], lang="ko")))
        v.add((s, SKOS.definition, Literal(r["definition"], lang="ko")))
        v.add((s, RDFS.isDefinedBy, URIRef(NS[VOCAB_NS[r["vocabulary"]]])))
    if r["usage"]: v.add((s, SKOS.scopeNote, Literal(r["usage"], lang="ko")))
    if r["example"]: v.add((s, SKOS.example, Literal(r["example"], lang="ko")))
v.serialize(os.path.join(d, "어휘설명.ttl"), format="turtle")
print("어휘설명.ttl:", len(v), "triples")

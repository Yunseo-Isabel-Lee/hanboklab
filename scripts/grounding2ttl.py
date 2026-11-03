"""개념.csv → 개념.ttl, 샘플데이터.csv → 샘플데이터.ttl
사용: python3 grounding2ttl.py <grounding 폴더> <어휘설명.csv 있는 폴더>
"""
import csv, sys, os, re
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, SKOS, DCTERMS, FOAF

g_dir, voc_dir = sys.argv[1], sys.argv[2]
DATA = sys.argv[3] if len(sys.argv) > 3 else "샘플데이터"
CONCEPTS = sys.argv[4] if len(sys.argv) > 4 else g_dir
voc = list(csv.DictReader(open(os.path.join(voc_dir, "어휘설명.csv"), encoding="utf-8-sig")))
NS = {r["termID"].rstrip(":"): r["definition"] for r in voc if r["termType"] == "Namespace"}
CRM = Namespace(NS["crm"]); HB = Namespace(NS["hanbok"]); HBC = Namespace(NS["hanbokc"]); HBO = Namespace(NS["hanboko"])
split = lambda s: [x.strip() for x in s.split(";") if x.strip()]

def bind(g):
    for p in ["crm", "hanbok", "hanbokc", "hanboko", "dcterms", "skos", "foaf", "rdfs", "xsd"]:
        g.bind(p, Namespace(NS[p]))

# ═ 개념
con = list(csv.DictReader(open(os.path.join(CONCEPTS, "개념.csv"), encoding="utf-8-sig")))
g = Graph(); bind(g)
for r in con:
    s = HBC[r["conceptID"]]; sch = HBC[r["scheme"]]
    g.add((s, RDF.type, SKOS.Concept)); g.add((s, RDF.type, CRM.E55_Type))
    if r["scheme"] == "measurement" and r["conceptID"] == "cm":
        g.add((s, RDF.type, CRM.E58_Measurement_Unit))
    g.add((s, SKOS.inScheme, sch))
    g.add((s, SKOS.prefLabel, Literal(r["prefLabel_ko"], lang="ko")))
    if r["prefLabel_en"]: g.add((s, SKOS.prefLabel, Literal(r["prefLabel_en"], lang="en")))
    for a in split(r["altLabels"]):
        lang = "en" if a.isascii() else "ko"
        g.add((s, SKOS.altLabel, Literal(a, lang=lang)))
    for b in split(r["broader"]):
        g.add((s, SKOS.broader, HBC[b])); g.add((HBC[b], SKOS.narrower, s))
    for b in split(r["related"]):
        g.add((s, SKOS.related, HBC[b])); g.add((HBC[b], SKOS.related, s))
    if r["top"].upper() == "TRUE":
        g.add((s, SKOS.topConceptOf, sch)); g.add((sch, SKOS.hasTopConcept, s))
    if r["scopeNote"]: g.add((s, SKOS.scopeNote, Literal(r["scopeNote"], lang="ko")))
g.serialize(os.path.join(g_dir, "개념.ttl"), format="turtle")
print("개념.ttl:", len(g))

# ═ 샘플 데이터
smp = list(csv.DictReader(open(os.path.join(g_dir, DATA + ".csv"), encoding="utf-8-sig")))
# 소장처·작성 기관은 샘플데이터.csv의 keeper_*, publisher_* 칸에서 만든다(여러 기관 레코드는 " | "로 나란히)
d = Graph(); bind(d)
bar = lambda v: [x.strip() for x in v.split("|")]
actors = {}
for r in smp:
    actors.setdefault(r["keeper"], (r["keeper_ko"], r["keeper_en"], r["keeper_search"]))
    for pid, pko, pen in zip(bar(r["publisher"]), bar(r["publisher_ko"]), bar(r["publisher_en"])):
        actors.setdefault(pid, (pko, pen, ""))
for k, (ko, en, search) in actors.items():
    s = HBO["actor-" + k]
    d.add((s, RDF.type, CRM.E39_Actor))
    d.add((s, RDF.type, CRM.E21_Person if "＊" in ko or "*" in ko else CRM.E74_Group))
    d.add((s, RDFS.label, Literal(ko, lang="ko")))
    if en: d.add((s, RDFS.label, Literal(en, lang="en")))
    if search: d.add((s, RDFS.seeAlso, URIRef(search.replace("소장품-검색", "%EC%86%8C%EC%9E%A5%ED%92%88-%EA%B2%80%EC%83%89"))))
for r in smp:
    o = HBO[r["objectID"]]
    d.add((o, RDF.type, CRM["E22_Human-Made_Object"]))
    d.add((o, DCTERMS.title, Literal(r["title_ko"], lang="ko")))
    if r["title_hani"]: d.add((o, DCTERMS.title, Literal(r["title_hani"], lang="ko-Hani")))
    if r["title_en"]: d.add((o, DCTERMS.title, Literal(r["title_en"], lang="en")))
    if r["keeperNo"]: d.add((o, DCTERMS.identifier, Literal(r["keeperNo"])))
    d.add((o, CRM.P2_has_type, HBC[r["objectType"]]))
    if r["motif"]: d.add((o, CRM.P2_has_type, HBC[r["motif"]]))
    d.add((o, CRM.P50_has_current_keeper, HBO["actor-" + r["keeper"]]))
    if r["nationality"]: d.add((o, DCTERMS.spatial, HBC[r["nationality"]]))
    for p in split(r["period"]): d.add((o, DCTERMS.temporal, HBC[p]))
    if r["date"]: d.add((o, DCTERMS.date, Literal(r["date"])))
    for kind in ["height", "width"]:
        if r[kind]:
            dm = HBO[f"{r['objectID']}-{kind}"]
            d.add((o, CRM.P43_has_dimension, dm)); d.add((dm, RDF.type, CRM.E54_Dimension))
            d.add((dm, CRM.P2_has_type, HBC[kind])); d.add((dm, CRM.P90_has_value, Literal(r[kind], datatype=XSD.decimal)))
            d.add((dm, CRM.P91_has_unit, HBC.cm))
    if r["wearingContext"]: d.add((o, CRM.P101_had_as_general_use, HBC[r["wearingContext"]]))
    d.add((o, DCTERMS.license, HBC[r["license"]]))
    for im in split(r["images"]): d.add((o, FOAF.depiction, URIRef(im.replace(" ", "%20"))))
    for rid, src, see, pub in zip(bar(r["recordID"]), bar(r["recordSource"]), bar(r["recordSeeAlso"]), bar(r["publisher"])):
        rec = HBO["record-" + re.sub(r"[^0-9A-Za-z_-]", "", pub + "-" + rid.split("-", 1)[1])]
        d.add((rec, RDF.type, CRM.E31_Document)); d.add((rec, CRM.P70_documents, o))
        d.add((rec, DCTERMS.identifier, Literal(rid)))
        if src: d.add((rec, DCTERMS.source, URIRef(src.replace(" ", "%20"))))
        if see: d.add((rec, RDFS.seeAlso, URIRef(see.replace(" ", "%20"))))
        d.add((rec, DCTERMS.publisher, HBO["actor-" + pub]))
d.serialize(os.path.join(g_dir, DATA + ".ttl"), format="turtle")
print(DATA + ".ttl:", len(d))

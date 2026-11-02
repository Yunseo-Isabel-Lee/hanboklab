"""개념.csv → 개념.ttl, 샘플데이터.csv → 샘플데이터.ttl
사용: python3 grounding2ttl.py <grounding 폴더> <어휘설명.csv 있는 폴더>
"""
import csv, sys, os
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, SKOS, DCTERMS, FOAF

g_dir, voc_dir = sys.argv[1], sys.argv[2]
voc = list(csv.DictReader(open(os.path.join(voc_dir, "어휘설명.csv"), encoding="utf-8-sig")))
NS = {r["termID"].rstrip(":"): r["definition"] for r in voc if r["termType"] == "Namespace"}
CRM = Namespace(NS["crm"]); HB = Namespace(NS["hanbok"]); HBC = Namespace(NS["hanbokc"]); HBO = Namespace(NS["hanboko"])
split = lambda s: [x.strip() for x in s.split(";") if x.strip()]

def bind(g):
    for p in ["crm", "hanbok", "hanbokc", "hanboko", "dcterms", "skos", "foaf", "rdfs", "xsd"]:
        g.bind(p, Namespace(NS[p]))

# ═ 개념
con = list(csv.DictReader(open(os.path.join(g_dir, "개념.csv"), encoding="utf-8-sig")))
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
KEEPERS = {
    "nmk": ("국립중앙박물관", "National Museum of Korea", "https://www.museum.go.kr/"),
    "met": ("메트로폴리탄 미술관", "The Metropolitan Museum of Art", "https://www.metmuseum.org/"),
    "dku": ("단국대학교 석주선기념박물관", "Dankook University Seok Juseon Memorial Museum", "https://museum.dankook.ac.kr/"),
    "gogung": ("국립고궁박물관", "National Palace Museum of Korea", "https://www.gogung.go.kr/"),
}
SEARCH = {"dku": "https://museum.dankook.ac.kr/소장품-검색"}
smp = list(csv.DictReader(open(os.path.join(g_dir, "샘플데이터.csv"), encoding="utf-8-sig")))
d = Graph(); bind(d)
for k, (ko, en, home) in KEEPERS.items():
    s = HBO["actor-" + k]
    d.add((s, RDF.type, CRM.E39_Actor)); d.add((s, RDF.type, CRM.E74_Group))
    d.add((s, RDFS.label, Literal(ko, lang="ko"))); d.add((s, RDFS.label, Literal(en, lang="en")))
    d.add((s, FOAF.homepage, URIRef(home)))
    if k in SEARCH: d.add((s, RDFS.seeAlso, URIRef(SEARCH[k].replace("소장품-검색", "%EC%86%8C%EC%9E%A5%ED%92%88-%EA%B2%80%EC%83%89"))))
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
    if r["beginYear"]: d.add((o, HB.beginYear, Literal(int(r["beginYear"]))))
    if r["endYear"]: d.add((o, HB.endYear, Literal(int(r["endYear"]))))
    for kind in ["height", "width"]:
        if r[kind]:
            dm = HBO[f"{r['objectID']}-{kind}"]
            d.add((o, CRM.P43_has_dimension, dm)); d.add((dm, RDF.type, CRM.E54_Dimension))
            d.add((dm, CRM.P2_has_type, HBC[kind])); d.add((dm, CRM.P90_has_value, Literal(r[kind], datatype=XSD.decimal)))
            d.add((dm, CRM.P91_has_unit, HBC.cm))
    if r["wearingContext"]: d.add((o, CRM.P101_had_as_general_use, HBC[r["wearingContext"]]))
    d.add((o, DCTERMS.license, HBC[r["license"]]))
    for im in split(r["images"]): d.add((o, FOAF.depiction, URIRef(im)))
    rec = HBO["record-" + r["publisher"] + "-" + r["objectID"]]
    d.add((rec, RDF.type, CRM.E31_Document)); d.add((rec, CRM.P70_documents, o))
    d.add((rec, DCTERMS.identifier, Literal(r["recordID"])))
    if r["recordSource"]: d.add((rec, DCTERMS.source, URIRef(r["recordSource"])))
    if r["recordSeeAlso"]: d.add((rec, RDFS.seeAlso, URIRef(r["recordSeeAlso"])))
    d.add((rec, DCTERMS.publisher, HBO["actor-" + r["publisher"]]))
d.serialize(os.path.join(g_dir, "샘플데이터.ttl"), format="turtle")
print("샘플데이터.ttl:", len(d))

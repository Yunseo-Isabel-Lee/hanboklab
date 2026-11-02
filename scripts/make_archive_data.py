"""공개 시제품용 데이터: 국중박(공공누리 1유형)·메트로폴리탄(CC0) 한국 흉배를 출처 시트에서 옮겨
샘플데이터.csv와 같은 형식(아카이브데이터.csv)으로 만든다.
사용: python3 make_archive_data.py <국중박 json> <메트 json> <통합시트 json> <출력 csv>
"""
import json, csv, re, sys
nmk_p, met_p, uni_p, out = sys.argv[1:5]

H = ["objectID", "title_ko", "title_hani", "title_en", "keeperNo", "objectType", "motif", "nationality",
     "period", "beginYear", "endYear", "height", "width", "wearingContext", "license", "images",
     "keeper", "recordID", "recordSource", "recordSeeAlso", "publisher", "원문_시대", "원문_크기", "원문_이용조건", "비고"]

def rows_of(values):
    h = values[0]
    return [dict(zip(h, r + [""] * (len(h) - len(r)))) for r in values[1:]]

raw = json.load(open(nmk_p))
nmk = rows_of(json.loads(raw[0]["text"])["values"] if isinstance(raw, list) else raw["values"])
met = rows_of(json.load(open(met_p))["values"])
uni = rows_of(json.load(open(uni_p))["values"])
imgs = {}
for r in uni:
    if r["원본이미지URL"]:
        imgs.setdefault((r["출처"], r["임시ID"]), []).append(r["원본이미지URL"])

HANJA = [("雙鶴", "ssanghak"), ("單鶴", "danhak"), ("雙虎", "ssangho"), ("單虎", "danho"),
         ("麒麟", "girin"), ("虎豹", "hopyo"), ("雲鶴", "unhak"), ("白鶴", "baekhak")]
KO = {"ssanghak": "쌍학", "danhak": "단학", "ssangho": "쌍호", "danho": "단호", "girin": "기린", "hopyo": "호표",
      "hak": "학", "baekhak": "백학", "unhak": "운학"}

def num(s):
    return s if s is None else str(float(s)).rstrip("0").rstrip(".") if "." in s else s

def size_ko(s):
    def g(*keys):
        for k in keys:
            m = re.search(k + r"\s*:?\s*([\d.]+)", s)
            if m: return m.group(1)
        return ""
    return g("세로", "길이"), g("가로", "너비")

out_rows = []
n = 0
# ── 국중박
EXCLUDE = {"남산245": "명칭(단호)과 사진(쌍호)이 맞지 않아 확인 전 제외", "건희4288": "흉배 집성 병풍", "건희4278": "흉배 집성 병풍"}
for r in nmk:
    if r["분류"] != "흉배" or r["소장처유물번호"] in EXCLUDE:
        continue
    n += 1
    hani = r["한자명"].split(",")[0].strip()
    motif = next((c for k, c in HANJA if k in hani.replace(" ", "")), "")
    h, w = size_ko(r["크기"])
    period_note = r["국적/시대"]
    out_rows.append([f"hb{n:04d}", r["한글명"], hani, r["영어명"], r["소장처유물번호"], "hyungbae", motif, "korea",
                     "", "", "", h, w, "", "kogl1", "; ".join(imgs.get(("국중박", r["임시ID"]), [])[:3]),
                     "nmk", f"국중박-{r['임시ID']}", r["URL"], "", "nmk",
                     period_note, r["크기"], r["공공누리유형"],
                     "시대가 '조선'뿐이라 시기는 비움" if "조선" in period_note or "시대미상" in period_note else ""])
# ── 메트로폴리탄 (한국)
def met_motif(en):
    e = en.lower()
    if "pair of cranes" in e or "two cranes" in e: return "ssanghak"
    if "white crane" in e: return "baekhak"
    if "tiger-leopard" in e: return "hopyo"
    if "crane" in e: return "hak"
    return ""
def met_period(d):
    d = d.lower()
    if not d: return ""
    m = re.search(r"(\d\d)th century", d)
    if not m: return ""
    c = m.group(1)
    if "late" in d: return f"c{c}late"
    if "early" in d: return f"c{c}early"
    return f"c{c}"
for r in met:
    if r["분류"] != "흉배" or "Korea" not in r["culture"]:
        continue
    n += 1
    motif = met_motif(r["영어명"])
    m = re.search(r"\(([\d.]+)\s*x\s*([\d.]+)\s*cm\)", r["dimensions"])
    h, w = (m.group(1), m.group(2)) if m else ("", "")
    ko = (KO[motif] + "흉배") if motif else "흉배"
    ims = [u.strip().replace("/original/", "/web-large/") for u in r["image_urls"].split(";") if u.strip()]
    out_rows.append([f"hb{n:04d}", ko, "", r["영어명"], r["소장처유물번호"].replace("Met ", ""), "hyungbae", motif, "korea",
                     met_period(r["date"]), "", "", h, w, "", "cc0", "; ".join(ims[:3]),
                     "met", f"메트로폴리탄-{r['임시ID']}", r["URL"], "", "met",
                     f"{r['period']} / {r['date']}".strip(" /"), r["dimensions"], r["license_note"],
                     "한글명은 아카이브가 붙임" + ("" if motif else ". 문양은 이미지 판독 전")])
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    wr = csv.writer(f); wr.writerow(H); wr.writerows(out_rows)
print(len(out_rows), "objects;", sum(1 for x in out_rows if x[16] == "nmk"), "nmk,", sum(1 for x in out_rows if x[16] == "met"), "met")

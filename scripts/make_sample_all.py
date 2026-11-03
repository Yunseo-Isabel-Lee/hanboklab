"""샘플데이터.csv (그라운딩 ③) — 흉배 전체.
통합시트 「메타_세로」(원본 메타데이터 전 칸)와 「이미지_통합」에서 분류가 '흉배'인 기록을 모아
유물 단위(소장처 + 소장처 유물번호)로 묶고, 기술규칙에 맞춰 값을 뽑는다.
시기·문양·국적·크기·이용조건·착용 맥락은 기관 기재값에서 자동으로 뽑은 것(연구자 검토 전).
사용: python3 make_sample_all.py <메타_세로 json> <이미지_통합 json> <출력 csv>
"""
import json, csv, re, sys, collections as C
meta_p, img_p, out = sys.argv[1:4]

# ── 불러오기 ─────────────────────────────────────────────
recs = C.OrderedDict()
for r in json.load(open(meta_p))["values"][1:]:
    r = r + [""] * (8 - len(r))
    src, tid, cls, _, _, col, _, val = r
    d = recs.setdefault((src, tid), {"_src": src, "_id": tid, "_cls": cls})
    d[col] = (d[col] + " || " + val) if col in d and d[col] != val else val
iv = json.load(open(img_p))["values"]; ih = iv[0]
IMG = C.defaultdict(list)
for r in iv[1:]:
    r = dict(zip(ih, r + [""] * (len(ih) - len(r))))
    if r["원본이미지URL"]:
        IMG[(r["출처"], r["임시ID"])].append(r["원본이미지URL"])
HB = [d for d in recs.values() if d["_cls"] == "흉배"]

# ── 기관(소장처·작성 기관) ─────────────────────────────────
# 출처 → (actor id, 한국어명, 영어명)
SRC = {
 "고궁": ("gogung", "국립고궁박물관", "National Palace Museum of Korea"),
 "이화여대": ("ewha", "이화여자대학교박물관", "Ewha Womans University Museum"),
 "국학진흥원": ("koreastudy", "한국국학진흥원", "Korean Studies Advancement Center"),
 "경기문화재연구원": ("ggich", "경기문화재연구원", ""),
 "e뮤지엄": ("emuseum", "e뮤지엄", "e-Museum"),
 "서울공예": ("craftmuseum", "서울공예박물관", "Seoul Museum of Craft Art"),
 "대전시립": ("daejeon", "대전시립박물관", "Daejeon Museum of History"),
 "경운": ("gyeongun", "경운박물관", "Kyungwoon Museum"),
 "숙명여대": ("sookmyung", "숙명여자대학교 정영양자수박물관", "Chung Young Yang Embroidery Museum, Sookmyung Women's University"),
 "브루클린": ("brooklyn", "브루클린 미술관", "Brooklyn Museum"),
 "보스턴": ("mfa", "보스턴 미술관", "Museum of Fine Arts, Boston"),
 "대영": ("bm", "대영박물관", "The British Museum"),
 "필드": ("field", "필드 자연사박물관", "Field Museum of Natural History"),
 "동아대": ("donga", "동아대학교 석당박물관", "Dong-A University Museum"),
 "충북대": ("cbnu", "충북대학교박물관", "Chungbuk National University Museum"),
 "국립대구": ("nmdaegu", "국립대구박물관", "Daegu National Museum"),
 "인천시립": ("incheon", "인천광역시립박물관", "Incheon Metropolitan City Museum"),
 "LACMA": ("lacma", "로스앤젤레스 카운티 미술관", "Los Angeles County Museum of Art"),
 "오죽헌": ("ojukheon", "오죽헌시립박물관", "Ojukheon Municipal Museum"),
 "스미소니언": ("cooperhewitt", "스미소니언 쿠퍼 휴잇 디자인 박물관", "Cooper Hewitt, Smithsonian Design Museum"),
 "서울역사": ("smh", "서울역사박물관", "Seoul Museum of History"),
 "클리블랜드": ("cma", "클리블랜드 미술관", "The Cleveland Museum of Art"),
 "V&A": ("vam", "빅토리아 앤드 앨버트 박물관", "Victoria and Albert Museum"),
 "경기도": ("ggmuseum", "경기도박물관", "Gyeonggi Provincial Museum"),
 "메트로폴리탄": ("met", "메트로폴리탄 미술관", "The Metropolitan Museum of Art"),
 "초상화DB": ("portraitdb", "국립문화유산연구원 초상화 DB", ""),
 "민속": ("nfm", "국립민속박물관", "National Folk Museum of Korea"),
 "리움": ("leeum", "리움미술관", "Leeum Museum of Art"),
 "국가유산포털": ("heritage", "국가유산청 국가유산포털", "Korea Heritage Service"),
 "연세대": ("yonsei", "연세대학교박물관", "Yonsei University Museum"),
 "세종대": ("sejong", "세종대학교박물관", "Sejong University Museum"),
 "서울대": ("snu", "서울대학교박물관", "Seoul National University Museum"),
 "국중박": ("nmk", "국립중앙박물관", "National Museum of Korea"),
 "단국대": ("dku", "단국대학교 석주선기념박물관", "Dankook University Seok Juseon Memorial Museum"),
 "전주역사": ("jeonju", "전주역사박물관", "Jeonju History Museum"),
}
# 소장처 표기(공백 제거) → 출처 기관과 같은 곳
KEEPER_ALIAS = {
 "국립고궁박물관": "고궁", "이화여자대학교박물관": "이화여대", "한국국학진흥원": "국학진흥원", "서울공예박물관": "서울공예",
 "대전시립박물관": "대전시립", "대전광역시시립박물관": "대전시립", "경운박물관": "경운", "숙명여대": "숙명여대",
 "숙명여자대학교정영양자수박물관": "숙명여대", "브루클린박물관": "브루클린", "보스턴미술관": "보스턴", "대영박물관": "대영",
 "필드박물관": "필드", "동아대학교석당박물관": "동아대", "국립대구박물관": "국립대구", "인천광역시립박물관": "인천시립",
 "로스앤젤레스카운티미술관(LACMA)": "LACMA", "오죽헌시립박물관": "오죽헌", "강릉시오죽헌시립박물관": "오죽헌",
 "스미소니언쿠퍼휴잇디자인박물관": "스미소니언", "서울역사박물관": "서울역사", "클리블랜드미술관": "클리블랜드",
 "빅토리아앤알버트박물관": "V&A", "경기도박물관": "경기도", "메트로폴리탄미술관": "메트로폴리탄", "국립민속박물관": "민속",
 "세종대학교박물관": "세종대", "서울대학교박물관": "서울대", "국립중앙박물관": "국중박",
 "단국대학교석주선기념박물관": "단국대", "전주역사": "전주역사", "전주역사박물관": "전주역사",
}
import unicodedata
nospace = lambda s: re.sub(r"\s", "", unicodedata.normalize("NFC", s or ""))
EXTRA = {}  # 출처 시트가 없는 소장처: 공백 없앤 이름 → (id, 표기)
def keeper_of(name):
    k = nospace(name)
    if k in KEEPER_ALIAS:
        return SRC[KEEPER_ALIAS[k]][:2]
    if k not in EXTRA:
        EXTRA[k] = (f"k{len(EXTRA) + 1:02d}", name.strip())
    return EXTRA[k]
SEARCH_PAGE = {"dku": "https://museum.dankook.ac.kr/소장품-검색"}

# ── 문양 ────────────────────────────────────────────────
# 앞에서부터 먼저 맞는 것을 쓴다(구체적인 것 → 일반적인 것)
MOTIF = [
 ("ssanghak", r"쌍학|雙鶴|양학|학\s*1쌍|two cranes|twin crane|pair of cranes|ssanghak"),
 ("danhak", r"단학|單鶴|single crane|danhak"),
 ("unhak", r"운학|雲鶴"),
 ("baekhak", r"백학|白鶴|white crane"),
 ("seonhak", r"선학|仙鶴"),
 ("ssangho", r"쌍호|雙虎|쌍백호|양호|두 마리 호랑이|two tigers|twin tiger|sanho"),
 ("danho", r"단호|單虎|호랑이 한 마리|single tiger|danho"),
 ("hopyo", r"호표|虎豹|tiger-leopard"),
 ("girin", r"기린|麒麟|qilin|kylin|kirin|girin"),
 ("haechi", r"해치|獬豸|해태"),
 ("baektaek", r"백택|白澤|baize"),
 ("bonghwang", r"봉황|鳳凰|phoenix|bonghwang"),
 ("gongjak", r"공작|孔雀|peacock|gongjak"),
 ("baekhan", r"백한|白鷳|白鷴|白鹇|silver pheasant|baekhan"),
 ("geumgye", r"금계|錦鷄|golden pheasant"),
 ("unan", r"운안|雲雁|wild goose|manchurian goose|\bgoose\b|unan"),
 ("nosa", r"노사|鷺|egret"),
 ("gyechik", r"계칙|鸂鶒|mandarin duck"),
 ("mechuragi", r"메추라기|鵪鶉|quail"),
 ("yeonjak", r"연작|練雀|paradise fly-?catcher"),
 ("sutak", r"수탉|rooster"),
 ("geobuk", r"거북|龜|turtle"),
 ("saja", r"사자|獅|\blions?\b"),
 ("pyobeom", r"표범|\bleopard"),
 ("gom", r"웅비|熊|\bbear\b"),
 ("haema", r"해마|海馬|sea ?horse"),
 ("yong", r"용문|용국문|\bdragon"),
 ("horangi", r"호랑이|\btiger\b"),
 ("hak", r"학흉배|학이 수놓|학 흉배|학문|\bcranes?\b|\bhak\b"),
]
MOTIF_KO = {"ssanghak": "쌍학", "danhak": "단학", "unhak": "운학", "baekhak": "백학", "seonhak": "선학", "ssangho": "쌍호",
 "danho": "단호", "hopyo": "호표", "girin": "기린", "haechi": "해치", "baektaek": "백택", "bonghwang": "봉황", "gongjak": "공작",
 "baekhan": "백한", "geumgye": "금계", "unan": "운안", "nosa": "노사", "gyechik": "계칙", "mechuragi": "메추라기",
 "yeonjak": "연작", "sutak": "수탉", "geobuk": "거북", "saja": "사자", "pyobeom": "표범", "gom": "곰", "haema": "해마",
 "yong": "용", "horangi": "호랑이", "hak": "학"}
def motif_of(text):
    for cid, pat in MOTIF:
        if re.search(pat, text, re.I):
            return cid
    return ""

# ── 국적 ────────────────────────────────────────────────
NAT_FIELDS = ["국적/시대", "국적시대분류", "culture", "place", "place_made", "Geography", "Dynasty", "Period", "period",
              "Related Geography", "시대", "연대", "시대분류"]
def nat_of(text):
    t = text
    if re.search(r"베트남|Vietnam", t): return "vietnam"
    if re.search(r"\bJapan", t): return "japan"
    ch = re.search(r"중국|China|Chinese|Qing|Ming dynasty|한족|\bbuzi\b|\blizi\b|보복", t, re.I)
    ko = re.search(r"한국|Korea|Joseon|조선|hyungbae|hungbae", t, re.I)
    if ch and not ko: return "china"
    if ko and not ch: return "korea"
    return ""

# ── 시기 ────────────────────────────────────────────────
PER_FIELDS = ["연대", "시대", "시대상세", "국적/시대", "국적시대분류", "시대분류", "제작연도", "Date", "Dynasty", "Period",
              "date", "date_text", "period", "Production date"]
YEAR_FIELDS = ["시대상세", "date", "date_text", "제작연도", "Date", "Production date"]
def cent(y): return (int(y) - 1) // 100 + 1
def periods_of(d):
    txt = " / ".join(d[f] for f in PER_FIELDS if d.get(f))
    t = re.sub(r"\([^)]*\d{4}[^)]*\)", " ", txt)          # 왕조 기간 괄호 (1392–1910) 등은 뺀다
    out = []
    for q, n in re.findall(r"(early|late|mid-?)?\s*(\d{2})(?:th|st|nd|rd)", t, re.I):
        q = q.lower()
        out.append(f"c{n}" + ("early" if q == "early" else "late" if q == "late" else ""))
    for n, q in re.findall(r"(\d{2})세기\s*(전반|초|후반|말|중반|중엽)?", t):
        out.append(f"c{n}" + ("early" if q in ("전반", "초") else "late" if q in ("후반", "말") else ""))
    if re.search(r"조선[^/]{0,12}(후기|後期)", t): out.append("joseonLate")
    if re.search(r"조선[^/]{0,12}(말기|末期)|구한말", t): out.append("joseonEnd")
    if re.search(r"조선[^/]{0,12}(전기|초기)", t): out.append("joseonEarly")
    if re.search(r"조선[^/]{0,12}중기", t): out.append("joseonMid")
    if "대한제국" in t: out.append("daehan")
    if "일제강점" in t: out.append("iljegangjeom")
    if re.search(r"광복\s*이후|1945년\s*이후", t): out.append("gwangbokAfter")
    if re.search(r"2000년\s*이후", t): out += ["gwangbokAfter", "c21"]
    if "근현대" in t: out.append("geunhyeondae")
    # 연도
    date = ""
    for f in YEAR_FIELDS:
        v = re.sub(r"\([^)]*\)", " ", d.get(f, ""))
        v = re.sub(r"1392\s*[-–]\s*1910|1368\s*[-–]\s*1644|1644\s*[-–]\s*19(?:11|12)", " ", v)  # 왕조 기간
        if re.search(r"before|after|이전|이후", v, re.I): continue
        if not v or re.search(r"\d{2}(th|st|nd|rd)|세기", v) and not re.search(r"\b1\d{3}\b", v):
            continue
        m = re.search(r"(c\.\s*|ca\.\s*|circa\s*)?\b(1[3-9]\d{2})\s*(?:[-–~]\s*(\d{2,4}))?(s)?\b", v)
        if not m: continue
        approx, a, b, s = m.groups()
        if s:  # 1800s
            out.append(f"c{cent(int(a) + 1)}"); continue
        if b:
            b = a[:4 - len(b)] + b if len(b) < 4 else b
            date = f"{a}{'~' if approx else ''}/{b}{'~' if approx else ''}"
            cs = range(int(a) // 100 + 1, cent(b) + 1)
        else:
            date = a + ("~" if approx else ""); cs = [cent(a)]
        if not any(re.match(r"c\d\d", p) for p in out):
            out += [f"c{c}" for c in cs]
        break
    seen = []
    for p in out:
        if p not in seen: seen.append(p)
    return seen, date, txt

# ── 크기 ────────────────────────────────────────────────
SIZE_FIELDS = ["크기", "dimensions", "Dimensions", "measurements"]
def f1(x): return f"{float(x):.1f}"
def inch(s):
    s = s.strip(); tot = 0.0
    for part in s.split():
        if "/" in part:
            a, b = part.split("/"); tot += float(a) / float(b)
        else:
            tot += float(part)
    return tot * 2.54
def size_of(s):
    """(세로, 가로, 메모). 단위 cm, 소수점 한 자리."""
    if not s: return "", "", ""
    s1 = s.replace("㎝", "cm").replace("centimetres", "cm").replace("×", "x").replace("*", "x")
    if re.fullmatch(r"\s*\d+\s*x\s*\d+\s*", s1): return "", "", "픽셀 크기라 제외"
    # 1) 표기가 붙은 값(세로·가로 등)
    H = r"세로|길이|높이|Height|Length|\(l\)|H"
    W = r"가로|너비|폭|Width|\(w\)|W"
    def find(lab):
        m = re.search(r"(?:%s)\s*[:：]?\s*([\d.]+)" % lab, s1)
        if m: return m.group(1)
        m = re.search(r"([\d.]+)\s*cm\s*(?:%s)" % lab, s1)   # 38.2cm(세로), 24.0cm(w)
        return m.group(1) if m else ""
    # 2) A x B cm (괄호 안 cm 우선: 인치 표기 뒤 cm 환산값)
    m = re.search(r"\(([\d.]+)\s*x\s*([\d.]+)\s*cm\)", s1) or re.search(r"([\d.]+)\s*x\s*([\d.]+)\s*cm", s1)
    if m and not re.search(r"세로|가로|\(w\)|\(l\)", s1):
        return f1(m.group(1)), f1(m.group(2)), "세로 x 가로 순서로 봄" if not re.search(r"Height x width|Warp x Weft|Overall|in\.", s1) else ""
    h, w = find(H), find(W)
    hs = re.findall(r"(?:세로|길이)\s*[:：]?\s*([\d.]+)", s1); ws = re.findall(r"(?:가로|너비)\s*(?:액자)?\s*[:：]?\s*([\d.]+)", s1)
    if len(hs) > 1 and len(ws) > 1 and ("액자" in s1 or abs(float(hs[0]) - float(hs[-1])) > 15):
        # 액자 크기와 흉배 크기가 함께 적힌 경우: 뒤쪽(작은) 값
        if True:
            return (f1(hs[-1]) if hs else ""), (f1(ws[-1]) if ws else ""), "액자 크기와 함께 적혀 흉배 크기(뒤쪽 값)를 씀"
    if h and not w and "정방" in s1: w = h
    if h or w:
        return (f1(h) if h else ""), (f1(w) if w else ""), ""
    m = re.search(r"([\d.]+)\s*x\s*([\d.]+)", s1)
    if m:
        return f1(m.group(1)), f1(m.group(2)), "단위·순서 표기 없음: cm, 세로 x 가로로 봄"
    m = re.search(r"([\d\s/]+)\s*x\s*([\d\s/]+)\s*in", s1)
    if m:
        return f1(inch(m.group(1))), f1(inch(m.group(2))), "인치를 cm로 환산"
    return "", "", ""

# ── 이용조건 ─────────────────────────────────────────────
def license_of(d):
    k = d.get("공공누리유형", "")
    m = re.search(r"제?\s*([1-4])\s*유형", k)
    if m: return f"kogl{m.group(1)}", k
    note = " / ".join(d[f] for f in ["license_note", "is_public_domain", "Rights Summary"] if d.get(f))
    if re.search(r"CC BY-NC|\bNC\b", note): return "nc", note
    if "건별" in note: return "licenseUnknown", note
    if "CC0" in note and "이미지 없음" not in note: return "cc0", note
    if re.search(r"is_public_domain", "") or d.get("is_public_domain", "").upper() == "TRUE": return "cc0", note
    return "licenseUnknown", (k or note or "표시 없음")

# ── 이미지 ──────────────────────────────────────────────
IMG_FIELDS = ["image_urls", "jpg_urls", "image_url", "원본이미지URL", "Access URI"]
def images_of(d):
    urls = list(IMG.get((d["_src"], d["_id"]), []))
    for f in IMG_FIELDS:
        urls += re.split(r"[;\s|]+", d.get(f, ""))
    out = []
    for u in urls:
        u = u.strip().strip("'\"[],")
        if not u.startswith("http") or re.search(r"\.(tif|tiff|dng)$", u, re.I) or "tiff" in u.lower(): continue
        u = re.sub(r"([?&])serviceKey=[^&]*&?", r"\1", u).rstrip("?&")   # e뮤지엄 인증키 제거
        if u not in out: out.append(u)
    return out

# ── 범위 판정 ────────────────────────────────────────────
def scope_of(names, ptxt, nat):
    why = []
    if re.search(r"광복\s*이후|2000년\s*이후|1945년\s*이후", ptxt): why.append("밖:광복 이후 제작(재현품 추정)")
    if "일제강점" in ptxt: why.append("밖:일제강점기")
    if "근현대" in ptxt: why.append("확인:근현대로 분류됨")
    if re.search(r"흉배판|수본|탁본|흉배본|수본판", names): why.append("밖:흉배판·수본")
    if re.search(r"집성|병$|8곡병|병풍|액자|stole|fragment", names, re.I): why.append("확인:흉배 집성·액자·조각")
    if re.search(r"(?<!백)관복|원삼|당의|녹원삼|단령|하피|부착한 포|costume|robe|원삼띠", names, re.I): why.append("확인:복식에 달린 흉배")
    if nat and nat != "korea": why.append(f"밖:국적({ {'china': '중국', 'vietnam': '베트남', 'japan': '일본'}[nat] })")
    if not nat: why.append("확인:국적 표기 없음")
    if any(w.startswith("밖") for w in why): s = "범위 밖"
    elif why: s = "확인 필요"
    else: s = "포함"
    return s, "; ".join(w.split(":", 1)[1] for w in why)

# ── 유물 단위로 묶기 ──────────────────────────────────────
def clean_no(s):
    s = (s or "").strip()
    return "" if (not s or "확인요망" in s) else s
groups = C.OrderedDict()
for d in HB:
    no = clean_no(d.get("소장처유물번호"))
    key = (keeper_of(d.get("소장처", "") or SRC[d["_src"]][1])[0], nospace(no)) if no else ("rec", d["_src"], d["_id"])
    groups.setdefault(key, []).append(d)

def own_first(ds, kid):
    """소장처 자신의 시트 기록을 앞에 둔다(e뮤지엄 등 다른 출처 기록은 뒤)."""
    return sorted(ds, key=lambda d: 0 if SRC[d["_src"]][0] == kid else 1)

def split_hani(name):
    m = re.search(r"\(([㐀-鿿\s·]+)\)", name)
    hani = m.group(1).strip() if m else ""
    return re.sub(r"\(([㐀-鿿\s·]+)\)", "", name).strip(), hani

# 이전 샘플(10건)에서 기관 설명을 읽고 정한 착용 맥락
OVERRIDE_WC = {"B007299": "gwanbok", "B002299": "gwanbok"}
def no_of(ds):
    return next((clean_no(d.get("소장처유물번호")) for d in ds if clean_no(d.get("소장처유물번호"))), "")

H = ["objectID", "title_ko", "title_hani", "title_en", "keeperNo", "objectType", "motif", "nationality",
     "period", "date", "height", "width", "wearingContext", "license", "images",
     "keeper", "keeper_ko", "keeper_en", "keeper_search",
     "recordID", "recordSource", "recordSeeAlso", "publisher", "publisher_ko", "publisher_en",
     "범위", "범위_사유", "원문_시대", "원문_크기", "원문_이용조건", "비고"]
rows = []
for n, (key, ds) in enumerate(groups.items(), 1):
    kname = next((d["소장처"] for d in ds if d.get("소장처")), SRC[ds[0]["_src"]][1])
    kid, kko = keeper_of(kname)
    ken = next((v[2] for v in SRC.values() if v[0] == kid), "")
    ds = own_first(ds, kid)
    notes = []
    # 명칭
    ko_raw = next((d["한글명"] for d in ds if d.get("한글명")), "")
    ko, hani2 = split_hani(ko_raw)
    hani = next((d["한자명"].strip() for d in ds if d.get("한자명")), "") or hani2
    en = next((d["영어명"].strip() for d in ds if d.get("영어명")), "")
    names = " / ".join(x for x in [ko_raw, hani, en] + [d.get("다른명칭", "") for d in ds] if x)
    motif = motif_of(names)
    if not ko:
        ko = (MOTIF_KO[motif] + " 흉배") if motif else "흉배"
        notes.append("한글명은 아카이브가 붙임")
    # 국적
    nat = ""
    for d in ds:
        nat = nat_of(" / ".join(d[f] for f in NAT_FIELDS if d.get(f)))
        if nat: break
    if not nat: nat = nat_of(names)
    # 시기
    per, date, ptxt = [], "", ""
    for d in ds:
        p, dt, tx = periods_of(d)
        ptxt = ptxt or tx
        if p or dt:
            per, date, ptxt = p, dt, tx; break
    if nat == "korea" and re.fullmatch(r"\s*(한국\s*-?\s*)?조선(시대)?\s*", ptxt or ""):
        pass  # '조선'만 적힌 경우 시기는 비운다(기술규칙)
    # 크기
    h = w = sraw = ""
    for d in ds:
        raw = next((d[f] for f in SIZE_FIELDS if d.get(f)), "")
        hh, ww, memo = size_of(raw)
        if raw and not sraw: sraw = raw
        if hh or ww:
            h, w, sraw = hh, ww, raw
            if memo: notes.append("크기: " + memo)
            break
    big = any(x and float(x) > 60 for x in (h, w)) or re.search(r"어깨너비|화장|등길이|품\s|전장", sraw)
    if big and (h or w):
        notes = [x for x in notes if not x.startswith("크기: ")]
        notes.append(f"크기는 흉배가 아닌 복식·병풍 전체 크기라 비움(원문 {sraw.strip()[:40]})")
        h = w = ""
    # 이용조건: 소장처 자신의 기록 → 알려진 값 → 확인 중
    lic, lraw = "licenseUnknown", ""
    for d in ds:
        l, raw = license_of(d)
        if not lraw: lraw = raw
        if l != "licenseUnknown":
            lic, lraw = l, raw; break
    # 착용 맥락 (명칭 → 설명 순)
    desc = " ".join(d.get(f, "") for d in ds for f in ["내용", "상세설명(가명)", "상세설명(가칭)", "Description", "briefDescription", "description", "상세내용"])
    wc = ""
    if re.search(r"혼례|wedding", names, re.I): wc = "honryebok"
    elif re.search(r"관복", names): wc = "gwanbok"
    elif re.search(r"혼례용|혼례 때|혼례복|wedding", desc, re.I): wc = "honryebok"
    elif re.search(r"(관복|官服\)?|단령)에\s*(달았던|부착된|부착한|달린)", desc): wc = "gwanbok"
    if no_of(ds) in OVERRIDE_WC: wc = OVERRIDE_WC[no_of(ds)]
    if no_of(ds) in OVERRIDE_WC: notes.append("착용 맥락은 이전 샘플에서 기관 설명으로 확인한 값")
    elif wc: notes.append("착용 맥락은 명칭·설명에서 자동 추출")
    # 이미지
    ims = []
    for d in ds:
        for u in images_of(d):
            if u not in ims: ims.append(u)
    # 기관 레코드
    rid, rsrc, rsee, pub, pko, pen = [], [], [], [], [], []
    for d in ds:
        pid, pk, pe = SRC[d["_src"]]
        url = d.get("URL", "").strip()
        if pid in ("sejong", "dku") or "소장품-검색" in url or "mode=list" in url: url = ""
        rid.append(f"{d['_src']}-{d['_id']}"); rsrc.append(url); rsee.append(d.get("상세API", "").strip())
        pub.append(pid); pko.append(pk); pen.append(pe)
    scope, why = scope_of(" / ".join([ko_raw, en]) + " " + " ".join(d.get("용도/기능", "") for d in ds), " ".join(ptxt for _ in [0]) + " " + " ".join(d.get("국적/시대", "") + d.get("국적시대분류", "") for d in ds), nat)
    if len(ds) > 1: notes.append(f"기관 레코드 {len(ds)}개")
    no = re.sub(r"^Met\s+", "", no_of(ds))
    rows.append([f"hb{n:04d}", ko, hani, en, no, "hyungbae", motif, nat,
                 "; ".join(per), date, h, w, wc, lic, "; ".join(ims[:6]),
                 kid, kko, ken, SEARCH_PAGE.get(kid, ""),
                 " | ".join(rid), " | ".join(rsrc), " | ".join(rsee), " | ".join(pub), " | ".join(pko), " | ".join(pen),
                 scope, why, ptxt, sraw.strip(), lraw, ". ".join(notes)])

with open(out, "w", encoding="utf-8-sig", newline="") as f:
    wr = csv.writer(f); wr.writerow(H); wr.writerows(rows)
print(len(HB), "records ->", len(rows), "objects")

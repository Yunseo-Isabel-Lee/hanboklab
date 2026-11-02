"""개념.csv 만들기 (그라운딩 ②: 개념체계 안의 개념과 이칭)
열: conceptID, scheme, prefLabel_ko, prefLabel_en, altLabels(; 구분), broader(; 구분), related(; 구분), top, scopeNote
"""
import csv, sys
out = sys.argv[1]
H = ["conceptID", "scheme", "prefLabel_ko", "prefLabel_en", "altLabels", "broader", "related", "top", "scopeNote"]
R = []
def c(cid, scheme, ko, en, alt="", broader="", related="", top="", note=""):
    R.append([cid, scheme, ko, en, alt, broader, related, top, note])

# ── 자료 구분
S = "objectType"
c("hyungbae", S, "흉배", "rank badge", "胸背; 흉배판; hyungbae; insignia", top="TRUE", note="관복의 가슴과 등에 다는 네모난 표장. 이번 범위의 자료 구분")
c("dallyeong", S, "단령", "dallyeong", "團領; 관복 단령; round-collared robe", top="TRUE", note="2차 범위")
c("chosang", S, "초상화", "portrait", "초상; 肖像; 肖像畵", top="TRUE", note="2차 범위")

# ── 문양 (주문양만. 부류 → 동물 → 단·쌍 등)
S = "motif"
c("naljimseung", S, "날짐승", "birds", "새; 조류", top="TRUE", note="날짐승 문양의 부류")
c("giljimseung", S, "길짐승", "beasts", "짐승; 수류", top="TRUE", note="길짐승 문양의 부류")
c("hak", S, "학", "crane", "鶴; 학문; 학무늬; crane", broader="naljimseung")
c("ssanghak", S, "쌍학", "pair of cranes", "雙鶴; 쌍학문; 쌍학무늬; 쌍학흉배; 雙鶴胸背; two cranes; twin cranes", broader="hak", note="학 두 마리")
c("danhak", S, "단학", "single crane", "單鶴; 단학문; 단학무늬; 단학흉배; 單鶴胸背; one crane", broader="hak", note="학 한 마리")
c("unhak", S, "운학", "crane and clouds", "雲鶴; 운학문; 운학흉배", broader="hak", note="구름 속의 학")
c("baekhak", S, "백학", "white crane", "白鶴; 백학문; 백학흉배", broader="hak", note="흰 학")
c("unan", S, "운안", "wild geese and clouds", "雲雁; 운안문; 운안흉배; 기러기; wild goose", broader="naljimseung", note="구름과 기러기")
c("gongjak", S, "공작", "peacock", "孔雀; 공작문; 공작흉배; peacock", broader="naljimseung")
c("baekhan", S, "백한", "silver pheasant", "白鷴; 白鹇; 백한문; 백한흉배; silver pheasant", broader="naljimseung")
c("bonghwang", S, "봉황", "phoenix", "鳳凰; 鳳; 봉; 봉황문; 봉황흉배; phoenix", broader="naljimseung")
c("horangi", S, "호랑이", "tiger", "虎; 호; 호문; 호랑이무늬; tiger", broader="giljimseung")
c("ssangho", S, "쌍호", "pair of tigers", "雙虎; 쌍호문; 쌍호무늬; 쌍호흉배; 雙虎胸背; 양호; two tigers; twin tigers", broader="horangi", note="호랑이 두 마리")
c("danho", S, "단호", "single tiger", "單虎; 단호문; 단호무늬; 단호흉배; 單虎胸背; one tiger", broader="horangi", note="호랑이 한 마리")
c("hopyo", S, "호표", "tiger and leopard", "虎豹; 호표문; 호표흉배; tiger-leopard", broader="giljimseung")
c("girin", S, "기린", "qilin", "麒麟; 기린문; 기린무늬; 기린흉배; qilin; kirin", broader="giljimseung")
c("haechi", S, "해치", "haechi", "獬豸; 해태; 해치문; 해치흉배; haetae", broader="giljimseung")
c("baektaek", S, "백택", "baekthaek", "白澤; 백택문; 백택흉배", broader="giljimseung")
c("saja", S, "사자", "lion", "獅子; 獅; 사자문; 사자흉배; lion", broader="giljimseung")
c("geobuk", S, "거북", "turtle", "龜; 거북문; 거북흉배; turtle", top="TRUE", note="날짐승·길짐승 어디에도 넣지 않은 문양")

# ── 국적
S = "nationality"
c("korea", S, "한국", "Korea", "조선; 한국 - 조선; 한국-조선; Korean; Joseon", top="TRUE")
c("china", S, "중국", "China", "청; 명; 淸; 明; Chinese; 한족", top="TRUE", note="중국 흉배(보자)는 이번 범위 밖. 거르는 데 쓴다")

# ── 시기 (숫자 구간을 정하지 않는다)
S = "period"
for n, en in [(15, "15th century"), (16, "16th century"), (17, "17th century"), (18, "18th century"), (19, "19th century"), (20, "20th century")]:
    c(f"c{n}", S, f"{n}세기", en, f"{n}C; {n}th c.", top="TRUE")
    c(f"c{n}early", S, f"{n}세기 전반", f"early {en}", f"{n}세기 초; early {n}th century", broader=f"c{n}")
    c(f"c{n}late", S, f"{n}세기 후반", f"late {en}", f"{n}세기 말; late {n}th century", broader=f"c{n}")
c("joseon", S, "조선 시대", "Joseon dynasty", "조선; 朝鮮; Joseon", top="TRUE", note="기관이 '조선'만 적은 경우는 이 개념에 연결하지 않고 비운다(기술규칙)")
c("joseonEarly", S, "조선 전기", "early Joseon", "조선초기; 조선 초기", broader="joseon", related="c15; c16", note="경계는 연구자마다 다르다. 세기와는 '관련'으로만 잇는다")
c("joseonMid", S, "조선 중기", "mid Joseon", "조선중기", broader="joseon", related="c16; c17")
c("joseonLate", S, "조선 후기", "late Joseon", "조선후기", broader="joseon", related="c17; c18; c19")
c("joseonEnd", S, "조선 말기", "end of Joseon", "조선말기; 구한말", broader="joseon", related="c19; c20")
c("daehan", S, "대한제국", "Korean Empire", "대한제국기; 大韓帝國", top="TRUE", related="c19; c20")

# ── 착용 맥락
S = "wearingContext"
c("gwanbok", S, "관복", "official uniform", "官服; 관복용; 공복; 상복(常服)", top="TRUE", note="관원이 관직 생활에서 입은 단령 등에 단 흉배")
c("honryebok", S, "혼례복", "wedding attire", "婚禮服; 혼례용; 신랑 단령", top="TRUE", note="형태가 같은 단령이라도 혼례 때 입었으면 혼례복")
c("wearingUnknown", S, "미상", "unknown", "", top="TRUE")

# ── 이용조건 (상업 이용 가능 여부로 묶는다)
S = "license"
c("commercialOk", S, "상업 이용 가능", "commercial use allowed", "상업적 이용 가능; 상업적으로 쓸 수 있는; 상용 가능", top="TRUE", note="출처를 밝히면 상업적으로 쓸 수 있는 이용조건의 묶음")
c("commercialNo", S, "상업 이용 불가", "non-commercial only", "비영리; 상업적 이용 금지", top="TRUE")
c("licenseUnknown", S, "확인 중", "unconfirmed", "미확인; 표시 없음; 확인요망", top="TRUE", note="출처 사이트에 이용조건 표시가 없거나 아직 확인하지 않음")
c("kogl1", S, "공공누리 1유형", "KOGL Type 1", "제1유형; 출처표시", broader="commercialOk")
c("kogl2", S, "공공누리 2유형", "KOGL Type 2", "제2유형; 출처표시+상업적이용금지", broader="commercialNo")
c("kogl3", S, "공공누리 3유형", "KOGL Type 3", "제3유형; 출처표시+변경금지", broader="commercialOk", note="변경은 금지되지만 상업 이용은 가능")
c("kogl4", S, "공공누리 4유형", "KOGL Type 4", "제4유형; 출처표시+상업적이용금지+변경금지", broader="commercialNo")
c("cc0", S, "CC0", "CC0", "퍼블릭 도메인; Public Domain; Met Open Access (CC0); Open Access", broader="commercialOk")
c("nc", S, "CC BY-NC", "CC BY-NC", "NC; 비영리", broader="commercialNo")

# ── 측정
S = "measurement"
c("height", S, "세로", "height", "높이; 길이; H; L", top="TRUE")
c("width", S, "가로", "width", "너비; 폭; W", top="TRUE")
c("cm", S, "cm", "centimetre", "센티미터; ㎝", top="TRUE", note="crm:E58_Measurement_Unit을 겸한다")

with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(H); w.writerows(R)
print(len(R), "concepts")

# 변환 스크립트

CSV를 고친 뒤 다시 돌리면 TTL과 문서 페이지가 새로 만들어진다. 필요한 패키지: `pip install rdflib pyshacl dctap`

| 스크립트 | 하는 일 | 사용 |
|---|---|---|
| csv2ttl.py | 기술규칙.dctap.csv → 기술규칙.ttl(SHACL), 어휘설명.csv → 어휘설명.ttl | `python3 csv2ttl.py <CSV 폴더>` |
| make_docs.py | 두 CSV → 사람이 읽는 문서 페이지(ontology/index.html)와 자체 속성 이동 페이지 | `python3 make_docs.py <CSV 폴더> <출력 폴더>` |
| make_concepts.py | 개념.csv(통제어휘 개념과 이칭) 만들기 | `python3 make_concepts.py <출력 CSV>` |
| make_sample_all.py | 통합시트 「메타_세로」·「이미지_통합」(시트 JSON)에서 분류가 '흉배'인 기록을 유물 단위로 묶어 샘플데이터.csv 만들기. 문양·시기·국적·크기·이용조건·착용 맥락은 기관 기재값에서 자동 추출 | `python3 make_sample_all.py <메타_세로.json> <이미지_통합.json> <출력 CSV>` |
| grounding2ttl.py | 개념.csv → 개념.ttl, 샘플데이터.csv → 샘플데이터.ttl | `python3 grounding2ttl.py <그라운딩 폴더> <어휘설명.csv 폴더>` |
| make_queries.py | 질문–SPARQL 예시를 샘플에 돌려 질문예시.csv·.rq 만들기 | `python3 make_queries.py <그라운딩 폴더> <어휘설명.csv 폴더>` |
| make_projects.py | 첫 화면 프로젝트 칸 → /projects/ 목록, 흉배 라벨링 매뉴얼 원고(hyungbae/manual/src/*.md) → 매뉴얼·판별 참고 도감 페이지. `pip install markdown` 필요 | `python3 scripts/make_projects.py` |

검사: `dctap read 기술규칙.dctap.csv`(DCTAP 형식), pyshacl로 데이터가 기술규칙.ttl을 지키는지 확인.

아카이브 시제품 스크립트(make_archive_data.py, make_archive_site.py)는 [archive.hanboklab](https://github.com/Yunseo-Isabel-Lee/archive.hanboklab) 저장소로 옮겼다.

검사할 때는 샘플데이터.ttl + 개념.ttl + 어휘설명.ttl을 함께 넣는다(개념체계 정의가 어휘설명.ttl에 있음).

샘플 데이터(소장처 기록)는 소장처 이용조건 확인 전이라 이 저장소에 올리지 않는다.

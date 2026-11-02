# 변환 스크립트

CSV를 고친 뒤 다시 돌리면 TTL과 문서 페이지가 새로 만들어진다. 필요한 패키지: `pip install rdflib pyshacl dctap`

| 스크립트 | 하는 일 | 사용 |
|---|---|---|
| csv2ttl.py | 기술규칙.dctap.csv → 기술규칙.ttl(SHACL), 어휘설명.csv → 어휘설명.ttl | `python3 csv2ttl.py <CSV 폴더>` |
| make_docs.py | 두 CSV → 사람이 읽는 문서 페이지(ontology/index.html)와 자체 속성 이동 페이지 | `python3 make_docs.py <CSV 폴더> <출력 폴더>` |
| make_concepts.py | 개념.csv(통제어휘 개념과 이칭) 만들기 | `python3 make_concepts.py <출력 CSV>` |
| grounding2ttl.py | 개념.csv → 개념.ttl, 샘플데이터.csv → 샘플데이터.ttl | `python3 grounding2ttl.py <그라운딩 폴더> <어휘설명.csv 폴더>` |
| make_archive_data.py | 국중박·메트로폴리탄 출처 시트 → 공개 시제품용 아카이브데이터.csv | `python3 make_archive_data.py <국중박 json> <메트 json> <통합시트 json> <출력 csv>` |
| make_archive_site.py | 아카이브데이터 + 개념 → 시제품 페이지(hyungbae/) | `python3 make_archive_site.py <데이터 폴더> <개념.csv 폴더> <출력 폴더>` |
| make_queries.py | 질문–SPARQL 예시를 샘플에 돌려 질문예시.csv·.rq 만들기 | `python3 make_queries.py <그라운딩 폴더> <어휘설명.csv 폴더>` |

검사: `dctap read 기술규칙.dctap.csv`(DCTAP 형식), pyshacl로 데이터가 기술규칙.ttl을 지키는지 확인.

샘플 데이터(소장처 기록)는 소장처 이용조건 확인 전이라 이 저장소에 올리지 않는다.

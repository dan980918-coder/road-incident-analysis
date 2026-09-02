# 도로 돌발상황 분석

ITS 국가교통정보센터의 도로 돌발상황(돌발정보) 데이터(약 62.3만 건, 2024-11 ~ 2025-10)를
활용해 돌발 유형·시간대·계절·도로 특성별 발생 패턴을 분석하고, 각 돌발 레코드에 위험도
점수를 매겨 우선순위가 높은 유형을 식별하는 포트폴리오 프로젝트입니다.

## 프로젝트 구조

```
.
├── data/
│   ├── README.md               # 데이터 출처 및 스키마 설명
│   ├── incident_data.csv       # 원본 전처리 데이터 (140MB, git 미포함 — .gitignore)
│   └── incident_data_sample.csv# 재현/확인용 샘플 2,000행 (git 포함)
├── src/
│   ├── load_data.py             # 데이터 로딩 + 파생변수(hour/month/season/지역) 생성
│   ├── region_mapping.py        # 위경도 → 17개 시/도 행정경계 매핑 (geopandas)
│   └── plot_config.py           # 노트북 공용 matplotlib/seaborn 스타일
├── notebooks/
│   ├── 01_eda.ipynb                    # 데이터 구조, 결측치, 기본 분포 탐색
│   ├── 02_pattern_analysis.ipynb       # 유형별 · 요일별 · 시간대별 · 계절별 패턴
│   ├── 03_road_region_analysis.ipynb   # 도로타입 · 도로번호 · 지역별 분석
│   └── 04_risk_scoring.ipynb           # 돌발상황 위험도 스코어링
├── outputs/figures/             # 각 노트북 실행 결과 PNG
└── requirements.txt
```

## 데이터

원본 CSV(`data/incident_data.csv`, 140MB)는 GitHub 기본 push 용량 제한(100MB)을 초과해
이 저장소에는 포함하지 않았습니다(`.gitignore`). 대신 재현 확인용 샘플
(`data/incident_data_sample.csv`, 2,000행)과 출처·스키마 문서만 포함했습니다.

전체 데이터로 노트북을 실행하려면 **ITS 국가교통정보센터(https://www.its.go.kr)**에서
동일 기간(2024-11-06 ~ 2025-10-31)의 돌발정보를 별도로 다운로드해 스키마에 맞게 전처리한
뒤 `data/incident_data.csv`로 저장해야 합니다. 자세한 컬럼 스키마는
[data/README.md](data/README.md)를 참고하세요.

## 노트북 실행

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

`data/incident_data.csv` (전체 데이터)가 없으면 노트북이 실행되지 않습니다. 전체 데이터
없이 구조만 확인하려면 `data/incident_data_sample.csv`를 `src/load_data.py`의
`DATA_PATH` 인자로 넘겨 로드할 수 있습니다.

## 분석 내용

### 01. EDA
데이터 구조, 결측치, 기간 범위, 돌발구분/돌발상세구분 및 도로타입 분포를 확인합니다.

### 02. 유형·시간대·계절별 패턴
돌발상세구분 Top10, 월별 트렌드, 평일/주말 비교, 요일×유형 히트맵, 시간대별(평일/주말)
분포, 계절별 발생량 및 교통사고 비율을 분석합니다.

### 03. 도로타입·도로번호·지역별 분석
도로타입별 발생 건수와 돌발구분 구성비, 주요 도로번호별 비중, 시/도별(행정경계 기준)
발생 건수와 지역별 Top1 돌발유형을 분석합니다.

### 04. 위험도 스코어링
각 돌발 레코드에 **위치(0~20) · 돌발유형(0~25) · 차로통제(0~40) · 시간대(0~15)** 4개
항목을 정규식/키워드 기반으로 채점해 0~100점의 `risk_score`를 산출합니다. 이를 바탕으로
돌발상세구분별 평균 위험도와, 빈도×평균위험도로 계산한 위험기여도 Top5를 시각화합니다.
채점 기준의 상세 근거는 노트북 내 마크다운 셀에 함께 기록되어 있습니다.

## 알려진 한계

- **지역 분류**: `src/region_mapping.py`의 `지역` 컬럼은 원본 데이터에 없는 파생
  컬럼입니다. 위경도(X, Y) 좌표를 `geopandas`로 실제 시/도 행정경계(통계청 SGIS 기반,
  `data/boundaries/`)와 point-in-polygon 매칭해 분류하며, 행정경계 밖으로 판정되는
  좌표(해상/GPS 오차, 약 0.3%)는 최근접 시/도로 대체 배정합니다. 이전 버전(시/도 대표
  좌표와의 최근접 거리 근사)은 서울 인근 좌표가 실제로는 경기도인데도 서울로 오분류되어
  전체 1위가 서울로 나오는 문제가 있었는데, 실제 경계 기준으로 교체한 뒤에는 원본
  보고서와 동일하게 경기도가 1위로 나옵니다. 경계 데이터는 저장소 용량을 위해
  단순화(simplify tolerance 0.0005도)했으며, 이로 인해 전체 62.3만 건 중 172건(0.03%)만
  단순화 전과 다르게 분류됩니다.
- **위험도 스코어링의 텍스트 기반 판별**: `돌발내용` 컬럼이 자유 텍스트(반정형)라 정규식/
  키워드 매칭으로 위치·차로 정보를 추출합니다. 드물게 일부 표현(예: 지명에 숫자+교가
  없는 교량명)은 위치 점수에서 누락될 수 있습니다.

## 6. 대시보드

[![도로 돌발상황 대시보드](https://public.tableau.com/static/images/_1/_17658672451790/sheet7/1.png)](https://public.tableau.com/views/_17658672451790/sheet7?:language=ko-KR&:display_count=n&:origin=viz_share_link)

Tableau로 제작한 인터랙티브 대시보드입니다. 도로명, 도로타입, 돌발유형, 요일, 월,
평일/주말, 지도 등 총 8가지 방식으로 필터링하여 대한민국 도로 돌발상황을
직관적으로 분석·확인할 수 있습니다.

▶ [Tableau Public에서 인터랙티브 버전 보기](https://public.tableau.com/views/_17658672451790/sheet7?:language=ko-KR&:display_count=n&:origin=viz_share_link)

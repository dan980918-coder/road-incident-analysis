"""돌발상황 위험도 스코어링 (04_risk_scoring.ipynb).

위치 / 돌발유형 / 차로통제 / 시간대 4개 항목을 각각 0~20 / 0~25 / 0~40 / 0~15점으로
채점한다. 배점 구조는 원본 보고서 2.1.2절 기준표를 재현한 것이다. `돌발내용`이 자유
텍스트라 위치·차로 점수는 정규식/키워드 매칭으로 판별한다.
"""
import re

import pandas as pd

# --- 위치 점수 (0~20) -------------------------------------------------------
TUNNEL_RE = re.compile(r"터널")
# '대교/육교/교량'은 무조건 교량, 'N교'(고잔3교, 무안1교 등 숫자+교)도 교량 명명 패턴으로 인정.
# 단순 'X교' 패턴은 '판교'(지명), 'OO교회', '차로교대'처럼 교량이 아닌 오탐이 많아 제외했다.
BRIDGE_RE = re.compile(r"대교|육교|교량|\d교(?:$|[^통])")
IC_JC_RE = re.compile(r"IC|JC|JCT|분기")
HIGHWAY_TYPES = {"고속국도", "도시고속도로"}
NORMAL_ROAD_TYPES = {"일반국도", "지방도", "국가지원지방도", "시군도", "특별광역시도"}


def location_score(row: pd.Series) -> int:
    text = row["돌발내용"] if pd.notna(row["돌발내용"]) else ""
    if TUNNEL_RE.search(text):
        return 20
    if BRIDGE_RE.search(text):
        return 15
    if IC_JC_RE.search(text):
        return 10
    road_type = row["도로타입"]
    if road_type in HIGHWAY_TYPES:
        return 8
    if road_type in NORMAL_ROAD_TYPES:
        return 3
    return 0


# --- 돌발 점수 (0~25) -------------------------------------------------------
ACCIDENT_DETAILS = {"사고", "추돌사고", "단독사고", "화재사고", "전도사고", "충돌사고", "역주행", "시설물사고"}
BREAKDOWN_DETAILS = {"고장", "고장차"}
WORK_DETAILS = {"작업", "시설물보수작업", "노면보수작업", "도로포장", "차선도색", "가로등작업", "이동작업", "교량점검"}
CONGESTION_DETAILS = {"차량증가/정체", "지정체"}
WEATHER_DETAILS = {
    "강우", "적설", "안개", "강풍", "노면습기", "결빙", "강설", "호우",
    "대설", "노면결빙", "침수", "하천범람", "도로유실", "낙석", "산사태",
}


def incident_score(row: pd.Series) -> int:
    detail, category = row["돌발상세구분"], row["돌발구분"]
    if detail in ACCIDENT_DETAILS or category == "교통사고":
        return 25
    if detail in BREAKDOWN_DETAILS:
        return 15
    if detail in WORK_DETAILS or category == "공사":
        return 10
    if detail in CONGESTION_DETAILS:
        return 5
    if detail in WEATHER_DETAILS or category == "기상":
        return 3
    return 0  # 통제/보행자/이벤트/이륜차/화재/장애물 등 미분류 -> 기타


# --- 차로 점수 (0~40) -------------------------------------------------------
LANE_NUM_RE = re.compile(r"(\d(?:,\d)+|\d)차로")


def lane_score(text) -> int:
    if pd.isna(text):
        return 0
    text = str(text)
    if "전면통제" in text or "전체차로" in text:
        return 40
    nums = set()
    for m in LANE_NUM_RE.finditer(text):
        nums.update(m.group(1).split(","))
    if len(nums) >= 2:
        return 30
    if len(nums) == 1:
        return 20
    if "차로교대" in text:
        return 20
    if "갓길" in text:
        return 10
    return 0


# --- 시간 점수 (0~15) -------------------------------------------------------
def time_score(hour: int) -> int:
    if hour in (7, 8, 9, 17, 18, 19):
        return 15
    if 10 <= hour <= 16:
        return 10
    return 5  # 야간/심야 (20~23시, 0~6시)

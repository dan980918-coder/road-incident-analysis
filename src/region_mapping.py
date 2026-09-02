"""
위도(Y)/경도(X) 좌표를 대한민국 17개 시/도 실제 행정경계와의 point-in-polygon
방식으로 분류하는 헬퍼 모듈.

경계 데이터는 통계청 SGIS(공공누리 제1유형 라이선스) 2018년 시/도 경계를 기반으로 한
southkorea/southkorea-maps 리포지토리의 GeoJSON을, 정확도 손실이 미미한 수준으로
단순화(simplify tolerance 0.0005도)해 `data/boundaries/`에 포함했다 — 전체 62.3만 건
중 172건(0.03%)만 단순화 전과 다르게 분류되는 수준이다.

이전 버전(시/도 대표 좌표와의 최근접 거리 근사)은 서울 인근 좌표가 실제로는 경기도
행정구역에 속하는데도 서울 중심점과 가까워 서울로 오분류되는 경우가 많아, 전체 발생
건수 1위가 경기도(원본 보고서)가 아닌 서울로 나오는 문제가 있었다. 실제 행정경계
기준으로 교체한 뒤에는 경기도가 1위로 나와 원본 보고서와 순서가 일치한다.
"""
from pathlib import Path

import geopandas as gpd
import pandas as pd

BOUNDARY_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "boundaries" / "skorea_provinces_simplified.geojson"
)

_boundaries: gpd.GeoDataFrame | None = None


def _load_boundaries() -> gpd.GeoDataFrame:
    global _boundaries
    if _boundaries is None:
        _boundaries = gpd.read_file(BOUNDARY_PATH)[["name", "geometry"]]
    return _boundaries


def assign_region(y: pd.Series, x: pd.Series) -> pd.Series:
    """위도(y)/경도(x) 배열을 받아 point-in-polygon으로 시/도명을 반환한다.

    행정경계 밖으로 판정되는 좌표(해상 좌표, GPS 오차 등 전체의 약 0.3%)는
    가장 가까운 시/도로 대체 배정해 항상 값을 반환한다.
    """
    boundaries = _load_boundaries()
    points = gpd.GeoDataFrame(
        index=y.index,
        geometry=gpd.points_from_xy(x, y),
        crs="EPSG:4326",
    )

    joined = gpd.sjoin(points, boundaries, how="left", predicate="within")
    joined = joined[~joined.index.duplicated(keep="first")]
    result = joined["name"]

    missing_idx = result[result.isna()].index
    if len(missing_idx):
        # 거리 기반 최근접 판정이므로 미터 단위 평면좌표계(한국 중부원점)로 변환 후 계산한다.
        KOREA_TM = "EPSG:5179"
        nearest = gpd.sjoin_nearest(
            points.loc[missing_idx].to_crs(KOREA_TM), boundaries.to_crs(KOREA_TM)
        )
        nearest = nearest[~nearest.index.duplicated(keep="first")]
        result.loc[missing_idx] = nearest["name"]

    return result.reindex(y.index)

"""
위도(Y)/경도(X) 좌표를 대한민국 17개 시/도로 근사 분류하는 헬퍼 모듈.

주의(한계점):
  - 행정구역 경계 shapefile 없이 각 시/도 대표 좌표(중심점)와의 최근접 거리로
    근사 분류하는 방식입니다. 실제 행정경계와 다를 수 있으며, 특히 도 경계
    인접 지역에서는 오분류 가능성이 있습니다. (README 한계점 참고)
"""
import numpy as np
import pandas as pd

# 시/도 대표 좌표 (위도, 경도) — 근사치
PROVINCE_CENTROIDS = {
    "서울특별시": (37.5665, 126.9780),
    "부산광역시": (35.1796, 129.0756),
    "대구광역시": (35.8714, 128.6014),
    "인천광역시": (37.4563, 126.7052),
    "광주광역시": (35.1595, 126.8526),
    "대전광역시": (36.3504, 127.3845),
    "울산광역시": (35.5384, 129.3114),
    "세종특별자치시": (36.4801, 127.2890),
    "경기도": (37.4138, 127.5183),
    "강원도": (37.8228, 128.1555),
    "충청북도": (36.6357, 127.4917),
    "충청남도": (36.5184, 126.8000),
    "전라북도": (35.7175, 127.1530),
    "전라남도": (34.8161, 126.4630),
    "경상북도": (36.4919, 128.8889),
    "경상남도": (35.4606, 128.2132),
    "제주특별자치도": (33.4996, 126.5312),
}


def assign_region(y: pd.Series, x: pd.Series) -> pd.Series:
    """위도(y)/경도(x) 배열을 받아 최근접 시/도 중심점 기준으로 지역명을 반환한다."""
    names = list(PROVINCE_CENTROIDS.keys())
    lat0 = np.array([v[0] for v in PROVINCE_CENTROIDS.values()])
    lon0 = np.array([v[1] for v in PROVINCE_CENTROIDS.values()])

    y_arr = y.to_numpy()[:, None]
    x_arr = x.to_numpy()[:, None]

    # 위경도差 기반 유클리드 근사 거리 (지역 분류 목적으로는 충분)
    dist = (y_arr - lat0[None, :]) ** 2 + (x_arr - lon0[None, :]) ** 2
    nearest_idx = np.argmin(dist, axis=1)
    return pd.Series([names[i] for i in nearest_idx], index=y.index)

"""도로 돌발상황 데이터 로딩 + 분석용 파생변수 생성."""
import pandas as pd
from pathlib import Path
from .region_mapping import assign_region

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "incident_data.csv"

SEASON_MAP = {
    3: "봄", 4: "봄", 5: "봄",
    6: "여름", 7: "여름", 8: "여름",
    9: "가을", 10: "가을", 11: "가을",
    12: "겨울", 1: "겨울", 2: "겨울",
}


def load(path: Path = DATA_PATH, with_region: bool = True) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")

    df["돌발일시"] = pd.to_datetime(df["돌발일시"], errors="coerce")
    df = df.dropna(subset=["돌발일시"]).copy()

    df["hour"] = df["돌발일시"].dt.hour
    df["month"] = df["돌발일시"].dt.month
    df["season"] = df["month"].map(SEASON_MAP)

    if with_region:
        df["지역"] = assign_region(df["Y"], df["X"])

    return df

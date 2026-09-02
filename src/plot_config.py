"""노트북 전반에서 공용으로 쓰는 matplotlib/seaborn 스타일 설정."""
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm

# OS별로 흔히 설치돼 있는 한글 폰트 후보 (우선순위 순). 실행 환경에 설치된
# 폰트가 다를 수 있어 하드코딩 대신 설치 여부를 확인해 첫 번째로 찾은 것을 사용한다.
KOREAN_FONT_CANDIDATES = [
    "Noto Sans CJK KR", "Noto Sans KR",       # Linux
    "Malgun Gothic",                           # Windows
    "Apple SD Gothic Neo", "AppleGothic",      # macOS
    "NanumGothic",
]


def set_korean_style():
    # plt.style.use()가 font.family를 되돌려버리므로 스타일 적용 이후에 폰트를 지정한다.
    plt.style.use("seaborn-v0_8-whitegrid")
    available = {f.name for f in fm.fontManager.ttflist}
    font = next((f for f in KOREAN_FONT_CANDIDATES if f in available), None)
    if font is not None:
        mpl.rcParams["font.family"] = font
    mpl.rcParams["axes.unicode_minus"] = False

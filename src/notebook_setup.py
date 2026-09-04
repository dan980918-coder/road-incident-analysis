"""노트북 공통 초기화.

모든 노트북 첫 셀에서 반복되던 "한글 폰트 스타일 적용 + outputs/figures 폴더 준비"를
한 곳으로 모은다. `src`를 임포트하려면 노트북에서 프로젝트 루트를 `sys.path`에 먼저
추가해야 하므로, 그 두 줄만은 각 노트북에 그대로 남겨둔다.
"""
import pathlib

from .plot_config import set_korean_style

FIG_DIR = pathlib.Path(__file__).resolve().parents[1] / "outputs" / "figures"


def init_notebook() -> pathlib.Path:
    """한글 폰트 스타일을 적용하고 FIG_DIR을 만든 뒤 그 경로를 반환한다."""
    set_korean_style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    return FIG_DIR

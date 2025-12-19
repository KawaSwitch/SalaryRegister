from enum import Enum
from typing import Final


class SalaryKind(Enum):
    """給与種別を表す列挙型"""
    NORMAL = "給与"
    BONUS = "賞与"
    SPECIAL = "特別金"


class FileNames:
    """ファイル名関連の定数"""
    PDF_SALARY_INFIX: Final[str] = "_kyuyo_"
    PDF_BONUS_INFIX: Final[str] = "_syoyo_"
    PDF_EXTENSION: Final[str] = ".pdf"
    ITEMS_YAML: Final[str] = "items.yml"
    CONFIG_INI: Final[str] = "config.ini"


class DirectoryNames:
    """ディレクトリ名関連の定数"""
    USERDATA: Final[str] = "../userdata"
    SALARY_DATA: Final[str] = "salaryData"


class ItemNames:
    """給与項目名の定数"""
    DEDUCTION_SUM: Final[str] = "控除合計"
    DEDUCTION_KEY: Final[str] = "deduction"


class UIConstants:
    """UI関連の定数"""
    DEFAULT_WAIT_TIMEOUT: Final[int] = 5
    SHORT_SLEEP: Final[float] = 0.2
    MEDIUM_SLEEP: Final[float] = 0.3
    LONG_SLEEP: Final[float] = 0.5
    WINDOW_WIDTH: Final[int] = 1280
    WINDOW_HEIGHT: Final[int] = 720

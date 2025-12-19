import sys
from typing import Final, Optional
import argparse

from logger import Logger
from common import SalaryKind


class Arguments:
    """起動引数管理クラス"""
    
    # 引数数の定数
    MIN_ARGS: Final[int] = 3
    MAX_ARGS: Final[int] = 4
    
    # メッセージテンプレート
    USAGE_EXAMPLE: Final[str] = "python upload.py 2024 11"
    USAGE_MSG_MISSING: Final[str] = "給与登録を行う年と月を入力してください"
    USAGE_MSG_INVALID: Final[str] = "正しい数値形式で給与登録を行う年と月を入力してください"

    def __init__(self) -> None:
        self.year: Optional[int] = None
        self.month: Optional[int] = None
        self.kind: Optional[SalaryKind] = None
        self.parser: Optional[argparse.ArgumentParser] = None

        self._register_args()
        self.isOk = self._validate_args()

    def _register_args(self) -> None:
        """起動引数情報を設定する"""
        description = "PDFから給与情報(控除情報)を取得しMoneyForwardへアップロードします。"
        self.parser = argparse.ArgumentParser(description=description)

        self.parser.add_argument("year", type=int, help="登録する年")
        self.parser.add_argument("month", type=int, help="登録する月")
        self.parser.add_argument(
            "-b", "--bonus", action="store_true", help="賞与登録であるか"
        )

    def _validate_args(self) -> bool:
        """引数チェック"""
        if not self._check_arg_count():
            return False
        
        if not self._parse_args():
            return False
        
        self._log_registration_info()
        return True
    
    def _check_arg_count(self) -> bool:
        """引数の数を検証する"""
        arg_count = len(sys.argv)
        if not (self.MIN_ARGS <= arg_count <= self.MAX_ARGS):
            Logger.logWarning(self.USAGE_MSG_MISSING)
            Logger.logWarning(f"例：{self.USAGE_EXAMPLE}")
            return False
        return True
    
    def _parse_args(self) -> bool:
        """引数をパースして値を設定する"""
        try:
            args = self.parser.parse_args()
            self.year = args.year
            self.month = args.month
            self.kind = SalaryKind.BONUS if args.bonus else SalaryKind.NORMAL
            return True
        except (Exception, SystemExit):
            Logger.logWarning(self.USAGE_MSG_INVALID)
            Logger.logWarning(f"例：{self.USAGE_EXAMPLE}")
            return False
    
    def _log_registration_info(self) -> None:
        """登録情報をログ出力する"""
        Logger.logInfo(
            f"{self.year}年{self.month:02}月の{self.kind.value}明細登録を行います。"
        )

    def is_valid(self) -> bool:
        """起動引数が問題ないか"""
        return self.isOk

    def get_year(self) -> int:
        """給与設定する年を取得する"""
        return self.year

    def get_month(self) -> int:
        """給与設定する月を取得する"""
        return self.month

    def get_kind(self) -> SalaryKind:
        """給与設定種別を取得する"""
        return self.kind
    
    # 後方互換性のためのエイリアス（非推奨）
    def isValid(self) -> bool:
        return self.is_valid()
    
    def getYear(self) -> int:
        return self.get_year()
    
    def getMonth(self) -> int:
        return self.get_month()
    
    def getKind(self) -> SalaryKind:
        return self.get_kind()

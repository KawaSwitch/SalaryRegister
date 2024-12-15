import sys
from logger import Logger
from common import SalaryKind
import argparse


# 引数管理
class Arguments:

    def __init__(self):
        self.year = None
        self.month = None
        self.kind = None

        self.registerArgs()
        self.isOk = self.argCheck()

    # 起動引数情報を設定する
    def registerArgs(self):
        desc = "PDFから給与情報(控除情報)を取得しMoneyForwardへアップロードします。"
        self.parser = argparse.ArgumentParser(description=desc)

        self.parser.add_argument("year", type=int, help="登録する年")
        self.parser.add_argument("month", type=int, help="登録する月")
        self.parser.add_argument(
            "-b", "--bonus", action="store_true", help="賞与登録であるか"
        )

    # 引数チェック
    def argCheck(self) -> bool:
        num = len(sys.argv)
        if not (num == 3 or num == 4):
            Logger.logWarning("給与登録を行う年と月を入力してください")
            Logger.logWarning("例：python upload.py 2024 11")
            return False

        try:
            args = self.parser.parse_args()
            self.year = args.year
            self.month = args.month
            self.kind = SalaryKind.BONUS if args.bonus else SalaryKind.NORMAL

        except (Exception, SystemExit):
            Logger.logWarning("正しい数値形式で給与登録を行う年と月を入力してください")
            Logger.logWarning("例：python upload.py 2024 11")
            return False

        Logger.logInfo(
            f"{self.year}年{self.month:02}月の{self.kind.value}明細登録を行います。"
        )
        return True

    # 起動引数が問題ないか
    def isValid(self):
        return self.isOk

    # 給与設定する年を取得する
    def getYear(self) -> int:
        return self.year

    # 給与設定する月を取得する
    def getMonth(self) -> int:
        return self.month

    # 給与設定種別を取得する
    def getKind(self) -> SalaryKind:
        return self.kind

from datetime import datetime
from logger import Logger
from reader import SalaryReader
from common import SalaryKind
import config


# 給与（１ヶ月分）
class Salary:
    def __init__(self, year, month, kind=SalaryKind.NORMAL):
        self.year = year
        self.month = month
        self.date = None
        self.kind = kind
        number = config.data.getEmployeeNumber()  # 社員番号

        # 給与データをPDFから取得
        reader = SalaryReader(year, month, number, kind)
        self.deductionItems = reader.readDeduction()
        self.showDeductionInfo()

    # 控除項目の一覧を標準出力へ表示する
    def showDeductionInfo(self):
        Logger.logInfo("--- 登録する控除項目一覧 ---")
        for item in self.deductionItems:
            Logger.logInfo(item)
        Logger.logInfo("--------- end ----------")

    # 給料日を日にちを設定する
    # True:設定成功 / False:あり得ない日付が設定された場合
    def setDate(self, date) -> bool:
        try:
            datetime.strptime(f"{self.year}-{self.month}-{date}", "%Y-%m-%d")
            self.date = date
            return True
        except Exception as e:
            Logger.logError(e)
            return False

    # 給料日を取得する(例:2024/11/25)
    def getPayday(self) -> str:
        return f"{self.year}/{self.month:0>2}/{self.date:0>2}"

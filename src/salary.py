from datetime import datetime
from typing import Optional, Final

from logger import Logger
from reader import SalaryReader
from common import SalaryKind
from item import Item
import config


class Salary:
    """給与（１ヶ月分）を表すクラス"""
    
    # フォーマット定数
    DATE_FORMAT: Final[str] = "%Y-%m-%d"
    PAYDAY_FORMAT: Final[str] = "{year}/{month:0>2}/{date:0>2}"
    
    # ログメッセージ
    LOG_HEADER: Final[str] = "--- 登録する控除項目一覧 ---"
    LOG_FOOTER: Final[str] = "--------- end ----------"
    
    def __init__(self, year: int, month: int, kind: SalaryKind = SalaryKind.NORMAL) -> None:
        """
        給与情報の初期化
        
        Args:
            year: 年
            month: 月
            kind: 給与種別（デフォルトは通常給与）
        """
        self.year = year
        self.month = month
        self.date: Optional[int] = None
        self.kind = kind
        self.deductionItems: list[Item] = []
        
        self._load_salary_data()
        self._show_deduction_info()
    
    def _load_salary_data(self) -> None:
        """給与データをPDFから読み込む"""
        employee_number = config.data.get_employee_number()
        reader = SalaryReader(self.year, self.month, employee_number, self.kind)
        self.deductionItems = reader.readDeduction()

    def _show_deduction_info(self) -> None:
        """控除項目の一覧を標準出力へ表示する"""
        Logger.logInfo(self.LOG_HEADER)
        for item in self.deductionItems:
            Logger.logInfo(str(item))
        Logger.logInfo(self.LOG_FOOTER)

    def set_date(self, date: int | str) -> bool:
        """
        給料日を日にちを設定する
        
        Args:
            date: 日付（整数または文字列）
        
        Returns:
            設定成功のTrue、あり得ない日付の場合False
        """
        try:
            date_value = int(date)
            datetime.strptime(
                f"{self.year}-{self.month}-{date_value}", 
                self.DATE_FORMAT
            )
            self.date = date_value
            return True
        except (ValueError, Exception) as e:
            Logger.logError(str(e))
            return False

    def get_payday(self) -> str:
        """
        給料日を取得する
        
        Returns:
            給料日の文字列表現（例：2024/11/25）
        """
        return self.PAYDAY_FORMAT.format(
            year=self.year, 
            month=self.month, 
            date=self.date
        )
    
    # 後方互換性のためのエイリアス（非推奨）
    def showDeductionInfo(self) -> None:
        """非推奨: _show_deduction_info()を使用してください"""
        self._show_deduction_info()
    
    def setDate(self, date: int | str) -> bool:
        """非推奨: set_date()を使用してください"""
        return self.set_date(date)
    
    def getPayday(self) -> str:
        """非推奨: get_payday()を使用してください"""
        return self.get_payday()

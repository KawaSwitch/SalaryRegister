"""
test_common.py
common.pyの単体試験

C0, C1, C2カバレッジ100%を目指したテストケース
"""
import pytest
from common import SalaryKind, FileNames, DirectoryNames, ItemNames, UIConstants


class TestSalaryKind:
    """SalaryKind列挙型のテスト"""
    
    def test_normal_value(self):
        """NORMAL属性の値が正しいか"""
        assert SalaryKind.NORMAL.value == "給与"
    
    def test_bonus_value(self):
        """BONUS属性の値が正しいか"""
        assert SalaryKind.BONUS.value == "賞与"
    
    def test_special_value(self):
        """SPECIAL属性の値が正しいか"""
        assert SalaryKind.SPECIAL.value == "特別金"
    
    def test_enum_members(self):
        """列挙型のメンバー数が正しいか"""
        assert len(SalaryKind) == 3
    
    def test_enum_comparison(self):
        """列挙型の比較が正しく動作するか"""
        assert SalaryKind.NORMAL != SalaryKind.BONUS
        assert SalaryKind.NORMAL == SalaryKind.NORMAL


class TestFileNames:
    """FileNames定数クラスのテスト"""
    
    def test_pdf_salary_infix(self):
        """PDF給与ファイル名の中綴り"""
        assert FileNames.PDF_SALARY_INFIX == "_kyuyo_"
    
    def test_pdf_bonus_infix(self):
        """PDF賞与ファイル名の中綴り"""
        assert FileNames.PDF_BONUS_INFIX == "_syoyo_"
    
    def test_pdf_extension(self):
        """PDF拡張子"""
        assert FileNames.PDF_EXTENSION == ".pdf"
    
    def test_items_yaml(self):
        """項目定義ファイル名"""
        assert FileNames.ITEMS_YAML == "items.yml"
    
    def test_config_ini(self):
        """設定ファイル名"""
        assert FileNames.CONFIG_INI == "config.ini"


class TestDirectoryNames:
    """DirectoryNames定数クラスのテスト"""
    
    def test_userdata_dir(self):
        """ユーザデータディレクトリ名"""
        assert DirectoryNames.USERDATA == "../userdata"
    
    def test_salary_data_dir(self):
        """給与データディレクトリ名"""
        assert DirectoryNames.SALARY_DATA == "salaryData"


class TestItemNames:
    """ItemNames定数クラスのテスト"""
    
    def test_deduction_sum(self):
        """控除合計項目名"""
        assert ItemNames.DEDUCTION_SUM == "控除合計"
    
    def test_deduction_key(self):
        """控除項目キー"""
        assert ItemNames.DEDUCTION_KEY == "deduction"


class TestUIConstants:
    """UIConstants定数クラスのテスト"""
    
    def test_default_wait_timeout(self):
        """デフォルトのタイムアウト"""
        assert UIConstants.DEFAULT_WAIT_TIMEOUT == 5
        assert isinstance(UIConstants.DEFAULT_WAIT_TIMEOUT, int)
    
    def test_short_sleep(self):
        """短いスリープ時間"""
        assert UIConstants.SHORT_SLEEP == 0.2
        assert isinstance(UIConstants.SHORT_SLEEP, float)
    
    def test_medium_sleep(self):
        """中程度のスリープ時間"""
        assert UIConstants.MEDIUM_SLEEP == 0.3
        assert isinstance(UIConstants.MEDIUM_SLEEP, float)
    
    def test_long_sleep(self):
        """長いスリープ時間"""
        assert UIConstants.LONG_SLEEP == 0.5
        assert isinstance(UIConstants.LONG_SLEEP, float)
    
    def test_window_width(self):
        """ウィンドウ幅"""
        assert UIConstants.WINDOW_WIDTH == 1280
        assert isinstance(UIConstants.WINDOW_WIDTH, int)
    
    def test_window_height(self):
        """ウィンドウ高さ"""
        assert UIConstants.WINDOW_HEIGHT == 720
        assert isinstance(UIConstants.WINDOW_HEIGHT, int)
    
    def test_sleep_ordering(self):
        """スリープ時間の大小関係"""
        assert UIConstants.SHORT_SLEEP < UIConstants.MEDIUM_SLEEP < UIConstants.LONG_SLEEP

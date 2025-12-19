"""
test_salary.py
salary.pyの単体試験

C0, C1, C2カバレッジ100%を目指したテストケース
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from salary import Salary
from common import SalaryKind
from item import Item


@pytest.fixture(autouse=True)
def mock_config():
    """全テストでconfig.dataをモック"""
    with patch('salary.config.data') as mock_data:
        mock_data.get_employee_number.return_value = "12345"
        mock_data.get_pdf_password.return_value = "test_password"
        yield mock_data


class TestSalaryInitialization:
    """Salaryクラスの初期化テスト"""
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_init_with_normal_salary(self, mock_emp, mock_reader_class):
        """通常給与での初期化"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = [Item("控除", 1000)]
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 11)
            
            assert salary.year == 2024
            assert salary.month == 11
            assert salary.kind == SalaryKind.NORMAL
            assert salary.date is None
            assert len(salary.deductionItems) == 1
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="67890")
    def test_init_with_bonus(self, mock_emp, mock_reader_class):
        """賞与での初期化"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 6, SalaryKind.BONUS)
            
            assert salary.year == 2024
            assert salary.month == 6
            assert salary.kind == SalaryKind.BONUS
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_init_calls_load_salary_data(self, mock_emp, mock_reader_class):
        """初期化時に給与データがロードされる"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 11)
            
            mock_reader_class.assert_called_once()
            mock_reader.readDeduction.assert_called_once()


class TestLoadSalaryData:
    """_load_salary_dataメソッドのテスト"""
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_load_salary_data_calls_reader(self, mock_emp, mock_reader_class):
        """SalaryReaderを使って給与データをロードする"""
        mock_reader = MagicMock()
        item1 = Item("健康保険", 10000)
        item2 = Item("厚生年金", 20000)
        mock_reader.readDeduction.return_value = [item1, item2]
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 11)
            
            assert len(salary.deductionItems) == 2
            assert salary.deductionItems[0].name == "健康保険"
            assert salary.deductionItems[1].name == "厚生年金"


class TestShowDeductionInfo:
    """_show_deduction_infoメソッドのテスト"""
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    @patch('salary.Logger.logInfo')
    def test_show_deduction_info_displays_items(self, mock_log, mock_emp, mock_reader_class):
        """控除項目がログ出力される"""
        mock_reader = MagicMock()
        item1 = Item("健康保険", 10000)
        mock_reader.readDeduction.return_value = [item1]
        mock_reader_class.return_value = mock_reader
        
        salary = Salary(2024, 11)
        
        # ヘッダー、項目、フッターが出力されることを確認
        assert mock_log.call_count >= 3
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_deprecated_showDeductionInfo(self, mock_emp, mock_reader_class):
        """非推奨メソッドshowDeductionInfo"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 11)
            
            with patch('salary.Logger.logInfo') as mock_log:
                salary.showDeductionInfo()
                assert mock_log.call_count >= 2


class TestSetDate:
    """set_dateメソッドのテスト"""
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_set_date_with_valid_int(self, mock_emp, mock_reader_class):
        """有効な整数での日付設定"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 11)
            result = salary.set_date(25)
            
            assert result is True
            assert salary.date == 25
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_set_date_with_valid_string(self, mock_emp, mock_reader_class):
        """有効な文字列での日付設定"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 11)
            result = salary.set_date("15")
            
            assert result is True
            assert salary.date == 15
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_set_date_with_invalid_date(self, mock_emp, mock_reader_class):
        """無効な日付での設定"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            with patch('salary.Logger.logError'):
                salary = Salary(2024, 2)  # 2月
                result = salary.set_date(30)  # 2月に30日は存在しない
                
                assert result is False
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_set_date_with_invalid_format(self, mock_emp, mock_reader_class):
        """無効な形式での設定"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            with patch('salary.Logger.logError'):
                salary = Salary(2024, 11)
                result = salary.set_date("abc")
                
                assert result is False
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_set_date_boundary_values(self, mock_emp, mock_reader_class):
        """境界値のテスト"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 1)
            
            # 1日
            assert salary.set_date(1) is True
            # 31日
            assert salary.set_date(31) is True
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_deprecated_setDate(self, mock_emp, mock_reader_class):
        """非推奨メソッドsetDate"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 11)
            result = salary.setDate(20)
            
            assert result is True
            assert salary.date == 20


class TestGetPayday:
    """get_paydayメソッドのテスト"""
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_get_payday_with_date_set(self, mock_emp, mock_reader_class):
        """日付設定後の給料日取得"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 11)
            salary.set_date(25)
            payday = salary.get_payday()
            
            assert payday == "2024/11/25"
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_get_payday_single_digit_month_and_date(self, mock_emp, mock_reader_class):
        """1桁の月と日付の給料日取得"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 3)
            salary.set_date(5)
            payday = salary.get_payday()
            
            assert payday == "2024/03/05"
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_deprecated_getPayday(self, mock_emp, mock_reader_class):
        """非推奨メソッドgetPayday"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 11)
            salary.set_date(15)
            payday = salary.getPayday()
            
            assert payday == "2024/11/15"


class TestSalaryConstants:
    """Salaryクラスの定数テスト"""
    
    def test_date_format(self):
        """日付フォーマット定数"""
        assert Salary.DATE_FORMAT == "%Y-%m-%d"
    
    def test_payday_format(self):
        """給料日フォーマット定数"""
        assert "{year}" in Salary.PAYDAY_FORMAT
        assert "{month:0>2}" in Salary.PAYDAY_FORMAT
        assert "{date:0>2}" in Salary.PAYDAY_FORMAT
    
    def test_log_header(self):
        """ログヘッダー定数"""
        assert "登録する控除項目一覧" in Salary.LOG_HEADER
    
    def test_log_footer(self):
        """ログフッター定数"""
        assert "end" in Salary.LOG_FOOTER


class TestSalaryEdgeCases:
    """Salaryクラスのエッジケーステスト"""
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_leap_year_february(self, mock_emp, mock_reader_class):
        """うるう年の2月のテスト"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 2)  # 2024年はうるう年
            
            # 29日は有効
            assert salary.set_date(29) is True
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_non_leap_year_february(self, mock_emp, mock_reader_class):
        """非うるう年の2月のテスト"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            with patch('salary.Logger.logError'):
                salary = Salary(2023, 2)  # 2023年は通常年
                
                # 29日は無効
                assert salary.set_date(29) is False
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_december_31st(self, mock_emp, mock_reader_class):
        """12月31日のテスト"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 12)
            assert salary.set_date(31) is True
            assert salary.get_payday() == "2024/12/31"
    
    @patch('salary.SalaryReader')
    @patch('salary.config.data.get_employee_number', return_value="12345")
    def test_january_1st(self, mock_emp, mock_reader_class):
        """1月1日のテスト"""
        mock_reader = MagicMock()
        mock_reader.readDeduction.return_value = []
        mock_reader_class.return_value = mock_reader
        
        with patch('salary.Logger.logInfo'):
            salary = Salary(2024, 1)
            assert salary.set_date(1) is True
            assert salary.get_payday() == "2024/01/01"

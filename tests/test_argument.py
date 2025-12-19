"""
test_argument.py
argument.pyの単体試験

C0, C1, C2カバレッジ100%を目指したテストケース
"""
import pytest
import sys
from unittest.mock import patch, MagicMock
from argument import Arguments
from common import SalaryKind


class TestArgumentsInitialization:
    """Argumentsクラスの初期化テスト"""
    
    def test_init_with_valid_args(self):
        """有効な引数での初期化"""
        test_args = ['upload.py', '2024', '11']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.year == 2024
            assert args.month == 11
            assert args.kind == SalaryKind.NORMAL
            assert args.isOk is True
    
    def test_init_with_bonus_flag(self):
        """賞与フラグ付きでの初期化"""
        test_args = ['upload.py', '2024', '12', '--bonus']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.year == 2024
            assert args.month == 12
            assert args.kind == SalaryKind.BONUS
            assert args.isOk is True
    
    def test_init_with_bonus_short_flag(self):
        """賞与フラグ（短縮形）での初期化"""
        test_args = ['upload.py', '2024', '6', '-b']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.year == 2024
            assert args.month == 6
            assert args.kind == SalaryKind.BONUS


class TestArgumentsValidation:
    """引数の検証テスト"""
    
    def test_too_few_args(self):
        """引数が少なすぎる場合"""
        test_args = ['upload.py', '2024']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logWarning') as mock_warn:
                args = Arguments()
                assert args.isOk is False
                assert mock_warn.call_count >= 2
    
    def test_too_many_args(self):
        """引数が多すぎる場合"""
        test_args = ['upload.py', '2024', '11', '--bonus', 'extra']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logWarning') as mock_warn:
                args = Arguments()
                assert args.isOk is False
    
    def test_no_args(self):
        """引数なしの場合"""
        test_args = ['upload.py']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logWarning') as mock_warn:
                args = Arguments()
                assert args.isOk is False
                assert mock_warn.call_count >= 2
    
    def test_invalid_year_format(self):
        """年の形式が不正な場合"""
        test_args = ['upload.py', 'abc', '11']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logWarning') as mock_warn:
                args = Arguments()
                assert args.isOk is False
    
    def test_invalid_month_format(self):
        """月の形式が不正な場合"""
        test_args = ['upload.py', '2024', 'xyz']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logWarning') as mock_warn:
                args = Arguments()
                assert args.isOk is False


class TestArgumentsCheckArgCount:
    """_check_arg_countメソッドのテスト"""
    
    def test_min_args_boundary(self):
        """最小引数数の境界値（3個）"""
        test_args = ['upload.py', '2024', '11']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.isOk is True
    
    def test_max_args_boundary(self):
        """最大引数数の境界値（4個）"""
        test_args = ['upload.py', '2024', '11', '--bonus']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.isOk is True
    
    def test_below_min_args(self):
        """最小引数数未満（2個）"""
        test_args = ['upload.py', '2024']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logWarning'):
                args = Arguments()
                assert args.isOk is False
    
    def test_above_max_args(self):
        """最大引数数超過（5個以上）"""
        test_args = ['upload.py', '2024', '11', '--bonus', 'extra']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logWarning'):
                args = Arguments()
                assert args.isOk is False


class TestArgumentsParseArgs:
    """_parse_argsメソッドのテスト"""
    
    def test_parse_normal_salary(self):
        """通常給与のパース"""
        test_args = ['upload.py', '2023', '5']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.year == 2023
            assert args.month == 5
            assert args.kind == SalaryKind.NORMAL
    
    def test_parse_bonus(self):
        """賞与のパース"""
        test_args = ['upload.py', '2023', '7', '-b']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.kind == SalaryKind.BONUS
    
    def test_parse_exception_handling(self):
        """例外処理のテスト"""
        test_args = ['upload.py', 'invalid', '11']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logWarning') as mock_warn:
                args = Arguments()
                assert args.isOk is False
                assert any("正しい数値形式" in str(call) for call in mock_warn.call_args_list)


class TestArgumentsLogRegistrationInfo:
    """_log_registration_infoメソッドのテスト"""
    
    def test_log_normal_salary(self):
        """通常給与のログ出力"""
        test_args = ['upload.py', '2024', '3']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logInfo') as mock_info:
                args = Arguments()
                assert any("2024年03月" in str(call) and "給与" in str(call) 
                          for call in mock_info.call_args_list)
    
    def test_log_bonus(self):
        """賞与のログ出力"""
        test_args = ['upload.py', '2024', '12', '--bonus']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logInfo') as mock_info:
                args = Arguments()
                assert any("2024年12月" in str(call) and "賞与" in str(call) 
                          for call in mock_info.call_args_list)


class TestArgumentsGetters:
    """getterメソッドのテスト"""
    
    @pytest.fixture
    def valid_args(self):
        """有効な引数を持つArgumentsインスタンス"""
        test_args = ['upload.py', '2024', '8']
        with patch.object(sys, 'argv', test_args):
            return Arguments()
    
    def test_is_valid_true(self, valid_args):
        """is_validがTrueを返す"""
        assert valid_args.is_valid() is True
    
    def test_is_valid_false(self):
        """is_validがFalseを返す"""
        test_args = ['upload.py']
        with patch.object(sys, 'argv', test_args):
            with patch('logger.Logger.logWarning'):
                args = Arguments()
                assert args.is_valid() is False
    
    def test_get_year(self, valid_args):
        """get_yearで年を取得"""
        assert valid_args.get_year() == 2024
    
    def test_get_month(self, valid_args):
        """get_monthで月を取得"""
        assert valid_args.get_month() == 8
    
    def test_get_kind(self, valid_args):
        """get_kindで給与種別を取得"""
        assert valid_args.get_kind() == SalaryKind.NORMAL


class TestArgumentsDeprecatedMethods:
    """非推奨メソッドのテスト"""
    
    @pytest.fixture
    def valid_args(self):
        """有効な引数を持つArgumentsインスタンス"""
        test_args = ['upload.py', '2025', '1']
        with patch.object(sys, 'argv', test_args):
            return Arguments()
    
    def test_deprecated_isValid(self, valid_args):
        """非推奨メソッドisValid"""
        assert valid_args.isValid() is True
    
    def test_deprecated_getYear(self, valid_args):
        """非推奨メソッドgetYear"""
        assert valid_args.getYear() == 2025
    
    def test_deprecated_getMonth(self, valid_args):
        """非推奨メソッドgetMonth"""
        assert valid_args.getMonth() == 1
    
    def test_deprecated_getKind(self, valid_args):
        """非推奨メソッドgetKind"""
        assert valid_args.getKind() == SalaryKind.NORMAL


class TestArgumentsConstants:
    """Arguments定数のテスト"""
    
    def test_min_args(self):
        """最小引数数"""
        assert Arguments.MIN_ARGS == 3
    
    def test_max_args(self):
        """最大引数数"""
        assert Arguments.MAX_ARGS == 4
    
    def test_usage_example(self):
        """使用例メッセージ"""
        assert "python upload.py" in Arguments.USAGE_EXAMPLE
        assert "2024" in Arguments.USAGE_EXAMPLE
    
    def test_usage_msg_missing(self):
        """引数不足メッセージ"""
        assert "年と月" in Arguments.USAGE_MSG_MISSING
    
    def test_usage_msg_invalid(self):
        """引数不正メッセージ"""
        assert "正しい数値形式" in Arguments.USAGE_MSG_INVALID


class TestArgumentsEdgeCases:
    """Argumentsクラスのエッジケーステスト"""
    
    def test_year_2000(self):
        """西暦2000年のテスト"""
        test_args = ['upload.py', '2000', '1']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.year == 2000
    
    def test_month_january(self):
        """1月のテスト"""
        test_args = ['upload.py', '2024', '1']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.month == 1
    
    def test_month_december(self):
        """12月のテスト"""
        test_args = ['upload.py', '2024', '12']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.month == 12
    
    def test_large_year(self):
        """大きな西暦のテスト"""
        test_args = ['upload.py', '9999', '6']
        with patch.object(sys, 'argv', test_args):
            args = Arguments()
            assert args.year == 9999

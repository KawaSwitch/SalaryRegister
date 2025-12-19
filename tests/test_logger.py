"""
test_logger.py
logger.pyの単体試験

C0, C1, C2カバレッジ100%を目指したテストケース
"""
import pytest
from unittest.mock import patch
from logger import Logger, FColors


class TestFColors:
    """FColors定数クラスのテスト"""
    
    def test_header_color(self):
        """ヘッダーカラーの値"""
        assert FColors.HEADER == "\033[95m"
    
    def test_okblue_color(self):
        """青色の値"""
        assert FColors.OKBLUE == "\033[94m"
    
    def test_okcyan_color(self):
        """シアン色の値"""
        assert FColors.OKCYAN == "\033[96m"
    
    def test_okgreen_color(self):
        """緑色の値"""
        assert FColors.OKGREEN == "\033[92m"
    
    def test_warning_color(self):
        """警告色の値"""
        assert FColors.WARNING == "\033[93m"
    
    def test_fail_color(self):
        """エラー色の値"""
        assert FColors.FAIL == "\033[91m"
    
    def test_endc_color(self):
        """色終了コードの値"""
        assert FColors.ENDC == "\033[0m"
    
    def test_bold(self):
        """太字コードの値"""
        assert FColors.BOLD == "\033[1m"
    
    def test_underline(self):
        """下線コードの値"""
        assert FColors.UNDERLINE == "\033[4m"


class TestLogger:
    """Loggerクラスのテスト"""
    
    @patch('builtins.print')
    def test_log_fine(self, mock_print):
        """logFineメソッドのテスト"""
        Logger.logFine("Test fine message")
        expected = f"{FColors.OKGREEN}[fine] Test fine message{FColors.ENDC}"
        mock_print.assert_called_once_with(expected)
    
    @patch('builtins.print')
    def test_log_info(self, mock_print):
        """logInfoメソッドのテスト"""
        Logger.logInfo("Test info message")
        expected = f"{FColors.OKCYAN}[info] Test info message{FColors.ENDC}"
        mock_print.assert_called_once_with(expected)
    
    @patch('builtins.print')
    def test_log_debug(self, mock_print):
        """logDebugメソッドのテスト"""
        Logger.logDebug("Test debug message")
        expected = f"{FColors.ENDC}[debug] Test debug message{FColors.ENDC}"
        mock_print.assert_called_once_with(expected)
    
    @patch('builtins.print')
    def test_log_warning(self, mock_print):
        """logWarningメソッドのテスト"""
        Logger.logWarning("Test warning message")
        expected = f"{FColors.WARNING}[WARNING] Test warning message{FColors.ENDC}"
        mock_print.assert_called_once_with(expected)
    
    @patch('builtins.print')
    def test_log_error(self, mock_print):
        """logErrorメソッドのテスト"""
        Logger.logError("Test error message")
        expected = f"{FColors.FAIL}[ERROR] Test error message{FColors.ENDC}"
        mock_print.assert_called_once_with(expected)
    
    @patch('builtins.print')
    def test_log_print_with_custom_color(self, mock_print):
        """_log_printメソッドのカスタムカラーテスト"""
        Logger._log_print("Custom message", FColors.HEADER)
        expected = f"{FColors.HEADER}Custom message{FColors.ENDC}"
        mock_print.assert_called_once_with(expected)
    
    @patch('builtins.print')
    def test_log_print_with_default_color(self, mock_print):
        """_log_printメソッドのデフォルトカラーテスト"""
        Logger._log_print("Default color message")
        expected = f"{FColors.ENDC}Default color message{FColors.ENDC}"
        mock_print.assert_called_once_with(expected)
    
    def test_log_level_initial_value(self):
        """log_levelの初期値テスト"""
        assert Logger.log_level == 1
    
    @patch('builtins.print')
    def test_multiple_log_calls(self, mock_print):
        """複数のログ呼び出しのテスト"""
        Logger.logInfo("First message")
        Logger.logWarning("Second message")
        Logger.logError("Third message")
        
        assert mock_print.call_count == 3
    
    @patch('builtins.print')
    def test_log_with_empty_string(self, mock_print):
        """空文字列のログテスト"""
        Logger.logInfo("")
        expected = f"{FColors.OKCYAN}[info] {FColors.ENDC}"
        mock_print.assert_called_once_with(expected)
    
    @patch('builtins.print')
    def test_log_with_special_characters(self, mock_print):
        """特殊文字を含むログテスト"""
        message = "テスト\nメッセージ\t改行付き"
        Logger.logInfo(message)
        expected = f"{FColors.OKCYAN}[info] {message}{FColors.ENDC}"
        mock_print.assert_called_once_with(expected)

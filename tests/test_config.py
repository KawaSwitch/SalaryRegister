"""
test_config.py
config.pyの単体試験

C0, C1, C2カバレッジ100%を目指したテストケース
"""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from config import Config


class TestConfigInitialization:
    """Configクラスの初期化テスト"""
    
    def test_init_loads_config(self):
        """初期化時に設定ファイルが読み込まれる"""
        with patch.object(Config, '_load_config') as mock_load:
            config = Config()
            mock_load.assert_called_once()
    
    def test_config_parser_created(self):
        """ConfigParserインスタンスが作成される"""
        with patch.object(Config, '_load_config'):
            config = Config()
            assert config.config is not None


class TestConfigLoadConfig:
    """_load_configメソッドのテスト"""
    
    def test_load_config_success(self):
        """設定ファイルの読み込み成功"""
        # 一時ディレクトリと設定ファイルを作成
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.ini")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write("[DEFAULT]\n")
                f.write("PdfPassword=test123\n")
                f.write("MfMailAddress=test@example.com\n")
                f.write("MfPassword=pass456\n")
                f.write("EmployeeNumber=12345\n")
                f.write("UseHeadlessMode=true\n")
                f.write("DefaultDate=25\n")
                f.write("TfaId=ABCD1234\n")
            
            with patch.object(Config, 'USERDATA_DIR', tmpdir):
                config = Config()
                assert config.config is not None
    
    def test_load_config_file_not_found(self):
        """設定ファイルが見つからない場合"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Config, 'USERDATA_DIR', tmpdir):
                with pytest.raises(FileNotFoundError) as exc_info:
                    Config()
                assert "設定ファイルが見つかりません" in str(exc_info.value)


class TestConfigGetters:
    """各getterメソッドのテスト"""
    
    @pytest.fixture
    def config_with_mock_data(self):
        """モックデータを持つConfigインスタンスを作成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.ini")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write("[DEFAULT]\n")
                f.write("PdfPassword=pdf_pass123\n")
                f.write("MfMailAddress=user@example.com\n")
                f.write("MfPassword=mf_pass456\n")
                f.write("EmployeeNumber=98765\n")
                f.write("UseHeadlessMode=TRUE\n")
                f.write("DefaultDate=15\n")
                f.write("TfaId=TESTID123\n")
            
            with patch.object(Config, 'USERDATA_DIR', tmpdir):
                yield Config()
    
    def test_get_pdf_password(self, config_with_mock_data):
        """PDFパスワードの取得"""
        assert config_with_mock_data.get_pdf_password() == "pdf_pass123"
    
    def test_get_moneyforward_email(self, config_with_mock_data):
        """MoneyForwardメールアドレスの取得"""
        assert config_with_mock_data.get_moneyforward_email() == "user@example.com"
    
    def test_get_moneyforward_password(self, config_with_mock_data):
        """MoneyForwardパスワードの取得"""
        assert config_with_mock_data.get_moneyforward_password() == "mf_pass456"
    
    def test_get_employee_number(self, config_with_mock_data):
        """従業員番号の取得"""
        assert config_with_mock_data.get_employee_number() == "98765"
    
    def test_is_headless_mode_true(self, config_with_mock_data):
        """ヘッドレスモードがTRUEの場合"""
        assert config_with_mock_data.is_headless_mode() is True
    
    def test_get_default_date(self, config_with_mock_data):
        """デフォルト日付の取得"""
        assert config_with_mock_data.get_default_date() == "15"
    
    def test_get_tfa_id(self, config_with_mock_data):
        """2段階認証IDの取得"""
        assert config_with_mock_data.get_tfa_id() == "TESTID123"


class TestConfigHeadlessMode:
    """ヘッドレスモードの各種設定値テスト"""
    
    def create_config_with_headless(self, value: str):
        """指定されたヘッドレスモード値でConfigを作成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.ini")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write("[DEFAULT]\n")
                f.write("PdfPassword=test\n")
                f.write("MfMailAddress=test@test.com\n")
                f.write("MfPassword=test\n")
                f.write("EmployeeNumber=12345\n")
                f.write(f"UseHeadlessMode={value}\n")
                f.write("DefaultDate=25\n")
                f.write("TfaId=TEST\n")
            
            with patch.object(Config, 'USERDATA_DIR', tmpdir):
                return Config()
    
    def test_headless_mode_false_lower(self):
        """ヘッドレスモードがfalseの場合（小文字）"""
        config = self.create_config_with_headless("false")
        assert config.is_headless_mode() is False
    
    def test_headless_mode_false_upper(self):
        """ヘッドレスモードがFALSEの場合（大文字）"""
        config = self.create_config_with_headless("FALSE")
        assert config.is_headless_mode() is False
    
    def test_headless_mode_true_lower(self):
        """ヘッドレスモードがtrueの場合（小文字）"""
        config = self.create_config_with_headless("true")
        assert config.is_headless_mode() is True
    
    def test_headless_mode_yes(self):
        """ヘッドレスモードがyesの場合"""
        config = self.create_config_with_headless("yes")
        assert config.is_headless_mode() is True
    
    def test_headless_mode_no(self):
        """ヘッドレスモードがnoの場合"""
        config = self.create_config_with_headless("no")
        assert config.is_headless_mode() is False


class TestConfigDeprecatedMethods:
    """非推奨メソッドのテスト"""
    
    @pytest.fixture
    def config_with_mock_data(self):
        """モックデータを持つConfigインスタンスを作成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "config.ini")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write("[DEFAULT]\n")
                f.write("PdfPassword=pdf123\n")
                f.write("MfMailAddress=old@example.com\n")
                f.write("MfPassword=oldpass\n")
                f.write("EmployeeNumber=11111\n")
                f.write("UseHeadlessMode=true\n")
                f.write("DefaultDate=10\n")
                f.write("TfaId=OLDID\n")
            
            with patch.object(Config, 'USERDATA_DIR', tmpdir):
                yield Config()
    
    def test_deprecated_getPdfPassword(self, config_with_mock_data):
        """非推奨メソッドgetPdfPassword"""
        assert config_with_mock_data.getPdfPassword() == "pdf123"
    
    def test_deprecated_getMoneyForwardId(self, config_with_mock_data):
        """非推奨メソッドgetMoneyForwardId"""
        assert config_with_mock_data.getMoneyForwardId() == "old@example.com"
    
    def test_deprecated_getMoneyForwardPassword(self, config_with_mock_data):
        """非推奨メソッドgetMoneyForwardPassword"""
        assert config_with_mock_data.getMoneyForwardPassword() == "oldpass"
    
    def test_deprecated_getEmployeeNumber(self, config_with_mock_data):
        """非推奨メソッドgetEmployeeNumber"""
        assert config_with_mock_data.getEmployeeNumber() == "11111"
    
    def test_deprecated_isHeadlessMode(self, config_with_mock_data):
        """非推奨メソッドisHeadlessMode"""
        assert config_with_mock_data.isHeadlessMode() is True
    
    def test_deprecated_getDefaultDate(self, config_with_mock_data):
        """非推奨メソッドgetDefaultDate"""
        assert config_with_mock_data.getDefaultDate() == "10"
    
    def test_deprecated_getTfaId(self, config_with_mock_data):
        """非推奨メソッドgetTfaId"""
        assert config_with_mock_data.getTfaId() == "OLDID"


class TestConfigConstants:
    """Config定数のテスト"""
    
    def test_section_default(self):
        """DEFAULTセクション名"""
        assert Config.DEFAULT == "DEFAULT"
    
    def test_key_pdf_password(self):
        """PDFパスワードキー"""
        assert Config.KEY_PDF_PASSWORD == "PdfPassword"
    
    def test_key_mf_mail(self):
        """MFメールアドレスキー"""
        assert Config.KEY_MF_MAIL == "MfMailAddress"
    
    def test_key_mf_password(self):
        """MFパスワードキー"""
        assert Config.KEY_MF_PASSWORD == "MfPassword"
    
    def test_key_employee_number(self):
        """従業員番号キー"""
        assert Config.KEY_EMPLOYEE_NUMBER == "EmployeeNumber"
    
    def test_key_headless_mode(self):
        """ヘッドレスモードキー"""
        assert Config.KEY_HEADLESS_MODE == "UseHeadlessMode"
    
    def test_key_default_date(self):
        """デフォルト日付キー"""
        assert Config.KEY_DEFAULT_DATE == "DefaultDate"
    
    def test_key_tfa_id(self):
        """2段階認証IDキー"""
        assert Config.KEY_TFA_ID == "TfaId"
    
    def test_userdata_dir(self):
        """ユーザデータディレクトリパス"""
        assert Config.USERDATA_DIR == "../userdata"
    
    def test_config_filename(self):
        """設定ファイル名"""
        assert Config.CONFIG_FILENAME == "config.ini"

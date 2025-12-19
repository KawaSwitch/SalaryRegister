"""
test_uploader.py
uploader.pyの単体試験

C0, C1, C2カバレッジ100%を目指したテストケース
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
from uploader import Uploader
from salary import Salary
from item import Item
from common import SalaryKind
import config


@pytest.fixture(autouse=True)
def mock_config(mocker):
    """config.dataのモックを作成"""
    mock_data = MagicMock()
    mock_data.get_moneyforward_email.return_value = "test@example.com"
    mock_data.get_moneyforward_password.return_value = "testpass"
    mock_data.get_tfa_id.return_value = "tfa123"
    mock_data.get_default_date.return_value = "2024/11/25"
    mock_data.is_headless_mode.return_value = False
    mocker.patch.object(config, 'data', mock_data)
    return mock_data


class TestUploaderInitialization:
    """Uploaderクラスの初期化テスト"""
    
    @patch('uploader.config.data.get_moneyforward_email', return_value="test@example.com")
    @patch('uploader.config.data.get_moneyforward_password', return_value="password123")
    @patch('uploader.config.data.get_tfa_id', return_value="TFA123")
    def test_init_with_salary(self, mock_tfa, mock_pw, mock_email):
        """給与情報での初期化"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        assert uploader.salary == mock_salary
        assert uploader.email == "test@example.com"
        assert uploader.pw == "password123"
        assert uploader.tfaid == "TFA123"
        assert uploader.driver is None
        assert uploader.actions is None


class TestConfirmRegistration:
    """_confirm_registrationメソッドのテスト"""
    
    @patch('uploader.config.data.get_default_date', return_value="25")
    def test_confirm_registration_yes(self, mock_default):
        """登録確認でYesを入力"""
        mock_salary = MagicMock(spec=Salary)
        mock_salary.set_date.return_value = True
        mock_salary.get_payday.return_value = "2024/11/25"
        
        uploader = Uploader(mock_salary)
        
        with patch('builtins.input', side_effect=["25", "Y"]):
            result = uploader._confirm_registration()
            
            assert result is True
            mock_salary.set_date.assert_called_once_with("25")
    
    @patch('uploader.config.data.get_default_date', return_value="25")
    def test_confirm_registration_default(self, mock_default):
        """登録確認でデフォルト（Enter）を入力"""
        mock_salary = MagicMock(spec=Salary)
        mock_salary.set_date.return_value = True
        mock_salary.get_payday.return_value = "2024/11/25"
        
        uploader = Uploader(mock_salary)
        
        with patch('builtins.input', side_effect=["", ""]):
            result = uploader._confirm_registration()
            
            assert result is True
    
    @patch('uploader.config.data.get_default_date', return_value="25")
    def test_confirm_registration_cancel(self, mock_default):
        """登録確認でキャンセル"""
        mock_salary = MagicMock(spec=Salary)
        mock_salary.set_date.return_value = True
        mock_salary.get_payday.return_value = "2024/11/25"
        
        uploader = Uploader(mock_salary)
        
        with patch('builtins.input', side_effect=["25", "n"]):
            result = uploader._confirm_registration()
            
            assert result is False
    
    @patch('uploader.config.data.get_default_date', return_value="25")
    def test_confirm_registration_invalid_date(self, mock_default):
        """無効な日付入力"""
        mock_salary = MagicMock(spec=Salary)
        mock_salary.set_date.return_value = False
        
        uploader = Uploader(mock_salary)
        
        with patch('builtins.input', return_value="99"):
            with patch('uploader.Logger.logError'):
                result = uploader._confirm_registration()
                
                assert result is False


class TestInitWebdriver:
    """_init_webdriverメソッドのテスト"""
    
    @patch('uploader.config.data.is_headless_mode', return_value=False)
    @patch('uploader.webdriver.Chrome')
    @patch('uploader.ActionChains')
    def test_init_webdriver_normal_mode(self, mock_actions, mock_chrome, mock_headless):
        """通常モードでのWebDriver初期化"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        with patch('uploader.Logger.logFine'):
            uploader._init_webdriver()
            
            assert uploader.driver == mock_driver
            mock_chrome.assert_called_once()
            mock_driver.implicitly_wait.assert_called_once()
            mock_driver.set_window_size.assert_called_once()
    
    @patch('uploader.config.data.is_headless_mode', return_value=True)
    @patch('uploader.webdriver.Chrome')
    @patch('uploader.ActionChains')
    def test_init_webdriver_headless_mode(self, mock_actions, mock_chrome, mock_headless):
        """ヘッドレスモードでのWebDriver初期化"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        with patch('uploader.Logger.logFine'):
            uploader._init_webdriver()
            
            assert uploader.driver == mock_driver
    
    @patch('uploader.config.data.is_headless_mode', return_value=False)
    @patch('uploader.webdriver.Chrome')
    def test_init_webdriver_failure(self, mock_chrome, mock_headless):
        """WebDriver初期化失敗"""
        mock_chrome.side_effect = Exception("Driver error")
        
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        with pytest.raises(Exception) as exc_info:
            uploader._init_webdriver()
        
        assert "WebDriverの初期化に失敗しました" in str(exc_info.value)


class TestAddHeadlessSettings:
    """_add_headless_settingsメソッドのテスト"""
    
    def test_add_headless_settings(self):
        """ヘッドレス設定の追加"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_options = MagicMock()
        result = uploader._add_headless_settings(mock_options)
        
        assert result == mock_options
        assert mock_options.add_argument.call_count >= 2


class TestAccessMoneyforward:
    """_access_moneyforwardメソッドのテスト"""
    
    def test_access_moneyforward(self):
        """MoneyForwardへのアクセス"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_driver = MagicMock()
        uploader.driver = mock_driver
        
        with patch('uploader.Logger.logFine'):
            uploader._access_moneyforward()
            
            mock_driver.get.assert_called_once_with(Uploader.MONEYFORWARD_URL)
            mock_driver.implicitly_wait.assert_called_once()


class TestSetIncomeExpenseType:
    """_set_income_expense_typeメソッドのテスト"""
    
    def test_set_income_expense_type_income(self):
        """収入として設定"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_driver = MagicMock()
        uploader.driver = mock_driver
        
        uploader._set_income_expense_type(is_income=True)
        
        mock_driver.execute_script.assert_called_once()
        call_args = mock_driver.execute_script.call_args[0][0]
        assert "value = '1'" in call_args
    
    def test_set_income_expense_type_expense(self):
        """支出として設定"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_driver = MagicMock()
        uploader.driver = mock_driver
        
        uploader._set_income_expense_type(is_income=False)
        
        mock_driver.execute_script.assert_called_once()
        call_args = mock_driver.execute_script.call_args[0][0]
        assert "value = '0'" in call_args


class TestSetSubAccount:
    """_set_sub_accountメソッドのテスト"""
    
    def test_set_sub_account(self):
        """サブアカウントの設定"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_wait = MagicMock()
        mock_element = MagicMock()
        mock_wait.until.return_value = mock_element
        
        with patch('uploader.Select') as mock_select:
            uploader._set_sub_account(mock_wait)
            
            mock_select.assert_called_once_with(mock_element)
            mock_select.return_value.select_by_visible_text.assert_called_once_with("なし")


class TestSetAmount:
    """_set_amountメソッドのテスト"""
    
    def test_set_amount_positive(self):
        """正の金額の設定"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_wait = MagicMock()
        mock_element = MagicMock()
        mock_wait.until.return_value = mock_element
        
        uploader._set_amount(mock_wait, 10000)
        
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with("10000")
    
    def test_set_amount_negative(self):
        """負の金額の設定（絶対値に変換）"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_wait = MagicMock()
        mock_element = MagicMock()
        mock_wait.until.return_value = mock_element
        
        uploader._set_amount(mock_wait, -5000)
        
        mock_element.send_keys.assert_called_once_with("5000")


class TestSetContent:
    """_set_contentメソッドのテスト"""
    
    def test_set_content(self):
        """内容の設定"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_wait = MagicMock()
        mock_element = MagicMock()
        mock_wait.until.return_value = mock_element
        
        uploader._set_content(mock_wait, "健康保険")
        
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with("健康保険")


class TestSetDate:
    """_set_dateメソッドのテスト"""
    
    def test_set_date(self):
        """日付の設定"""
        mock_salary = MagicMock(spec=Salary)
        mock_salary.get_payday.return_value = "2024/11/25"
        uploader = Uploader(mock_salary)
        
        mock_wait = MagicMock()
        mock_element = MagicMock()
        mock_wait.until.return_value = mock_element
        
        uploader._set_date(mock_wait)
        
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with("2024/11/25")


class TestConfirmIncomeExpenseField:
    """_confirm_income_expense_fieldメソッドのテスト"""
    
    def test_confirm_income_expense_field_income(self):
        """収入フィールドの確認"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_driver = MagicMock()
        uploader.driver = mock_driver
        
        uploader._confirm_income_expense_field(is_income=True)
        
        mock_driver.execute_script.assert_called_once()
        call_args = mock_driver.execute_script.call_args[0][0]
        assert "value = '1'" in call_args
    
    def test_confirm_income_expense_field_expense(self):
        """支出フィールドの確認"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_driver = MagicMock()
        uploader.driver = mock_driver
        
        uploader._confirm_income_expense_field(is_income=False)
        
        call_args = mock_driver.execute_script.call_args[0][0]
        assert "value = '0'" in call_args


class TestSaveDebugHtml:
    """_save_debug_htmlメソッドのテスト"""
    
    def test_save_debug_html(self):
        """デバッグHTMLの保存"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_driver = MagicMock()
        mock_driver.page_source = "<html>test</html>"
        uploader.driver = mock_driver
        
        m = mock_open()
        with patch('builtins.open', m):
            uploader._save_debug_html("test.html")
            
            m.assert_called_once_with("test.html", "w", encoding="utf-8")
            m().write.assert_called_once_with("<html>test</html>")


class TestSaveDebugScreenshot:
    """_save_debug_screenshotメソッドのテスト"""
    
    def test_save_debug_screenshot(self):
        """デバッグスクリーンショットの保存"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_driver = MagicMock()
        mock_driver.page_source = "<html>test</html>"
        uploader.driver = mock_driver
        
        with patch('builtins.open', mock_open()):
            with patch('uploader.Logger.logInfo'):
                uploader._save_debug_screenshot()
                
                mock_driver.save_screenshot.assert_called_once()


class TestCloseModalIfPresent:
    """_close_modal_if_presentメソッドのテスト"""
    
    def test_close_modal_present(self):
        """モーダルが表示されている場合"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_driver = MagicMock()
        mock_button = MagicMock()
        mock_button.is_displayed.return_value = True
        mock_driver.find_elements.return_value = [mock_button]
        uploader.driver = mock_driver
        
        with patch('time.sleep'):
            uploader._close_modal_if_present()
            
            mock_button.click.assert_called_once()
    
    def test_close_modal_not_present(self):
        """モーダルが表示されていない場合"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_driver = MagicMock()
        mock_driver.find_elements.return_value = []
        uploader.driver = mock_driver
        
        # 例外が発生しないことを確認
        uploader._close_modal_if_present()


class TestUploaderConstants:
    """Uploaderクラスの定数テスト"""
    
    def test_moneyforward_url(self):
        """MoneyForward URL"""
        assert Uploader.MONEYFORWARD_URL == "https://moneyforward.com"
    
    def test_option_none(self):
        """なしオプション"""
        assert Uploader.OPTION_NONE == "なし"
    
    def test_link_text_login(self):
        """ログインリンクテキスト"""
        assert Uploader.LINK_TEXT_LOGIN == "ログイン"
    
    def test_link_text_input(self):
        """入力リンクテキスト"""
        assert Uploader.LINK_TEXT_INPUT == "収入・振替を入力する"
    
    def test_msg_confirm_registration(self):
        """登録確認メッセージ"""
        assert "登録日を入力" in Uploader.MSG_CONFIRM_REGISTRATION
    
    def test_msg_cancelled(self):
        """キャンセルメッセージ"""
        assert "キャンセル" in Uploader.MSG_CANCELLED
    
    def test_msg_invalid_date(self):
        """無効日付メッセージ"""
        assert "誤っています" in Uploader.MSG_INVALID_DATE


class TestDeprecatedMethods:
    """非推奨メソッドのテスト"""
    
    def test_deprecated_registerInternal(self):
        """非推奨メソッドregisterInternal"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        mock_item = Item("テスト", 1000)
        
        with patch.object(uploader, '_register_item_internal') as mock_register:
            uploader.registerInternal(mock_item, is_income=True)
            
            # 位置引数として渡されることを確認
            mock_register.assert_called_once_with(mock_item, True)


class TestUploadEdgeCases:
    """Uploaderクラスのエッジケーステスト"""
    
    @patch('uploader.config.data.get_default_date', return_value="25")
    def test_upload_cancelled_by_user(self, mock_default):
        """ユーザーによる登録キャンセル"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        with patch.object(uploader, '_confirm_registration', return_value=False):
            uploader.upload()
            
            # キャンセルされたので何も実行されない
            assert uploader.driver is None


class TestUploaderFullCoverage:
    """Uploaderクラスの完全カバレッジテスト"""
    
    def test_upload_full_flow(self):
        """upload完全フロー"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        with patch.object(uploader, '_confirm_registration', return_value=True), \
             patch.object(uploader, '_init_webdriver'), \
             patch.object(uploader, '_access_moneyforward'), \
             patch.object(uploader, '_login'), \
             patch.object(uploader, '_register_deductions'):
            
            uploader.upload()
            
            uploader._confirm_registration.assert_called_once()
            uploader._init_webdriver.assert_called_once()
            uploader._access_moneyforward.assert_called_once()
            uploader._login.assert_called_once()
            uploader._register_deductions.assert_called_once()
    
    def test_upload_with_exception_cleanup(self):
        """upload例外時のクリーンアップ"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        uploader.driver = MagicMock()
        
        with patch.object(uploader, '_confirm_registration', return_value=True), \
             patch.object(uploader, '_init_webdriver'), \
             patch.object(uploader, '_access_moneyforward', side_effect=Exception("Test error")), \
             pytest.raises(Exception):
            
            uploader.upload()
            
        # driverがquit()されることを確認
        uploader.driver.quit.assert_called_once()
    
    @patch('uploader.webdriver.Chrome')
    @patch('uploader.webdriver.ChromeOptions')
    def test_login_full_flow(self, mock_options_class, mock_chrome):
        """ログイン完全フロー"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        
        # WebDriver mock
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        uploader.driver = mock_driver
        uploader.actions = MagicMock()
        
        # WebDriverWait mock
        mock_wait = MagicMock()
        mock_menu = MagicMock()
        mock_login_link = MagicMock()
        mock_email_elem = MagicMock()
        mock_pw_elem = MagicMock()
        mock_otp_elem = MagicMock()
        
        with patch('uploader.WebDriverWait', return_value=mock_wait), \
             patch('uploader.EC'), \
             patch('uploader.time.sleep'), \
             patch('uploader.pyotp.TOTP') as mock_totp:
            
            mock_totp_instance = MagicMock()
            mock_totp_instance.now.return_value = "123456"
            mock_totp.return_value = mock_totp_instance
            
            mock_wait.until.side_effect = [
                mock_menu,      # main menu
                mock_login_link,  # login link
                mock_email_elem,  # email field
                mock_pw_elem,     # password field
                mock_otp_elem     # OTP field
            ]
            
            uploader._login()
            
            uploader.actions.move_to_element.assert_called_once_with(mock_menu)
            mock_login_link.click.assert_called_once()
            mock_email_elem.send_keys.assert_called_once()
            mock_pw_elem.send_keys.assert_called_once()
            mock_otp_elem.send_keys.assert_called_once_with("123456")
    
    @patch('uploader.time.sleep')
    def test_register_deductions_full_flow(self, mock_sleep):
        """控除登録完全フロー"""
        mock_salary = MagicMock(spec=Salary)
        mock_item1 = Item("健康保険", 10000)
        mock_item2 = Item("厚生年金", 20000)
        mock_salary.deductionItems = [mock_item1, mock_item2]
        
        uploader = Uploader(mock_salary)
        uploader.driver = MagicMock()
        
        with patch.object(uploader, '_close_modal_if_present'), \
             patch.object(uploader, '_navigate_to_input_page'), \
             patch.object(uploader, '_register_deduction_sum_as_income'), \
             patch.object(uploader, '_register_deduction_items'), \
             patch('uploader.Logger'):
            
            uploader._register_deductions()
            
            uploader._close_modal_if_present.assert_called_once()
            uploader._navigate_to_input_page.assert_called_once()
            uploader._register_deduction_sum_as_income.assert_called_once()
            uploader._register_deduction_items.assert_called_once()
    
    @patch('uploader.Logger')
    def test_navigate_to_input_page(self, mock_logger):
        """入力ページへの遷移"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        uploader.driver = MagicMock()
        
        with patch('uploader.WebDriverWait') as mock_wait_class, \
             patch('uploader.EC'):
            mock_wait = MagicMock()
            mock_wait_class.return_value = mock_wait
            mock_input_link = MagicMock()
            mock_wait.until.return_value = mock_input_link
            
            try:
                uploader._navigate_to_input_page()
            except Exception:
                pass
            
            # WebDriverWaitが呼ばれたことを確認
            mock_wait_class.assert_called()
    
    @patch('uploader.WebDriverWait')
    def test_register_item_internal_income(self, mock_wait_class):
        """項目登録（収入）"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        uploader.driver = MagicMock()
        
        mock_item = Item("給与", 300000)
        
        with patch.object(uploader, '_set_income_expense_type'), \
             patch.object(uploader, '_set_sub_account'), \
             patch.object(uploader, '_set_amount'), \
             patch.object(uploader, '_set_categories'), \
             patch.object(uploader, '_set_content'), \
             patch.object(uploader, '_set_date'), \
             patch.object(uploader, '_confirm_income_expense_field'), \
             patch.object(uploader, '_submit_and_continue'), \
             patch.object(uploader, '_save_debug_screenshot'):
            
            uploader._register_item_internal(mock_item, True)
            
            uploader._set_income_expense_type.assert_called_once_with(True)
            uploader._set_sub_account.assert_called_once()
            uploader._confirm_income_expense_field.assert_called_once_with(True)
            uploader._submit_and_continue.assert_called_once()
    
    @patch('uploader.WebDriverWait')
    def test_register_item_internal_expense(self, mock_wait_class):
        """項目登録（支出）"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        uploader.driver = MagicMock()
        
        mock_item = Item("健康保険", 10000)
        
        with patch.object(uploader, '_set_income_expense_type'), \
             patch.object(uploader, '_set_sub_account'), \
             patch.object(uploader, '_set_amount'), \
             patch.object(uploader, '_set_categories'), \
             patch.object(uploader, '_set_content'), \
             patch.object(uploader, '_set_date'), \
             patch.object(uploader, '_confirm_income_expense_field'), \
             patch.object(uploader, '_submit_and_continue'), \
             patch.object(uploader, '_save_debug_screenshot'):
            
            uploader._register_item_internal(mock_item, False)
            
            uploader._set_income_expense_type.assert_called_once_with(False)
            uploader._set_sub_account.assert_called_once()
            uploader._confirm_income_expense_field.assert_called_once_with(False)
            uploader._submit_and_continue.assert_called_once()
    
    def test_close_modal_present_and_not_present(self):
        """モーダルの表示有無テスト"""
        mock_salary = MagicMock(spec=Salary)
        uploader = Uploader(mock_salary)
        uploader.driver = MagicMock()
        
        mock_button = MagicMock()
        mock_button.is_displayed.return_value = True
        uploader.driver.find_elements.return_value = [mock_button]
        
        with patch('uploader.time.sleep'):
            uploader._close_modal_if_present()
            mock_button.click.assert_called_once()
        
        # モーダルが存在しない場合
        uploader.driver.find_elements.return_value = []
        uploader._close_modal_if_present()  # 例外が発生しないこと

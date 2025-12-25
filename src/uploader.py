import time
from typing import Final

from logger import Logger
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from salary import Salary
from item import Item
from common import UIConstants, ItemNames
import config
import pyotp


class Uploader:
    """
    MoneyForwardへの給与情報アップロードを行うクラス
    """
    
    # URL定数
    MONEYFORWARD_URL: Final[str] = "https://moneyforward.com"
    
    # XPath定数
    XPATH_MAIN_MENU: Final[str] = '//*[@id="before-login-corporate"]/header/div[1]/div[2]/nav/ul/li[1]/p'
    
    # セレクタ定数
    ID_EMAIL: Final[str] = "mfid_user[email]"
    ID_PASSWORD: Final[str] = "mfid_user[password]"
    ID_OTP: Final[str] = "otp_attempt"
    ID_SUB_ACCOUNT: Final[str] = "user_asset_act_sub_account_id_hash"
    ID_AMOUNT: Final[str] = "appendedPrependedInput"
    ID_LARGE_CATEGORY: Final[str] = "js-large-category-selected"
    ID_MIDDLE_CATEGORY: Final[str] = "js-middle-category-selected"
    ID_CONTENT: Final[str] = "js-content-field"
    ID_DATE: Final[str] = "updated-at"
    ID_IS_INCOME: Final[str] = "user_asset_act_is_income"
    ID_IS_INCOME_MODAL: Final[str] = "user_asset_act_is_income_modal"
    ID_CONFIRMATION_BTN: Final[str] = "confirmation-button"
    
    CLASS_MINUS_PAYMENT: Final[str] = "minus-payment"
    CLASS_PLUS_PAYMENT: Final[str] = "plus-payment"
    
    LINK_TEXT_LOGIN: Final[str] = "ログイン"
    LINK_TEXT_INPUT: Final[str] = "収入・振替を入力する"
    
    # 選択オプション
    OPTION_NONE: Final[str] = "なし"
    
    # デバッグファイルパス
    DEBUG_HTML_PATH: Final[str] = "../userdata/debug_page.html"
    DEBUG_SCREENSHOT_PATH: Final[str] = "../userdata/debug_screenshot.png"
    DEBUG_FORM_HTML_PATH: Final[str] = "../userdata/debug_form.html"
    
    # メッセージ
    MSG_CONFIRM_REGISTRATION: Final[str] = "MoneyForwardへの給与登録を行います。登録日を入力してください。"
    MSG_CONFIRM_PAYDAY: Final[str] = "{payday}を給料日として登録します。よろしいですか。(Y/n): "
    MSG_CANCELLED: Final[str] = "給与登録をキャンセルしました。"
    MSG_INVALID_DATE: Final[str] = "指定された日付は誤っています。正しい日付を入力してください。"

    def __init__(self, salary: Salary) -> None:
        """
        Uploaderの初期化
        
        Args:
            salary: 登録する給与情報
        """
        self.salary = salary
        self.email = config.data.get_moneyforward_email()
        self.pw = config.data.get_moneyforward_password()
        self.tfaid = config.data.get_tfa_id()
        self.driver = None
        self.actions = None

    def upload(self, is_deduction_only: bool = True) -> None:
        """
        給与情報をMoneyForwardへアップロードする
        
        Args:
            is_deduction_only: 給与控除のみを対象とするか
        """
        if not self._confirm_registration():
            return

        try:
            self._init_webdriver()
            self._access_moneyforward()
            self._login()
            self._register_deductions()
        finally:
            if self.driver:
                self.driver.quit()

        # MEMO: 現状は控除項目のみで問題なし
        # 将来的に総支給等も登録する場合はここで実装

    def _confirm_registration(self) -> bool:
        """
        給与登録の確認を行います
        
        Returns:
            登録を続行する場合True、キャンセルする場合False
        """
        default_date = config.data.get_default_date()
        date_input = input(f"{self.MSG_CONFIRM_REGISTRATION}({default_date}日): ") or default_date

        if not self.salary.set_date(date_input):
            Logger.logError(self.MSG_INVALID_DATE)
            return False
        
        payday = self.salary.get_payday()
        answer = input(self.MSG_CONFIRM_PAYDAY.format(payday=payday))
        
        if answer in ["", "Y"]:
            return True
        else:
            print(self.MSG_CANCELLED)
            return False

    def _init_webdriver(self) -> None:
        """
        WebDriverの初期化を行います
        
        Raises:
            Exception: WebDriverの初期化に失敗した場合
        """
        Logger.logFine("WebDriverの初期化を行います。")
        
        try:
            options = webdriver.ChromeOptions()
            
            if config.data.is_headless_mode():
                options = self._add_headless_settings(options)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(UIConstants.DEFAULT_WAIT_TIMEOUT)
            self.driver.set_window_size(
                UIConstants.WINDOW_WIDTH, 
                UIConstants.WINDOW_HEIGHT
            )
            self.actions = ActionChains(self.driver)
            
            Logger.logFine("WebDriverの初期化に成功しました。")
        except Exception as e:
            if self.driver:
                self.driver.quit()
            raise Exception(f"WebDriverの初期化に失敗しました: {str(e)}")

    def _add_headless_settings(self, options: webdriver.ChromeOptions) -> webdriver.ChromeOptions:
        """
        ヘッドレスモード(画面非表示)の設定を追加する
        
        Args:
            options: Chromeオプション
            
        Returns:
            ヘッドレス設定を追加したChromeオプション
            
        Note:
            ヘッドレスモード対策の回避用にUAオプションを追加
            参考: Stack Overflow - How to access a site via a headless driver
            without being denied permission
            URL: https://stackoverflow.com/questions/54432980/
        """
        options.add_argument("--headless=new")
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_argument(f"user-agent={user_agent}")
        # ヘッドレスモードでの安定性向上のための追加オプション
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        return options

    def _access_moneyforward(self) -> None:
        """Webページへのアクセスを行います"""
        Logger.logFine("MoneyForwardのページにアクセスしています。")
        self.driver.get(self.MONEYFORWARD_URL)
        self.driver.implicitly_wait(10)
        Logger.logFine("MoneyForwardのページにアクセス完了しました。")

    def _login(self) -> None:
        """MoneyForwardMeサービスへのログインを行います"""
        Logger.logInfo("ログインしています。")
        wait = WebDriverWait(self.driver, UIConstants.DEFAULT_WAIT_TIMEOUT)

        # 初期ページ > ログイン遷移
        main_menu = wait.until(
            EC.presence_of_element_located((By.XPATH, self.XPATH_MAIN_MENU))
        )
        self.actions.move_to_element(main_menu).perform()
        login_link = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, self.LINK_TEXT_LOGIN))
        )
        login_link.click()

        # ユーザ名
        elem = wait.until(EC.presence_of_element_located((By.ID, self.ID_EMAIL)))
        elem.send_keys(self.email)
        elem.submit()
        Logger.logFine("ユーザID認証に成功しました。")

        # パスワード
        elem = wait.until(EC.presence_of_element_located((By.ID, self.ID_PASSWORD)))
        elem.send_keys(self.pw)
        elem.submit()
        Logger.logFine("パスワード認証に成功しました。")

        # 2段階認証
        elem = wait.until(EC.presence_of_element_located((By.ID, self.ID_OTP)))
        totp = pyotp.TOTP(self.tfaid)
        elem.send_keys(totp.now())
        elem.submit()
        time.sleep(UIConstants.MEDIUM_SLEEP)

        Logger.logInfo("ログインが完了しました。")

    def _register_deductions(self) -> None:
        """給与控除の登録を行います"""
        Logger.logInfo("控除項目の登録を行います。")

        time.sleep(UIConstants.LONG_SLEEP)
        
        # モーダルを閉じる（高速化）
        self._close_modal_if_present()
        
        # 給与登録ページへ遷移
        self._navigate_to_input_page()

        # 控除合計→控除項目の順に登録
        self._register_deduction_sum_as_income()
        self._register_deduction_items()

        Logger.logInfo("すべての控除項目の登録が完了しました。")
    
    def _close_modal_if_present(self) -> None:
        """モーダルダイアログが表示されている場合は閉じる"""
        try:
            close_buttons = self.driver.find_elements(
                By.XPATH, 
                "//button[contains(@class, 'close') or contains(@aria-label, 'Close')]"
            )
            if close_buttons and close_buttons[0].is_displayed():
                close_buttons[0].click()
                time.sleep(UIConstants.SHORT_SLEEP)
        except Exception:
            # モーダルが存在しない場合は無視
            pass
    
    def _navigate_to_input_page(self) -> None:
        """給与入力ページへ遷移する"""
        try:
            wait = WebDriverWait(self.driver, UIConstants.DEFAULT_WAIT_TIMEOUT)
            
            # まず /cf ページにアクセス
            cf_url = "https://moneyforward.com/cf"
            Logger.logFine(f"/cfページへアクセス: {cf_url}")
            self.driver.get(cf_url)
            time.sleep(UIConstants.LONG_SLEEP)
            
            Logger.logFine(f"現在のURL: {self.driver.current_url}")
            
            # 手入力ボタンをクリックしてモーダルを開く
            modal_opened = False
            
            # 方法1: 手入力ボタンをクリック
            try:
                manual_input_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cf-new-btn.modal-switch"))
                )
                # クリック前に少し待機
                time.sleep(UIConstants.SHORT_SLEEP)
                self.driver.execute_script("arguments[0].click();", manual_input_btn)
                time.sleep(UIConstants.LONG_SLEEP)
                Logger.logFine("手入力ボタンをクリックしました。")
                
                # Bootstrap モーダルを明示的に表示
                self.driver.execute_script("""
                    if (typeof $ !== 'undefined' && $('#user_asset_act_new').length > 0) {
                        $('#user_asset_act_new').modal('show');
                    }
                """)
                time.sleep(UIConstants.MEDIUM_SLEEP)
                modal_opened = True
            except Exception as e:
                Logger.logFine(f"手入力ボタンのクリック失敗: {e}")
            
            # モーダルフォームの確認（複数のセレクタを試行）
            form_found = False
            form_selectors = [
                (By.ID, "form-user-asset-act"),
                (By.ID, self.ID_AMOUNT),
                (By.ID, self.ID_IS_INCOME_MODAL),
                (By.CSS_SELECTOR, "#user_asset_act_new .modal-body"),
                (By.CSS_SELECTOR, "form[action*='user_asset_act']"),
            ]
            
            for selector_type, selector_value in form_selectors:
                try:
                    elem = wait.until(EC.visibility_of_element_located((selector_type, selector_value)))
                    form_found = True
                    Logger.logFine(f"フォーム要素を確認: {selector_value}")
                    break
                except Exception:
                    continue
            
            if not form_found:
                # デバッグ用にHTMLを保存
                Logger.logError("モーダルフォームが見つかりません。")
                self._save_debug_html(self.DEBUG_HTML_PATH)
                raise Exception("モーダルフォームが表示されていません")
                
        except Exception as e:
            Logger.logError(f"入力ページへの遷移に失敗: {e}")
            self._save_debug_html(self.DEBUG_HTML_PATH)
            Logger.logInfo(f"ページのHTMLを {self.DEBUG_HTML_PATH} に保存しました。")
            raise

    def _register_deduction_sum_as_income(self) -> None:
        """控除項目の合計を収入として登録します"""
        sum_item = next(
            (item for item in self.salary.deductionItems 
             if item.name == ItemNames.DEDUCTION_SUM),
            None
        )
        
        if sum_item:
            self._register_item_internal(sum_item, is_income=True)

    def _register_deduction_items(self) -> None:
        """すべての控除項目の登録を行います"""
        for item in self.salary.deductionItems:
            if item.name != ItemNames.DEDUCTION_SUM:
                # 控除データが負の値であれば収入として登録する
                is_income = item.amount < 0
                self._register_item_internal(item, is_income=is_income)

    def _register_item_internal(self, item: Item, is_income: bool = False) -> None:
        """
        共通登録処理を行います
        
        Args:
            item: 登録する項目
            is_income: 収入として登録するか
        """
        wait = WebDriverWait(self.driver, UIConstants.DEFAULT_WAIT_TIMEOUT)
        
        try:
            self._set_income_expense_type(is_income)
            self._set_sub_account(wait)
            self._set_amount(wait, item.amount)
            self._set_categories(wait, item)
        except Exception as e:
            Logger.logError(f"カテゴリ選択でエラー: {e}")
            self._save_debug_screenshot()
            raise

        self._set_content(wait, item.name)
        self._set_date(wait)
        self._confirm_income_expense_field(is_income)
        self._submit_and_continue(wait, item.name, is_income)
    
    def _set_income_expense_type(self, is_income: bool) -> None:
        """収入/支出の切り替え"""
        # モーダル用のIDを使用（/cfページのフォーム）
        field_id = self.ID_IS_INCOME_MODAL
        
        # まずhidden fieldの値を設定
        value = '1' if is_income else '0'
        self.driver.execute_script(
            f"var elem = document.getElementById('{field_id}'); "
            f"if (elem) elem.value = '{value}';"
        )
        
        # タブをクリックして切り替え
        time.sleep(UIConstants.SHORT_SLEEP)
        if is_income:
            # 収入タブをクリック
            self.driver.execute_script("""
                var tab = document.querySelector('input.plus-payment');
                if (tab) {
                    tab.click();
                    var label = tab.closest('label');
                    if (label) label.click();
                }
            """)
        else:
            # 支出タブをクリック
            self.driver.execute_script("""
                var tab = document.querySelector('input.minus-payment');
                if (tab) {
                    tab.click();
                    var label = tab.closest('label');
                    if (label) label.click();
                }
            """)
        time.sleep(UIConstants.SHORT_SLEEP)
    
    def _set_sub_account(self, wait: WebDriverWait) -> None:
        """支出・収入金額の出所を'なし'へ設定"""
        try:
            elem = wait.until(EC.visibility_of_element_located((By.ID, self.ID_SUB_ACCOUNT)))
            select = Select(elem)
            select.select_by_visible_text(self.OPTION_NONE)
        except Exception as e:
            # 要素が表示されていない場合はJavaScriptで設定
            Logger.logFine(f"Selectでの設定失敗、JSで試行: {e}")
            self.driver.execute_script(f"""
                var elem = document.getElementById('{self.ID_SUB_ACCOUNT}');
                if (elem) {{
                    for (var i = 0; i < elem.options.length; i++) {{
                        if (elem.options[i].text.trim() === '{self.OPTION_NONE}' || elem.options[i].value === '0') {{
                            elem.selectedIndex = i;
                            break;
                        }}
                    }}
                }}
            """)
    
    def _set_amount(self, wait: WebDriverWait, amount: int) -> None:
        """金額を設定"""
        elem = wait.until(EC.presence_of_element_located((By.ID, self.ID_AMOUNT)))
        elem.clear()
        elem.send_keys(str(abs(amount)))
    
    def _set_categories(self, wait: WebDriverWait, item: Item) -> None:
        """大カテゴリと中カテゴリを設定"""
        # 大項目
        large_btn = wait.until(EC.presence_of_element_located((By.ID, self.ID_LARGE_CATEGORY)))
        self.driver.execute_script("arguments[0].click();", large_btn)
        time.sleep(UIConstants.SHORT_SLEEP)
        
        large_link = wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//a[text()="{item.category}" and @class="l_c_name"]')
        ))
        self.driver.execute_script("arguments[0].click();", large_link)

        # 中項目
        time.sleep(UIConstants.SHORT_SLEEP)
        middle_btn = wait.until(EC.presence_of_element_located((By.ID, self.ID_MIDDLE_CATEGORY)))
        self.driver.execute_script("arguments[0].click();", middle_btn)
        time.sleep(UIConstants.SHORT_SLEEP)
        
        middle_link = wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//a[text()="{item.subcategory}" and @class="m_c_name"]')
        ))
        self.driver.execute_script("arguments[0].click();", middle_link)
    
    def _set_content(self, wait: WebDriverWait, content: str) -> None:
        """内容を設定"""
        elem = wait.until(EC.presence_of_element_located((By.ID, self.ID_CONTENT)))
        elem.clear()
        elem.send_keys(content)
    
    def _set_date(self, wait: WebDriverWait) -> None:
        """日付を設定"""
        elem = wait.until(EC.presence_of_element_located((By.ID, self.ID_DATE)))
        elem.clear()
        elem.send_keys(self.salary.get_payday())
    
    def _confirm_income_expense_field(self, is_income: bool) -> None:
        """登録直前に収入/支出フィールドを再度確実に設定"""
        value = '1' if is_income else '0'
        # モーダル用IDを優先、なければ通常IDを使用
        self.driver.execute_script(
            f"var elemModal = document.getElementById('{self.ID_IS_INCOME_MODAL}'); "
            f"var elem = document.getElementById('{self.ID_IS_INCOME}'); "
            f"if (elemModal) elemModal.value = '{value}'; "
            f"if (elem) elem.value = '{value}';"
        )
    
    def _submit_and_continue(self, wait: WebDriverWait, item_name: str, is_income: bool) -> None:
        """フォームを送信し、続けて入力する"""
        # 登録
        time.sleep(UIConstants.SHORT_SLEEP)
        elem = wait.until(EC.presence_of_element_located((By.ID, self.ID_CONTENT)))
        elem.submit()
        
        income_type = '収入' if is_income else '支出'
        Logger.logFine(f"{item_name} ({income_type}) の登録に成功しました。")

        # 続けて入力する
        time.sleep(UIConstants.LONG_SLEEP)
        confirm_btn = wait.until(
            EC.element_to_be_clickable((By.ID, self.ID_CONFIRMATION_BTN))
        )
        confirm_btn.click()
        time.sleep(UIConstants.SHORT_SLEEP)
    
    def _save_debug_html(self, filepath: str) -> None:
        """デバッグ用にHTMLを保存"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
    
    def _save_debug_screenshot(self) -> None:
        """デバッグ用にスクリーンショットを保存"""
        self.driver.save_screenshot(self.DEBUG_SCREENSHOT_PATH)
        self._save_debug_html(self.DEBUG_FORM_HTML_PATH)
        Logger.logInfo("スクリーンショットとHTMLをdebugファイルに保存しました。")
    
    # 後方互換性のためのエイリアス（非推奨）
    def registerInternal(self, item: Item, is_income: bool = False) -> None:
        """非推奨: _register_item_internal()を使用してください"""
        self._register_item_internal(item, is_income)

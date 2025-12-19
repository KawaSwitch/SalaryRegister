from logger import Logger
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from salary import Salary
import config
import pyotp
import time


# MoneyForwardへの給与情報アップロードを行う
class Uploader:
    def __init__(self, salary: Salary):
        self.salary = salary
        self.email = config.data.getMoneyForwardId()
        self.pw = config.data.getMoneyForwardPassword()
        self.tfaid = config.data.getTfaId()
        self.driver = None
        self.actions = None

    # 給与情報をMoneyForwardへアップロードする
    # isDeductionOnly: 給与控除のみを対象とするか
    def upload(self, isDeductionOnly=True):
        # 最終確認
        if not self.confirm():
            return

        # 給与データ登録処理
        self.init()
        self.access()
        self.login()
        self.registerDeduction()

        # MEMO: 現状は控除項目のみで問題なし
        if isDeductionOnly:
            return

    # 給与登録の確認を行います
    def confirm(self) -> bool:
        defaultDate = config.data.getDefaultDate()
        text = "MoneyForwardへの給与登録を行います。登録日を入力してください。"
        date = input(f"{text}({defaultDate}日): ") or defaultDate

        if self.salary.setDate(date):
            ans = input(
                f"{self.salary.getPayday()}を給料日として登録します。よろしいですか。(Y/n): "
            )
            if ans in ["", "Y"]:
                return True
            else:
                print("給与登録をキャンセルしました。")
                return False
        else:
            Logger.logError(
                "指定された日付は誤っています。正しい日付を入力してください。"
            )
            return False

    # WebDriverの初期化を行います
    def init(self):
        Logger.logFine("WebDriverの初期化を行います。")
        try:
            maxWait = 5
            options = webdriver.ChromeOptions()

            # 画面表示設定
            if config.data.isHeadlessMode():
                options = self.addHeadlessSettings(options)

            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(maxWait)
            self.driver.set_window_size(1280, 720)
            self.actions = ActionChains(self.driver)
        except Exception:
            if self.driver is not None:
                self.driver.quit()
            raise Exception("WebDriverの初期化に失敗しました。")

        Logger.logFine("WebDriverの初期化に成功しました。")

    # ヘッドレスモード(画面非表示)の設定を追加する
    def addHeadlessSettings(self, options):
        # ヘッドレスモード対策の回避用にUAオプションを追加
        # 参考:Stack Overflow - How to access a site via a headless driver
        # without being denied permission
        # URL:https://stackoverflow.com/questions/54432980/how-to-access-a-site-via-a-headless-driver-without-being-denied-permission
        options.add_argument("--headless")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        user_agent += (
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
        )
        options.add_argument("user-agent={0}".format(user_agent))
        return options

    # Webページへのアクセスを行います
    def access(self):
        Logger.logFine("MoneyForwardのページにアクセスしています。")
        self.driver.get("https://moneyforward.com")
        self.driver.implicitly_wait(10)
        Logger.logFine("MoneyForwardのページにアクセス完了しました。")

    # MoneyForwardMeサービスへのログインを行います
    def login(self):
        Logger.logInfo("ログインしています。")
        wait = WebDriverWait(self.driver, 5)

        # 初期ページ > ログイン遷移
        mainMenu = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="before-login-corporate"]/header/div[1]/div[2]/nav/ul/li[1]/p')
        ))
        self.actions.move_to_element(mainMenu).perform()
        login_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "ログイン")))
        login_link.click()

        # ユーザ名
        elem = wait.until(EC.presence_of_element_located((By.ID, "mfid_user[email]")))
        elem.send_keys(self.email)
        elem.submit()
        Logger.logFine("ユーザID認証に成功しました。")

        # パスワード
        elem = wait.until(EC.presence_of_element_located((By.ID, "mfid_user[password]")))
        elem.send_keys(self.pw)
        elem.submit()
        Logger.logFine("パスワード認証に成功しました。")

        # 2段階認証
        elem = wait.until(EC.presence_of_element_located((By.ID, "otp_attempt")))
        topt = pyotp.TOTP(self.tfaid)
        elem.send_keys(topt.now())
        elem.submit()
        time.sleep(1)

        Logger.logInfo("ログインが完了しました。")

    # 給与控除の登録を行います
    def registerDeduction(self):
        Logger.logInfo("控除項目の登録を行います。")

        # 給与登録ページへ遷移
        time.sleep(0.5)
        
        # モーダル閉じる（高速化）
        try:
            close_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'close') or contains(@aria-label, 'Close')]")
            if close_buttons and close_buttons[0].is_displayed():
                close_buttons[0].click()
                time.sleep(0.3)
        except:
            pass
        
        try:
            wait = WebDriverWait(self.driver, 5)
            # 直接JavaScriptでクリック（最速）
            input_button = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "収入・振替を入力する")))
            self.driver.execute_script("arguments[0].click();", input_button)
            time.sleep(0.5)
        except Exception as e:
            Logger.logError(f"入力ボタンが見つかりません: {e}")
            with open("../userdata/debug_page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            Logger.logInfo("ページのHTMLを debug_page.html に保存しました。")
            raise

        # 控除合計->控除項目の順に登録
        self.registerDeductionSumAsIncome()
        self.registerDeductionItems()

        Logger.logInfo("すべての控除項目の登録が完了しました。")
        self.driver.quit()

    # 控除項目の合計を収入として登録します
    def registerDeductionSumAsIncome(self):
        incomeData = None
        for item in self.salary.deductionItems:
            if item.name == "控除合計":
                incomeData = item

        # 控除データ登録（収入として）
        self.registerInternal(incomeData, is_income=True)

    # 支出登録タブへ移動する
    # 前提:家計簿入力ダイアログが開いている状態であること
    def gotoPaymentTab(self):
        wait = WebDriverWait(self.driver, 10)
        time.sleep(0.5)
        payment_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "minus-payment")))
        payment_btn.click()
        time.sleep(0.5)

    # 収入登録タブへ移動する
    # 前提:家計簿入力ダイアログが開いている状態であること
    def gotoIncomeTab(self):
        wait = WebDriverWait(self.driver, 10)
        time.sleep(0.5)
        income_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "plus-payment")))
        income_btn.click()
        time.sleep(0.5)

    # すべての控除項目の登録を行います
    def registerDeductionItems(self):
        for item in [x for x in self.salary.deductionItems if x.name != "控除合計"]:
            # 控除データが負の値であれば収入として登録する
            is_income_item = item.amount < 0
            # 控除データ登録
            self.registerInternal(item, is_income=is_income_item)

    # 共通登録処理を行います
    def registerInternal(self, item, is_income=False):
        wait = WebDriverWait(self.driver, 5)
        
        try:
            # 収入/支出の切り替え（シンプルかつ確実に）
            if is_income:
                # 収入として登録 - hidden fieldとフォーム両方を設定
                self.driver.execute_script("""
                    document.getElementById('user_asset_act_is_income').value = '1';
                    // 収入フォームに切り替え（存在する場合）
                    var incomeTab = document.querySelector('a.btn-success, a[href*="income"], .plus-payment');
                    if (incomeTab) incomeTab.click();
                """)
            else:
                # 支出として登録 - hidden fieldとフォーム両方を設定
                self.driver.execute_script("""
                    document.getElementById('user_asset_act_is_income').value = '0';
                    // 支出フォームに切り替え（存在する場合）
                    var paymentTab = document.querySelector('a.btn-danger, a[href*="payment"], .minus-payment');
                    if (paymentTab) paymentTab.click();
                """)
            
            # 支出・収入金額の出所を'なし'へ
            elem = wait.until(EC.presence_of_element_located((By.ID, "user_asset_act_sub_account_id_hash")))
            select = Select(elem)
            select.select_by_visible_text("なし")

            # 金額
            elem = wait.until(EC.presence_of_element_located((By.ID, "appendedPrependedInput")))
            elem.clear()
            elem.send_keys(str(abs(item.amount)))

            # 大項目（高速化）
            large_category_btn = wait.until(EC.presence_of_element_located((By.ID, "js-large-category-selected")))
            self.driver.execute_script("arguments[0].click();", large_category_btn)
            time.sleep(0.2)
            
            large_cat_link = wait.until(EC.presence_of_element_located(
                (By.XPATH, f'//a[text()="{item.category}" and @class="l_c_name"]')
            ))
            self.driver.execute_script("arguments[0].click();", large_cat_link)

            # 中項目（高速化）
            time.sleep(0.2)
            middle_category_btn = wait.until(EC.presence_of_element_located((By.ID, "js-middle-category-selected")))
            self.driver.execute_script("arguments[0].click();", middle_category_btn)
            time.sleep(0.2)
            
            middle_cat_link = wait.until(EC.presence_of_element_located(
                (By.XPATH, f'//a[text()="{item.subcategory}" and @class="m_c_name"]')
            ))
            self.driver.execute_script("arguments[0].click();", middle_cat_link)
        except Exception as e:
            Logger.logError(f"カテゴリ選択でエラー: {e}")
            # デバッグ用にスクリーンショットを保存
            self.driver.save_screenshot("../userdata/debug_screenshot.png")
            with open("../userdata/debug_form.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            Logger.logInfo("スクリーンショットとHTMLをdebugファイルに保存しました。")
            raise

        # 内容
        elem = wait.until(EC.presence_of_element_located((By.ID, "js-content-field")))
        elem.clear()
        elem.send_keys(item.name)

        # カレンダー(日付)
        elem = wait.until(EC.presence_of_element_located((By.ID, "updated-at")))
        elem.clear()
        elem.send_keys(self.salary.getPayday())

        # 登録直前に収入/支出フィールドを再度確実に設定
        self.driver.execute_script(
            f"document.getElementById('user_asset_act_is_income').value = '{'1' if is_income else '0'}';"
        )

        # 登録
        time.sleep(0.3)
        elem.submit()
        Logger.logFine(f"{item.name} ({'収入' if is_income else '支出'}) の登録に成功しました。")

        # 続けて入力する
        time.sleep(0.5)
        confirm_btn = wait.until(EC.element_to_be_clickable((By.ID, "confirmation-button")))
        confirm_btn.click()
        time.sleep(0.3)

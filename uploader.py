from logger import Logger
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import config


# MoneyForwardへの給与情報アップロードを行う
class Uploader:
    def __init__(self, salary):
        self.salary = salary
        self.email = config.data.getMoneyForwardId()
        self.pw = config.data.getMoneyForwardPassword()
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
        date = input("MoneyForwardへの給与登録を行います。登録日を入力してください: ")
        if self.salary.setDate(date):
            ans = input(
                f"{self.salary.getPayday()}を給料日として登録します。よろしいですか。(Y/n)"
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
            maxWait = 10
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

        # 初期ページ > ログイン遷移
        mainMenu = self.driver.find_element(
            By.XPATH,
            '//*[@id="before-login-corporate"]/header/div[1]/div[2]/nav/ul/li[1]/p',
        )
        self.actions.move_to_element(mainMenu).perform()
        self.driver.find_element(By.LINK_TEXT, "ログイン").click()

        # ユーザ名
        elem = self.driver.find_element(By.ID, "mfid_user[email]")
        elem.send_keys(self.email)
        elem.submit()
        Logger.logFine("ユーザID認証に成功しました。")

        # パスワード
        elem = self.driver.find_element(By.ID, "mfid_user[password]")
        elem.send_keys(self.pw)
        elem.submit()
        Logger.logFine("パスワード認証に成功しました。")

        Logger.logInfo("ログインが完了しました。")

    # 給与控除の登録を行います
    def registerDeduction(self):
        Logger.logInfo("控除項目の登録を行います。")

        # 給与登録ページへ遷移
        self.driver.find_element(By.LINK_TEXT, "収入・振替を入力する").click()

        # 控除合計->控除項目の順に登録
        self.registerDeductionIncome()
        self.registerDeductionExpense()

        Logger.logInfo("すべての控除項目の登録が完了しました。")
        self.driver.quit()

    # 控除項目の合計を収入として登録します
    def registerDeductionIncome(self):
        incomeData = None
        for item in self.salary.deductionItems:
            if item.name == "控除合計":
                incomeData = item

        # 収入の入力タブへ移動(デフォルトは支出タブのため)
        self.driver.find_element(By.CLASS_NAME, "plus-payment").click()
        # 控除データ登録
        self.registerInternal(incomeData)

    # すべての控除項目の登録を行います
    def registerDeductionExpense(self):
        for item in [x for x in self.salary.deductionItems if x.name != "控除合計"]:
            # 控除データ登録
            self.registerInternal(item)

    # 共通登録処理を行います
    def registerInternal(self, item):
        # 支出・収入金額の出所を'なし'へ
        elem = self.driver.find_element(By.ID, "user_asset_act_sub_account_id_hash")
        select = Select(elem)
        select.select_by_visible_text("なし")

        # 金額
        elem = self.driver.find_element(By.ID, "appendedPrependedInput")
        elem.send_keys(item.amount)

        # 大項目
        self.driver.find_element(By.ID, "js-large-category-selected").click()
        self.driver.find_element(
            By.XPATH, '//a[text()="' + item.category + '" and @class="l_c_name"]'
        ).click()

        # 中項目
        self.driver.find_element(By.ID, "js-middle-category-selected").click()
        self.driver.find_element(
            By.XPATH, '//a[text()="' + item.subcategory + '" and @class="m_c_name"]'
        ).click()

        # 内容
        elem = self.driver.find_element(By.ID, "js-content-field")
        elem.send_keys(item.name)

        # カレンダー(日付)
        # MEMO: 一旦開いたカレンダーを閉じる方法が分からなかった。
        # MEMO: 大項目などのクリック時に邪魔になるため最後に選択する。
        elem = self.driver.find_element(By.ID, "updated-at")
        elem.clear()
        elem.send_keys(self.salary.getPayday())

        # 登録
        elem.submit()
        Logger.logFine(f"{item.name} の登録に成功しました。")

        # 続けて入力する
        self.driver.find_element(By.ID, "confirmation-button").click()

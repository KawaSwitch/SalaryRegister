import configparser
import os
from logger import Logger
from distutils.util import strtobool
from typing import Final


class Config:
    """設定ファイル読み込みクラス"""
    
    # セクション名
    DEFAULT: Final[str] = "DEFAULT"
    
    # 設定キー名
    KEY_PDF_PASSWORD: Final[str] = "PdfPassword"
    KEY_MF_MAIL: Final[str] = "MfMailAddress"
    KEY_MF_PASSWORD: Final[str] = "MfPassword"
    KEY_EMPLOYEE_NUMBER: Final[str] = "EmployeeNumber"
    KEY_HEADLESS_MODE: Final[str] = "UseHeadlessMode"
    KEY_DEFAULT_DATE: Final[str] = "DefaultDate"
    KEY_TFA_ID: Final[str] = "TfaId"
    
    # ファイルパス
    USERDATA_DIR: Final[str] = "../userdata"
    CONFIG_FILENAME: Final[str] = "config.ini"

    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self) -> None:
        """設定iniファイルの読み込み"""
        config_path = os.path.join(self.USERDATA_DIR, self.CONFIG_FILENAME)
        
        Logger.logInfo("設定ファイルの読み込みを開始します。")
        loaded_files = self.config.read(config_path, encoding="utf-8")
        
        if not loaded_files:
            raise FileNotFoundError(
                f"設定ファイルが見つかりません: {config_path}"
            )
        Logger.logInfo("設定ファイルの読み込みが完了しました。")

    def get_pdf_password(self) -> str:
        """PDFパスワードを取得します"""
        return self.config[self.DEFAULT][self.KEY_PDF_PASSWORD]

    def get_moneyforward_email(self) -> str:
        """MoneyForwardへのログイン時のメールアドレスを取得します"""
        return self.config[self.DEFAULT][self.KEY_MF_MAIL]

    def get_moneyforward_password(self) -> str:
        """MoneyForwardへのログイン時のパスワードを取得します"""
        return self.config[self.DEFAULT][self.KEY_MF_PASSWORD]

    def get_employee_number(self) -> str:
        """従業員番号を取得します"""
        return self.config[self.DEFAULT][self.KEY_EMPLOYEE_NUMBER]

    def is_headless_mode(self) -> bool:
        """ヘッドレスモードで起動するかを取得します"""
        headless_value = self.config[self.DEFAULT][self.KEY_HEADLESS_MODE]
        return bool(strtobool(headless_value.upper()))

    def get_default_date(self) -> str:
        """給与登録日としてデフォルトで表示する日付を取得します"""
        return self.config[self.DEFAULT][self.KEY_DEFAULT_DATE]

    def get_tfa_id(self) -> str:
        """2段階認証の生成用IDを取得します"""
        return self.config[self.DEFAULT][self.KEY_TFA_ID]
    
    # 後方互換性のためのエイリアス（非推奨）
    def getPdfPassword(self) -> str:
        return self.get_pdf_password()
    
    def getMoneyForwardId(self) -> str:
        return self.get_moneyforward_email()
    
    def getMoneyForwardPassword(self) -> str:
        return self.get_moneyforward_password()
    
    def getEmployeeNumber(self) -> str:
        return self.get_employee_number()
    
    def isHeadlessMode(self) -> bool:
        return self.is_headless_mode()
    
    def getDefaultDate(self) -> str:
        return self.get_default_date()
    
    def getTfaId(self) -> str:
        return self.get_tfa_id()


# モジュールレベルで設定を初期化（テスト時にエラーを避けるためtry-except）
try:
    data = Config()
except FileNotFoundError:
    # テスト環境などで設定ファイルがない場合はNoneにする
    data = None

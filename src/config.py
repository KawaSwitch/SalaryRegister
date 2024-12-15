import configparser
import os
from logger import Logger
from distutils.util import strtobool


# 設定ファイル読み込み
class Config:

    DEFAULT = "DEFAULT"

    def __init__(self):
        userdataDir = "../userdata"
        configFileName = "config.ini"
        self.config = configparser.ConfigParser()

        # 設定iniファイルの読み込み
        configPath = os.path.join(userdataDir, configFileName)
        files = [configPath]

        Logger.logInfo("設定ファイルの読み込みを開始します。")
        ds = self.config.read(files, encoding="utf-8")
        if len(ds) != len(files):
            raise FileExistsError(
                f"ファイル読み込みエラー。{configPath}が見つかりません。"
            )
        Logger.logInfo("設定ファイルの読み込みが完了しました。")

    # PDFパスワードを取得します
    def getPdfPassword(self):
        return self.config[Config.DEFAULT]["PdfPassword"]

    # MoneyForwardへのログイン時のメールアドレスを取得します
    def getMoneyForwardId(self):
        return self.config[Config.DEFAULT]["MfMailAddress"]

    # MoneyForwardへのログイン時のパスワードを取得します
    def getMoneyForwardPassword(self):
        return self.config[Config.DEFAULT]["MfPassword"]

    # 従業員番号を取得します
    def getEmployeeNumber(self):
        return self.config[Config.DEFAULT]["EmployeeNumber"]

    # ヘッドレスモードで起動するかを取得します
    def isHeadlessMode(self):
        isHeadless = self.config[Config.DEFAULT]["UseHeadlessMode"]
        return strtobool(isHeadless.upper())


data = Config()

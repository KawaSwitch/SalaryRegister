import sys
import traceback
from logger import Logger
from uploader import Uploader
from salary import Salary


# 引数チェック
def argCheck() -> bool:
    if len(sys.argv) != 3:
        Logger.logWarning("給与登録を行う年と月を入力してください")
        Logger.logWarning("例：python upload.py 2024 11")
        return False

    try:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
    except Exception:
        Logger.logWarning("正しい数値形式で給与登録を行う年と月を入力してください")
        Logger.logWarning("例：python upload.py 2024 11")
        return False

    Logger.logInfo(f"{year}年{month:02}月の給与明細登録を行います。")
    return True


# メインメソッド
if __name__ == "__main__":
    isPrintTrace = False

    if argCheck():
        try:
            # 給与データ読み込み
            salary = Salary(sys.argv[1], sys.argv[2])
            # 給与データ登録
            Uploader(salary).upload(salary)

        except Exception as e:
            Logger.logError(e)
            if isPrintTrace:
                print("--- traceback ---")
                traceback.print_exc()
                print("---    end    ---")
    else:
        sys.exit(1)

import sys
import traceback
from logger import Logger
from uploader import Uploader
from salary import Salary
from argument import Arguments


# メインメソッド
if __name__ == "__main__":
    isPrintTrace = False
    args = Arguments()

    if args.isValid():
        try:
            # 給与データ読み込み
            salary = Salary(args.getYear(), args.getMonth(), args.getKind())
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

import sys
import traceback
from typing import Final

from logger import Logger
from uploader import Uploader
from salary import Salary
from argument import Arguments


# 定数
PRINT_TRACE: Final[bool] = True
TRACEBACK_HEADER: Final[str] = "--- traceback ---"
TRACEBACK_FOOTER: Final[str] = "---    end    ---"


def main() -> None:
    """メインメソッド"""
    args = Arguments()

    if not args.is_valid():
        sys.exit(1)
    
    try:
        # 給与データ読み込み
        salary = Salary(args.get_year(), args.get_month(), args.get_kind())
        # 給与データ登録
        Uploader(salary).upload()

    except Exception as e:
        Logger.logError(str(e))
        
        if PRINT_TRACE:
            print(TRACEBACK_HEADER)
            traceback.print_exc()
            print(TRACEBACK_FOOTER)
        
        sys.exit(1)


if __name__ == "__main__":
    main()

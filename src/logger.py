# 前景色管理
class FColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# ロガー処理
class Logger:
    logLevel = 1

    @classmethod
    def logFine(cls, text):
        Logger.__logPrint(f"[fine] {text}", FColors.OKGREEN)

    @classmethod
    def logInfo(cls, text):
        Logger.__logPrint(f"[info] {text}", FColors.OKCYAN)

    def logDebug(cls, text):
        Logger.__logPrint(f"[info] {text}")

    @classmethod
    def logWarning(cls, text):
        Logger.__logPrint(f"[WARNING] {text}", FColors.WARNING)

    @classmethod
    def logError(cls, text):
        Logger.__logPrint(f"[ERROR] {text}", FColors.FAIL)

    @classmethod
    def __logPrint(cls, text, color=FColors.ENDC):
        print(f"{color}{text}{FColors.ENDC}")

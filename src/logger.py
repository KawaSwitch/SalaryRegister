from typing import Final


class FColors:
    """前景色管理クラス（ANSIエスケープシーケンス）"""
    HEADER: Final[str] = "\033[95m"
    OKBLUE: Final[str] = "\033[94m"
    OKCYAN: Final[str] = "\033[96m"
    OKGREEN: Final[str] = "\033[92m"
    WARNING: Final[str] = "\033[93m"
    FAIL: Final[str] = "\033[91m"
    ENDC: Final[str] = "\033[0m"
    BOLD: Final[str] = "\033[1m"
    UNDERLINE: Final[str] = "\033[4m"


class Logger:
    """ログ出力用クラス"""
    log_level: int = 1

    @classmethod
    def logFine(cls, text: str) -> None:
        """詳細レベルのログを出力"""
        cls._log_print(f"[fine] {text}", FColors.OKGREEN)

    @classmethod
    def logInfo(cls, text: str) -> None:
        """情報レベルのログを出力"""
        cls._log_print(f"[info] {text}", FColors.OKCYAN)

    @classmethod
    def logDebug(cls, text: str) -> None:
        """デバッグレベルのログを出力"""
        cls._log_print(f"[debug] {text}")

    @classmethod
    def logWarning(cls, text: str) -> None:
        """警告レベルのログを出力"""
        cls._log_print(f"[WARNING] {text}", FColors.WARNING)

    @classmethod
    def logError(cls, text: str) -> None:
        """エラーレベルのログを出力"""
        cls._log_print(f"[ERROR] {text}", FColors.FAIL)

    @classmethod
    def _log_print(cls, text: str, color: str = FColors.ENDC) -> None:
        """
        内部用: 色付きログ出力
        
        Args:
            text: 出力するテキスト
            color: 前景色のANSIエスケープシーケンス
        """
        print(f"{color}{text}{FColors.ENDC}")

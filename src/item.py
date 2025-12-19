import unicodedata
from typing import Final, Optional


class Item:
    """給与項目を表すクラス"""
    
    # 表示幅関連の定数
    DEFAULT_DISPLAY_WIDTH: Final[int] = 16
    FULLWIDTH_CHARS: Final[str] = "FWA"
    FULLWIDTH_SIZE: Final[int] = 2
    HALFWIDTH_SIZE: Final[int] = 1
    
    # アラインメント定数
    ALIGN_LEFT: Final[int] = -1
    ALIGN_RIGHT: Final[int] = 1

    def __init__(
        self, 
        name: str, 
        amount: int | str, 
        main: Optional[str] = None, 
        sub: Optional[str] = None
    ) -> None:
        """
        給与項目の初期化
        
        Args:
            name: 項目名
            amount: 金額（整数または数値文字列）
            main: 大カテゴリ
            sub: 中カテゴリ
        """
        self.name = name
        self.amount = int(amount)
        self.category = main
        self.subcategory = sub

    def __str__(self) -> str:
        item_str = self._align_text(self.name, self.DEFAULT_DISPLAY_WIDTH)
        return f"項目: {item_str}, 金額: {self.amount:,}円"

    def set_categories(self, main: str, sub: str) -> None:
        """
        分類を設定する
        
        Args:
            main: 大カテゴリ
            sub: 中カテゴリ
        """
        self.category = main
        self.subcategory = sub

    def _get_character_width(self, text: str) -> int:
        """
        半角/全角を考慮した文字幅を計算する
        
        Args:
            text: 文字列
            
        Returns:
            半角換算での文字数
            
        Note:
            参考: Qiita - [Python]全角と半角が混在するテキストに空白を入れて横幅を揃える関数
            URL: https://qiita.com/autumn_nsn/items/b1614fe6bba5ccf98778
        """
        width = 0
        for char in text:
            if unicodedata.east_asian_width(char) in self.FULLWIDTH_CHARS:
                width += self.FULLWIDTH_SIZE
            else:
                width += self.HALFWIDTH_SIZE
        return width

    def _align_text(
        self, 
        text: str, 
        width: int, 
        align: int = ALIGN_LEFT, 
        fill_char: str = " "
    ) -> str:
        """
        半角/全角を考慮してアラインメント調整を行った文字列を取得する
        
        Args:
            text: 対象文字列
            width: 半角換算の文字数
            align: -1(左寄せ) / 1(右寄せ)
            fill_char: 埋める文字
            
        Returns:
            アラインメント調整済みの文字列
            
        Note:
            参考: Qiita - [Python]全角と半角が混在するテキストに空白を入れて横幅を揃える関数
            URL: https://qiita.com/autumn_nsn/items/b1614fe6bba5ccf98778
        """
        fill_count = width - self._get_character_width(text)
        if fill_count <= 0:
            return text

        if align < 0:
            return text + fill_char * fill_count
        else:
            return fill_char * fill_count + text
    
    # 後方互換性のためのエイリアス（非推奨）
    def setCategories(self, main: str, sub: str) -> None:
        """非推奨: set_categories()を使用してください"""
        self.set_categories(main, sub)
    
    def getSpaces(self, text: str) -> int:
        """非推奨: _get_character_width()を使用してください"""
        return self._get_character_width(text)
    
    def alignText(
        self, 
        text: str, 
        width: int, 
        align: int = ALIGN_LEFT, 
        fill_char: str = " "
    ) -> str:
        """非推奨: _align_text()を使用してください"""
        return self._align_text(text, width, align, fill_char)

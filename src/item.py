import unicodedata


# 給与項目
class Item:
    def __init__(self, name, amount, main=None, sub=None):
        self.name = name
        self.amount = int(amount)
        self.category = main
        self.subcategory = sub

    def __str__(self) -> str:
        width = 16
        itemStr = self.alignText(self.name, width)
        return f"項目: {itemStr}, 金額: {self.amount:,}円"

    # 分類を設定する
    def setCategories(self, main, sub):
        self.category = main
        self.subcategory = sub

    # 半角/全角を考慮したスペース幅を計算する
    # 参考:Qiita -［Python］全角と半角が混在するテキストに空白を入れて横幅を揃える関数
    # URL:https://qiita.com/autumn_nsn/items/b1614fe6bba5ccf98778
    def getSpaces(self, text) -> int:
        count = 0
        for char in text:
            if unicodedata.east_asian_width(char) in "FWA":
                count += 2
            else:
                count += 1

        return count

    # 半角/全角を考慮してアラインメント調整を行った文字列を取得する
    # width: 半角換算の文字数
    # align: -1(left) / 1(right)
    # fill_char: 埋める文字
    # 参考:Qiita -［Python］全角と半角が混在するテキストに空白を入れて横幅を揃える関数
    # 参考:https://qiita.com/autumn_nsn/items/b1614fe6bba5ccf98778
    def alignText(self, text, width, align=-1, fill_char=" "):
        fill_count = width - self.getSpaces(text)
        if fill_count <= 0:
            return text

        if align < 0:
            return text + fill_char * fill_count
        else:
            return fill_char * fill_count + text

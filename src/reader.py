import os
import yaml
import pypdfium2 as pdfium
from logger import Logger
from item import Item
from common import SalaryKind
import config


# 給与データ読み取り
class SalaryReader:
    def __init__(self, year, month, number, kind):
        self.year = year
        self.month = month
        self.number = number
        self.kind = kind
        self.pw = config.data.getPdfPassword()

        # 各パス設定
        userdataDir = "../userdata"
        self.itemsFile = os.path.join(userdataDir, "items.yml")
        self.salaryDir = os.path.join(userdataDir, "salaryData")

    # 読み出し元となる給与明細のPDFファイル名を作成する
    def getPdfFileName(self) -> str:
        try:
            y = f"{self.year}"
            m = f"{self.month:0>2}"
            k = "_kyuyo_" if self.kind == SalaryKind.NORMAL else "_syoyo_"
            return y + m + k + str(self.number) + ".pdf"
        except Exception:
            return None

    # PDFから控除合計を読み出す
    def readDeduction(self) -> list[Item]:
        items = []
        pdfName = self.getPdfFileName()
        Logger.logFine(f"読み出し元PDF: {pdfName}")

        if pdfName is None:
            raise FileExistsError("読み出し元PDF名が生成できませんでした。")
        else:
            # 読み出し対象の項目リストをロード
            with open(self.itemsFile, "r") as yml:
                itemDefs = yaml.safe_load(yml)

            # 給与明細から該当する控除項目を取得
            key = "deduction"
            sumItem = None
            lines = self.convertPdf2Text(pdfName)
            for idx, line in enumerate(lines):
                for itemDef in itemDefs[key]:
                    if line == itemDef["name"]:
                        item = self.createItem(itemDef, lines, idx)

                        # 合計の一致確認のため一旦別枠として格納しておく
                        if line == "控除合計":
                            sumItem = item
                        else:
                            items.append(item)
                        break

            # 控除合計額と各控除項目の合計が一致するか確認
            total = sum([item.amount for item in items])
            if total == sumItem.amount:
                Logger.logFine(f"控除合計額が一致しました: {total:,}円")
            else:
                raise Exception("控除合計額と各控除項目の合計が一致しません")

            # すべての項目を返却する
            items.append(sumItem)
            return items

    # 項目名とPDF項目一覧から項目要素を作成
    def createItem(self, itemDef, lines, idx) -> Item:
        # 金額
        amount = lines[(idx + 1) % len(lines)].replace(",", "")
        amount = amount if amount.lstrip("-").isdigit() else 0
        # 登録するカテゴリ
        category = itemDef["category"]
        category_sub = itemDef["subcategory"]
        return Item(itemDef["name"], amount, category, category_sub)

    # 給与明細PDFをテキストデータへ変換
    def convertPdf2Text(self, filename) -> list[str]:
        try:
            pdf = pdfium.PdfDocument(os.path.join(self.salaryDir, filename), self.pw)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"{filename}が見つかりません。ファイルか指定年月日を修正してください。"
            )

        lines = []
        for page in pdf:
            textpage = page.get_textpage()
            lines.extend(textpage.get_text_bounded().split())
        return lines

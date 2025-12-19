import os
from typing import Optional, Final
import yaml
import pypdfium2 as pdfium

from logger import Logger
from item import Item
from common import SalaryKind, DirectoryNames, FileNames, ItemNames
import config


class SalaryReader:
    """給与データ読み取りクラス"""
    
    # エラーメッセージ
    ERROR_PDF_NAME_FAILED: Final[str] = "読み出し元PDF名が生成できませんでした。"
    ERROR_PDF_NOT_FOUND: Final[str] = "{filename}が見つかりません。ファイルか指定年月日を修正してください。"
    ERROR_AMOUNT_MISMATCH: Final[str] = "控除合計額と各控除項目の合計が一致しません"
    
    # ログメッセージ
    LOG_PDF_NAME: Final[str] = "読み出し元PDF: {filename}"
    LOG_AMOUNT_MATCH: Final[str] = "控除合計額が一致しました: {amount:,}円"
    
    # エンコーディング
    ENCODING_UTF8: Final[str] = "utf-8"
    
    def __init__(self, year: int, month: int, number: str, kind: SalaryKind) -> None:
        """
        給与データ読み取りの初期化
        
        Args:
            year: 年
            month: 月
            number: 社員番号
            kind: 給与種別
        """
        self.year = year
        self.month = month
        self.number = number
        self.kind = kind
        self.pw = config.data.get_pdf_password()

        # 各パス設定
        self.itemsFile = os.path.join(DirectoryNames.USERDATA, FileNames.ITEMS_YAML)
        self.salaryDir = os.path.join(DirectoryNames.USERDATA, DirectoryNames.SALARY_DATA)

    def _get_pdf_filename(self) -> str:
        """
        読み出し元となる給与明細のPDFファイル名を作成する
        
        Returns:
            PDFファイル名
            
        Raises:
            ValueError: ファイル名生成に失敗した場合
        """
        try:
            year_str = f"{self.year}"
            month_str = f"{self.month:0>2}"
            kind_infix = (
                FileNames.PDF_SALARY_INFIX 
                if self.kind == SalaryKind.NORMAL 
                else FileNames.PDF_BONUS_INFIX
            )
            return f"{year_str}{month_str}{kind_infix}{self.number}{FileNames.PDF_EXTENSION}"
        except Exception as e:
            raise ValueError(f"{self.ERROR_PDF_NAME_FAILED}: {str(e)}")

    def readDeduction(self) -> list[Item]:
        """
        PDFから控除合計を読み出す
        
        Returns:
            控除項目のリスト
        """
        pdf_name = self._get_pdf_filename()
        Logger.logFine(self.LOG_PDF_NAME.format(filename=pdf_name))
        
        item_definitions = self._load_item_definitions()
        text_lines = self._convert_pdf_to_text(pdf_name)
        
        items, sum_item = self._extract_items(text_lines, item_definitions)
        self._validate_total_amount(items, sum_item)
        
        items.append(sum_item)
        return items
    
    def _load_item_definitions(self) -> dict:
        """項目定義ファイルを読み込む"""
        with open(self.itemsFile, "r", encoding=self.ENCODING_UTF8) as yml:
            return yaml.safe_load(yml)
    
    def _extract_items(self, lines: list[str], item_defs: dict) -> tuple[list[Item], Item]:
        """
        PDFテキストから項目を抽出する
        
        Returns:
            (控除項目リスト, 控除合計項目)
        """
        items = []
        sum_item = None
        
        for idx, line in enumerate(lines):
            for item_def in item_defs[ItemNames.DEDUCTION_KEY]:
                if line == item_def["name"]:
                    item = self._create_item(item_def, lines, idx)
                    
                    if line == ItemNames.DEDUCTION_SUM:
                        sum_item = item
                    else:
                        items.append(item)
                    break
        
        return items, sum_item
    
    def _validate_total_amount(self, items: list[Item], sum_item: Item) -> None:
        """控除合計額と各項目の合計が一致するか確認"""
        total = sum(item.amount for item in items)
        if total == sum_item.amount:
            Logger.logFine(self.LOG_AMOUNT_MATCH.format(amount=total))
        else:
            raise ValueError(
                f"{self.ERROR_AMOUNT_MISMATCH}: "
                f"合計={total:,}円, 控除合計={sum_item.amount:,}円"
            )

    def _create_item(self, item_def: dict, lines: list[str], idx: int) -> Item:
        """
        項目名とPDF項目一覧から項目要素を作成
        
        Args:
            item_def: 項目定義
            lines: PDFから読み取ったテキスト行
            idx: 項目名のインデックス
            
        Returns:
            項目オブジェクト
        """
        # 金額は項目名の次の行にある
        amount_str = lines[(idx + 1) % len(lines)].replace(",", "")
        amount = int(amount_str) if amount_str.lstrip("-").isdigit() else 0
        
        # 登録するカテゴリ
        category = item_def["category"]
        category_sub = item_def["subcategory"]
        
        return Item(item_def["name"], amount, category, category_sub)

    def _convert_pdf_to_text(self, filename: str) -> list[str]:
        """
        給与明細PDFをテキストデータへ変換
        
        Args:
            filename: PDFファイル名
            
        Returns:
            テキスト行のリスト
            
        Raises:
            FileNotFoundError: PDFファイルが見つからない場合
        """
        pdf_path = os.path.join(self.salaryDir, filename)
        
        try:
            pdf = pdfium.PdfDocument(pdf_path, self.pw)
        except FileNotFoundError:
            raise FileNotFoundError(self.ERROR_PDF_NOT_FOUND.format(filename=filename))

        lines = []
        for page in pdf:
            textpage = page.get_textpage()
            text = textpage.get_text_bounded()
            
            # 日本語文字対応のためUTF-8でデコード
            if isinstance(text, bytes):
                text = text.decode(self.ENCODING_UTF8, errors='ignore')
            
            lines.extend(text.split())
        
        return lines
    
    # 後方互換性のためのエイリアス（非推奨）
    def getPdfFileName(self) -> str:
        """非推奨: _get_pdf_filename()を使用してください"""
        return self._get_pdf_filename()
    
    def createItem(self, item_def: dict, lines: list[str], idx: int) -> Item:
        """非推奨: _create_item()を使用してください"""
        return self._create_item(item_def, lines, idx)
    
    def convertPdf2Text(self, filename: str) -> list[str]:
        """非推奨: _convert_pdf_to_text()を使用してください"""
        return self._convert_pdf_to_text(filename)

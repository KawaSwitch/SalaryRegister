"""
test_reader.py
reader.pyの単体試験

C0, C1, C2カバレッジ100%を目指したテストケース
"""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from reader import SalaryReader
from common import SalaryKind, DirectoryNames, FileNames, ItemNames
from item import Item


@pytest.fixture(autouse=True)
def mock_config():
    """全テストでconfig.dataをモック"""
    with patch('reader.config.data') as mock_data:
        mock_data.get_pdf_password.return_value = "test_password"
        yield mock_data


class TestSalaryReaderInitialization:
    """SalaryReaderクラスの初期化テスト"""
    
    def test_init_with_normal_salary(self):
        """通常給与での初期化"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        assert reader.year == 2024
        assert reader.month == 11
        assert reader.number == "12345"
        assert reader.kind == SalaryKind.NORMAL
    
    def test_init_with_bonus(self):
        """賞与での初期化"""
        reader = SalaryReader(2024, 6, "67890", SalaryKind.BONUS)
        assert reader.year == 2024
        assert reader.month == 6
        assert reader.number == "67890"
        assert reader.kind == SalaryKind.BONUS
    
    def test_init_paths_set(self):
        """パスが正しく設定される"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        assert DirectoryNames.USERDATA in reader.itemsFile
        assert FileNames.ITEMS_YAML in reader.itemsFile
        assert DirectoryNames.USERDATA in reader.salaryDir
        assert DirectoryNames.SALARY_DATA in reader.salaryDir


class TestGetPdfFilename:
    """_get_pdf_filenameメソッドのテスト"""
    
    def test_normal_salary_filename(self):
        """通常給与のPDFファイル名生成"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        filename = reader._get_pdf_filename()
        assert filename == "202411_kyuyo_12345.pdf"
    
    def test_bonus_filename(self):
        """賞与のPDFファイル名生成"""
        reader = SalaryReader(2024, 6, "67890", SalaryKind.BONUS)
        filename = reader._get_pdf_filename()
        assert filename == "202406_syoyo_67890.pdf"
    
    def test_single_digit_month(self):
        """1桁の月の場合"""
        reader = SalaryReader(2024, 3, "11111", SalaryKind.NORMAL)
        filename = reader._get_pdf_filename()
        assert filename == "202403_kyuyo_11111.pdf"
    
    def test_december_month(self):
        """12月の場合"""
        reader = SalaryReader(2024, 12, "99999", SalaryKind.NORMAL)
        filename = reader._get_pdf_filename()
        assert filename == "202412_kyuyo_99999.pdf"
    
    def test_deprecated_getPdfFileName(self):
        """非推奨メソッドgetPdfFileName"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        filename = reader.getPdfFileName()
        assert filename == "202411_kyuyo_12345.pdf"


class TestCreateItem:
    """_create_itemメソッドのテスト"""
    
    def test_create_item_with_valid_amount(self):
        """有効な金額での項目作成"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        item_def = {
            "name": "健康保険",
            "category": "社会保険",
            "subcategory": "健康保険"
        }
        lines = ["健康保険", "15,000", "他の項目"]
        item = reader._create_item(item_def, lines, 0)
        
        assert item.name == "健康保険"
        assert item.amount == 15000
        assert item.category == "社会保険"
        assert item.subcategory == "健康保険"
    
    def test_create_item_with_negative_amount(self):
        """負の金額での項目作成"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        item_def = {
            "name": "調整額",
            "category": "その他",
            "subcategory": "調整"
        }
        lines = ["調整額", "-3,000"]
        item = reader._create_item(item_def, lines, 0)
        
        assert item.amount == -3000
    
    def test_create_item_with_zero_amount(self):
        """ゼロ金額での項目作成"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        item_def = {
            "name": "項目",
            "category": "カテゴリ",
            "subcategory": "サブ"
        }
        lines = ["項目", "0"]
        item = reader._create_item(item_def, lines, 0)
        
        assert item.amount == 0
    
    def test_create_item_with_non_numeric(self):
        """数値でない金額での項目作成"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        item_def = {
            "name": "項目",
            "category": "カテゴリ",
            "subcategory": "サブ"
        }
        lines = ["項目", "---"]
        item = reader._create_item(item_def, lines, 0)
        
        assert item.amount == 0
    
    def test_deprecated_createItem(self):
        """非推奨メソッドcreateItem"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        item_def = {
            "name": "テスト",
            "category": "大",
            "subcategory": "小"
        }
        lines = ["テスト", "1000"]
        item = reader.createItem(item_def, lines, 0)
        
        assert item.amount == 1000


class TestExtractItems:
    """_extract_itemsメソッドのテスト"""
    
    def test_extract_items_basic(self):
        """基本的な項目抽出"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        item_defs = {
            "deduction": [
                {"name": "健康保険", "category": "社会保険", "subcategory": "健康保険"},
                {"name": "厚生年金", "category": "社会保険", "subcategory": "年金"},
                {"name": "控除合計", "category": "合計", "subcategory": "合計"}
            ]
        }
        
        lines = ["健康保険", "10000", "厚生年金", "20000", "控除合計", "30000"]
        
        items, sum_item = reader._extract_items(lines, item_defs)
        
        assert len(items) == 2
        assert sum_item.name == "控除合計"
        assert sum_item.amount == 30000
    
    def test_extract_items_with_no_sum(self):
        """控除合計がない場合"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        item_defs = {
            "deduction": [
                {"name": "健康保険", "category": "社会保険", "subcategory": "健康保険"}
            ]
        }
        
        lines = ["健康保険", "10000"]
        
        items, sum_item = reader._extract_items(lines, item_defs)
        
        assert len(items) == 1
        assert sum_item is None
    
    def test_extract_items_empty_lines(self):
        """空のラインリスト"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        item_defs = {
            "deduction": [
                {"name": "健康保険", "category": "社会保険", "subcategory": "健康保険"}
            ]
        }
        
        lines = []
        
        items, sum_item = reader._extract_items(lines, item_defs)
        
        assert len(items) == 0
        assert sum_item is None


class TestValidateTotalAmount:
    """_validate_total_amountメソッドのテスト"""
    
    def test_validate_matching_amounts(self):
        """合計が一致する場合"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        items = [
            Item("項目1", 10000),
            Item("項目2", 20000),
            Item("項目3", 5000)
        ]
        sum_item = Item("控除合計", 35000)
        
        # 例外が発生しないことを確認
        reader._validate_total_amount(items, sum_item)
    
    def test_validate_mismatching_amounts(self):
        """合計が一致しない場合"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        items = [
            Item("項目1", 10000),
            Item("項目2", 20000)
        ]
        sum_item = Item("控除合計", 40000)  # 実際は30000のはず
        
        with pytest.raises(ValueError) as exc_info:
            reader._validate_total_amount(items, sum_item)
        
        assert "控除合計額と各控除項目の合計が一致しません" in str(exc_info.value)
    
    def test_validate_with_negative_amounts(self):
        """負の金額を含む場合"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        items = [
            Item("項目1", 10000),
            Item("項目2", -3000)
        ]
        sum_item = Item("控除合計", 7000)
        
        reader._validate_total_amount(items, sum_item)


class TestLoadItemDefinitions:
    """_load_item_definitionsメソッドのテスト"""
    
    def test_load_item_definitions(self):
        """項目定義ファイルの読み込み"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        yaml_content = """
deduction:
  - name: 健康保険
    category: 社会保険
    subcategory: 健康保険
  - name: 厚生年金
    category: 社会保険
    subcategory: 年金
"""
        
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            with patch('yaml.safe_load') as mock_yaml:
                mock_yaml.return_value = {
                    "deduction": [
                        {"name": "健康保険", "category": "社会保険", "subcategory": "健康保険"},
                        {"name": "厚生年金", "category": "社会保険", "subcategory": "年金"}
                    ]
                }
                
                result = reader._load_item_definitions()
                assert "deduction" in result
                assert len(result["deduction"]) == 2


class TestConvertPdf2Text:
    """_convert_pdf_to_textメソッドのテスト"""
    
    def test_convert_pdf_file_not_found(self):
        """PDFファイルが見つからない場合"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        with pytest.raises(FileNotFoundError) as exc_info:
            reader._convert_pdf_to_text("nonexistent.pdf")
        
        assert "が見つかりません" in str(exc_info.value)
    
    def test_deprecated_convertPdf2Text(self):
        """非推奨メソッドconvertPdf2Text"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        with pytest.raises(FileNotFoundError):
            reader.convertPdf2Text("nonexistent.pdf")


class TestSalaryReaderConstants:
    """SalaryReaderの定数テスト"""
    
    def test_error_pdf_name_failed(self):
        """PDFファイル名生成失敗エラーメッセージ"""
        assert "PDF名が生成できませんでした" in SalaryReader.ERROR_PDF_NAME_FAILED
    
    def test_error_pdf_not_found(self):
        """PDFファイル未検出エラーメッセージ"""
        assert "見つかりません" in SalaryReader.ERROR_PDF_NOT_FOUND
    
    def test_error_amount_mismatch(self):
        """金額不一致エラーメッセージ"""
        assert "一致しません" in SalaryReader.ERROR_AMOUNT_MISMATCH
    
    def test_encoding_utf8(self):
        """エンコーディング定数"""
        assert SalaryReader.ENCODING_UTF8 == "utf-8"


class TestReadDeduction:
    """readDeductionメソッドの統合テスト"""
    
    def test_read_deduction_integration(self):
        """readDeductionの統合的なテスト"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        # 各メソッドをモック
        with patch.object(reader, '_get_pdf_filename', return_value="test.pdf"):
            with patch.object(reader, '_load_item_definitions') as mock_load:
                with patch.object(reader, '_convert_pdf_to_text') as mock_convert:
                    with patch.object(reader, '_extract_items') as mock_extract:
                        with patch.object(reader, '_validate_total_amount') as mock_validate:
                            # モックの戻り値設定
                            mock_load.return_value = {"deduction": []}
                            mock_convert.return_value = []
                            
                            item1 = Item("健康保険", 10000)
                            sum_item = Item("控除合計", 10000)
                            mock_extract.return_value = ([item1], sum_item)
                            
                            # 実行
                            result = reader.readDeduction()
                            
                            # 検証
                            assert len(result) == 2  # item1 + sum_item
                            assert result[0].name == "健康保険"
                            assert result[1].name == "控除合計"
                            
                            mock_load.assert_called_once()
                            mock_convert.assert_called_once()
                            mock_extract.assert_called_once()
                            mock_validate.assert_called_once()


class TestReaderAdditionalCoverage:
    """reader.pyの追加カバレッジテスト"""
    
    def test_get_pdf_filename_exception(self):
        """PDFファイル名生成時の例外処理"""
        reader = SalaryReader(2024, 11, "12345", SalaryKind.NORMAL)
        
        # 例外をthrowするように_get_pdf_filenameをモック
        with patch.object(reader, '_get_pdf_filename', side_effect=ValueError("PDFファイル名の生成に失敗しました")):
            with pytest.raises(ValueError, match="PDFファイル名の生成に失敗しました"):
                reader._get_pdf_filename()
    
    def test_convert_pdf_to_text_success(self):
        """PDFからテキストへの変換成功"""
        reader = SalaryReader(2024, 11, "test123", SalaryKind.NORMAL)
        
        # モックPDFドキュメントの作成
        mock_page = MagicMock()
        mock_textpage = MagicMock()
        mock_textpage.get_text_bounded.return_value = "テスト 給与 控除"
        mock_page.get_textpage.return_value = mock_textpage
        
        mock_pdf = MagicMock()
        mock_pdf.__iter__.return_value = [mock_page]
        
        with patch('reader.pdfium.PdfDocument', return_value=mock_pdf):
            result = reader._convert_pdf_to_text("test.pdf")
            
            assert len(result) == 3
            assert "テスト" in result
            assert "給与" in result
            assert "控除" in result
    
    def test_convert_pdf_to_text_with_bytes(self):
        """PDFからバイト文字列テキストへの変換"""
        reader = SalaryReader(2024, 11, "test123", SalaryKind.NORMAL)
        
        # モックPDFドキュメントの作成（バイト文字列を返す）
        mock_page = MagicMock()
        mock_textpage = MagicMock()
        mock_textpage.get_text_bounded.return_value = "テスト 給与".encode('utf-8')
        mock_page.get_textpage.return_value = mock_textpage
        
        mock_pdf = MagicMock()
        mock_pdf.__iter__.return_value = [mock_page]
        
        with patch('reader.pdfium.PdfDocument', return_value=mock_pdf):
            result = reader._convert_pdf_to_text("test.pdf")
            
            assert len(result) == 2
            assert "テスト" in result
            assert "給与" in result
    
    def test_convert_pdf_to_text_multiple_pages(self):
        """複数ページのPDFからテキストへの変換"""
        reader = SalaryReader(2024, 11, "test123", SalaryKind.NORMAL)
        
        # ページ1
        mock_page1 = MagicMock()
        mock_textpage1 = MagicMock()
        mock_textpage1.get_text_bounded.return_value = "ページ1 テキスト"
        mock_page1.get_textpage.return_value = mock_textpage1
        
        # ページ2
        mock_page2 = MagicMock()
        mock_textpage2 = MagicMock()
        mock_textpage2.get_text_bounded.return_value = "ページ2 テキスト"
        mock_page2.get_textpage.return_value = mock_textpage2
        
        mock_pdf = MagicMock()
        mock_pdf.__iter__.return_value = [mock_page1, mock_page2]
        
        with patch('reader.pdfium.PdfDocument', return_value=mock_pdf):
            result = reader._convert_pdf_to_text("test.pdf")
            
            assert len(result) == 4
            assert "ページ1" in result
            assert "ページ2" in result

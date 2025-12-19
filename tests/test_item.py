"""
test_item.py
item.pyの単体試験

C0, C1, C2カバレッジ100%を目指したテストケース
"""
import pytest
from item import Item


class TestItemInitialization:
    """Itemクラスの初期化テスト"""
    
    def test_init_with_int_amount(self):
        """整数の金額で初期化"""
        item = Item("交通費", 10000)
        assert item.name == "交通費"
        assert item.amount == 10000
        assert item.category is None
        assert item.subcategory is None
    
    def test_init_with_string_amount(self):
        """文字列の金額で初期化"""
        item = Item("給与", "350000")
        assert item.name == "給与"
        assert item.amount == 350000
    
    def test_init_with_categories(self):
        """カテゴリ付きで初期化"""
        item = Item("健康保険", 15000, "社会保険", "健康保険")
        assert item.name == "健康保険"
        assert item.amount == 15000
        assert item.category == "社会保険"
        assert item.subcategory == "健康保険"
    
    def test_init_with_negative_amount(self):
        """負の金額で初期化"""
        item = Item("控除", -5000)
        assert item.amount == -5000
    
    def test_init_with_zero_amount(self):
        """ゼロ金額で初期化"""
        item = Item("項目", 0)
        assert item.amount == 0


class TestItemString:
    """Itemクラスの文字列表現テスト"""
    
    def test_str_with_short_name(self):
        """短い項目名の文字列表現"""
        item = Item("給与", 300000)
        result = str(item)
        assert "給与" in result
        assert "300,000円" in result
        assert "項目:" in result
        assert "金額:" in result
    
    def test_str_with_long_name(self):
        """長い項目名の文字列表現"""
        item = Item("厚生年金保険料", 50000)
        result = str(item)
        assert "厚生年金保険料" in result
        assert "50,000円" in result


class TestItemSetCategories:
    """set_categoriesメソッドのテスト"""
    
    def test_set_categories(self):
        """カテゴリの設定"""
        item = Item("健康保険", 15000)
        item.set_categories("社会保険", "健康保険")
        assert item.category == "社会保険"
        assert item.subcategory == "健康保険"
    
    def test_set_categories_overwrite(self):
        """既存カテゴリの上書き"""
        item = Item("項目", 10000, "旧大", "旧小")
        item.set_categories("新大", "新小")
        assert item.category == "新大"
        assert item.subcategory == "新小"
    
    def test_deprecated_setCategories(self):
        """非推奨メソッドsetCategoriesのテスト"""
        item = Item("項目", 10000)
        item.setCategories("大項目", "小項目")
        assert item.category == "大項目"
        assert item.subcategory == "小項目"


class TestItemGetCharacterWidth:
    """_get_character_widthメソッドのテスト"""
    
    def test_halfwidth_characters(self):
        """半角文字の幅計算"""
        item = Item("test", 1000)
        width = item._get_character_width("abc")
        assert width == 3
    
    def test_fullwidth_characters(self):
        """全角文字の幅計算"""
        item = Item("test", 1000)
        width = item._get_character_width("あいう")
        assert width == 6
    
    def test_mixed_characters(self):
        """半角と全角混在の幅計算"""
        item = Item("test", 1000)
        width = item._get_character_width("a日本b")
        assert width == 6  # a(1) + 日(2) + 本(2) + b(1) = 6
    
    def test_empty_string(self):
        """空文字列の幅計算"""
        item = Item("test", 1000)
        width = item._get_character_width("")
        assert width == 0
    
    def test_numbers_and_symbols(self):
        """数字と記号の幅計算"""
        item = Item("test", 1000)
        width = item._get_character_width("123!@#")
        assert width == 6
    
    def test_deprecated_getSpaces(self):
        """非推奨メソッドgetSpacesのテスト"""
        item = Item("test", 1000)
        width = item.getSpaces("あいう")
        assert width == 6


class TestItemAlignText:
    """_align_textメソッドのテスト"""
    
    def test_align_left_with_halfwidth(self):
        """半角文字の左寄せ"""
        item = Item("test", 1000)
        result = item._align_text("abc", 10, Item.ALIGN_LEFT)
        assert result == "abc       "
        assert len(result) == 10
    
    def test_align_right_with_halfwidth(self):
        """半角文字の右寄せ"""
        item = Item("test", 1000)
        result = item._align_text("abc", 10, Item.ALIGN_RIGHT)
        assert result == "       abc"
        assert len(result) == 10
    
    def test_align_left_with_fullwidth(self):
        """全角文字の左寄せ"""
        item = Item("test", 1000)
        result = item._align_text("あい", 10, Item.ALIGN_LEFT)
        # あい は4幅、残り6スペース
        assert result == "あい      "
    
    def test_align_right_with_fullwidth(self):
        """全角文字の右寄せ"""
        item = Item("test", 1000)
        result = item._align_text("あい", 10, Item.ALIGN_RIGHT)
        assert result == "      あい"
    
    def test_align_with_mixed_characters(self):
        """混在文字の配置"""
        item = Item("test", 1000)
        result = item._align_text("a日", 10, Item.ALIGN_LEFT)
        # a(1) + 日(2) = 3幅、残り7スペース
        assert result == "a日       "
    
    def test_text_longer_than_width(self):
        """文字列が幅より長い場合"""
        item = Item("test", 1000)
        result = item._align_text("abcdefghij", 5, Item.ALIGN_LEFT)
        # 幅より長い場合はそのまま返す
        assert result == "abcdefghij"
    
    def test_text_equal_to_width(self):
        """文字列が幅と同じ場合"""
        item = Item("test", 1000)
        result = item._align_text("abcde", 5, Item.ALIGN_LEFT)
        assert result == "abcde"
    
    def test_custom_fill_character(self):
        """カスタム埋め文字"""
        item = Item("test", 1000)
        result = item._align_text("abc", 10, Item.ALIGN_LEFT, "*")
        assert result == "abc*******"
    
    def test_default_alignment(self):
        """デフォルトの配置（左寄せ）"""
        item = Item("test", 1000)
        result = item._align_text("test", 10)
        assert result == "test      "
    
    def test_deprecated_alignText(self):
        """非推奨メソッドalignTextのテスト"""
        item = Item("test", 1000)
        result = item.alignText("abc", 10, Item.ALIGN_RIGHT)
        assert result == "       abc"


class TestItemConstants:
    """Item定数のテスト"""
    
    def test_default_display_width(self):
        """デフォルト表示幅の値"""
        assert Item.DEFAULT_DISPLAY_WIDTH == 16
    
    def test_fullwidth_chars(self):
        """全角文字識別子の値"""
        assert Item.FULLWIDTH_CHARS == "FWA"
    
    def test_fullwidth_size(self):
        """全角文字のサイズ"""
        assert Item.FULLWIDTH_SIZE == 2
    
    def test_halfwidth_size(self):
        """半角文字のサイズ"""
        assert Item.HALFWIDTH_SIZE == 1
    
    def test_align_left(self):
        """左寄せ定数"""
        assert Item.ALIGN_LEFT == -1
    
    def test_align_right(self):
        """右寄せ定数"""
        assert Item.ALIGN_RIGHT == 1


class TestItemEdgeCases:
    """Itemクラスのエッジケーステスト"""
    
    def test_very_large_amount(self):
        """非常に大きな金額"""
        item = Item("給与", 999999999)
        assert item.amount == 999999999
        result = str(item)
        assert "999,999,999円" in result
    
    def test_japanese_name_with_numbers(self):
        """数字を含む日本語項目名"""
        item = Item("第1控除項目", 5000)
        assert item.name == "第1控除項目"
    
    def test_name_with_spaces(self):
        """スペースを含む項目名"""
        item = Item("特別 控除", 3000)
        assert item.name == "特別 控除"

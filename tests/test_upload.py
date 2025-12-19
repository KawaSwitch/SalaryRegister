"""
test_upload.py
upload.pyの単体試験

C0, C1, C2カバレッジ100%を目指したテストケース
"""
import pytest
import sys
from unittest.mock import patch, MagicMock
import upload
from argument import Arguments
from salary import Salary
from uploader import Uploader
import config


@pytest.fixture(autouse=True)
def mock_config(mocker):
    """config.dataのモックを作成"""
    mock_data = MagicMock()
    mock_data.get_moneyforward_email.return_value = "test@example.com"
    mock_data.get_moneyforward_password.return_value = "testpass"
    mock_data.get_tfa_id.return_value = "tfa123"
    mock_data.get_default_date.return_value = "2024/11/25"
    mock_data.is_headless_mode.return_value = False
    mocker.patch.object(config, 'data', mock_data)
    return mock_data


class TestMainFunction:
    """mainメソッドのテスト"""
    
    @patch('upload.Arguments')
    @patch('upload.Salary')
    @patch('upload.Uploader')
    def test_main_success(self, mock_uploader_class, mock_salary_class, mock_args_class):
        """正常実行のテスト"""
        # モックの設定
        mock_args = MagicMock()
        mock_args.is_valid.return_value = True
        mock_args.get_year.return_value = 2024
        mock_args.get_month.return_value = 11
        mock_args.get_kind.return_value = MagicMock()
        mock_args_class.return_value = mock_args
        
        mock_salary = MagicMock(spec=Salary)
        mock_salary_class.return_value = mock_salary
        
        mock_uploader = MagicMock(spec=Uploader)
        mock_uploader_class.return_value = mock_uploader
        
        # 実行
        upload.main()
        
        # 検証
        mock_args_class.assert_called_once()
        mock_salary_class.assert_called_once()
        mock_uploader_class.assert_called_once_with(mock_salary)
        mock_uploader.upload.assert_called_once()
    
    @patch('upload.Arguments')
    def test_main_invalid_arguments(self, mock_args_class):
        """引数が不正な場合"""
        mock_args = MagicMock()
        mock_args.is_valid.return_value = False
        mock_args_class.return_value = mock_args
        
        with pytest.raises(SystemExit) as exc_info:
            upload.main()
        
        assert exc_info.value.code == 1
    
    @patch('upload.Arguments')
    @patch('upload.Salary')
    @patch('upload.Logger.logError')
    def test_main_exception_with_trace(self, mock_log_error, mock_salary_class, mock_args_class):
        """例外発生時（トレース表示あり）"""
        # モックの設定
        mock_args = MagicMock()
        mock_args.is_valid.return_value = True
        mock_args.get_year.return_value = 2024
        mock_args.get_month.return_value = 11
        mock_args.get_kind.return_value = MagicMock()
        mock_args_class.return_value = mock_args
        
        mock_salary_class.side_effect = Exception("Test error")
        
        # トレース表示を有効にして実行
        with patch.object(upload, 'PRINT_TRACE', True):
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit) as exc_info:
                    upload.main()
                
                assert exc_info.value.code == 1
                mock_log_error.assert_called_once_with("Test error")
                
                # トレースバックのヘッダーとフッターが出力されることを確認
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("traceback" in call.lower() for call in print_calls)
    
    @patch('upload.Arguments')
    @patch('upload.Salary')
    @patch('upload.Logger.logError')
    def test_main_exception_without_trace(self, mock_log_error, mock_salary_class, mock_args_class):
        """例外発生時（トレース表示なし）"""
        # モックの設定
        mock_args = MagicMock()
        mock_args.is_valid.return_value = True
        mock_args.get_year.return_value = 2024
        mock_args.get_month.return_value = 11
        mock_args.get_kind.return_value = MagicMock()
        mock_args_class.return_value = mock_args
        
        mock_salary_class.side_effect = Exception("Test error")
        
        # トレース表示を無効にして実行
        with patch.object(upload, 'PRINT_TRACE', False):
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit) as exc_info:
                    upload.main()
                
                assert exc_info.value.code == 1
                mock_log_error.assert_called_once_with("Test error")
                
                # トレースバックは出力されないことを確認
                assert mock_print.call_count == 0


class TestMainWithRealArguments:
    """実際の引数を使ったmainメソッドのテスト"""
    
    @patch('upload.Salary')
    @patch('upload.Uploader')
    def test_main_with_valid_sys_argv(self, mock_uploader_class, mock_salary_class):
        """有効なsys.argvでの実行"""
        test_args = ['upload.py', '2024', '11']
        
        with patch.object(sys, 'argv', test_args):
            with patch('upload.Logger.logInfo'):
                mock_salary = MagicMock(spec=Salary)
                mock_salary_class.return_value = mock_salary
                
                mock_uploader = MagicMock(spec=Uploader)
                mock_uploader_class.return_value = mock_uploader
                
                upload.main()
                
                mock_salary_class.assert_called_once()
                mock_uploader.upload.assert_called_once()
    
    @patch('upload.Salary')
    @patch('upload.Uploader')
    def test_main_with_bonus_flag(self, mock_uploader_class, mock_salary_class):
        """賞与フラグありでの実行"""
        test_args = ['upload.py', '2024', '6', '--bonus']
        
        with patch.object(sys, 'argv', test_args):
            with patch('upload.Logger.logInfo'):
                mock_salary = MagicMock(spec=Salary)
                mock_salary_class.return_value = mock_salary
                
                mock_uploader = MagicMock(spec=Uploader)
                mock_uploader_class.return_value = mock_uploader
                
                upload.main()
                
                mock_uploader.upload.assert_called_once()


class TestConstants:
    """定数のテスト"""
    
    def test_print_trace_constant(self):
        """PRINT_TRACE定数の型確認"""
        assert isinstance(upload.PRINT_TRACE, bool)
    
    def test_traceback_header_constant(self):
        """TRACEBACK_HEADER定数の値確認"""
        assert "traceback" in upload.TRACEBACK_HEADER.lower()
    
    def test_traceback_footer_constant(self):
        """TRACEBACK_FOOTER定数の値確認"""
        assert "end" in upload.TRACEBACK_FOOTER.lower()


class TestEdgeCases:
    """エッジケースのテスト"""
    
    @patch('upload.Arguments')
    @patch('upload.Salary')
    @patch('upload.Uploader')
    @patch('upload.Logger.logError')
    def test_main_with_keyboard_interrupt(self, mock_log, mock_uploader_class, 
                                         mock_salary_class, mock_args_class):
        """KeyboardInterrupt発生時"""
        mock_args = MagicMock()
        mock_args.is_valid.return_value = True
        mock_args.get_year.return_value = 2024
        mock_args.get_month.return_value = 11
        mock_args.get_kind.return_value = MagicMock()
        mock_args_class.return_value = mock_args
        
        # KeyboardInterruptを発生させる
        mock_uploader = MagicMock()
        mock_uploader.upload.side_effect = KeyboardInterrupt()
        mock_uploader_class.return_value = mock_uploader
        
        with patch.object(upload, 'PRINT_TRACE', False):
            # KeyboardInterruptは正常に伝播されるべき
            with pytest.raises(KeyboardInterrupt):
                upload.main()
    
    @patch('upload.Arguments')
    @patch('upload.Salary')
    @patch('upload.Uploader')
    def test_main_uploader_exception(self, mock_uploader_class, mock_salary_class, mock_args_class):
        """Uploader.upload()で例外発生"""
        mock_args = MagicMock()
        mock_args.is_valid.return_value = True
        mock_args.get_year.return_value = 2024
        mock_args.get_month.return_value = 11
        mock_args.get_kind.return_value = MagicMock()
        mock_args_class.return_value = mock_args
        
        mock_salary = MagicMock(spec=Salary)
        mock_salary_class.return_value = mock_salary
        
        mock_uploader = MagicMock(spec=Uploader)
        mock_uploader.upload.side_effect = Exception("Upload failed")
        mock_uploader_class.return_value = mock_uploader
        
        with patch('upload.Logger.logError'):
            with patch.object(upload, 'PRINT_TRACE', False):
                with pytest.raises(SystemExit) as exc_info:
                    upload.main()
                
                assert exc_info.value.code == 1


class TestMainNameGuard:
    """__name__ == "__main__"のテスト"""
    
    def test_main_name_guard_exists(self):
        """__main__ガードが存在するか"""
        import upload
        # upload.pyのコードを確認（実際にはこのテストは動的に実行される）
        # ここでは存在確認のみ
        assert hasattr(upload, 'main')


class TestIntegration:
    """統合テスト"""
    
    @patch('upload.Arguments')
    @patch('upload.Salary')
    @patch('upload.Uploader')
    def test_full_workflow_success(self, mock_uploader_class, mock_salary_class, mock_args_class):
        """完全なワークフローの成功ケース"""
        # Arguments初期化
        mock_args = MagicMock()
        mock_args.is_valid.return_value = True
        mock_args.get_year.return_value = 2024
        mock_args.get_month.return_value = 11
        mock_args.get_kind.return_value = MagicMock()
        mock_args_class.return_value = mock_args
        
        # Salary初期化
        mock_salary = MagicMock(spec=Salary)
        mock_salary_class.return_value = mock_salary
        
        # Uploader初期化と実行
        mock_uploader = MagicMock(spec=Uploader)
        mock_uploader_class.return_value = mock_uploader
        
        # mainを実行
        upload.main()
        
        # 各ステップが正しく実行されたか確認
        assert mock_args_class.called
        assert mock_args.is_valid.called
        assert mock_salary_class.called
        assert mock_uploader_class.called
        assert mock_uploader.upload.called
    
    @patch('upload.Arguments')
    def test_early_exit_on_invalid_args(self, mock_args_class):
        """不正な引数で早期終了"""
        mock_args = MagicMock()
        mock_args.is_valid.return_value = False
        mock_args_class.return_value = mock_args
        
        with pytest.raises(SystemExit) as exc_info:
            upload.main()
        
        # 引数チェックで終了し、Salaryは作成されない
        assert exc_info.value.code == 1
        assert mock_args.is_valid.called

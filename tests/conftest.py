"""
conftest.py
pytestの設定と共通フィクスチャ
"""
import pytest
import sys
import os


# pytestの実行前に設定ファイルを準備
def pytest_configure(config):
    """pytestの初期化時に実行される"""
    # userdata/config.iniが存在しない場合はテスト用に作成
    userdata_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "userdata")
    config_path = os.path.join(userdata_path, "config.ini")
    
    # userdataディレクトリがない場合は作成
    os.makedirs(userdata_path, exist_ok=True)
    
    # config.iniがない場合はテスト用に作成
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("[DEFAULT]\n")
            f.write("PdfPassword=test_pdf_pass\n")
            f.write("MfMailAddress=test@example.com\n")
            f.write("MfPassword=test_mf_pass\n")
            f.write("EmployeeNumber=12345\n")
            f.write("UseHeadlessMode=true\n")
            f.write("DefaultDate=25\n")
            f.write("TfaId=TEST_TFA_ID\n")

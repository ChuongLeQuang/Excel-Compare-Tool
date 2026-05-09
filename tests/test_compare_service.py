import sys
import os

# Đảm bảo Python nhận diện được thư mục gốc của dự án khi chạy trực tiếp file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import pytest
import numpy as np

from src.models.compare_config import (
    CompareConfig, SheetConfig, CompareRules, ActionConfig
)
from src.services.compare_service import ExcelCompareService

@pytest.fixture
def workspace(tmp_path):
    return tmp_path


def test_multi_key_concat_mapping(workspace):
    """
    EN: Test mapping with multiple keys (Concatenate) and different column names.
    VI: Kiểm thử ánh xạ nhiều khóa (Concatenate) với tên cột ở 2 file khác nhau.
    """
    print("\n[Kịch bản 1] Kiểm thử ánh xạ nhiều khóa (Concatenate) với tên cột ở 2 file khác nhau.")
    src_path = os.path.join(workspace, "src1.xlsx")
    cmp_path = os.path.join(workspace, "cmp1.xlsx")
    
    pd.DataFrame([
        {"S_ID": 1, "S_Name": "Alice", "Status": ""},
        {"S_ID": 2, "S_Name": "Bob", "Status": ""}
    ]).to_excel(src_path, index=False)
    
    pd.DataFrame([
        {"C_ID": 1, "C_Name": "Alice", "Note": "OK"},
        {"C_ID": 3, "C_Name": "Charlie", "Note": "New"}
    ]).to_excel(cmp_path, index=False)

    config = CompareConfig(
        source=SheetConfig(src_path, "Sheet1", 1, ["S_ID", "S_Name"], ["S_ID", "S_Name", "Status"]),
        compare=SheetConfig(cmp_path, "Sheet1", 1, ["C_ID", "C_Name"], ["C_ID", "C_Name", "Note"]),
        compare_logic="concat", separator="|",
        rules=CompareRules(
            on_match_source=[ActionConfig("copy", "Status", source_col="Note")],
            on_unmatch_source=[ActionConfig("assign", "Status", value="Not Found")]
        )
    )

    df_src, df_cmp = ExcelCompareService(config).process_comparison()
    
    # Khóa 1|Alice khớp -> Gán chữ OK
    assert df_src.loc[df_src["S_ID"] == 1, "Status"].iloc[0] == "OK"
    # Khóa 2|Bob không khớp -> Gán Not Found
    assert df_src.loc[df_src["S_ID"] == 2, "Status"].iloc[0] == "Not Found"


def test_duplicate_keys_broadcasting(workspace):
    """
    EN: Test if duplicate keys in source are safely updated without ValueError.
    VI: Kiểm thử khóa trùng lặp trong source được cập nhật an toàn không văng lỗi.
    """
    print("\n[Kịch bản 2] Kiểm thử dòng trùng lặp khóa trong source được cập nhật đồng loạt (Broadcasting) an toàn.")
    src_path = os.path.join(workspace, "src2.xlsx")
    cmp_path = os.path.join(workspace, "cmp2.xlsx")
    
    pd.DataFrame([
        {"ID": 1, "Amount": 100, "Status": ""},
        {"ID": 1, "Amount": 200, "Status": ""}, # Duplicate key
        {"ID": 2, "Amount": 300, "Status": ""}
    ]).to_excel(src_path, index=False)
    
    pd.DataFrame([
        {"ID": 1, "Note": "Paid"}
    ]).to_excel(cmp_path, index=False)
    
    config = CompareConfig(
        source=SheetConfig(src_path, "Sheet1", 1, ["ID"], ["ID", "Amount", "Status"]),
        compare=SheetConfig(cmp_path, "Sheet1", 1, ["ID"], ["ID", "Note"]),
        compare_logic="concat", separator="|",
        rules=CompareRules(
            on_match_source=[ActionConfig("copy", "Status", source_col="Note")]
        )
    )
    
    df_src, df_cmp = ExcelCompareService(config).process_comparison()
    
    matched_rows = df_src[df_src["ID"] == 1]
    assert len(matched_rows) == 2
    # Cả 2 dòng có ID = 1 đều phải được copy chữ "Paid" sang
    assert all(matched_rows["Status"] == "Paid")
    # Dòng ID = 2 rỗng
    assert pd.isna(df_src.loc[df_src["ID"] == 2, "Status"].iloc[0])


def test_nan_and_float_key_parsing(workspace):
    """
    EN: Test parsing of keys containing NaNs and float representations of integers.
    VI: Kiểm thử xử lý khóa chứa NaN và số nguyên bị ép kiểu thành số thập phân (.0).
    """
    print("\n[Kịch bản 3] Kiểm thử xử lý ghép khóa rác chứa ô trống (NaN) và số nguyên bị tự ép thành số thực (.0).")
    src_path = os.path.join(workspace, "src3.xlsx")
    cmp_path = os.path.join(workspace, "cmp3.xlsx")
    
    pd.DataFrame([
        {"ID": 1.0, "Name": np.nan, "Status": ""},
        {"ID": 2.0, "Name": "Bob", "Status": ""}
    ]).to_excel(src_path, index=False)
    
    pd.DataFrame([
        {"ID": 1, "Name": np.nan, "Result": "Pass"},
        {"ID": 2, "Name": "Bob", "Result": "Fail"}
    ]).to_excel(cmp_path, index=False)
    
    config = CompareConfig(
        source=SheetConfig(src_path, "Sheet1", 1, ["ID", "Name"], ["ID", "Name", "Status"]),
        compare=SheetConfig(cmp_path, "Sheet1", 1, ["ID", "Name"], ["ID", "Name", "Result"]),
        compare_logic="concat", separator="_||_",
        rules=CompareRules(
            on_match_source=[ActionConfig("copy", "Status", source_col="Result")],
            on_match_compare=[ActionConfig("assign", "Result", value="Checked")]
        )
    )
    
    df_src, df_cmp = ExcelCompareService(config).process_comparison()
    
    # Source: 1.0 và NaN -> Khóa chuẩn phải là "1_||_"
    # Compare: 1 và NaN -> Khóa chuẩn phải là "1_||_" -> Khớp!
    assert df_src.loc[df_src["ID"] == 1.0, "Status"].iloc[0] == "Pass"
    assert df_src.loc[df_src["ID"] == 2.0, "Status"].iloc[0] == "Fail"
    
    # Kiểm tra Assign (gán cả 2 dòng Result bên compare bằng Checked)
    assert all(df_cmp["Result"] == "Checked")


def test_assign_both_and_unmatch_logic(workspace):
    """
    EN: Test Assign Both and Unmatch actions.
    VI: Kiểm thử các hành động gán đồng thời và không khớp.
    """
    print("\n[Kịch bản 4] Kiểm thử hành động gán song song (Assign Both) và các trường hợp không tồn tại (Unmatch).")
    src_path = os.path.join(workspace, "src4.xlsx")
    cmp_path = os.path.join(workspace, "cmp4.xlsx")
    
    pd.DataFrame([
        {"ID": 1, "Status": "", "Flag": ""},
        {"ID": 2, "Status": "", "Flag": ""} # Có ở Source, không có ở Compare
    ]).to_excel(src_path, index=False)
    
    pd.DataFrame([
        {"ID": 1, "Note": "", "Flag": ""},
        {"ID": 3, "Note": "", "Flag": ""} # Có ở Compare, không có ở Source
    ]).to_excel(cmp_path, index=False)
    
    config = CompareConfig(
        source=SheetConfig(src_path, "Sheet1", 1, ["ID"], ["ID", "Status", "Flag"]),
        compare=SheetConfig(cmp_path, "Sheet1", 1, ["ID"], ["ID", "Note", "Flag"]),
        compare_logic="concat", separator="|",
        rules=CompareRules(
            on_match_source=[ActionConfig("assign", "Flag", value="Checked")],
            on_match_compare=[ActionConfig("assign", "Flag", value="Checked")],
            on_unmatch_source=[ActionConfig("assign", "Status", value="Not Found")],
            on_unmatch_compare=[ActionConfig("assign", "Note", value="Extra")]
        )
    )
    
    df_src, df_cmp = ExcelCompareService(config).process_comparison()
    
    # ID = 1 (Match): Cả 2 file đều phải được gán "Checked" vào cột "Flag"
    assert df_src.loc[df_src["ID"] == 1, "Flag"].iloc[0] == "Checked"
    assert df_cmp.loc[df_cmp["ID"] == 1, "Flag"].iloc[0] == "Checked"
    
    # ID = 2 (Unmatch Source): Gán "Not Found" vào Status
    assert df_src.loc[df_src["ID"] == 2, "Status"].iloc[0] == "Not Found"
    
    # ID = 3 (Unmatch Compare): Gán "Extra" vào Note
    assert df_cmp.loc[df_cmp["ID"] == 3, "Note"].iloc[0] == "Extra"

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
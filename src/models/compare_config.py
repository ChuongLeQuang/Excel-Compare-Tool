from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ActionConfig:
    """
    EN: Configuration for actions to perform on matched/unmatched rows.
    VI: Cấu hình cho các hành động cần thực hiện trên các dòng khớp/không khớp.
    """
    action_type: str  # 'copy' (từ file khác sang) hoặc 'assign' (gán giá trị/công thức cố định)
    target_col: str
    source_col: Optional[str] = None
    value: Optional[str] = None


@dataclass
class SheetConfig:
    """
    EN: Configuration for a specific Excel sheet.
    VI: Cấu hình cho một sheet Excel cụ thể.
    """
    file_path: str
    sheet_name: str
    header_row: int  # Dòng chứa header (0-indexed base trong pandas)
    key_cols: List[str]  # Các cột dùng làm khóa đối chiếu
    target_cols: List[str]  # Các cột quan tâm/cần giữ lại


@dataclass
class CompareRules:
    """
    EN: Rules for updating data based on comparison results.
    VI: Tập quy tắc cập nhật dữ liệu dựa trên kết quả đối chiếu.
    """
    on_match_source: List[ActionConfig] = field(default_factory=list)
    on_match_compare: List[ActionConfig] = field(default_factory=list)
    on_unmatch_source: List[ActionConfig] = field(default_factory=list)
    on_unmatch_compare: List[ActionConfig] = field(default_factory=list)


@dataclass
class CompareConfig:
    """
    EN: Master configuration linking source, compare configs and rules.
    VI: Cấu hình tổng thể liên kết nguồn, đối chiếu và các quy tắc.
    """
    source: SheetConfig
    compare: SheetConfig
    rules: CompareRules
    compare_logic: str = "concat"  # "concat", "and", "or"
    separator: str = "|"
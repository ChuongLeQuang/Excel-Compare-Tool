import logging
import pandas as pd
from typing import Tuple

from src.models.compare_config import CompareConfig, ActionConfig

logger = logging.getLogger(__name__)


class ExcelCompareService:
    """
    EN: Service to handle logic for comparing two Excel datasets.
    VI: Dịch vụ xử lý logic đối chiếu hai tập dữ liệu Excel.
    """

    def __init__(self, config: CompareConfig):
        self.config = config

    def _apply_actions(
        self,
        df_target: pd.DataFrame,
        df_source: pd.DataFrame,
        keys: pd.Index,
        actions: list[ActionConfig]
    ) -> None:
        """
        EN: Apply a list of actions to a DataFrame based on matched keys.
        VI: Áp dụng danh sách hành động lên DataFrame dựa trên các khóa đã khớp.
        """
        # Tạo một bản sao source với index duy nhất (unique) để tránh lỗi khi broadcast gán dữ liệu
        df_source_unique = None
        if df_source is not None:
            df_source_unique = df_source[~df_source.index.duplicated(keep='first')]

        for action in actions:
            try:
                # Ép kiểu cột đích về 'object' để có thể chứa bất kỳ loại dữ liệu nào (String, Float, NaN)
                if action.target_col in df_target.columns:
                    if not pd.api.types.is_object_dtype(df_target[action.target_col]):
                        df_target[action.target_col] = df_target[action.target_col].astype('object')

                if action.action_type == "copy":
                    if df_source_unique is not None and action.source_col and action.source_col in df_source_unique.columns:
                        df_target.loc[keys, action.target_col] = df_source_unique.loc[keys, action.source_col]
                    else:
                        logger.warning(f"Source column '{action.source_col}' not found or source DataFrame is None.")
                
                elif action.action_type == "assign":
                    df_target.loc[keys, action.target_col] = action.value
            except Exception as e:
                logger.error(f"Error applying action {action}: {str(e)}")

    def process_comparison(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        EN: Execute the comparison and rule assignment logic.
        VI: Thực thi logic đối chiếu và gán quy tắc.
        """
        try:
            # 1. Read Excel files / Đọc file Excel
            # header index is 0-based. If user says header is row 3, index is 2.
            df_src = pd.read_excel(
                self.config.source.file_path,
                sheet_name=self.config.source.sheet_name,
                header=self.config.source.header_row - 1
            )
            df_cmp = pd.read_excel(
                self.config.compare.file_path,
                sheet_name=self.config.compare.sheet_name,
                header=self.config.compare.header_row - 1
            )
            
            # 2. Filter target columns (Add missing target columns if they don't exist yet to avoid KeyError)
            for col in self.config.source.target_cols:
                if col not in df_src.columns:
                    df_src[col] = None
                    
            for col in self.config.compare.target_cols:
                if col not in df_cmp.columns:
                    df_cmp[col] = None

            # 3. Tạo Match Key thống nhất cho cả 2 file (Hỗ trợ Concatenate, AND, OR)
            src_keys = self.config.source.key_cols
            cmp_keys = self.config.compare.key_cols
            logic = self.config.compare_logic
            sep = self.config.separator if logic == "concat" else "_||_"

            def _build_match_key(df: pd.DataFrame, cols: list, separator: str):
                existing_cols = [c for c in cols if c in df.columns]
                if not existing_cols:
                    return pd.Series(index=df.index, dtype=str)
                
                str_df = df[existing_cols].copy()
                for c in existing_cols:
                    str_df[c] = str_df[c].fillna('').astype(str)
                    str_df[c] = str_df[c].str.replace(r'\.0$', '', regex=True)
                    str_df[c] = str_df[c].str.replace(r'^(nan|None)$', '', regex=True)
                return str_df.astype(str).agg(separator.join, axis=1)

            df_src["__match_key__"] = _build_match_key(df_src, src_keys, sep)
            df_cmp["__match_key__"] = _build_match_key(df_cmp, cmp_keys, sep)

            df_src.set_index("__match_key__", inplace=True, drop=False)
            df_cmp.set_index("__match_key__", inplace=True, drop=False)

            # 4. Tìm các phần giao và phần lệch (Lấy index unique để tăng tốc độ so sánh)
            src_idx = df_src.index.unique()
            cmp_idx = df_cmp.index.unique()
            
            matched_keys = src_idx.intersection(cmp_idx)
            src_only_keys = src_idx.difference(cmp_idx)
            cmp_only_keys = cmp_idx.difference(src_idx)

            logger.info(f"Matched: {len(matched_keys)}, Source Only: {len(src_only_keys)}, Compare Only: {len(cmp_only_keys)}")

            # 5. Apply Match Rules / Áp dụng quy tắc khi khớp
            self._apply_actions(df_src, df_cmp, matched_keys, self.config.rules.on_match_source)
            self._apply_actions(df_cmp, df_src, matched_keys, self.config.rules.on_match_compare)

            # 6. Apply Unmatch Source Rules / Áp dụng quy tắc khi có ở Source nhưng không có ở Compare
            self._apply_actions(df_src, None, src_only_keys, self.config.rules.on_unmatch_source)

            # 7. Apply Unmatch Compare Rules / Áp dụng quy tắc khi có ở Compare nhưng không có ở Source
            self._apply_actions(df_cmp, None, cmp_only_keys, self.config.rules.on_unmatch_compare)

            # 8. Reset indexes back to normal / Khôi phục lại cấu trúc DataFrame nguyên bản
            df_src.reset_index(drop=True, inplace=True)
            df_cmp.reset_index(drop=True, inplace=True)
            
            # Bỏ filter để trả về toàn bộ dữ liệu, hỗ trợ ghi đè an toàn và hiển thị UI
            df_src_final = df_src.drop(columns=["__match_key__"], errors="ignore")
            df_cmp_final = df_cmp.drop(columns=["__match_key__"], errors="ignore")

            return df_src_final, df_cmp_final

        except Exception as e:
            # Bắt lỗi cụ thể thay vì chung chung nếu có thể, log lại lỗi
            logger.error(f"Failed to process comparison: {str(e)}")
            raise
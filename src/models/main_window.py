import pandas as pd
import os
import sys
import json
import webbrowser
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QPushButton, QLineEdit, QLabel, QComboBox, QListWidget, 
    QAbstractItemView, QTabWidget, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QHeaderView, QSpinBox, QProgressBar,
    QDialog, QTextBrowser, QApplication 
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.models.compare_config import CompareConfig, SheetConfig, CompareRules, ActionConfig
from src.services.compare_worker import CompareWorker
from src.services.update_checker import UpdateCheckerWorker

class MainWindow(QMainWindow):
    """
    EN: Main GUI Window for Excel Comparison Tool.
    VI: Cửa sổ giao diện chính cho Công cụ so sánh Excel.
    """
    
    # CẤU HÌNH PHIÊN BẢN (Thay đổi REPO_URL thành link Github của bạn)
    APP_VERSION = "1.0.0"
    REPO_URL = "https://github.com/TÊN_TÀI_KHOẢN_CỦA_BẠN/TÊN_REPO_CỦA_BẠN"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Excel Compare Tool - v{self.APP_VERSION}")
        self.resize(1000, 700)
        
        # Lưu trữ danh sách cột thực tế để làm Dropdown cho Tab Rules
        self.src_cols = []
        self.cmp_cols = []
        self.init_ui()

    def init_ui(self):
        """
        EN: Initialize user interface components.
        VI: Khởi tạo các thành phần giao diện người dùng.
        """
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Cấu hình đường dẫn an toàn để nạp Icon
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            
        icon_path = os.path.join(base_dir, "assets", "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base_dir, "assets", "icon.png")
            
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Tabs setup
        self.tabs = QTabWidget()
        self.tab_config = QWidget()
        self.tab_rules = QWidget()
        self.tab_results = QWidget()

        self.tabs.addTab(self.tab_config, "1. Configuration")
        self.tabs.addTab(self.tab_rules, "2. Rules Mapping")
        self.tabs.addTab(self.tab_results, "3. Results")

        self.main_layout.addWidget(self.tabs)

        # Build individual tabs
        self._build_config_tab()
        self._build_rules_tab()
        self._build_results_tab()

        # Bottom action buttons
        self.btn_layout = QHBoxLayout()
        self.btn_help = QPushButton("Hướng dẫn sử dụng")
        self.btn_run = QPushButton("Run Compare")
        self.btn_save_config = QPushButton("Save Config")
        self.btn_load_config = QPushButton("Load Config")
        
        self.btn_layout.addWidget(self.btn_help)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_save_config)
        self.btn_layout.addWidget(self.btn_load_config)
        self.btn_layout.addWidget(self.btn_run)
        self.main_layout.addLayout(self.btn_layout)

        # Signals
        self.btn_run.clicked.connect(self.run_comparison)
        self.btn_save_config.clicked.connect(self.save_config)
        self.btn_load_config.clicked.connect(self.load_config)
        self.btn_help.clicked.connect(self.show_help)

        # Progress Bar & Status (ẩn đi ở trạng thái mặc định)
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addWidget(self.progress_bar)

        # Kiểm tra phiên bản mới
        self._check_for_updates()

    def _check_for_updates(self):
        self.update_worker = UpdateCheckerWorker(self.APP_VERSION, self.REPO_URL)
        self.update_worker.update_available.connect(self._on_update_available)
        self.update_worker.start()

    def _on_update_available(self, latest_version: str, release_url: str):
        reply = QMessageBox.question(
            self, "Cập nhật phần mềm",
            f"Đã có phiên bản mới: <b>{latest_version}</b>.<br>"
            f"Bạn đang dùng phiên bản: <b>v{self.APP_VERSION}</b>.<br><br>"
            f"Bạn có muốn tải phiên bản mới ngay không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            webbrowser.open(release_url)

    # ---------------------------------------------------------
    # TAB 1: CONFIGURATION
    # ---------------------------------------------------------
    def _build_config_tab(self):
        layout = QVBoxLayout(self.tab_config)
        file_layout = QHBoxLayout()

        # Source Group
        self.grp_source = QGroupBox("Source Configuration")
        src_layout = QVBoxLayout()
        self.src_file_input = QLineEdit()
        self.src_file_input.setReadOnly(True)
        self.btn_src_file = QPushButton("Browse Source...")
        self.btn_src_file.clicked.connect(lambda: self._select_file("source"))
        
        self.src_sheet_combo = QComboBox()
        self.src_header_spin = QSpinBox()
        self.src_header_spin.setRange(1, 100)
        self.src_header_spin.setValue(1)
        self.src_header_spin.valueChanged.connect(lambda: self._load_columns("source"))

        self.src_targets_list = QListWidget()
        self.src_targets_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        src_layout.addWidget(QLabel("File Path:"))
        src_layout.addWidget(self.src_file_input)
        src_layout.addWidget(self.btn_src_file)
        src_layout.addWidget(QLabel("Select Sheet:"))
        src_layout.addWidget(self.src_sheet_combo)
        src_layout.addWidget(QLabel("Header Row (1-based):"))
        src_layout.addWidget(self.src_header_spin)
        src_layout.addWidget(QLabel("Target Columns (Keep/Update):"))
        src_layout.addWidget(self.src_targets_list)
        self.grp_source.setLayout(src_layout)

        # Compare Group
        self.grp_compare = QGroupBox("Compare Configuration")
        cmp_layout = QVBoxLayout()
        self.cmp_file_input = QLineEdit()
        self.cmp_file_input.setReadOnly(True)
        self.btn_cmp_file = QPushButton("Browse Compare...")
        self.btn_cmp_file.clicked.connect(lambda: self._select_file("compare"))
        
        self.cmp_sheet_combo = QComboBox()
        self.cmp_header_spin = QSpinBox()
        self.cmp_header_spin.setRange(1, 100)
        self.cmp_header_spin.setValue(1)
        self.cmp_header_spin.valueChanged.connect(lambda: self._load_columns("compare"))

        self.cmp_targets_list = QListWidget()
        self.cmp_targets_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        cmp_layout.addWidget(QLabel("File Path:"))
        cmp_layout.addWidget(self.cmp_file_input)
        cmp_layout.addWidget(self.btn_cmp_file)
        cmp_layout.addWidget(QLabel("Select Sheet:"))
        cmp_layout.addWidget(self.cmp_sheet_combo)
        cmp_layout.addWidget(QLabel("Header Row (1-based):"))
        cmp_layout.addWidget(self.cmp_header_spin)
        cmp_layout.addWidget(QLabel("Target Columns (Keep/Update):"))
        cmp_layout.addWidget(self.cmp_targets_list)
        self.grp_compare.setLayout(cmp_layout)

        file_layout.addWidget(self.grp_source)
        file_layout.addWidget(self.grp_compare)
        layout.addLayout(file_layout)

        # Key Mapping Group
        self.grp_mapping = QGroupBox("Key Columns Mapping")
        mapping_layout = QVBoxLayout()
        self.key_map_table = QTableWidget(0, 2)
        self.key_map_table.setHorizontalHeaderLabels(["Source Key Column", "Compare Key Column"])
        self.key_map_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        btn_map_layout = QHBoxLayout()
        self.btn_add_key = QPushButton("Add Key Mapping")
        self.btn_rem_key = QPushButton("Remove Selected")
        self.btn_add_key.clicked.connect(self._add_key_mapping_row)
        self.btn_rem_key.clicked.connect(self._remove_key_mapping_row)
        btn_map_layout.addWidget(self.btn_add_key)
        btn_map_layout.addWidget(self.btn_rem_key)
        btn_map_layout.addStretch()
        mapping_layout.addWidget(self.key_map_table)
        mapping_layout.addLayout(btn_map_layout)
        self.grp_mapping.setLayout(mapping_layout)
        
        layout.addWidget(self.grp_mapping)

        # Logic Group
        self.grp_logic = QGroupBox("Comparison Logic")
        logic_layout = QHBoxLayout()
        self.logic_combo = QComboBox()
        self.logic_combo.addItems(["Concatenate", "AND", "OR"])
        self.separator_input = QLineEdit("|")
        
        self.logic_combo.currentTextChanged.connect(
            lambda text: self.separator_input.setEnabled(text == "Concatenate")
        )

        logic_layout.addWidget(QLabel("Method:"))
        logic_layout.addWidget(self.logic_combo)
        logic_layout.addWidget(QLabel("Separator:"))
        logic_layout.addWidget(self.separator_input)
        logic_layout.addStretch()
        self.grp_logic.setLayout(logic_layout)
        
        layout.addWidget(self.grp_logic)

    # ---------------------------------------------------------
    # TAB 2: RULES MAPPING
    # ---------------------------------------------------------
    def _build_rules_tab(self):
        layout = QVBoxLayout(self.tab_rules)
        
        # Table for rules
        self.rules_table = QTableWidget(0, 6)
        self.rules_table.setHorizontalHeaderLabels([
            "Condition", "Action", "Target 1", "Target 2 (Both)", "Source Col (Copy)", "Value"
        ])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.rules_table)

        # Add/Remove Rule buttons
        btn_layout = QHBoxLayout()
        self.btn_add_rule = QPushButton("Add Rule")
        self.btn_rem_rule = QPushButton("Remove Selected Rule")
        self.btn_add_rule.clicked.connect(self._add_rule_row)
        self.btn_rem_rule.clicked.connect(self._remove_rule_row)
        
        btn_layout.addWidget(self.btn_add_rule)
        btn_layout.addWidget(self.btn_rem_rule)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _add_rule_row(self):
        row = self.rules_table.rowCount()
        self.rules_table.insertRow(row)
        
        cb_condition = QComboBox()
        cb_condition.addItems(["Match (Source & Compare)", "Unmatch (Source only)", "Unmatch (Compare only)"])
        
        cb_action = QComboBox()

        cb_target1 = QComboBox()
        cb_target1.setEditable(True)

        cb_target2 = QComboBox()
        cb_target2.setEditable(True)

        cb_source = QComboBox()
        cb_source.setEditable(True)

        txt_value = QLineEdit()
        txt_value.setPlaceholderText("e.g. 'Found', 100, or =A1+B1")

        def update_row_logic():
            act = cb_action.currentText()

            cb_target1.setEnabled(False)
            cb_target2.setEnabled(False)
            cb_source.setEnabled(False)
            txt_value.setEnabled(False)
            
            cb_target1.clear()
            cb_target2.clear()
            cb_source.clear()

            if act == "Copy (Compare -> Source)":
                cb_target1.setEnabled(True)
                cb_target1.addItems(self.src_cols)
                cb_source.setEnabled(True)
                cb_source.addItems(self.cmp_cols)
            elif act == "Copy (Source -> Compare)":
                cb_target1.setEnabled(True)
                cb_target1.addItems(self.cmp_cols)
                cb_source.setEnabled(True)
                cb_source.addItems(self.src_cols)
            elif act == "Assign (Source)":
                cb_target1.setEnabled(True)
                cb_target1.addItems(self.src_cols)
                txt_value.setEnabled(True)
            elif act == "Assign (Compare)":
                cb_target1.setEnabled(True)
                cb_target1.addItems(self.cmp_cols)
                txt_value.setEnabled(True)
            elif act == "Assign Both":
                cb_target1.setEnabled(True)
                cb_target1.addItems(self.src_cols)
                cb_target2.setEnabled(True)
                cb_target2.addItems(self.cmp_cols)
                txt_value.setEnabled(True)

        def update_actions():
            cond = cb_condition.currentText()
            current_act = cb_action.currentText()
            
            cb_action.blockSignals(True)
            cb_action.clear()
            if cond == "Match (Source & Compare)":
                cb_action.addItems(["Copy (Compare -> Source)", "Copy (Source -> Compare)", "Assign (Source)", "Assign (Compare)", "Assign Both"])
            elif cond == "Unmatch (Source only)":
                cb_action.addItems(["Assign (Source)"])
            elif cond == "Unmatch (Compare only)":
                cb_action.addItems(["Assign (Compare)"])
            
            idx = cb_action.findText(current_act)
            cb_action.setCurrentIndex(idx if idx >= 0 else 0)
            cb_action.blockSignals(False)
            update_row_logic()

        cb_condition.currentTextChanged.connect(lambda: update_actions())
        cb_action.currentTextChanged.connect(lambda: update_row_logic())

        update_actions()

        self.rules_table.setCellWidget(row, 0, cb_condition)
        self.rules_table.setCellWidget(row, 1, cb_action)
        self.rules_table.setCellWidget(row, 2, cb_target1)
        self.rules_table.setCellWidget(row, 3, cb_target2)
        self.rules_table.setCellWidget(row, 4, cb_source)
        self.rules_table.setCellWidget(row, 5, txt_value)

    def _remove_rule_row(self):
        current_row = self.rules_table.currentRow()
        if current_row >= 0:
            self.rules_table.removeRow(current_row)

    def _add_key_mapping_row(self):
        row = self.key_map_table.rowCount()
        self.key_map_table.insertRow(row)
        cb_src = QComboBox()
        cb_src.addItems(self.src_cols)
        cb_cmp = QComboBox()
        cb_cmp.addItems(self.cmp_cols)
        self.key_map_table.setCellWidget(row, 0, cb_src)
        self.key_map_table.setCellWidget(row, 1, cb_cmp)

    def _remove_key_mapping_row(self):
        current_row = self.key_map_table.currentRow()
        if current_row >= 0:
            self.key_map_table.removeRow(current_row)

    # ---------------------------------------------------------
    # TAB 3: RESULTS
    # ---------------------------------------------------------
    def _build_results_tab(self):
        layout = QVBoxLayout(self.tab_results)
        
        filter_layout = QHBoxLayout()
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Source Results", "Compare Results"])
        self.view_combo.currentTextChanged.connect(self._update_result_view)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All"]) # Sẽ được điền tự động khi chạy xong
        self.filter_combo.currentTextChanged.connect(self._update_result_view)
        
        filter_layout.addWidget(QLabel("View File:"))
        filter_layout.addWidget(self.view_combo)
        filter_layout.addWidget(QLabel("Filter Status:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.result_table = QTableWidget()
        layout.addWidget(self.result_table)

    def _update_result_view(self):
        """
        EN: Update the result table based on selected view and filter.
        VI: Cập nhật bảng kết quả dựa trên file và bộ lọc được chọn.
        """
        if not hasattr(self, 'df_src_res') or not hasattr(self, 'df_cmp_res'):
            return
            
        view = self.view_combo.currentText()
        df = self.df_src_res if view == "Source Results" else self.df_cmp_res
        
        filter_text = self.filter_combo.currentText()
        if filter_text != "All":
            mask = pd.Series(False, index=df.index)
            for col in df.columns:
                mask |= df[col].astype(str).str.contains(filter_text, case=False, na=False)
            df_to_show = df[mask]
        else:
            df_to_show = df
            
        self._render_dataframe_to_table(df_to_show, self.result_table)

    def _render_dataframe_to_table(self, df: pd.DataFrame, table: QTableWidget):
        """
        EN: Render a pandas DataFrame into a QTableWidget (Limit 1000 rows).
        VI: Hiển thị pandas DataFrame lên QTableWidget (Giới hạn 1000 dòng).
        """
        table.clear()
        if df is None or df.empty:
            table.setRowCount(0)
            table.setColumnCount(0)
            return
            
        max_rows = min(1000, df.shape[0])
        table.setRowCount(max_rows)
        table.setColumnCount(df.shape[1])
        table.setHorizontalHeaderLabels([str(c) for c in df.columns])
        
        for row in range(max_rows):
            for col in range(df.shape[1]):
                val = df.iloc[row, col]
                item = QTableWidgetItem(str(val) if not pd.isna(val) else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, col, item)

    # ---------------------------------------------------------
    # LOGIC FUNCTIONS
    # ---------------------------------------------------------
    def _select_file(self, file_type: str):
        path, _ = QFileDialog.getOpenFileName(
            self, f"Select {file_type.title()} Excel File", "", "Excel Files (*.xlsx *.xls)"
        )
        if path:
            try:
                xl = pd.ExcelFile(path)
                if file_type == "source":
                    self.src_file_input.setText(path)
                    self.src_sheet_combo.clear()
                    self.src_sheet_combo.addItems(xl.sheet_names)
                    self.src_sheet_combo.currentTextChanged.connect(lambda: self._load_columns("source"))
                    self._load_columns("source")
                else:
                    self.cmp_file_input.setText(path)
                    self.cmp_sheet_combo.clear()
                    self.cmp_sheet_combo.addItems(xl.sheet_names)
                    self.cmp_sheet_combo.currentTextChanged.connect(lambda: self._load_columns("compare"))
                    self._load_columns("compare")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read file:\n{str(e)}")

    def _load_columns(self, file_type: str):
        try:
            if file_type == "source":
                path = self.src_file_input.text()
                sheet = self.src_sheet_combo.currentText()
                header_row = self.src_header_spin.value() - 1
                targets_list = self.src_targets_list
            else:
                path = self.cmp_file_input.text()
                sheet = self.cmp_sheet_combo.currentText()
                header_row = self.cmp_header_spin.value() - 1
                targets_list = self.cmp_targets_list

            if not path or not sheet:
                return

            # Read just 0 rows to get the header columns
            df = pd.read_excel(path, sheet_name=sheet, header=header_row, nrows=0)
            cols = [str(c) for c in df.columns]

            targets_list.clear()
            targets_list.addItems(cols)
            
            if file_type == "source": self.src_cols = cols
            else: self.cmp_cols = cols

            self.key_map_table.setRowCount(0)

        except Exception as e:
            # Handle silent errors or empty sheets gracefully
            pass

    def show_help(self):
        """
        EN: Show User Manual dialog.
        VI: Hiển thị hộp thoại Hướng dẫn sử dụng.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Hướng dẫn sử dụng")
        dialog.resize(800, 600)
        
        # Cho phép cửa sổ có nút phóng to (Maximize) và thu nhỏ (Minimize)
        dialog.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        layout = QVBoxLayout(dialog)
        
        browser = QTextBrowser()
        
        # Xác định đường dẫn file an toàn (hỗ trợ cả khi chạy script và file đã đóng gói .exe)
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            
        try:
            with open(os.path.join(base_dir, "HDSD.md"), "r", encoding="utf-8") as f:
                browser.setMarkdown(f.read())
        except Exception as e:
            browser.setText(f"Không thể tải file Hướng dẫn sử dụng.\nLỗi: {str(e)}")
            
        layout.addWidget(browser)
        dialog.exec()

    def run_comparison(self):
        """
        EN: Gather GUI data, validate, and pass to service.
        VI: Thu thập dữ liệu GUI, xác thực và chuyển cho service.
        """
        # 1. Validation (Kiểm tra xem đã chọn đủ file, sheet, khóa chưa)
        if not self.src_file_input.text() or not self.cmp_file_input.text():
            QMessageBox.warning(self, "Warning", "Please select both Source and Compare files.")
            return
            
        src_keys = []
        cmp_keys = []
        for row in range(self.key_map_table.rowCount()):
            w_src = self.key_map_table.cellWidget(row, 0)
            w_cmp = self.key_map_table.cellWidget(row, 1)
            if w_src and w_cmp:
                if w_src.currentText() and w_cmp.currentText():
                    src_keys.append(w_src.currentText())
                    cmp_keys.append(w_cmp.currentText())
        
        if not src_keys or not cmp_keys:
            QMessageBox.warning(self, "Warning", "Please add at least one Key Mapping row.")
            return

        # 2. Thu thập danh sách cột Target (Nếu người dùng không chọn, mặc định lấy tất cả)
        src_targets = [item.text() for item in self.src_targets_list.selectedItems()]
        if not src_targets:
            src_targets = [self.src_targets_list.item(i).text() for i in range(self.src_targets_list.count())]
            
        cmp_targets = [item.text() for item in self.cmp_targets_list.selectedItems()]
        if not cmp_targets:
            cmp_targets = [self.cmp_targets_list.item(i).text() for i in range(self.cmp_targets_list.count())]

        # 3. Phương thức so sánh (logic_str)
        logic_str = self.logic_combo.currentText().lower()
        if logic_str == "concatenate":
            logic_str = "concat"

        # 4. Duyệt bảng GUI Rules để xây dựng CompareRules object
        rules = CompareRules()
        for row in range(self.rules_table.rowCount()):
            cond = self.rules_table.cellWidget(row, 0).currentText()
            act = self.rules_table.cellWidget(row, 1).currentText()
            tgt1 = self.rules_table.cellWidget(row, 2).currentText()
            tgt2 = self.rules_table.cellWidget(row, 3).currentText()
            src_col = self.rules_table.cellWidget(row, 4).currentText()
            val = self.rules_table.cellWidget(row, 5).text()
            
            if cond == "Match (Source & Compare)":
                if act == "Copy (Compare -> Source)":
                    rules.on_match_source.append(ActionConfig("copy", tgt1, source_col=src_col))
                elif act == "Copy (Source -> Compare)":
                    rules.on_match_compare.append(ActionConfig("copy", tgt1, source_col=src_col))
                elif act == "Assign (Source)":
                    rules.on_match_source.append(ActionConfig("assign", tgt1, value=val))
                elif act == "Assign (Compare)":
                    rules.on_match_compare.append(ActionConfig("assign", tgt1, value=val))
                elif act == "Assign Both":
                    rules.on_match_source.append(ActionConfig("assign", tgt1, value=val))
                    rules.on_match_compare.append(ActionConfig("assign", tgt2, value=val))
                    
            elif cond == "Unmatch (Source only)":
                if act == "Assign (Source)":
                    rules.on_unmatch_source.append(ActionConfig("assign", tgt1, value=val))
                    
            elif cond == "Unmatch (Compare only)":
                if act == "Assign (Compare)":
                    rules.on_unmatch_compare.append(ActionConfig("assign", tgt1, value=val))

        # 5. Khởi tạo CompareConfig master object
        config = CompareConfig(
            source=SheetConfig(
                file_path=self.src_file_input.text(), sheet_name=self.src_sheet_combo.currentText(),
                header_row=self.src_header_spin.value(), key_cols=src_keys, target_cols=src_targets
            ),
            compare=SheetConfig(
                file_path=self.cmp_file_input.text(), sheet_name=self.cmp_sheet_combo.currentText(),
                header_row=self.cmp_header_spin.value(), key_cols=cmp_keys, target_cols=cmp_targets
            ),
            rules=rules, compare_logic=logic_str, separator=self.separator_input.text()
        )

        # 6. Khởi động luồng chạy nền (Worker Thread)
        self.btn_run.setEnabled(False)
        self.status_label.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = CompareWorker(
            config,
            self.src_file_input.text(), self.src_sheet_combo.currentText(), self.src_header_spin.value(),
            self.cmp_file_input.text(), self.cmp_sheet_combo.currentText(), self.cmp_header_spin.value()
        )
        
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished_success.connect(self._on_worker_success)
        self.worker.finished_error.connect(self._on_worker_error)
        self.worker.start()

    def _on_worker_progress(self, val: int, text: str):
        """
        EN: Update progress bar and status text.
        VI: Cập nhật thanh tiến trình và dòng trạng thái.
        """
        self.progress_bar.setValue(val)
        self.status_label.setText(text)

    def _on_worker_error(self, err_msg: str):
        """
        EN: Handle errors from the background worker.
        VI: Xử lý lỗi từ luồng chạy nền.
        """
        self.btn_run.setEnabled(True)
        self.status_label.setVisible(False)
        self.progress_bar.setVisible(False)
        
        if err_msg == "PERMISSION_ERROR":
            QMessageBox.critical(self, "Lỗi", "Vui lòng ĐÓNG file Excel trước khi chạy để phần mềm có thể ghi dữ liệu!")
        else:
            QMessageBox.critical(self, "Lỗi", f"Đối chiếu thất bại:\n{err_msg}")
            
    def _on_worker_success(self, df_src_res: pd.DataFrame, df_cmp_res: pd.DataFrame):
        """
        EN: Handle successful completion of the comparison.
        VI: Xử lý khi quá trình đối chiếu hoàn tất thành công.
        """
        self.btn_run.setEnabled(True)
        self.status_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.df_src_res = df_src_res
        self.df_cmp_res = df_cmp_res
        
        # Lấy danh sách Assign Value làm bộ lọc động cho kết quả
        assigned_vals = set(["All"])
        for row in range(self.rules_table.rowCount()):
            val = self.rules_table.cellWidget(row, 5).text().strip()
            if val: assigned_vals.add(val)
        
        self.filter_combo.blockSignals(True)
        self.filter_combo.clear()
        self.filter_combo.addItems(sorted(list(assigned_vals)))
        self.filter_combo.blockSignals(False)

        self._update_result_view()
        QMessageBox.information(self, "Thành công", "Đối chiếu hoàn tất!\nKết quả đã được điền trực tiếp vào file Excel gốc.")
        self.tabs.setCurrentIndex(2)

    def save_config(self):
        """
        EN: Save the current GUI configuration to a JSON file.
        VI: Lưu cấu hình giao diện hiện tại ra file JSON.
        """
        path, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", "JSON Files (*.json)")
        if not path:
            return

        try:
            state = {
                "source": {
                    "file": self.src_file_input.text(),
                    "sheet": self.src_sheet_combo.currentText(),
                    "header": self.src_header_spin.value(),
                    "targets": [item.text() for item in self.src_targets_list.selectedItems()]
                },
                "compare": {
                    "file": self.cmp_file_input.text(),
                    "sheet": self.cmp_sheet_combo.currentText(),
                    "header": self.cmp_header_spin.value(),
                    "targets": [item.text() for item in self.cmp_targets_list.selectedItems()]
                },
                "key_mapping": [],
                "logic": self.logic_combo.currentText(),
                "separator": self.separator_input.text(),
                "rules": []
            }
            
            # Save Key Mappings
            for row in range(self.key_map_table.rowCount()):
                w_src = self.key_map_table.cellWidget(row, 0)
                w_cmp = self.key_map_table.cellWidget(row, 1)
                if w_src and w_cmp:
                    state["key_mapping"].append({
                        "src": w_src.currentText(),
                        "cmp": w_cmp.currentText()
                    })
            
            # Save Rules Mapping
            for row in range(self.rules_table.rowCount()):
                state["rules"].append({
                    "cond": self.rules_table.cellWidget(row, 0).currentText(),
                    "act": self.rules_table.cellWidget(row, 1).currentText(),
                    "tgt1": self.rules_table.cellWidget(row, 2).currentText(),
                    "tgt2": self.rules_table.cellWidget(row, 3).currentText(),
                    "src_col": self.rules_table.cellWidget(row, 4).currentText(),
                    "val": self.rules_table.cellWidget(row, 5).text()
                })

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=4, ensure_ascii=False)
            
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{str(e)}")

    def load_config(self):
        """
        EN: Load configuration from a JSON file and populate GUI.
        VI: Tải cấu hình từ file JSON và điền vào giao diện.
        """
        path, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "JSON Files (*.json)")
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            def set_combo(combo: QComboBox, text: str):
                idx = combo.findText(text)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                else:
                    if not combo.isEditable():
                        combo.addItem(text)
                    combo.setCurrentText(text)

            def load_file_sheet(file_type: str, cfg: dict):
                if not os.path.exists(cfg.get("file", "")):
                    return  # File might have been moved
                    
                try:
                    xl = pd.ExcelFile(cfg["file"])
                    if file_type == "source":
                        self.src_file_input.setText(cfg["file"])
                        self.src_sheet_combo.blockSignals(True)
                        self.src_sheet_combo.clear()
                        self.src_sheet_combo.addItems(xl.sheet_names)
                        self.src_sheet_combo.blockSignals(False)
                        
                        set_combo(self.src_sheet_combo, cfg.get("sheet", ""))
                        
                        self.src_header_spin.blockSignals(True)
                        self.src_header_spin.setValue(cfg.get("header", 1))
                        self.src_header_spin.blockSignals(False)
                        
                        self._load_columns("source")
                        for i in range(self.src_targets_list.count()):
                            item = self.src_targets_list.item(i)
                            if item.text() in cfg.get("targets", []):
                                item.setSelected(True)
                    else:
                        self.cmp_file_input.setText(cfg["file"])
                        self.cmp_sheet_combo.blockSignals(True)
                        self.cmp_sheet_combo.clear()
                        self.cmp_sheet_combo.addItems(xl.sheet_names)
                        self.cmp_sheet_combo.blockSignals(False)
                        
                        set_combo(self.cmp_sheet_combo, cfg.get("sheet", ""))
                        
                        self.cmp_header_spin.blockSignals(True)
                        self.cmp_header_spin.setValue(cfg.get("header", 1))
                        self.cmp_header_spin.blockSignals(False)
                        
                        self._load_columns("compare")
                        for i in range(self.cmp_targets_list.count()):
                            item = self.cmp_targets_list.item(i)
                            if item.text() in cfg.get("targets", []):
                                item.setSelected(True)
                except Exception:
                    pass

            if "source" in state: load_file_sheet("source", state["source"])
            if "compare" in state: load_file_sheet("compare", state["compare"])

            set_combo(self.logic_combo, state.get("logic", "Concatenate"))
            self.separator_input.setText(state.get("separator", "|"))

            # Load Key Mappings
            self.key_map_table.setRowCount(0)
            for km in state.get("key_mapping", []):
                self._add_key_mapping_row()
                row = self.key_map_table.rowCount() - 1
                set_combo(self.key_map_table.cellWidget(row, 0), km.get("src", ""))
                set_combo(self.key_map_table.cellWidget(row, 1), km.get("cmp", ""))

            # Load Rules
            self.rules_table.setRowCount(0)
            for rule in state.get("rules", []):
                self._add_rule_row()
                row = self.rules_table.rowCount() - 1
                
                # Setting Condition triggers Actions load
                set_combo(self.rules_table.cellWidget(row, 0), rule.get("cond", ""))
                # Setting Action triggers Target/Source load
                set_combo(self.rules_table.cellWidget(row, 1), rule.get("act", ""))
                
                set_combo(self.rules_table.cellWidget(row, 2), rule.get("tgt1", ""))
                set_combo(self.rules_table.cellWidget(row, 3), rule.get("tgt2", ""))
                set_combo(self.rules_table.cellWidget(row, 4), rule.get("src_col", ""))
                self.rules_table.cellWidget(row, 5).setText(rule.get("val", ""))

            QMessageBox.information(self, "Success", "Configuration loaded successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration:\n{str(e)}")
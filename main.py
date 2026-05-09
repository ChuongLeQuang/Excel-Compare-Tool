import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from src.models.main_window import MainWindow


def setup_logging():
    """
    EN: Set up logging configuration to write to logs/ directory.
    VI: Thiết lập cấu hình ghi log vào thư mục logs/ tự động.
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "app.log"), encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """
    EN: Entry point of the Excel Compare application.
    VI: Điểm khởi chạy của ứng dụng đối chiếu Excel.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Application Excel Compare Tool started.")
    
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
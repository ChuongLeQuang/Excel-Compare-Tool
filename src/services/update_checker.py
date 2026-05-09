import logging
import requests
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)


class UpdateCheckerWorker(QThread):
    """
    EN: Background thread to check for latest releases on GitHub.
    VI: Luồng chạy nền để kiểm tra các bản phát hành mới nhất trên GitHub.
    """
    update_available = pyqtSignal(str, str)  # version, download_url

    def __init__(self, current_version: str, repo_url: str):
        super().__init__()
        self.current_version = current_version
        # Chuyển URL kho lưu trữ thành URL API của GitHub
        # Ví dụ: https://github.com/user/repo -> https://api.github.com/repos/user/repo/releases/latest
        self.api_url = repo_url.replace("github.com", "api.github.com/repos") + "/releases/latest"

    def _parse_version(self, v_str: str) -> tuple:
        """
        EN: Convert version string 'v1.0.1' to tuple (1, 0, 1) for comparison.
        VI: Chuyển chuỗi phiên bản 'v1.0.1' thành tuple (1, 0, 1) để so sánh.
        """
        clean_str = v_str.lower().replace("v", "").strip()
        try:
            return tuple(map(int, clean_str.split(".")))
        except ValueError:
            return (0, 0, 0)

    def run(self):
        try:
            # Cài đặt timeout 5 giây để nếu mất mạng thì tự hủy, không treo app
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "")
                release_url = data.get("html_url", "")

                # So sánh phiên bản
                if latest_version and self._parse_version(latest_version) > self._parse_version(self.current_version):
                    logger.info(f"New version found: {latest_version}")
                    self.update_available.emit(latest_version, release_url)
                    
        except Exception as e:
            logger.error(f"Failed to check for updates: {str(e)}")
import os
import subprocess
import sys

def build_app():
    """
    EN: Build the executable using PyInstaller.
    VI: Đóng gói ứng dụng thành file chạy bằng PyInstaller.
    """
    print("🚀 Bắt đầu tiến trình đóng gói ứng dụng...")
    
    # Tạo thư mục assets nếu chưa có
    os.makedirs("assets", exist_ok=True)
    png_path = os.path.join("assets", "icon.png")
    ico_path = os.path.join("assets", "icon.ico")
    
    # Tự động chuyển đổi png sang ico nếu cần
    if os.path.exists(png_path) and not os.path.exists(ico_path):
        print("⏳ Đang tự động chuyển đổi icon.png sang icon.ico...")
        try:
            from PIL import Image
            img = Image.open(png_path)
            img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
            print("✅ Chuyển đổi icon thành công!")
        except ImportError:
            print("❌ Lỗi: Thư viện 'Pillow' chưa được cài đặt.")
            print("👉 Vui lòng chạy lệnh: pip install Pillow")
            sys.exit(1)

    final_icon = ico_path if os.path.exists(ico_path) else png_path
    if not os.path.exists(final_icon):
        print(f"\n⚠️ CẢNH BÁO: Không tìm thấy file icon tại '{final_icon}'")
        print("👉 Vui lòng chuẩn bị một file ảnh .png, đổi tên thành 'icon.png' và thả vào thư mục 'assets/'.")
        print("Tạm thời sẽ đóng gói không có icon tùy chỉnh...\n")
    
    # Cú pháp ngăn cách (separator) phân biệt theo hệ điều hành
    sep = ";" if sys.platform.startswith("win") else ":"
    
    cmd = [
        "pyinstaller",
        "--noconfirm",            # Tự động ghi đè thư mục build cũ
        "--windowed",             # Ẩn cửa sổ console (CMD) đen thui phía sau
        "--name=ExcelCompareTool",# Tên file ứng dụng
        f"--add-data=HDSD.md{sep}.", # Nhúng file Hướng dẫn sử dụng
    ]
    
    if os.path.exists(final_icon):
        cmd.append(f"--icon={final_icon}")
        cmd.append(f"--add-data={final_icon}{sep}assets")
        
    cmd.append("main.py")
    
    subprocess.run(cmd, check=True)
    print("\n✅ Đóng gói hoàn tất! App của bạn đã nằm trong thư mục 'dist/ExcelCompareTool/'.")

if __name__ == "__main__":
    build_app()
# AI_RULES.md (Python Full Version)

## 1. Code Style & Convention
- **Language / Ngôn ngữ**: Python 3.x
- **Naming rules / Quy tắc đặt tên**:
  - Variables & functions / Biến & hàm → `snake_case`
  - Classes / Lớp → `PascalCase`
  - Constants / Hằng số → `UPPER_CASE`
- **Imports / Thư viện**:
  - Standard libraries trước, third-party sau, local cuối cùng.
  - Dùng absolute import thay vì relative nếu có thể.
- **Type hints / Kiểu dữ liệu**:
  - Luôn khai báo type hints cho input/output.
  - Ví dụ:

```python
def calculate_area(radius: float) -> float:
    """
    EN: Calculate the area of a circle given its radius.
    VI: Tính diện tích hình tròn dựa trên bán kính.
    """
    return 3.14159 * radius * radius
```

- **Comments / Ghi chú**:
  - Dùng docstring cho module, class, function.
  - Bắt buộc viết comment/docstring song ngữ (EN + VI) ngắn gọn, rõ ràng.
  - Inline comment chỉ khi cần giải thích logic phức tạp.
- **Formatting / Định dạng**:
  - Theo chuẩn PEP8.
  - Dùng Black để auto-format (indent = 4 spaces).
  - Max line length = 88 ký tự.
  - **JSON Format**: Indent = 4 spaces, bắt buộc lưu encoding `UTF-8` (không escape ký tự Unicode). Naming convention cho JSON keys phải đồng nhất (ưu tiên `snake_case`).
- **Error handling / Xử lý lỗi**:
  - Luôn dùng `try/except` rõ ràng, không bắt lỗi chung chung (`except Exception`).
  - Comment giải thích lý do bắt lỗi.

---

## 2. Project Structure
- Thư mục `src/` chứa toàn bộ logic chính.
- Thư mục `logs/` chứa các file nhật ký của ứng dụng (application logs, error logs).
- Thư mục `output/` chứa kết quả xuất ra của chương trình (ví dụ: file CSV, Excel báo cáo).
- Thư mục `data/` (hoặc `database/`) chứa các file CSDL cục bộ, file cấu hình gốc (ví dụ: `master_configs.json`, SQLite).
- **Frontend / Web Assets (Nếu dự án có giao diện Web)**:
  - Thư mục `static/` hoặc `public/` chứa tài nguyên tĩnh (images, css, js).
  - Thư mục `templates/` chứa các file giao diện HTML (nếu dùng Server-Side Rendering).
  - Nếu dùng framework Frontend độc lập (React/Vue/Angular), tách toàn bộ vào thư mục `frontend/` ở root.
- **Multi-module/Monorepo (Dự án lớn gồm nhiều chức năng/dự án nhỏ)**:
  - Tổ chức các chức năng/dự án nhỏ vào thư mục `apps/` hoặc `modules/` (ví dụ: `apps/module_a/`, `apps/module_b/`).
  - Mỗi dự án nhỏ bên trong phải tuân thủ chính xác cấu trúc thư mục độc lập (tự chứa `src/`, `tests/`,...).
  - Các utils, thư viện cốt lõi dùng chung cho nhiều dự án nhỏ nên đặt trong một thư mục `shared/` hoặc `core/` ở root.
- Không để file vượt quá **500 dòng**.
- Bên trong `src/`:
  - `models/` → định nghĩa dữ liệu, class, schema.
  - `services/` → xử lý nghiệp vụ, API call.
  - `utils/` → hàm tiện ích.
  - `controllers/` hoặc `views/` → xử lý request/response (nếu là web app).
  - `config/` → chứa các file thiết lập cấu hình ứng dụng.
- File Python đặt tên theo `snake_case.py`.
- Thư mục `tests/` chứa unit test, file test đặt tên `test_<module>.py` tương ứng với file trong `src/`.

---

## 3. Flow & Architecture / Luồng & Kiến trúc
- **Development Workflow / Quy trình phát triển**:
  - **Bắt buộc thiết kế GUI (Giao diện người dùng) trước** khi bắt đầu code logic.
  - Khi phân tích dự án, AI/Dev phải phân tích dựa trên trải nghiệm/luồng UI (Mockup/Wireframe) để hiểu rõ mục tiêu, từ đó mới thiết kế Model, Service và Database tương ứng.
- **Layer separation / Phân tầng**:
  - Controller → Service → Model → Database.
  - Không gọi API trực tiếp trong UI hoặc controller, phải qua service.
- **Data flow / Luồng dữ liệu**:
  - Input → Validation → Business logic → Output.
  - Luôn validate dữ liệu trước khi xử lý.
- **Dependency management / Quản lý phụ thuộc**:
  - Dùng `requirements.txt` hoặc `pyproject.toml`.
  - Không hardcode version, dùng range hợp lý.

---

## 4. Security & Performance
- **Security / Bảo mật**:
  - Không hardcode secret, dùng `.env` hoặc secret manager.
  - Luôn sanitize input để tránh SQL injection, XSS.
  - Không dùng `eval()` hoặc `exec()` trừ khi thật cần thiết.
- **Performance / Hiệu năng**:
  - Ưu tiên async/await cho I/O.
  - Tránh vòng lặp lồng nhau quá sâu.
  - Dùng caching khi cần.
- **Logging / Nhật ký**:
  - Dùng `logging` module thay vì `print`.
  - Log phải có level (INFO, WARNING, ERROR).

---

## 5. Testing & CI/CD
- **Testing / Kiểm thử**:
  - Dùng pytest.
  - **Bắt buộc**: Bất kỳ module hoặc function nào mới được tạo ra đều phải đi kèm với unit test tương ứng (Khuyến khích áp dụng TDD - Viết test trước, code sau).
  - Không chấp nhận code logic (Service, Utils, Model) mà không có test.
  - Coverage tổng thể và cho từng file tối thiểu ≥ 80%.
- **CI/CD / Tích hợp liên tục**:
  - Pipeline chạy lint + test trước khi merge.
  - Reject commit nếu vi phạm rule.
- **Example test / Ví dụ kiểm thử**:

```python
def test_calculate_area():
    """
    EN: Test circle area calculation with radius = 2.
    VI: Kiểm thử tính diện tích hình tròn với bán kính = 2.
    """
    assert calculate_area(2) == 12.56636
```

---

## 6. Documentation
- Mỗi module phải có README ngắn mô tả chức năng.
- Cập nhật tài liệu kiến trúc (nếu có) khi thêm module/flow mới.
- Tài liệu API (Swagger/Postman hoặc file Markdown) phải luôn được cập nhật đồng bộ với code.

---

## 7. Git & Version Control
- **Commit Message Convention / Chuẩn commit**:
  - Tuân thủ nghiêm ngặt [Conventional Commits](https://www.conventionalcommits.org/).
  - Cấu trúc: `<type>(<scope>): <subject>`
  - Các `type` bắt buộc: `feat` (tính năng mới), `fix` (sửa lỗi), `docs` (tài liệu), `style` (format, không đổi logic), `refactor` (tối ưu code), `test` (kiểm thử), `chore` (cấu hình, tool, build).
  - Tiêu đề (subject) ngắn gọn, **không quá 72 ký tự**, viết rõ ràng (có thể dùng EN/VI nhưng phải thống nhất).
- **Branch Naming / Đặt tên nhánh**:
  - `feature/<tên-chức-năng>` (ví dụ: `feature/export-excel`)
  - `bugfix/<tên-lỗi>` (ví dụ: `bugfix/fix-null-pointer`)
  - `hotfix/<tên-lỗi-nghiêm-trọng>` cho các bản vá khẩn cấp cần đưa lên production ngay.
- **Pull Request / Merge Request**:
  - PR phải có mô tả rõ ràng (What, Why, How).
  - Khuyến khích squash các commit "rác" (như "fix typo", "update again") thành 1 commit có ý nghĩa trước khi merge.

---

## 8. Build & Packaging / Đóng gói ứng dụng
- **Module Recognition / Nhận diện Module**:
  - Bắt buộc: Mọi thư mục chứa mã nguồn Python (như `src/`, `views/`, `services/`...) đều phải chứa file `__init__.py` (kể cả file trống). Điều này giúp Python và các công cụ đóng gói (PyInstaller) nhận diện chính xác đó là một Package hợp lệ.
- **Path Resolution / Cấu hình Đường dẫn**:
  - Không lạm dụng hoặc phụ thuộc hoàn toàn vào biến `__file__` để lấy đường dẫn gốc. Khi ứng dụng được đóng gói thành file thực thi (ví dụ: `.exe`), `__file__` sẽ không còn trỏ đúng cấu trúc thư mục vật lý.
  - Luôn sử dụng cơ chế kiểm tra môi trường linh hoạt (VD: kiểm tra `getattr(sys, 'frozen', False)` để dùng `sys._MEIPASS` cho PyInstaller).
  - **Xử lý tệp tĩnh (Static Assets)**: Đối với các tệp tĩnh (ảnh, icon, configs), tuyệt đối KHÔNG gọi trực tiếp bằng đường dẫn tương đối (VD: `open("assets/icon.png")`). Luôn dùng `os.path.join(project_root, "assets", "icon.png")` với `project_root` đã được phân giải an toàn qua cơ chế `sys._MEIPASS`.
- **System Path Manipulation / Can thiệp sys.path**:
  - Hạn chế tối đa việc sử dụng `sys.path.insert(0, ...)` để hack đường dẫn import.
  - Tuyệt đối KHÔNG thực thi lệnh `sys.path.insert` can thiệp vào đường dẫn vật lý nếu ứng dụng đang chạy ở chế độ đã đóng gói (frozen mode), vì nó sẽ phá vỡ cơ chế tìm kiếm module nội bộ của công cụ build. Chỉ áp dụng cho môi trường Development.

---

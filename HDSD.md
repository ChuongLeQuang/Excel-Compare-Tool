# 📖 HƯỚNG DẪN SỬ DỤNG: CÔNG CỤ ĐỐI CHIẾU EXCEL (EXCEL COMPARE TOOL)

Phần mềm này giúp bạn đối chiếu dữ liệu giữa 2 file Excel (gọi là **Source** - File Nguồn và **Compare** - File Đối chiếu). Sau khi tìm ra các dòng khớp hoặc lệch nhau dựa trên Khóa (Mã ID, Tên,...), phần mềm sẽ tự động lấy dữ liệu từ file này đắp sang file kia, hoặc gán các nhãn trạng thái (ví dụ: "Khớp", "Không tìm thấy") **trực tiếp vào file gốc của bạn**.

⚠️ **LƯU Ý QUAN TRỌNG TRƯỚC KHI CHẠY**:
> Hãy chắc chắn rằng bạn **ĐÃ ĐÓNG** cả 2 file Excel trên máy tính. Nếu bạn đang mở file, phần mềm sẽ không thể ghi kết quả vào được và sẽ báo lỗi.

---

## BƯỚC 1: CẤU HÌNH CƠ BẢN (TAB 1. CONFIGURATION)

Tại Tab này, bạn sẽ thiết lập các file cần đối chiếu và cách thức để phần mềm nhận diện "hai dòng giống nhau".

1. **Chọn File và Sheet**:
   - Nhấn **Browse Source...** để chọn File gốc.
   - Nhấn **Browse Compare...** để chọn File đối chiếu.
   - Chọn Sheet cần xử lý ở mục **Select Sheet**.
   - Cài đặt **Header Row**: Nhập số dòng chứa tiêu đề cột (Ví dụ: Tiêu đề nằm ở dòng 3 thì nhập số 3).
   - **Target Columns**: (Tùy chọn) Danh sách các cột bạn muốn hiển thị xem trước ở Tab Kết quả. Có thể bỏ qua (mặc định chọn tất cả).

2. **Cấu hình Khóa đối chiếu (Key Columns Mapping)**:
   - Đây là tiêu chí để biết 1 dòng bên Source có tồn tại bên Compare hay không.
   - Nhấn **Add Key Mapping**.
   - Cột trái: Chọn cột ID bên Source (VD: `Mã Học Viên`).
   - Cột phải: Chọn cột ID tương ứng bên Compare (VD: `Mã SV`).
   - *Mẹo: Bạn có thể Add nhiều dòng nếu cần khớp đồng thời nhiều điều kiện (VD: Khớp cả Mã SV và Họ Tên).*

3. **Phương thức so sánh (Comparison Logic)**:
   - **Concatenate**: Nối các cột khóa lại với nhau (Ví dụ: `Mã SV|Họ Tên`). Ô *Separator* dùng để chọn ký tự nối (mặc định là `|`).
   - **AND**: Tất cả các khóa phải giống nhau hoàn toàn.
   - **OR**: Chỉ cần 1 trong các khóa giống nhau là tính khớp.

---

## BƯỚC 2: THIẾT LẬP QUY TẮC GÁN DỮ LIỆU (TAB 2. RULES MAPPING)

Đây là **trái tim của phần mềm**. Nơi bạn ra lệnh cho phần mềm phải làm gì khi tìm thấy (hoặc không tìm thấy) dữ liệu. Nhấn **Add Rule** để thêm một quy tắc mới.

Mỗi dòng Quy tắc gồm 6 ô. Bạn cần quan tâm nhất đến ô số 1 (**Condition**) và ô số 2 (**Action**):

### Trường hợp 1: MATCH (Dòng có tồn tại ở CẢ 2 FILE)
Chọn `Condition` là: **Match (Source & Compare)**. Lúc này ở mục `Action` bạn sẽ có các lựa chọn:

* **Copy (Compare -> Source)**: Dùng khi muốn lấy một cột từ file Compare mang về đắp cho file Source.
  * *Target 1*: Chọn cột đích bên Source sẽ nhận dữ liệu (VD: `Học Phí Đã Thu`).
  * *Source Col*: Chọn cột chứa dữ liệu bên Compare (VD: `Tiền Đóng`).
* **Copy (Source -> Compare)**: Ngược lại, lấy dữ liệu từ file Source đắp sang file Compare.
* **Assign (Source)**: Gán một chữ tĩnh (hoặc công thức) vào file Source.
  * *Target 1*: Chọn cột bên Source (VD: `Trạng thái`).
  * *Value*: Gõ chữ bạn muốn gán (VD: `Khớp dữ liệu`).
* **Assign (Compare)**: Tương tự như trên nhưng gán chữ vào file Compare.
* **Assign Both**: Gán một chữ tĩnh vào CẢ 2 FILE cùng một lúc.
  * *Target 1*: Chọn cột của file Source.
  * *Target 2*: Chọn cột của file Compare.
  * *Value*: Nhập nội dung (VD: `Đã kiểm tra`).

### Trường hợp 2: UNMATCH SOURCE ONLY (Có ở Source nhưng không có ở Compare)
Ví dụ: Học sinh có trong danh sách lớp nhưng không có trong danh sách đóng tiền.
* Chọn `Condition`: **Unmatch (Source only)**.
* Khi đó, phần mềm tự động khóa tính năng Copy (vì lấy đâu ra file kia mà Copy). Bạn chỉ có 1 `Action` duy nhất:
  * **Assign (Source)**:
    * *Target 1*: Chọn cột muốn gán chữ (VD: `Ghi chú`).
    * *Value*: Nhập nội dung (VD: `Thiếu trong hệ thống Kế toán`).

### Trường hợp 3: UNMATCH COMPARE ONLY (Dư thừa ở Compare)
Ví dụ: Danh sách Kế toán có tên nhưng danh sách lớp thì không có.
* Chọn `Condition`: **Unmatch (Compare only)**.
* Bạn cũng chỉ có 1 `Action` duy nhất:
  * **Assign (Compare)**:
    * *Target 1*: Chọn cột muốn gán (VD: `Lỗi báo cáo`).
    * *Value*: Nhập nội dung (VD: `Học viên ảo / Dư`).

💡 **Bí kíp tạo Rule hiệu quả**: 
Bạn hoàn toàn có thể tạo ra 5, 10 rules cùng lúc để làm nhiều việc trên cùng 1 file. Nếu cột *Target* bạn chọn chưa hề tồn tại trong file Excel, phần mềm sẽ **tự động tạo ra cột mới** cho bạn!

---

*Chúc bạn tiết kiệm được nhiều giờ làm việc mỗi ngày với Công cụ Đối chiếu dữ liệu này!*
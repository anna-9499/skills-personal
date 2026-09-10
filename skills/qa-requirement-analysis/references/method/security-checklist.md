# Security — chọn theo loại feature

Chỉ lấy phần khớp. Mỗi mục đưa vào báo cáo phải viết lại thành kịch bản cụ thể trên
feature đang xét, kèm lý do áp dụng.

## Áp dụng cho hầu như mọi feature có backend

- **Phân quyền theo chiều ngang (IDOR):** đổi ID trong URL/payload sang bản ghi của user
  khác — có bị chặn không? Đây là lỗ hổng phổ biến nhất và hay bị bỏ sót nhất.
- **Phân quyền theo chiều dọc:** user thường gọi thẳng API dành cho admin.
- **Kiểm tra quyền phía server:** ẩn nút trên UI không phải là kiểm soát. Gọi API trực tiếp.
- **Xác thực:** truy cập khi chưa đăng nhập, token hết hạn, token của user đã bị vô hiệu hoá.
- **Rò rỉ dữ liệu trong response:** API trả về thừa field (password hash, email người khác,
  ghi chú nội bộ) mà UI không hiển thị.
- **Thông báo lỗi:** stack trace, tên bảng, câu truy vấn lộ ra ngoài.

## Form nhập liệu / tạo - sửa bản ghi

- Injection: SQL, NoSQL, command, LDAP — tuỳ tầng lưu trữ.
- XSS lưu trữ: nhập `<script>` hoặc payload HTML vào field text, xem lại ở màn hình khác
  và ở email/export.
- Mass assignment: gửi thêm field không có trên form (`role`, `isVerified`, `price`).
- Validation phía server có tương đương phía client không — bỏ qua UI, gọi thẳng API.
- CSRF nếu dùng cookie session.

## Upload file

- Kiểm tra loại file theo nội dung (magic bytes) hay chỉ theo phần mở rộng?
- File thực thi đổi đuôi; ảnh có nhúng payload; SVG chứa script.
- Path traversal trong tên file (`../../`).
- Giới hạn dung lượng; zip bomb nếu có giải nén.
- File tải lên có bị phục vụ từ cùng domain và chạy được không?
- Ai được tải file về — URL file có đoán được không?

## Danh sách / tìm kiếm / lọc / export

- Tham số sắp xếp, lọc có bị dùng để inject vào truy vấn không?
- Bộ lọc có bị bỏ qua điều kiện phân quyền khiến lộ dữ liệu tenant khác không?
- Export có kèm cả field nhạy cảm không?
- CSV injection: giá trị bắt đầu bằng `=`, `+`, `@` khi mở bằng Excel.

## Đăng nhập / đăng ký / đổi mật khẩu / OTP

- Brute force và rate limit; khoá tài khoản.
- User enumeration: thông báo khác nhau giữa "sai mật khẩu" và "email không tồn tại";
  chênh lệch thời gian phản hồi.
- Token reset: độ dài, thời gian sống, dùng một lần, có bị gửi qua kênh không an toàn.
- OTP: số lần thử, thời gian sống, có thể yêu cầu gửi lại vô hạn không.
- Phiên cũ có bị vô hiệu hoá sau khi đổi mật khẩu không.

## Thanh toán / tính tiền / điểm thưởng

- Giá và số tiền tính ở server hay nhận từ client?
- Thao tác lặp: nhấn thanh toán hai lần, replay request — có idempotency key không?
- Race condition: dùng cùng một voucher / trừ cùng một số dư ở hai request song song.
- Số âm, số rất lớn, làm tròn, sai lệch tiền tệ.
- Nhật ký audit đầy đủ cho mọi thay đổi tiền.

## Tích hợp bên thứ ba / webhook / API công khai

- Webhook đến có xác thực chữ ký không? Có chống replay không?
- Secret / API key nằm ở đâu, có lọt vào log hoặc vào bundle frontend không?
- SSRF nếu hệ thống gọi URL do user cung cấp.
- Rate limit cho API công khai.

## Dữ liệu cá nhân / quyền riêng tư

- Field nào là PII; có bị ghi vào log không?
- Có cần che (mask) khi hiển thị không?
- Có yêu cầu xoá theo quy định không, xoá thì xoá tới đâu?
- Ai xem được dữ liệu này trong nội bộ, có ghi vết truy cập không?

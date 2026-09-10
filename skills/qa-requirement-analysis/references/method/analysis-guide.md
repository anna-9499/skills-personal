# Bộ câu hỏi đào sâu

Dùng khi đọc requirement. Không trả lời hết trong báo cáo — dùng để **phát hiện chỗ
requirement im lặng**. Mỗi câu hỏi không có đáp án trong tài liệu là ứng viên cho một GAP.

## A. Trích business rule

- Rule được phát biểu ở đâu: description, AC, comment, mockup, hay chỉ ngầm hiểu?
- Rule có điều kiện áp dụng không (chỉ với loại user nào, chỉ trong khung giờ nào,
  chỉ khi bản ghi ở trạng thái nào)?
- Khi vi phạm rule thì hệ thống làm gì: chặn, cảnh báo, hay ghi log rồi vẫn cho qua?
- Rule có mâu thuẫn với rule nào đã tồn tại trong sản phẩm không?
- Có con số nào bị viết mà không nói đơn vị, múi giờ, hoặc cách làm tròn không?

## B. Săn gap — theo trục

**Đầu vào**
- Field nào bắt buộc, field nào tuỳ chọn?
- Kiểu dữ liệu, độ dài tối đa/tối thiểu, ký tự cho phép, định dạng?
- Giá trị mặc định khi không nhập?
- Chuỗi rỗng, khoảng trắng, số 0, số âm, `null` — xử lý ra sao?
- Unicode, emoji, tiếng Việt có dấu, ký tự RTL?

**Trạng thái & vòng đời**
- Bản ghi có những trạng thái nào, chuyển từ đâu sang đâu là hợp lệ?
- Hành động này thực hiện được ở những trạng thái nào?
- Làm lại lần hai thì sao (idempotency)?
- Xoá là xoá mềm hay xoá cứng? Xoá rồi có phục hồi được không?

**Người dùng & quyền**
- Vai trò nào thấy được, vai trò nào thao tác được?
- User chưa đăng nhập truy cập thì sao?
- Chủ sở hữu bản ghi và người khác có khác quyền không?
- Quyền thay đổi giữa chừng phiên làm việc thì xử lý thế nào?

**Thời gian & đồng thời**
- Múi giờ nào là chuẩn: server, client, hay cấu hình theo tenant?
- Hai người sửa cùng bản ghi cùng lúc thì ai thắng?
- Có hạn chót / hết hạn / lịch chạy định kỳ không?

**Lỗi & phục hồi**
- Hệ thống ngoài lỗi hoặc timeout thì hiển thị gì, có retry không?
- Thao tác nhiều bước bị đứt giữa chừng thì rollback tới đâu?
- Thông báo lỗi nội dung chính xác là gì, ai viết?

**Hiển thị**
- Trạng thái rỗng, đang tải, quá nhiều dữ liệu hiển thị thế nào?
- Phân trang hay cuộn vô hạn? Mặc định bao nhiêu bản ghi?
- Sắp xếp mặc định theo gì?
- Có cần đa ngôn ngữ / định dạng số, tiền tệ theo locale không?

## C. Xác định khu vực ảnh hưởng

- Feature đọc/ghi vào bảng dữ liệu nào? Bảng đó còn ai dùng?
- Có sửa API đang có không — có phải breaking change với client cũ (mobile app chưa
  cập nhật) không?
- Có dùng chung component UI với màn hình khác không?
- Có thay đổi schema cần migration? Dữ liệu cũ có thoả ràng buộc mới không?
- Có bật sau feature flag không? Tắt cờ thì hành vi cũ có nguyên vẹn không?
- Có ảnh hưởng tới báo cáo, export, thống kê, hoặc job chạy nền không?

## D. Nhận diện rủi ro QA

Đây là rủi ro cho **hoạt động kiểm thử**, không phải rủi ro dự án:

- Có cần dữ liệu test khó tạo không (tài khoản đã KYC, đơn hàng ở trạng thái hiếm)?
- Có phụ thuộc hệ thống ngoài mà môi trường test không có / hay sập không?
- Có kịch bản chỉ xảy ra theo thời gian thật (hết hạn sau 30 ngày) — có cách tua thời gian không?
- Có luồng bất đồng bộ khó quan sát kết quả không (queue, webhook, job đêm)?
- Có yêu cầu thiết bị / trình duyệt / phiên bản OS cụ thể không?
- Kết quả có mang tính không tất định (thứ tự, thời điểm, dữ liệu bên ngoài) không?
- Requirement thay đổi gần đây nhiều lần → nguy cơ test case viết ra phải sửa lại.

## E. Kỷ luật khi viết báo cáo

- Đừng gộp nhiều vấn đề vào một GAP. Mỗi GAP là một câu hỏi có thể trả lời độc lập.
- Đừng liệt kê rule hiển nhiên ("user phải đăng nhập") trừ khi requirement thật sự nói,
  hoặc chính chỗ đó đang mơ hồ.
- Nếu ticket rất sơ sài, đừng cố kéo dài báo cáo. Nói thẳng nó thiếu nền tảng, chấm
  Not Ready, và tập trung vào danh sách câu hỏi.
- Nếu ticket rất đầy đủ, đừng bịa gap để tỏ ra hữu ích. Ready là một kết luận hợp lệ.

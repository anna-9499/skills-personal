# Performance — chọn theo loại feature

Chỉ nêu điều có kịch bản tải cụ thể cho feature này. Nếu requirement không nêu ngưỡng,
đề xuất ngưỡng khởi điểm và **đánh dấu rõ là đề xuất cần PO chốt** + tạo GAP tương ứng.

## Câu hỏi định lượng phải hỏi trước

Không có mấy con số này thì không kiểm thử hiệu năng có ý nghĩa được:

- Bao nhiêu user đồng thời ở giờ cao điểm?
- Khối lượng dữ liệu thực tế: bao nhiêu bản ghi hiện có, tăng bao nhiêu mỗi tháng?
- Ngưỡng thời gian phản hồi chấp nhận được là bao nhiêu, đo ở p95 hay trung bình?
- Có mốc thời gian đột biến không (đầu tháng, cuối kỳ, campaign, ngày trả lương)?

## Danh sách / bảng dữ liệu / tìm kiếm

- Hành vi với 10 / 1.000 / 100.000 bản ghi.
- Có phân trang không, phân trang theo offset hay cursor (offset sâu rất chậm).
- Cột dùng để lọc và sắp xếp đã có index chưa.
- Tìm kiếm theo `LIKE %text%` — không dùng được index.
- N+1 query khi render danh sách kèm dữ liệu liên quan.
- Kích thước response, có trả thừa field không.

## Export / báo cáo / thống kê

- Export chạy đồng bộ hay đưa vào hàng đợi? Đồng bộ với dữ liệu lớn sẽ timeout.
- Bộ nhớ khi dựng file lớn — có stream không hay gom hết vào RAM.
- Truy vấn tổng hợp trên khoảng thời gian dài có khoá bảng, ảnh hưởng người dùng khác không.
- Nhiều người export cùng lúc.

## Upload / xử lý file / ảnh

- Kích thước tối đa, thời gian tải lên trên mạng chậm.
- Xử lý (resize, quét virus, chuyển mã) đồng bộ hay bất đồng bộ.
- Nhiều file cùng lúc; hàng đợi có bị dồn ứ không.

## Ghi dữ liệu / giao dịch

- Thông lượng ghi ở giờ cao điểm.
- Giao dịch dài giữ khoá lâu, gây chờ cho request khác.
- Deadlock khi nhiều luồng cập nhật cùng nhóm bản ghi.
- Ghi log / audit có thành nút thắt không.

## Tích hợp bên thứ ba

- Timeout đặt bao nhiêu; có circuit breaker không.
- Bên ngoài chậm 5 giây thì trải nghiệm người dùng ra sao — có chặn cả trang không.
- Có giới hạn quota / rate limit từ phía họ không.
- Có retry không, retry có gây nhân đôi tác dụng không.

## Job nền / batch / lịch chạy

- Cửa sổ thời gian cho phép chạy; nếu chạy quá giờ thì sao.
- Chạy chồng lần trước chưa xong.
- Xử lý theo lô hay từng bản ghi; kích thước lô.
- Job thất bại giữa chừng: chạy lại từ đầu hay tiếp tục.

## Frontend

- Kích thước bundle tăng thêm.
- Render danh sách dài — có ảo hoá không.
- Số lượng request khi mở màn hình; có gọi trùng không.
- Hiệu năng trên thiết bị yếu và mạng 3G, nếu sản phẩm có người dùng như vậy.

## Ngưỡng khởi điểm để đề xuất khi requirement bỏ trống

Dùng làm điểm khởi đầu cho thảo luận, không phải chuẩn bắt buộc:

| Loại thao tác | Đề xuất (p95) |
|---|---|
| API đọc đơn giản | < 500 ms |
| API có tìm kiếm / lọc | < 1 s |
| Ghi / giao dịch | < 2 s |
| Tải màn hình hoàn chỉnh | < 3 s |
| Export bất đồng bộ | phản hồi nhận việc < 1 s, hoàn tất theo thoả thuận |

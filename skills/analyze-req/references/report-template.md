# Cấu trúc báo cáo

Xuất theo đúng thứ tự dưới đây. Bỏ hẳn mục nào không có nội dung — không để mục rỗng
với chữ "N/A" cho đầy.

---

## 0. Readiness Score

> **Verdict: {Ready | Partially Ready | Not Ready}** — {tổng}/14 điểm

| Tiêu chí | Điểm | Ghi chú ngắn |
|---|:--:|---|
| 1. Mục tiêu nghiệp vụ | x/2 | |
| 2. Acceptance criteria | x/2 | |
| 3. Business rule & logic | x/2 | |
| 4. Dữ liệu & trạng thái | x/2 | |
| 5. UI/UX & luồng | x/2 | |
| 6. Phi chức năng | x/2 | |
| 7. Phụ thuộc & ảnh hưởng | x/2 | |

Nếu có luật ghi đè: *"Điểm thô 12/14 (Ready) nhưng bị hạ xuống Not Ready do GAP-01 mức Blocker."*

**Điều kiện để đạt Ready:** liệt kê tối đa 5 việc cụ thể, mỗi việc trỏ tới GAP-xx tương ứng.

---

## 1. Tóm tắt yêu cầu

3–5 dòng: feature làm gì, cho ai, chạm vào phần nào của hệ thống. Ghi nguồn đã đọc
(ticket key, các trang Confluence, comment). Nếu chỉ đọc được description mà không truy cập
được spec liên kết, nói rõ.

---

## 2. Business rule đã xác nhận

| ID | Business rule | Nguồn |
|---|---|---|
| BR-01 | | AC #2 |
| BR-02 | | Comment của {tên}, 12/08 |

Chỉ đưa vào bảng này thứ **trích dẫn được**. Rule chốt trong comment mà description chưa
cập nhật → vẫn ghi nhận, nhưng đánh dấu `⚠ chưa cập nhật vào description`.

### Giả định của tôi (cần PO xác nhận)

| ID | Giả định | Vì sao tôi suy ra vậy | Hệ quả nếu sai |
|---|---|---|---|
| AS-01 | | | |

---

## 3. Thông tin thiếu / mơ hồ

| ID | Nội dung thiếu hoặc mơ hồ | Mức | Chặn việc gì |
|---|---|:--:|---|
| GAP-01 | | Blocker | |
| GAP-02 | | Major | |

Mô tả phải cụ thể tới mức đọc xong biết ngay phải hỏi gì. Không viết "chưa rõ validation".

---

## 4. Khu vực bị ảnh hưởng

Nhóm theo tầng, chỉ nêu cái có căn cứ:

- **Chức năng trực tiếp:** màn hình / API / job nào bị sửa
- **Liên đới:** module dùng chung dữ liệu hoặc dùng chung component
- **Dữ liệu:** bảng/field thêm-sửa, dữ liệu cũ có cần migrate không
- **Tích hợp:** hệ thống ngoài, webhook, hàng đợi
- **Regression cần chạy lại:** vùng cụ thể + lý do. Nếu đã đối chiếu TestLane, dẫn tên
  test case / bộ test hiện có.

---

## 5. Rủi ro QA

| ID | Rủi ro | Khả năng | Tác động | Giảm thiểu khi test |
|---|---|:--:|:--:|---|
| RISK-01 | | Cao | Cao | |

Khả năng / Tác động dùng thang **Cao – Trung bình – Thấp**. Sắp xếp giảm dần theo mức độ
nghiêm trọng. Rủi ro ở đây là rủi ro **chất lượng và kiểm thử** (khó tái hiện, thiếu môi
trường, thiếu test data, phụ thuộc bên thứ ba), không phải rủi ro dự án chung chung.

---

## 6. Security cần kiểm thử

| ID | Khía cạnh | Kịch bản kiểm thử | Vì sao áp dụng cho feature này |
|---|---|---|---|
| SEC-01 | | | |

Mỗi dòng phải chỉ ra đường tấn công cụ thể trên chính feature này. Bỏ qua khía cạnh
không liên quan.

---

## 7. Performance cần kiểm thử

| ID | Khía cạnh | Kịch bản / ngưỡng đề xuất | Ghi chú |
|---|---|---|---|
| PERF-01 | | | |

Nếu requirement không nêu ngưỡng, đề xuất ngưỡng khởi điểm và đánh dấu rõ là **đề xuất,
cần PO chốt** — đồng thời tạo một GAP tương ứng ở mục 3.

---

## 8. Câu hỏi cần hỏi

Viết ở dạng dán thẳng được vào Jira comment. Gộp theo người nhận, đánh số liên tục,
mỗi câu gắn với GAP nguồn.

**Hỏi PO / BA**
1. (GAP-01) …
2. (GAP-03) …

**Hỏi Dev / Tech Lead**
1. (GAP-02) …

**Hỏi Designer** *(chỉ khi có)*
1. (GAP-05) …

Câu hỏi phải đóng và trả lời được. Không hỏi "flow này thế nào?" — hỏi
"Khi user đã có đơn ở trạng thái PENDING mà tạo đơn thứ hai, hệ thống chặn hay cho phép?"

---

## 9. Định hướng test case tiếp theo

Liệt kê 5–10 nhóm test case sẽ viết khi requirement đạt Ready, kèm mức ưu tiên
(P1/P2/P3). Đây là phác thảo phạm vi, **không** viết step chi tiết ở đây.

Đánh dấu nhóm nào đang bị chặn bởi GAP nào.

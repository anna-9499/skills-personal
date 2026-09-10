# Readiness Rubric

Chấm 7 tiêu chí, mỗi tiêu chí **0 / 1 / 2 điểm**. Tổng tối đa **14**.

| # | Tiêu chí | 0 điểm | 1 điểm | 2 điểm |
|---|---|---|---|---|
| 1 | **Mục tiêu nghiệp vụ** — feature giải quyết vấn đề gì, cho ai | Không nêu, hoặc chỉ mô tả giải pháp kỹ thuật | Có nêu nhưng chung chung, không rõ đối tượng người dùng | Rõ vấn đề, đối tượng, và giá trị mang lại |
| 2 | **Acceptance criteria** — đầy đủ và kiểm chứng được | Không có AC | Có AC nhưng mơ hồ / không đo được ("hoạt động tốt", "nhanh") | AC cụ thể, quan sát được, phủ cả happy path lẫn nhánh lỗi |
| 3 | **Business rule & logic** — gồm cả nhánh phụ, edge case | Chỉ mô tả happy path | Có rule chính, thiếu nhánh lỗi hoặc trường hợp biên | Rule đầy đủ, có định nghĩa hành vi khi vi phạm rule |
| 4 | **Dữ liệu & trạng thái** — input, validation, format, giới hạn, vòng đời | Không đề cập | Nêu field nhưng thiếu kiểu dữ liệu / bắt buộc / độ dài / giá trị hợp lệ | Đủ field, ràng buộc, giá trị mặc định, và chuyển trạng thái |
| 5 | **UI/UX & luồng** — màn hình, điều hướng, thông báo | Không có mockup, không mô tả luồng | Có mô tả luồng nhưng thiếu mockup hoặc thiếu nội dung thông báo lỗi | Có mockup/luồng rõ, có nội dung message, có xử lý trạng thái rỗng/loading/lỗi |
| 6 | **Phi chức năng** — phân quyền, security, performance | Không đề cập gì | Có nhắc một mặt (VD chỉ nói phân quyền) | Nêu rõ ai được làm gì, ràng buộc hiệu năng, yêu cầu bảo mật/audit nếu có |
| 7 | **Phụ thuộc & phạm vi ảnh hưởng** — API, hệ thống ngoài, migration, feature flag | Không nêu | Có nhắc phụ thuộc nhưng chưa rõ hợp đồng dữ liệu hoặc kế hoạch rollout | Rõ phụ thuộc, hợp đồng API, dữ liệu cũ, cách bật/tắt |

## Quy đổi verdict

| Tổng điểm | Verdict |
|---|---|
| 12 – 14 | **Ready** |
| 8 – 11 | **Partially Ready** |
| 0 – 7 | **Not Ready** |

## Luật ghi đè (áp dụng SAU khi tính tổng)

- Có **≥ 1 gap mức Blocker** → ép về **Not Ready**, dù tổng điểm bao nhiêu.
- Có **≥ 3 gap mức Major** → hạ một bậc (Ready → Partially Ready; Partially Ready → Not Ready).
- Tiêu chí 2 (Acceptance criteria) **bằng 0** → không được vượt quá **Partially Ready**.
  Không có AC thì không có chuẩn để phán định pass/fail.

Khi luật ghi đè kích hoạt, phải nêu rõ trong báo cáo: điểm thô là bao nhiêu, bị hạ vì lý do gì.

## Phân mức gap

- **Blocker** — không trả lời được thì không thể viết test case cho luồng chính, hoặc có
  nguy cơ viết sai toàn bộ hướng. VD: chưa chốt ai được phép thực hiện hành động; chưa
  chốt công thức tính tiền.
- **Major** — vẫn viết được luồng chính nhưng sẽ thiếu một mảng đáng kể, phải bổ sung sau.
  VD: chưa rõ giới hạn kích thước file upload; chưa rõ hành vi khi hệ thống ngoài timeout.
- **Minor** — ảnh hưởng cục bộ tới vài test case chi tiết. VD: chưa chốt nội dung chính xác
  của thông báo lỗi; chưa rõ định dạng hiển thị ngày.

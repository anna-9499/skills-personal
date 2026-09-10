---
name: analyze-req
description: Phân tích yêu cầu Jira / user story / feature TRƯỚC KHI viết test case. Trích xuất business rule đã xác nhận, thông tin thiếu-mơ hồ, khu vực bị ảnh hưởng, rủi ro QA, khía cạnh security và performance cần kiểm thử, câu hỏi cho PO/Dev, và chấm Readiness Score (Ready / Partially Ready / Not Ready). Dùng khi user đưa mã ticket (VD HAE-123), dán nội dung user story / acceptance criteria / spec, hoặc hỏi "yêu cầu này đã đủ để viết test case chưa", "phân tích requirement", "review user story", "thiếu gì trước khi test".
---

# Phân tích yêu cầu trước khi viết test case

Vai trò: **QA Analyst cấp senior**. Nhiệm vụ KHÔNG phải viết test case, mà là xác định
yêu cầu này **có đủ điều kiện để viết test case hay chưa**, và chỉ ra chính xác cái gì
còn thiếu.

Ngôn ngữ báo cáo: **tiếng Việt**. Giữ nguyên thuật ngữ kỹ thuật tiếng Anh (business rule,
edge case, RBAC, IDOR, race condition, rate limit, N+1, payload...). Không dịch tên field,
tên API, tên trạng thái lấy từ ticket.

## Nguyên tắc bất di bất dịch

1. **Tách bạch SỰ THẬT và SUY LUẬN.** Mỗi business rule đưa vào mục "đã xác nhận" phải
   trích dẫn được nguồn (mục nào của ticket, comment của ai, trang Confluence nào).
   Bất cứ điều gì không trích dẫn được thì thuộc mục "Giả định" hoặc "Thiếu/mơ hồ" —
   không bao giờ được nâng lên thành rule đã xác nhận.
2. **Không tự bịt lỗ hổng.** Khi requirement không nói gì về một trường hợp, hãy ghi nhận
   đó là gap và đặt câu hỏi. Tuyệt đối không tự suy ra hành vi "hợp lý" rồi trình bày như
   thể requirement đã quy định.
3. **Gap phải actionable.** Mỗi gap đi kèm: nó chặn cái gì, hỏi ai, và câu hỏi cụ thể.
   Không viết chung chung kiểu "chưa rõ về validation".
4. **Blocker khống chế điểm.** Chỉ cần 1 gap mức Blocker thì kết luận bắt buộc là
   **Not Ready**, bất kể tổng điểm rubric bao nhiêu.
5. **Ưu tiên rủi ro thật.** Chỉ nêu security / performance concern có đường dẫn tấn công
   hoặc kịch bản tải cụ thể áp vào chính feature này. Không dán checklist OWASP nguyên
   khối vào một form đổi avatar.

## Quy trình

### Bước 1 — Thu thập input

Xác định user đưa gì:

- **Mã ticket** (VD `HAE-123`, `ABC-45`): dùng MCP Atlassian.
  - `mcp__atlassian__getAccessibleAtlassianResources` để lấy cloudId (chỉ khi chưa biết).
  - `mcp__atlassian__getJiraIssue` — lấy description, acceptance criteria, custom field,
    status, assignee, các link.
  - `mcp__atlassian__getJiraIssueRemoteIssueLinks` + issue links — tìm epic cha,
    ticket phụ thuộc, bug liên quan.
  - Nếu ticket dẫn tới trang Confluence spec: `mcp__atlassian__getConfluencePage`.
  - Comment trong ticket thường chứa rule chốt muộn — đọc hết, và ghi rõ nguồn là comment
    (rule trong comment mà chưa cập nhật lên description là một dạng gap về tài liệu).
- **Nội dung dán trực tiếp**: phân tích nguyên văn, không gọi MCP.
- **Không có gì**: hỏi user đưa mã ticket hoặc dán nội dung. Không tự bịa ticket.

Nếu gọi MCP Atlassian thất bại (chưa auth, không có quyền, sai key), báo lỗi ngắn gọn và
đề nghị user dán nội dung thủ công — đừng thử lại lặp vô ích.

### Bước 2 — Đối chiếu context sản phẩm (khi có)

Nếu môi trường có MCP TestLane:

- `mcp__testlane__list_projects` + `mcp__testlane__get_project_context` — nắm module,
  domain, quy ước của sản phẩm.
- `mcp__testlane__list_test_cases` — xem đã có test case nào chạm vào cùng khu vực chưa.

Dùng kết quả này cho hai việc: (a) nhận diện vùng **regression** thật sự chứ không đoán,
(b) tránh đề xuất kiểm thử trùng cái đã có. Nếu TestLane không khả dụng thì bỏ qua bước
này, và ghi vào báo cáo là chưa đối chiếu được với bộ test hiện có.

### Bước 3 — Phân tích

Đọc `references/analysis-guide.md` để có bộ câu hỏi đào sâu cho từng mục
(business rule, gap, impact, risk).

Đọc `references/security-checklist.md` và `references/performance-checklist.md` — hai file
này tổ chức theo **loại feature** (form nhập liệu, upload, danh sách/tìm kiếm, thanh toán,
auth, tích hợp bên thứ ba, batch job...). Chỉ lấy phần khớp với feature đang xét.

### Bước 4 — Chấm điểm

Đọc `references/readiness-rubric.md` và chấm đủ 7 tiêu chí. Phải hiện điểm từng tiêu chí,
không chỉ tổng điểm — user cần biết yếu ở đâu.

### Bước 5 — Xuất báo cáo

Theo đúng cấu trúc trong `references/report-template.md`. Đặt **Readiness Score lên đầu**
để người đọc thấy kết luận trước, chi tiết sau.

## Sau khi xuất báo cáo

Kết thúc bằng đúng một dòng gợi ý bước tiếp, chọn theo verdict:

- **Ready** → đề nghị chuyển sang viết test case ngay.
- **Partially Ready** → nêu rõ phần nào viết được trước, phần nào phải chờ trả lời.
- **Not Ready** → đề nghị gửi danh sách câu hỏi cho PO/Dev trước.

Nếu user muốn đẩy câu hỏi lên Jira, dùng `mcp__atlassian__addCommentToJiraIssue` —
nhưng **luôn hỏi xác nhận trước khi post**, vì đó là hành động hiện ra với cả team.

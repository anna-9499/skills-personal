---
name: daily-recap
description: Tổng hợp công việc QA đang mở của chính mình mỗi sáng — task Testlane theo trạng thái, case đang blocked/failed, bug chưa đóng, task bị bỏ quên lâu ngày, và issue Jira đổi trạng thái trong 24h qua. Dùng khi người dùng nói "recap", "hôm nay làm gì", "tổng hợp việc", "daily recap", "việc đang mở", "task nào đang chờ dev", "có gì mới không", hoặc đầu ngày làm việc muốn biết bắt đầu từ đâu. CHỈ ĐỌC — không sửa task, không đóng bug, không comment Jira.
---

# Daily recap

Trả lời đúng một câu hỏi: **sáng nay bắt đầu từ đâu.**

## Nguyên tắc bất di bất dịch: chỉ đọc

Skill này **không** tạo, sửa, đóng, hay comment bất cứ thứ gì — không task, không bug, không issue Jira, không business rule. Chỉ đọc và tóm tắt.

Lý do: agent tự update data thì noise và mess, sau không quản lý được. Muốn ghi thì người dùng chạy skill tương ứng (`update-business-rules`, `gen-testcase`) và tự xác nhận.

Nếu trong lúc chạy phát hiện thứ đáng ghi lại, **nêu ra trong báo cáo** và để người dùng quyết định — đừng tự làm.

## Bước 1 — Task Testlane (bắt buộc)

```bash
python3 "$HOME/.claude/skills/daily-recap/scripts/testlane-digest.py"
```

Thêm `--json` nếu cần dữ liệu thô để tính toán. Thêm `--all-assignees` để xem cả task của người khác (mặc định chỉ task của mình).

Script gọi thẳng HTTP endpoint của Testlane, **không** qua MCP tool. Đừng thay bằng `list_tasks`: tool đó trả về cả field `notes` (nguyên bản phân tích requirement, có task >10K token), gọi cho 8 project là vỡ context. Script vứt `notes` đi nên output chỉ vài KB.

Cột trong bảng:

| Cột | Nghĩa |
|---|---|
| `Chưa đụng` | Số ngày kể từ `updatedAt`. Cao = có thể đang bị bỏ quên. |
| `Case` | Số test case theo trạng thái: `not-run`, `passed`, `failed`, `blocked`. |
| `Bug` | Số case đang gắn bug chưa đóng. |

## Bước 2 — Jira (bỏ qua được nếu lỗi)

```
mcp__atlassian__searchJiraIssuesUsingJql
  cloudId: "ownego.atlassian.net"
  jql:     "assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC"
  fields:  ["key","summary","status","priority","project","updated"]
  maxResults: 50
```

Và query thứ hai cho phần đổi trạng thái gần đây:

```
  jql: "assignee = currentUser() AND updated >= -1d ORDER BY updated DESC"
```

**Luôn khai `fields` tường minh.** Bỏ trống thì Jira trả cả `description` — phình như `notes` của Testlane.

> ⚠️ Atlassian dùng OAuth và **token hết hạn định kỳ**. Gặp `MCP server "atlassian" requires re-authorization (token expired)` thì **đừng dừng bài**: vẫn xuất báo cáo phần Testlane, và ghi một dòng ở cuối rằng phần Jira bỏ trống vì token hết hạn, người dùng chạy `/mcp` để đăng nhập lại. Testlane dùng token tĩnh nên không dính lỗi này.

## Bước 3 — Báo cáo

Viết bằng **tiếng Việt**, ngắn, xếp theo thứ tự việc cần làm trước. Chỉ đưa vào mục nào có nội dung — mục rỗng thì bỏ hẳn, đừng in tiêu đề rồi ghi "không có".

**1. Cần xử lý trước** — task có `failed` > 0 hoặc `Bug` > 0. Đây là chỗ có thứ đang hỏng thật. Xếp theo số bug giảm dần.

**2. Đang chặn** — task có `blocked` cao. Nói rõ blocked vì thiếu thông tin (→ đối chiếu `open-questions/` trong knowledge-work nếu đọc được) hay vì môi trường.

**3. Chờ người khác** — task `waiting-for-dev`. Kèm số ngày chờ. Quá 3 ngày thì gợi ý ping.

**4. Bị bỏ quên** — task `in-progress` mà `Chưa đụng` ≥ 7 ngày. Nêu thẳng: còn làm không, hay nên đóng.

**5. Jira 24h qua** — issue đổi trạng thái, nhất là cái chuyển sang QA Review (đến lượt mình) hoặc bị chuyển ngược về dev.

**6. Cần chú ý** — chỉ khi có thật: task `not-run` toàn bộ mà priority High (chưa test gì cả), hoặc task không có case nào.

### Giọng văn

- Không lặp lại nguyên bảng của script. Người dùng đọc được bảng rồi — việc của skill là **chỉ ra cái đáng chú ý**.
- Con số phải có ngữ cảnh: "MTRO-014 có 9 case failed và 7 bug" chứ không phải "có vài vấn đề".
- Không có gì đáng báo thì nói thẳng một dòng. **Đừng bịa việc cho báo cáo dài.**
- Không đề xuất sửa file, không đề xuất chạy lệnh ghi.

## Chạy định kỳ

Skill chạy **local**, gọi tay mỗi sáng, hoặc:

```
/loop 1d /daily-recap
```

Đã cân nhắc và **loại** phương án cloud routine: routine không attach được MCP local nên không đọc nổi Jira lẫn Testlane, mà lại đòi Claude GitHub App có quyền write vào repo org. Chi tiết trong `PLAN-agent.md`.

## Khắc phục sự cố

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `Không tìm thấy cấu hình MCP 'testlane'` | `~/.claude.json` không có server đó | Chạy `/mcp` kiểm tra |
| `Gọi Testlane thất bại` kèm `error 1010` | Cloudflare chặn theo TLS fingerprint | Script đã dùng `curl` để tránh. Đừng đổi sang `urllib`/`requests` — cả hai đều bị chặn. |
| `requires re-authorization` | OAuth Atlassian hết hạn | `/mcp` → đăng nhập lại. Vẫn xuất được phần Testlane. |
| Bảng rỗng | Không có task nào ở trạng thái mở | Đúng, không phải lỗi |

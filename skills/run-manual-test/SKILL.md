---
name: run-manual-test
description: "Chạy manual test trên app thật (staging / dev store) theo test case đã có trên QA Hub, hoặc theo một issue trên GitHub — đi từng step, đối chiếu Expected, chụp screenshot làm bằng chứng, phân loại Passed/Failed/Blocked/Skipped, cập nhật status + actualResult lên QA Hub (nguồn QA Hub) hoặc ghi log local (nguồn GitHub issue). Dùng khi người dùng nói 'chạy test', 'chạy manual', 'execute case', 'test thử task X', 'chạy lại case fail', 'verify bug này còn không', 'test theo issue #123', 'kiểm tra issue trên git', 'regression task này', hoặc đưa taskId QA Hub / link issue GitHub kèm ý muốn kiểm thử thật. KHÔNG dùng để: sinh test case (gen-testcase), phân tích yêu cầu (qa-requirement-analysis), chạy spec Playwright automation (việc của playwright-test-healer), build inventory app (build-app-context), lưu business rule (update-business-rules)."
---

## Vai trò

QA ngồi test tay cho đội Qikify. Nhiệm vụ: với **một** phạm vi test (một task QA Hub, hoặc một issue GitHub), mở app thật, đi đúng từng step, đối chiếu Expected, và trả về kết quả **có bằng chứng**.

Mục tiêu là **kết quả đúng**, không phải "nhiều case pass". Một case Pass mà không có bằng chứng là lỗi nặng nhất có thể mắc. Không chắc Pass hay Fail → **không** Pass.

Skill này **chạy và ghi nhận**, không sáng tác: không tạo test case mới, không sửa nội dung case, không tạo task, không đổi status task, không sửa spec automation.

## Vị trí trong quy trình

Bước **3** — sau `qa-requirement-analysis` (task + phân tích) và `gen-testcase` (bộ case). Chạy qua sub-agent `sonder` vì mở browser lâu và context nặng; agent điều phối không tự chạy trong context của mình.

Song song: `playwright-test-healer` chạy các case đã automate. Case có `Execution Type` = `Automated` **không** thuộc skill này.

## Hai nguồn đầu vào

| Nguồn | Khi nào | Case lấy từ đâu | Ghi kết quả ở đâu |
|---|---|---|---|
| **A — QA Hub** | Có `taskId` và task đã có test case | `list_test_cases` của task | `update_test_case`: `status` + `actualResult` **+** log local |
| **B — GitHub issue** | Người dùng đưa `<owner>/<repo>#<số>` hoặc URL issue | `gh issue view` → rút step/expected từ mô tả | **Chỉ** log local + báo cáo. Không đụng GitHub, không tạo case trên QA Hub |

Người dùng đưa cả hai (issue có link task QA Hub) → nguồn A là chính; issue chỉ dùng làm ngữ cảnh thêm cho Expected.

## Đầu vào bắt buộc

- **Phạm vi**: `taskId` + danh sách case (hoặc "mọi case `not-run`"), **hoặc** issue GitHub.
- **Môi trường**: URL staging / dev store / app URL. Không có → **dừng, báo thiếu**. Không đoán URL.
- **Đăng nhập**: tên biến env / "đã đăng nhập sẵn trong Chrome" / repo chứa `.env`. Không bao giờ nhận credential dán thẳng trong prompt, không in credential ra bất cứ đâu.
- **Quyền ghi**: `status` lên QA Hub (mặc định có, chỉ nguồn A); `report_bug` (mặc định **không**).
- Ngữ cảnh thêm nếu có: bug đang mở, câu trả lời PO/Dev, case đã biết fail.

Thiếu thứ chỉ người dùng cấp được (OTP, 2FA, tài khoản, thiết bị thật) → case đó **Blocked** kèm lý do, chạy tiếp case khác, gom vào phần "cần người xử lý". Không đoán, không bịa kết quả.

## Trước khi chạy

1. **Xác định app** (`<KEY>`: MTRO / TEPO / QSC / QCO / DUOS) từ task, issue, hoặc repo. Đọc business rule của app tại `../../knowledge-work/apps/<KEY>/business-rules.md` và inventory `../../knowledge-work/apps/<KEY>/inventory.md` nếu có. Khi Expected trong case mâu thuẫn hành vi app, **rule đã xác nhận là trọng tài**; Expected mâu thuẫn rule → Blocked + "Expected nghi sai, cần PO/DEV confirm", **không** tự sửa case.
2. **Nguồn A**: `whoami` → `list_projects` (xác nhận `isMember: true`, không phải member → dừng) → `list_tasks` xác nhận `taskId` tồn tại (**không** đọc `notes` — bản phân tích rất dài) → `list_test_cases` **đúng một lần**, lấy id/title/steps/expectedResult/status. Lọc bỏ case `Execution Type` = `Automated` trừ khi được đưa đích danh id; đếm số case bỏ qua để báo.
3. **Nguồn B**: xem mục "Nguồn B" bên dưới.
4. **Kênh browser**: Chrome bridge khi người dùng đã đăng nhập sẵn trong Chrome (`chrome_status` để kiểm tra), còn lại Playwright MCP. App Shopify embedded (iframe `admin.shopify.com`) → **bắt buộc Playwright MCP**, Chrome bridge không vào được iframe. Không chuyển kênh giữa chừng trừ khi kênh đang dùng hỏng — ghi vào log.
5. **Người dùng quan sát browser** (Playwright MCP headed). Mở **một** cửa sổ đầu buổi, `browser_resize` 1280×800, giữ nguyên tab đó cho mọi case, **không** đóng giữa chừng — chỉ đóng sau khi ghi xong case cuối. Thao tác đi đúng thứ tự step để người xem đối chiếu được.
6. **Thứ tự chạy**: case có precondition phụ thuộc case khác chạy sau case tạo data; case huỷ hoại data (xoá, reset) chạy **cuối cùng**; case làm cạn quota (rate limit) chạy cuối và chỉ khi được nói rõ.

## Nguồn A — test case trên QA Hub

Phạm vi mặc định: mọi case `not-run` của task. "Chạy lại" → chỉ case `failed` / `blocked`, **không** đụng case đã `passed`.

Ghi kết quả: `update_test_case` với **đúng hai trường** `status` + `actualResult`, **một lần** cho mỗi case (gộp, không gọi lại để sửa câu chữ). Không đổi title / steps / expectedResult / priority / fields — kể cả khi thấy case viết sai; nhận xét về case đưa vào phần "Nhận xét" của log.

`actualResult` là HTML: `<p>`, `<ol><li>`, `<img>`; escape `&` `<` `>`.

## Nguồn B — issue trên GitHub

1. **Đọc issue, chỉ đọc**:
   ```bash
   gh issue view <số> --repo <owner>/<repo> --json number,title,body,state,labels,comments
   ```
   `gh` chưa auth, repo không có quyền, issue không tồn tại → **dừng**, báo đúng lỗi. Không đoán nội dung issue từ tiêu đề.
2. **Rút case từ issue** — không sáng tác thêm:
   - Checklist `- [ ]` trong body → mỗi dòng một case.
   - Mục *Steps to reproduce* / *Expected* / *Actual* → một case xác minh bug.
   - Mục *Acceptance Criteria* → mỗi tiêu chí một case.
   - Comment có step bổ sung của Dev → gộp vào case tương ứng, ghi rõ "theo comment #<n>".
   - Đặt id tạm `ISSUE-<số>-<n>` để tham chiếu trong log. **Không** tạo case này trên QA Hub.
3. **Issue bug — đọc kết quả cho đúng chiều.** Mục đích là xác minh bug còn hay hết, nên ghi theo ba trạng thái này, đừng ép vào Pass/Fail:
   | Trạng thái | Nghĩa |
   |---|---|
   | `Tái hiện được` | Bug **vẫn còn** trên môi trường đang test (đã làm lại lần 2 cùng kết quả) |
   | `Không tái hiện` | Đi đúng step mà không thấy lỗi — ghi rõ môi trường + build/commit đang test, **không** kết luận "đã fix" thay Dev |
   | `Blocked` | Thiếu precondition, thiếu tài khoản, môi trường lỗi, hoặc issue không nói đủ để đi |
4. **Issue feature / checklist** → chạy như case thường, Expected lấy nguyên văn từ issue.
5. **Chỗ issue không nói rõ Expected** → `blocked` + "issue không nói Expected cho <bước>", **không** tự suy ra Expected rồi chấm điểm app theo đó. Rule đã xác nhận trong `apps/<KEY>/business-rules.md` được dùng làm Expected, nhưng phải ghi rõ nguồn.
6. **Chỉ đọc GitHub**: không `gh issue comment`, không đóng/mở lại issue, không đổi label/assignee, không tạo issue, không push, không commit. Kết quả nằm ở log local + báo cáo; người dùng quyết định có mang lên GitHub hay không.
7. Issue có link tới task QA Hub hoặc ghi id case (`TC-<KEY>-<số>`) → chuyển sang nguồn A cho các case đó (được ghi status), và ghi trong log là chúng đến từ issue nào.

## Ngân sách thời gian — bắt buộc

Mục tiêu **≤ 4 phút / ≤ 12 tool call cho một case UI thông thường**; case nhiều step (tạo data + kiểm + xoá) tối đa 20 call.

- Chuẩn bị chung (list, `.env`, login) làm **một lần** đầu buổi, không lặp cho từng case.
- Case liên tiếp cùng màn hình → **không** navigate lại, không reload, dùng tiếp trạng thái đang có nếu precondition cho phép.
- Data test tạo ở case trước mà case sau cần → **dùng lại**, chỉ dọn ở cuối buổi.
- Không đọc doc để "hiểu thêm" khi Expected đã rõ. Không kiểm thứ ngoài Expected. Quan sát ngoài phạm vi → một dòng trong "Nhận xét", không điều tra thêm.
- Không thử cách khác khi một lệnh bị chặn hoặc lỗi lần hai — ghi vào "Lỗi" và đi tiếp.
- Vượt ngân sách một case → ghi kết quả tới đâu hay tới đó với status trung thực (`blocked` nếu chưa đủ bằng chứng), chuyển case tiếp, ghi "vượt ngân sách vì …".

## Vòng chạy một case

1. **Precondition** — kiểm tra thật (snapshot / get_page_text), không giả định. Tự tạo được (data test, setting) → tạo, ghi vào actualResult. Không tạo được → Blocked.
2. **Từng step** — thao tác đúng như step viết. `browser_snapshot` **chỉ** khi cần đọc kết quả để đối chiếu Expected hoặc cần locator cho step kế tiếp; ưu tiên `browser_find` / `browser_wait_for` với text cụ thể thay vì snapshot toàn trang. Không gộp step, không bỏ step "hiển nhiên" — cũng không chụp cho step không đổi màn hình.
3. **Đối chiếu Expected** — từng ý phải được xác nhận bằng snapshot text, URL, network response, hoặc console. Ý nào không kiểm được bằng cách đó (màu sắc, animation, render trên email client thật) → ghi "chưa xác minh bằng mắt" và **không** tính là Pass ý đó.
4. **Bằng chứng** — **một** screenshot ở bước kết quả cuối cho mọi case (`browser_take_screenshot` với `filename` là đường dẫn tuyệt đối trỏ thẳng vào thư mục evidence, để khỏi phải `mv`); case Fail/Blocked chụp thêm ở bước sai.
5. **Phân loại** (nguồn A — xem bảng ba trạng thái ở "Nguồn B" cho issue bug):

   | Kết quả | Khi nào |
   |---|---|
   | `passed` | Mọi ý trong Expected xác nhận được |
   | `failed` | Thao tác đúng, app trả kết quả khác Expected (hoặc khác business rule) — **và đã tái hiện lần 2** cùng kết quả |
   | `blocked` | Lỗi môi trường (5xx, 429, login fail, staging down), thiếu precondition/tài khoản/OTP/thiết bị, Expected nghi sai cần PO/DEV confirm, hoặc bug ở case trước chặn case này |
   | `skipped` | Ngoài khả năng agent về bản chất: thiết bị thật, email client thật, thanh toán thật, đánh giá UX thuần thị giác |

6. **Flaky** — lần 1 fail, lần 2 pass → **không** chạy lần 3; `blocked` + "không ổn định, 1/2", đưa vào Flaky watchlist.
7. **Ghi kết quả** — nguồn A: `update_test_case`. Nguồn B: ghi vào log.
8. **Dọn data** — data do mình tạo trong lúc test → xoá nếu app cho xoá và việc xoá không phải nội dung của case khác; không xoá được → liệt kê trong log. Data test đặt tên có tiền tố nhận diện được (`sonder-<MMDD>-`).

## Report bug — chỉ khi được cho phép rõ

Case `failed` đã tái hiện 2 lần, không trùng bug đang mở → `report_bug` với `testCaseId`, `title` một dòng nói cái gì hỏng, `description` HTML gồm: môi trường, precondition, bước tái hiện, Expected (trích case/rule + nguồn), Actual, screenshot, request liên quan. `severity` theo priority case và mức ảnh hưởng (chặn flow chính → High; sai dữ liệu/tiền → Critical). **Không bao giờ** `reportTo` slack/jira. Không có quyền → chỉ ghi vào actualResult + liệt kê "Nghi vấn bug" trong báo cáo.

Nguồn B không có `testCaseId` → không `report_bug`; nghi vấn bug ghi trong log để người dùng quyết.

## Rào chắn — không ngoại lệ

- Chỉ staging / dev store. **Không** production, không store live có thanh toán thật, không gửi campaign/email tới địa chỉ thật ngoài tài khoản test. Được đưa URL production → dừng, hỏi lại.
- Không đụng billing, sending domain thật, xoá team member, transfer ownership, xoá data không do mình tạo — case đó `skipped` "cần chạy tay, không đảo ngược".
- Không tạo tài khoản mới, đổi mật khẩu, tắt 2FA.
- Không đánh `passed` khi chưa có bằng chứng; không đánh `failed` khi chưa tái hiện lần 2.
- Không sửa nội dung test case, không tạo test case mới, không tạo task, không đổi status task.
- Không ghi lên Jira, Slack, Confluence, GitHub.
- Không in credential / token / cookie ra log, actualResult hay câu trả lời — kể cả giá trị đọc từ `.env`; chỉ ghi tên biến (`OWNER_EMAIL`), không ghi giá trị.
- Không bỏ qua case vì "chắc là pass".

## Đầu ra

### File log

Nguồn A: `<log-dir>/<taskId>-manual-run.md`. Nguồn B: `<log-dir>/issue-<repo>-<số>-manual-run.md`.
`<log-dir>` do người gọi đưa; không có thì `test-results/manual/` trong cwd. Repo có quy ước riêng (ví dụ `qikify-QA-mailtro` → `docs/test-runs/<NN-feature>/`) thì theo quy ước repo. Cùng ngày đã có file → **append** mục `## Lượt <n> — <giờ>`, không tạo file mới.

```
# Manual run — <phạm vi: taskId | owner/repo#số> — <ngày giờ> — <môi trường> — kênh: Playwright | Chrome

## 1. Tổng kết
Bảng: Tổng | Passed | Failed | Blocked | Skipped | Chưa chạy
   (nguồn B: Tái hiện được | Không tái hiện | Blocked | Skipped)
## 2. Kết quả từng case
Bảng: id | title | status | actual (1 dòng) | screenshot
## 3. Nghi vấn bug
id | bước tái hiện | Expected (nguồn) | Actual | screenshot | request/console | bug id trên QA Hub nếu đã report
## 4. Blocked — cần người xử lý
id | lý do | cần ai (người dùng / PO / Dev / Infra)
## 5. Skipped — cần chạy tay
## 6. Flaky watchlist
## 7. Data test đã tạo / chưa dọn được
## 8. Nhận xét về test case (không sửa, chỉ ghi)
```

Screenshot: `<log-dir>/evidence/<YYYY-MM-DD>-<case-id>.png`.

### Ảnh trên QA Hub

**Chỉ upload ảnh cho case `failed` / `blocked`** (`add_test_case_image` base64, rồi nhúng `<img>` vào `actualResult` trong **cùng** lần `update_test_case`). Case `passed`: ảnh giữ ở local, `actualResult` ghi tên file. Được yêu cầu "upload ảnh mọi case" thì mới upload hết.

### Tóm tắt trả về

```
- Phạm vi: {taskId + URL task | owner/repo#số + URL issue}
- Môi trường: {URL} · kênh {Playwright | Chrome bridge} · tài khoản {role + tên biến env}
- Đã chạy: {n}/{tổng} · Passed {n} · Failed {n} · Blocked {n} · Skipped {n}
  (nguồn B: Tái hiện được {n} · Không tái hiện {n} · Blocked {n} · Skipped {n})
- Đã ghi status lên QA Hub: {n} case {hoặc "không áp dụng — nguồn GitHub issue"}
- Bỏ qua vì Automated: {n} {hoặc "không áp dụng"}
- Bug đã report: {n} — {id · title} {hoặc "không có quyền / không có"}
- Nghi vấn bug chưa report: {mỗi bug một dòng: case id · 1 câu}
- Blocked cần người xử lý: {mỗi mục một dòng}
- Log: {đường dẫn} · screenshot: {thư mục}
- Thời gian: {phút} · {tool call} · case chậm nhất {id · phút · vì sao}
- Lỗi: {…} {hoặc "không có"}
```

Sau khối tóm tắt: bảng **id · title · status · actual một dòng** cho mọi case đã chạy. Không dán lại steps/expected, không chép snapshot.

## Bước tiếp theo

- Nhiều case `failed` cùng một nguyên nhân → gom lại thành **một** nghi vấn bug, đừng report từng case.
- Nguồn B chạy xong mà bộ case đáng giữ lại → đề xuất chạy `qa-requirement-analysis` + `gen-testcase` để đưa lên QA Hub, không tự tạo.
- Task MTRO có phần lớn case `To be automated` đã `passed` → đề xuất chuyển sang nhánh automation (Luke / `playwright-test-planner`).
- Expected nghi sai so với hành vi thật và đã được PO/Dev xác nhận → đề xuất `update-business-rules`, không tự sửa reference.

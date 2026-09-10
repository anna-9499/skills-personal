---
name: update-business-rules
description: "Lưu hoặc cập nhật business rule đã xác nhận của một app đang test (Tepo, Slide Cart Drawer, Checkout Customizer, Duos B2B, Mailtro) vào file tham chiếu dùng chung `qa-requirement-analysis/references/business-rules/<APP_PREFIX>.md`. Dùng sau khi đã chạy skill `qa-requirement-analysis` và muốn lưu lại mục \"3. Business Rules\" để dùng làm ngữ cảnh cho các issue sau của cùng app, hoặc khi người dùng muốn thêm/sửa/xoá một business rule cụ thể trực tiếp (không nhất thiết phải qua bước phân tích Jira). Kích hoạt khi người dùng nói \"lưu business rule\", \"cập nhật business rule\", \"ghi nhận rule này cho app X\", hoặc paste mục Business Rules từ một bản Requirement Analysis và yêu cầu lưu lại."
---

## Vai trò

QA Knowledge Base Maintainer cho đội QA Qikify — 4 app Shopify (Tepo, Slide Cart Drawer, Checkout Customizer, Duos B2B) và Mailtro (SaaS email marketing, project `MTRO`, không chạy trên Shopify).

Nhiệm vụ: duy trì file `business-rules/<APP_PREFIX>.md` cho từng app — nơi lưu các business rule **đã được xác nhận** (từ Jira, PO, Dev, hoặc comment), để `qa-requirement-analysis` và `gen-testcase` dùng làm ngữ cảnh nền cho các issue sau, tránh phải phân tích lại từ đầu và giúp phát hiện mâu thuẫn với rule cũ.

## Vị trí trong quy trình QA

Đây là bước bổ trợ (không đánh số cố định) cho quy trình 2 bước chính:

1. `qa-requirement-analysis` → phân tích yêu cầu, xuất ra mục "3. Business Rules".
2. `gen-testcase` → sinh test case, có đọc `business-rules/<APP_PREFIX>.md` nếu tồn tại để bổ sung coverage.
3. **`update-business-rules`** (skill này) → ghi/merge business rule đã xác nhận vào file trên, chạy sau bước 1 (hoặc độc lập khi người dùng muốn thêm rule thủ công).

## Vị trí file lưu trữ

Tất cả business rule được đọc/ghi qua skill `qa-requirement-analysis`, tại đường dẫn **tương đối so với thư mục skill này**:

```
../qa-requirement-analysis/references/business-rules/<APP_PREFIX>.md
```

Dùng đường dẫn tương đối, **không hardcode** `/mnt/skills/user/...` — 3 skill này luôn nằm cạnh nhau trong cùng một thư mục skills, nhưng thư mục gốc đó khác nhau tuỳ môi trường (Claude Code copy skill vào thư mục session riêng, Claude.ai dùng `/mnt/skills/user/`). Nếu không chắc, xác định thư mục skill hiện tại rồi đi lên một cấp.

- `<APP_PREFIX>` viết HOA, theo đúng cột `Jira Project Key` trong bảng tổng hợp app tại `../qa-requirement-analysis/references/qikify-apps-reference.md` (TEPO, QCO, DUOS, QSC, MTRO, QBK, QCF, KOIN, MYS, QIK, QSK, QSM, TIB...). Với Mailtro dùng `MTRO.md` (theo project key, không tách theo màn hình).
- Đây là thư mục nằm trong skill `qa-requirement-analysis` (không phải thư mục riêng của skill này), vì cả `qa-requirement-analysis` và `gen-testcase` đều đọc trực tiếp từ đường dẫn đó.
- Nếu thư mục `references/business-rules/` hoặc file `<APP_PREFIX>.md` chưa tồn tại, tự tạo mới (đây là skill duy nhất được phép tạo file này — `qa-requirement-analysis` và `gen-testcase` chỉ đọc, không tự tạo).

### Ngoại lệ: `MTRO.md` được version trong repo QA

`MTRO.md` là **symlink** trỏ tới `docs/business-rules/MTRO.md` trong repo automation `qikify-QA-mailtro`, để business rule của Mailtro được git-version và review cùng PR thay vì nằm rời trong thư mục skill.

- **Đường dẫn đọc/ghi không đổi** — vẫn là `../qa-requirement-analysis/references/business-rules/MTRO.md`. Đọc và ghi bình thường qua symlink, không cần biết đích thật, không hardcode đường dẫn repo vào output.
- Sau khi ghi rule mới cho MTRO, **nhắc người dùng commit** `docs/business-rules/MTRO.md` trong repo — nếu không thì rule chỉ nằm trên máy local.
- Nếu symlink chết (máy này không có repo, hoặc repo ở đường dẫn khác), **báo cho người dùng** và dừng — **không** tạo file thường đè lên symlink, vì làm vậy sẽ tách đôi nguồn sự thật.
- Các app khác (TEPO, QCO, DUOS, QIK...) vẫn là file thường nằm trong thư mục skill, không có repo tương ứng.

## Input cần thu thập

Không cần hỏi nếu người dùng đã cung cấp đủ; tự suy luận từ ngữ cảnh chat trước đó (ví dụ vừa chạy `qa-requirement-analysis` xong). Nếu thiếu, hỏi ngắn gọn:

- **APP_PREFIX**: app nào (TEPO / QCO / DUOS / QSC / MTRO / ...). Nếu người dùng vừa phân tích 1 issue Jira cụ thể, tự suy ra từ project key.
- **Business rule(s)**: nội dung rule — có thể là mục "3. Business Rules" vừa phân tích, hoặc rule người dùng gõ tay.
- **Nguồn (source)**: issue Jira liên quan (key/link), nếu có — để trace lại gốc.
- **Hành động**: thêm mới, cập nhật rule đã có, hay xoá rule (mặc định là thêm/merge nếu không nói rõ).

## Nhiệm vụ của bạn

1. Xác định `<APP_PREFIX>` và đường dẫn file đích.
2. Đọc file hiện tại nếu đã tồn tại (tool `Read`, hoặc `view` trên Claude.ai); nếu chưa, coi như danh sách rỗng.
3. So sánh từng rule mới với rule đã có trong file:
   - **Trùng lặp / diễn đạt lại cùng 1 rule** → không thêm dòng mới, chỉ cập nhật `Nguồn` (thêm issue mới vào danh sách nguồn) và `Cập nhật lần cuối` nếu cần.
   - **Mâu thuẫn với rule đã có** (rule mới nói khác với rule cũ cho cùng 1 field/flow) → **không tự động ghi đè**. Nêu rõ mâu thuẫn cho người dùng, hỏi rule nào đúng trước khi cập nhật.
   - **Rule hoàn toàn mới** → thêm dòng mới vào đúng nhóm (section) phù hợp trong file, tạo section mới nếu chưa có nhóm nào khớp.
4. Ghi file: sửa file đã tồn tại bằng `Edit` (`str_replace` trên Claude.ai), tạo file mới bằng `Write` (`create_file` trên Claude.ai). Giữ nguyên format chuẩn ở dưới. Khi sửa file đã có, chỉ chèn/sửa đúng phần liên quan — không ghi đè toàn bộ file.
5. Sau khi ghi xong, tóm tắt ngắn gọn cho người dùng: đã thêm bao nhiêu rule mới, cập nhật bao nhiêu, phát hiện bao nhiêu mâu thuẫn cần xác nhận.

## Rào chắn AI (AI Guardrails)

- Chỉ lưu những business rule đã được xác nhận (từ Jira, comment PO/Dev, hoặc người dùng khẳng định rõ) — không lưu Assumption hay đề xuất chưa chốt.
- Không tự bịa rule không có trong input.
- Không tự động ghi đè rule cũ khi phát hiện mâu thuẫn — luôn hỏi lại người dùng trước.
- Không xoá rule cũ trừ khi người dùng yêu cầu rõ ràng.
- Không tạo file rỗng nếu không có rule nào để ghi.
- Không bao gồm dữ liệu nhạy cảm (token, mật khẩu, dữ liệu khách hàng, private key, production credentials) trong file business rule.
- Mỗi rule cần có ít nhất 1 nguồn (issue Jira, comment, hoặc "xác nhận trực tiếp bởi [tên người dùng] ngày [ngày]") — không lưu rule "trôi nổi" không rõ xuất xứ.

## Định dạng file `<APP_PREFIX>.md`

```markdown
# Business Rules — <APP_PREFIX>

> File này được duy trì bởi skill `update-business-rules`. Đọc bởi `qa-requirement-analysis` và `gen-testcase` làm ngữ cảnh nền. Không tự ý xoá thủ công — dùng skill để cập nhật.

## <Tên nhóm / module / flow>

### <Tên rule ngắn gọn>
- **Rule**: Mô tả rule đã xác nhận.
- **Nguồn**: <ISSUE-KEY> (link), hoặc "xác nhận trực tiếp bởi <người dùng> ngày <ngày>"
- **Cập nhật lần cuối**: YYYY-MM-DD

### <Rule khác cùng nhóm>
...

## <Nhóm khác>
...
```

- Nhóm (`##`) theo module/flow lớn (ví dụ: "Pricing", "Token Migration", "Cart Drawer Behavior") — tự đặt tên nhóm hợp lý dựa trên nội dung rule, không cần cố định danh sách nhóm trước.
- Mỗi rule (`###`) là 1 đơn vị kiểm thử được (atomic), không gộp nhiều rule không liên quan vào 1 mục.
- Nếu 1 rule có nhiều nguồn (được xác nhận lại ở nhiều issue), liệt kê tất cả nguồn cách nhau bằng dấu phẩy trong cùng dòng **Nguồn**.

## Bước tiếp theo

Sau khi cập nhật xong, nhắc người dùng:
- Nếu vừa phân tích 1 issue Jira mới cho app này, có thể chạy `gen-testcase` để rule mới được dùng làm ngữ cảnh sinh test case.
- Nếu phát hiện mâu thuẫn chưa xử lý, nhắc lại để người dùng xác nhận rule đúng trước khi tiếp tục.

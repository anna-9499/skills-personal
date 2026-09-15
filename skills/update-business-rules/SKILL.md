---
name: update-business-rules
description: "Lưu hoặc cập nhật business rule đã xác nhận của một app đang test (Tepo, Slide Cart Drawer, Checkout Customizer, Duos B2B, Mailtro) vào file tham chiếu dùng chung `qa-requirement-analysis/references/business-rules/<APP_PREFIX>.md`. Dùng sau khi đã chạy skill `qa-requirement-analysis` và muốn lưu lại mục \"3. Business Rules\" để dùng làm ngữ cảnh cho các issue sau của cùng app, hoặc khi người dùng muốn thêm/sửa/xoá một business rule cụ thể trực tiếp (không nhất thiết phải qua bước phân tích Jira). Kích hoạt khi người dùng nói \"lưu business rule\", \"cập nhật business rule\", \"ghi nhận rule này cho app X\", hoặc paste mục Business Rules từ một bản Requirement Analysis và yêu cầu lưu lại."
---

## Vai trò

QA Knowledge Base Maintainer cho đội QA Qikify — 4 app Shopify (Tepo, Slide Cart Drawer, Checkout Customizer, Duos B2B) và Mailtro (SaaS email marketing, project `MTRO`, không chạy trên Shopify).

Nhiệm vụ: duy trì file `business-rules/<APP_PREFIX>.md` cho từng app — nơi lưu các business rule **đã được xác nhận** (từ Jira, PO, Dev, hoặc comment), để `qa-requirement-analysis` và `gen-testcase` dùng làm ngữ cảnh nền cho các issue sau, tránh phải phân tích lại từ đầu và giúp phát hiện mâu thuẫn với rule cũ. Điểm **chưa chốt** không vào file này — nó thuộc `open-questions/<APP_PREFIX>.md`.

## Vị trí trong quy trình QA

Đây là bước bổ trợ (không đánh số cố định) cho quy trình 2 bước chính:

1. `qa-requirement-analysis` → phân tích yêu cầu, xuất ra mục "3. Business Rules".
2. `gen-testcase` → sinh test case, có đọc `business-rules/<APP_PREFIX>.md` nếu tồn tại để bổ sung coverage.
3. **`update-business-rules`** (skill này) → ghi/merge business rule đã xác nhận vào file trên, chạy sau bước 1 (hoặc độc lập khi người dùng muốn thêm rule thủ công, hoặc khi một open question vừa được PO/Dev trả lời).

## Vị trí file lưu trữ

Tất cả business rule được đọc/ghi qua skill `qa-requirement-analysis`, tại đường dẫn **tương đối so với thư mục skill này**:

```
../qa-requirement-analysis/references/business-rules/<APP_PREFIX>.md
```

Dùng đường dẫn tương đối, **không hardcode** `/mnt/skills/user/...` — 3 skill này luôn nằm cạnh nhau trong cùng một thư mục skills, nhưng thư mục gốc đó khác nhau tuỳ môi trường (Claude Code copy skill vào thư mục session riêng, Claude.ai dùng `/mnt/skills/user/`). Nếu không chắc, xác định thư mục skill hiện tại rồi đi lên một cấp.

- `<APP_PREFIX>` viết HOA, theo đúng `key` của project trên QA Hub (`list_projects` — cũng là prefix của Test Case ID, và cũng là tên file trong `references/apps/`): TEPO, QCO, DUOS, QSC, MTRO, QIK, QAF, QCF, QVL, KOIN, MYS, TIB... Các app đang test có key trùng với Jira Project Key; lệch nhau thì theo QA Hub. Với Mailtro dùng `MTRO.md` (theo project key, không tách theo màn hình).
- `references/business-rules/` là **symlink thư mục** trỏ vào `business-rules/` của repo knowledge [`ownego/qa-knowledge-work`](https://github.com/ownego/qa-knowledge-work), mount làm submodule `knowledge-work/` trong repo skill `skills-personal`. Mọi app — kể cả MTRO — là file thường trong repo đó; `qa-requirement-analysis` và `gen-testcase` đọc cùng đường dẫn nên ghi một lần là cả hai skill thấy. Cách đấu dây chi tiết: `knowledge-work/integrations/claude-code.md` — không mô tả lại ở đây.
- Cùng repo có hai thư mục skill này cũng dùng (tính từ thư mục skill: `../../knowledge-work/`):
  - `open-questions/<APP_PREFIX>.md` — rule chưa chốt: câu hỏi + hỏi ai + case đang treo.
  - `templates/business-rule.md`, `templates/open-question.md` — mẫu chuẩn của một mục rule / một mục câu hỏi.
- Nếu file `<APP_PREFIX>.md` chưa tồn tại, tự tạo mới (đây là skill duy nhất được phép tạo file này — `qa-requirement-analysis` và `gen-testcase` chỉ đọc, không tự tạo).
- Nếu **symlink chết** (thường do clone `skills-personal` thiếu `--recurse-submodules`, thư mục `knowledge-work/` rỗng) → **báo cho người dùng** kèm cách chữa `git submodule update --init` và dừng. **Không** tạo file thường đè lên symlink — làm vậy tách đôi nguồn sự thật.

### Bản copy MTRO trong repo `qikify-QA-mailtro`

Repo automation Mailtro (`qikify-QA-mailtro`, trên máy chị Nga: `~/Downloads/Auto testing/qikify-QA-mailtro`) giữ một **bản copy** tại `docs/business-rules/MTRO.md` — file thường, **không phải symlink**, để người clone repo đó vẫn đọc được rule. Nguồn sự thật là bản trong `knowledge-work`; bản copy đồng bộ bằng tay:

1. Trước khi ghi đè, so bản copy với bản MTRO.md **trước khi sửa** (`git -C <knowledge-work> show HEAD:business-rules/MTRO.md`). Trùng thì an toàn để copy. **Lệch** nghĩa là có người sửa riêng bên Mailtro → báo người dùng, **không** ghi đè.
2. Copy bản mới sang, commit **đúng file đó** trên branch hiện tại của repo Mailtro (không kéo theo file khác đang dở).
3. Máy không có repo Mailtro → bỏ qua bước này, nhắc người dùng một dòng.

### Sau khi ghi: đưa lên GitHub

Ghi xong, rule mới **chỉ nằm trên máy local**. Chỉ commit/push khi người dùng yêu cầu; nếu không, nhắc một dòng rằng rule chưa lên GitHub.

Khi được yêu cầu:

1. Chạy 3 lệnh "Rà an toàn trước mỗi lần push" trong `knowledge-work/integrations/claude-code.md`.
2. **Submodule trước**: trong `knowledge-work/`, `git add` đúng các file vừa sửa (`business-rules/…`, `open-questions/…`), commit, `git push origin main`.
3. **Repo cha sau**: trong `skills-personal/`, `git add knowledge-work` (chỉ con trỏ submodule — không kéo theo file khác đang sửa dở như `README.md`), commit, push.
4. Nếu có sửa `MTRO.md` → đồng bộ bản copy theo mục trên.
5. Kiểm link: mọi dòng `> ❓ Chưa chốt … § "<tên>"` phải khớp đúng một heading `### <tên>` trong `open-questions/<APP_PREFIX>.md` — lệch thì sửa trước khi commit.

Message commit ghi rõ app, nhóm rule và ticket nguồn (ví dụ "Thêm business rule MTRO cho Contacts, Segments, Campaigns").

## Input cần thu thập

Không cần hỏi nếu người dùng đã cung cấp đủ; tự suy luận từ ngữ cảnh chat trước đó (ví dụ vừa chạy `qa-requirement-analysis` xong). Nếu thiếu, hỏi ngắn gọn:

- **APP_PREFIX**: app nào (TEPO / QCO / DUOS / QSC / MTRO / ...). Nếu người dùng vừa phân tích 1 issue Jira cụ thể, tự suy ra từ project key.
- **Business rule(s)**: nội dung rule — có thể là mục "3. Business Rules" vừa phân tích, rule người dùng gõ tay, hoặc câu trả lời PO/Dev cho một open question.
- **Nguồn (source)**: issue Jira liên quan (key/link), nếu có — để trace lại gốc.
- **Hành động**: thêm mới, cập nhật rule đã có, hay xoá rule (mặc định là thêm/merge nếu không nói rõ).

Người dùng chỉ đưa task QA Hub (đã có test case) mà không đưa rule: đọc bản phân tích trong `notes` của task, rồi đọc **lại** ticket Jira gốc kèm comment — comment sau ngày phân tích hay chứa quyết định mới của PO.

## Nhiệm vụ của bạn

1. Xác định `<APP_PREFIX>` và đường dẫn file đích.
2. Đọc file hiện tại nếu đã tồn tại (tool `Read`, hoặc `view` trên Claude.ai); nếu chưa, coi như danh sách rỗng. Đọc cả `open-questions/<APP_PREFIX>.md` nếu có — để không ghi trùng câu hỏi, và để biết câu hỏi nào vừa được trả lời.
3. Phân loại từng rule đầu vào:
   - **Đã xác nhận** (Jira description/AC, comment PO/Dev, người dùng khẳng định) → đi tiếp bước 4.
   - **Chưa chốt** (Assumption, GAP, `PO/DEV confirm`, hành vi build lệch AC mà chưa ai quyết) → **không** ghi thành rule. Thêm một mục vào `open-questions/<APP_PREFIX>.md` theo `templates/open-question.md` (Câu hỏi / Hỏi / Case treo / Rule liên quan), và nếu có rule liên quan thì thêm dòng `> ❓ Chưa chốt` ngay dưới rule đó.
4. So sánh từng rule đã xác nhận với rule đã có trong file:
   - **Trùng lặp / diễn đạt lại cùng 1 rule** → không thêm dòng mới, chỉ cập nhật `Nguồn` (thêm issue mới vào danh sách nguồn) và `Cập nhật lần cuối` nếu cần.
   - **Mâu thuẫn với rule đã có** (rule mới nói khác với rule cũ cho cùng 1 field/flow) → **không tự động ghi đè**. Nêu rõ mâu thuẫn cho người dùng, hỏi rule nào đúng trước khi cập nhật.
   - **Rule hoàn toàn mới** → thêm dòng mới vào đúng nhóm (section) phù hợp trong file, tạo section mới nếu chưa có nhóm nào khớp.
   - **Trả lời một open question** → ghi rule với nguồn là câu trả lời đó, **xoá** mục khỏi `open-questions/`, gỡ dòng `> ❓ Chưa chốt` tương ứng.
5. Ghi file: sửa file đã tồn tại bằng `Edit` (`str_replace` trên Claude.ai), tạo file mới bằng `Write` (`create_file` trên Claude.ai). Giữ nguyên format chuẩn ở dưới. Khi sửa file đã có, chỉ chèn/sửa đúng phần liên quan — không ghi đè toàn bộ file. Nếu đầu file có dòng mô tả phạm vi (module nào đã có rule), cập nhật dòng đó khi thêm nhóm mới.
6. Sau khi ghi xong, tóm tắt ngắn gọn cho người dùng: đã thêm bao nhiêu rule mới, cập nhật bao nhiêu, bao nhiêu điểm chuyển sang open question, phát hiện bao nhiêu mâu thuẫn cần xác nhận.

## Rào chắn AI (AI Guardrails)

- Chỉ lưu những business rule đã được xác nhận (từ Jira, comment PO/Dev, hoặc người dùng khẳng định rõ) — không lưu Assumption hay đề xuất chưa chốt.
- **Hành vi quan sát được khi chạy test không phải rule** — build đang làm gì chỉ là bằng chứng, chưa phải quyết định. Chỉ ghi khi PO/Dev đã xác nhận (ví dụ BE chốt method `PUT` → ghi được, nguồn là lần chốt đó); còn lại đưa vào open question.
- **Description Jira lệch comment PO** → theo quyết định mới nhất (thường là comment), ghi cả hai nguồn và đánh dấu "⚠ description chưa cập nhật" để người đọc ticket không bị lệch.
- Không tự bịa rule không có trong input.
- Không tự động ghi đè rule cũ khi phát hiện mâu thuẫn — luôn hỏi lại người dùng trước.
- Không xoá rule cũ trừ khi người dùng yêu cầu rõ ràng.
- Không tạo file rỗng nếu không có rule nào để ghi.
- Không bao gồm dữ liệu nhạy cảm (token, mật khẩu, dữ liệu khách hàng, shop domain của merchant thật, private key, production credentials) trong file business rule.
- Mỗi rule cần có ít nhất 1 nguồn (issue Jira, comment, hoặc "xác nhận trực tiếp bởi [tên người dùng] ngày [ngày]") — không lưu rule "trôi nổi" không rõ xuất xứ.

## Định dạng file `<APP_PREFIX>.md`

```markdown
# Business Rules — <APP_PREFIX>

> File này được duy trì bởi skill `update-business-rules`. Đọc bởi `qa-requirement-analysis` và `gen-testcase` làm ngữ cảnh nền. Không tự ý xoá thủ công — dùng skill để cập nhật.

## <Tên nhóm / module / flow>

### <Câu khẳng định ngắn, đọc là biết rule nói gì>
- **Rule**: Hành vi cụ thể, quan sát được — nêu status code, tên field, tên bảng, con số ngưỡng, text UI nguyên văn nếu có. Viết đủ để người khác không phải mở lại ticket gốc.
- **Nguồn**: <ISSUE-KEY> (link), hoặc "xác nhận trực tiếp bởi <người dùng> ngày <ngày>"
- **Cập nhật lần cuối**: YYYY-MM-DD

> ❓ **Chưa chốt** — <tóm tắt một mệnh đề>: xem [open-questions/<APP_PREFIX>.md](../open-questions/<APP_PREFIX>.md) § "<tên mục bên đó>".

### <Rule khác cùng nhóm>
...

## <Nhóm khác>
...
```

- Nhóm (`##`) theo module/flow lớn (ví dụ: "Pricing", "Token Migration", "Cart Drawer Behavior") — tự đặt tên nhóm hợp lý dựa trên nội dung rule, không cần cố định danh sách nhóm trước. Nhóm gắn với một epic/story thì ghi key vào tên nhóm hoặc một dòng `>` ngay dưới (ví dụ `## Automations — builder (MTRO-33)`).
- Mỗi rule (`###`) là 1 đơn vị kiểm thử được (atomic), không gộp nhiều rule không liên quan vào 1 mục.
- Nếu 1 rule có nhiều nguồn (được xác nhận lại ở nhiều issue), liệt kê tất cả nguồn cách nhau bằng dấu phẩy trong cùng dòng **Nguồn**.
- Dòng `> ❓ Chưa chốt` chỉ có khi rule có phần còn treo; tên sau `§` phải trùng **nguyên văn** heading bên `open-questions/`.

## Bước tiếp theo

Sau khi cập nhật xong, nhắc người dùng:
- Nếu vừa phân tích 1 issue Jira mới cho app này, có thể chạy `gen-testcase` để rule mới được dùng làm ngữ cảnh sinh test case.
- Nếu phát hiện mâu thuẫn chưa xử lý, nhắc lại để người dùng xác nhận rule đúng trước khi tiếp tục.
- Nếu có mục mới trong `open-questions/`, liệt kê câu hỏi và người cần hỏi để người dùng mang đi hỏi PO/Dev.
- Rule đang nằm local — chưa lên GitHub nếu người dùng chưa yêu cầu push (xem "Sau khi ghi: đưa lên GitHub").

---
name: context-change-request
description: "Soạn Context Change Request (CCR) theo ĐÚNG quy trình + template của leader QA (quy-trinh.md + template.md, nguyên văn) — yêu cầu cập nhật canonical QA context khi hành vi đã/sắp ship THIẾU, SAI, CŨ hoặc MÂU THUẪN với canon của app (knowledge-work/apps/<KEY>/ + knowledge trên QA Hub). Đọc ticket Jira (chỉ đọc) + test case QA Hub + canon, ghi knowledge-work/apps/<KEY>/ccr/CCR-<ngày>-<slug>.md (+ bản Anh khớp dòng + file trạng thái), chỗ cần người ghi ⏳ CHỜ BẠN. Dùng khi người dùng nói \"tạo CCR\", \"context change request\", \"cập nhật context cho ticket X\", \"ticket này KB chưa có / sai\", khi ticket đã ship mà canon chưa có, khi inventory / RA / chạy test thấy hành vi đã ship lệch business rule. Cũng xử lý \"trả lời CCR\" (điền chỗ ⏳). KHÔNG dùng để: sửa business rule (update-business-rules), build inventory (build-app-context), đính kèm / Submit CCR lên QA Hub (Hae làm sau khi người dùng duyệt — gắn bằng set_task_ccr_file, nộp bằng submit_task_ccr)."
---

Nguồn: `github.com/qikify-QA/qa-workflow` `.claude/skills/context-change-request` @ `33d081b` (2026-09-29). Mang về
2026-10-20, giữ nguyên 3 file của leader, viết lại SKILL.md cho repo `skills-personal` (không có `qa_workflow.py`,
không có web Work/Done của bản gốc).

## Luật số 1 — theo đúng template của leader

Ba file trong thư mục này là **nguyên văn** bản gốc — **không sửa, không thêm/bớt mục, không đổi câu chữ**:

- `quy-trinh.md` — "Việc này KHÔNG làm" + **Phần A — Quy trình 10 bước** (Bước 0–9). **Đọc trọn và làm theo.**
- `template.md` — **Phần B — Template CCR**. Mỗi CCR = copy file này rồi điền; giữ nguyên thứ tự + tiêu đề mọi mục.
- `template.en.md` — bản tiếng Anh **khớp từng dòng** của `template.md`. Chỉ dùng làm khung cho bản Anh; không viết CCR từ nó.

**Cách điền — luật cứng** (bản gốc từng bị viết lại / xoá 30/83 dòng khung — sự cố QA-3364):
- `cp template.md <file CCR>` rồi **chỉ thay chữ BÊN TRONG `<<< >>>`** (cả cặp dấu, và cặp backtick bao quanh nếu có).
  **Không xoá, không sửa, không viết lại bất kỳ dòng nào khác** — kể cả dòng hướng dẫn `> …`, các gạch đầu dòng luật,
  danh sách `HIGH · MEDIUM · LOW`, 2 checklist cuối, tiêu đề `# Phần B …`.
- Được phép, và chỉ những thứ này: xoá đúng dòng hướng dẫn đầu file (`> Nếu knowledge base đích …` — template dặn xoá);
  thay `<<< PRODUCT >>>` bằng tên app; tick `[ ]` → `[x]` ở checklist; thêm hàng vào bảng "Phạm vi cần re-explore"
  (mỗi claim 1 hàng, đúng 5 cột).
- Chỗ không có `<<< >>>` thì **không điền gì vào đó** (bảng Phần 0 chỉ có câu hỏi — đề xuất gộp/tách đi vào `note` của
  file trạng thái; mức gấp 4.4 cũng nằm ở file trạng thái).
- Chữ `` `<<< ... >>>` `` ở dòng 9 và dòng checklist cuối là **chữ của khung**, không phải placeholder — giữ nguyên.

Mâu thuẫn giữa SKILL.md và 3 file trên → 3 file trên thắng, trừ các quyết định ở mục cuối "Khác bản gốc".

## Công cụ máy — `scripts/ccr.py` (0 token)

`CCR="$HOME/.claude/skills/context-change-request/scripts/ccr.py"`

| Lệnh | Khi nào |
|---|---|
| `python3 "$CCR" find --tickets <K1,K2> --key <KEY>` | Trước khi tạo — exit 2 = đã có CCR đang mở (PENDING / ATTACHED) cho ticket đó → không tạo mới, sửa tiếp CCR đó |
| `python3 "$CCR" lint <CCR.md> --en <CCR.en.md>` | Sau khi ghi / sửa — phải ra ✅. Lệch → sửa đúng dòng nó chỉ, chạy lại; **không báo xong khi còn lệch** |
| `python3 "$CCR" lint … --final` | Trước khi đính kèm QA Hub — còn `⏳` cũng là lỗi |
| `python3 "$CCR" open --key <KEY> [--rules]` | Liệt kê CCR đang mở; `--rules` trả `{BR-nn: [file…]}` — rule đang tranh chấp |
| `python3 "$CCR" status <CCR.md> --set … / --urgency … / --task …` | Đổi file trạng thái (không sửa tay JSON) |
| `python3 "$CCR" hub-copy <CCR.en.md> --out <file>` | Sinh bản gửi QA Hub (xem "Khác bản gốc" #3) |

## Ở repo này — làm từng bước của quy-trinh.md bằng gì

**Bước 0 — knowledge base đích.** Không có `_registry.json` / `kb.json` / `manifest.json` / checklist JSON. Canon của
app `<KEY>` (TEPO · QSC · QCO · DUOS · MTRO) gồm, theo thứ tự tra:
1. QA Hub: `search_knowledge` (business rule, theo tên feature) + `get_project_context` item `Inventory <KEY>` (+ item module).
2. File local `~/.claude/skills/qa-requirement-analysis/references/apps/<KEY>/` (= `knowledge-work/apps/<KEY>/`):
   `business-rules.md` (`BR-nn`) · `open-questions.md` (`OQ-…`) · `inventory.md` (§ 5 "Phát hiện lệch") · `README.md` · `kb/`.
   File lớn → `Grep`, không đọc full.
3. Rule nền tảng chung: `…/references/platform/business-rules.md`.

Template ghi "không tra được registry" → làm đúng như template: mô tả bằng lời, **không bịa `object_key`**; chỗ
`KB-id/check-id` trích `BR-nn` / dòng inventory / tên knowledge QA Hub **nguyên văn**; "context version" → ghi ngày
`**Cập nhật lần cuối**` của rule / ngày build inventory, không có thì "không rõ".

**Bước 1 — input.** Ticket key/link được đưa (hoặc mô tả bằng lời). App suy từ key. Không tự tìm thêm ticket.

**Bước 2 — đọc ticket (chỉ đọc).** `getJiraIssue` từng key, **kèm toàn bộ comment** (và changelog nếu lấy được — cần cho
mốc "Dev giao QA cuối"); `getJiraIssueRemoteIssueLinks` để ghi nhận link. Tra test case trên QA Hub:
`list_tasks` của project → task có dòng `Source:` khớp key (Epic + story con = một task) → `list_test_cases` của task
**một lần**; output lớn thì `Grep` file tool-result theo từ khoá hành vi / feature, không đọc lại. Tìm cả ở task khác
(Bước 2: "đừng chỉ tìm đúng ticket key") — `Grep` tên feature trong output `list_test_cases` của các task cùng
feature, tối đa 3 task. Với mỗi case: `status`, `actualResult` (nhãn `[AI] <ngày>` hay `[QA]`), `bugId`. Case
`not-run` / `skipped` / `blocked` / chờ mắt nhìn **không bao giờ** là bằng chứng PASS. PO/Dev confirm: tra bản phân
tích trong `notes` của task — mục 11/12 GAP đã `✅` có người + ngày + nguồn (do terra chế độ cập nhật ghi).
Log manual run của sonder (MTRO: `docs/test-runs/<NN-feature>/` repo `qikify-QA-mailtro`; app khác: đường dẫn Hae đưa)
dùng để lấy ngày chạy + môi trường; không có thì ghi "không rõ".

**Bước 3 — tra canon.** Theo thứ tự Bước 0; ghi đúng từ khoá + nơi đã tra. Có CCR khác đang mở chạm cùng rule
(`ccr.py open --key <KEY> --rules`) → nêu ở "Canon hiện nói": "(đang có CCR mở: <file>)".

**Bước 4–6** — đúng như quy-trinh.md, cộng các luật ở mục "Luật điền nội dung" dưới.

**Bước 7 — xác nhận `[BẠN]`.** Lượt chạy không hỏi-đáp được người dùng → chỗ `<<< >>>` cần người mà chưa có câu trả lời
→ điền `⏳ CHỜ BẠN: <câu hỏi cụ thể>` (đúng chỗ trống, không thêm mục). **Luôn có ít nhất**: `⏳` ở 4.1 ("có PO/business
xác nhận ngoài Jira không?") và ở "Thử gì mà KHÔNG tái hiện" (phần `[BẠN]`: "chị đã tự thử gì mà QA Hub / log không
ghi?"). Báo cáo cuối liệt kê đủ câu hỏi Bước 7: Phần 0 (đề xuất gộp/tách), 4.1, **4.4 mức gấp** (đề xuất kèm lý do),
các chỗ "không rõ", dòng CHƯA ĐỦ mà người dùng có thể nghĩ đã xác nhận.

**Bước 8** — đúng như quy-trinh.md. File nằm trong repo knowledge-work (submodule chung của team) **và** sẽ lên QA Hub
→ redact là bắt buộc (email, SĐT, tên shop / khách thật, token, URL có token).

**Bước 9 — ghi file.** Trong `~/.claude/skills/qa-requirement-analysis/references/apps/<KEY>/ccr/` (tạo thư mục nếu chưa có):
- `CCR-<YYYY-MM-DD>-<slug>.md` — bản Việt (`<slug>` = kebab-case ASCII không dấu, vd `reposition-toggle`).
- `CCR-<…>.en.md` — bản Anh: dòng khung lấy **thẳng** từ `template.en.md` cùng số dòng; chỉ dịch phần đã điền, giữ
  nguyên key Jira, `BR-nn`, TC id, tên UI, trích dẫn (trích dẫn tiếng Việt giữ nguyên văn + dịch trong ngoặc ngay sau,
  cùng dòng). **Khớp từng dòng** với bản Việt — `lint --en` kiểm.
- `CCR-<…>.status.json`:
  `{"status": "PENDING", "urgency": null, "urgency_proposed": "<HIGH|MEDIUM|LOW>", "note": "<đề xuất Phần 0 + lý do>",
  "created_at": "<ISO>", "tickets": [...], "taskId": "<task QA Hub hoặc null>", "rules": ["BR-nn", ...]}`
  — `rules` = mọi `BR-nn` / `OQ-…` CCR nhắc tới ở "Canon hiện nói". File CCR giữ **đúng template**; mọi thứ máy cần nằm
  ở file trạng thái.

Trước khi ghi: `ccr.py find` chống trùng (exit 2 → không tạo mới, báo đường dẫn CCR đó để sửa tiếp — trừ khi được bảo
tạo CCR thứ hai / tách theo Phần 0, khi đó ghi lý do tách vào `note`). Ghi xong: `lint --en` phải ✅. **Không commit,
không push** — người dùng tự commit submodule knowledge-work.

Báo cáo cuối: số CCR, mỗi CCR một dòng (loại request · object/feature · số claim · số dòng CHƯA ĐỦ / ĐỦ), đường dẫn 3
file, danh sách câu ⏳, mức gấp đề xuất, và mọi CCR đang mở của app (`ccr.py open --key <KEY>`). Bước tiếp theo nói
đúng: *"trả lời các chỗ ⏳ → Hae đính kèm bản Anh vào task QA Hub rồi Submit (sau khi người dùng duyệt)"* — không nói
"đã gửi".

## Chế độ trả lời (điền chỗ ⏳)

Đầu vào: đường dẫn CCR + nguyên văn câu trả lời của người dùng. Sửa **đúng** chỗ `⏳` tương ứng ở cả bản Việt và bản Anh
(mức gấp → `ccr.py status --urgency`; đồng ý / đổi Phần 0 → `--note`). Người dùng khẳng định "đã xác nhận rồi" cho một
dòng CHƯA ĐỦ → **không tự nâng** thành ĐỦ TIN CẬY (Bước 7): cần TC id PASS + ngày + môi trường, hoặc quote + link PO/Dev;
không có thì giữ CHƯA ĐỦ và ghi lại câu hỏi. Xong chạy `lint --en`, báo còn bao nhiêu `⏳`.

## Luật điền nội dung (bổ sung cho quy-trinh.md, rút từ bản gốc)

- **CCR sau khi ticket đã ship / pass**: trọng tâm = **mục đích chính của ticket** (summary) — thường `NEW_FEATURE` hoặc
  `BEHAVIOR_CHANGE`. Tiêu đề, slug nói đúng mục đích này. Phát hiện phụ (lỗi có sẵn, câu hỏi còn mở, mâu thuẫn với canon
  ngoài phạm vi) **không thay** CCR chính: đáng thì tách CCR riêng theo Phần 0 (lý do vào `note`), không thì ghi ở 4.2 /
  một dòng bảng.
- **"Quan sát được" = TOÀN BỘ thay đổi ticket đã làm**, mỗi nguồn ghi rõ: (1) description + comment Dev dạng "Context" /
  "Behaviour changes" / "Test cases"; (2) bản phân tích trong `notes` task QA Hub: requirement + BR đã xác nhận + GAP đã
  đóng; (3) bug của task đã retest VERIFIED (case có `bugId` đã `passed`) — hành vi SAU fix là hành vi đã ship;
  (4) § 5 inventory nhắc tới feature. Liệt kê giá trị hợp lệ / biên / lỗi, phạm vi áp dụng, cái KHÔNG đổi.
- **Bảng "Phạm vi cần re-explore"**: mỗi thay đổi = 1 dòng.
- **Cột "Độ tin cậy" = ĐÚNG 1 trong 3 dạng, không thêm chữ**:
  `ĐỦ TIN CẬY (test case PASS #<TC-id> <ngày> <env> [AI|QA]; … — build: <mốc>)` ·
  `ĐỦ TIN CẬY (PO/Dev confirm: "<quote>" — <link>)` · `CHƯA ĐỦ — cần re-explore`.
  Giải thích (TC nào skip, thiếu gì) để ở cột "Vì sao chưa thể tin ngay". `lint` kiểm dạng này.
- **TC PASS chỉ được ghi ĐỦ TIN CẬY khi đủ cả 4**: kiểm đúng hành vi đang claim · có ngày chạy của TỪNG TC + môi trường ·
  chạy **SAU** lần Dev giao QA cuối và sau fix bug cuối liên quan · ghi build theo dòng dưới. Thiếu một → CHƯA ĐỦ.
  `[AI]` PASS vẫn tính, luôn ghi nguồn `[AI]` / `[QA]`.
- **"Build" khi QA không có quyền repo**: `<staging|production> @ <YYYY-MM-DD> — sau lần <KEY> giao QA cuối (<ngày>)
  [; Fix Version <v>][; release <ngày>]; build hash: không rõ (QA không có quyền repo)`. Mốc lấy từ Jira (status
  changelog, `fixVersions`). Không có thì "không rõ", **không bịa**.
- **"Đã xác nhận" trong RA ≠ PO/business sign-off.** RA có thể ghi rule đã xác nhận khi nguồn chỉ là mô tả / comment Dev
  — template coi đó KHÔNG phải xác nhận. 4.1 và dạng `ĐỦ TIN CẬY (PO/Dev confirm …)` chỉ tính câu trả lời của
  **PO/business** có người + ngày + link, trích nguyên văn.
- **"Canon hiện nói" = trích NGUYÊN VĂN**, không cắt bằng "…"; dài → trích đủ dòng liên quan, nối bằng ` ▸ `.
- **Phần 0 vẫn áp cho CCR chính**: lệch câu nào (vd phần cần PO quyết lẫn phần tự explore được) → tách CCR.

## CCR đang mở = canon "đang tranh chấp"

Rule mà một CCR `PENDING` / `ATTACHED` nhắc tới chưa chắc còn đúng. `ccr.py open --key <KEY> --rules` (hoặc `Grep`
`"BR-nn"` trong `apps/<KEY>/ccr/*.status.json` có `"status": "PENDING"|"ATTACHED"`). terra / ore / flint coi rule đó như
rule đang lệch theo § 5 inventory: ghi rõ "(đang có CCR mở: <file>)", không coi là đã chốt.

## Khác bản gốc — các chỗ đã quyết cho repo này

1. **Không web Work/Done, không `qa_workflow.py`.** Mọi bước máy = `scripts/ccr.py`. Lượt chạy bất đồng bộ như bản gốc:
   chỗ cần người = `⏳ CHỜ BẠN`, trả lời sau qua chế độ trả lời.
2. **"Đính kèm vào task" = MCP `set_task_ccr_file`, do Hae gọi sau khi người dùng duyệt** (bản gốc: người gửi tự đính kèm).
   Skill / sub-agent soạn CCR **không** có tool này. Điều kiện: `lint --en --final` ✅ + có `urgency` + có `taskId`.
   Trước khi gắn: `get_task_ccr` — `ccrStatus: submitted` → task đã nộp CCR (mỗi task chỉ một lần) → không gắn được, báo
   người dùng; đã có draft khác → không ghi đè khi chưa được bảo. Gắn xong → `status --set ATTACHED`.
   **Submit = MCP `submit_task_ccr`, cũng do Hae gọi, cùng lần duyệt đó** (bản gốc: người gửi tự bấm Submit; leader QA chốt
   2026-11-02 cho submit qua MCP). Nộp xong → `status --set SUBMITTED`. QA Hub chưa có tool → người dùng bấm Submit tay.
   Skill / sub-agent soạn CCR vẫn không Submit, không `create_proposal`. Thấy `ccrStatus: submitted` ở lần
   kiểm sau → `status --set SUBMITTED`. Bỏ CCR → `status --set DROPPED --reason …` (không gỡ file trên QA Hub).
3. **Bản gửi QA Hub = bản Anh qua `hub-copy`.** QA Hub từ chối Submit khi còn chuỗi `<<<`, mà dòng 9 và dòng checklist
   cuối của template có sẵn chữ `` `<<< ... >>>` ``. `hub-copy` chỉ đổi đúng 2 dòng đó sang `` `‹‹‹ ... ›››` `` trong
   **bản gửi**; file CCR trong repo giữ nguyên văn. (Chờ leader xác nhận cách này.)
4. **Song ngữ, QA Hub nhận bản Anh** (theo bản gốc: leader đọc tiếng Anh). Người dùng đọc / sửa bản Việt; bản Anh do
   agent dịch khớp dòng, sửa bản Việt thì dịch lại đúng dòng đó.
5. **Đề xuất Phần 0 + mức gấp 4.4 nằm ở `.status.json`** — file CCR không thêm mục / field nào.
6. **Không commit / push** — knowledge-work là submodule chung; người dùng tự commit.

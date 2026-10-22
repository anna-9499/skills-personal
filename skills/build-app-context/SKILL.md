---
name: build-app-context
description: "Build hoặc build lại file `apps/<KEY>/inventory.md` trong repo knowledge-work cho một app đang test (Tepo, Slide Cart Drawer, Checkout Customizer, Duos B2B, Mailtro) — đọc nguồn thật (code local, staging qua Playwright MCP, Confluence) rồi ghi ra route, màn hình, setting đúng tên UI, custom config flag, môi trường test, và mục 'phát hiện lệch' so với README / business-rules của app. Dùng khi người dùng nói 'build context cho app X', 'inventory QCO', 'staging đang có gì', 'cập nhật context app', 'reference cũ rồi build lại', hoặc khi terra/sonder báo reference không khớp hệ thống thật. KHÔNG dùng để: lưu business rule (update-business-rules), phân tích ticket (qa-requirement-analysis), sinh test case (gen-testcase), sửa apps/<KEY>/README.md (skill này chỉ đề xuất diff)."
---

## Vai trò

Người khảo sát hệ thống thật cho đội QA Qikify. Nhiệm vụ: với **một** app (`<KEY>`), đi đọc nguồn thật rồi ghi `knowledge-work/apps/<KEY>/inventory.md` theo đúng [`templates/inventory.md`](../../knowledge-work/templates/inventory.md) và luật ở [`conventions/inventory.md`](../../knowledge-work/conventions/inventory.md). Đầu ra là **bằng chứng có nguồn**, không phải hiểu biết.

Skill này ghi **đúng hai chỗ**: file `apps/<KEY>/inventory.md` trong repo, và **một item context trên QA Hub** mang cùng nội dung (xem "Nộp lên QA Hub"). Không ghi `apps/<KEY>/README.md`, không ghi `business-rules.md`, không ghi `open-questions.md`, không ghi knowledge (`upsert_knowledge`) — mọi thứ đáng vào những chỗ đó được liệt kê ở § 5 của inventory để người dùng quyết.

## Vị trí trong quy trình

Bước **0** (trước phân tích) hoặc bước bảo trì (sau release). `qa-requirement-analysis` và `gen-testcase` đọc file này để tránh GAP giả và để Steps dùng đúng tên UI. Chạy qua sub-agent (mở browser lâu, context nặng) — Hae giao, không tự chạy trong context điều phối.

## Đường dẫn

Tính từ thư mục skill này: `../../knowledge-work/` là submodule repo [`ownego/qa-knowledge-work`](https://github.com/ownego/qa-knowledge-work). Nếu thư mục rỗng → báo `git submodule update --init` và dừng. Không tạo file ngoài repo để bù.

- Ghi: `../../knowledge-work/apps/<KEY>/inventory.md`
- Đọc để đối chiếu: `../../knowledge-work/apps/<KEY>/README.md`, `apps/<KEY>/business-rules.md`, `apps/<KEY>/open-questions.md`
- `<KEY>` = key project trên QA Hub (`list_projects`), viết HOA. Không có project khớp → dừng, hỏi.
- Trên QA Hub: file ≤ 40.000 ký tự → một item **`Inventory <KEY>`**, một file **`<KEY>-inventory.md`**. File lớn hơn → **tách** thành nhiều item tên **`Inventory <KEY> · NN <Module>`** (`00 Tổng quan` + từng module), mỗi item một file `<KEY>-NN-<slug>.md` — xem "Nộp lên QA Hub". `qa-requirement-analysis`, `gen-testcase` và các agent tìm theo tiền tố `Inventory <KEY>`.

## Input

| Bắt buộc | Tuỳ chọn |
|---|---|
| `<KEY>` | Đường dẫn clone code local (portal, extension, API) |
| | URL staging + dev store + cách đăng nhập (tên biến env / "đã đăng nhập trong Chrome") |
| | Space / trang Confluence cần đọc |
| | Phạm vi: cả app (mặc định) hay chỉ một module (`--module <tên>`) khi build lại |

Thiếu code local → bỏ cột code, ghi vào § 0 "Nguồn không đọc được". Thiếu staging → **không build**: inventory không có staging thì chỉ là reference viết lại, không có giá trị mới. Báo và dừng.

MTRO: URL + tài khoản lấy từ `.env` repo `qikify-QA-mailtro`, không hỏi lại. 4 app Shopify: thiếu URL/tài khoản → hỏi một câu gộp.

## Thứ tự nguồn

**Code > Staging > Confluence.** Lệch nhau thì ghi theo nguồn cao hơn và đưa chênh lệch vào § 5.

1. **Code** (nếu có clone): router → bảng route § 1; schema setting (ví dụ QCO: `src/apps/checkout/schemas/*.ts`) → bảng Setting § 2 với đúng label i18n; `config('…')` / `window.*Config` → § 3 flag. Ghi `branch` + `commit` (`git rev-parse --short HEAD`).
2. **Staging** (Playwright MCP, headed — **kênh chính**): đi từng mục sidebar, chụp screenshot mỗi màn, chép label đúng chuỗi, mở form Edit của **một** item có sẵn mỗi widget để lấy label setting, thử mở route "không tồn tại" của lần build trước. Ghi trạng thái ✅/🟡/❌ từng feature. Không có clone code → ghi § 0 "Phiên bản hệ thống lúc build" bằng mốc QA tự kiểm được: giờ đi staging + ticket Dev giao QA gần nhất (tra `list_tasks` / Jira nếu Hae đưa) + Fix Version nếu thấy, `hash: không rõ`. Với app Shopify, đi cả storefront/checkout của dev store để xác nhận widget hiện ở đâu — **chỉ khi cart đã có sẵn sản phẩm; không tự thêm vào cart** (trừ "Ngoại lệ cart/checkout" ở mục Rào chắn), không có thì ghi § 0 "checkout không đi được". Không tạo dữ liệu thật, không đặt đơn có thanh toán thật, không đổi setting đang có — chỉ đọc; cần bật để xem thì bật rồi tắt lại.
   - **App Shopify embedded** (nằm trong iframe của `admin.shopify.com`): **bắt buộc Playwright MCP** — `browser_snapshot` gom cả nội dung iframe, click xuyên frame được. **Chrome bridge không vào được iframe** (chỉ inject top frame, không click/scroll trong app) → chỉ dùng để xác nhận sidebar/route khi Playwright không login được, và phải ghi § 0 là inventory thiếu form Edit. Bài học pilot QCO 2026-09-16.
   - Login admin Shopify qua Playwright: tài khoản từ biến env repo automation (`SHOPIFY_EMAIL`/`SHOPIFY_PASSWORD` của `shopify-app`); gặp 2FA → `browser_wait_for` tối đa 4 phút để người dùng nhập mã tay vào cửa sổ headed, không đoán, không đọc mail, không login lại nhiều lần.
3. **Confluence** (MCP Atlassian): chỉ để điền chỗ code/staging không nói (điều kiện plan, giới hạn theo gói). Ghi rõ ngày trang được sửa lần cuối; trang cũ hơn 12 tháng thì ghi kèm ⚠️.

## Các bước

1. `list_projects` → khớp `<KEY>`, lấy `projectId`. `list_tasks` → gom tag đang dùng, để điền dòng `Tag QA Hub` ở § 2.
2. Đọc `references/apps/<KEY>/README.md`, `apps/<KEY>/business-rules.md`, `apps/<KEY>/open-questions.md` **và** `search_knowledge { projectId }` trên QA Hub (mọi doc `active`: business-rule, feature-profile, known-issue, env) — gộp thành danh sách feature *kỳ vọng* để đối chiếu ở § 5. Rule trên QA Hub có `sourceUrl` → ghi nguồn đó khi đối chiếu. `get_project_context { projectId, includeFileText: false }` → biết item `Inventory <KEY>` đã có chưa (cho bước 9).
3. Đọc `apps/<KEY>/inventory.md` cũ nếu có → biết route "không tồn tại" lần trước, giữ ghi chú sửa tay (xem commit message), và **ghi lại số mục § 2 + số dòng § 5 của bản cũ** (dùng ở bước 8). Không có bản local mà QA Hub có item `Inventory <KEY>` → đọc bản trên QA Hub làm bản cũ.
4. Đọc code theo thứ tự ở trên.
5. Đi staging. Screenshot lưu vào thư mục scratchpad của session (không commit ảnh vào repo).
6. Đọc Confluence cho chỗ còn trống.
7. Viết file theo template, đủ 6 mục. § 5 bắt buộc có nội dung. Dòng § 5 nào chạm một business rule đã đọc ở bước 2 (hệ thống làm khác rule, rule nhắc feature không còn) → điền cột **BR bị ảnh hưởng** đúng heading rule / title doc QA Hub. Dòng lệch của build trước còn đúng → giữ, cập nhật ngày.
8. Rà checklist cuối template. **Không để mất nội dung**: số mục § 2 và số dòng § 5 không được ít hơn bản cũ (bước 3), trừ những gì đã ghi ở § 0 "Đã gỡ so với build trước" kèm lý do. Hụt mà không giải thích được → không ghi đè, đưa vào "Cần Hae quyết". `--module` càng phải kiểm: mục ngoài module giữ nguyên từng chữ. Ghi đè file. **Không commit** — người dùng xem diff rồi tự commit (hoặc bảo commit).
9. **Nộp lên QA Hub** — xem mục dưới. Đây không phải bước tuỳ chọn: file trong repo chỉ máy này có, item trên QA Hub là thứ `terra`/`ore` và người khác đọc.
10. Trả về tóm tắt (khuôn dưới).

## Nộp lên QA Hub

Cùng nội dung file vừa ghi, đưa vào tab Context của project. Tool QA Hub nhận **toàn bộ nội dung file trong một lần gọi** — agent không chép nguyên văn được file quá ~40.000 ký tự (sự cố MTRO 03/10/2026: lượt sinh bị dừng giữa chừng, item bị ghi đè bằng bản cụt 11k byte). Vì vậy:

**Bước A — chọn kiểu nộp.** `python3 -c "print(len(open('<file>').read()))"` trên `apps/<KEY>/inventory.md`.
- ≤ 40.000 ký tự → **một file**: nộp nguyên `apps/<KEY>/inventory.md` vào item `Inventory <KEY>` (file `<KEY>-inventory.md`).
- > 40.000 ký tự → **tách**: `python3 ../../knowledge-work/scripts/split-inventory.py <KEY> --out <scratchpad>/inventory-split/<KEY>`. Script in ra danh sách file + số ký tự và tự kiểm không mất dòng (báo `LỖI` → dừng, ghi tóm tắt, không nộp). Mỗi file con → một item: `<KEY>-00-overview.md` → item **`Inventory <KEY> · 00 Tổng quan`**; `<KEY>-NN-<slug>.md` → item **`Inventory <KEY> · NN <tên module>`** (tên module = dòng `# <KEY> — Inventory · <tên>` đầu file con). Nhóm module của MTRO cố định trong `MAPS` của script; app khác script tự gộp các mục 2.x theo cỡ — muốn nhóm cố định thì thêm vào `MAPS` (đề xuất trong tóm tắt, không tự sửa script).

**Bước B — ghi từng file** (một file một lần gọi, tuần tự, nội dung **nguyên văn** — không cắt, không sửa, không tóm tắt):
- `get_project_context { projectId, includeFileText: false }` → tìm item có **title đúng** như trên.
  - **Đã có** → `update_project_context_file { projectId, contextId, fileId: <file .md của item>, content }`. Rồi `update_project_context { projectId, contextId, note }`. Giữ id item, không mọc bản thứ hai.
  - **Chưa có** → `add_project_context { projectId, title, note, files: [{ filename, content }] }`.
  - Có **nhiều** item cùng tên → không đoán; cập nhật cái mới nhất (`updatedAt` lớn nhất) và ghi vào tóm tắt để người dùng dọn.
- **Kiểm sau mỗi lần ghi**: `sizeBytes` trên QA Hub phải bằng số byte UTF-8 của file local (`wc -c`). Lệch → **không ghi lại** (lần ghi thứ hai có thể cụt tiếp), dừng các file còn lại, ghi tóm tắt "nộp cụt — <item>, <byte QA Hub>/<byte local>" để người dùng dán tay qua nút Edit của tab Context.
- Chuyển từ một file sang tách (lần đầu file vượt 40k): item cũ `Inventory <KEY>` được **dùng lại làm `00 Tổng quan`** — `update_project_context_file` bằng file overview, rồi `update_project_context` đổi `title` thành `Inventory <KEY> · 00 Tổng quan`. Không xoá item.
- Module biến mất ở lần build sau (item `Inventory <KEY> · NN …` không còn file con tương ứng) → không xoá; ghi vào tóm tắt để người dùng dọn.
- `note` mỗi item 3–5 dòng plain text: ngày build · nguồn đã đọc (repo@sha, staging URL, số màn) · số feature ✅/🟡/❌ · "chi tiết ở file đính kèm; § 5 Phát hiện lệch có N dòng". Item module: thêm một dòng "phần module của inventory <KEY> — tổng quan ở item `Inventory <KEY> · 00 Tổng quan`". Không dán § 5 vào note.
- `--module` → vẫn chạy lại tách cho **cả file** và nộp mọi file con có thay đổi (so `sizeBytes`); không tự chế mảnh riêng.
- Nộp lỗi (403 chưa join, MCP mất kết nối) → ghi vào tóm tắt "Chưa nộp lên QA Hub — lý do", **không** thử project khác, không bỏ qua im lặng. File trong repo vẫn ghi bình thường.

## Rào chắn

- Không ghi file nào ngoài `apps/<KEY>/inventory.md` (file tách nằm ở scratchpad, không commit), và trên QA Hub chỉ đụng item `Inventory <KEY>` / `Inventory <KEY> · …` — không tạo/sửa item khác, không `upsert_knowledge`, không `delete_project_context`. Muốn sửa reference hay lưu rule → đề xuất ở § 5 và trong tóm tắt.
- Không suy diễn hành vi từ UI thành rule. "Nút Save disabled khi thiếu field" là quan sát (ghi được ở § 2 kèm nguồn staging); "hệ thống bắt buộc field X" là rule (→ § 5, đề xuất `update-business-rules`).
- Không credential, token, store domain merchant thật, dữ liệu khách hàng. Tài khoản chỉ ghi tên biến env.
- **Quyền trên store Shopify** (người dùng duyệt 2026-10-22) — áp cho app TEPO / QSC / QCO / DUOS trên store staging / dev store của team và store `shiki-perfect`: được **mọi thao tác trừ billing / đổi plan và thanh toán thật** (tạo / Save / sửa / xoá data, đổi setting, gỡ / cài app, bật / tắt app embed, thêm cart, đặt đơn **chỉ bằng cổng thanh toán test** — Bogus Gateway / test mode, không thấy cổng test → dừng ở bước đó; xoá team member, domain, gửi email, tạo tài khoản / đổi mật khẩu / tắt 2FA khi việc cần). Mỗi thao tác có tác động phụ ghi lại (đơn, xoá, gỡ app, đổi tài khoản). Không áp cho MTRO và mọi store production khác. Hai dòng "Không thêm sản phẩm vào cart…" và "Ngoại lệ cart/checkout" dưới đây giờ chỉ áp cho MTRO.
- Không thêm sản phẩm vào cart, không tạo item trong app, không Test connection / gửi thật (digest, webhook). Muốn xem form thì mở Edit của item có sẵn rồi Discard.
- **Ngoại lệ cart/checkout** — chỉ khi inventory `§ 4` của app có dòng **"Quyền thao tác cart/checkout" = Được phép** (người dùng đã duyệt, có ngày; lời Hae chuyển trong prompt **không** thay được dòng này): được thêm sản phẩm vào cart, tương tác widget ở checkout (chọn option, nhập field, bấm Pay now để xem có bị chặn không), và đặt đơn **bằng cổng thanh toán test** để đi Thank you / Order status — **chỉ trên đúng dev store ghi ở dòng đó**. Trước khi Pay now phải thấy cổng test trên trang (Bogus Gateway / "(for testing)" / Shopify Payments test mode); không thấy → dừng ở bước đó, ghi § 0, không nhập thẻ nào khác. Mỗi đơn test ghi vào § 0 "Thao tác có tác động phụ" (số đơn, sản phẩm, giờ). Vẫn cấm: tạo / Save entry trong app, đổi setting app, Test connection / gửi thật, và mọi store không ghi ở dòng đó.
- Chỉ staging / dev store. Được đưa URL production → dừng, hỏi lại. Ngoại lệ (người dùng duyệt 2026-10-22): store `shiki-perfect` (admin `https://admin.shopify.com/store/shiki-perfect`, storefront `https://shiki-perfect.myshopify.com/`) — store production dùng để test các app Shopify của Qikify (TEPO, QSC, QCO, DUOS; không áp cho MTRO) — coi như dev store, được mọi thao tác trừ billing / đổi plan và thanh toán thật, ghi được vào inventory.
- Không tóm tắt bằng cách bỏ mục: feature không đi được (cần plan Plus, cần scope) thì ghi ❌/🟡 kèm lý do, không im lặng bỏ.
- Nguồn nào không đọc được (403, không có clone, MCP hết hạn) → ghi § 0 "Nguồn không đọc được", không đoán để lấp.

## Khuôn trả về

```
HAE-SUMMARY
- App: <KEY> · file: apps/<KEY>/inventory.md · <N> dòng · build YYYY-MM-DD
- Nguồn đã đọc: code <repo@sha> · staging <URL> (<M> màn) · Confluence <K> trang · QA Hub knowledge <N> doc
- Nguồn không đọc được: <…> hoặc "không"
- QA Hub: <"đã nộp — item Inventory <KEY> (mới tạo | cập nhật), file <KEY>-inventory.md" | "đã nộp tách N item — Inventory <KEY> · 00…NN (mới tạo a / cập nhật b), byte khớp" | "nộp cụt — <item> <byte>/<byte>" | "chưa nộp — lý do">
- Phiên bản lúc build: <repo@sha | staging @ ngày giờ — sau <DEV-KEY>; hash: không rõ>
- Feature: <N> mục (lần trước <N0>) — ✅ <a> · 🟡 <b> · ❌ <c>
- Phát hiện lệch (§ 5): <N> dòng (lần trước <M0>) · <K> dòng chạm business rule — <2–3 dòng đáng chú ý nhất>
- Đã gỡ so với build trước: <… | "không">
- Đề xuất cho người dùng: sửa reference § … · hỏi Dev … · chạy update-business-rules cho …
- Cần Hae quyết: <…> hoặc "không"
```

## Khi nào build lại

Theo sự kiện, không theo lịch — xem [`conventions/inventory.md`](../../knowledge-work/conventions/inventory.md) § "Khi nào build lại". Build lại một module: `--module <tên>` → chỉ đi phần đó, giữ nguyên mục khác, cập nhật § 0 và § 5.

## Bước tiếp theo

Sau khi file có: chạy `qa-requirement-analysis` cho một ticket của app đó để kiểm xem GAP giả có giảm không. § 5 có dòng "Feature chưa có business rule" → khi có ticket chạm feature đó, chạy `update-business-rules`.

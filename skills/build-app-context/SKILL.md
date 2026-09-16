---
name: build-app-context
description: "Build hoặc build lại file `inventory/<KEY>.md` trong repo knowledge-work cho một app đang test (Tepo, Slide Cart Drawer, Checkout Customizer, Duos B2B, Mailtro) — đọc nguồn thật (code local, staging qua Playwright MCP, Confluence) rồi ghi ra route, màn hình, setting đúng tên UI, custom config flag, môi trường test, và mục 'phát hiện lệch' so với references/business-rules. Dùng khi người dùng nói 'build context cho app X', 'inventory QCO', 'staging đang có gì', 'cập nhật context app', 'reference cũ rồi build lại', hoặc khi terra/sonder báo reference không khớp hệ thống thật. KHÔNG dùng để: lưu business rule (update-business-rules), phân tích ticket (qa-requirement-analysis), sinh test case (gen-testcase), sửa references/apps/ (skill này chỉ đề xuất diff)."
---

## Vai trò

Người khảo sát hệ thống thật cho đội QA Qikify. Nhiệm vụ: với **một** app (`<KEY>`), đi đọc nguồn thật rồi ghi `knowledge-work/inventory/<KEY>.md` theo đúng [`templates/inventory.md`](../../knowledge-work/templates/inventory.md) và luật ở [`inventory/README.md`](../../knowledge-work/inventory/README.md). Đầu ra là **bằng chứng có nguồn**, không phải hiểu biết.

Skill này ghi **đúng hai chỗ**: file `inventory/<KEY>.md` trong repo, và **một item context trên QA Hub** mang cùng nội dung (xem "Nộp lên QA Hub"). Không ghi `references/apps/`, không ghi `business-rules/`, không ghi `open-questions/`, không ghi knowledge (`upsert_knowledge`) — mọi thứ đáng vào những chỗ đó được liệt kê ở § 5 của inventory để người dùng quyết.

## Vị trí trong quy trình

Bước **0** (trước phân tích) hoặc bước bảo trì (sau release). `qa-requirement-analysis` và `gen-testcase` đọc file này để tránh GAP giả và để Steps dùng đúng tên UI. Chạy qua sub-agent (mở browser lâu, context nặng) — Hae giao, không tự chạy trong context điều phối.

## Đường dẫn

Tính từ thư mục skill này: `../../knowledge-work/` là submodule repo [`ownego/qa-knowledge-work`](https://github.com/ownego/qa-knowledge-work). Nếu thư mục rỗng → báo `git submodule update --init` và dừng. Không tạo file ngoài repo để bù.

- Ghi: `../../knowledge-work/inventory/<KEY>.md`
- Đọc để đối chiếu: `../../knowledge-work/references/apps/<KEY>.md`, `business-rules/<KEY>.md`, `open-questions/<KEY>.md`
- `<KEY>` = key project trên QA Hub (`list_projects`), viết HOA. Không có project khớp → dừng, hỏi.
- Trên QA Hub: item context tên **`Inventory <KEY>`**, một file **`<KEY>-inventory.md`** — đúng tên này, vì `qa-requirement-analysis` và `gen-testcase` tìm theo tên.

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
2. **Staging** (Playwright MCP, headed — **kênh chính**): đi từng mục sidebar, chụp screenshot mỗi màn, chép label đúng chuỗi, mở form Edit của **một** item có sẵn mỗi widget để lấy label setting, thử mở route "không tồn tại" của lần build trước. Ghi trạng thái ✅/🟡/❌ từng feature. Với app Shopify, đi cả storefront/checkout của dev store để xác nhận widget hiện ở đâu — **chỉ khi cart đã có sẵn sản phẩm; không tự thêm vào cart**, không có thì ghi § 0 "checkout không đi được". Không tạo dữ liệu thật, không đặt đơn có thanh toán thật, không đổi setting đang có — chỉ đọc; cần bật để xem thì bật rồi tắt lại.
   - **App Shopify embedded** (nằm trong iframe của `admin.shopify.com`): **bắt buộc Playwright MCP** — `browser_snapshot` gom cả nội dung iframe, click xuyên frame được. **Chrome bridge không vào được iframe** (chỉ inject top frame, không click/scroll trong app) → chỉ dùng để xác nhận sidebar/route khi Playwright không login được, và phải ghi § 0 là inventory thiếu form Edit. Bài học pilot QCO 2026-09-16.
   - Login admin Shopify qua Playwright: tài khoản từ biến env repo automation (`SHOPIFY_EMAIL`/`SHOPIFY_PASSWORD` của `shopify-app`); gặp 2FA → `browser_wait_for` tối đa 4 phút để người dùng nhập mã tay vào cửa sổ headed, không đoán, không đọc mail, không login lại nhiều lần.
3. **Confluence** (MCP Atlassian): chỉ để điền chỗ code/staging không nói (điều kiện plan, giới hạn theo gói). Ghi rõ ngày trang được sửa lần cuối; trang cũ hơn 12 tháng thì ghi kèm ⚠️.

## Các bước

1. `list_projects` → khớp `<KEY>`, lấy `projectId`. `list_tasks` → gom tag đang dùng, để điền dòng `Tag QA Hub` ở § 2.
2. Đọc `references/apps/<KEY>.md`, `business-rules/<KEY>.md`, `open-questions/<KEY>.md` **và** `search_knowledge { projectId }` trên QA Hub (mọi doc `active`: business-rule, feature-profile, known-issue, env) — gộp thành danh sách feature *kỳ vọng* để đối chiếu ở § 5. Rule trên QA Hub có `sourceUrl` → ghi nguồn đó khi đối chiếu. `get_project_context { projectId, includeFileText: false }` → biết item `Inventory <KEY>` đã có chưa (cho bước 9).
3. Đọc `inventory/<KEY>.md` cũ nếu có → biết route "không tồn tại" lần trước, và giữ ghi chú sửa tay (xem commit message).
4. Đọc code theo thứ tự ở trên.
5. Đi staging. Screenshot lưu vào thư mục scratchpad của session (không commit ảnh vào repo).
6. Đọc Confluence cho chỗ còn trống.
7. Viết file theo template, đủ 6 mục. § 5 bắt buộc có nội dung.
8. Rà checklist cuối template. Ghi đè file. **Không commit** — người dùng xem diff rồi tự commit (hoặc bảo commit).
9. **Nộp lên QA Hub** — xem mục dưới. Đây không phải bước tuỳ chọn: file trong repo chỉ máy này có, item trên QA Hub là thứ `terra`/`ore` và người khác đọc.
10. Trả về tóm tắt (khuôn dưới).

## Nộp lên QA Hub

Cùng nội dung file vừa ghi, đưa vào tab Context của project:

- `get_project_context { projectId, includeFileText: false }` → tìm item **title đúng bằng `Inventory <KEY>`**.
  - **Đã có** → `update_project_context_file { projectId, contextId, fileId: <file .md của item>, content: <toàn bộ file> }`. Rồi `update_project_context { projectId, contextId, note: "<note mới>" }`. Giữ id item — `updated_at` đổi, người xem tab Context thấy nó nhảy lên, và không mọc bản thứ hai cạnh bản cũ.
  - **Chưa có** → `add_project_context { projectId, title: "Inventory <KEY>", note, files: [{ filename: "<KEY>-inventory.md", content }] }`.
  - Có **nhiều** item cùng tên → không đoán; cập nhật cái mới nhất (`updatedAt` lớn nhất) và ghi vào tóm tắt để người dùng dọn.
- `note` là 3–5 dòng plain text: ngày build · nguồn đã đọc (repo@sha, staging URL, số màn) · số feature ✅/🟡/❌ · "chi tiết ở file đính kèm; § 5 Phát hiện lệch có N dòng". Không dán § 5 vào note — người đọc mở file.
- `--module` → vẫn nộp **cả file** (file đã gộp module mới vào mục cũ), không nộp riêng một mảnh.
- File > 1MB → `update_project_context_file` từ chối (413). Inventory Markdown không tới mức đó; tới thì file đang chứa thứ không phải inventory (log, dump) — cắt ở phía file, không chia nhỏ trên QA Hub.
- Nộp lỗi (403 chưa join, MCP mất kết nối) → ghi vào tóm tắt "Chưa nộp lên QA Hub — lý do", **không** thử project khác, không bỏ qua im lặng. File trong repo vẫn ghi bình thường.

## Rào chắn

- Không ghi file nào ngoài `inventory/<KEY>.md`, và trên QA Hub chỉ đụng item `Inventory <KEY>` — không tạo/sửa item khác, không `upsert_knowledge`, không `delete_project_context`. Muốn sửa reference hay lưu rule → đề xuất ở § 5 và trong tóm tắt.
- Không suy diễn hành vi từ UI thành rule. "Nút Save disabled khi thiếu field" là quan sát (ghi được ở § 2 kèm nguồn staging); "hệ thống bắt buộc field X" là rule (→ § 5, đề xuất `update-business-rules`).
- Không credential, token, store domain merchant thật, dữ liệu khách hàng. Tài khoản chỉ ghi tên biến env.
- Không thêm sản phẩm vào cart, không tạo item trong app, không Test connection / gửi thật (digest, webhook). Muốn xem form thì mở Edit của item có sẵn rồi Discard.
- Chỉ staging / dev store. Được đưa URL production → dừng, hỏi lại.
- Không tóm tắt bằng cách bỏ mục: feature không đi được (cần plan Plus, cần scope) thì ghi ❌/🟡 kèm lý do, không im lặng bỏ.
- Nguồn nào không đọc được (403, không có clone, MCP hết hạn) → ghi § 0 "Nguồn không đọc được", không đoán để lấp.

## Khuôn trả về

```
HAE-SUMMARY
- App: <KEY> · file: inventory/<KEY>.md · <N> dòng · build YYYY-MM-DD
- Nguồn đã đọc: code <repo@sha> · staging <URL> (<M> màn) · Confluence <K> trang · QA Hub knowledge <N> doc
- Nguồn không đọc được: <…> hoặc "không"
- QA Hub: <"đã nộp — item Inventory <KEY> (mới tạo | cập nhật), file <KEY>-inventory.md" | "chưa nộp — lý do">
- Feature: <N> mục — ✅ <a> · 🟡 <b> · ❌ <c>
- Phát hiện lệch (§ 5): <N> dòng — <2–3 dòng đáng chú ý nhất>
- Đề xuất cho người dùng: sửa reference § … · hỏi Dev … · chạy update-business-rules cho …
- Cần Hae quyết: <…> hoặc "không"
```

## Khi nào build lại

Theo sự kiện, không theo lịch — xem [`inventory/README.md`](../../knowledge-work/inventory/README.md) § "Khi nào build lại". Build lại một module: `--module <tên>` → chỉ đi phần đó, giữ nguyên mục khác, cập nhật § 0 và § 5.

## Bước tiếp theo

Sau khi file có: chạy `qa-requirement-analysis` cho một ticket của app đó để kiểm xem GAP giả có giảm không. § 5 có dòng "Feature chưa có business rule" → khi có ticket chạm feature đó, chạy `update-business-rules`.

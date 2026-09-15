---
name: build-app-context
description: "Build hoặc build lại file `inventory/<KEY>.md` trong repo knowledge-work cho một app đang test (Tepo, Slide Cart Drawer, Checkout Customizer, Duos B2B, Mailtro) — đọc nguồn thật (code local, staging qua Playwright MCP, Confluence) rồi ghi ra route, màn hình, setting đúng tên UI, custom config flag, môi trường test, và mục 'phát hiện lệch' so với references/business-rules. Dùng khi người dùng nói 'build context cho app X', 'inventory QCO', 'staging đang có gì', 'cập nhật context app', 'reference cũ rồi build lại', hoặc khi terra/sonder báo reference không khớp hệ thống thật. KHÔNG dùng để: lưu business rule (update-business-rules), phân tích ticket (qa-requirement-analysis), sinh test case (gen-testcase), sửa references/apps/ (skill này chỉ đề xuất diff)."
---

## Vai trò

Người khảo sát hệ thống thật cho đội QA Qikify. Nhiệm vụ: với **một** app (`<KEY>`), đi đọc nguồn thật rồi ghi `knowledge-work/inventory/<KEY>.md` theo đúng [`templates/inventory.md`](../../knowledge-work/templates/inventory.md) và luật ở [`inventory/README.md`](../../knowledge-work/inventory/README.md). Đầu ra là **bằng chứng có nguồn**, không phải hiểu biết.

Skill này **chỉ ghi một file**: `inventory/<KEY>.md`. Không ghi `references/apps/`, không ghi `business-rules/`, không ghi `open-questions/` — mọi thứ đáng vào ba chỗ đó được liệt kê ở § 5 của inventory để người dùng quyết.

## Vị trí trong quy trình

Bước **0** (trước phân tích) hoặc bước bảo trì (sau release). `qa-requirement-analysis` và `gen-testcase` đọc file này để tránh GAP giả và để Steps dùng đúng tên UI. Chạy qua sub-agent (mở browser lâu, context nặng) — Hae giao, không tự chạy trong context điều phối.

## Đường dẫn

Tính từ thư mục skill này: `../../knowledge-work/` là submodule repo [`ownego/qa-knowledge-work`](https://github.com/ownego/qa-knowledge-work). Nếu thư mục rỗng → báo `git submodule update --init` và dừng. Không tạo file ngoài repo để bù.

- Ghi: `../../knowledge-work/inventory/<KEY>.md`
- Đọc để đối chiếu: `../../knowledge-work/references/apps/<KEY>.md`, `business-rules/<KEY>.md`, `open-questions/<KEY>.md`
- `<KEY>` = key project trên QA Hub (`list_projects`), viết HOA. Không có project khớp → dừng, hỏi.

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
2. **Staging** (Playwright MCP, headed): đi từng mục sidebar, chụp screenshot mỗi màn, chép label đúng chuỗi, thử mở route "không tồn tại" của lần build trước. Ghi trạng thái ✅/🟡/❌ từng feature. Với app Shopify, đi cả storefront/checkout của dev store để xác nhận widget hiện ở đâu. Không tạo dữ liệu thật, không đặt đơn có thanh toán thật, không đổi setting đang có — chỉ đọc; cần bật để xem thì bật rồi tắt lại.
3. **Confluence** (MCP Atlassian): chỉ để điền chỗ code/staging không nói (điều kiện plan, giới hạn theo gói). Ghi rõ ngày trang được sửa lần cuối; trang cũ hơn 12 tháng thì ghi kèm ⚠️.

## Các bước

1. `list_projects` → khớp `<KEY>`, lấy `projectId`. `list_tasks` → gom tag đang dùng, để điền dòng `Tag QA Hub` ở § 2.
2. Đọc `references/apps/<KEY>.md`, `business-rules/<KEY>.md`, `open-questions/<KEY>.md` — làm danh sách feature *kỳ vọng* để đối chiếu ở § 5.
3. Đọc `inventory/<KEY>.md` cũ nếu có → biết route "không tồn tại" lần trước, và giữ ghi chú sửa tay (xem commit message).
4. Đọc code theo thứ tự ở trên.
5. Đi staging. Screenshot lưu vào thư mục scratchpad của session (không commit ảnh vào repo).
6. Đọc Confluence cho chỗ còn trống.
7. Viết file theo template, đủ 6 mục. § 5 bắt buộc có nội dung.
8. Rà checklist cuối template. Ghi đè file. **Không commit** — người dùng xem diff rồi tự commit (hoặc bảo commit).
9. Trả về tóm tắt (khuôn dưới).

## Rào chắn

- Không ghi file nào ngoài `inventory/<KEY>.md`. Muốn sửa reference → đề xuất diff ở § 5 và trong tóm tắt.
- Không suy diễn hành vi từ UI thành rule. "Nút Save disabled khi thiếu field" là quan sát (ghi được ở § 2 kèm nguồn staging); "hệ thống bắt buộc field X" là rule (→ § 5, đề xuất `update-business-rules`).
- Không credential, token, store domain merchant thật, dữ liệu khách hàng. Tài khoản chỉ ghi tên biến env.
- Chỉ staging / dev store. Được đưa URL production → dừng, hỏi lại.
- Không tóm tắt bằng cách bỏ mục: feature không đi được (cần plan Plus, cần scope) thì ghi ❌/🟡 kèm lý do, không im lặng bỏ.
- Nguồn nào không đọc được (403, không có clone, MCP hết hạn) → ghi § 0 "Nguồn không đọc được", không đoán để lấp.

## Khuôn trả về

```
HAE-SUMMARY
- App: <KEY> · file: inventory/<KEY>.md · <N> dòng · build YYYY-MM-DD
- Nguồn đã đọc: code <repo@sha> · staging <URL> (<M> màn) · Confluence <K> trang
- Nguồn không đọc được: <…> hoặc "không"
- Feature: <N> mục — ✅ <a> · 🟡 <b> · ❌ <c>
- Phát hiện lệch (§ 5): <N> dòng — <2–3 dòng đáng chú ý nhất>
- Đề xuất cho người dùng: sửa reference § … · hỏi Dev … · chạy update-business-rules cho …
- Cần Hae quyết: <…> hoặc "không"
```

## Khi nào build lại

Theo sự kiện, không theo lịch — xem [`inventory/README.md`](../../knowledge-work/inventory/README.md) § "Khi nào build lại". Build lại một module: `--module <tên>` → chỉ đi phần đó, giữ nguyên mục khác, cập nhật § 0 và § 5.

## Bước tiếp theo

Sau khi file có: chạy `qa-requirement-analysis` cho một ticket của app đó để kiểm xem GAP giả có giảm không. § 5 có dòng "Feature chưa có business rule" → khi có ticket chạm feature đó, chạy `update-business-rules`.

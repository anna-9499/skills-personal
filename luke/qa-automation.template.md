# QA Automation Profile

<!--
Template cho `.claude/qa-automation.md` của một repo Playwright automation.
Luke và 3 sub-agent (planner / generator / healer) đọc file này đầu tiên; mọi thứ đặc thù
app nằm ở đây, không nằm trong prompt agent. Giá trị credential KHÔNG bao giờ ghi vào file
này — chỉ TÊN biến env. Chỗ chưa biết ghi `chưa có`.
-->

| Trường | Giá trị |
|---|---|
| App | <tên app> |
| App key (Jira / QA Hub) | <KEY, ví dụ MTRO, TEPO, QSC, QCO, DUOS> |
| Reference app | ~/.claude/skills/qa-requirement-analysis/references/apps/<KEY>.md (+ file phụ nếu có) |
| Business rules | ~/.claude/skills/qa-requirement-analysis/references/business-rules/<KEY>.md |
| Tỷ lệ auto/manual mục tiêu | <đường dẫn file | không áp dụng> |

## 1. Môi trường
- Domain / URL: <tên biến env cho từng domain; mô tả cross-domain nếu có>
- Tài khoản test (tên biến env theo role): <ROLE → TÊN_BIẾN_EMAIL / TÊN_BIẾN_PASSWORD>
- Cách đăng nhập: <Playwright MCP với tài khoản env | Chrome bridge (session đã đăng nhập, 2FA) | fixture storageState>
- Dấu hiệu production cần dừng: <pattern URL — agent thấy là dừng, không thao tác>
- Biến env đặc biệt: <TÊN=ý nghĩa, ví dụ RUN_RATE_LIMIT=1 bật case rate limit>
- Rate limit / giới hạn staging: <workers khuyến nghị; số lần thử tối đa login/signup/forgot mỗi phiên>

## 2. Cấu trúc repo
- Spec: `tests/<...>/<...>.spec.ts` — <quy tắc đặt thư mục/file>
- Page object / fixture / helper: <thư mục thật; file tiêu biểu nên đọc trước>
- Test plan: `specs/<TICKET>-<feature>-test-plan.md`; screenshot: `specs/screenshots/<TICKET>/`
- Bảng manual test case: <`docs/manual-testcases/<...>/<...>.md` — số cột, tên cột, 2 cột automation | không có>
- JSON xuất: <script + có phải chạy sau khi sửa md | không có>
- Log / healing: `test-results/`
- Lệnh chuẩn:
  - list: `npx playwright test <file> --list`
  - typecheck: `npx tsc --noEmit -p tsconfig.json`
  - lint: <lệnh | không có>
  - chạy 1 file: `npx playwright test <file> --reporter=list --retries=0 --workers=<n>`
  - chạy 1 test theo id: `npx playwright test <file> -g "<ID>" --retries=0`

## 3. Quy ước test case
- ID: <pattern, ví dụ TC-<SCREEN>-0xx; dải theo loại: conventions/module-naming.md>
- Tag title: conventions/scenario-tags.md
- Tag Playwright: <cách repo đang dùng, ví dụ thật>
- Tên test = `<ID> [<Tag>] <title>`
- Execution Type / Automation Script Ref: conventions/testcase-schema.md § 4.1

## 4. Dữ liệu test
- Prefix data tự tạo: plan `qa-plan-<TICKET>-…`; auto `qa-auto-<TICKET>-…` <hoặc helper của repo>
- Dọn dẹp: <helper có sẵn | chưa có → TODO trong spec>
- Data seed cần có sẵn: <…>

## 5. Không được đụng (an toàn)
- <hành động cấm trên staging: gửi email/notification tới địa chỉ thật, billing/thanh toán, xoá tài nguyên dùng chung, đổi quyền người khác, đơn hàng thật…>
- Case cần inbox thật / thiết bị thật / thanh toán thật → Manual với lý do chuẩn: `Manual — <lý do>`

## 6. Ghi chú riêng của app
<đặc thù kỹ thuật ảnh hưởng automation: cross-domain login, app embedded trong Shopify admin (iframe, 2FA), feature flag, empty state…>

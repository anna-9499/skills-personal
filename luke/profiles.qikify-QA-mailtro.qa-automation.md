# QA Automation Profile

| Trường | Giá trị |
|---|---|
| App | Mailtro — SaaS email marketing multi-tenant (workspace-based), **không phải Shopify app** (ADR 0008) |
| App key (Jira / QA Hub) | MTRO |
| Reference app | ~/.claude/skills/qa-requirement-analysis/references/apps/MTRO.md (+ MTRO-auto-manual-ratio.md) |
| Business rules | ~/.claude/skills/qa-requirement-analysis/references/business-rules/MTRO.md (bản sao y hệt trong repo: `docs/business-rules/MTRO.md`) |
| Tỷ lệ auto/manual mục tiêu | `docs/auto-manual-ratio.md` (bản sống, cập nhật 2026-09-11) — bản trong skill `MTRO-auto-manual-ratio.md` là draft 2026-08-13, số cũ hơn |

## 1. Môi trường
- Domain / URL — **2 host tách biệt, điều hướng sau auth là cross-domain**:
  - `AUTH_URL` — Mailtro ID (`https://staging-id.mailtro.ai`): `/login`, `/signup`, `/verify`, `/forgot-password`, `/reset-password`, màn `Choose a workspace` tại `/`. Mặc định trong `config/env.ts` nếu thiếu biến.
  - `BASE_URL` — app của workspace `https://<workspace-slug>.wisle.app` (`use.baseURL` trong `playwright.config.ts`, đọc lazy — suite `01-auth` không cần).
  - `WORKSPACE_DOMAIN_SUFFIX` — `.wisle.app`, hiển thị cạnh ô Workspace URL ở signup; dùng ghép slug → URL.
  - Luồng thật: login thành công ở `AUTH_URL` → dừng ở `/` (Choose a workspace) → chọn workspace → redirect kiểu OAuth `authorize` → `/callback` trên `<slug>.wisle.app` → `/dashboard`. Assert cross-domain bằng regex host đích, không hardcode slug.
- Tài khoản test (tên biến env theo role):
  - `AUTH_EMAIL` / `AUTH_PASSWORD` — tài khoản đã verify cho happy-path login + case "email đã tồn tại"; trống thì fallback `OWNER_*` (`env.authUser`, `hasAuthUser`).
  - `OWNER_EMAIL` / `OWNER_PASSWORD`, `ADMIN_EMAIL` / `ADMIN_PASSWORD`, `MEMBER_EMAIL` / `MEMBER_PASSWORD` — 3 role Owner/Admin/Member (`env.users.<role>`). Cả 3 phải cùng 1 workspace (R9 — chưa xác nhận).
  - `EXISTING_WORKSPACE_SLUG` — slug đã tồn tại, precondition TC-SIGNUP-034; trống thì test tự skip.
  - `data/test-data.json` cũng có `workspace.{name,slug}` + `users.<role>` nhưng code hiện đọc từ `.env` qua `config/env.ts`.
- Cách đăng nhập:
  - Suite Playwright: **fixture storageState** — `tests/auth.setup.ts` (project `setup`) login 3 role, lưu `.auth/owner|admin|member.json`; project `chromium` mặc định `.auth/admin.json`; role khác dùng `fixtures/auth.fixture.ts` → `test.use({ role: 'owner' })` + `roleAwarePage`. `01-auth/**` chạy ở project `chromium-unauthenticated` (không storageState). `.auth/` gitignored, phải chạy `npx playwright test --project=setup` trước.
  - Agent khám phá/heal (Playwright MCP): đăng nhập bằng tài khoản env ở `AUTH_URL/login`, rồi đi qua Choose a workspace sang `BASE_URL`.
  - Chrome bridge session có sẵn: chỉ dùng cho manual run (sonder), không phải quy ước của repo này.
- Dấu hiệu production cần dừng: URL `mailtro.ai` **không có** tiền tố `staging-` (theo agent planner). Repo không có guard code; biến `ENV` (`staging | production`) có trong `.env` nhưng chưa được kiểm tra ở đâu.
- Biến env đặc biệt:
  - `RUN_RATE_LIMIT_TESTS=1` — bật TC-SIGNUP-063 (11 request `/register`, làm cạn quota 10 req/60s → signup sau dính 429). Mặc định tắt, chạy riêng: `RUN_RATE_LIMIT_TESTS=1 npx playwright test -g TC-SIGNUP-063`. Lưu ý các agent cũ ghi tên biến là `RUN_RATE_LIMIT` — **tên đúng trong repo là `RUN_RATE_LIMIT_TESTS`**.
  - `SLOW_MO` (ms, mặc định 0; `npm run test:slow` đặt 800) — `use.launchOptions.slowMo`.
  - `CI` — bật `forbidOnly`, `retries: 2`, `workers: 1`.
  - Dự kiến thêm khi có R1/R13 (`docs/api-test-plan.md` R20): `API_BASE_URL`, `RUN_SIDE_EFFECT`, `MAIL_API_KEY`, `QA_WORKSPACE_SLUG` — chưa có.
- Rate limit / giới hạn staging:
  - `POST /login`: `x-ratelimit-limit: 10` / phiên. `POST /register`: 10 req/60s, request 11 → 429 `Too Many Attempts.`. `POST /api/auth/forgot-password` + `reset-password`: 10 req/60s **chung một bucket**, mọi 4xx cũng trừ quota (ADR 0004).
  - Project `api`: `workers: 1`, `fullyParallel: false`, `timeout: 120_000`; `utils/auth-api.ts` tự xếp hàng theo `x-ratelimit-remaining`. Không chạy `api` song song với `01-auth`.
  - Healer chạy `--workers=1 --retries=0`; planner tối đa 3 lần thử signup/login/forgot mỗi phiên khám phá.
  - Local mặc định `workers: undefined` (Playwright tự chọn) và `fullyParallel: true` — với data dùng chung trên 1 workspace (R31 chưa có workspace riêng) nên ưu tiên `--workers=1` khi chạy suite nghiệp vụ.

## 2. Cấu trúc repo
- Spec: `tests/<NN>-<feature>/<screen>.spec.ts` — `NN` map 1-1 epic MTRO theo thứ tự phase, **số đã cấp không đánh lại** (ADR 0001): `01-auth` MTRO-30 · `02-team` MTRO-20 · `03-account-setup` MTRO-6 · `04-contacts` MTRO-8 · `05-templates` MTRO-15 · `06-automations` MTRO-13 · `07-campaigns` MTRO-11 · `08-brand-guideline` MTRO-18 · `09-backlog` (epic chưa có due; đề xuất tách `10-unsubscribe` MTRO-17, `11-bounce-complaint` MTRO-64, `12-analytics` MTRO-16) · `smoke/app-shell.spec.ts` (khung app) · `tests/auth.setup.ts`. Spec API: `<screen>.api.spec.ts` cùng thư mục với spec UI (project `api`). Feature chưa có UI → khung `test.fixme` có mô tả + link US, không để thư mục trống (ADR 0006).
- Page object / fixture / helper:
  - `pages/base.page.ts` (`BasePage`: `goto`, `waitForPageLoad`) + `pages/<feature>/<screen>.page.ts` chia đúng bộ tên feature — tiêu biểu `pages/auth/login.page.ts` (locator `getByRole`/`#email`/`[data-slot="alert"]`, `submitAndWaitForLogin`, `countLoginRequests`, `sessionCookie`), `pages/auth/signup.page.ts`, `pages/auth/forgot-password.page.ts` (export `FORGOT_PASSWORD_API`, `RESET_PASSWORD_API`).
  - `fixtures/auth.fixture.ts` (dùng được) · `fixtures/seed-data.fixture.ts`, `fixtures/workspace.fixture.ts` (khung TODO, chờ API spec MTRO-8/MTRO-6 — workspace fixture hiện `throw`).
  - `utils/helpers.ts` (`waitForLoadState`, `waitForToast`, `withinIframe`, `retry`, `randomString`) · `utils/test-data-generator.ts` (`uniqueEmail`, `contactPayload`, `campaignName`, `workspaceName`, `slugify`, `signupPayload`) · `utils/auth-api.ts` (`AuthApi` có throttle, `jsonBody`, `ValidationErrorBody`) · `utils/api-client.ts` (khung TODO, path `/api/contacts`, `/api/segments` là phỏng đoán). Mọi HTTP phải qua `utils/<module>-api.ts` (ADR 0007).
  - `config/env.ts` — nguồn duy nhất đọc `.env`.
- Test plan: `specs/<TICKET>-<feature>-test-plan.md` — thư mục `specs/` **tạo khi planner chạy lần đầu, commit bình thường** ( screenshot dự kiến `specs/screenshots/<TICKET>/<NN>-<ten>.png`). Tài liệu bối cảnh sẵn có thay thế: `docs/staging-feature-inventory.md`, `docs/build-staging-feature-overview.md`, `docs/qa-sprint-status.md`, `docs/api-test-plan.md`.
- Bảng manual test case: `docs/manual-testcases/<NN-feature>/<screen>.md` — **9 cột**: `ID | Title | Precondition | Steps | Test Data | Expected Result | Priority | Execution Type | Automation Script Ref`. Header file có bảng meta (Epic / Story, Module, Màn hình, URL, Môi trường, Ngày viết, Cập nhật, Người viết, Spec auto tương ứng); mục 1 mô tả màn hình + DOM, mục 2 precondition chung, mục 3 bảng case chia `### 3.x` theo nhóm (UI / Validation / Happy path / Negative-Edge / Security / Navigation…). Xuống dòng trong ô `<br>`, ô rỗng `—`, Priority `P0/P1/P2`. Map file ↔ spec ghi trong README (vd `04-contacts/segment.md` ↔ `segment*.spec.ts`).
- JSON xuất: `node scripts/testcases-to-json.mjs docs/manual-testcases/<NN>/<screen>.md` (alias `npm run testcases:json -- <path>`) → `data-output/testcases_<module-không-NN>-<screen>.json`, tự chia `.part1/.part2` khi > 50.000 byte; 13 cột QA Hub/Sheet, `appPrefix: MTRO`, P0/P1/P2 → High/Medium/Low. Markdown là nguồn sự thật, JSON **không sửa tay** nhưng **được commit** → **phải chạy lại sau mỗi lần sửa md** (ADR 0009).
- Log / healing: **healing log ghi `docs/test-runs/<NN-feature>/<TICKET>-healing-log.md`** (được commit, cùng chỗ manual run log; screenshot nghi vấn bug vào `docs/test-runs/<NN-feature>/evidence/<TICKET>/bug-<TC-ID>.png`). Log thô của lần chạy (`<TICKET>-run-N.log`), trace, report Playwright để ở `test-results/` (gitignored). Report: `playwright-report/index.html` (`npm run report`), `smart-report/index.html` + `test-history.json` (playwright-smart-reporter, 20 run). Manual run/bug log của người: `docs/test-runs/<NN>/<YYYY-MM-DD>-<màn>-manual-run.md` (+ `evidence/`), `docs/bugs/<NN>/<YYYY-MM-DD>-<màn>-bug-log.md`. Quay video tái hiện bug: `npm run record:bug -- --name <slug> [--role owner|admin|member] [--path /campaigns] [--fresh] [--viewport 375x812]` → `bug-recordings/` (gitignored). Snapshot Playwright MCP rơi vào `.playwright-mcp/` (gitignored).
- Lệnh chuẩn:
  - list: `npx playwright test tests/<NN-feature>/<screen>.spec.ts --list`
  - typecheck: `npx tsc --noEmit -p tsconfig.json` (`strict: true`, module `node16`, include `tests|pages|fixtures|utils|config|data`)
  - lint: **chưa có** (không có eslint trong `package.json`)
  - setup storageState: `npx playwright test --project=setup`
  - chạy 1 file: `npx playwright test tests/01-auth/login.spec.ts --reporter=list --retries=0 --workers=1`
  - chạy 1 test theo id: `npx playwright test --grep "TC-LOGIN-020"` (hoặc `-g`)
  - theo tag/phase/project: `npm run test:smoke|phase1..4|backlog|P0|auth|team|contacts|templates|automations|campaigns|api`; `test:headed`, `test:slow`, `test:debug`, `test:ui`.

## 3. Quy ước test case
- ID: `TC-<SCREEN>-0xx` theo **màn hình** (ngoại lệ MTRO trong `conventions/module-naming.md`), chia lô theo loại kiểm thử và chừa khoảng trống: `001..00x` UI/hiển thị · `010..` Validation · `020..` Happy path · `030..` (signup: auto-slug) · `040..` Happy/Negative · `050..` Negative/Edge · `060..` Security · `070..` Navigation — nối tiếp id lớn nhất đã có trong md, không reset. Prefix đang dùng: `LOGIN`, `SIGNUP`, `FORGOT`, `RESET`, `API` (auth api), `INV`, `CONTACT`, `SEGMENT`, `SUPP`, `LIB`, `AUTO`, `FLOW`, `AUTORUN`, `AUTOISO`, `AUTORBAC`, `CAMP`, `WIZ`, `REP`. Spec API: `TC-API-<MODULE>-0xx` (`001–009` hợp đồng, `010–019` validate, `020–029` bảo mật/rate limit, `030–039` phân quyền, `040+` nghiệp vụ). Trên QA Hub id là `TC-MTRO-<số>` do QA Hub cấp; id repo ghi vào `Automation Script Ref`.
- Tag title: `conventions/scenario-tags.md` (`[Happy Path]`, `[Validation]`, `[Negative]`, `[Edge]`, `[Boundary]`, `[Security]`, `[UI]`, `[Navigation]`, `[Regression]`, `[Performance]`, `[Cross-app]`) — quy ước của skill; **bảng md và spec hiện tại của repo chưa dùng tag này** (title bắt đầu thẳng bằng nội dung, loại kiểm thử suy từ heading `### 3.x` và dải id).
- Tag Playwright (ADR 0002): khai ở option thứ 2 của `test.describe`: `{ tag: ['@phase1', '@auth'] }`; priority gắn ở từng test `test('TC-LOGIN-001 …', { tag: '@P0' }, …)`. Phase `@phase1..@phase4`/`@backlog`; feature theo tên thư mục: `@auth @team @account-setup @contacts @templates @automations @campaigns @brand @app-shell` (+ backlog `@unsubscribe @signup-form @onboarding @mcp-connectors @dashboard @analytics`); `@api` bắt buộc cho `*.api.spec.ts`; `@smoke` chỉ gắn cho 1 test/epic đã DONE và không bao giờ lên `test.fixme`.
- Tên test = `<ID> <title>` — xác nhận từ `tests/01-auth/login.spec.ts`: `test('TC-LOGIN-020 đăng nhập thành công với email/password hợp lệ', { tag: '@P0' }, …)`; case data-driven `test(\`TC-LOGIN-012 email sai định dạng "${invalidEmail}" bị chặn ở client\`)`. Không có `[Tag]` trong tên (khác với agent generator ghi `TC-LOGIN-014 [Validation] …`). Case chưa làm: `test.fixme('TC-… …', …)` với lý do trong comment/string; bug đang mở có key: `test.fail()` + `// BUG MTRO-xxx`. Cấm `test.skip` để xanh, cấm `waitForTimeout`.
- Execution Type / Automation Script Ref (`testcase-schema.md` § 4.1): `Automated` → `` `login.spec.ts` › TC-LOGIN-020 `` (+ `— chạy riêng RUN_RATE_LIMIT_TESTS=1`, `— test.fail() (bug MTRO-xxx đang mở)`, `(cover gián tiếp)`); `To be automated` → `` `login.spec.ts` › TC-LOGIN-014 — đang `test.fixme` `` hoặc `` `runtime.spec.ts` — chưa viết test ``; `Manual` → `—` **bắt buộc kèm lý do**. Mặc định case có assertion rõ là `To be automated`; chỉ ghi `Automated` khi xác nhận test tồn tại.

## 4. Dữ liệu test
- Prefix data tự tạo: plan `qa-plan-<TICKET>-…`, auto `qa-auto-<TICKET>-${Date.now()}` — **hoặc helper của repo** (ưu tiên khi viết spec): `uniqueEmail('qa'|'signup'|'contact')` → `qa+<ts>-<rand>@mailtro-test.com`, `signupPayload()`, `contactPayload()`, `campaignName('QA Campaign')`, `workspaceName('QA Workspace')`, `slugify()`. Manual run đang dùng tên như `RT-CREATED`, `AUTO-ISO-B`, `rt-created@example.com`.
- Dọn dẹp: **chưa có helper chung** (R19). `fixtures/seed-data.fixture.ts` có `deleteContact` sau `use()` nhưng API path là phỏng đoán chờ R1/R2. Không có helper → ghi TODO rõ trong spec; chỉ xoá thứ do chính mình tạo.
- Data seed cần có sẵn (hiện tạo tay qua UI, ghi rõ trong Precondition):
  - Workspace QA (`BASE_URL`) với 3 tài khoản `OWNER_*/ADMIN_*/MEMBER_*` cùng workspace; workspace thứ 2 + Owner khác cho case isolation (R11, đang tạo tay qua signup).
  - Sending domain **verified** hoặc borrowed sender (R12 ❌ — hiện chỉ test được nhánh bị chặn gửi).
  - Contacts: ≥ 1 contact, custom fields; segment có contact — precondition cho Campaigns/Automations.
  - Templates: ≥ 1 template trong Email library (`/templates`).
  - Automations: ≥ 1 automation cho list; flow test dùng step `Update property` để không gửi mail; dry-run qua `POST …/automations/{id}/test`.
  - Campaign `Sent` để test report; folder để test filter.
  - Bounce/suppression: địa chỉ SES Mailbox Simulator (`bounce@simulator.amazonses.com`, `complaint@…`, `ooto@…`; hậu tố `+tcNNN` để tách log).
  - Mail API để đọc inbox: **chưa có** (R13 — blocker lớn nhất).

## 5. Không được đụng (an toàn)
- Chỉ chạy trên staging (`staging-id.mailtro.ai`, `<slug>.wisle.app`); gặp `mailtro.ai` không có `staging-` → dừng.
- Không gửi campaign / test email / automation `Send email` tới địa chỉ thật ngoài hộp thư QA hoặc SES simulator; case Send sheet, Preview & test là side effect (R6/R13/R14) — chạy có kiểm soát, sau cờ env.
- Không đụng billing; không xoá workspace, đổi tên/transfer ownership workspace dùng chung (nhóm "test phá hoại" cần workspace riêng — R31); không đổi/xoá sending domain; không revoke role, remove member, revoke invitation của người khác.
- Không tạo tài khoản mới hàng loạt (mỗi signup gửi mail verify thật); không chạy TC-SIGNUP-063 / test rate limit trong suite mặc định; không chạy `api` song song `01-auth`.
- Không in giá trị credential ra log/plan/câu trả lời — chỉ tên biến; không hardcode email/password/slug thật vào spec.
- Không sửa `playwright.config.ts` (`retries`, `timeout`, tắt project) để ẩn lỗi; không sửa `data-output/*.json` tay; không sửa code app.
- Case cần inbox thật / thiết bị thật → `Manual` với lý do chuẩn: `— cần đọc inbox thật (chưa có mail API)` (verify email, reset link, invite token, test send), `— kiểm tra bằng mắt trên nhiều mail client` (render email), hoặc lý do tương đương cho DNS thật, deliverability, timing/scheduling, responsive/accessibility bằng mắt.

## 6. Ghi chú riêng của app
- **Cross-domain login**: session cookie `mailtro-staging-session` (httpOnly, Secure, SameSite=Lax) set ở `AUTH_URL`; sang workspace qua `authorize → /callback`. `tests/auth.setup.ts` hiện `goto(env.baseUrl)` rồi login — chưa xử lý bước Choose a workspace; credential đi qua 2 host để gọi API `*.wisle.app` (cookie hay Bearer) **chưa rõ** (R2) → mọi test API ngoài auth đang chặn.
- **Cảnh báo cho healer**: `tests/auth.setup.ts` chưa xử lý bước Choose a workspace / `/callback`; `.auth/` chưa từng thấy trên máy → storageState có thể chưa sinh thành công. Suite ngoài `01-auth` fail ở login → xếp loại B (môi trường), ghi log, không heal `auth.setup.ts` trong phạm vi ticket khác.
- **Backend Laravel Sanctum**: `POST /login`, `/register` cần `x-xsrf-token` (lấy qua `/sanctum/csrf-cookie`); `/api/auth/*` stateless; lỗi validate theo shape `{message, errors}`, 422; sai credential 422 `Sign in failed` / `Incorrect email or password.`; `GET` vào endpoint POST-only trả 404 và không tốn quota.
- **UI**: shadcn (`[data-slot="alert"]`, `alert-title`, `alert-description`); form login chỉ `#email` + `#password`, nút disabled tới khi đủ field; validation email bằng HTML5 (không gọi API khi sai format). Automations builder là canvas Vue Flow (kéo-thả assert bằng `dragTo()` + thứ tự node); dry-run trả bảng step/status/detail.
- **Chưa có / feature flag**: topbar `News`/`Support` không hoạt động (`component.topbar.notAvailable`); Import contact chưa có UI (`import-contact.spec.ts` giữ fixme); wait/delay step Automations (MTRO-85) Coming soon; schedule campaign (MTRO-84) đang In Progress; Team/Permission, Brand guideline, Analytics phần lớn To Do → spec là khung `test.fixme`.
- **Trạng thái suite**: chỉ `01-auth` (login/signup/forgot-password + api) có test thật (~124 test có TC-ID); các thư mục khác toàn `test.fixme` **không có TC-ID** trong tên, trong khi md đã có id → khi implement phải gắn id khớp bảng md.
- **Bug/không nhất quán đã biết** ảnh hưởng assert: login email viết HOA trả 422 trong khi signup coi HOA là trùng (TC-LOGIN-014 fixme); password toàn khoảng trắng chưa chặn (TC-LOGIN-015); MTRO-41 prototype "accept any non-empty email/password" — review lại khi BE thật (MTRO-54) merge; 13 điểm Automations chưa chốt (R39).
- Mọi thay đổi quy ước phải qua ADR mới trong `docs/decisions/` (không sửa đè); việc đang chờ ai ở `docs/decisions/assignments.md` (R1–R39).

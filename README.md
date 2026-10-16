# skills-personal

Capability cá nhân: skill và agent tự viết. Tách khỏi knowledge của công ty.

Ranh giới: **skill là *cách làm*, knowledge là *biết gì*.** Rule của app không nằm ở đây — nó ở repo [`knowledge-work`](knowledge-work), mount vào đây làm submodule.

**Mục lục:** [Yêu cầu](#yêu-cầu) · [Nội dung](#nội-dung) · [Nối vào Claude Code](#nối-vào-claude-code) · [Phụ thuộc knowledge-work](#phụ-thuộc-knowledge-work) · [Sửa skill](#sửa-skill) · [Hae](#hae--agent-điều-phối) · [Luke](#luke--agent-điều-phối-playwright-automation) · [daily-recap](#daily-recap-vì-sao-có-scriptstestlane-digestpy)

## Yêu cầu

- **macOS** (hoặc Linux). Mọi thứ nối bằng symlink và script bash; Windows không hỗ trợ.
- Claude Code **≥ 2.1** — cần `--agent <tên>` và setting `agent` để Hae chạy ở main thread.
- `git`, `python3` (≥ 3.8), `jq`, `curl`.
- Quyền đọc repo private `ownego/qa-knowledge-work` (submodule).
- Repo nằm đúng **`~/Downloads/AI Agent/skills-personal`**: `hae.md` gọi `hae/bin/*.sh` và `settings-patch.jq` gọi `env-guard.sh` theo đường dẫn tuyệt đối đó. Mailtro thêm: repo automation ở `~/Downloads/Auto testing/qikify-QA-mailtro` (`hae.md`, `sonder.md` đọc `.env` ở đó). Đặt chỗ khác thì sửa các đường dẫn này — `install.sh` sẽ nhắc.
- MCP server: `testlane` (QA Hub), `playwright` (headed), `chrome` (Chrome bridge), `atlassian`, Slack — `hae/bin/preflight.sh` kiểm đủ trước khi giao `sonder` / `ash`.

---

## Nội dung

```
skills/
  qa-requirement-analysis/   Phân tích yêu cầu Jira → báo cáo 14 mục + Readiness 14 điểm + task QA Hub
  gen-testcase/              Sinh test case 8 loại → ghi thẳng lên QA Hub qua MCP
  update-business-rules/     Merge rule đã xác nhận vào knowledge-work/apps/<KEY>/business-rules.md
  daily-recap/               Tổng hợp việc QA đang mở mỗi sáng — chỉ đọc
  build-app-context/         Đọc code / staging / Confluence → knowledge-work/apps/<KEY>/inventory.md + item context QA Hub
hae/                         Nhóm QA manual — agent mặc định mọi session (xem mục "Hae")
  hae.md                     Hae — agent điều phối, chạy ở main thread
  terra.md                   Sub-agent: chạy trọn vẹn qa-requirement-analysis → task QA Hub
  ore.md                     Sub-agent: chạy trọn vẹn gen-testcase → test case trên QA Hub
  flint.md                   Sub-agent: review độc lập bản phân tích + bộ test case (chỉ đọc, Opus)
  sonder.md                  Sub-agent: chạy manual test case trên staging → status lên QA Hub
  ash.md                     Sub-agent: chạy trọn vẹn build-app-context → inventory app
  bin/staging-lock.sh        Khoá staging một app một khoá, dùng chung Hae (sonder, ash) và Luke (healer)
  bin/preflight.sh           Kiểm repo / MCP / staging / khoá trước khi Hae giao sonder hoặc ash
  hooks/                     env-guard (chặn browser vào URL production) + apply-settings.sh vá settings.json
install.sh                   Nối repo vào Claude Code (symlink + hook) — chạy lại được
scripts/check-publish.py     Kiểm publish.json khớp SKILL.md — chạy trong pre-commit
.githooks/pre-commit         Hook của repo (bật bằng core.hooksPath)
luke/                        Nhóm Playwright automation — mở bằng `claude --agent luke` (xem mục "Luke")
  luke.md                    Luke — agent điều phối, chạy ở main thread
  playwright-test-planner.md    Sub-agent: khám phá app trên staging → test plan
  playwright-test-generator.md  Sub-agent: test plan → spec Playwright
  playwright-test-healer.md     Sub-agent: chạy spec trên staging, phân loại fail, sửa lỗi test
  qa-automation.template.md     Template profile `.claude/qa-automation.md` cho repo automation
  profiles.<repo>.qa-automation.md  Bản lưu profile đã dựng cho từng repo
```

## Nối vào Claude Code

`~/.claude/skills/<tên>`, `~/.claude/agents/Hae/*.md` và `~/.claude/agents/Luke/*.md` là symlink trỏ vào repo này. Sửa ở repo = sửa ở skill/agent đang chạy.

Skill khác trong `~/.claude/skills/` (cloudflare, wrangler, sandbox-*, nodeterm…) là skill vendor, **không** thuộc repo này.

Máy mới:
```bash
git clone --recurse-submodules git@github.com:anna-9499/skills-personal.git "$HOME/Downloads/AI Agent/skills-personal"
cd "$HOME/Downloads/AI Agent/skills-personal"
bash install.sh
```

`install.sh` chạy lại bao nhiêu lần cũng được: symlink mọi `skills/*/`, `hae/*.md`, `luke/*.md` (trừ `profiles.*`; `qa-automation.template.md` vẫn link vì `luke.md` đọc template qua đường dẫn này), gỡ symlink chết của skill / agent đã xoá khỏi repo, bật pre-commit hook, tự `git submodule update --init` nếu quên `--recurse-submodules`, và nhắc hai việc dưới nếu chưa làm. Thêm skill / agent mới → chạy lại `install.sh`, không phải sửa script. Không ghi đè file thật (không phải symlink) đang nằm ở đích — báo `BỎ QUA` để chị tự xem.

Rồi đặt Hae làm agent mặc định cho mọi session — thêm vào `~/.claude/settings.json`:
```json
{ "agent": "hae" }
```
Không có dòng này thì session là Claude Code thường; vẫn gọi được Hae từng lần bằng `claude --agent hae`.

Rồi cài rào chắn — **bắt buộc**, thiếu bước này thì `sonder` / `ash` điều hướng được tới URL production mà không ai chặn:
```bash
bash hae/hooks/apply-settings.sh    # backup + vá ~/.claude/settings.json, in diff; restart Claude Code
```
Script thêm hook `PreToolUse` `env-guard` cho các tool navigate của Playwright MCP / Chrome bridge (URL production → deny; mở tạm 30 phút bằng `touch ~/.hae-allow-production`, chỉ chị làm) và đưa `delete_bug` / `delete_knowledge` của QA Hub vào `permissions.ask`. Đường dẫn trong `settings-patch.jq` đang hardcode `~/Downloads/AI Agent/skills-personal` — clone chỗ khác thì sửa file đó trước.

> ⚠️ Quên `--recurse-submodules` → `knowledge-work/` rỗng → cả 3 symlink trong
> `references/` chết mà Claude **không báo lỗi rõ**, chỉ im lặng phân tích thiếu
> business rule. Lỡ clone thiếu thì `git submodule update --init`.

## Phụ thuộc knowledge-work

`knowledge-work/` là **submodule** trỏ tới [`ownego/qa-knowledge-work`](https://github.com/ownego/qa-knowledge-work) (private, org ownego). Knowledge của công ty do org quản quyền; repo này chỉ pin một commit của nó.

`skills/qa-requirement-analysis/references/` có 3 thư mục là symlink **thư mục** vào submodule đó — symlink thư mục nên thêm app hay convention mới không phải sửa wiring:

```
references/apps/            → ../../../knowledge-work/apps/         (apps/<KEY>/README.md, business-rules.md, open-questions.md, inventory.md, kb/)
references/platform/        → ../../../knowledge-work/platform/     (rule nền tảng chung mọi app)
references/conventions/     → ../../../knowledge-work/conventions/
```

Đường dẫn dừng **trong** repo (3 cấp `..`, không phải 4) — trước đây nó thoát ra thư mục cha nên clone lệch chỗ là chết. Giờ clone ở đâu cũng chạy, miễn có `--recurse-submodules`.

Thư mục thứ tư, `references/method/`, là file thật nằm trong repo này — `analysis-guide.md`, `security-checklist.md`, `performance-checklist.md`. Đó là **cách làm**, không phải knowledge của app, nên không đẩy sang `knowledge-work`.

### Sửa knowledge thì làm ở đâu

Sửa thẳng trong `knowledge-work/` — nó là bản làm việc thật, không phải bản sao. Trên đĩa chỉ có đúng một bản; `~/Downloads/AI Agent/knowledge-work` là symlink tương thích trỏ vào đây, chỉ để đường dẫn cũ không gãy — không repo nào phụ thuộc (repo automation Mailtro không trỏ vào đó, kiểm 2026-09-15). Chi tiết: `knowledge-work/integrations/claude-code.md`.

```bash
cd knowledge-work
# sửa file, rồi:
git add -A && git commit -m "..." && git push      # đẩy lên org
cd ..
git add knowledge-work && git commit -m "Cập nhật pin knowledge-work"
```

Bước cuối là **pin lại submodule**. Quên bước đó thì máy khác clone về vẫn nhận commit cũ.

### Vì sao là submodule chứ không phải copy

Quyền do org quản, sửa có audit qua git log, cả team mount cùng một nguồn. Và khi nghỉ việc, org gỡ quyền → submodule không clone được nữa → repo cá nhân này **không mang theo rule của công ty**.

---

## Sửa skill

1. Sửa `skills/<tên>/SKILL.md`.
2. `description` trong frontmatter là thứ Claude đọc để quyết định có gọi skill hay không — viết mơ hồ thì skill không kích hoạt đúng lúc. Liệt kê cả câu người dùng hay nói.
3. Session đang chạy **không** nạp lại; session mới mới có bản mới.
4. Đổi `name:` thì đổi cả tên thư mục.
5. Commit.

### Bẫy: publish.json

`qa-requirement-analysis`, `gen-testcase`, `update-business-rules` được port sang Cloudflare Worker để chạy trong QA Hub. `publish.json` mô tả phần nào bị bỏ / thay khi port, và nó trỏ theo **tên section chính xác** trong SKILL.md.

Đổi tiêu đề một section mà quên sửa `publish.json` → trỏ trượt, không báo lỗi, bản trên Worker âm thầm sai. Sửa tiêu đề thì mở `publish.json` cùng skill sửa theo.

Kiểm tự động bằng **pre-commit hook**: commit có đụng `SKILL.md` / `publish.json` của 3 skill trên thì `scripts/check-publish.py` chạy trên bản đang staged, khoá nào trỏ trượt (0 lần) hoặc mơ hồ (≥ 2 lần) → chặn commit. Khoá là tiêu đề (`## …`) phải khớp **nguyên dòng** — thêm chữ vào cuối tiêu đề cũng bị bắt. Bật hook một lần sau khi clone:

```bash
git config core.hooksPath .githooks
```

Kiểm tay file trên đĩa: `python3 scripts/check-publish.py --worktree`. Bỏ qua khẩn cấp: `git commit --no-verify`.

Worker **không có filesystem**. Thêm một câu "đọc `references/...`" vào SKILL.md thì phải đưa câu đó vào `dropParagraphs` (hoặc `replaceParagraphs`), và phần cốt lõi của file đó phải được inline sẵn trong SKILL.md — nếu không bản Worker sẽ mất hẳn phần hướng dẫn ấy mà không báo gì.

### Lịch sử: analyze-req đã bị gộp

`analyze-req` từng là một skill riêng làm cùng việc phân tích requirement, product-agnostic, không tạo task QA Hub. Hai `description` gần trùng nhau nên lúc gọi hay phân vân. Đã gộp hẳn vào `qa-requirement-analysis`:

- rubric 7 tiêu chí / 14 điểm + luật ghi đè, phân mức gap Blocker/Major/Minor, kỷ luật trích nguồn cho từng business rule, và các bảng có ID (BR/AS/GAP/RISK/SEC/PERF) → inline vào `SKILL.md`
- `analysis-guide.md`, `security-checklist.md`, `performance-checklist.md` → `references/method/`
- `readiness-rubric.md`, `report-template.md` → hoà tan vào `SKILL.md`, không còn file riêng
- yêu cầu **ngoài 5 app Qikify** vẫn phân tích được — chỉ bỏ qua `references/apps/<KEY>/` và bước tạo task

## Hae — agent điều phối

Người dùng chỉ nói chuyện với **Hae**. Hae không tự phân tích yêu cầu, sinh test case, review, chạy manual test hay build inventory app — giao cho 5 sub-agent, nhận kết quả, tự quyết bước tiếp, báo lại. Việc ngoài 5 mảng đó (business rule, daily recap, code, hỏi đáp) Hae làm như một session Claude Code bình thường.

```
chị ──▶ hae (main thread, settings.agent = "hae")
          ├──▶ terra    chạy trọn vẹn qa-requirement-analysis → báo cáo 14 mục + task QA Hub
          │               + chế độ cập nhật: gộp câu trả lời PO/Dev → đóng GAP, chấm lại Verdict, ghi đè notes
          ├──▶ ore      chạy trọn vẹn gen-testcase → test case trên QA Hub
          ├──▶ flint    review độc lập: sau terra (RA) và sau ore (TC) → BLOCK/WARN/PASS, thiếu case → ore bổ sung
          │               + chế độ MISS: bug production → case nào lẽ ra bắt được / ứng viên thiếu case
          ├──▶ sonder   chạy manual test case đã có, trên staging → status + actualResult lên QA Hub
          │               + case cần mắt nhìn: chụp ảnh từng bước, để not-run · chế độ retest bug: Passed / To Do
          ├──▶ ash      chạy trọn vẹn build-app-context → knowledge-work/apps/<KEY>/inventory.md + item context QA Hub
          └──  (tự làm) báo cáo gửi Dev/PO cho một task — chỉ trong chat
```

Vì sao Hae phải là **main thread** chứ không phải sub-agent: sub-agent trong Claude Code không gọi được Agent tool, nên "agent cha" bắt buộc là session chính. Claude Code ≥ 2.1 có `--agent <tên>` và setting `agent` cho việc này.

Claude Code quét `~/.claude/agents/` đệ quy và nhận agent theo `name:` trong frontmatter, nên gom vào thư mục con `Hae/` không đổi gì. Đường dẫn tới skill trong 6 file là `~/.claude/skills/...`, không phụ thuộc vị trí file agent.

Các quyết định trong `hae/hae.md` đáng biết trước khi sửa:

| Tình huống | Hae làm gì | Vì sao |
|---|---|---|
| Verdict Ready / Partially Ready | `flint` review RA rồi tự nối sang `ore`, không hỏi | đúng gợi ý sẵn trong skill qa-requirement-analysis; case chạm GAP mở đã có nhãn `PO/DEV confirm` |
| Verdict Not Ready | vẫn đi tiếp, sinh bộ case **nháp**: case chạm GAP Blocker gắn `PO/DEV confirm`, Expected theo giả định `AS-xx`; GAP Blocker + câu hỏi mục 12 lên đầu "Chị cần làm" (chốt 2026-10-05) | dừng hẳn thì chờ PO lâu mà không có gì để chạy; PO trả lời → `terra` chế độ cập nhật → `flint` TC sửa trên case cũ. Chị nói "chỉ phân tích" / "Not Ready thì dừng" thì vẫn dừng |
| "Tạo test case" mà chưa có task QA Hub | chạy `terra` trước, nói một câu, không hỏi | gen-testcase không tự tạo task |
| "Chạy test" mà task chưa có test case | đi `terra` → `ore` trước; xong mới hỏi có chạy `sonder` không | bước chạy cần môi trường + tài khoản, nên **không** tự nối `ore` → `sonder` |
| Chạy manual cho MTRO | không hỏi URL / tài khoản — `sonder` tự đọc `.env` của repo `qikify-QA-mailtro` | data test đã nằm trong repo; 4 app Shopify thì hỏi một câu gộp URL + cách đăng nhập |
| `sonder` báo nghi vấn bug | liệt kê bug, hỏi có report lên QA Hub không; chỉ gọi lại `sonder` cho đúng các case đó | `report_bug` có thể announce Slack/Jira — luôn không kèm `reportTo` |
| Retest bug sau khi Dev fix | `sonder` retest, không hỏi quyền `update_bug`; bug trên Jira → không đổi status | Jira giữ status bug (webhook ghi đè); đóng bug là việc của chị |
| `flint` MISS trả ứng viên thiếu case | hỏi chị chọn dòng rồi mới gọi `ore` | ứng viên chưa phải kết luận |
| Giao `sonder` / `ash` | chạy `bin/preflight.sh` rồi `bin/staging-lock.sh acquire`; `sonder` chia lô ≤ 15 case, giữ khoá suốt các lô | hai agent dùng chung staging (cả healer của Luke) dẫm data nhau |

Danh sách 11 câu Hae **được phép hỏi** (chia 3 nhóm A thiếu input / B duyệt trước khi ghi / C xung đột, đánh số cố định nên không liền) nằm trong `hae.md` mục "Khi nào hỏi, khi nào tự quyết". Muốn Hae hỏi nhiều hơn / ít hơn thì sửa đúng danh sách đó, đừng sửa rải rác.

**Sub-agent không nói chuyện được với người dùng.** Chúng chạy hết việc được giao, điểm nào skill bảo "hỏi người dùng" thì ghi vào `Cần Hae quyết` trong khối `### HAE-SUMMARY` đầu output. Hae bóc khối đó để ra quyết định, rồi chuyển kết quả cho người dùng — **dán nguyên văn** báo cáo 14 mục của `terra` và bảng kết quả chạy của `sonder`, vì output của sub-agent không tự hiện ra.

Khác với `req-analyst` đã xoá (xem bên dưới): `terra`, `ore`, `ash` chạy skill **đầy đủ**, có ghi lên QA Hub, và chỉ có Hae gọi — nên không còn chuyện model phân vân giữa skill và agent.

Tool của sub-agent được khai tường minh trong frontmatter và cố ý **thiếu** — mỗi agent chỉ ghi được đúng phần việc của mình:

| Sub-agent | Ghi được lên QA Hub | Cố ý không có |
|---|---|---|
| `terra` | `create_task`, `update_task` (chỉ `notes`, chế độ cập nhật) | `create_test_cases`, `update_test_case`, `report_bug` |
| `ore` | `create_test_cases` | `create_task`, `update_test_case`, `report_bug` |
| `sonder` | `update_test_case`, `report_bug` (chỉ khi Hae cho phép), `update_bug` (chỉ chế độ retest, chỉ `status` `Passed` / `To Do` — không đóng bug) | `create_task`, `create_test_cases`, `add_test_case_image` (bị treo — ảnh lưu local) |
| `flint` | **không ghi gì** — chỉ đọc QA Hub, Jira, file | mọi tool ghi, `Bash`, `Write`, `Edit` |
| `ash` | `add_project_context`, `update_project_context`, `update_project_context_file` (chỉ item `Inventory <KEY>…`); file `apps/<KEY>/inventory.md` | `create_task`, `create_test_cases`, `upsert_knowledge`, tool ghi Jira |

Không sub-agent nào có tool ghi lên Jira / Slack. `sonder` và `ash` mở app bằng Playwright MCP, hoặc Chrome bridge (`mcp__chrome__*`) khi cần session người dùng đã đăng nhập. Muốn mở thêm quyền thì mở ở frontmatter, có chủ đích.

### Lịch sử: agent req-analyst đã bị xoá

`agents/req-analyst.md` từng là subagent chạy `qa-requirement-analysis` ở chế độ chỉ đọc (không tạo task QA Hub, không hỏi tiếp), dành cho việc phân tích nhiều ticket song song. Nó không có phương pháp riêng — chỉ đọc lại SKILL.md — nhưng `description` trùng ~90% với skill nên khi paste 1 ticket model hay chọn nhầm agent, mất task QA Hub và bước nối sang `gen-testcase`. Cùng một lỗi với `analyze-req` ở trên. Đã xoá; cần chạy song song thì spawn agent `general-purpose` và bảo nó chạy skill này ở chế độ chỉ đọc.

## Luke — agent điều phối Playwright automation

Luke **không** phải agent mặc định (`settings.agent` vẫn là `hae`). Mở riêng bằng `claude --agent luke` khi đứng trong repo automation. Hae gặp yêu cầu automation (lập test plan, sinh spec, chạy/heal suite) thì chỉ nói một câu bảo mở session Luke — Hae không gọi 3 agent `playwright-test-*`.

```
chị ──▶ luke (main thread, claude --agent luke, trong repo automation)
          ├──▶ playwright-test-planner     khám phá app thật trên staging → specs/<TICKET>-*-test-plan.md
          ├──▶ playwright-test-generator   test plan → spec TypeScript theo convention của repo (chỉ --list + typecheck)
          └──▶ playwright-test-healer      chạy spec trên staging, phân loại fail A/B/C/D, sửa lỗi test ≤ 3 vòng
```

**Project profile là điều kiện tiên quyết.** Mọi thứ đặc thù của app — URL / tài khoản dưới dạng *tên biến env*, cấu trúc thư mục, quy ước id / tag, prefix data, danh sách không được đụng, rate limit — nằm trong `.claude/qa-automation.md` của repo automation. Repo chưa có thì Luke dựng nháp theo `luke/qa-automation.template.md` (đọc qua `~/.claude/agents/Luke/`, nên symlink template phải có dù nó không phải agent).

`luke/profiles.<repo>.qa-automation.md` là bản lưu của profile đã dựng. Bản thật nằm và được git track trong repo automation — với Mailtro là `qikify-QA-mailtro/.claude/qa-automation.md`, đang trùng bản lưu (kiểm 2026-10-05, sau ADR 0010 sắp lại thư mục module). Sửa bên nào thì chép sang bên kia.

Phân biệt với `sonder` của Hae: `sonder` đi tay từng **manual test case trên QA Hub**; `playwright-test-healer` chạy **spec Playwright** trong repo. Healer cập nhật được status test case trên QA Hub khi được đưa task, nhưng **không** report bug; generator không mở browser và không chạy staging; planner không ghi gì lên QA Hub.


---

## daily-recap: vì sao có `scripts/testlane-digest.py`

Skill này **không** dùng MCP tool `list_tasks`, mà gọi thẳng HTTP endpoint của QA Hub. Hai lý do, cả hai đều đã đo được:

1. **`list_tasks` trả về cả field `notes`** — nguyên bản phân tích requirement. Một project (QCO) trả ~14K token, project MTRO 62K ký tự cho 12 task. Gọi cho cả 8 project là vỡ context. Script vứt `notes` đi trước khi in → output còn ~1.5KB.
2. **Không dùng được `urllib`/`requests`.** QA Hub đứng sau Cloudflare, và CF chặn bằng error 1010 `browser_signature_banned` — chặn theo **TLS fingerprint**, không phải User-Agent, nên đổi UA không cứu được. `curl` thì qua. Script vì vậy shell out sang `curl`; đừng "dọn dẹp" ngược lại.

Token đọc từ `~/.claude.json` lúc chạy, không hardcode, không in ra.

### QA Hub vs Atlassian: khác nhau ở chỗ hết hạn

| | Cách xác thực | Hết hạn? |
|---|---|---|
| QA Hub | Bearer token tĩnh trong `~/.claude.json` | Không |
| Atlassian | OAuth | **Có** — gặp `requires re-authorization` thì chạy `/mcp` đăng nhập lại |

Vì vậy `daily-recap` được viết để **chịu được việc Jira chết**: vẫn xuất báo cáo phần QA Hub và ghi một dòng nói phần Jira bỏ trống. Đừng sửa thành fail cả bài.

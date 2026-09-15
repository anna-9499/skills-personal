# skills-personal

Capability cá nhân: skill và agent tự viết. Tách khỏi knowledge của công ty.

Ranh giới: **skill là *cách làm*, knowledge là *biết gì*.** Rule của app không nằm ở đây — nó ở repo [`knowledge-work`](knowledge-work), mount vào đây làm submodule.

---

## Nội dung

```
skills/
  qa-requirement-analysis/   Phân tích yêu cầu Jira → báo cáo 14 mục + Readiness 14 điểm + task Testlane
  gen-testcase/              Sinh test case 8 loại → ghi thẳng lên QA Hub (Testlane) qua MCP
  update-business-rules/     Merge rule đã xác nhận vào knowledge-work/business-rules/
  daily-recap/               Tổng hợp việc QA đang mở mỗi sáng — chỉ đọc
hae/                         Nhóm QA manual — agent mặc định mọi session (xem mục "Hae")
  hae.md                     Hae — agent điều phối, chạy ở main thread
  terra.md                   Sub-agent: chạy trọn vẹn qa-requirement-analysis → task Testlane
  ore.md                     Sub-agent: chạy trọn vẹn gen-testcase → test case trên QA Hub
  sonder.md                  Sub-agent: chạy manual test case trên staging → status lên QA Hub
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
git clone --recurse-submodules git@github.com:anna-9499/skills-personal.git
cd skills-personal
for s in qa-requirement-analysis gen-testcase update-business-rules daily-recap; do
  ln -sfn "$PWD/skills/$s" ~/.claude/skills/$s
done
mkdir -p ~/.claude/agents/Hae ~/.claude/agents/Luke
for a in hae terra ore sonder; do
  ln -sfn "$PWD/hae/$a.md" ~/.claude/agents/Hae/$a.md
done
# qa-automation.template.md không phải agent nhưng vẫn phải link: luke.md đọc template qua đường dẫn này
for a in luke playwright-test-planner playwright-test-generator playwright-test-healer qa-automation.template; do
  ln -sfn "$PWD/luke/$a.md" ~/.claude/agents/Luke/$a.md
done
```

Rồi đặt Hae làm agent mặc định cho mọi session — thêm vào `~/.claude/settings.json`:
```json
{ "agent": "hae" }
```
Không có dòng này thì session là Claude Code thường; vẫn gọi được Hae từng lần bằng `claude --agent hae`.

> ⚠️ Quên `--recurse-submodules` → `knowledge-work/` rỗng → cả 3 symlink trong
> `references/` chết mà Claude **không báo lỗi rõ**, chỉ im lặng phân tích thiếu
> business rule. Lỡ clone thiếu thì `git submodule update --init`.

## Phụ thuộc knowledge-work

`knowledge-work/` là **submodule** trỏ tới [`ownego/qa-knowledge-work`](https://github.com/ownego/qa-knowledge-work) (private, org ownego). Knowledge của công ty do org quản quyền; repo này chỉ pin một commit của nó.

`skills/qa-requirement-analysis/references/` có 3 thư mục là symlink **thư mục** vào submodule đó — symlink thư mục nên thêm app hay convention mới không phải sửa wiring:

```
references/apps/            → ../../../knowledge-work/references/apps/
references/business-rules/  → ../../../knowledge-work/business-rules/
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

`qa-requirement-analysis`, `gen-testcase`, `update-business-rules` được port sang Cloudflare Worker để chạy trong Testlane (qa-hub). `publish.json` mô tả phần nào bị bỏ / thay khi port, và nó trỏ theo **tên section chính xác** trong SKILL.md.

Đổi tiêu đề một section mà quên sửa `publish.json` → trỏ trượt, không báo lỗi, bản trên Worker âm thầm sai. Sửa tiêu đề thì mở `publish.json` cùng skill sửa theo.

Kiểm nhanh trước khi commit — báo ngay nếu có khoá nào trỏ trượt:

```bash
python3 - << 'EOF'
import io, json
for skill in ["qa-requirement-analysis", "gen-testcase", "update-business-rules"]:
    cfg = json.load(io.open(f"skills/{skill}/publish.json", encoding="utf-8"))
    md  = io.open(f"skills/{skill}/SKILL.md", encoding="utf-8").read()
    bad = [f"{f}: [{md.count(k)}x] {k[:70]}"
           for f in ["dropSections", "dropParagraphs"] for k in cfg.get(f, [])
           if md.count(k) != 1]
    bad += [f"{f}: [{md.count(k)}x] {k[:70]}"
            for f in ["sectionNotes", "replaceSections", "replaceParagraphs"] for k in cfg.get(f, {})
            if md.count(k) != 1]
    print(("FAIL " if bad else "OK   ") + skill)
    for b in bad: print("      ", b)
EOF
```

Worker **không có filesystem**. Thêm một câu "đọc `references/...`" vào SKILL.md thì phải đưa câu đó vào `dropParagraphs` (hoặc `replaceParagraphs`), và phần cốt lõi của file đó phải được inline sẵn trong SKILL.md — nếu không bản Worker sẽ mất hẳn phần hướng dẫn ấy mà không báo gì.

### Lịch sử: analyze-req đã bị gộp

`analyze-req` từng là một skill riêng làm cùng việc phân tích requirement, product-agnostic, không tạo task Testlane. Hai `description` gần trùng nhau nên lúc gọi hay phân vân. Đã gộp hẳn vào `qa-requirement-analysis`:

- rubric 7 tiêu chí / 14 điểm + luật ghi đè, phân mức gap Blocker/Major/Minor, kỷ luật trích nguồn cho từng business rule, và các bảng có ID (BR/AS/GAP/RISK/SEC/PERF) → inline vào `SKILL.md`
- `analysis-guide.md`, `security-checklist.md`, `performance-checklist.md` → `references/method/`
- `readiness-rubric.md`, `report-template.md` → hoà tan vào `SKILL.md`, không còn file riêng
- yêu cầu **ngoài 5 app Qikify** vẫn phân tích được — chỉ bỏ qua `references/apps/` và bước tạo task

## Hae — agent điều phối

Người dùng chỉ nói chuyện với **Hae**. Hae không tự phân tích yêu cầu, sinh test case hay chạy manual test — giao cho 3 sub-agent, nhận kết quả, tự quyết bước tiếp, báo lại. Việc ngoài 3 mảng đó (business rule, daily recap, code, hỏi đáp) Hae làm như một session Claude Code bình thường.

```
chị ──▶ hae (main thread, settings.agent = "hae")
          ├──▶ terra    chạy trọn vẹn qa-requirement-analysis → báo cáo 14 mục + task Testlane
          ├──▶ ore      chạy trọn vẹn gen-testcase → test case trên QA Hub
          └──▶ sonder   chạy manual test case đã có, trên staging → status + actualResult lên QA Hub
```

Vì sao Hae phải là **main thread** chứ không phải sub-agent: sub-agent trong Claude Code không gọi được Agent tool, nên "agent cha" bắt buộc là session chính. Claude Code ≥ 2.1 có `--agent <tên>` và setting `agent` cho việc này.

Claude Code quét `~/.claude/agents/` đệ quy và nhận agent theo `name:` trong frontmatter, nên gom vào thư mục con `Hae/` không đổi gì. Đường dẫn tới skill trong 4 file là `~/.claude/skills/...`, không phụ thuộc vị trí file agent.

Các quyết định trong `hae/hae.md` đáng biết trước khi sửa:

| Tình huống | Hae làm gì | Vì sao |
|---|---|---|
| Verdict Ready / Partially Ready | tự nối sang `ore`, không hỏi | đúng gợi ý sẵn trong skill qa-requirement-analysis; case chạm GAP mở đã có nhãn `PO/DEV confirm` |
| Verdict Not Ready | dừng, đưa câu hỏi mục 12 | có GAP Blocker thì sinh case dễ sai cả hướng |
| "Tạo test case" mà chưa có task Testlane | chạy `terra` trước, nói một câu, không hỏi | gen-testcase không tự tạo task |
| "Chạy test" mà task chưa có test case | đi `terra` → `ore` trước; xong mới hỏi có chạy `sonder` không | bước chạy cần môi trường + tài khoản, nên **không** tự nối `ore` → `sonder` |
| Chạy manual cho MTRO | không hỏi URL / tài khoản — `sonder` tự đọc `.env` của repo `qikify-QA-mailtro` | data test đã nằm trong repo; 4 app Shopify thì hỏi một câu gộp URL + cách đăng nhập |
| `sonder` báo nghi vấn bug | liệt kê bug, hỏi có report lên Testlane không; chỉ gọi lại `sonder` cho đúng các case đó | `report_bug` có thể announce Slack/Jira — luôn không kèm `reportTo` |

Danh sách 8 tình huống Hae **được phép hỏi** nằm trong `hae.md` mục "Khi nào hỏi, khi nào tự quyết". Muốn Hae hỏi nhiều hơn / ít hơn thì sửa đúng danh sách đó, đừng sửa rải rác.

**Sub-agent không nói chuyện được với người dùng.** Chúng chạy hết việc được giao, điểm nào skill bảo "hỏi người dùng" thì ghi vào `Cần Hae quyết` trong khối `### HAE-SUMMARY` đầu output. Hae bóc khối đó để ra quyết định, rồi chuyển kết quả cho người dùng — **dán nguyên văn** báo cáo 14 mục của `terra` và bảng kết quả chạy của `sonder`, vì output của sub-agent không tự hiện ra.

Khác với `req-analyst` đã xoá (xem bên dưới): ba sub-agent này chạy skill **đầy đủ**, có ghi lên Testlane, và chỉ có Hae gọi — nên không còn chuyện model phân vân giữa skill và agent.

Tool của sub-agent được khai tường minh trong frontmatter và cố ý **thiếu** — mỗi agent chỉ ghi được đúng phần việc của mình:

| Sub-agent | Ghi được lên Testlane | Cố ý không có |
|---|---|---|
| `terra` | `create_task` | `create_test_cases`, `update_test_case`, `report_bug` |
| `ore` | `create_test_cases` | `create_task`, `update_test_case`, `report_bug` |
| `sonder` | `update_test_case`, `add_test_case_image`, `report_bug` (chỉ khi Hae cho phép) | `create_task`, `create_test_cases` |

Cả ba chỉ **đọc** Jira, không có tool ghi lên Jira. `sonder` mở app bằng Playwright MCP, hoặc Chrome bridge (`mcp__chrome__*`) khi cần session người dùng đã đăng nhập. Muốn mở thêm quyền thì mở ở frontmatter, có chủ đích.

### Lịch sử: agent req-analyst đã bị xoá

`agents/req-analyst.md` từng là subagent chạy `qa-requirement-analysis` ở chế độ chỉ đọc (không tạo task Testlane, không hỏi tiếp), dành cho việc phân tích nhiều ticket song song. Nó không có phương pháp riêng — chỉ đọc lại SKILL.md — nhưng `description` trùng ~90% với skill nên khi paste 1 ticket model hay chọn nhầm agent, mất task Testlane và bước nối sang `gen-testcase`. Cùng một lỗi với `analyze-req` ở trên. Đã xoá; cần chạy song song thì spawn agent `general-purpose` và bảo nó chạy skill này ở chế độ chỉ đọc.

## Luke — agent điều phối Playwright automation

Luke **không** phải agent mặc định (`settings.agent` vẫn là `hae`). Mở riêng bằng `claude --agent luke` khi đứng trong repo automation. Hae gặp yêu cầu automation (lập test plan, sinh spec, chạy/heal suite) thì chỉ nói một câu bảo mở session Luke — Hae không gọi 3 agent `playwright-test-*`.

```
chị ──▶ luke (main thread, claude --agent luke, trong repo automation)
          ├──▶ playwright-test-planner     khám phá app thật trên staging → specs/<TICKET>-*-test-plan.md
          ├──▶ playwright-test-generator   test plan → spec TypeScript theo convention của repo (chỉ --list + typecheck)
          └──▶ playwright-test-healer      chạy spec trên staging, phân loại fail A/B/C/D, sửa lỗi test ≤ 3 vòng
```

**Project profile là điều kiện tiên quyết.** Mọi thứ đặc thù của app — URL / tài khoản dưới dạng *tên biến env*, cấu trúc thư mục, quy ước id / tag, prefix data, danh sách không được đụng, rate limit — nằm trong `.claude/qa-automation.md` của repo automation. Repo chưa có thì Luke dựng nháp theo `luke/qa-automation.template.md` (đọc qua `~/.claude/agents/Luke/`, nên symlink template phải có dù nó không phải agent).

`luke/profiles.<repo>.qa-automation.md` là bản lưu của profile đã dựng. Bản thật nằm và được git track trong repo automation — với Mailtro là `qikify-QA-mailtro/.claude/qa-automation.md`, đang trùng bản lưu (kiểm 2026-09-15). Sửa bên nào thì chép sang bên kia.

Phân biệt với `sonder` của Hae: `sonder` đi tay từng **manual test case trên QA Hub**; `playwright-test-healer` chạy **spec Playwright** trong repo. Healer cập nhật được status test case trên QA Hub khi được đưa task, nhưng **không** report bug; generator không mở browser và không chạy staging; planner không ghi gì lên QA Hub.


---

## daily-recap: vì sao có `scripts/testlane-digest.py`

Skill này **không** dùng MCP tool `list_tasks`, mà gọi thẳng HTTP endpoint của Testlane. Hai lý do, cả hai đều đã đo được:

1. **`list_tasks` trả về cả field `notes`** — nguyên bản phân tích requirement. Một project (QCO) trả ~14K token, project MTRO 62K ký tự cho 12 task. Gọi cho cả 8 project là vỡ context. Script vứt `notes` đi trước khi in → output còn ~1.5KB.
2. **Không dùng được `urllib`/`requests`.** QA Hub đứng sau Cloudflare, và CF chặn bằng error 1010 `browser_signature_banned` — chặn theo **TLS fingerprint**, không phải User-Agent, nên đổi UA không cứu được. `curl` thì qua. Script vì vậy shell out sang `curl`; đừng "dọn dẹp" ngược lại.

Token đọc từ `~/.claude.json` lúc chạy, không hardcode, không in ra.

### Testlane vs Atlassian: khác nhau ở chỗ hết hạn

| | Cách xác thực | Hết hạn? |
|---|---|---|
| Testlane | Bearer token tĩnh trong `~/.claude.json` | Không |
| Atlassian | OAuth | **Có** — gặp `requires re-authorization` thì chạy `/mcp` đăng nhập lại |

Vì vậy `daily-recap` được viết để **chịu được việc Jira chết**: vẫn xuất báo cáo phần Testlane và ghi một dòng nói phần Jira bỏ trống. Đừng sửa thành fail cả bài.

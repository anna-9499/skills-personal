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
```

## Nối vào Claude Code

`~/.claude/skills/<tên>` là symlink trỏ vào repo này. Sửa ở repo = sửa ở skill đang chạy.

Skill khác trong `~/.claude/skills/` (cloudflare, wrangler, sandbox-*, nodeterm…) là skill vendor, **không** thuộc repo này.

Máy mới:
```bash
git clone --recurse-submodules git@github.com:anna-9499/skills-personal.git
cd skills-personal
for s in qa-requirement-analysis gen-testcase update-business-rules daily-recap; do
  ln -sfn "$PWD/skills/$s" ~/.claude/skills/$s
done
```

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

Sửa thẳng trong `knowledge-work/` — nó là bản làm việc thật, không phải bản sao. Trên đĩa chỉ có đúng một bản; `~/Downloads/AI Agent/knowledge-work` là symlink tương thích trỏ vào đây (repo automation Mailtro còn dùng đường dẫn cũ).

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

### Lịch sử: agent req-analyst đã bị xoá

`agents/req-analyst.md` từng là subagent chạy `qa-requirement-analysis` ở chế độ chỉ đọc (không tạo task Testlane, không hỏi tiếp), dành cho việc phân tích nhiều ticket song song. Nó không có phương pháp riêng — chỉ đọc lại SKILL.md — nhưng `description` trùng ~90% với skill nên khi paste 1 ticket model hay chọn nhầm agent, mất task Testlane và bước nối sang `gen-testcase`. Cùng một lỗi với `analyze-req` ở trên. Đã xoá; cần chạy song song thì spawn agent `general-purpose` và bảo nó chạy skill này ở chế độ chỉ đọc.


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

# skills-personal

Capability cá nhân: skill và agent tự viết. Tách khỏi knowledge của công ty.

Ranh giới: **skill là *cách làm*, knowledge là *biết gì*.** Rule của app không nằm ở đây — nó ở repo [`knowledge-work`](../knowledge-work).

---

## Nội dung

```
skills/
  qa-requirement-analysis/   Phân tích yêu cầu Jira → báo cáo 14 mục + task Testlane
  gen-testcase/              Sinh test case 8 loại → JSON + xlsx + push Google Sheet
  update-business-rules/     Merge rule đã xác nhận vào knowledge-work/business-rules/
  analyze-req/               Phân tích yêu cầu, chấm Readiness Score (product-agnostic)
agents/
  req-analyst.md             Subagent chạy qa analysis song song, giữ context chính gọn
```

## Nối vào Claude Code

`~/.claude/skills/<tên>` và `~/.claude/agents/req-analyst.md` là symlink trỏ vào repo này. Sửa ở repo = sửa ở skill đang chạy.

Skill khác trong `~/.claude/skills/` (cloudflare, wrangler, sandbox-*, nodeterm…) là skill vendor, **không** thuộc repo này.

Máy mới:
```bash
for s in qa-requirement-analysis gen-testcase update-business-rules analyze-req; do
  ln -sfn "$PWD/skills/$s" ~/.claude/skills/$s
done
ln -sfn "$PWD/agents/req-analyst.md" ~/.claude/agents/req-analyst.md
```

## Phụ thuộc knowledge-work

`skills/qa-requirement-analysis/references/` toàn bộ là symlink **tương đối** sang `knowledge-work`:

```
references/qikify-apps-reference.md      → ../../../../knowledge-work/references/…
references/business-rules/DUOS.md        → ../../../../../knowledge-work/business-rules/…
```

Tương đối chứ không tuyệt đối, nên repo còn dùng được trên máy khác — **với điều kiện `skills-personal` và `knowledge-work` nằm cùng một thư mục cha**. Clone lệch chỗ là symlink chết.

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

`analyze-req` không có `publish.json` — không dính Testlane.

### Trùng vai trò cần xử lý

`analyze-req` và `qa-requirement-analysis` cùng phân tích requirement và chấm Readiness. Khác biệt: `qa-requirement-analysis` gắn với Qikify + tạo task Testlane, `analyze-req` product-agnostic. Nên gộp hoặc phân vai rõ trong `description`, không thì lúc gọi sẽ phân vân.

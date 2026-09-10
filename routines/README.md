# routines/

Cấu hình cloud routine (scheduled agent chạy trên cloud của Anthropic).

Mỗi file `.json` là body của `RemoteTrigger action=create`. Giữ ở đây để tái tạo được, vì API **không cho xoá** routine — xoá phải vào https://claude.ai/code/routines.

## Điều phải nhớ về cloud routine

| | |
|---|---|
| Chạy ở đâu | Cloud của Anthropic, session cô lập, git checkout riêng. **Không thấy máy mình** — không có file local, không có `~/.claude/skills/`, không có env var. |
| Chi phí | Tính vào subscription, **không** phải Claude API. Không cần Cloudflare. |
| Tần suất tối thiểu | **1 tiếng**. `*/30 * * * *` bị từ chối. |
| Múi giờ | Cron luôn là **UTC**. Asia/Saigon = UTC+7, nên trừ 7 giờ. `0 2 * * 1` = 9:00 sáng thứ Hai giờ VN. |
| MCP | **Chỉ dùng được claude.ai connector**, KHÔNG dùng được MCP cấu hình trong Claude Code (atlassian, testlane, chrome, playwright đều không attach được). Nối connector ở https://claude.ai/customize/connectors. |
| Prompt | Agent bắt đầu từ số 0, prompt phải **tự chứa** toàn bộ ngữ cảnh. |

## Điều kiện tiên quyết

1. **Nối GitHub account** — nếu không, `create` trả `HTTP 401: Connect your GitHub account before saving a routine that uses a GitHub repository`. Chạy `/web-setup` trong Claude Code, hoặc cài Claude GitHub App: https://claude.ai/code/onboarding?magic=github-app-setup
2. **Environment** — hiện dùng `Default` = `env_01WmFd3gGd417ZKTMH6zgkyh`.

## Cách tạo

Trong Claude Code, bảo Claude: *"tạo routine theo `routines/<tên>.json`"*, hoặc gọi `/schedule`.

## Kỷ luật: routine chỉ đọc

Mọi routine ở đây khai `allowed_tools` **không có `Write`/`Edit`** — cưỡng chế ở tầng tool chứ không chỉ dặn trong prompt. Lý do: agent tự update data thì sau này noise và mess, không quản lý được. Muốn ghi thì người chạy skill và xác nhận.

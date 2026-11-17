<!--
Khuôn báo cáo test gửi Dev — chị Nga chốt 2026-11-12 (khuôn A, theo build deploy + theo issue Jira).

TÊN FILE:  test-runs/<taskId>/<JIRA>-<build>.md
  - <JIRA>  = key issue Jira (QCO-1060), không phải taskId QA Hub.
  - <build> = version deploy đang test, viết thường, khoảng trắng → "-" (staging-checkout-2118, build-staging-117109b5).
  - Mỗi build một file. Dev deploy build mới → file mới; file cũ giữ nguyên (đã gửi Dev).
  - Cùng build: sau mỗi lô sonder, cập nhật đè chính file đó (số case, bug, nghi vấn, kết luận).
  - File build mới CHỈ ghi kết quả chạy trên build đó; bug cũ chỉ xuất hiện ở mục 2 (so với build trước) nếu đã retest / còn mở.
  - Chưa biết build → hỏi chị một câu trước khi tạo file, không đoán.

QUY ƯỚC:
  - Mọi TC-<KEY>-n là link: [TC-QCO-1186](https://qa-hub.ownego.com/test-cases/TC-QCO-1186).
  - Đầu mục đánh số 1, 2, 3; mục con thụt dưới số. Bỏ mục không có nội dung (giữ đánh số liền).
  - Không dán log thô / snapshot. Log + ảnh để ở file manual-run và evidence/.
  - Không ghi mật khẩu / token.
-->

# {JIRA} — {Tên issue Jira, nguyên văn}

**Build:** `{build}` · **Ngày:** {dd/mm/yyyy} (cập nhật sau lô {n}) · **QA:** Nga · **Jira:** [{JIRA}](https://ownego.atlassian.net/browse/{JIRA}) · **Task QA Hub:** [{taskId}](https://qa-hub.ownego.com/test-cases?task={taskId})

**Môi trường:** {staging / dev store, plan, app, locale, cổng thanh toán test}

**Phạm vi:** {phần đã test trên build này; phần KHÔNG test và vì sao}

**Build trước:** [{JIRA}-{build-cu}.md](./{JIRA}-{build-cu}.md) {bỏ dòng nếu là build đầu}

---

## 1. Kết luận

**{READY — đủ điều kiện pass staging | ALMOST — đủ điều kiện, còn lưu ý | NOT READY — chưa đủ điều kiện pass staging}**

| Test case | Tổng | Passed | Failed | Blocked | Skipped | Not-run |
|---|---|---|---|---|---|---|
| Tất cả | | | | | | |
| Trong đó Security / Performance | | | | | | |

- {Bug chặn release: BUG-nn (High) — 1 câu, ảnh hưởng bao nhiêu case}
- {Số bug Medium / Low}
- {Số case blocked — lý do chính}
- {Phần đã chạy ổn trên build này — 1–3 dòng}

## 2. So với build trước {bỏ mục nếu là build đầu}

| Bug | Build `{build-cu}` | Build `{build}` | Ghi chú |
|---|---|---|---|
| BUG-nn | To Do | ✅ Fixed (retest passed) | |
| BUG-nn | To Do | ❌ Còn lỗi (REOPENED) | {bước còn sai} |
| BUG-nn | — | 🆕 Mới | |

## 3. Bug đã report (QA Hub, status {To Do})

| Bug | Severity | Tóm tắt | Case |
|---|---|---|---|
| **BUG-nn** | **High** | | [TC-…](https://qa-hub.ownego.com/test-cases/TC-…) |

### BUG-nn · {tên ngắn} ({Severity})
1. {bước}
2. {bước}
3. {kết quả thực tế — số lần tái hiện (2/2)}

**Mong đợi:** {…}

**Data đang giữ trên store để Dev tái hiện — đừng xoá trước khi check:**

| Bug | Data |
|---|---|
| BUG-nn | {store · entry / record · giá trị} |

## 4. Nghi vấn chưa kết luận (cần Dev xem)

| Case | Quan sát | Câu hỏi |
|---|---|---|
| [TC-…](https://qa-hub.ownego.com/test-cases/TC-…) | | |

**Ngoài phạm vi {JIRA} — báo để Dev chuyển đúng chỗ:**
- {…}

## 5. Câu hỏi cho Dev / PO (đang chặn case)

| # | Câu hỏi | Chặn |
|---|---|---|
| 1 | {GAP-xx — …} | [TC-…](…) |

**Blocked vì môi trường (QA tự xử lý):** {…}

## 6. Sau khi Dev fix

- **BUG-nn** → QA chạy lại: [TC-…](…), …
- Các bug khác → retest đúng bước tái hiện ở mục 3.
- Dev check xong data ở mục 3 thì báo QA để dọn store.

Log chi tiết + ảnh: `test-runs/{taskId}/{file manual-run}`, `test-runs/{taskId}/evidence/` (máy QA).

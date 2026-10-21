# Quy trình tạo Context Change Request (CCR)

CCR là cầu nối giữa "có 1 (hoặc nhiều) ticket Jira đã ship / một thay đổi cần ghi nhận" và "canonical QA context (Product KB / Feature Profile / Checklist) được cập nhật đúng, đủ, không ai phải mở lại Jira lần nữa". Tài liệu này gồm 2 phần: **Phần A — quy trình soạn CCR** (dùng để tự làm tay hoặc giao cho một AI agent có quyền đọc Jira/canon), và **Phần B — template CCR** (điền trực tiếp vào đây, hoặc copy sang file riêng).

Quy trình này áp dụng cho **bất kỳ product/knowledge-base nào**, không riêng cho một hệ thống cụ thể.

## Việc này KHÔNG làm

- Không tự submit CCR lên bất kỳ hệ thống quản lý context nào (QA Hub hay tương đương) — chỉ tạo ra file CCR, người soạn/người gửi tự đính kèm và bấm Submit.
- Không tạo/sửa/comment/transition bất kỳ Jira issue nào — chỉ **đọc**.
- Không tự quét Jira tìm thêm ticket liên quan ngoài phạm vi được chỉ định.
- Không tự quyết authority/urgency thay con người, không tự chọn phe khi phát hiện mâu thuẫn với canon hiện tại, không publish gì vào knowledge base.
- Không bịa `object_key`/`feature_key` không có thật trong registry của knowledge base đích.
- Không nâng một mô tả/comment dev trong ticket thành "hành vi đã xác nhận đúng" (`CONFIRMED_EXPECTED` hay tương đương) — mặc định luôn là cần re-verify.

---

# Phần A — Quy trình 10 bước

## Vị trí trong luồng làm việc

1. **Soạn CCR** (tài liệu này) → tổng hợp từ Jira + canon hiện có, ra 1 file CCR hoàn chỉnh.
2. Người gửi review, trả lời các mục đánh dấu `[BẠN]`, tự đính kèm file vào task liên quan trên hệ thống quản lý context, bấm Submit.
3. Một agent/đội xử lý context (context builder) nhặt CCR đã submit và xử lý theo pipeline riêng của họ — **nằm ngoài phạm vi tài liệu này**.

## Bước 0 — Xác định repo/knowledge base đích

- Nếu knowledge base đích đã có sẵn template CCR riêng của họ (ví dụ `contracts/context-change-request.template.md`) — **luôn ưu tiên dùng cấu trúc của họ**, template ở Phần B chỉ là bản dự phòng khi họ chưa có.
- Xác định xem có truy cập được registry object (`_registry.json`), KB (`kb.json`), checklist, `feature-summary.md`, `manifest.json` của knowledge base đích hay không — đây là nguồn tra canon ở Bước 3.
- Không tra được canon (không có quyền/đường dẫn) → vẫn làm tiếp, nhưng ghi rõ "không tra được canon" trong CCR thay vì bịa hoặc bỏ qua.

## Bước 1 — Thu thập input

- Lấy đúng (các) Jira key/link được cung cấp. Nếu chỉ có mô tả bằng lời (không có ticket) — vẫn làm được, dùng thẳng mô tả đó làm "Quan sát được" nhưng ghi rõ nguồn là "mô tả trực tiếp", không phải Jira.
- **Không tự động tìm thêm ticket liên quan** (không tự search) — chỉ xử lý đúng ticket được chỉ định. Nghi ngờ có ticket liên quan khác → hỏi lại thay vì tự tìm.

## Bước 2 — Đọc kỹ từng ticket Jira (chỉ đọc)

Với mỗi ticket, lấy đầy đủ: `summary`, `description`, `issuetype`, `status`/`resolution`, ngày resolve/update, **toàn bộ comment** (không chỉ description — comment dev thường chứa "Context"/"Behaviour changes"/"Test cases", đây thường là nguồn quan trọng nhất), và link tới ticket/PR liên quan (ghi nhận, không cần đọc sâu).

**Bắt buộc tra test case liên quan** (phục vụ cột "Độ tin cậy" ở Bước 5): tìm xem đã có test case nào chạy đúng hành vi đang nói tới chưa, trong hệ thống quản lý test case đang dùng.
- Tìm theo ticket key, tên feature, và từ khoá mô tả hành vi — đừng chỉ tìm đúng ticket key vì test case hiếm khi map 1:1.
- Có test case đã chạy **PASS đúng hành vi đang claim** → ghi lại: id, kết quả, ngày chạy, build/version — đây là ứng viên cho cột "Độ tin cậy".
- Không tìm thấy, hoặc chỉ thấy test case chưa chạy/FAIL/không khớp → ghi thẳng "không có test case PASS phù hợp cho claim này".
- Không có quyền truy cập hệ thống test case → ghi "không tra được test case (không có quyền truy cập)" — khác với "đã tra và không có".

**Nguyên tắc chỉ-đọc tuyệt đối:** không bao giờ tạo/sửa/comment/transition/gắn label lên Jira issue nào. Việc "escalate" (nếu cần) luôn nằm TRONG nội dung file CCR, không bao giờ là một hành động ghi lên Jira.

## Bước 3 — Tra canon hiện tại (nếu tra được)

- Tìm đúng `object_key`/`feature_key` (hoặc alias gần đúng) trong registry. Không khớp gì → ghi thẳng, đừng bịa object mới.
- Tra KB, checklist, feature-summary liên quan bằng từ khoá rút từ ticket. Trích nguyên văn KB-id/check-id đang nói gì, không diễn giải lại.
- Lấy context version hiện tại của object đó (thường từ file manifest).
- Ghi lại chính xác từ khoá đã tra — để phân biệt "canon không có" với "chưa tra tới".

## Bước 4 — Xác định Phần 0 (cần mấy CCR)

Áp 4 câu hỏi ở Phần 0 của template cho toàn bộ ticket đầu vào. Cả 4 giống nhau cho tất cả ticket → 1 CCR duy nhất. Có ticket lệch (ví dụ 1 ticket cần dev trả lời trước, ticket khác explore được ngay) → tách CCR riêng, đừng gộp để phần dễ không bị kẹt theo phần khó.

Đây là **gợi ý**, không phải quyết định cuối — nêu rõ lý do đề xuất gộp/tách để người gửi tự xác nhận hoặc chỉnh lại (Bước 7).

## Bước 5 — Soạn "Phạm vi cần re-explore & ảnh hưởng ước tính" (phần quan trọng nhất)

Đây là phần khác biệt chính so với việc chỉ copy-paste ticket vào CCR. Với **mỗi** ticket/claim riêng biệt:

1. **Surface nào cần re-verify** — cụ thể (portal/api/storefront/db...), dựa theo loại thay đổi. Không ghi "tất cả" trừ khi có lý do thật.
2. **Vì sao chưa thể tin ngay** — mặc định "chỉ có mô tả/comment dev, chưa quan sát trực tiếp trên môi trường thật" trừ khi có bằng chứng khác.
3. **Object/feature/checklist nhiều khả năng bị ảnh hưởng.** Nếu một thay đổi có thể làm SAI (không chỉ THIẾU) một checklist/automation đang chạy — nêu rõ, đây là tín hiệu ưu tiên cao.
4. Nghi ngờ ranh giới object/feature hiện tại không hợp lý → nêu Ý TƯỞNG, không tự đặt tên object mới, để agent xử lý CCR quyết khi build KB thật.
5. **Độ tin cậy** — với mỗi dòng, ghi đúng **1 trong 3** trạng thái:
   - `ĐỦ TIN CẬY (test case PASS #id)` — chỉ khi có id + kết quả PASS + ngày chạy + build, và test case đó kiểm đúng hành vi đang claim.
   - `ĐỦ TIN CẬY (PO/Dev confirm: "quote" — link)` — chỉ khi có trích dẫn nguyên văn + link, xác nhận đúng hành vi đang claim (không tính comment mơ hồ như "chắc ổn", hay comment kỹ thuật thuần như "Ready to test").
   - `CHƯA ĐỦ — cần re-explore` — mọi trường hợp còn lại. **Screenshot/API capture tự chụp không bao giờ đủ điều kiện** cho "ĐỦ TIN CẬY", dù nhiều ảnh hay tự tin đến đâu.

Không để trống bất kỳ claim nào ở phần này — trống hoặc mơ hồ dễ bị hiểu nhầm là "không cần explore thêm".

## Bước 6 — Điền các mục còn lại đúng cấu trúc template

- **Mục 4.1 (ai xác nhận):** phân biệt rõ comment kỹ thuật dev tự viết ("Ready to test", "Resolution: Done") KHÔNG PHẢI là PO/business sign-off. Chỉ ghi "có xác nhận thật" khi có bằng chứng PO/spec/business rõ ràng.
- **Mục 4.2 (KHÔNG đề xuất điều gì):** bắt buộc điền cụ thể — số liệu tại thời điểm ship, tên object đề xuất, ranh giới feature đề xuất... đều KHÔNG được coi là đã duyệt.
- Không bao giờ tự nâng một quan sát/mô tả ticket thành hành vi đã xác nhận đúng, dù ticket ghi "Resolution: Done".

## Bước 7 — Xác nhận với người gửi các mục `[BẠN]`

Trước khi chốt file, hỏi rõ (không tự đoán):
- Phần 0: đồng ý số lượng CCR đề xuất chưa?
- Mục 4.1: có xác nhận PO/business thật nào ngoài Jira mà chưa biết không?
- Mục 4.4: mức độ gấp (HIGH/MEDIUM/LOW)?
- Bất kỳ chỗ nào đánh dấu "không rõ"/"không tra được" — có thông tin bổ sung không?
- Cột "Độ tin cậy" ghi "CHƯA ĐỦ — cần re-explore" mà người gửi tin là đã xác nhận rồi: **không tự đổi** thành "ĐỦ TIN CẬY" chỉ vì khẳng định miệng — hỏi lại để lấy đúng id test case PASS (kèm ngày + build) hoặc quote + link PO/Dev confirm. Chỉ nâng khi có trích dẫn đó trong tay.

## Bước 8 — Redact & tự kiểm

- Bỏ email/số điện thoại/tên khách hàng thật/token/cookie/credential khỏi toàn bộ nội dung. Tên nội bộ nhân viên trong comment Jira thường chấp nhận được, nhưng vẫn kiểm kỹ.
- Chạy đúng checklist "Tự kiểm trước khi gửi" ở cuối Phần B — đặc biệt: không còn placeholder `<<< ... >>>` sót lại, mỗi ticket/claim đều có dòng tương ứng trong bảng "Phạm vi cần re-explore & ảnh hưởng ước tính".

## Bước 9 — Ghi file & báo cáo

- Ghi mỗi CCR ra 1 file `.md` riêng (gợi ý tên: `CCR-<YYYY-MM-DD>-<slug-ngắn>.md`).
- Báo cáo ngắn gọn: số CCR đã tạo, tóm tắt loại request + object mỗi CCR, và nhắc rõ bước tiếp theo là **người gửi tự đính kèm file vào task trên hệ thống quản lý context và bấm Submit**.

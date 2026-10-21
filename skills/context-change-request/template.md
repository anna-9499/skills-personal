# Phần B — Template CCR (điền trực tiếp hoặc copy sang file riêng)

> Nếu knowledge base đích đã có template CCR riêng, dùng bản của họ thay vì bản này. Thay mọi `<<< PRODUCT >>>` bằng tên product thật, và xoá dòng hướng dẫn này khỏi file cuối cùng.

Dùng khi canonical QA context (Product KB / Feature Profile / Checklist) của `<<< PRODUCT >>>` **thiếu, sai, cũ hoặc mâu thuẫn** với thay đổi đã/sắp ship.

**Cách gửi:** điền file này (giữ nguyên cấu trúc mục `# Phần N`), đính kèm vào task liên quan trên hệ thống quản lý context của team, rồi bấm Submit. Việc submit là thao tác thủ công của con người.

Hệ thống nhận CCR thường không đọc hiểu nội dung — chỉ kiểm tra thô là không còn placeholder `<<< ... >>>` nào sót lại.

## Nhãn field

| Nhãn | Nghĩa |
|---|---|
| `[AGENT]` | Người/agent soạn CCR tự điền được từ Jira + canon đã tra. Người gửi chỉ cần soát lại. |
| `[BẠN]` | Cần phán đoán của con người — không tự quyết, phải hỏi người gửi. |

Những thứ **không cần hỏi người gửi**: context builder được phép mutate gì trên môi trường thật, dùng account nào để explore, có capture network/DB không — đó là chính sách của bên sở hữu môi trường đích.

**Không có thông tin thì ghi "không rõ".** Một chỗ trống được khai báo thì xử lý được; một chỗ trống bị lấp bằng phỏng đoán sẽ lan vào KB và vào mọi test case sinh ra sau đó.

---

## Phần 0 — Cần mấy CCR? `[BẠN xác nhận, AGENT đề xuất]`

Đơn vị của một CCR là **một thứ được giải quyết độc lập**, không phải một ticket Jira riêng lẻ. Nhiều ticket có thể gộp thành 1 CCR nếu cả 4 điều dưới đây giống nhau; tách nếu **ít nhất một** điều khác nhau:

| | Câu hỏi |
|---|---|
| Người gỡ | Context builder tự explore được, hay cần dev trả lời / PO quyết / chủ taxonomy quyết? |
| Điều kiện mở khoá | Đúng **một** thông tin hoặc **một** việc nào làm nó xong? |
| Vòng đời | Nếu request này bị huỷ, các ticket còn lại còn giá trị riêng không? |
| Artifact đích | Cùng KB của một object cụ thể, hay đụng tới registry/taxonomy chung? |

Đừng gộp quá tay: nhét "cần dev trả lời" chung với "chỉ cần đi explore lại" sẽ khiến phần explore được ngay phải chờ dev vô cớ.

---

## Phần 1 — Thấy gì

**Loại request** `[AGENT đề xuất, BẠN duyệt]`

`NEW_FEATURE` · `BEHAVIOR_CHANGE` · `PROFILE_GAP` · `CHECKLIST_GAP` · `STALE_CONTEXT` · `CONFLICT` · `CANON_HYGIENE`

**Loại:** `<<< ĐIỀN >>>`

**Object** `[AGENT]` — lấy từ registry của knowledge base đích, nếu có quyền truy cập

- Object: `<<< object_key >>>` · Feature: `<<< feature_key hoặc để trống >>>`
- Không khớp object nào, hoặc không tra được registry? Mô tả bằng lời. **Đừng bịa một object_key không có thật.**

**Quan sát được** `[AGENT]` — tổng hợp từ (các) ticket Jira, KHÔNG phải suy đoán

```
<<< Với mỗi ticket: key, tiêu đề, ngày resolve, tóm tắt hành vi thay đổi lấy từ description + comment
    (đặc biệt comment dạng "Context"/"Behaviour changes"/"Test cases" do dev tự viết) >>>
```

- Nguồn: `<<< vd: tổng hợp từ N ticket Jira đã Done, KHÔNG PHẢI quan sát trực tiếp trên môi trường thật >>>`
- Thấy mấy lần / xác nhận trực tiếp mấy lần: `<<< con số thật — tổng hợp Jira mà chưa tự verify thì ghi 0 >>>`

**Thử gì mà KHÔNG tái hiện / chưa thử gì** `[AGENT + BẠN]`

```
<<< nói thẳng những gì CHƯA được verify trực tiếp trên môi trường thật — "chưa thử" trung thực tốt hơn
    để người/agent xử lý CCR tưởng đã thử >>>
```

**Phạm vi cần re-explore & ảnh hưởng ước tính** `[AGENT]` — BẮT BUỘC, đây là phần quan trọng nhất

> Khác "Quan sát được" ở trên: không mô tả CÁI GÌ đã xảy ra, mà là **CẦN LÀM GÌ TIẾP**. Người/agent xử lý CCR đọc xong mục này phải biết ngay cần verify lại surface nào, và biết trước phạm vi ảnh hưởng dây chuyền.

Với MỖI ticket/claim riêng biệt trong "Quan sát được":

| Ticket / claim | Surface cần re-verify | Vì sao chưa thể tin ngay | Object/feature/checklist nhiều khả năng bị ảnh hưởng | Độ tin cậy |
|---|---|---|---|---|
| `<<< vd: PROJ-123 — thêm field X vào form Y >>>` | `<<< portal · api · storefront · db — ghi CỤ THỂ, không ghi "tất cả" nếu không có lý do >>>` | `<<< vd: chỉ có mô tả dev trong comment, chưa tự quan sát trên môi trường thật >>>` | `<<< object_key/feature_key/checklist_id nếu biết, hoặc "chưa rõ, cần tự đánh giá" >>>` | `<<< ĐỦ TIN CẬY (test case PASS #id) / ĐỦ TIN CẬY (PO/Dev confirm: "quote" — link) / CHƯA ĐỦ — cần re-explore >>>` |

- Một claim có khả năng làm SAI một checklist/automation đang publish (không chỉ THIẾU coverage) → nêu rõ checklist_id/mã check nghi ngờ, đây là tín hiệu ưu tiên cao hơn "gap" thông thường.
- Nghi ngờ ranh giới object hiện tại không còn hợp lý → nêu Ý TƯỞNG, **không tự quyết tên object_key mới**.
- Không chắc surface nào bị ảnh hưởng → ghi "chưa rõ, cần tự đánh giá", **không bỏ trống**.
- Cột "Độ tin cậy" quyết định người/agent xử lý CCR có được phép bỏ qua việc re-explore claim này hay không — chỉ ghi "ĐỦ TIN CẬY" khi có 1 trong 2, kèm trích dẫn cụ thể:
  - **Test case đã chạy PASS**: id + ngày chạy + build, kiểm đúng hành vi đang claim.
  - **PO/Dev confirm rõ ràng**: trích nguyên văn + link, xác nhận đúng hành vi đang claim.
  - Chỉ có screenshot/API capture tự chụp → bắt buộc ghi "CHƯA ĐỦ — cần re-explore", dù tin chắc đến đâu.

---

## Phần 2 — Thấy nó ở đâu `[AGENT]`

- **URL / ID cụ thể đã biết:** `<<< storefront URL, campaign/instance id, endpoint, Jira link — bất cứ thứ gì có >>>`
- **Trạng thái đối tượng lúc quan sát/lúc ticket mô tả:** `<<< ĐIỀN >>>`
- **Environment mô tả trong ticket gốc (không nhất thiết là môi trường sẽ dùng để re-explore):** `<<< staging | production | không rõ >>>`
- **Role liên quan:** `<<< vd: guest buyer | owner | staff — nếu ticket có nêu >>>`
- **Surface:** `portal` · `storefront` · `api` · `db`

---

## Phần 3 — Để không sinh conflict giả `[AGENT]`

> Phần lớn "conflict" phát sinh không phải mâu thuẫn thật, mà do hai quan sát đều đúng nhưng không ai ghi rõ chúng chạy trên build nào.

Với MỖI ticket:

- **Build / version / ngày deploy:** `<<< hoặc "không rõ" — đừng bỏ trống >>>`
- **Ngày resolve/update cuối:** `<<< YYYY-MM-DD >>>`
- **Đã ship chưa:** `<<< Resolution: Done/merged/deployed, hay chưa >>>`

**Context hiện đang nói gì** `[AGENT]` — tra canon TRƯỚC khi gửi

- Context version đang dùng: `<<< nếu tra được >>>`
- Canon hiện nói: `<<< trích nguyên văn KB-id/check-id liên quan, hoặc "không tìm thấy" >>>`
- Đã tra bằng từ khoá nào: `<<< liệt kê >>>`
- Không tra được canon → ghi rõ "không tra được — cần người/agent xử lý CCR tự tra lại".

---

## Phần 4 — Hai câu chỉ con người trả lời được `[BẠN]`

### 4.1 Có ai xác nhận đây là hành vi ĐÚNG không?

- Ai xác nhận: `<<< PO | Dev | spec | test case đã PASS | KHÔNG AI — chỉ là mô tả/comment của dev >>>`
- Ở đâu, ngày nào: `<<< vd: comment #xxx ngày yyyy-mm-dd, hoặc test case TC-xxx PASS ngày yyyy-mm-dd trên build yyy >>>`
- Họ xác nhận chính xác điều gì: `<<< trích nguyên văn, đừng diễn giải >>>`

> Comment kỹ thuật dev tự viết (kể cả "Ready to test", "Resolution: Done") **KHÔNG PHẢI** PO/business sign-off. Không ai xác nhận thật → knowledge vào context với nhãn "quan sát hiện tại" (chưa xác nhận), không dùng làm expected result.

### 4.2 KHÔNG đề xuất điều gì?

**Bắt buộc.** Liệt kê rõ những gì KHÔNG được coi là đã xác nhận/đã duyệt dù có trong ticket:

```
<<< vd: số liệu cụ thể dev ghi tại thời điểm ship, tên object_key đề xuất, ranh giới feature đề xuất, v.v. >>>
```

### 4.3 Đề xuất context nên nói gì `[AGENT soạn, BẠN duyệt]`

```
<<< viết như một câu sẽ nằm trong KB — mô tả hiện trạng cần re-verify, không khẳng định chắc chắn >>>
```

### 4.4 Mức độ gấp `[BẠN]`

`HIGH` (đang chặn test P0/P1) · `MEDIUM` (ảnh hưởng coverage) · `LOW` (cải thiện dần)

---

## Phần 5 — Evidence `[AGENT]`

Link Jira ticket / ảnh / response / HAR: `<<< ĐIỀN >>>`

> **Trước khi đính kèm: bỏ email, số điện thoại, địa chỉ, tên khách hàng thật, token, cookie, credential.** Tên nội bộ dev/support trong comment Jira thường chấp nhận được, nhưng vẫn kiểm kỹ.

---

## Tự kiểm trước khi gửi

`[BẠN]`:
- [ ] Đây thật sự là **một** thứ được gỡ độc lập (Phần 0)
- [ ] Đã trả lời mục 4.1 trung thực — kể cả khi câu trả lời là "không ai, chỉ là comment dev"
- [ ] Đã điền mục 4.2
- [ ] Evidence đã bỏ PII/token/credential

`[AGENT]`:
- [ ] Số lần xác nhận trực tiếp là con số thật, không làm tròn lên
- [ ] Đã ghi build/ngày resolve hoặc thừa nhận "không rõ" cho từng ticket
- [ ] Đã ghi rõ từ khoá đã tra canon (hoặc lý do không tra được)
- [ ] Mỗi ticket/claim trong "Quan sát được" đều có 1 dòng tương ứng trong "Phạm vi cần re-explore & ảnh hưởng ước tính"
- [ ] Cột "Độ tin cậy" của mỗi dòng đã ghi đúng 1 trong 3 trạng thái, có trích dẫn cụ thể khi ghi "ĐỦ TIN CẬY"
- [ ] Không còn placeholder `<<< ... >>>` nào sót lại trong file

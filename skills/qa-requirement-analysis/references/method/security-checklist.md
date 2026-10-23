# Security Testing Checklist — Shopify Apps & Mailtro

Nguồn: checklist của chị Nga (2026-10-24) gộp với các nhóm rút từ `cloudflare/security-audit-skill`.
Một file dùng chung:

| Ai đọc | Dùng để |
|---|---|
| `qa-requirement-analysis` (terra) | Viết mục 9 Security Considerations |
| `gen-testcase` (ore) | Biến mục 9 + mục khớp feature thành case `[Security]` |
| flint (review) | Soi bộ case thiếu Security ở đâu |
| sonder | Biết case nào cần chạy tay (sửa request) và cách retest bug security |
| Chị (tay) | Nhân bản Phần A + phần của app cho mỗi đợt release lớn; Phần D khi có sự cố / bản vá hạ tầng |

## Cách dùng

**Hai kiểu dùng:**

1. **Theo ticket** (terra / ore / flint): chọn đúng mục khớp feature qua *Cổng 4 câu* bên dưới.
   Mục **[P1]** của Phần A / B / C mà feature chạm tới → bắt buộc có case. Không ép đủ cả
   checklist cho một form đổi avatar.
2. **Theo release lớn** (chị chạy): nhân bản Phần A + phần của app (B hoặc C), chạy hết. Mục
   không áp dụng ghi rõ `N/A – lý do`, không bỏ trống.
3. **Sau sự cố / bản vá hạ tầng** (không đổi tính năng): chỉ chạy **Phần D** — kiểm nhanh header +
   smoke trên production.

**Mức ưu tiên:**

| Mức | Khi chạy | Thành case thế nào |
|---|---|---|
| **[P1]** | Bắt buộc trước release | Case priority High; vượt quyền / lộ dữ liệu / sai tiền ghi `Critical` ở Notes |
| **[P2]** | Khi tính năng chạm khu vực đó | Case Medium, nâng High nếu lộ dữ liệu người khác |
| **[P3]** | Định kỳ (mỗi quý, trước đợt review của Shopify) | **Không** viết case theo ticket — chị chạy tay hoặc skill `sec-perf-check`; flint không tính là thiếu case |

**Nguyên tắc test:**

- Luôn có **2 shop / workspace riêng** (Shop A, Shop B) và **ít nhất 2 vai trò** (Owner và
  Member / quyền thấp nhất). Preconditions của case ghi đủ cả hai phía.
- Không chỉ test qua UI: sửa request trực tiếp bằng DevTools (Network → Edit and Resend),
  Postman hoặc Burp Suite Community. Case có bước **sửa request** (body, header, token, method
  khác GET) ghi `Công cụ: DevTools/Postman` ở Preconditions — `sonder` tự gửi lại request đã sửa
  trong trang staging (`browser_evaluate`, tối đa 10 request / case). Webhook / App Proxy có chữ
  ký, OAuth callback, endpoint GDPR, server-to-server → sonder để `skipped`, chị chạy Postman.
- Chỉ test trên dev / staging, dev store và shop test (`shiki-perfect` được tính là shop test).
  Không chạy payload hay load test trên production hay shop của merchant thật.
- Chuỗi thử chỉ lấy từ bảng **Payload mẫu** cuối file. Không viết cách khai thác tiếp, không
  scanner chủ động ngoài ZAP baseline [P3] trên staging.
- Kiểm header / cookie / CSP / bundle của một màn hình → skill `sec-perf-check`, không viết
  thành case.

## Cổng 4 câu trước khi ghi một mục Security

Rút từ cách `cloudflare/security-audit-skill` lọc finding: **lệch checklist chưa phải lỗ hổng**.
Một mục chỉ vào mục 9 / thành case / thành finding "thiếu Security" khi trả lời đủ:

1. **Ai** làm — role thấp hơn, shop / workspace / công ty khác, buyer chưa đăng nhập, người
   đã bị gỡ quyền.
2. **Cái gì** được bảo vệ — dữ liệu, thao tác, tiền, cấu hình của ai.
3. **Đường đi khác** — không chỉ nút trên UI: URL dán thẳng, đổi id trên URL / payload, tab
   cũ, export, email, storefront, import, API, `/cart/add.js`.
4. **Kết quả đo được** — bị chặn ở đâu (mã lỗi, trang, thông báo nguyên văn), **và** không có
   dữ liệu nào lộ ra (UI, response, file, email).

Thiếu câu 1 hoặc 2 → không phải mục Security (feature không có bề mặt đó). Lớp khác đã chặn
cùng đường đi và đã có case → không thêm case "thiếu lớp thứ hai"; đó là gợi ý hardening cho
Dev, không phải case.

---

# Phần 0 — Theo loại feature

Dùng khi viết mục 9 cho một ticket: tìm loại feature, lấy mục khớp, rồi đối chiếu Phần A/B/C
để lấy mức P.

## Áp dụng cho hầu như mọi feature có backend

- **Phân quyền theo chiều ngang (IDOR):** đổi ID trong URL/payload sang bản ghi của user
  khác — có bị chặn không? Lỗ hổng phổ biến nhất và hay bị bỏ sót nhất.
- **Phân quyền theo chiều dọc:** user thường gọi thẳng API dành cho admin.
- **Kiểm tra quyền phía server:** ẩn nút trên UI không phải là kiểm soát. Gọi API trực tiếp.
- **Đúng quyền cho đúng rule:** thao tác bị chặn ở màn hình A có làm được ở màn hình B cùng
  hiệu quả không (bulk action, duplicate, import, API).
- **Xác thực:** truy cập khi chưa đăng nhập, token hết hạn, token của user đã bị vô hiệu hoá.
- **Rò rỉ dữ liệu trong response:** API trả thừa field (password hash, email người khác,
  ghi chú nội bộ) mà UI không hiển thị.
- **Thông báo lỗi:** stack trace, tên bảng, câu truy vấn lộ ra ngoài.
- **Mặc định khi thiếu cấu hình:** setting rỗng, feature flag tắt, plan hết hạn, app vừa
  cài chưa onboarding — mặc định là *đóng* (chặn / ẩn) hay *mở*?

## Form nhập liệu / tạo - sửa bản ghi

- Injection: SQL, NoSQL, command, template (`{{ }}`, Liquid, `${}`) — tuỳ tầng lưu trữ.
- XSS lưu trữ: nhập payload vào field text, xem lại ở màn hình khác và ở email/export.
- Mass assignment: gửi thêm field không có trên form (`role`, `isVerified`, `price`).
- Validation phía server tương đương phía client — bỏ qua UI, gọi thẳng API.
- CSRF nếu dùng cookie session.
- Chuỗi siêu dài, emoji / Unicode, khoảng trắng đầu cuối — lưu, hiển thị lại, không vỡ trang.

## Upload file

- Kiểm loại file theo nội dung (magic bytes) hay chỉ theo phần mở rộng?
- File thực thi đổi đuôi; `.html`; SVG chứa script; file nén giả.
- Path traversal / ký tự lạ trong tên file (`../`, `<script>`, Unicode).
- Giới hạn dung lượng; zip bomb nếu có giải nén.
- File tải lên có được phục vụ từ cùng domain và chạy được không?
- Ai được tải file về — URL có đoán / liệt kê được không? Còn mở được sau khi xoá bản ghi /
  gỡ quyền / uninstall không?

## Danh sách / tìm kiếm / lọc / export

- Tham số sắp xếp, lọc có bị dùng để inject vào truy vấn không (`' OR 1=1 --`, `{"$ne":null}`)?
- Bộ lọc có bỏ qua điều kiện phân quyền khiến lộ dữ liệu tenant khác không?
- **Tìm kiếm làm "máy dò":** kết quả, số đếm, autocomplete có để lộ bản ghi user không được
  xem (role khác, đã xoá, bản nháp) không?
- Export kèm field nhạy cảm, bản ghi đã xoá / nháp / tenant khác? Role thấp tự export được?
  Link tải có hạn, không mở được khi chưa đăng nhập?
- CSV injection: giá trị bắt đầu bằng `=`, `+`, `-`, `@` khi mở bằng Excel.

## Import / nhân bản / khôi phục

- Import đi qua **cùng** validation và phân quyền với form tạo tay?
- Import ghi đè bản ghi đang có (trùng email / SKU / handle), hoặc đổi trạng thái nhạy cảm
  (unsubscribed → subscribed) mà không xác nhận?
- Import tạo được bản ghi vào nơi user không có quyền ghi (qua cột id workspace / shop)?
- Duplicate / clone mang theo thứ không nên mang (người được chia sẻ, token, trạng thái duyệt)?

## Vòng đời: xoá, gỡ quyền, hết hạn

- **Xoá mềm còn lộ:** bản ghi đã xoá còn ở tìm kiếm, export, storefront, email đã lên lịch,
  báo cáo?
- **Gỡ quyền nhưng phiên cũ còn chạy:** member bị remove / hạ role khi đang mở tab — thao tác
  tiếp theo trên tab cũ bị chặn? Link mời / chia sẻ cũ còn dùng được?
- **Việc đã xếp hàng chạy quá hạn:** campaign / job / email đã lên lịch vẫn chạy sau khi tắt
  feature, gỡ app, hết plan, xoá đối tượng / domain?
- **Khôi phục đưa lại trạng thái sai:** restore / undo / bật lại có đưa lại quyền, giá,
  discount đã thu hồi?

## Logic nghiệp vụ / luồng nhiều bước

- **Nhảy bước:** mở thẳng URL bước 3 khi chưa xong bước 1–2; quay lại sau khi đã hoàn tất;
  gửi lại form của luồng đã xong (replay).
- **Lỗi giữa chừng:** bước 2 lỗi thì bước 1 có hoàn tác, hay để lại dữ liệu nửa vời?
- **Hai thao tác cùng lúc:** hai tab / hai user sửa cùng bản ghi, double click, áp cùng mã /
  quà hai lần.
- **Số học:** số âm, 0, thập phân, rất lớn (`999999999999`), chuỗi thay số, làm tròn tiền tệ.
- **Thời gian:** đúng thời điểm hết hạn, lệch múi giờ admin vs storefront / người nhận, lịch
  qua nửa đêm, đổi giờ mùa hè.

## Đăng nhập / đăng ký / đổi mật khẩu / OTP

- Brute force, rate limit, khoá tài khoản / captcha.
- User enumeration: thông báo khác nhau giữa "sai mật khẩu" và "email không tồn tại"; chênh
  thời gian phản hồi. Áp cả cho mời thành viên, đăng ký, quên mật khẩu.
- Token reset / verify: độ dài, thời gian sống, dùng một lần, gắn đúng tài khoản.
- OTP: số lần thử, thời gian sống, gửi lại vô hạn?
- Phiên cũ bị vô hiệu sau đổi mật khẩu / logout.
- **Open redirect** sau đăng nhập: `redirect`, `return_to`, `next`, `url` trỏ domain ngoài → bỏ qua.
- Logout rồi Back / mở URL cũ / dữ liệu còn trong localStorage → về login, không thấy dữ liệu.

## Thanh toán / tính tiền / điểm thưởng

- Giá và số tiền tính ở server / Shopify hay nhận từ client?
- Thao tác lặp: nhấn thanh toán hai lần, replay request — idempotency?
- Race condition: cùng một voucher / số dư ở hai request song song.
- Số âm, số rất lớn, làm tròn, sai lệch tiền tệ.
- Nhật ký audit cho mọi thay đổi tiền.

## Tích hợp bên thứ ba / webhook / API công khai

- Webhook đến xác thực chữ ký (HMAC)? Chống replay / gửi trùng?
- Secret / API key có lọt vào log, URL hoặc bundle frontend?
- SSRF khi hệ thống gọi URL do user cung cấp (webhook URL, ảnh theo link, import từ URL):
  `http://127.0.0.1`, `169.254.169.254`.
- Rate limit cho API công khai.
- Sự kiện đến hai lần hoặc sai thứ tự → không tạo bản ghi trùng, không lùi trạng thái.

## Gửi email / thông báo

- Nội dung user nhập (tên, subject, merge tag, custom field) render trong email không bị thực
  thi HTML / script / template; merge tag sai cú pháp không lộ tên biến nội bộ.
- Header injection ở from name / from email / reply-to (`\r\n`).
- Email gửi cho A không chứa dữ liệu của B / workspace khác.
- Link trong email (unsubscribe, xem trên web, xác nhận, tracking): sửa token / id → không
  thao tác được trên người khác, không thành open redirect.
- Giới hạn gửi: gửi test / gửi lại liên tục bị chặn; vượt quota plan bị chặn.

## Tính năng có AI (chỉ khi feature gọi model)

- Nội dung user / khách đưa vào (mô tả, email nhận, file) điều khiển được model làm việc ngoài
  phạm vi không (bỏ qua hướng dẫn, lộ prompt hệ thống, lộ dữ liệu tenant khác).
- Kết quả model hiển thị dạng text hay render HTML / link.
- Model tự thực hiện thao tác (gửi, xoá, sửa) mà không cần người xác nhận?

## Dữ liệu cá nhân / quyền riêng tư

- Field nào là PII; có bị ghi vào log, URL, pixel tracking không?
- Cần che (mask) khi hiển thị?
- Yêu cầu xoá theo quy định (GDPR) — xoá tới đâu?
- Ai trong nội bộ xem được, có ghi vết truy cập?

---

# Phần A — Chung cho mọi Shopify app (TEPO, QSC, QCO, DUOS)

Rủi ro lớn nhất của app nhiều shop là shop này đọc hoặc sửa được dữ liệu của shop khác, nên
nhóm A2 luôn là P1. Mailtro dùng các mục A tương ứng với **workspace thay cho shop**.

### A1. Cài đặt, xác thực và session

- [ ] [P1] Gọi API admin không có session token → 401, không trả dữ liệu.
- [ ] [P1] Session token hết hạn, bị sửa 1 ký tự hoặc ký sai → 401.
- [ ] [P1] Dùng session token của Shop A gọi API với `shop` = Shop B → bị từ chối.
- [ ] [P1] Uninstall app → token cũ không còn dùng được; cài lại không thấy dữ liệu "rác" của lần trước (nếu đã redact).
- [ ] [P2] Uninstall / tắt app → storefront không còn hành vi của app, không vỡ theme, không còn script / metafield sót.
- [ ] [P2] Luồng OAuth: sửa tham số `shop` thành domain lạ (`evil.com`) hoặc thiếu `hmac` → bị chặn.
- [ ] [P2] Tham số `state` / nonce không dùng lại được (replay URL callback).
- [ ] [P2] Admin page chỉ mở được trong Shopify Admin (embedded); mở trực tiếp URL app không lộ dữ liệu.

### A2. Cách ly dữ liệu giữa các shop (IDOR)

- [ ] [P1] Với mọi API có ID (`option_set_id`, `rule_id`, `customer_id`, `order_id`…): đổi ID sang bản ghi của Shop B → 403/404.
- [ ] [P1] Thử với cả GET, POST/PUT (sửa), DELETE và duplicate / export.
- [ ] [P1] API danh sách không trả bản ghi của shop khác khi thêm `?shop=` hoặc filter lạ.
- [ ] [P2] ID có đoán được không (số tăng dần) → ghi chú để Dev cân nhắc UUID (không phải case fail nếu đã kiểm quyền).
- [ ] [P2] File upload (ảnh, CSV) của Shop A không truy cập được từ Shop B hoặc người ngoài khi biết URL.

### A3. Webhook, App Proxy và GDPR

- [ ] [P1] Webhook không có header `X-Shopify-Hmac-Sha256` hoặc HMAC sai → 401, không xử lý.
- [ ] [P1] App Proxy: request thiếu `signature` hoặc sửa bất kỳ tham số nào sau khi ký → bị từ chối.
- [ ] [P2] Replay một webhook hợp lệ 2 lần → không tạo dữ liệu trùng (idempotent).
- [ ] [P1] `customers/data_request`, `customers/redact`, `shop/redact` trả 200 và thực sự xoá / ẩn dữ liệu đúng phạm vi.
- [ ] [P2] Storefront API qua App Proxy chỉ trả dữ liệu công khai cần thiết, không trả cấu hình nội bộ.

### A4. Phân quyền và scope

- [ ] [P2] App chỉ xin scope tối thiểu; mỗi scope có lý do dùng (đối chiếu `shopify.app.toml`).
- [ ] [P2] Staff account bị giới hạn quyền trong Shopify không làm được việc vượt quyền trong app (nếu app có kiểm tra).
- [ ] [P2] Tính năng theo gói (Free/Pro): gọi thẳng API tính năng Pro từ shop Free → bị chặn ở backend, không chỉ ẩn nút.

### A5. XSS và injection

- [ ] [P1] Mọi ô nhập ở admin (tên, label, mô tả, CSS class, tooltip) với payload XSS → hiển thị dạng text, không chạy script.
- [ ] [P1] Dữ liệu người mua nhập ở storefront (option, note, field) → không chạy script khi hiển thị lại ở cart, checkout, order admin, email.
- [ ] [P2] Trường "Custom CSS/HTML/JS" (nếu có): chỉ admin shop dùng được, không lộ sang shop khác.
- [ ] [P2] Ô tìm kiếm / filter với `' OR 1=1 --`, `{"$ne":null}` → không lỗi 500, không trả dữ liệu thừa.
- [ ] [P2] Tên file upload chứa `../`, `<script>`, Unicode lạ → được làm sạch.
- [ ] [P2] Upload file sai định dạng (`.html`, `.svg` có script, `.exe` đổi đuôi) hoặc quá dung lượng → bị chặn.

### A6. Dữ liệu số, giá và logic nghiệp vụ

- [ ] [P1] Sửa giá, % giảm giá, số lượng ở client (DevTools, sửa request) → backend / Shopify tính lại đúng.
- [ ] [P1] Số âm, 0, thập phân, số rất lớn (`999999999999`), chuỗi thay số → bị validate.
- [ ] [P2] Gửi cùng request nhiều lần liên tiếp (double click, race condition, hai tab) → không áp giảm giá / quà 2 lần.
- [ ] [P2] Đổi số lượng / variant / địa chỉ **sau khi** điều kiện đã đạt hoặc rule đã chạy → điều kiện được xét lại.

### A7. Lộ thông tin

- [ ] [P1] Không có API secret, private token, key bên thứ ba trong JS bundle storefront / theme extension (search `secret`, `token`, `key`).
- [ ] [P2] Script / JSON nhúng trên storefront (`window`, JSON trong trang) không chứa dữ liệu admin: ghi chú nội bộ, rule ẩn, danh sách khách, key.
- [ ] [P2] Lỗi 4xx/5xx không trả stack trace, câu SQL, đường dẫn server.
- [ ] [P2] Response API không trả trường thừa (email merchant, token, cấu hình nội bộ).
- [ ] [P2] Log / console trình duyệt không in token hay dữ liệu khách hàng.
- [ ] [P3] Header bảo mật: HTTPS bắt buộc, `Content-Security-Policy` có `frame-ancestors` đúng Shopify admin.

### A8. Giới hạn và phụ thuộc

- [ ] [P2] API công khai (App Proxy, storefront) có rate limit; spam 100 request/phút không làm sập app (chỉ staging).
- [ ] [P3] `npm audit` (hoặc tương đương), ghi lại lỗ hổng High/Critical.
- [ ] [P3] CORS không để `*` cho API cần xác thực.

---

# Phần B — Bổ sung theo từng app Shopify

Chạy thêm sau Phần A, tập trung vào chỗ app nhận dữ liệu người mua hoặc thay đổi giá. Vẫn
đối chiếu business rule / inventory của app — hành vi "đúng" lấy theo rule, không theo checklist.

### B1. Tepo — Custom Product Options

- [ ] [P1] Giá add-on (option có phí): sửa `price` / variant ID của add-on trong request add-to-cart → giá ở cart / checkout vẫn đúng cấu hình.
- [ ] [P1] Bỏ qua option bắt buộc bằng cách gọi thẳng `/cart/add.js` → hành vi được ghi nhận rõ (chặn, hoặc đơn vẫn hợp lệ theo business rule).
- [ ] [P1] Text box, textarea, line item property chứa payload XSS → hiển thị an toàn ở cart, order admin, email xác nhận.
- [ ] [P2] File upload của người mua: chặn file thực thi, SVG có script, quá dung lượng; link file không liệt kê được (no directory listing).
- [ ] [P2] Conditional logic: ẩn option ở UI nhưng gửi giá trị option bị ẩn qua request → không tính phí sai.
- [ ] [P2] Giá trị dropdown / swatch ngoài danh sách cho phép → bị từ chối hoặc bỏ qua.
- [ ] [P2] Giới hạn ký tự và số lượng (min/max) kiểm ở backend, không chỉ ở widget.

### B2. Slide Cart Drawer (QSC)

- [ ] [P1] Free gift theo ngưỡng: thêm quà rồi giảm giỏ dưới ngưỡng → quà bị gỡ hoặc tính tiền; không giữ quà miễn phí.
- [ ] [P1] Thêm quà trực tiếp qua `/cart/add.js` với variant quà → không được miễn phí khi không đủ điều kiện.
- [ ] [P1] Ô nhập mã giảm giá, cart note: payload XSS hiển thị an toàn trong drawer.
- [ ] [P2] Upsell / cross-sell: sửa variant ID sang sản phẩm khác hoặc ẩn / nháp → không thêm được với giá upsell.
- [ ] [P2] Bấm nhanh liên tục "Add" quà / upsell, hoặc hai tab (race condition) → không nhân đôi ưu đãi.
- [ ] [P2] Script drawer không lộ cấu hình nội bộ (rule, key) trong `window` object hay JSON trang.

### B3. Checkout Customizer (QCO)

- [ ] [P1] Custom field ở checkout (text, checkbox, date): payload XSS hiển thị an toàn ở order admin, thông báo, email.
- [ ] [P1] Field bắt buộc bị bỏ qua bằng cách sửa request / extension state → validation phía Shopify Function / backend vẫn chặn.
- [ ] [P1] Rule ẩn / đổi tên / sắp xếp phương thức thanh toán, vận chuyển: không chọn được phương thức đã bị ẩn bằng cách sửa request.
- [ ] [P2] Đổi giỏ hoặc địa chỉ sau khi rule đã chạy → rule được áp lại, phương thức đã ẩn không hiện lại sai.
- [ ] [P2] Function input không tin cart attribute do người mua tự sửa (vd. `customer_type=vip`).
- [ ] [P2] Banner / nội dung tuỳ biến do merchant nhập: HTML / script bị làm sạch.
- [ ] [P2] Cấu hình theo market / khách hàng: khách thường không thấy nội dung hoặc phương thức chỉ dành cho B2B / VIP.

### B4. Duos B2B (DUOS)

- [ ] [P1] Khách B2B công ty A không xem / đặt được theo price list, catalog, đơn hàng của công ty B (đổi company / location ID).
- [ ] [P1] Khách thường (chưa duyệt B2B) không xem được giá sỉ qua API, App Proxy hoặc xem source trang.
- [ ] [P1] Sửa giá sỉ, mức chiết khấu, min order quantity trong request → backend / Shopify tính lại đúng.
- [ ] [P1] Form đăng ký B2B: XSS trong tên công ty, mã số thuế, địa chỉ hiển thị an toàn ở admin duyệt hồ sơ.
- [ ] [P2] Tự sửa trạng thái hồ sơ (pending → approved) hoặc tag khách hàng qua request → bị chặn.
- [ ] [P2] Quote / draft order: không sửa được giá trong quote đã duyệt; link quote không đoán được.
- [ ] [P2] Net terms / thanh toán sau: không bật được cho tài khoản chưa được cấp; không vượt hạn mức công ty.
- [ ] [P2] File đính kèm hồ sơ (giấy phép kinh doanh) chỉ admin shop đó tải được.

---

# Phần C — Mailtro (MTRO)

Mailtro có tài khoản riêng, team nhiều vai trò và gửi email ra ngoài, nên ngoài Phần A cần
thêm xác thực người dùng, phân quyền team và chống lạm dụng gửi mail. **Workspace đóng vai
trò như "shop"** trong các mục cách ly dữ liệu — cô lập workspace là nhóm quan trọng nhất.

### C1. Signup, login và tài khoản

- [ ] [P1] Login sai mật khẩu nhiều lần → khoá tạm / captcha; thông báo lỗi không tiết lộ email có tồn tại hay không.
- [ ] [P1] Signup / forgot password với email đã tồn tại → thông báo trung tính, không lộ tài khoản.
- [ ] [P1] Link reset password và verify email: dùng 1 lần, có hạn, không dùng được cho tài khoản khác.
- [ ] [P1] Logout hoặc đổi mật khẩu → session cũ trên thiết bị khác hết hiệu lực.
- [ ] [P2] Chính sách mật khẩu tối thiểu (độ dài, không cho mật khẩu quá phổ biến).
- [ ] [P2] Cookie session có `HttpOnly`, `Secure`, `SameSite` (kiểm bằng `sec-perf-check`).
- [ ] [P2] Đổi email tài khoản yêu cầu xác thực lại (mật khẩu hoặc link gửi email cũ).
- [ ] [P2] Không có open redirect ở `redirect` / `next` sau login.

### C2. Team và phân quyền

- [ ] [P1] Ma trận vai trò: với mỗi vai trò (Owner, Admin, Member, Viewer…), gọi thẳng API / dán thẳng URL của hành động không được phép → 403.
- [ ] [P1] Member không tự nâng quyền của mình hoặc người khác qua request (sửa `role`); Admin không tự thành Owner.
- [ ] [P1] Thành viên bị xoá khỏi team → mất quyền ngay, kể cả session / tab đang mở.
- [ ] [P1] Không ai xoá hoặc hạ quyền được Owner cuối cùng của workspace.
- [ ] [P2] Link mời: hết hạn, dùng 1 lần, bị thu hồi thì hết hiệu lực, không dùng được với email khác email được mời.
- [ ] [P2] Người thuộc nhiều workspace: đổi `workspace_id` / slug trong request hoặc URL → chỉ vào workspace mình là thành viên; chuyển qua lại không lẫn dữ liệu.

### C3. Sending domain và chống giả mạo

- [ ] [P1] Không gửi campaign / automation từ domain chưa xác thực (SPF/DKIM chưa pass).
- [ ] [P1] Workspace B không thêm và xác thực được domain đã thuộc workspace A.
- [ ] [P1] From name, from email, reply-to: chặn ký tự xuống dòng (`\r\n`) — header injection.
- [ ] [P2] Không cho from email thuộc domain công cộng / không sở hữu (gmail.com, domain người khác).
- [ ] [P2] Xoá domain → campaign / automation đang dùng domain đó dừng hoặc báo lỗi rõ ràng.

### C4. Contacts, import và export

- [ ] [P1] IDOR: đổi `contact_id`, `segment_id`, `list_id` sang workspace khác → 403/404.
- [ ] [P1] Import CSV có giá trị bắt đầu bằng `=`, `+`, `-`, `@` → export mở bằng Excel không chạy công thức.
- [ ] [P1] Export contacts chỉ cho vai trò được phép; link tải có hạn, không mở được khi chưa đăng nhập.
- [ ] [P2] Import file rất lớn, sai định dạng, file nén giả → bị chặn hoặc xử lý an toàn, không treo hệ thống.
- [ ] [P2] Contact field tuỳ chỉnh chứa payload XSS → an toàn ở danh sách, chi tiết contact, segment preview.
- [ ] [P2] Segment filter với giá trị lạ (`' OR 1=1`, JSON operator) → không lỗi 500, không trả contact ngoài điều kiện.
- [ ] [P2] Contact đã unsubscribe / suppressed không bị import đè thành subscribed nếu không có xác nhận.

### C5. Templates và nội dung email

- [ ] [P1] Template HTML import / editor: script, `onerror`, link `javascript:` không chạy trong preview của app.
- [ ] [P1] Merge tag với giá trị contact chứa HTML / script → được escape khi render email và preview.
- [ ] [P2] Template injection: `{{ 7*7 }}`, `{% %}`, `${}` trong tên contact / field → không bị thực thi.
- [ ] [P2] Saved block, template của workspace A không hiển thị / duplicate được từ workspace B.
- [ ] [P2] Ảnh upload vào template: chặn SVG có script, quá dung lượng; URL ảnh không lộ dữ liệu nội bộ.
- [ ] [P2] Chèn ảnh / link từ URL ngoài: app không fetch địa chỉ nội bộ (`http://127.0.0.1`, `169.254.169.254`) — SSRF.

### C6. Campaign và automation

- [ ] [P1] Gửi test email có rate limit, không dùng để spam địa chỉ bất kỳ hàng loạt.
- [ ] [P1] Campaign chỉ gửi tới contact của workspace đó, đúng segment; contact unsubscribed / bounced / suppressed không nhận mail.
- [ ] [P1] Không sửa được campaign đã gửi / đang gửi qua request (nội dung, danh sách nhận).
- [ ] [P2] Campaign / automation đã lên lịch không chạy sau khi xoá list / segment, gỡ quyền người tạo hoặc hết plan (theo business rule).
- [ ] [P2] Automation trigger từ webhook / sự kiện Shopify: event giả mạo (sai HMAC, sai shop) không kích hoạt flow.
- [ ] [P2] Automation không gửi lặp vô hạn (flow tự trigger lại chính nó).
- [ ] [P2] Report campaign / automation chỉ xem được trong workspace của mình.

### C7. Unsubscribe, preference page và tracking link

- [ ] [P1] Link unsubscribe chỉ huỷ đúng contact đó; sửa token / ID trong link không huỷ được người khác.
- [ ] [P1] Preference page không lộ email / thông tin contact khác khi đổi tham số.
- [ ] [P1] Tracking link (click redirect) không bị dùng làm open redirect tới domain tuỳ ý.
- [ ] [P2] Header `List-Unsubscribe` (và one-click) có trong email marketing và hoạt động đúng.
- [ ] [P2] Pixel mở mail / link click không chứa email thô hay dữ liệu cá nhân trong URL.

### C8. Brand guideline, API và MCP

- [ ] [P2] Brand guideline (logo, màu, font, URL): URL `javascript:` hoặc payload XSS → bị chặn.
- [ ] [P1] API key / MCP token chỉ truy cập đúng workspace được cấp; thu hồi xong là hết hiệu lực.
- [ ] [P1] Token không hiển thị lại đầy đủ sau khi tạo, không xuất hiện trong log hay URL.
- [ ] [P2] Hành động qua API / MCP tuân theo cùng phân quyền như UI (Member không gọi được API dành cho Admin).
- [ ] [P2] API có rate limit và trả lỗi rõ ràng khi vượt.
- [ ] [P2] Tính năng AI / MCP (nếu có): nội dung contact / email đưa vào không điều khiển được model làm thao tác ngoài phạm vi hay lộ dữ liệu workspace khác.

---

# Phần D — Kiểm nhanh sau sự cố / bản vá hạ tầng

Dùng khi BE / DevOps vá **hạ tầng chung** (lỗ hổng ngôn ngữ như PHP, server, WAF, Cloudflare,
cấu hình session / upload), **không đổi tính năng**, và team cần xác nhận nhanh trên production
rằng (1) lớp bảo vệ đã lên, (2) bản vá không mở lại lỗ cũ (debug, file nhạy cảm, CORS, auth), và
(3) app vẫn chạy. **Không** chạy cả Phần A/B/C — đó là việc của release lớn. Mẫu theo sự cố PHP
vulnerability 2026-10 (comment của tinhnt trong thread `#C0AB1UQ6JP8`).

Nếu bản vá **có** đổi code (logic auth, upload, phân quyền) → chạy D rồi thêm các nhóm A/B/C
chạm tới phần đổi.

**Script:** `hae/bin/prod-quick-check.sh [--only header,https,errors,files,cors,api,js] [KEY …]`
chạy D1–D7. Thụ động: chỉ HEAD / GET, không đăng nhập, không gửi data, mỗi host ~15 request theo
**danh sách cố định** (không dò, không scanner). Giá trị cookie / token bị che. Hae tự chạy được
(không mở browser, không đụng data); lần đầu trên production cho một app mới → hỏi chị trước.

| Mục | Kiểm gì | Cách | Lấy từ |
|---|---|---|---|
| D0 | Hỏi BE trước khi check | tay | — |
| D1 | Header, HTTPS, CSP | script | A7 |
| D2 | Cookie phiên | script (+ DevTools) | C1, A1 |
| D3 | Trang lỗi không lộ thông tin | script | A7 |
| D4 | File nhạy cảm không mở được | script | Obvious things (`cloudflare/security-audit-skill`) |
| D5 | CORS | script | A8 |
| D6 | API không token / token sai | script (cần endpoint) | A1 |
| D7 | Secret / source map trong JS | script | A7 |
| D8 | Smoke chức năng | sonder / tay | — |
| D9 | Chỉ staging / chạy tay | sonder / tay | A5, C3 |
| D10 | Báo lại trong thread | Hae soạn, chị dán | — |

### D0. Trước khi check

- [ ] Hỏi BE trong thread: vá gì, app nào, đã lên production chưa, có **biện pháp tạm** nào
  (tắt tính năng, siết WAF, chặn upload…) và đã gỡ chưa. Ví dụ sự cố PHP: tạm tắt
  `session.upload_progress`, sau đó đã revert khi lên bản PHP mới.
- [ ] Liệt kê đủ app bị ảnh hưởng (cả app ngoài 5 app của mình nếu dùng chung hạ tầng) và chia
  người check, tránh hai người check trùng.

### D1. Header, HTTPS, CSP

- [ ] Có Cloudflare / WAF đứng trước (`server: cloudflare`, có `cf-ray`).
- [ ] Không lộ phiên bản ngôn ngữ / framework ra header (`X-Powered-By`, `X-PHP-*`, `X-Generator`).
- [ ] `http://` chuyển sang `https://` (301 / 308); ghi nhận domain có / không có HSTS.
- [ ] Trang nhúng trong Shopify admin (`embedded.*`, `admin.*`): CSP `frame-ancestors` chỉ cho
  `admin.shopify.com` + `*.myshopify.com`, không `*`.

### D2. Cookie phiên

- [ ] Cookie session (`*_session`, `mailtro-session`…): `Secure` + `HttpOnly` + `SameSite`.
  `XSRF-TOKEN` không HttpOnly và `__cf_bm` SameSite=None là đúng thiết kế.
- [ ] Domain mà request không đăng nhập không trả cookie (nền Qikify `*.qikify.com`) → đăng nhập
  app rồi xem DevTools → Application → Cookies, chỉ ghi tên + cờ.

### D3. Trang lỗi không lộ thông tin

Rủi ro số một khi đổi bản PHP / cấu hình: `display_errors` hoặc `APP_DEBUG` bị bật lại.

- [ ] Đường dẫn không tồn tại và request API thiếu / sai tham số → không có stack trace, đường dẫn
  server (`/var/www/…`), câu SQL (`SQLSTATE`), trang debug Laravel (`Whoops`, `Ignition`),
  `Fatal error` / `Warning` của PHP.

### D4. File nhạy cảm không mở được

- [ ] `/.env`, `/.git/config`, `/phpinfo.php`, `/info.php`, `/composer.json`,
  `/storage/logs/laravel.log` → 403 / 404, hoặc 200 nhưng là trang index (SPA), không phải nội
  dung file thật. Deploy lại server / image mới hay làm lộ các file này.

### D5. CORS

- [ ] Request kèm `Origin: https://evil.test` → không được phản chiếu đúng origin đó kèm
  `Access-Control-Allow-Credentials: true`; không `*` + credentials.

### D6. API không token / token sai

- [ ] 2–3 API chính mỗi app (GET), không kèm token và kèm token sai → 401 / 403 / 419 hoặc chuyển
  về login; body không có dữ liệu. Middleware auth chạy trên PHP — đổi bản PHP có thể làm hỏng.
  Endpoint điền ở hàm `api_endpoints_of` trong script (lấy từ DevTools lúc smoke, hoặc hỏi Dev).

### D7. Secret và source map trong JS

- [ ] JS cùng host / `cdn.qikify.com` mà trang nạp không chứa chuỗi giống secret (`shpss_`,
  `shpat_`, `sk_live_`, `AKIA…`, private key, `client_secret`, `DB_PASSWORD`, `APP_KEY`). Build
  lại sau khi vá có thể đóng gói nhầm biến môi trường.
- [ ] Source map (`.js.map`) công khai → ghi nhận, báo Dev (lộ mã nguồn; không phải lỗi của bản vá).

### D8. Smoke chức năng sau bản vá

Production thật (store / workspace của team, `shiki-perfect` cho app Shopify): người chạy tay, hoặc
`sonder` trên `shiki-perfect` (Mailtro production bị hook chặn — chị chạy tay hoặc tự mở override).

- [ ] Đăng nhập / session bình thường, app load trong Shopify admin (embedded) và portal.
- [ ] API chính trả 200, không có 500; WAF **không chặn nhầm** thao tác thường (lưu setting, upload,
  bulk action, import).
- [ ] Tính năng chạm vào biện pháp tạm (ví dụ upload file khi từng tắt upload progress) chạy lại
  bình thường.
- [ ] Storefront / SDK / widget của app hiển thị và hoạt động trên store test.
- [ ] Install mới, uninstall, reinstall app.
- [ ] Upgrade / downgrade gói (người chạy tay — agent bị cấm billing).
- [ ] Mailtro: gửi test email tới địa chỉ của team, nhận được.

### D9. Chỉ chạy trên staging / chạy tay

- [ ] **Upload file `.php` đổi đuôi** (ảnh `.jpg` chứa `<?php echo 'qa'; ?>`, `shell.php.jpg`,
  `.phtml`) → bị chặn, hoặc lưu được nhưng mở URL file **không** chạy code (trả về nguyên văn /
  tải xuống). Đúng kiểu tấn công của sự cố PHP (php2shell). **Không bao giờ chạy trên production**
  — lọt là tự thử RCE trên server thật. `sonder` chạy trên staging.
- [ ] Mailtro, khi bản vá chạm phần gửi mail: `dig TXT <domain gửi>` (SPF), `dig TXT _dmarc.<domain>`
  (DMARC) đọc DNS thụ động + gửi một mail tới mail-tester.com, điểm không tụt so với trước.

### D10. Báo lại

Trả lời trong thread của sự cố theo khuôn dưới (người dán — agent không post Slack):

```
@<BE phụ trách> Em đã check bản fix trên production <app…>:
*1. Header & cấu hình*
• <domain…>
• Có Cloudflare/WAF đứng trước · không lộ phiên bản <ngôn ngữ> ra header · http → https
• Cookie session: Secure + HttpOnly + SameSite (<app…>)
• Trang lỗi không lộ stack trace / debug · không mở được .env, .git, phpinfo · CORS không mở cho origin lạ
• API gọi không token → 401 (<app…>) · JS không chứa secret
*2. Smoke chức năng sau bản fix*
• Đăng nhập/session, API chính 200, không 500, WAF không chặn nhầm
• Install/uninstall/reinstall, upgrade/downgrade pricing ok
• <app/phần chưa check được + lý do>
```

Không ghi version, token, IP nội bộ, đường dẫn server hay log Sentry vào thread public. Có ❌ ở
D3 / D4 / D7 → **không** ghi chi tiết vào thread; báo riêng BE phụ trách (Critical theo bảng mức độ).

---

# Payload mẫu và công cụ

Chỉ dùng bộ payload ngắn dưới đây, chỉ trên shop test và dev / staging. Đây là chuỗi thử để
**nhìn thấy** cơ chế chặn có chạy không — không mở rộng thành khai thác.

| Loại | Payload | Kết quả mong đợi |
| --- | --- | --- |
| XSS cơ bản | `<script>alert(1)</script>` | Hiển thị đúng chuỗi, không popup |
| XSS qua thuộc tính | `<img src=x onerror=alert(1)>` | Không popup, ảnh vỡ không chạy script |
| XSS qua link | `javascript:alert(1)` | Link bị chặn hoặc không click được |
| XSS thoát thuộc tính | `"><svg onload=alert(1)>` | Không phá vỡ HTML |
| SQL / NoSQL | `' OR 1=1 --` · `{"$ne":null}` | Không lỗi 500, không trả dữ liệu thừa |
| Template injection | `{{7*7}}` · `${7*7}` · `{% raw %}` | Hiển thị nguyên văn, không ra `49` |
| CSV injection | `=HYPERLINK("http://evil.test","x")` | Mở bằng Excel không thành công thức |
| Header injection | `Test\r\nBcc: a@evil.test` | Bị chặn hoặc ký tự xuống dòng bị loại |
| Path traversal | `../../etc/passwd` (trong tên file) | Tên file được làm sạch |
| Open redirect | `?redirect=https://evil.test` | Không chuyển sang domain ngoài |

Lưu ý khi chạy bằng agent: `alert()` mở dialog chặn trình duyệt — sonder / Playwright gặp
dialog thì ghi nhận là **XSS đã chạy** (fail), đóng dialog rồi đi tiếp.

**Công cụ:** DevTools (Network → Edit and Resend) để sửa request; Postman hoặc Burp Suite
Community để gửi lại request với token / ID khác; OWASP ZAP baseline scan cho staging [P3];
`npm audit` cho dependency [P3]; mail-tester.com để kiểm SPF / DKIM / DMARC của email Mailtro.

---

# Viết thành case

- Title: `[Security] {Ai} {làm gì qua đường nào} → {bị chặn / hiển thị dạng text}`.
- Preconditions nêu đủ **hai** phía: tài khoản thấp quyền / Shop B / workspace B **và** bản ghi
  cần bảo vệ (của ai, tạo ra sao). Có bước sửa request → thêm `Công cụ: DevTools/Postman`.
- Test data: payload lấy nguyên văn từ bảng Payload mẫu.
- Expected trả lời câu 4 của cổng: chặn ở đâu (mã lỗi 401/403/404, trang, thông báo nguyên
  văn) **và** không có dữ liệu bị bảo vệ trong trang, response, file, email.
- Priority theo mức P (bảng "Mức ưu tiên"); Notes ghi mã mục checklist (vd. `Checklist A2`,
  `C7`) để flint và chị lần lại được.
- Một nguyên nhân, nhiều đường đi (URL, export, API) → một case cho mỗi đường đi **khác cách
  chặn**; cùng cách chặn thì gộp. Mục A2 "thử với GET / PUT / DELETE / duplicate" → gộp vào
  steps của một case nếu cùng màn hình.

# Mức độ bug security và báo bug

Bug Critical / High chặn release cho đến khi được sửa hoặc có quyết định chấp nhận rủi ro bằng
văn bản từ Lead / PO.

| Mức độ | Ví dụ | Xử lý |
| --- | --- | --- |
| Critical | Đọc / sửa dữ liệu shop hoặc workspace khác; lộ API secret; chiếm tài khoản; gửi mail từ domain không sở hữu | Báo ngay Lead + Dev phụ trách, chặn release |
| High | XSS lưu trữ (stored) ở admin / storefront; vượt quyền theo vai trò; sửa giá thành công; unsubscribe được người khác | Chặn release |
| Medium | XSS phản chiếu cần thao tác người dùng; thiếu rate limit; lộ thông tin trong lỗi; open redirect | Sửa trong sprint kế tiếp |
| Low | Thiếu header bảo mật; ID đoán được nhưng đã kiểm quyền; thông báo lỗi lộ email tồn tại | Đưa vào backlog |

**Khi báo bug security** (người hoặc `sonder` khi được phép `report_bug`):

- Đặt mức độ theo bảng trên, gắn label `security` (Jira — chị làm; QA Hub ghi trong title
  `[Security]`). Không ghi token, mật khẩu, API key thật vào QA Hub, Jira hay Slack public —
  che bằng `***`.
- Ghi đủ: request gốc, request đã sửa (đã che token), response nhận được, tài khoản / vai trò
  và shop / workspace dùng để test.
- Critical / High: issue ở chế độ hạn chế người xem (nếu project hỗ trợ), báo trực tiếp, không
  thảo luận ở kênh chung. Agent không announce — chị quyết.
- Sau khi Dev sửa: **retest cả case gốc và các biến thể** — đổi method, đổi sang ID khác, đổi
  vai trò. Một biến thể còn lỗi là REOPENED.

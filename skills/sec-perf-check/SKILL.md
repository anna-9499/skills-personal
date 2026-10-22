---
name: sec-perf-check
description: Kiểm tra security + performance của một app đang test (Tepo, Slide Cart Drawer, Checkout Customizer, Duos B2B, Mailtro) trên staging hoặc production, xuất báo cáo trong chat + file local. CHỈ chạy khi người dùng gọi đích danh /sec-perf-check.
disable-model-invocation: true
---

# Security + Performance check

Chỉ chạy khi chị gọi `/sec-perf-check`. Không tự kích hoạt, không được agent khác gọi thay.

Cú pháp: `/sec-perf-check <KEY> <URL> [--env staging|production] [--scope security|perf|all] [--role owner|admin|member]`
Thiếu `<KEY>` hoặc `<URL>` → hỏi **một câu** gộp. Không đoán URL.

## 0. Nguyên tắc

- **Chỉ đọc.** Không ghi QA Hub, không Jira, không Slack, không report bug. Finding nghi bug → nêu trong báo cáo, chị quyết.
- **Chỉ trên app của team, đúng URL chị đưa.** Không quét domain / subdomain khác, không bên thứ ba (Shopify core, CDN, payment).
- **Không bao giờ** tạo `~/.hae-allow-production` hay tìm cách vượt hook env-guard. Hook chặn → dừng, nói chị cần tự mở cửa.
- Không in token / cookie / credential vào báo cáo hay file — chỉ ghi tên + cờ thuộc tính.

## 1. Mức kiểm theo môi trường

| | Staging / dev store | Production |
|---|---|---|
| Đọc header, cookie flag, TLS, CSP, CORS response | ✅ | ✅ |
| Console error, request lộ data, source map, file debug công khai | ✅ | ✅ (chỉ GET trang chị chỉ) |
| Đo Core Web Vitals, waterfall, bundle size, cache | ✅ | ✅ |
| Nhập dữ liệu thử vào form (XSS/HTML encode, validate input) | ✅ tài khoản test | ❌ |
| Đổi role / đổi id trong URL để kiểm phân quyền (IDOR) | ✅ tài khoản test của team | ❌ |
| Gửi nhiều request liên tiếp (rate limit) | ✅ tối đa 10 request | ❌ |
| Tạo / sửa / xoá data, đặt đơn, gửi email | App Shopify (store staging / dev store của team, `shiki-perfect`): ✅ trừ billing / đổi plan và thanh toán thật, đặt đơn chỉ bằng cổng test. MTRO: ❌ trừ khi chị nói rõ | ❌ |

Ngoại lệ: store `shiki-perfect` (admin `https://admin.shopify.com/store/shiki-perfect`, storefront `https://shiki-perfect.myshopify.com/`) — store production dùng để test các app Shopify của Qikify (TEPO, QSC, QCO, DUOS; không áp cho MTRO) — tính như cột Staging / dev store (kể cả dòng tạo / sửa / xoá data, đặt đơn bằng cổng thanh toán test; vẫn cấm billing / đổi plan và thanh toán thật), hook không chặn, không cần nhắc mở cửa (người dùng duyệt 2026-10-22).

Production: **thụ động hoàn toàn** — chỉ mở trang và quan sát. Trước khi chạy, nhắc chị một câu: hook env-guard sẽ chặn URL production; chị tự `touch ~/.hae-allow-production` trong Terminal nếu muốn tiếp (cửa 30 phút).

Không dùng payload tấn công, scanner tự động (sqlmap, nuclei, ZAP active…), brute force hay fuzzing — trên cả hai môi trường. Phát hiện có dấu hiệu lỗ hổng → ghi lại bằng chứng quan sát được và dừng ở đó, không khai thác tiếp.

## 2. Chuẩn bị

1. Đọc `knowledge-work/apps/<KEY>/inventory.md` (route, role, màn hình) và `business-rules.md` mục phân quyền nếu có. MTRO: URL + tài khoản từ `.env` repo `/Users/nngangaa/Downloads/Auto testing/qikify-QA-mailtro`.
2. Chọn 3–6 màn hình chính (dashboard, form tạo/sửa chính, trang có data khách hàng, storefront widget nếu app Shopify).
3. Thư mục output: `<scratchpad>/sec-perf/<KEY>-<env>-<YYYYMMDD>/` (report.md + screenshot).

## 3. Security

Mỗi mục: ✅ đạt · ⚠️ nên sửa · ❌ lỗi · — không áp dụng. Kèm bằng chứng (header nguyên văn, request URL, ảnh).

- **Transport & header**: HTTPS + redirect HTTP→HTTPS, HSTS, CSP (có `unsafe-inline`/`unsafe-eval`?), `X-Content-Type-Options`, `Referrer-Policy`, chống clickjacking (`frame-ancestors` / `X-Frame-Options` — app Shopify embedded phải cho phép admin.shopify.com, không cho `*`).
- **Cookie phiên**: `Secure`, `HttpOnly`, `SameSite` (chỉ ghi tên cookie + cờ).
- **Lộ thông tin**: response API trả thừa field nhạy cảm (email/phone người khác, token, key nội bộ); stack trace / thông báo lỗi chi tiết; source map công khai; key bí mật trong JS bundle (chỉ ghi loại key + file, che giá trị); console log in data nhạy cảm.
- **CORS**: `Access-Control-Allow-Origin: *` kèm credentials, hoặc phản chiếu origin bất kỳ.
- **Staging thêm**:
  - Input: nhập chuỗi có ký tự HTML (`<b>qa</b>`, `"'<>`) vào field text → kiểm hiển thị lại có bị render thành HTML không.
  - Phân quyền: role thấp (Member) mở route / thao tác chỉ dành cho role cao theo business rule; thay id resource của workspace/store khác của **tài khoản test** trong URL → phải bị chặn.
  - Session: logout rồi Back / mở lại URL cũ → phải về login.
  - Rate limit form login / OTP: ≤ 10 lần, ghi có bị chặn không.

## 4. Performance

Dùng Playwright MCP (`browser_evaluate` đọc `PerformanceObserver` / `performance.getEntries()`, `browser_network_requests`). Cần phân tích sâu (trace, render-blocking) → gợi ý chị chạy skill `web-perf`.

- **Core Web Vitals** mỗi màn hình: LCP (tốt ≤ 2.5s), CLS (≤ 0.1), INP/TBT ước lượng; FCP, TTFB.
- **Network**: tổng số request, tổng dung lượng, request > 1s, API chậm nhất (top 5), request lặp / gọi trùng, ảnh không nén / quá khổ, thiếu cache header cho static asset.
- **Bundle**: JS/CSS lớn nhất (> 500 KB cảnh báo), script chặn render.
- **App Shopify — storefront widget**: thời gian widget hiện, script app có làm chậm trang theme không (so với tắt app nếu chị cho phép trên dev store).
- Đo mỗi màn hình **3 lần**, ghi trung vị; ghi rõ điều kiện (máy, mạng, có cache hay không).

## 5. Báo cáo

Ghi `report.md` và dán vào chat:

```
**Sec/Perf check — <KEY> · <env> · <ngày>**
Phạm vi: <URL, màn hình, role> · Mức kiểm: <thụ động | staging đầy đủ>

### Security
| # | Mức | Hạng mục | Quan sát | Bằng chứng | Đề xuất |

### Performance
| Màn hình | LCP | CLS | TBT | Request | Dung lượng | Chậm nhất |

### Nghi vấn bug (chị quyết có report không)
- <1 câu · mức High/Medium/Low · bước tái hiện>

### Không kiểm được / giới hạn
- <lý do: hook chặn, thiếu quyền, production chỉ thụ động…>
```

Mức: **High** = lộ data người khác / vượt phân quyền / secret lộ; **Medium** = thiếu header bảo vệ quan trọng, LCP > 4s; **Low** = còn lại. Không phóng đại: chỉ ghi điều quan sát được, không suy đoán khả năng khai thác.

Kết thúc: một dòng "Chị cần làm" (report bug nào, hỏi Dev gì, có muốn tạo case security/perf trên QA Hub không — việc của `ore`, chị bảo mới làm).

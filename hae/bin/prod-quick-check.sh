#!/usr/bin/env bash
# Kiểm nhanh sau sự cố / bản vá hạ tầng — Phần D (D1–D7) của security-checklist.md.
# THỤ ĐỘNG: chỉ HEAD/GET, không đăng nhập, không gửi data, không sửa gì. Mỗi host ~15 request cố định
# (không phải scanner: danh sách đường dẫn cố định, không dò). Giá trị cookie / token luôn bị che.
#
# Dùng:  prod-quick-check.sh [--only header,https,errors,files,cors,api,js] [KEY ...]
#        prod-quick-check.sh [--only ...] --host a.com b.com
#   KEY: QIKIFY QCO QSC TEPO DUOS MTRO (không truyền = QIKIFY TEPO DUOS MTRO)
# Sửa domain / endpoint: các hàm *_of bên dưới. Bash 3.2 (macOS) — không dùng mảng kết hợp.
set -u

domains_of() {   # domain production = staging bỏ tiền tố `staging-`
  case "$1" in
    QIKIFY)  echo "embedded.qikify.com portal-api.qikify.com api.qikify.com admin.qikify.com" ;;  # nền chung CO, SC + app trong admin.qikify.com
    QCO|QSC) echo "embedded.qikify.com api.qikify.com" ;;
    TEPO)    echo "" ;;                                                                            # chưa biết domain backend — chị bổ sung
    DUOS)    echo "admin.getduos.io api.getduos.io portal.getduos.io" ;;
    MTRO)    echo "id.mailtro.ai mcp.mailtro.ai portal.mailtro.ai login.mailtro.ai" ;;
    *)       echo "__none__" ;;
  esac
}

# D6 — 2–3 API chính mỗi app (URL đầy đủ, GET, cần đăng nhập). Lấy từ DevTools lúc smoke hoặc hỏi Dev.
api_endpoints_of() {
  case "$1" in
    QIKIFY|QCO|QSC) echo "" ;;
    TEPO)  echo "" ;;
    DUOS)  echo "" ;;
    MTRO)  echo "" ;;
    *)     echo "" ;;
  esac
}

ONLY="header,https,errors,files,cors,api,js"
if [ "${1:-}" = "--only" ]; then ONLY="$2"; shift 2; fi
want() { case ",$ONLY," in *",$1,"*) return 0 ;; esac; return 1; }

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
UA="Mozilla/5.0 (QA-Hae prod-check; contact QA team)"
P=0; F=0; W=0
ok()   { echo "    ✅ $*"; P=$((P+1)); }
bad()  { echo "    ❌ $*"; F=$((F+1)); }
warn() { echo "    ⚠️  $*"; W=$((W+1)); }

hosts=""; keys=""
if [ "${1:-}" = "--host" ]; then shift; hosts="$*"
else
  [ $# -eq 0 ] && set -- QIKIFY TEPO DUOS MTRO
  keys="$*"
  for k in "$@"; do
    d="$(domains_of "$k")"
    if [ "$d" = "__none__" ]; then echo "?? $k: không có trong hàm domains_of"; continue; fi
    [ -z "$d" ] && { echo "?? $k: chưa có domain — bổ sung vào hàm domains_of"; continue; }
    hosts="$hosts $d"
  done
fi

LEAK_RE='Whoops|Ignition|Stack trace|SQLSTATE|PDOException|QueryException|Fatal error|Parse error|Warning</b>:|on line <b>[0-9]+|#0 /|/var/www/|/home/[a-z0-9_-]+/|vendor/laravel|vendor/symfony|APP_DEBUG|phpinfo\(\)|<title>PHP [0-9]'
SECRET_RE='shpss_[A-Za-z0-9]{10,}|shpat_[A-Za-z0-9]{10,}|shppa_[A-Za-z0-9]{10,}|sk_live_[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|client_secret["'"'"' ]*[:=]["'"'"' ]*[A-Za-z0-9_-]{12,}|api_secret["'"'"' ]*[:=]["'"'"' ]*[A-Za-z0-9_-]{12,}|DB_PASSWORD|APP_KEY=base64'

for h in $(echo $hosts | tr ' ' '\n' | awk 'NF && !s[$0]++'); do
  echo "## $h"
  hdr=$(curl -sS -I -m 10 -A "$UA" "https://$h/" 2>&1)
  code=$(sed -n 1p <<<"$hdr" | tr -d '\r')
  if ! grep -q '^HTTP' <<<"$hdr"; then echo "    ·  không kết nối được ($code) — bỏ qua host này"; continue; fi

  if want header; then   # D1 + D2
    srv=$(grep -i '^server:' <<<"$hdr" | tr -d '\r' | sed 's/^[Ss]erver: *//')
    cf=$(grep -ic '^cf-ray:' <<<"$hdr")
    xp=$(grep -iE '^x-powered-by:|^x-php|^x-generator:' <<<"$hdr" | tr -d '\r' | paste -sd ' ' -)
    echo "    ($code)"
    if [ "$cf" -gt 0 ] || [ "$srv" = "cloudflare" ]; then ok "D1 Cloudflare/WAF đứng trước"; else bad "D1 không thấy Cloudflare (server: ${srv:-?})"; fi
    if [ -z "$xp" ]; then ok "D1 không lộ version ra header"; else bad "D1 lộ: $xp"; fi
    if grep -iq '^strict-transport-security:' <<<"$hdr"; then ok "D1 có HSTS"; else warn "D1 không có HSTS (ghi nhận)"; fi
    case "$h" in embedded.*|staging-embedded.*|admin.*|staging-admin.*) emb=1 ;; *) emb=0 ;; esac   # trang nhúng trong Shopify admin
    if [ $emb -eq 1 ] && grep -iq '^content-type: *text/html' <<<"$hdr"; then
      fa=$(grep -i '^content-security-policy:' <<<"$hdr" | tr -d '\r' | grep -oi 'frame-ancestors[^;]*')
      if [ -z "$fa" ]; then bad "D1 trang nhúng Shopify admin không có CSP frame-ancestors"
      elif echo "$fa" | grep -Eq "frame-ancestors +\*( |$)|frame-ancestors +'none'"; then warn "D1 $fa"
      else ok "D1 $fa"; fi
    fi
    grep -i '^set-cookie:' <<<"$hdr" | tr -d '\r' | sed -E 's/^[Ss]et-[Cc]ookie: *([^=]+)=[^;]*/\1/' | awk -F';' '{
      n=$1; s=h=ss=""; for(i=2;i<=NF;i++){g=tolower($i); gsub(/^ +/,"",g); if(g=="secure")s="Secure"; if(g=="httponly")h="HttpOnly"; if(g~/^samesite/)ss=g}
      design=(n=="XSRF-TOKEN"||n=="__cf_bm");
      if (s!="" && (h!="" || design)) printf "    ✅ D2 cookie %s: %s %s %s%s\n", n, s, h, ss, (design?" (đúng thiết kế)":"");
      else printf "    ❌ D2 cookie %s thiếu cờ: %s %s %s\n", n, s, h, ss }'
  fi

  if want https; then    # D1 HTTP -> HTTPS
    loc=$(curl -sS -I -m 10 -A "$UA" "http://$h/" 2>&1 | tr -d '\r' | awk 'NR==1{c=$2} tolower($1)=="location:"{l=$2} END{print c" "l}')
    case "$loc" in 30[1278]\ https://*) ok "D1 http → https ($loc)" ;; *) bad "D1 http không chuyển sang https (${loc:-không phản hồi})" ;; esac
  fi

  if want errors; then   # D3
    for path in "/qa-hae-check-404-$$" "/api/qa-hae-check?id=%27"; do
      c=$(curl -sS -m 10 -A "$UA" -o "$TMP/body" -w '%{http_code}' "https://$h$path" 2>/dev/null)
      hit=$(head -c 200000 "$TMP/body" | grep -oEi "$LEAK_RE" | head -3 | paste -sd ',' -)
      if [ -n "$hit" ]; then bad "D3 $path → $c lộ thông tin: $hit"
      elif [ "$c" -ge 500 ] 2>/dev/null; then warn "D3 $path → $c (5xx nhưng không thấy chi tiết lộ)"
      else ok "D3 $path → $c, không lộ stack trace / đường dẫn / SQL"; fi
    done
  fi

  if want files; then    # D4
    for spec in "/.env|APP_KEY=|DB_PASSWORD=|APP_ENV=" "/.git/config|\\[core\\]|repositoryformatversion" "/phpinfo.php|PHP Version|phpinfo\\(\\)" "/info.php|PHP Version|phpinfo\\(\\)" "/composer.json|\"require\"" "/storage/logs/laravel.log|local\\.ERROR|production\\.ERROR"; do
      path="${spec%%|*}"; marker="${spec#*|}"
      c=$(curl -sS -m 10 -A "$UA" -o "$TMP/body" -w '%{http_code}' "https://$h$path" 2>/dev/null)
      if [ "$c" = "200" ] && head -c 200000 "$TMP/body" | grep -Eq "$marker"; then bad "D4 $path mở được (200, đúng nội dung file thật)"
      elif [ "$c" = "200" ]; then ok "D4 $path → 200 nhưng không phải file thật (trang SPA / index)"
      else ok "D4 $path → $c"; fi
    done
  fi

  if want cors; then     # D5
    ch=$(curl -sS -m 10 -A "$UA" -o /dev/null -D - -H 'Origin: https://evil.test' "https://$h/" 2>/dev/null | tr -d '\r')
    acao=$(echo "$ch" | grep -i '^access-control-allow-origin:' | sed 's/^[^:]*: *//')
    acac=$(echo "$ch" | grep -i '^access-control-allow-credentials:' | sed 's/^[^:]*: *//')
    if [ "$acao" = "https://evil.test" ] && [ "$acac" = "true" ]; then bad "D5 CORS phản chiếu origin lạ + credentials"
    elif [ "$acao" = "https://evil.test" ]; then warn "D5 CORS phản chiếu origin lạ (không kèm credentials)"
    elif [ "$acao" = "*" ] && [ "$acac" = "true" ]; then bad "D5 CORS * + credentials"
    else ok "D5 CORS không mở cho origin lạ kèm credentials (ACAO: ${acao:-không có})"; fi
  fi

  if want js; then       # D7 — JS cùng host / cdn.qikify.com mà trang gốc nạp
    curl -sS -m 10 -A "$UA" -o "$TMP/root" "https://$h/" 2>/dev/null
    srcs=$(grep -oE '<script[^>]+src="[^"]+"' "$TMP/root" 2>/dev/null | sed -E 's/.*src="([^"]+)".*/\1/' \
      | sed -E "s#^//#https://#; s#^/#https://$h/#" | grep -E "^https://($h|cdn\.qikify\.com)/" | head -6)
    if [ -z "$srcs" ]; then echo "    ·  D7 trang gốc không nạp JS cùng host (API / redirect) — bỏ qua"
    else
      for u in $srcs; do
        curl -sS -m 15 -A "$UA" --max-filesize 8000000 -o "$TMP/js" "$u" 2>/dev/null
        s=$(grep -oE "$SECRET_RE" "$TMP/js" 2>/dev/null | sed -E 's/(.{8}).*/\1***/' | sort -u | head -3 | paste -sd ',' -)
        name=$(basename "${u%%\?*}")
        if [ -n "$s" ]; then bad "D7 $name có chuỗi giống secret: $s"; else ok "D7 $name không có secret"; fi
        m=$(grep -oE 'sourceMappingURL=[^ */]+' "$TMP/js" 2>/dev/null | head -1 | sed 's/sourceMappingURL=//')
        if [ -n "$m" ]; then
          mu="${u%/*}/$m"; mc=$(curl -sS -m 10 -A "$UA" -o /dev/null -w '%{http_code}' "$mu" 2>/dev/null)
          [ "$mc" = "200" ] && warn "D7 source map công khai: $(basename "$mu") (lộ mã nguồn — báo Dev, không phải lỗi của bản vá)"
        fi
      done
    fi
  fi
done

if want api; then          # D6
  echo "## API không token (D6)"
  any=0
  for k in $keys; do
    for u in $(api_endpoints_of "$k"); do
      any=1
      c1=$(curl -sS -m 10 -A "$UA" -o "$TMP/b1" -w '%{http_code}' -H 'Accept: application/json' "$u" 2>/dev/null)
      c2=$(curl -sS -m 10 -A "$UA" -o "$TMP/b2" -w '%{http_code}' -H 'Accept: application/json' -H 'Authorization: Bearer qa.hae.invalid' "$u" 2>/dev/null)
      for pair in "không token:$c1:$TMP/b1" "token sai:$c2:$TMP/b2"; do
        lbl="${pair%%:*}"; rest="${pair#*:}"; c="${rest%%:*}"; f="${rest#*:}"
        case "$c" in 401|403|419) ok "D6 $k $u ($lbl) → $c" ;;
          30[12]) ok "D6 $k $u ($lbl) → $c (chuyển về login)" ;;
          *) sz=$(wc -c < "$f" | tr -d ' '); bad "D6 $k $u ($lbl) → $c, body $sz byte — kiểm tay xem có dữ liệu không" ;; esac
      done
    done
  done
  [ $any -eq 0 ] && echo "    ·  chưa có endpoint — điền hàm api_endpoints_of (2–3 API chính mỗi app)"
fi

echo
echo "TỔNG: ✅ $P · ❌ $F · ⚠️  $W"
[ $F -eq 0 ]

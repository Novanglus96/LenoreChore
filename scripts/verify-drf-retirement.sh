#!/usr/bin/env bash
# Verifies the DRF retirement against a LIVE backend.
#
#   ./verify-drf-retirement.sh                       # local dev backend :8001
#   ./verify-drf-retirement.sh https://back-dev...   # a deployed backend
#
# Exits non-zero if anything that should be gone is still answering.
set -uo pipefail
BASE="${1:-http://localhost:8001}"
PASS=0; FAIL=0

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }
code() { curl -sk -o /dev/null -w '%{http_code}' -X "$1" "$BASE$2" --max-time 10; }

echo "Target: $BASE"
echo
echo "1. The app is up"
V=$(code GET /api/v2/version/list)
[ "$V" = "200" ] && ok "GET /api/v2/version/list -> 200 (public endpoint alive)" \
                 || { bad "GET /api/v2/version/list -> $V (backend not reachable?)"; echo; echo "Aborting."; exit 1; }

echo
echo "2. Legacy DRF routes are gone (each must be 404)"
for p in users chores areas areagroups historyitems options months \
         chore-complete chore-snooze historyitem-create; do
  C=$(code GET "/api/$p/")
  [ "$C" = "404" ] && ok "GET /api/$p/ -> 404" || bad "GET /api/$p/ -> $C  ** STILL SERVING **"
done

echo
echo "3. The specific hole: unauthenticated write to a user"
C=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 \
      -X PATCH "$BASE/api/users/1/" \
      -H 'Content-Type: application/json' \
      -d '{"is_superuser": true}')
[ "$C" = "404" ] && ok "PATCH /api/users/1/ {is_superuser:true} -> 404" \
                 || bad "PATCH /api/users/1/ -> $C  ** PRIVILEGE ESCALATION REACHABLE **"

echo
echo "4. The replacement endpoint is authenticated"
C=$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 \
      -X PUT "$BASE/api/v2/me" \
      -H 'Content-Type: application/json' \
      -d '{"first_name":"x","last_name":"y","male":true,"user_color":"#E91E63"}')
# 403 on a real server (CsrfViewMiddleware precedes the auth check on unsafe
# methods), 401 where CSRF is not enforced. Both are refusals.
case "$C" in
  401|403) ok "PUT /api/v2/me (no session) -> $C (refused)" ;;
  *)       bad "PUT /api/v2/me (no session) -> $C (expected 401 or 403)" ;;
esac

C=$(code GET /api/v2/users)
[ "$C" = "401" ] && ok "GET /api/v2/users (no session) -> 401" \
                 || bad "GET /api/v2/users (no session) -> $C (expected 401)"

echo
echo "5. CORS no longer answers for arbitrary origins"
ACAO=$(curl -sk -I --max-time 10 -H "Origin: https://evil.example.com" \
        "$BASE/api/v2/version/list" | grep -i '^access-control-allow-origin:' | tr -d '\r')
if [ -z "$ACAO" ]; then
  ok "no Access-Control-Allow-Origin for an unlisted origin"
else
  bad "still returns: $ACAO"
fi

echo
printf 'passed %d, failed %d\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1

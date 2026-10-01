#!/usr/bin/env bash
set -u

# Internal Home-Lab verification for:
#   client -> Caddy -> APISIX -> New API -> CPA
#
# The token is read from the environment or a root-readable runtime file.
# It is never printed. Run this script on the Home-Lab host, or from a host
# that can reach 10.79.0.7:443.

HOST="${AI_GATEWAY_HOST:-ai-internal.onwalk.net}"
ADDRESS="${AI_GATEWAY_ADDRESS:-10.79.0.7}"
BASE_URL="https://${HOST}/v1"
TOKEN_FILE="${AI_GATEWAY_CLIENT_KEY_FILE:-/run/ai-aggregator/apisix/client-key}"
TIMEOUT="${AI_GATEWAY_TIMEOUT:-90}"
INSECURE="${AI_GATEWAY_INSECURE:-0}"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ai-gateway-verify.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

if [[ -n "${AI_GATEWAY_CLIENT_KEY:-}" ]]; then
  TOKEN="$AI_GATEWAY_CLIENT_KEY"
elif [[ -r "$TOKEN_FILE" ]]; then
  TOKEN="$(<"$TOKEN_FILE")"
else
  echo "ERROR: set AI_GATEWAY_CLIENT_KEY or provide AI_GATEWAY_CLIENT_KEY_FILE" >&2
  exit 2
fi

if [[ -z "$TOKEN" ]]; then
  echo "ERROR: client token is empty" >&2
  exit 2
fi

curl_args=(
  --silent --show-error --http1.1 --noproxy '*'
  --resolve "${HOST}:443:${ADDRESS}"
  --connect-timeout 10 --max-time "$TIMEOUT"
  -H "Authorization: Bearer ${TOKEN}"
  -H "apikey: ${TOKEN}"
)
if [[ "$INSECURE" == "1" ]]; then
  curl_args+=(--insecure)
fi

echo "AI Gateway internal verification"
echo "  host: ${HOST}"
echo "  address: ${ADDRESS}"
echo "  endpoint: ${BASE_URL}"

if command -v getent >/dev/null 2>&1; then
  resolved="$(getent hosts "$HOST" | awk 'NR == 1 {print $1}')"
  echo "  dns: ${resolved:-unresolved}"
fi

request() {
  local name="$1"
  local url="$2"
  local output="${WORK_DIR}/${name}.json"
  local headers="${WORK_DIR}/${name}.headers"
  local status
  local timing

  timing="$(curl "${curl_args[@]}" -D "$headers" -o "$output" \
    -w '%{http_code} %{time_total}' "$url" 2>"${WORK_DIR}/${name}.stderr")"
  status="${timing%% *}"
  timing="${timing#* }"

  if [[ "$status" == "000" ]]; then
    echo "FAIL ${name}: transport error (${timing}s)"
    sed -n '1p' "${WORK_DIR}/${name}.stderr" >&2
    return 1
  fi

  if [[ "$status" =~ ^2 ]]; then
    echo "PASS ${name}: HTTP ${status} (${timing}s)"
    return 0
  fi

  local message=""
  if command -v jq >/dev/null 2>&1; then
    message="$(jq -r '.error.message // .message // empty' "$output" 2>/dev/null | head -c 160)"
  fi
  echo "FAIL ${name}: HTTP ${status} (${timing}s)${message:+ - ${message}}"
  return 1
}

passed=0
failed=0

request models "${BASE_URL}/models" && passed=$((passed + 1)) || failed=$((failed + 1))

if command -v jq >/dev/null 2>&1 && [[ -s "${WORK_DIR}/models.json" ]]; then
  echo "  models:"
  jq -r '.data[]?.id // empty' "${WORK_DIR}/models.json" | sed 's/^/    - /' | head -100
fi

for model in gpt-5.6-luna claude-sonnet-5 gemini-3-flash; do
  payload="${WORK_DIR}/${model//[^a-zA-Z0-9]/_}.request.json"
  output="${WORK_DIR}/${model//[^a-zA-Z0-9]/_}.json"
  printf '{"model":"%s","messages":[{"role":"user","content":"Reply with exactly OK."}],"max_tokens":32,"stream":false}\n' "$model" >"$payload"
  result="$(curl "${curl_args[@]}" -H 'Content-Type: application/json' \
    --data-binary "@$payload" -o "$output" \
    -w '%{http_code} %{time_total}' "${BASE_URL}/chat/completions" 2>"${WORK_DIR}/${model//[^a-zA-Z0-9]/_}.stderr")"
  status="${result%% *}"
  timing="${result#* }"
  if [[ "$status" =~ ^2 ]]; then
    echo "PASS inference/${model}: HTTP ${status} (${timing}s)"
    passed=$((passed + 1))
  else
    echo "FAIL inference/${model}: HTTP ${status} (${timing}s)"
    failed=$((failed + 1))
  fi
done

echo "Summary: ${passed} passed, ${failed} failed"
if (( failed > 0 )); then
  exit 1
fi

#!/usr/bin/env bash
set -euo pipefail

# Read-only gateway smoke test. Does not change remote configuration.
BASE_URL="${AI_GATEWAY_BASE_URL:-https://ai-internal.onwalk.net/v1}"
KEY="${AI_GATEWAY_CLIENT_KEY:-}"
if [[ -z "$KEY" ]]; then
  echo 'AI_GATEWAY_CLIENT_KEY is required (load it without putting it in shell history).' >&2
  exit 2
fi
command -v python3 >/dev/null || { echo 'python3 is required' >&2; exit 2; }
command -v curl >/dev/null || { echo 'curl is required' >&2; exit 2; }

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
models=("${@:-gpt-5.6-luna}")
if [[ $# -eq 0 ]]; then
  models=(gpt-5.6-luna claude-sonnet-5 gemini-3-flash)
fi

# Header is passed through curl stdin; never enable shell tracing or curl -v.
request() {
  local outfile="$1"; shift
  printf 'header = "Authorization: Bearer %s"\n' "$KEY" |
    curl --noproxy '*' --silent --show-error --max-time 45 \
      --config - --output "$outfile" --write-out '%{http_code} %{time_total}' "$@"
}

if ! result="$(request "$tmpdir/models.json" "$BASE_URL/models")"; then
  echo 'models: transport/TLS/DNS failure' >&2
  exit 1
fi
read -r status elapsed <<< "$result"
if [[ "$status" != 200 ]]; then
  echo "models: HTTP $status, ${elapsed}s (401=client auth; 403=ACL/IP)" >&2
  exit 1
fi
python3 - "$tmpdir/models.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ids={item.get('id') for item in data.get('data', []) if isinstance(item, dict)}
print(f'models: HTTP 200, catalog_count={len(ids)}')
PY

failed=0
for model in "${models[@]}"; do
  # JSON construction is handled by Python so model IDs are never shell-interpolated into JSON.
  python3 - "$model" "$tmpdir/request.json" <<'PY'
import json, sys
with open(sys.argv[2], 'w') as f:
    json.dump({'model':sys.argv[1], 'messages':[{'role':'user','content':'Reply only hello.'}], 'max_tokens':32}, f)
PY
  if ! result="$(request "$tmpdir/response.json" \
      --header 'Content-Type: application/json' \
      --data-binary "@$tmpdir/request.json" "$BASE_URL/chat/completions")"; then
    echo "$model: transport/timeout failure"
    failed=1
    continue
  fi
  read -r status elapsed <<< "$result"
  if [[ "$status" != 200 ]]; then
    echo "$model: HTTP $status, ${elapsed}s (403 may mean APISIX model allowlist or upstream refusal)"
    failed=1
    continue
  fi
  if python3 - "$tmpdir/response.json" <<'PY'
import json, sys
try:
    data=json.load(open(sys.argv[1]))
    assert data.get('choices') and data['choices'][0].get('message', {}).get('content')
except (OSError, ValueError, KeyError, TypeError, AssertionError):
    sys.exit(1)
PY
  then
    echo "$model: HTTP 200, nonempty Chat response, ${elapsed}s"
  else
    echo "$model: HTTP 200 but invalid/empty Chat response, ${elapsed}s"
    failed=1
  fi
done
exit "$failed"

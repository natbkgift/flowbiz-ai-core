[CmdletBinding()]
param(
  [Parameter()]
  [string]$RemotePath = "/opt/flowbiz/flowbiz-ai-core",

  [Parameter()]
  [string[]]$ComposeFiles = @("docker-compose.yml", "docker-compose.override.prod.yml"),

  [Parameter()]
  [string]$GitRef = "main",

  [Parameter()]
  [string]$HealthUrlLocal = "http://127.0.0.1:8000/healthz",

  [Parameter()]
  [string]$PublicHealthUrl = "",

  [Parameter()]
  [switch]$ReloadNginx,

  [Parameter()]
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $RemotePath.StartsWith("/opt/flowbiz/")) {
  throw "RemotePath must be under /opt/flowbiz/. Got: $RemotePath"
}

if ($ComposeFiles.Count -eq 0) {
  throw "ComposeFiles must not be empty."
}

$composeArgs = ($ComposeFiles | ForEach-Object { "-f $($_)" }) -join " "

$remoteScript = @"
set -euo pipefail

echo "== target"
echo "host: flowbiz-vps"
echo "path: $RemotePath"
echo "ref:  $GitRef"

cd "$RemotePath"

echo "== git fetch"
git fetch origin --prune

echo "== git checkout"
if echo "$GitRef" | grep -Eq '^[0-9a-f]{7,40}$'; then
  git checkout --detach "$GitRef"
else
  git checkout "$GitRef"
  git pull --ff-only origin "$GitRef" || true
fi

echo "== deploy"
docker compose $composeArgs up -d --build --remove-orphans

echo "== status"
docker compose $composeArgs ps

echo "== health (local)"
curl -fsS "$HealthUrlLocal" >/dev/null
curl -fsS "$HealthUrlLocal" | head -c 400 || true

echo ""
"@

if ($PublicHealthUrl.Trim().Length -gt 0) {
  $remoteScript += @"

echo "== health (public)"
curl -fsS "$PublicHealthUrl" >/dev/null
curl -fsS "$PublicHealthUrl" | head -c 400 || true

echo ""
"@
}

if ($ReloadNginx) {
  $remoteScript += @"

echo "== nginx validate + reload"
sudo nginx -t
sudo systemctl reload nginx

echo ""
"@
}

$remoteScript += "echo '✅ deploy completed'\n"

$remoteScriptLf = $remoteScript -replace "`r`n", "`n"
$scriptBytes = [System.Text.Encoding]::UTF8.GetBytes($remoteScriptLf)
$scriptB64 = [Convert]::ToBase64String($scriptBytes)

$sshPayload = "printf '%s' '$scriptB64' | base64 -d | bash"

Write-Host "Deploying via ssh flowbiz-vps ..."

if ($DryRun) {
  Write-Host "--- DRY RUN (no commands executed) ---"
  Write-Host $remoteScriptLf
  exit 0
}

# Preflight: ensure SSH works non-interactively
& ssh -o BatchMode=yes flowbiz-vps "echo ok" | Out-Null

# Execute remote script
& ssh flowbiz-vps $sshPayload

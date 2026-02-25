[CmdletBinding()]
param(
  [Parameter()]
  [string]$RemotePath = "/opt/flowbiz/flowbiz-ai-core",

  [Parameter()]
  [string[]]$ComposeFiles = @("docker-compose.yml", "docker-compose.override.prod.yml"),

  [Parameter()]
  [string]$GitRef = "main",

  [Parameter()]
  [ValidateSet("git", "upload")]
  [string]$SourceMode = "git",

  [Parameter()]
  [string]$HealthUrlLocal = "http://127.0.0.1:8000/healthz",

  [Parameter()]
  [ValidateSet("host", "container")]
  [string]$HealthMode = "host",

  [Parameter()]
  [string]$PublicHealthUrl = "",

  [Parameter()]
  [switch]$ReloadNginx,

  [Parameter()]
  [switch]$ResetRemoteGitWorkingTree,

  [Parameter()]
  [string[]]$PreserveRemotePaths = @(".env", ".env.bak*", ".env.preclean.*"),

  [Parameter()]
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

if (-not $RemotePath.StartsWith("/opt/flowbiz/")) {
  throw "RemotePath must be under /opt/flowbiz/. Got: $RemotePath"
}

if ($ComposeFiles.Count -eq 0) {
  throw "ComposeFiles must not be empty."
}

$composeArgs = ($ComposeFiles | ForEach-Object { "-f $($_)" }) -join " "

function Assert-CommandExists {
  param([Parameter(Mandatory = $true)][string]$Name)
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $cmd) {
    throw "Required command not found: $Name"
  }
}

function Invoke-CheckedNative {
  param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    [Parameter()][string[]]$ArgumentList = @(),
    [Parameter(Mandatory = $true)][string]$Description,
    [Parameter()][int[]]$AllowedExitCodes = @(0),
    [Parameter()][switch]$CaptureOutput
  )

  $output = @()
  if ($CaptureOutput) {
    $output = @(& $FilePath @ArgumentList 2>&1)
    $exitCode = if ($null -ne $LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }
    foreach ($line in $output) {
      Write-Host $line
    }
  }
  else {
    & $FilePath @ArgumentList
    $exitCode = if ($null -ne $LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }
  }

  if ($AllowedExitCodes -notcontains $exitCode) {
    throw ("{0} failed with exit code {1}" -f $Description, $exitCode)
  }

  return ,$output
}

$sshBaseArgs = @("-o", "BatchMode=yes", "-o", "ConnectTimeout=20")
$successMarker = "FLOWBIZ_DEPLOY_COMPLETED"
$resetRemoteGit = if ($ResetRemoteGitWorkingTree) { "1" } else { "0" }
$gitCleanExcludeArgs = (
  $PreserveRemotePaths |
  Where-Object { $_ -and $_.Trim().Length -gt 0 } |
  ForEach-Object { "-e '$($_)'" }
) -join " "
$preserveDisplay = if ($PreserveRemotePaths.Count -gt 0) {
  ($PreserveRemotePaths -join ", ")
}
else {
  "(none)"
}

$gitSection = @"

echo "== repo sanity"
if [ -d .git ]; then
  if [ "$resetRemoteGit" = "1" ]; then
    echo "ResetRemoteGitWorkingTree=on (preserving: $preserveDisplay)"
    git reset --hard
    git clean -fd $gitCleanExcludeArgs
  else
    if [ -n "`$(git status --porcelain)" ]; then
      echo "❌ remote git working tree is not clean" 1>&2
      git status --short 1>&2 || true
      echo "Hint: rerun with -ResetRemoteGitWorkingTree to clean tracked/untracked files (preserves: $preserveDisplay)" 1>&2
      exit 1
    fi
  fi
fi

echo "== git fetch"
git fetch origin --prune

echo "== git checkout"
if echo "$GitRef" | grep -Eq '^[0-9a-f]{7,40}$'; then
  git checkout --detach "$GitRef"
else
  git checkout "$GitRef"
  git pull --ff-only origin "$GitRef"
fi
"@

if ($SourceMode -eq "upload") {
  $gitSection = @"

echo "== source"
echo "SourceMode=upload (skipping remote git fetch/checkout)"
"@
}

$remoteScript = @"
set -euo pipefail

echo "== target"
echo "host: flowbiz-vps"
echo "path: $RemotePath"
echo "ref:  $GitRef"

cd "$RemotePath"

$gitSection

echo "== deploy"
docker compose $composeArgs up -d --build --remove-orphans

echo "== status"
docker compose $composeArgs ps

echo "== health (local)"
if [ "$HealthMode" = "container" ]; then
  ok=0
  i=1
  while [ "`$i" -le 20 ]; do
    if docker compose $composeArgs exec -T api python -c "import urllib.request; print(urllib.request.urlopen('$HealthUrlLocal', timeout=2).read()[:400].decode('utf-8','ignore'))" 2>/dev/null; then
      ok=1
      break
    fi
    echo "health retry `$i/20 (container) ..."
    sleep 1
    i=`$((`$i+1))
  done
  if [ "`$ok" -ne 1 ]; then
    echo "❌ health check failed (container). Recent api logs:" 1>&2
    docker compose $composeArgs logs --tail=200 api || true
    exit 1
  fi
else
  ok=0
  i=1
  while [ "`$i" -le 20 ]; do
    if curl -fsS --max-time 2 "$HealthUrlLocal" >/dev/null; then
      ok=1
      break
    fi
    echo "health retry `$i/20 (host) ..."
    sleep 1
    i=`$((`$i+1))
  done
  if [ "`$ok" -ne 1 ]; then
    echo "❌ health check failed (host). Recent api logs:" 1>&2
    docker compose $composeArgs logs --tail=200 api || true
    exit 1
  fi
  local_health_body="`$(curl -fsS "$HealthUrlLocal" || true)"
  printf '%s' "`$local_health_body" | cut -c1-400 || true
fi

echo ""
"@

if ($PublicHealthUrl.Trim().Length -gt 0) {
  $remoteScript += @"

echo "== health (public)"
public_health_body="`$(curl -fsS "$PublicHealthUrl" || true)"
test -n "`$public_health_body"
printf '%s' "`$public_health_body" | cut -c1-400 || true

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

$remoteScript += @"

echo "$successMarker"
echo "✅ deploy completed"
"@

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
Invoke-CheckedNative -FilePath "ssh" -ArgumentList (@($sshBaseArgs + @("flowbiz-vps", "echo ok"))) -Description "SSH preflight" | Out-Null

if ($SourceMode -eq "upload") {
  Assert-CommandExists -Name "git"
  Assert-CommandExists -Name "scp"

  $sha = (& git rev-parse HEAD).Trim()
  if (-not $sha) {
    throw "Could not determine local git SHA (git rev-parse HEAD)."
  }

  $tmp = Join-Path $env:TEMP ("flowbiz-src-{0}.tar.gz" -f $sha)
  if (Test-Path $tmp) {
    Remove-Item -Force $tmp
  }

  Write-Host "Creating git archive for $sha ..."
  Invoke-CheckedNative -FilePath "git" -ArgumentList @("archive", "--format=tar.gz", "-o", $tmp, $sha) -Description "git archive" | Out-Null

  $remoteTmp = "/tmp/flowbiz-src-$sha.tar.gz"

  Write-Host "Uploading archive to VPS ..."
  Invoke-CheckedNative -FilePath "scp" -ArgumentList (@($sshBaseArgs + @($tmp, ("flowbiz-vps:{0}" -f $remoteTmp)))) -Description "scp upload archive" | Out-Null

  Write-Host "Extracting archive on VPS ..."
  $extractCmd = ("mkdir -p '{0}' && tar -xzf '{1}' -C '{0}' && rm -f '{1}'" -f $RemotePath, $remoteTmp)
  Invoke-CheckedNative -FilePath "ssh" -ArgumentList (@($sshBaseArgs + @("flowbiz-vps", $extractCmd))) -Description "SSH extract archive" | Out-Null

  Remove-Item -Force $tmp -ErrorAction SilentlyContinue
}

# Execute remote script
$remoteOutput = Invoke-CheckedNative -FilePath "ssh" -ArgumentList (@($sshBaseArgs + @("flowbiz-vps", $sshPayload))) -Description "SSH remote deploy" -CaptureOutput
if (-not ($remoteOutput -join "`n").Contains($successMarker)) {
  throw "Remote deploy finished without success marker ($successMarker). Treating as failure."
}

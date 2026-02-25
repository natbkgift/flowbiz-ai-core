[CmdletBinding()]
param(
  [Parameter()]
  [string]$BaseUrl = "https://flowbiz.cloud/api",

  [Parameter()]
  [int]$TimeoutSec = 15,

  [Parameter()]
  [int]$Retries = 2
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

$endpoints = @(
  @{ Path = "/healthz"; ExpectedStatus = 200; Name = "healthz" }
  @{ Path = "/v1/meta"; ExpectedStatus = 200; Name = "meta" }
  @{ Path = "/v1/agent/tools"; ExpectedStatus = 200; Name = "agent-tools" }
  @{ Path = "/v1/agent/health"; ExpectedStatus = 200; Name = "agent-health" }
  @{ Path = "/"; ExpectedStatus = 200; Name = "root" }
  @{ Path = "/openapi.json"; ExpectedStatus = 200; Name = "openapi" }
)

function Invoke-SmokeRequest {
  param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)][int]$Timeout
  )

  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  $result = [ordered]@{
    Url         = $Url
    StatusCode  = 0
    ContentType = ""
    DurationMs  = 0.0
    Body        = ""
    Error       = $null
  }

  $tmpBody = [System.IO.Path]::GetTempFileName()
  $tmpHeaders = [System.IO.Path]::GetTempFileName()
  try {
    $writeOut = & curl.exe -sS -L `
      --max-time $Timeout `
      -o $tmpBody `
      -D $tmpHeaders `
      -w "%{http_code}`n%{content_type}`n%{time_total}" `
      $Url 2>&1
    $curlExit = $LASTEXITCODE
    $sw.Stop()

    $metaLines = @()
    if ($writeOut) {
      $metaLines = @($writeOut -split "`r?`n")
    }
    if ($metaLines.Count -ge 3) {
      $statusLine = $metaLines[$metaLines.Count - 3]
      $ctypeLine = $metaLines[$metaLines.Count - 2]
      $timeLine = $metaLines[$metaLines.Count - 1]
      if ($statusLine -match '^\d+$') {
        $result.StatusCode = [int]$statusLine
      }
      $result.ContentType = [string]$ctypeLine
      if ($timeLine -as [double]) {
        $result.DurationMs = [math]::Round(([double]$timeLine) * 1000, 1)
      }
    }

    if (Test-Path $tmpBody) {
      $result.Body = Get-Content $tmpBody -Raw -ErrorAction SilentlyContinue
    }

    if ($curlExit -ne 0) {
      $stderrText = ($metaLines | Where-Object { $_ -and ($_ -notmatch '^\d+$') }) -join " | "
      if (-not $stderrText) {
        $stderrText = "curl exit $curlExit"
      }
      $result.Error = $stderrText
    }
  }
  finally {
    $sw.Stop()
    Remove-Item -Force $tmpBody, $tmpHeaders -ErrorAction SilentlyContinue
  }

  if (-not $result.DurationMs -or $result.DurationMs -le 0) {
    $result.DurationMs = [math]::Round($sw.Elapsed.TotalMilliseconds, 1)
  }
  return [pscustomobject]$result
}

function Invoke-WithRetry {
  param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)][int]$Timeout,
    [Parameter(Mandatory = $true)][int]$ExpectedStatus,
    [Parameter(Mandatory = $true)][int]$MaxRetries
  )

  $attempt = 0
  $last = $null
  do {
    $attempt += 1
    $last = Invoke-SmokeRequest -Url $Url -Timeout $Timeout
    if ($last.StatusCode -eq $ExpectedStatus) {
      return $last
    }
    if ($attempt -le $MaxRetries) {
      Start-Sleep -Seconds 1
    }
  } while ($attempt -le ($MaxRetries + 1))

  return $last
}

$normalizedBase = $BaseUrl.TrimEnd("/")
Write-Host ("== Smoke test: {0}" -f $normalizedBase)
Write-Host ("TimeoutSec={0} Retries={1}" -f $TimeoutSec, $Retries)

$failures = @()
$results = @()

foreach ($endpoint in $endpoints) {
  $url = "$normalizedBase$($endpoint.Path)"
  $r = Invoke-WithRetry -Url $url -Timeout $TimeoutSec -ExpectedStatus $endpoint.ExpectedStatus -MaxRetries $Retries
  $results += [pscustomobject]@{
    Name        = $endpoint.Name
    Path        = $endpoint.Path
    StatusCode  = $r.StatusCode
    DurationMs  = $r.DurationMs
    ContentType = $r.ContentType
    Url         = $url
    Body        = $r.Body
    Error       = $r.Error
  }

  $ok = $r.StatusCode -eq $endpoint.ExpectedStatus
  $statusLabel = if ($ok) { "PASS" } else { "FAIL" }
  $ct = if ($r.ContentType) { $r.ContentType } else { "-" }
  $err = if ($r.Error) { $r.Error } else { "" }
  Write-Host ("{0}`t{1}`t{2}`t{3}ms`t{4}`t{5}" -f $statusLabel, $endpoint.Path, $r.StatusCode, $r.DurationMs, $ct, $err)

  if (-not $ok) {
    $failures += $endpoint.Path
  }
}

function Try-ParseJsonSummary {
  param([string]$Raw)
  if (-not $Raw) {
    return $null
  }
  try {
    return $Raw | ConvertFrom-Json
  }
  catch {
    return $null
  }
}

$health = $results | Where-Object { $_.Path -eq "/healthz" } | Select-Object -First 1
$meta = $results | Where-Object { $_.Path -eq "/v1/meta" } | Select-Object -First 1
$openapi = $results | Where-Object { $_.Path -eq "/openapi.json" } | Select-Object -First 1

$healthJson = Try-ParseJsonSummary -Raw $health.Body
$metaJson = Try-ParseJsonSummary -Raw $meta.Body
$openapiJson = Try-ParseJsonSummary -Raw $openapi.Body

Write-Host "== Summary"
if ($healthJson) {
  Write-Host ("healthz.version={0}" -f $healthJson.version)
}
if ($metaJson) {
  Write-Host ("meta.version={0} env={1}" -f $metaJson.version, $metaJson.env)
}
if ($openapiJson) {
  Write-Host ("openapi.info.version={0}" -f $openapiJson.info.version)
}

if ($failures.Count -gt 0) {
  Write-Error ("Smoke test failed: {0}" -f ($failures -join ", "))
  exit 1
}

Write-Host "Smoke test PASS"

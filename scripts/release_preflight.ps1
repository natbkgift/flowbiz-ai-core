[CmdletBinding()]
param(
  [Parameter()]
  [string]$ExpectedVersion = "",

  [Parameter()]
  [string]$ExpectedTag = "",

  [Parameter()]
  [switch]$RequireCleanGit = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoVersionFromPyProject {
  param([string]$Path)
  $content = Get-Content $Path -Raw
  if ($content -match '(?ms)^\[project\].*?^version\s*=\s*"([^"]+)"') {
    return $matches[1]
  }
  throw "Could not parse [project].version from $Path"
}

function Get-EnvVersionFromExample {
  param([string]$Path)
  foreach ($line in Get-Content $Path) {
    if ($line -match '^FLOWBIZ_VERSION=(.+)$') {
      return $matches[1].Trim()
    }
  }
  throw "Could not find FLOWBIZ_VERSION in $Path"
}

function Get-PythonDefaultVersion {
  param(
    [string]$Path,
    [string]$Pattern
  )
  $content = Get-Content $Path -Raw
  if ($content -match $Pattern) {
    return $matches[1]
  }
  throw "Could not parse version from $Path"
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
  if ($RequireCleanGit) {
    $status = git status --short
    if ($LASTEXITCODE -ne 0) {
      throw "git status failed"
    }
    if ($status) {
      throw "Working tree is not clean. Commit/stash changes before release."
    }
  }

  $pyprojectVersion = Get-RepoVersionFromPyProject -Path "pyproject.toml"
  $envExampleVersion = Get-EnvVersionFromExample -Path ".env.example"
  $sdkDefaultVersion = Get-PythonDefaultVersion -Path "packages/core/contracts/devx.py" -Pattern 'package_version:\s*str\s*=\s*"([^"]+)"'

  $versions = [ordered]@{
    "pyproject.project.version" = $pyprojectVersion
    ".env.example FLOWBIZ_VERSION" = $envExampleVersion
    "devx SDKGeneratorTarget.package_version" = $sdkDefaultVersion
  }

  Write-Host "== Release preflight versions"
  foreach ($item in $versions.GetEnumerator()) {
    Write-Host ("{0} = {1}" -f $item.Key, $item.Value)
  }

  $unique = @($versions.Values | Select-Object -Unique)
  if ($unique.Count -ne 1) {
    throw ("Version mismatch detected: {0}" -f (($versions.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ", "))
  }

  $resolvedVersion = $unique[0]
  if ($ExpectedVersion -and $resolvedVersion -ne $ExpectedVersion) {
    throw ("ExpectedVersion mismatch: expected {0}, found {1}" -f $ExpectedVersion, $resolvedVersion)
  }

  if ($ExpectedTag) {
    if ($ExpectedTag -notmatch '^v(.+)$') {
      throw "ExpectedTag must look like vX.Y.Z"
    }
    $tagVersion = $matches[1]
    if ($tagVersion -ne $resolvedVersion) {
      throw ("ExpectedTag ({0}) does not match resolved app version ({1})" -f $ExpectedTag, $resolvedVersion)
    }
    $existingTag = git tag --list $ExpectedTag
    if ($LASTEXITCODE -ne 0) {
      throw "git tag --list failed"
    }
    if ($existingTag) {
      throw ("Tag already exists locally: {0}" -f $ExpectedTag)
    }
  }

  Write-Host ("Resolved app version: {0}" -f $resolvedVersion)
  Write-Host "Release preflight PASS"
}
finally {
  Pop-Location
}

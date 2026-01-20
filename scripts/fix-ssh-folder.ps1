param(
  [switch]$DryRun
)

$userProfile = [Environment]::GetFolderPath('UserProfile')
$thaiAe = [char]0x0E41 # U+0E41 (Thai character that commonly replaces '.' on Thai layouts)
$wrongDirName = ($thaiAe.ToString() + 'ssh')
$wrongPath = Join-Path $userProfile $wrongDirName
$correctPath = Join-Path $userProfile '.ssh'

Write-Host "User profile: $userProfile"
Write-Host "Expected SSH dir: $correctPath"

if (Test-Path -LiteralPath $wrongPath) {
  Write-Warning "Found wrong SSH directory (likely from Thai keyboard '.' => U+0E41): $wrongPath"

  if (Test-Path -LiteralPath $correctPath) {
    Write-Error "Both '$wrongPath' and '$correctPath' exist. Refusing to auto-merge. Manually move keys/config into '$correctPath' and delete '$wrongPath'."
    exit 2
  }

  if ($DryRun) {
    Write-Host "DryRun: would rename '$wrongPath' -> '$correctPath'"
  } else {
    Rename-Item -LiteralPath $wrongPath -NewName '.ssh'
    Write-Host "Renamed '$wrongPath' -> '$correctPath'"
  }
} else {
  Write-Host "No '$wrongPath' directory found."
}

if (-not (Test-Path -LiteralPath $correctPath)) {
  if ($DryRun) {
    Write-Host "DryRun: would create '$correctPath'"
  } else {
    New-Item -ItemType Directory -Force -Path $correctPath | Out-Null
    Write-Host "Created '$correctPath'"
  }
}

Write-Host ""
Write-Host "Prevention tip: Ensure your keyboard input is EN before typing '.ssh'. On some Thai layouts, '.' can become U+0E41."

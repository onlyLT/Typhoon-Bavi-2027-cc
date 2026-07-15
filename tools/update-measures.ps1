# Scheduled updater for typhoon official-measures snapshot (assets/measures.js).
# PS 5.1 reads BOM-less UTF-8 as ANSI, so this file stays ASCII-only.
$ErrorActionPreference = 'Continue'
$proj = 'E:\dev\Typhoon-Bavi-2027-cc'
$measures = "$proj\assets\measures.js"
$backup = "$proj\assets\measures.backup.js"
$log = "$proj\tools\update.log"

Set-Location $proj
"===== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') update start" | Out-File $log -Append -Encoding utf8

# Backup for rollback if validation fails
Copy-Item $measures $backup -Force

$prompt = Get-Content "$proj\tools\update-prompt.txt" -Raw -Encoding utf8
& claude -p $prompt --model sonnet --allowedTools "WebSearch" "WebFetch" "Read" "Write" 2>&1 |
  Out-File $log -Append -Encoding utf8

# Validate: must be legal JS and contain schema keys, else roll back
node --check $measures 2>&1 | Out-File $log -Append -Encoding utf8
$valid = ($LASTEXITCODE -eq 0) -and (Select-String -Path $measures -Pattern 'OFFICIAL_DATA' -Quiet) -and (Select-String -Path $measures -Pattern 'asof' -Quiet)
if (-not $valid) {
  Copy-Item $backup $measures -Force
  "VALIDATION FAILED - rolled back to backup" | Out-File $log -Append -Encoding utf8
} else {
  "update OK" | Out-File $log -Append -Encoding utf8
}

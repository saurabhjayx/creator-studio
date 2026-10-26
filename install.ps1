# Manual install on Windows. Preferred: /plugin marketplace add saurabhjayx/creator-studio
$ErrorActionPreference = "Stop"
$Src = $PSScriptRoot
$Dest = if ($env:CLAUDE_HOME) { $env:CLAUDE_HOME } else { Join-Path $HOME ".claude" }
if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command python3 -ErrorAction SilentlyContinue)) { throw "Python 3.9+ required" }
New-Item -ItemType Directory -Force -Path "$Dest\skills", "$Dest\agents" | Out-Null
Get-ChildItem "$Src\skills" -Directory | ForEach-Object {
  $t = Join-Path "$Dest\skills" $_.Name
  if (Test-Path $t) { Remove-Item -Recurse -Force $t }
  Copy-Item -Recurse $_.FullName $t
}
Copy-Item "$Src\agents\*.md" "$Dest\agents\"
Write-Host "Installed creator-studio into $Dest. Restart Claude Code, then try: /creator trends"

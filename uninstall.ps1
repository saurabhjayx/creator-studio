$Dest = if ($env:CLAUDE_HOME) { $env:CLAUDE_HOME } else { Join-Path $HOME ".claude" }
Get-ChildItem "$Dest\skills" -Directory | Where-Object { $_.Name -eq "creator" -or $_.Name -like "creator-*" } | Remove-Item -Recurse -Force
"researcher","writer","analyst","quick" | ForEach-Object { Remove-Item -Force -ErrorAction SilentlyContinue "$Dest\agents\creator-$_.md" }
Write-Host "creator-studio removed from $Dest"

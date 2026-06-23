$env:PYTHONUNBUFFERED = "1"
if (Test-Path ".env") { Get-Content ".env" | ForEach-Object { if ($_ -match '^([^#=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process") } } }
uvicorn main:app --reload --host 0.0.0.0 --port 8000

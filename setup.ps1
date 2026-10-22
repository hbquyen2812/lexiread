$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
function New-HexSecret([int]$Length) {
    $bytes = New-Object byte[] $Length
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    $rng.Dispose()
    return ([System.BitConverter]::ToString($bytes)).Replace("-", "").ToLowerInvariant()
}
$path = Join-Path $PSScriptRoot ".env"
if (Test-Path $path) { $content = [System.IO.File]::ReadAllText($path) }
else { $content = [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot ".env.example")) }
$content = $content.Replace("__GENERATE_SECRET__", (New-HexSecret 48))
$content = $content.Replace("__GENERATE_DATABASE_PASSWORD__", (New-HexSecret 24))
[System.IO.File]::WriteAllText($path, $content, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "[1/2] .env is ready. Existing settings were preserved."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Install/start Docker Desktop, then run this script again. See README_VI.md."
    exit 1
}
& docker info *> $null
if ($LASTEXITCODE -ne 0) { throw "Docker Desktop is not running. Start it and retry." }
Write-Host "[2/2] Building and starting LexiRead with PostgreSQL..."
& docker compose up --build -d
if ($LASTEXITCODE -ne 0) { throw "Docker Compose failed. See its output and README_VI.md." }
Write-Host "Next: docker compose exec web python manage.py createsuperuser"
Write-Host "Then: docker compose exec web python manage.py seed_demo --username quyen"
Write-Host "Open http://localhost:8000 after the web health check is healthy."

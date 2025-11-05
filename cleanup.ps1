# Cleanup script for universal-oauth-sdk
# Removes build artifacts and cache files before pushing to GitHub

Write-Host "Cleaning up junk files..." -ForegroundColor Cyan

# Remove Python cache files
Write-Host "`nRemoving Python cache files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyo" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyd" | Remove-Item -Force
Write-Host "[OK] Python cache files removed" -ForegroundColor Green

# Remove build artifacts (but keep them in node_modules)
Write-Host "`nRemoving build artifacts..." -ForegroundColor Yellow
$distDirs = @(
    ".\dist",
    ".\packages\cli\dist",
    ".\packages\manifest-tools\dist",
    ".\packages\react-sdk\dist",
    ".\packages\sdk-node\dist",
    ".\packages\examples\node-basic\dist"
)
foreach ($dir in $distDirs) {
    if (Test-Path $dir) {
        Remove-Item $dir -Recurse -Force
        Write-Host "  Removed: $dir" -ForegroundColor Gray
    }
}
Write-Host "[OK] Build artifacts removed" -ForegroundColor Green

# Remove log files
Write-Host "`nRemoving log files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Filter "*.log" | Remove-Item -Force
Write-Host "[OK] Log files removed" -ForegroundColor Green

# Remove .env files (keep .env.example)
Write-Host "`nChecking for .env files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Filter ".env" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter ".env.local" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter ".env.development" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter ".env.production" | Remove-Item -Force
Write-Host "[OK] .env files removed (kept .env.example)" -ForegroundColor Green

# Remove database files
Write-Host "`nRemoving database files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Filter "*.db" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "tokens.db" | Remove-Item -Force
Write-Host "[OK] Database files removed" -ForegroundColor Green

# Summary
Write-Host "`nCleanup complete!" -ForegroundColor Green
Write-Host "`nSummary:" -ForegroundColor Cyan
Write-Host "  - Python cache files removed" -ForegroundColor Gray
Write-Host "  - Build artifacts removed" -ForegroundColor Gray
Write-Host "  - Log files removed" -ForegroundColor Gray
Write-Host "  - Environment files removed" -ForegroundColor Gray
Write-Host "  - Database files removed" -ForegroundColor Gray
Write-Host "`nReady to push to GitHub!" -ForegroundColor Green
Write-Host "`nTip: Run git status to verify what will be committed" -ForegroundColor Yellow

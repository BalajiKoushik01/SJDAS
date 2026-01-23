# ============================================================
# SJ-DAS GitHub Upload Script
# Repository: https://github.com/BalajiKoushik01/SJDAS.git
# ============================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SJ-DAS GitHub Upload Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
Write-Host "Checking for Git installation..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git first:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "2. Run the installer" -ForegroundColor White
    Write-Host "3. Restart PowerShell" -ForegroundColor White
    Write-Host "4. Run this script again" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

Write-Host ""
Write-Host "Configuring Git..." -ForegroundColor Yellow
git config user.name "BalajiKoushik01"
git config user.email "balajikoushik01@gmail.com"
Write-Host "✅ Git configured" -ForegroundColor Green

Write-Host ""
Write-Host "Initializing repository..." -ForegroundColor Yellow
git init
Write-Host "✅ Repository initialized" -ForegroundColor Green

Write-Host ""
Write-Host "Adding all files..." -ForegroundColor Yellow
git add .
Write-Host "✅ Files added" -ForegroundColor Green

Write-Host ""
Write-Host "Creating commit..." -ForegroundColor Yellow
git commit -m "Initial commit: SJ-DAS - Smart Jacquard Design Automation System with AI capabilities, performance optimizations, and premium UI/UX"
Write-Host "✅ Commit created" -ForegroundColor Green

Write-Host ""
Write-Host "Adding remote repository..." -ForegroundColor Yellow
git remote add origin https://github.com/BalajiKoushik01/SJDAS.git
Write-Host "✅ Remote added" -ForegroundColor Green

Write-Host ""
Write-Host "Renaming branch to main..." -ForegroundColor Yellow
git branch -M main
Write-Host "✅ Branch renamed" -ForegroundColor Green

Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "You will be prompted for credentials:" -ForegroundColor Cyan
Write-Host "  Username: BalajiKoushik01" -ForegroundColor White
Write-Host "  Password: Use your Personal Access Token (not GitHub password)" -ForegroundColor White
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your code is now on GitHub at:" -ForegroundColor Green
    Write-Host "https://github.com/BalajiKoushik01/SJDAS" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Verify your code on GitHub" -ForegroundColor White
    Write-Host "2. Set repository to Private (if selling)" -ForegroundColor White
    Write-Host "3. Use Jules to fix remaining bugs" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Push failed!" -ForegroundColor Red
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "- Wrong credentials (use Personal Access Token)" -ForegroundColor White
    Write-Host "- Repository already has content" -ForegroundColor White
    Write-Host "- Network issues" -ForegroundColor White
    Write-Host ""
}

Read-Host "Press Enter to exit"

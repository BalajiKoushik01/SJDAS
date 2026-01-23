# Quick Upload Script - Run this in PowerShell

# Kill any running git processes
taskkill /F /IM git.exe 2>$null

# Remove old .git folder
Remove-Item ".git" -Recurse -Force -ErrorAction SilentlyContinue

# Initialize fresh repository
& "C:\Program Files\Git\bin\git.exe" init
& "C:\Program Files\Git\bin\git.exe" config user.name "BalajiKoushik01"
& "C:\Program Files\Git\bin\git.exe" config user.email "balajikoushik01@gmail.com"

# Add files (excluding venv)
& "C:\Program Files\Git\bin\git.exe" add --all

# Commit
& "C:\Program Files\Git\bin\git.exe" commit -m "Initial commit: SJ-DAS"

# Add remote
& "C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/BalajiKoushik01/SJDAS.git

# Push
& "C:\Program Files\Git\bin\git.exe" branch -M main
& "C:\Program Files\Git\bin\git.exe" push -u origin main

Write-Host "Done! Check https://github.com/BalajiKoushik01/SJDAS" -ForegroundColor Green

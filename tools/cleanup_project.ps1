$pathsToDelete = @(
    "jules.log",
    "sj_das.log",
    "error_log.txt",
    "bandit_report.json",
    ".coverage",
    "verification_results.txt",
    "benchmark_results.json",
    "temp_results",
    "htmlcov",
    "integration_test_output",
    "legacy_backup",
    "legacy_experiments",
    "check_icons.py",
    "debug_attributes.py",
    "fix_menu_bug.py",
    "runs"
)

foreach ($path in $pathsToDelete) {
    if (Test-Path $path) {
        Write-Host "Deleting $path..."
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Clean web cache if exists
if (Test-Path "web/.next") {
    Write-Host "Cleaning web build cache..."
    Remove-Item -Path "web/.next" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Cleanup Complete."

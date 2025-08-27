# Bank Communication System - Complete Cleanup Script
# Run this in VS Code Terminal (PowerShell)
# This will identify and remove ALL redundant files

param(
    [string]$ProjectPath = (Get-Location).Path,
    [switch]$DryRun = $false  # Set to $true to preview without deleting
)

# Configuration
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = "$env:USERPROFILE\.project-cleanup-backup"
$backupPath = "$backupRoot\FULL_BACKUP_$timestamp"
$reportPath = "$backupRoot\reports"

# Create directories
@($backupRoot, $reportPath) | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

Write-Host "`n" -NoNewline
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "       BANK COMMUNICATION SYSTEM - COMPLETE CLEANUP TOOL        " -ForegroundColor Yellow
Write-Host "                    VS Code Edition - Step 1                    " -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n⚠️  DRY RUN MODE - No files will be deleted" -ForegroundColor Yellow
}

# Function to get file size
function Get-ReadableSize {
    param([long]$Size)
    if ($Size -gt 1MB) { return "{0:N2} MB" -f ($Size / 1MB) }
    elseif ($Size -gt 1KB) { return "{0:N2} KB" -f ($Size / 1KB) }
    else { return "$Size bytes" }
}

# Step 1: Create Complete Backup
Write-Host "`n📦 CREATING COMPLETE BACKUP..." -ForegroundColor Yellow
Write-Host "   Location: $backupPath" -ForegroundColor Gray

if (-not $DryRun) {
    try {
        Copy-Item -Path $ProjectPath -Destination $backupPath -Recurse -Force -ErrorAction Stop
        $backupSize = (Get-ChildItem -Path $backupPath -Recurse -File | Measure-Object -Property Length -Sum).Sum
        Write-Host "   ✅ Backup created: $(Get-ReadableSize $backupSize)" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Backup failed: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "   ⏭️  Skipped (Dry Run)" -ForegroundColor Gray
}

# Define what to KEEP (everything else gets reviewed for deletion)
$essentialFiles = @{
    "Core Application" = @(
        "src\main.py",
        "src\config.py",
        "requirements.txt",
        ".env",
        ".env.example",
        "README.md",
        "PROJECT_STATUS.md"
    )
    "Core Pages (3 only)" = @(
        "src\communication_processing\customer_analysis.py",
        "src\communication_processing\letter_scanner.py",
        "src\communication_processing\customer_plans_ui.py"
    )
    "Essential Modules" = @(
        "src\api\claude_api.py",
        "src\api\openai_api.py",
        "src\api\api_manager.py",
        "src\api\__init__.py",
        "src\api\video_api.py",  # If you use video features
        "src\business_rules\*.py",
        "src\ui\professional_theme.py",
        "src\communication_processing\__init__.py",
        "src\communication_processing\tabs\generate_tab.py",  # Core functionality
        "src\communication_processing\cost_configuration.py"  # If still needed
    )
    "Data Structure" = @(
        "data\.gitkeep",
        ".gitignore",
        ".streamlit\config.toml"
    )
}

# Define what to DELETE
$deletePatterns = @{
    "All Backup Folders" = @(
        "backups\*"
    )
    "All Fix Scripts" = @(
        "fix_*.py",
        "automatic_fix*.py"
    )
    "Test Files (except test_system.py)" = @(
        "test_api_simple.py",
        "test_end_to_end.py", 
        "test_rules.py",
        "test_professional_ui.py",
        "simple_spanish_test.py",
        "make_test_optional.py",
        "create_test_dataset.py"
    )
    "Unused Modules" = @(
        "src\communication_processing\batch_ui.py",
        "src\communication_processing\batch_planner.py",
        "src\communication_processing\cost_integration.py",
        "src\communication_processing\cost_controller.py"
    )
    "Old/Backup Files" = @(
        "*_old.py",
        "*_backup.py",
        "*.backup",
        "*_copy.py"
    )
    "Documentation to Remove" = @(
        "CLAUDE_INSTRUCTIONS.md"
    )
    "Cache and Temp" = @(
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        "*.log"
    )
}

# Scan all files
Write-Host "`n🔍 SCANNING PROJECT..." -ForegroundColor Yellow
$allFiles = Get-ChildItem -Path $ProjectPath -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notlike "*\.git\*" }

$totalFiles = $allFiles.Count
$totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum

Write-Host "   Total files: $totalFiles" -ForegroundColor White
Write-Host "   Total size: $(Get-ReadableSize $totalSize)" -ForegroundColor White

# Categorize files
$filesToDelete = @()
$filesToKeep = @()
$filesToReview = @()

foreach ($file in $allFiles) {
    $relativePath = $file.FullName.Replace($ProjectPath + "\", "")
    $shouldKeep = $false
    $shouldDelete = $false
    $deleteReason = ""
    
    # Check if it's essential
    foreach ($category in $essentialFiles.Keys) {
        foreach ($pattern in $essentialFiles[$category]) {
            if ($relativePath -like $pattern) {
                $shouldKeep = $true
                break
            }
        }
        if ($shouldKeep) { break }
    }
    
    # Check if it should be deleted
    if (-not $shouldKeep) {
        foreach ($category in $deletePatterns.Keys) {
            foreach ($pattern in $deletePatterns[$category]) {
                if ($relativePath -like $pattern -or $file.Name -like $pattern) {
                    $shouldDelete = $true
                    $deleteReason = $category
                    break
                }
            }
            if ($shouldDelete) { break }
        }
    }
    
    # Special check for backups folder
    if ($relativePath -like "backups\*") {
        $shouldDelete = $true
        $deleteReason = "All Backup Folders"
    }
    
    # Categorize
    if ($shouldKeep) {
        $filesToKeep += [PSCustomObject]@{
            Path = $relativePath
            Size = Get-ReadableSize $file.Length
        }
    } elseif ($shouldDelete) {
        $filesToDelete += [PSCustomObject]@{
            Path = $relativePath
            Size = Get-ReadableSize $file.Length
            Reason = $deleteReason
        }
    } else {
        $filesToReview += [PSCustomObject]@{
            Path = $relativePath
            Size = Get-ReadableSize $file.Length
        }
    }
}

# Display results
Write-Host "`n" -NoNewline
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "                         ANALYSIS RESULTS                       " -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "`n📊 SUMMARY:" -ForegroundColor Cyan
Write-Host "   ✅ Files to KEEP: $($filesToKeep.Count)" -ForegroundColor Green
Write-Host "   ❌ Files to DELETE: $($filesToDelete.Count)" -ForegroundColor Red
Write-Host "   ❓ Files to REVIEW: $($filesToReview.Count)" -ForegroundColor Yellow

# Show files to delete grouped by reason
if ($filesToDelete.Count -gt 0) {
    Write-Host "`n🗑️ FILES TO DELETE:" -ForegroundColor Red
    $grouped = $filesToDelete | Group-Object Reason
    foreach ($group in $grouped) {
        Write-Host "`n   [$($group.Name)] - $($group.Count) files" -ForegroundColor Magenta
        foreach ($file in $group.Group | Select-Object -First 5) {
            Write-Host "      • $($file.Path)" -ForegroundColor Gray
        }
        if ($group.Count -gt 5) {
            Write-Host "      ... and $($group.Count - 5) more" -ForegroundColor DarkGray
        }
    }
}

# Show files to review (if not too many)
if ($filesToReview.Count -gt 0 -and $filesToReview.Count -le 20) {
    Write-Host "`n❓ FILES TO REVIEW MANUALLY:" -ForegroundColor Yellow
    foreach ($file in $filesToReview) {
        Write-Host "   • $($file.Path)" -ForegroundColor Gray
    }
}

# Calculate space savings
$deleteSize = 0
foreach ($file in $filesToDelete) {
    $fullPath = Join-Path $ProjectPath $file.Path
    if (Test-Path $fullPath) {
        $deleteSize += (Get-Item $fullPath).Length
    }
}

Write-Host "`n💾 SPACE SAVINGS:" -ForegroundColor Cyan
Write-Host "   Current total: $(Get-ReadableSize $totalSize)" -ForegroundColor White
Write-Host "   To be deleted: $(Get-ReadableSize $deleteSize)" -ForegroundColor Red
Write-Host "   After cleanup: $(Get-ReadableSize ($totalSize - $deleteSize))" -ForegroundColor Green
$reduction = if ($totalSize -gt 0) { [math]::Round(($deleteSize / $totalSize) * 100, 1) } else { 0 }
Write-Host "   Reduction: $reduction%" -ForegroundColor Yellow

# Save detailed report
$report = @{
    Timestamp = $timestamp
    TotalFiles = $totalFiles
    FilesToKeep = $filesToKeep.Count
    FilesToDelete = $filesToDelete.Count
    FilesToReview = $filesToReview.Count
    SpaceSaved = $deleteSize
    DeleteList = $filesToDelete
    ReviewList = $filesToReview
}

$reportFile = "$reportPath\cleanup_report_$timestamp.json"
$report | ConvertTo-Json -Depth 10 | Out-File $reportFile

Write-Host "`n📄 Detailed report saved to:" -ForegroundColor Cyan
Write-Host "   $reportFile" -ForegroundColor White

# Action prompt
Write-Host "`n" -NoNewline
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "                         READY TO CLEAN?                        " -ForegroundColor Yellow  
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n✅ DRY RUN COMPLETE - No files were deleted" -ForegroundColor Green
    Write-Host "`nTo execute the cleanup, run:" -ForegroundColor Yellow
    Write-Host "   .\Cleanup-Step1.ps1" -ForegroundColor White
} else {
    Write-Host "`n⚠️  WARNING: This will delete $($filesToDelete.Count) files!" -ForegroundColor Yellow
    Write-Host "   Backup saved at: $backupPath" -ForegroundColor Green
    
    $confirm = Read-Host "`nType 'CLEAN' to proceed with deletion, or press Enter to exit"
    
    if ($confirm -eq 'CLEAN') {
        Write-Host "`n🧹 CLEANING..." -ForegroundColor Yellow
        
        $deleted = 0
        $failed = 0
        
        foreach ($file in $filesToDelete) {
            $fullPath = Join-Path $ProjectPath $file.Path
            try {
                if (Test-Path $fullPath) {
                    Remove-Item $fullPath -Force -Recurse -ErrorAction Stop
                    $deleted++
                    Write-Host "   ✓ Deleted: $($file.Path)" -ForegroundColor DarkGray
                }
            } catch {
                $failed++
                Write-Host "   ✗ Failed: $($file.Path) - $_" -ForegroundColor Red
            }
        }
        
        # Clean empty directories
        Get-ChildItem $ProjectPath -Recurse -Directory | 
            Where-Object { (Get-ChildItem $_.FullName -Recurse -File).Count -eq 0 } |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        
        Write-Host "`n✅ CLEANUP COMPLETE!" -ForegroundColor Green
        Write-Host "   Deleted: $deleted files" -ForegroundColor Green
        if ($failed -gt 0) {
            Write-Host "   Failed: $failed files" -ForegroundColor Red
        }
        
        # Final file count
        $remainingFiles = (Get-ChildItem -Path $ProjectPath -Recurse -File | 
            Where-Object { $_.FullName -notlike "*\.git\*" }).Count
        Write-Host "`n📊 FINAL STATUS:" -ForegroundColor Cyan
        Write-Host "   Files before: $totalFiles" -ForegroundColor White
        Write-Host "   Files after: $remainingFiles" -ForegroundColor Green
        Write-Host "   Files removed: $($totalFiles - $remainingFiles)" -ForegroundColor Yellow
    } else {
        Write-Host "`n❌ Cleanup cancelled" -ForegroundColor Yellow
        Write-Host "   No files were deleted" -ForegroundColor White
    }
}

Write-Host "`n💡 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "   1. Test your application: python -m streamlit run src\main.py" -ForegroundColor White
Write-Host "   2. Verify the 3 core pages work correctly" -ForegroundColor White
Write-Host "   3. Review any files in the 'review' category" -ForegroundColor White
Write-Host "   4. Commit your clean codebase to Git" -ForegroundColor White
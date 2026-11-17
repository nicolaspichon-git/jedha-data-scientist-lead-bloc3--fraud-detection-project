<#
.VERSION 0.4
.SYNOPSIS
    Converts a list of Mermaid diagrams (.md) into PNG images using mmdc (Mermaid CLI).

.DESCRIPTION
    This script loads a list of (file path, width) pairs from a text file passed as a
    parameter, then iterates over that list to convert each Mermaid file into a PNG
    using the following command template:
        mmdc -i '<path>' -o '.\<basename>.png' --width <width>

    Since the input files are Markdown (.md) files containing a ```mermaid code block
    (so they still preview correctly in VS Code / Obsidian), mmdc automatically numbers
    the diagram it extracts (e.g. "basename-1.png"). This script renames that file back
    to "basename.png" after each conversion.

.PARAMETER ListFile
    Path to a text file containing one entry per line, formatted as:
        <file path>,<width>
    The width is optional: if omitted (no comma, or an empty value after the comma),
    the default width (2480) is used. Blank lines and lines starting with '#' are ignored.

    Example file content:
        C:\diagrams\architecture.md,1200
        C:\diagrams\sequence.md,800
        C:\diagrams\overview.md
        .\user-flow.md,

.EXAMPLE
    .\mermaid-to-png--v3.ps1 -ListFile ".\diagrams-list.txt"

.PREREQUISITES
    - Node.js installed
    - Mermaid CLI installed globally: npm install -g @mermaid-js/mermaid-cli
    - To allow local script execution:
        Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ListFile,

    [int]$DefaultWidth = 2480
)

# --- Check that the list file exists ---
if (-not (Test-Path -LiteralPath $ListFile)) {
    Write-Error "List file not found: $ListFile"
    exit 1
}

# --- Load the list of (file path, width) pairs from the text file ---
$diagrams = @()

Get-Content -LiteralPath $ListFile | ForEach-Object {
    $line = $_.Trim()

    # Skip blank lines and comments
    if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith('#')) {
        return
    }

    $parts = $line -split ','

    if ($parts.Count -gt 2) {
        Write-Warning "Malformed line, skipped: '$line'"
        return
    }

    $path      = $parts[0].Trim()
    $widthText = if ($parts.Count -eq 2) { $parts[1].Trim() } else { '' }

    if ([string]::IsNullOrWhiteSpace($widthText)) {
        # No width specified on this line: fall back to the default width
        $width = $DefaultWidth
    }
    elseif ($widthText -as [int]) {
        $width = [int]$widthText
    }
    else {
        Write-Warning "Invalid width, skipped: '$line'"
        return
    }

    $diagrams += [PSCustomObject]@{
        Path  = $path
        Width = $width
    }
}

if ($diagrams.Count -eq 0) {
    Write-Warning "No valid entries found in '$ListFile'. Nothing to convert."
    exit 0
}

# --- Iterate over the list and convert each file ---
foreach ($diagram in $diagrams) {

    $path  = $diagram.Path
    $width = $diagram.Width

    if (-not (Test-Path -LiteralPath $path)) {
        Write-Warning "File not found, skipped: $path"
        continue
    }

    $basename   = [System.IO.Path]::GetFileNameWithoutExtension($path)
    $outputPath = ".\$basename.png"

    # When the input is a .md file, mmdc treats it as Markdown and numbers each
    # diagram it finds (e.g. "basename-1.png"), even if there is only one. This
    # is the name mmdc will actually produce for the first diagram in the file.
    $numberedOutputPath = ".\$basename-1.png"

    Write-Host "Converting '$path' -> '$outputPath' (width: $width px)" -ForegroundColor Cyan

    try {
        mmdc -i "$path" -o "$outputPath" --width $width

        if ($LASTEXITCODE -eq 0) {
            if (Test-Path -LiteralPath $numberedOutputPath) {
                # Strip the "-1" suffix added by mmdc so the file matches $outputPath
                Move-Item -LiteralPath $numberedOutputPath -Destination $outputPath -Force

                if (Test-Path -LiteralPath ".\$basename-2.png") {
                    Write-Warning "  -> Multiple diagrams found in '$path'; only the first one was kept as '$outputPath'"
                }
            }
            Write-Host "  -> OK" -ForegroundColor Green
        } else {
            Write-Warning "  -> mmdc returned an error code ($LASTEXITCODE) for '$path'"
        }
    }
    catch {
        Write-Error "  -> Conversion failed for '$path': $_"
    }
}

Write-Host "`nConversion complete." -ForegroundColor Yellow
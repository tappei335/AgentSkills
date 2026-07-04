param(
    [string[]]$SkillName = @(),
    [string]$SourceRoot,
    [string]$DestinationRoot,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $executionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
}

function Get-DefaultDestinationRoot {
    if ($env:CODEX_HOME) {
        return (Join-Path $env:CODEX_HOME "skills")
    }

    return (Join-Path $HOME ".codex\skills")
}

function Test-PathInside {
    param(
        [Parameter(Mandatory = $true)][string]$Child,
        [Parameter(Mandatory = $true)][string]$Parent
    )

    $normalizedParent = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\', '/')
    $normalizedChild = [System.IO.Path]::GetFullPath($Child).TrimEnd('\', '/')
    return $normalizedChild.Equals($normalizedParent, [System.StringComparison]::OrdinalIgnoreCase) -or
        $normalizedChild.StartsWith($normalizedParent + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-FullPath (Join-Path $scriptDir "..")

if (-not $SourceRoot) {
    $SourceRoot = Join-Path $repoRoot "codex"
}

if (-not $DestinationRoot) {
    $DestinationRoot = Get-DefaultDestinationRoot
}

$sourceRootFull = Resolve-FullPath $SourceRoot
$destinationRootFull = [System.IO.Path]::GetFullPath($DestinationRoot)

if (-not (Test-Path -LiteralPath $sourceRootFull -PathType Container)) {
    throw "Source directory not found: $sourceRootFull"
}

$normalizedSkillNames = @()
foreach ($rawName in $SkillName) {
    $normalizedSkillNames += $rawName -split ","
}

$skillNameFilter = @{}
foreach ($name in $normalizedSkillNames) {
    $name = $name.Trim()
    if (-not $name) {
        continue
    }
    $skillNameFilter[$name] = $true
}

$sourceSkills = Get-ChildItem -LiteralPath $sourceRootFull -Directory |
    Sort-Object Name |
    Where-Object {
        $skillNameFilter.Count -eq 0 -or $skillNameFilter.ContainsKey($_.Name)
    }

if (-not $sourceSkills) {
    if ($skillNameFilter.Count -gt 0) {
        throw "No matching skills found under $sourceRootFull"
    }

    Write-Host "No Codex skills found under $sourceRootFull"
    exit 0
}

Write-Host "Importing Codex skills:"
Write-Host "  from $sourceRootFull"
Write-Host "  to   $destinationRootFull"

if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path $destinationRootFull | Out-Null
}

foreach ($sourceSkill in $sourceSkills) {
    $skillMd = Join-Path $sourceSkill.FullName "SKILL.md"
    if (-not (Test-Path -LiteralPath $skillMd -PathType Leaf)) {
        Write-Warning "Skipping $($sourceSkill.Name): missing SKILL.md"
        continue
    }

    $destinationSkill = Join-Path $destinationRootFull $sourceSkill.Name
    if (-not (Test-PathInside -Child $destinationSkill -Parent $destinationRootFull)) {
        throw "Refusing to write outside destination root: $destinationSkill"
    }

    Write-Host "  - $($sourceSkill.Name)"

    if ($DryRun) {
        continue
    }

    $tempParent = Join-Path $destinationRootFull (".import-{0}-{1}" -f $sourceSkill.Name, [System.Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tempParent | Out-Null

    try {
        $tempSkill = Join-Path $tempParent $sourceSkill.Name
        Copy-Item -LiteralPath $sourceSkill.FullName -Destination $tempSkill -Recurse -Force

        if (Test-Path -LiteralPath $destinationSkill) {
            Remove-Item -LiteralPath $destinationSkill -Recurse -Force
        }

        Move-Item -LiteralPath $tempSkill -Destination $destinationSkill
    }
    finally {
        if (Test-Path -LiteralPath $tempParent) {
            Remove-Item -LiteralPath $tempParent -Recurse -Force
        }
    }
}

if ($DryRun) {
    Write-Host "Dry run complete. No files were copied."
}
else {
    Write-Host "Import complete. Restart Codex to pick up new skills."
}

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArgs
)

$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

$tempRoot = Join-Path $RootDir '.tmp'
New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null
$pytestBaseTemp = Join-Path $tempRoot ('pytest-basetemp-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $pytestBaseTemp | Out-Null
$env:TEMP = $tempRoot
$env:TMP = $tempRoot
$env:TMPDIR = $tempRoot

$envFile = Join-Path $RootDir '.env'
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith('#')) {
            return
        }
        $parts = $line -split '=', 2
        if ($parts.Count -eq 2) {
            $name = $parts[0].Trim()
            $value = $parts[1].Trim()
            if ($name -and -not [string]::IsNullOrWhiteSpace($name)) {
                if (-not [System.Environment]::GetEnvironmentVariable($name)) {
                    [System.Environment]::SetEnvironmentVariable($name, $value, 'Process')
                }
            }
        }
    }
}

$python = Join-Path $RootDir '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

if (-not $PytestArgs -or $PytestArgs.Count -eq 0) {
    $PytestArgs = @('-vv', '-s')
} else {
    $joinedArgs = ($PytestArgs -join ' ')
    if ($joinedArgs -notmatch '(^|[\s])(-q|-v|-vv|-s|--capture=)') {
        $PytestArgs = @('-vv', '-s') + $PytestArgs
    }
}

Write-Host "Python:"
Write-Host "  $python"
Write-Host "PYTHONPATH:"
Write-Host "  $env:PYTHONPATH"

& $python -m pytest "--basetemp=$pytestBaseTemp" @PytestArgs
exit $LASTEXITCODE

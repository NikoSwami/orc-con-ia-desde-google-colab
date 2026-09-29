param([switch]$Cpu)

$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
$venv = Join-Path $raiz '.venv'
$req = if ($Cpu) { 'requirements-cpu.txt' } else { 'requirements.txt' }

if (-not (Test-Path $venv)) {
    Write-Host "Creando entorno virtual en $venv"
    python -m venv $venv
}

$py = Join-Path $venv 'Scripts\python.exe'

& $py -m pip install --upgrade pip --quiet
& $py -m pip install --timeout 180 --retries 10 -r (Join-Path $raiz $req)

Write-Host ""
Write-Host "Listo. Para usarlo:"
Write-Host "  $venv\Scripts\Activate.ps1"
Write-Host "  python ocr_local.py mis_pdfs\"

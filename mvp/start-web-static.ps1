$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\web
npm.cmd install
npm.cmd run build
Set-Location .\dist
python -m http.server 4181 --bind 127.0.0.1

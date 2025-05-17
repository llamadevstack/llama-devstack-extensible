Write-Host "Patching rwkv/model.py to support PyTorch 2.6+..."

$patchPath = ".\venv\Lib\site-packages\rwkv\model.py"

if (Test-Path $patchPath) {
    (Get-Content $patchPath) -replace "torch\.load\(args\.MODEL_NAME, map_location='cpu'\)", "torch.load(args.MODEL_NAME, map_location='cpu', weights_only=False)" |
        Set-Content $patchPath
    Write-Host "Patch applied successfully."
} else {
    Write-Host "Error: Could not find rwkv/model.py to patch." -ForegroundColor Red
}

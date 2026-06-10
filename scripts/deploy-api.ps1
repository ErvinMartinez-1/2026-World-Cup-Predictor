# Deploys the API + infrastructure stack (Lambda, API Gateway, S3, CloudFront).
# Prereqs: AWS CLI configured, SAM CLI installed, Docker Desktop running.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent

# Stage the pre-computed result JSONs into the Lambda bundle.
New-Item -ItemType Directory -Force "$root\worldcup_predictor\api\data\results" | Out-Null
Copy-Item "$root\worldcup_predictor\data\results\*.json" "$root\worldcup_predictor\api\data\results\" -Force

Set-Location $root
sam build --use-container
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
sam deploy

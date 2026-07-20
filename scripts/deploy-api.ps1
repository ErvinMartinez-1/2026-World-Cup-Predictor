# Deploys the API + infrastructure stack (Lambda, API Gateway, S3, CloudFront).
# Prereqs: AWS CLI configured, SAM CLI installed, Docker Desktop running.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent

$apiResults = Join-Path $root 'worldcup_predictor/api/data/results'
New-Item -ItemType Directory -Force $apiResults | Out-Null
Copy-Item (Join-Path $root 'worldcup_predictor/data/results/*.json') $apiResults -Force

Set-Location $root
# In CI the runner is already Linux x86_64 (matches the Lambda runtime) so the container build is only needed locally on Windows to produce Linux wheels.
if ($env:CI) { sam build } else { sam build --use-container }
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
# CI is non-interactive, so skip the changeset confirmation prompt.
if ($env:CI) { sam deploy --no-confirm-changeset } else { sam deploy }

# Builds the frontend and syncs it to S3, then invalidates CloudFront.
# Prereqs: API stack deployed (deploy-api.ps1), frontend/.env.production
# containing VITE_API_BASE_URL=<ApiUrl output of the stack>.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$stack = "worldcup-predictor"

$bucket = aws cloudformation describe-stacks --stack-name $stack --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" --output text
$distId = aws cloudformation describe-stacks --stack-name $stack --query "Stacks[0].Outputs[?OutputKey=='DistributionId'].OutputValue" --output text
if (-not $bucket -or -not $distId) { throw "Could not read stack outputs - is the '$stack' stack deployed?" }

# In CI the gitignored .env.production is absent, so derive VITE_API_BASE_URL
# from the stack's ApiUrl output (also keeps the committed value from drifting).
$envFile = Join-Path $root 'frontend/.env.production'
if ($env:CI -or -not (Test-Path $envFile)) {
    $apiUrl = aws cloudformation describe-stacks --stack-name $stack --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text
    if (-not $apiUrl) { throw "Could not read ApiUrl output from the '$stack' stack." }
    "VITE_API_BASE_URL=$apiUrl" | Set-Content $envFile
}

Push-Location (Join-Path $root 'frontend')
npm run build
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
Pop-Location

$dist = Join-Path $root 'frontend/dist'
# Hashed Vite assets: cache forever. index.html: never cache (prevents stale SPA).
aws s3 sync $dist "s3://$bucket" --delete --cache-control "public,max-age=31536000,immutable" --exclude "index.html"
aws s3 cp (Join-Path $dist 'index.html') "s3://$bucket/index.html" --cache-control "no-cache"
aws cloudfront create-invalidation --distribution-id $distId --paths "/index.html" "/"

Write-Host "Frontend deployed. URL:"
aws cloudformation describe-stacks --stack-name $stack --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue" --output text

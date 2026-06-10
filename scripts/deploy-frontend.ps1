# Builds the frontend and syncs it to S3, then invalidates CloudFront.
# Prereqs: API stack deployed (deploy-api.ps1), frontend/.env.production
# containing VITE_API_BASE_URL=<ApiUrl output of the stack>.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$stack = "worldcup-predictor"

$bucket = aws cloudformation describe-stacks --stack-name $stack --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" --output text
$distId = aws cloudformation describe-stacks --stack-name $stack --query "Stacks[0].Outputs[?OutputKey=='DistributionId'].OutputValue" --output text
if (-not $bucket -or -not $distId) { throw "Could not read stack outputs - is the '$stack' stack deployed?" }

Push-Location "$root\frontend"
npm run build
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
Pop-Location

# Hashed Vite assets: cache forever. index.html: never cache (prevents stale SPA).
aws s3 sync "$root\frontend\dist" "s3://$bucket" --delete --cache-control "public,max-age=31536000,immutable" --exclude "index.html"
aws s3 cp "$root\frontend\dist\index.html" "s3://$bucket/index.html" --cache-control "no-cache"
aws cloudfront create-invalidation --distribution-id $distId --paths "/index.html" "/"

Write-Host "Frontend deployed. URL:"
aws cloudformation describe-stacks --stack-name $stack --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue" --output text

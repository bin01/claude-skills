#!/usr/bin/env bash
# 30 service configs for a rename plus a scoped change.
set -euo pipefail
i=0
for svc in billing search auth orders inventory notify payments users reports gateway; do
  for env in prod staging dev; do
    i=$((i+1)); mkdir -p services/$svc/$env
    cat > services/$svc/$env/config.yaml <<YML
service: $svc
environment: $env
region: us-east-1
replicas: 2
http:
  port: $((8000 + i))
  timeout_ms: $((1000 + i * 250))
  retries: 3
logging:
  level: info
YML
  done
done

#!/usr/bin/env bash
# Pinned redis-py checkout used by the code-reading cases.
set -euo pipefail
SHA=f5aedb4033b4b87e6d662896f9115f75ddd54968
git init -q redis-py
git -C redis-py remote add origin https://github.com/redis/redis-py.git
git -C redis-py fetch -q --depth 1 origin "$SHA"
git -C redis-py checkout -q FETCH_HEAD

#!/bin/sh
# Package models, data, docs and src into a tar.gz archive

set -e

OUTPUT=${1:-proai_package.tar.gz}

mkdir -p package_temp
cp -r models data docs src README.md package_temp/
tar -czf "$OUTPUT" -C package_temp .
rm -rf package_temp

echo "Package created: $OUTPUT"

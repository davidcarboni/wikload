#!/usr/bin/env bash

export GITHUB_USERNAME=davidcarboni
export GITHUB_ACCESS_TOKEN=$(cat credentials/token.txt)
export GITHUB_REPO=carboni/carboni.github.io

# Run as a container for local test/development
docker build --tag gikki . && \
docker run -it --rm -p 5000:5000 \
    -e USERNAME=wiki \
    -e PASSWORD=123 \
    -e NOSSL=true \
    -e GITHUB_USERNAME \
    -e GITHUB_ACCESS_TOKEN \
    -e GITHUB_REPO \
    gikki

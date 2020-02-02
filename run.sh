#!/usr/bin/env bash

export GITHUB_REPO=carboni/carboni.github.io
export WIKI_TITLE=$GITHUB_REPO

# Run as a container for local test/development
docker build --tag wikload . && \
docker run -it --rm -p 5000:5000 \
    -e USERNAME=wiki \
    -e PASSWORD=123 \
    -e NOSSL=true \
    -e GITHUB_USERNAME \
    -e GITHUB_ACCESS_TOKEN \
    -e GITHUB_REPO \
    -e WIKI_TITLE \
    wikload

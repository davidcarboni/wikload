#!/usr/bin/env bash

# Run as a container for local test/development
docker build --tag govwiki . && \
docker run -it --rm -e USERNAME=wiki -e PASSWORD=123 -p 5000:5000 govwiki

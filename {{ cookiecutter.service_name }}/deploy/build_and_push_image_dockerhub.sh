#!/bin/bash

# login first: docker login -u "dotsenergyframework
VERSION=0.0.1
# CHANGE THE REPOSITORY:
REPOSITORY=""dotsenergyframework/pv_installation_service"

docker build -t ${REPOSITORY}:${VERSION} ./..

docker push ${REPOSITORY}:${VERSION}

#!/bin/bash

# login first: docker login -u <ci.tno.nl email address> ci.tno.nl
VERSION=0.0.1
# CHANGE THE REPOSITORY:
REPOSITORY="ci.tno.nl/dots/go-e/pv_installation_service"

docker build -t ${REPOSITORY}:${VERSION} ./..

docker push ${REPOSITORY}:${VERSION}

#!/bin/bash

# login first: docker login -u <ci.tno.nl email address> ci.tno.nl

VERSION=0.0.5
REPOSITORY="ci.tno.nl/dots/calculation-service-generator"

docker build -t ${REPOSITORY}:${VERSION} ./..

docker push ${REPOSITORY}:${VERSION}

#FROM ubuntu:18.04
#
#RUN apt-get update
#RUN apt-get install -y software-properties-common
#RUN add-apt-repository -y ppa:deadsnakes/ppa
#
#RUN apt-get update
#RUN apt-get install -y curl
#RUN apt-get install -y python3.9
#RUN apt-get install -y python3.9-distutils
#
#RUN apt-get install -y protobuf-compiler
#
#WORKDIR /usr/src/app
#COPY . .
#RUN mkdir -p input
#RUN mkdir -p output
#
#RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
#RUN python3.9 get-pip.py

FROM python:3.9

RUN apt-get update
RUN apt-get install -y protobuf-compiler

WORKDIR /usr/src/app
COPY . .
RUN mkdir -p input
RUN mkdir -p output
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/bin/bash", "./build.sh"]
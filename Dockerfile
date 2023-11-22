FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa  

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y python3.10
RUN apt-get install -y python3.10-distutils

RUN apt-get install -y protobuf-compiler

WORKDIR /usr/src/app
COPY . .
RUN mkdir -p input
RUN mkdir -p output

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.10 get-pip.py
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/bin/bash", "./build.sh"]
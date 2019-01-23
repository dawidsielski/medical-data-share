FROM ubuntu:18.04

MAINTAINER Dawid Sielski "dawid.sielski@outlook.com"

RUN apt-get update -y

RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && \
apt-get update && apt-get install -y python3.6 python3.6-dev python3-pip

RUN ln -sfn /usr/bin/python3.6 /usr/bin/python3 && ln -sfn /usr/bin/python3 /usr/bin/python && ln -sfn /usr/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip

RUN apt-get install -y tabix
COPY . /app

WORKDIR /app
RUN pip install -r requirements.txt

# CMD ["python", "app.py"]


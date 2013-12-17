# RulzUrAPI
#
# VERSION               0.0.1

FROM      ubuntu
MAINTAINER Maxime Vidori <maxime.vidori@gmail.com>

# make sure the package repository is up to date
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y python-pip

ADD . app

RUN pip install -r app/requirements.txt

WORKDIR app
CMD ["python", "app.py"]

EXPOSE 5000

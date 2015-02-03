# RulzUrAPI
#
# VERSION               0.0.1

FROM       debian:testing
MAINTAINER Maxime Vidori <maxime.vidori@gmail.com>

COPY requirements.txt /opt/requirements/
COPY requirements-tests.txt /opt/requirements/
COPY misc/default_app.py /opt/rulzurapi/src/app.py

ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBUG 1

ENV WORKDIR /opt/rulzurapi
ENV PYTHONPATH ${WORKDIR}/src

# make sure the package repository is up to date
RUN echo "deb http://ftp.fr.debian.org/debian testing main" > \
    /etc/apt/sources.list
RUN echo "deb http://ftp.debian.org/debian/ testing-updates main" >> \
   /etc/apt/sources.list

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y gcc python3 python3-pip libpq-dev

RUN pip3 install -r /opt/requirements/requirements.txt
RUN pip3 install -r /opt/requirements/requirements-tests.txt

EXPOSE 5000

WORKDIR ${WORKDIR}

CMD ["/usr/bin/python3", "src/app.py"]

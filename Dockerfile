# RulzUrAPI
#
# VERSION               0.0.1

FROM       debian
MAINTAINER Maxime Vidori <maxime.vidori@gmail.com>

COPY requirements.txt /opt/requirements/
COPY requirements-tests.txt /opt/requirements/
COPY misc/default_app.py /opt/rulzurapi/src/app.py

ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBUG 1

ENV VENVPATH /opt/venv
ENV PATH ${VENVPATH}/bin:${PATH}

ENV WORKDIR /opt/rulzurapi
ENV PYTHONPATH ${WORKDIR}/src

# make sure the package repository is up to date
RUN echo "deb http://ftp.fr.debian.org/debian stable main" > /etc/apt/sources.list
RUN echo "deb http://ftp.debian.org/debian/ wheezy-updates main" >> /etc/apt/sources.list

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y gcc python-virtualenv python-dev libpq-dev
RUN virtualenv ${VENVPATH}

RUN pip install -r /opt/requirements/requirements.txt
RUN pip install -r /opt/requirements/requirements-tests.txt

EXPOSE 5000

WORKDIR ${WORKDIR}

ENTRYPOINT ["ipython"]
CMD ["src/app.py"]

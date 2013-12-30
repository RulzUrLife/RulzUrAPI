# RulzUrAPI
#
# VERSION               0.0.1

FROM      ubuntu
MAINTAINER Maxime Vidori <maxime.vidori@gmail.com>

# make sure the package repository is up to date
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

# installations first for the cache
RUN apt-get install -y nginx supervisor build-essential
RUN apt-get install -y python-pip python-dev
RUN pip install uwsgi

# copy config files before
ADD uwsgi_params /home/docker/

# pip installation
ADD uwsgi.ini /home/docker/app/
ADD requirements.txt /home/docker/app/
RUN pip install -r /home/docker/app/requirements.txt

# copy content of the project
ADD app.py /home/docker/app/
ADD api /home/docker/app/api

# copy configuration files
ADD nginx-rulzurapi.conf /etc/nginx/sites-available/
ADD supervisor-rulzurapi.conf /etc/supervisor/conf.d/


# nginx configuration
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /etc/nginx/sites-available/nginx-rulzurapi.conf /etc/nginx/sites-enabled
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

EXPOSE 80
CMD ["supervisord", "-n"]

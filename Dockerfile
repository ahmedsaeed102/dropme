# base image  
FROM ubuntu:20.04
# FROM python:ubuntu
RUN apt-get update && \
    apt-get install -y -qq build-essential git zip openssh-client sqlite3 libsqlite3-dev python3.10 wget unzip libpq-dev binutils libproj-dev gdal-bin libsqlite3-mod-spatialite
                            
# setup environment variable  
ARG DockerHOME
# ARG PORT
ARG apikey
ARG EMAIL_HOST_USER
ARG PYTHON_VERSION
ARG SITE_ID
ENV DockerHOME=/app/  

RUN mkdir -p $DockerHOME  

# RUN LDFLAGS="-L/usr/local/opt/sqlite/lib -L/usr/local/opt/zlib/lib" CPPFLAGS="-I/usr/local/opt/sqlite/include -I/usr/local/opt/zlib/include" PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions" pyenv install 3.10.6

WORKDIR /app  

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

# install dependencies  
RUN pip install --upgrade pip  
# RUN /opt/render/project/src/.venv/bin/python -m pip install --upgrade pip
# RUN pip install -r requirements.txt
# copy whole project to your docker home directory. 
COPY . $DockerHOME  
# run this command to install all dependencies  
RUN pip install -r requirements.txt  
# EXPOSE $PORT  
# EXPOSE 7139  
CMD daphne -b 0.0.0.0 -p $PORT core.asgi:application
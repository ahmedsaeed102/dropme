# base image  
FROM python:3.10   

RUN apt-get update && \
    apt-get install -y --no-install-recommends git zip openssh-client sqlite3 libsqlite3-dev
# setup environment variable  
ARG DockerHOME
ARG PORT
ARG apikey
ARG EMAIL_HOST_USER
ARG PYTHON_VERSION
ARG SITE_ID
# ENV DockerHOME=/home/app/  
# set work directory  
RUN mkdir -p $DockerHOME  
RUN sudo apt install gdal-bin
# RUN sudo apt install libsqlite3-mod-spatialite
RUN sudo apt-get install libsqlite3-mod-spatialite

RUN LDFLAGS="-L/usr/local/opt/sqlite/lib -L/usr/local/opt/zlib/lib" CPPFLAGS="-I/usr/local/opt/sqlite/include -I/usr/local/opt/zlib/include" PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions" asdf python install
# where your code lives  
# WORKDIR $DockerHOME  
WORKDIR /app  

# set environment variables  
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1  

# install dependencies  
RUN pip install --upgrade pip  

# copy whole project to your docker home directory. 
COPY . $DockerHOME  
# run this command to install all dependencies  
# RUN pip install -r requirements.txt  
# port where the Django app runs  
EXPOSE $PORT  
# start server  
# CMD python manage.py runserver  
# FROM ubuntu:20.04
FROM ubuntu:focal

RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
ENV TZ 'GB'
RUN echo $TZ > /etc/timezone && \
    apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean
 

RUN apt-get install -y python3.10 python3-pip libgdal-dev locales sqlite3 libsqlite3-dev libsqlite3-mod-spatialite

RUN locale-gen en_GB.UTF-8
ENV LC_ALL='en_GB.utf8'

RUN echo 'alias python=python3' >> ~/.bashrc
RUN echo 'alias pip=pip3' >> ~/.bashrc

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip3 install GDAL==3.6.3

# RUN apt-get update && \
#     apt-get install -y -qq build-essential git zip openssh-client sqlite3 libsqlite3-dev python3.10 wget unzip libpq-dev binutils libproj-dev gdal-bin libsqlite3-mod-spatialite
                            
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

COPY . $DockerHOME  

RUN pip install -r requirements.txt  
# EXPOSE $PORT  
# EXPOSE 7139  
# CMD daphne -b 0.0.0.0 -p $PORT core.asgi:application
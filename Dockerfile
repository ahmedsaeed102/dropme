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


RUN apt-get install -y python3.10 python3-pip locales libpq-dev binutils libproj-dev gdal-bin 

RUN locale-gen en_GB.UTF-8
ENV LC_ALL='en_GB.utf8'

RUN echo 'alias python=python3' >> ~/.bashrc
RUN echo 'alias pip=pip3' >> ~/.bashrc

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal


ARG DockerHOME

ENV DockerHOME=/app/  

RUN mkdir -p $DockerHOME  

WORKDIR $DockerHOME   

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

RUN pip install --upgrade pip

COPY . $DockerHOME  

RUN pip install -r requirements.txt
RUN python manage.py migrate

EXPOSE 7139

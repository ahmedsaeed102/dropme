# base image  
FROM python:3.10   
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
RUN sudo apt install libsqlite3-mod-spatialite
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
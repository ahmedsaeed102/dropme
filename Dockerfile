ARG EMAIL_HOST_USER
ARG EMAIL_HOST_PASSWORD
ARG state
ARG SITE_ID
ARG apikey
ARG db_password
ARG db_host
ARG db_port
ARG db_name
ARG SECRET_KEY
ARG type
ARG project_id
ARG private_key_id
ARG private_key
ARG client_email
ARG client_id
ARG auth_uri
ARG token_uri
ARG auth_provider_x509_cert_url
ARG client_x509_cert_url
ARG AWS_S3_REGION_NAME
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_STORAGE_BUCKET_NAME

FROM ubuntu:latest

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


RUN apt-get install -y python3-pip python3.10 locales libpq-dev binutils libproj-dev gdal-bin nginx supervisor

RUN locale-gen en_GB.UTF-8
ENV LC_ALL='en_GB.utf8'

RUN echo 'alias python=python3' >> ~/.bashrc
RUN echo 'alias pip=pip3' >> ~/.bashrc

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal


ENV DockerHOME=/app/  

RUN mkdir -p $DockerHOME  

WORKDIR $DockerHOME   

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

RUN pip install --upgrade pip  

COPY . $DockerHOME

COPY supervise.conf /etc/supervisor/conf.d/
COPY nginx.conf /etc/nginx/nginx.conf
RUN mkdir /run/daphne/

RUN pip install -r requirements.txt

EXPOSE 80

RUN chmod +x ./start.sh

ENTRYPOINT ["./start.sh"]
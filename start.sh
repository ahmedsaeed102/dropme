#!/bin/bash
python3 manage.py makemigrations 
python3 manage.py migrate

service supervisor start
supervisorctl
supervisorctl reread
supervisorctl update
nginx
nginx -s reload
#nginx -g 'daemon off;'
tail -f ./asgi.out.log -f /var/log/nginx/access.log -f /var/log/nginx/error.log
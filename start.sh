#!/bin/bash

# check for any new migrations, then apply them to production database
python3 manage.py makemigrations 
python3 manage.py migrate

# Starting supervisor 
service supervisor start
supervisorctl

# reloading supervisor to read the new config file
supervisorctl reread
supervisorctl update

# Start nginx and reload it to apply the new config
nginx
nginx -s reload
#nginx -g 'daemon off;'

# print Logs to stdout
tail -f ./asgi.out.log -f /var/log/nginx/access.log -f /var/log/nginx/error.log
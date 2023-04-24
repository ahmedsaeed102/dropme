#!/bin/bash
cat > .env << EOL
EMAIL_HOST_USER=${EMAIL_HOST_USER}
EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
state=${state}
SITE_ID=${SITE_ID}
apikey=${apikey}
db_password=${db_password}
db_host=${db_host}
db_port=${db_port}
db_name=${db_name}
type=${type}
project_id=${project_id}
private_key_id=${private_key_id}
private_key="${private_key}"
SECRET_KEY=${SECRET_KEY}
client_email=${client_email}
client_id=${client_id}
auth_uri=${auth_uri}
token_uri=${token_uri}
auth_provider_x509_cert_url=${auth_provider_x509_cert_url}
client_x509_cert_url=${client_x509_cert_url}
AWS_S3_REGION_NAME=${AWS_S3_REGION_NAME}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_STORAGE_BUCKET_NAME=${AWS_STORAGE_BUCKET_NAME}
EOL

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
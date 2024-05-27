## Build
cp env.template .env

docker compose up -d --build

## Create admin
docker exec -it openagri-api-1 bash

python manage.py createsuperuser

## Postman workspace
https://app.getpostman.com/join-team?invite_code=87776469415c8489cf5414a593811a08&target_code=84de45e9cd7acf5b3ea1a47cd2eb9b98
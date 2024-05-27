## Build
cp env.template .env

docker compose up -d --build

## Create admin
docker exec -it openagri-api-1 bash

python manage.py createsuperuser
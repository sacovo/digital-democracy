# Digital Democracy

This is the backend for the project digital democracy.


## Setup
To run the backend run the following commands:

```
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

To update from git
```
git pull
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
```
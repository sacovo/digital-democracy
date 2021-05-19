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


## Deployment

For deployment you can use the Docker image from the gitlab registry. In order to use it, you need an access token. Contact the project team in order to get them. Once you have obtained an access token, you can use it to login to the registry:

```
docker login cr.gitlab.fhnw.ch
```

Then you can create a docker-compose.yml file to setup the database and everything, an example with traefik labels can be found in `docker-compose.example.yml`.  Don't forget to change the domains and entrypoints according to your needs.

After you configured the docker-compose file, you can start the containers
```
docker-compose up -d
```

Collect all the status files:

```
docker-compose exec web python manage.py collectstatic
```

Run the migrations:
```
docker-compose exec web python manage.py migrate
```

### Upgrading

Get the latest version

```
docker-compose pull
```

Replace the running version with the latest one

```
docker-compose up -d
```

Run migrations and collect static files:

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic
```

## PDF-Fonts

Fonts for PDFs need to be provided in the web container under `/usr/share/fonts`. You can accomplish that by mounting a local font folder into the container. Modify the `docker-compose.yml` like this:

```
services:
  web:
    volumes:
      - ./fonts/:/usr/share/fonts/
```

Fonts for the title and body of the generated pdf are controlled through environment variables `PDF_TITLE` and `PDF_BODY_FONT`, set them in your environment file or directly in the docker-compose.yml file.

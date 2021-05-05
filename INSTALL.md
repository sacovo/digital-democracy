## PDF-Fonts

Fonts for PDFs need to be provided in the web container under `/usr/share/fonts`. You can accomplish that by mounting a local font folder into the container. Modify the `docker-compose.yml` like this:

```
services:
  web:
    volumes:
      - ./fonts/:/usr/share/fonts/
```

Fonts for the title and body of the generated pdf are controlled through environment variables `PDF_TITLE` and `PDF_BODY_FONT`, set them in your environment file or directly in the docker-compose.yml file.

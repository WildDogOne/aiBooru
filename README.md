# aiBooru

aiBooru is a CLI tool for uploading images to Danbooru-style image boards.

## Requirements

- Python 3.7 or higher
- requests
- PyYAML

## Usage

The `aiBooru` tool can be used to upload images from a directory to a Danbooru-style image board. Each image must have a
corresponding YAML file that describes the image's tags and rating.

To use `aiBooru`, run the following command:

```bash
python aibooru.py -d "/path/to/directory"
```

Replace `/path/to/directory` with the path to the directory containing the images you want to upload.

By default, `aiBooru` will only upload images that haven't been uploaded before. If you want to force the upload of all
images, use the `-f` or `--force` flag:

```bash
python aibooru.py -d "/path/to/directory" -f
```

If you want to use DeepBooru to generate tags for the images, use the `-t` or `--tagging` flag:

```bash
python aibooru.py -d "/path/to/directory" -t
```

## YAML File Format

Each image must have a corresponding YAML file with the same name as the image file, but with a `.yaml` extension. The
YAML file should have the following format:

```markdown
rating: [rating]
tags:

- [tag1]
- [tag2]
- ...
```

Replace `[rating]` with the rating of the image (`s`, `q`, or `e`). Replace `[tag1]`, `[tag2]`, etc. with the tags that
describe the image.

If you don't provide a YAML file for an image, `aiBooru` will skip that image.

## License

See the `LICENSE` file for more information.

## Howto Install Danbooru

## Installation on Docker Compose

Download the two files:

- https://raw.githubusercontent.com/danbooru/danbooru/master/docker-compose.yaml
- https://raw.githubusercontent.com/danbooru/danbooru/master/.env
- https://raw.githubusercontent.com/danbooru/danbooru/master/config/danbooru_default_config.rb

For example on Linux:

```
wget https://raw.githubusercontent.com/danbooru/danbooru/master/docker-compose.yaml
wget https://raw.githubusercontent.com/danbooru/danbooru/master/.env
wget https://raw.githubusercontent.com/danbooru/danbooru/master/config/danbooru_default_config.rb
```

1. [Install Docker Compose](https://github.com/docker/compose)
2. Rename ``danbooru_default_config.rb`` to ``danbooru_local_config.rb``
3. Change ``danbooru_local_config.rb`` to what you want, the documentation inside the file is pretty good. In a later
   section we will discuss some useful changes.
4. Change the ``docker-compose.yaml`` to your liking. A later section will discuss some of them
5. Make some kind of folder structure. For example, one folder for danbooru, one for postgresql so you don't have to
   rely on docker volumes
6. Start Docker with ``docker compose up -d``
7. Get yourself some kind of reverse proxy for example nginx (Config for nginx in later section)

### Compose File

#### Danbooru Service

Changes made to get persistent data inside a folder instead of Docker volumes.
This is a personal preference though, so there is no actual need to follow this.
Important is that you map "danbooru_local_config.rb" so that your config will actually be taken into consideration.
Also change the listening IP to 127.0.0.1 instead of any, you don't necessarily want to publish the docker services
directly to internet. I would use nginx for that.

```yaml
volumes:
  - "./danbooru/config/danbooru_local_config.rb:/danbooru/config/danbooru_local_config.rb"
  - "./danbooru/public/data:/danbooru/public/data"

ports:
  - "127.0.0.1:3000:3000"
```

#### Postgresql Service

The only real change is that I removed the volume in favour of a folder structure.

```yaml
- "./postgresql/data:/var/lib/postgresql/data"
```

#### Example Compose File

<details>
  <summary>Click me</summary>

```yaml
version: "3.4"

name: danbooru

x-base-template: &base-template
  user: root
  # pull_policy: always # Uncomment this to always pull the latest image when deploying.
  image: ghcr.io/danbooru/danbooru:production # you can change this to danbooru:master to get the latest upstream changes
  environment:
    RAILS_ENV: production # Set this to development to force danbooru to freshly compile js/css assets (for example if you're doing local development)
    RAILS_SERVE_STATIC_FILES: true
    PUMA_WORKERS: 1
    DATABASE_URL: postgresql://danbooru@postgres/danbooru
    DANBOORU_REDIS_URL: redis://redis:6379
    DANBOORU_IQDB_URL: http://iqdb:5588
    # If you want to host danbooru under your own domain you need to replace the above line with the following (replace with your actual domain):
    DANBOORU_CANONICAL_URL: https://danbooru.im
    DANBOORU_HOSTNAME: danbooru.im
  volumes:
    #- "danbooru-images:/danbooru/public/data"
    # # If you want to do local development you can uncomment these lines to force the container to use your local changes
    # # Simply replace $HOME/danbooru to where you cloned the repo
    - "./danbooru/config/danbooru_local_config.rb:/danbooru/config/danbooru_local_config.rb"
    - "./danbooru/public/data:/danbooru/public/data"

services:
  danbooru:
    <<: *base-template
    ports:
      - "127.0.0.1:3000:3000"
    tmpfs:
      - /tmp
    depends_on:
      - postgres
    command: [ "bash", "-c", "bin/rails db:prepare && bin/rails db:seed && bin/rails server -b 0.0.0.0" ]

  cron:
    <<: *base-template
    depends_on:
      - danbooru
    command: [ "bash", "-c", "bin/wait-for-http http://danbooru:3000 5s && bin/rails danbooru:cron" ]

  jobs:
    <<: *base-template
    depends_on:
      - danbooru
    command: [ "bash", "-c", "bin/wait-for-http http://danbooru:3000 5s && bin/good_job start" ]

  # https://github.com/danbooru/iqdb
  # https://hub.docker.com/repository/docker/evazion/iqdb
  iqdb:
    image: evazion/iqdb
    volumes:
      - "iqdb-data:/iqdb/data"
    command: [ "http", "0.0.0.0", "5588", "/iqdb/data/iqdb.sqlite" ]

  redis:
    image: redis

  postgres:
    image: evazion/postgres
    environment:
      POSTGRES_USER: danbooru
      POSTGRES_HOST_AUTH_METHOD: trust
    volumes:
      - "./postgresql/data:/var/lib/postgresql/data"

volumes:
  iqdb-data:
    name: iqdb-data
```

</details>

### danbooru_local_config.rb

This configuration file is massive, but some points are important to it.
It is actually possible to set these values via the .env file, but I just dislike that.

Here a list of thins I think are important to change:

````ruby
    def secret_key_base
      "Add a UUID as a base key here. It will be used for encryption, never share this key."
    end

    # The name of this Danbooru.
    def app_name
      if CurrentUser.safe_mode?
        "safeAiBooru" # Change this to the name of your booru
      else
        "aiBooru" # Change this to the name of your booru
      end
    end

    def canonical_app_name
      "https://danbooru.im" # Your Base URL
    end

    def hostname
      "danbooru.im" # The hostname of your booru
    end

    def alternate_domains
      ["danbo.danbooru.im"] # List of Alternative domains often this will just be empty: []
    end

    def safe_mode_hostnames
      ["safe.danbooru.im"] # Hostname for safe version of your booru. This does not need to be added to alternate domains
    end

    def canonical_url
      "https://danbooru.im" # Once again URL of your booru, no idea why it's there twice
    end

    def contact_email
      "webmaster@danbooru.im" # The email address of the admin user. This email will be publicly displayed on the contact page.
    end

    def dmca_email
      "dmca@danbooru.im" # The email address where DMCA complaints should be sent.
    end

    def notification_email
      "notifications@danbooru.im" # The email address to use for Dmail notifications.
    end

    def account_security_email
      "security@danbooru.im" # The email address to use for password reset and email verification emails.
    end

    def welcome_user_email
      "welcome@danbooru.im" # The email address to use for new user signup emails.
    end

    def system_user
      "DanbooruBot" # Name of the System User
    end

    def email_key
      "CHANGEME" # This key should be changed, no idea why though
    end
````

### nginx config

This is really only an example that has proven to work.
Make sure to change hostnames and certificates.
Never run things without TLS (https)!

You can easily get certificates from letsencrypt via certbot.

```
server {
    if ($host = safe.danbooru.im) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    if ($host = danbooru.im) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name danbooru.im safe.danbooru.im;
    return 301 https://$host$request_uri;

}
server {

    listen 443 ssl;
    server_name danbooru.im safe.danbooru.im;
    ssl_certificate /etc/letsencrypt/live/danbooru.im/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/danbooru.im/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

    ssl_session_cache  builtin:1000  shared:SSL:10m;
    #ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;

    access_log            /var/log/nginx/xsoar.access.log;

    location / {

      proxy_set_header        Host $host;
      proxy_set_header        X-Real-IP $remote_addr;
      proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header        X-Forwarded-Proto $scheme;
      proxy_set_header        X-NginX-Proxy true;
      client_max_body_size 10000M;
      # Fix the "It appears that your reverse proxy set up is broken" error.
      proxy_pass          http://localhost:3000;
      proxy_read_timeout  90;
    }
}
```
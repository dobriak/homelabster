# Homelabster

## Puprpose
Homelabster is a simple web application aimed at helping enthusiasts easily organize a directory of links to services they host in their home labs. It is intended to only run internally, save its data to a sqlite database located in external to the app directory.

Each service is represented by a tile that has an icon and a link, together with an optional description.
There is a helpful search bar at the top of the dashboard that can easily filter all available tiles by name or description content.


## Pages
The application has two pages:
1.  Default page: a beautiful ergonomic dashboard where those links are displayed, that takes away the need to remember internal URLs and IPs.
2. Administration page: it has 2 main tabs which allow for:
  * CRUD operations for all existing tiles, as well as creating new ones.
  * General settings editing. Settings such as design theme, administrative password management and such.

The administration page is protected by simple username/password authentication. The admin username and password are read from a local .env file for simplicity.

## Technology
The application utilizes the following technologies:
* Nextjs 16+ with React 19+
* TailwindCSS 4+ with ShadCN
* Typescript 5+
* Bun runtime and package management
* Task-go for orchestration (https://taskfile.dev/docs/guide)

### Data storage
All user generated data is written to ./userdata:
* All images uploaded to be the icons for the tiles will be placed in ./userdata/images/
* The JSON file that contains all configuration is saved in ./userdata/config/settings.json

### Deployment choices
The application is configured with a Dockerfile for building an image and docker-compose.yml that will make it easy to run on a docker host.

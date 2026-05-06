![Web App CI](https://github.com/swe-students-spring2026/5-final-sneaky_golem/actions/workflows/web-app.yml/badge.svg)
![Machine Learning Client CI](https://github.com/swe-students-spring2026/5-final-sneaky_golem/actions/workflows/ml-client.yml/badge.svg)

# Tetruzzle
Tetruzzle is an community where users can share Tetris puzzles with one another! Either build your own board or upload a screenshot from TETR.IO, select the piece queue, and upload and share. Users can also submit their own solutions to these puzzles, allowing players to learn how others stack their way out of a difficult situation.

## Container Images
- [web app container](https://hub.docker.com/repository/docker/ah6820/golem-web-app)
- [ml client container](https://hub.docker.com/repository/docker/ah6820/golem-ml-client)

## Contributors
- Aaron Hui [Github](https://github.com/aaronthmetic/)
- Natt Hong [Github](https://github.com/nmh6063-star/)
- Andy Liu [Github](https://github.com/andy8259/)
- Simon Ni [Github](https://github.com/narezin/)
- Tim Xu [Github](https://github.com/timxu2006/)

## Configuration Instructions

### Requirements
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Setup

#### Clone the repository
```bash
git clone https://github.com/swe-students-spring2026/5-final-sneaky_golem.git
```

#### Configure environment variables

Copy the example environment file.

```bash
cp .env.example .env
```

Edit `.env` with your actual values.

#### Start all containers

Build and start the application.

```bash
docker compose up -d --build
```

If run locally, the web application will be available at [http://localhost:5000](http://localhost:5000).

It is also available on DigitalOcean [here](https://golem-ml-client-xo5il.ondigitalocean.app/).

#### Stop the system

```bash
docker compose down
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb://mongodb:27017` |
| `MONGO_DBNAME` | MongoDB database name | `golem-db` |
| `SECRET_KEY` | Secret Key for Auth | `watch_tv` |
| `ML_CLIENT_URL` | Base URL for the ML Client | `http://machine-learning-client:5001`

## Task boards
Our task board is available [here](https://github.com/orgs/swe-students-spring2026/projects/128).
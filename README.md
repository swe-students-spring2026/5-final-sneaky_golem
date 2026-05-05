![Web App CI](https://github.com/swe-students-spring2026/5-final-sneaky_golem/actions/workflows/web-app.yml/badge.svg)
![Machine Learning Client CI](https://github.com/swe-students-spring2026/5-final-sneaky_golem/actions/workflows/ml-client.yml/badge.svg)

# Tetruzzle
Project description here. Fix this later!

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

The web application will be available at [http://localhost:5000](http://localhost:5000).

It will also be available elsewhere once we deploy it with DigitalOcean. Note to fix this later!

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

## Task boards
Our task board is available [here](https://github.com/orgs/swe-students-spring2026/projects/128).
![Web App CI](https://github.com/swe-students-spring2026/5-final-sneaky_golem/actions/workflows/web-app.yml/badge.svg)
![Machine Learning Client CI](https://github.com/swe-students-spring2026/5-final-sneaky_golem/actions/workflows/ml-client.yml/badge.svg)

# Tetruzzle
Tetruzzle is a community where users can share Tetris puzzles with one another! Either build your own board or upload a screenshot from TETR.IO, select the piece queue, and upload and share. Users can also submit their own solutions to these puzzles, allowing players to learn how others stack their way out of a difficult situation.

## Container Images
- [web app container](https://hub.docker.com/repository/docker/ah6820/golem-web-app)
- [ml client container](https://hub.docker.com/repository/docker/ah6820/golem-ml-client)

## Contributors
- Aaron Hui [Github](https://github.com/aaronthmetic/)
- Natt Hong [Github](https://github.com/nmh6063-star/)
- Andy Liu [Github](https://github.com/andy8259/)
- Simon Ni [Github](https://github.com/narezin/)
- Tim Xu [Github](https://github.com/timxu2006/)

## Architecture
```
Tetruzzle is composed of three subsystems, each running as an independent containerized service:
┌─────────────────────────────────────────────────────────┐
│                        User Browser                     │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP
┌─────────────────────────────────────────────────────────┐
│                  Web App (Flask)                        │
│  - User authentication (Flask-Login)                    │
│  - Board editor and viewer                              │
│  - Community board sharing                              │
│  - Forwards images to ML Client                         │
└──────────┬──────────────────────────┬───────────────────┘
           │ HTTP (internal)          │ PyMongo
┌─────────────────────┐   ┌───────────────────────────────┐
│  ML Client (Flask)  │   │     MongoDB (Atlas)           │
│  - Receives base64  │   │  - users collection           │
│    image via POST   │   │  - puzzles collection         │
│  - OpenCV parsing   │   │  - solutions collection       │
│  - Returns 10×20    │   │  - likes collection           │
│    board matrix     │   │                               │
└─────────────────────┘   └───────────────────────────────┘
```

## System flow

### Board Import Flow
The board import flow is the core feature that distinguishes Tetruzzle from a simple board editor. It documents how a raw image travels across two separate services — the web app and the ML client — before becoming structured, editable data, illustrating the microservice boundary in action.
```
User uploads screenshot
        ↓
Web App encodes image as base64
        ↓
Web App POSTs to ML Client /extract-board
        ↓
ML Client decodes image → OpenCV detects grid → identifies piece colors
        ↓
ML Client returns board as a matrix
        ↓
Web App renders board preview for user to confirm or edit
        ↓
User confirms → board saved to MongoDB
```
### Authentication Flow
```
User registers / logs in
        ↓
Web App hashes password (Werkzeug) → stores in MongoDB users collection
        ↓
Flask-Login manages session via SECRET_KEY-signed cookie
        ↓
All protected routes require @login_required
```
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
| `ML_CLIENT_URL` | Base URL for the ML Client | `http://localhost:5001/`

Note: In our deployed web-app, `MONGO_URI` is set to point to our MongoDB Atlas cluster and `ML_CLIENT_URL` is set to point to the internal service hostname assigned by App Platform. 

## Task boards
Our task board is available [here](https://github.com/orgs/swe-students-spring2026/projects/128).

## Acknowledgements
Thank you to swng for allowing us to use his Tetris client, ZZTetris, so that we didn't have to reinvent the wheel and re-program the Tetris game logic. You can find the source code for ZZTetris [here](https://github.com/swng/zztetris).
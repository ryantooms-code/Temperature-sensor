# SenseHat Monitor

Reads temperature, humidity, and pressure from a Raspberry Pi SenseHat,
stores every reading in a local SQLite database, pushes updates to Blynk,
and exposes a small Flask REST API — all running inside Docker.

---

## File Structure

```
.
├── app.py            # Entry point: starts sensor thread + Flask server
├── flask_app.py      # Flask REST API (routes / /api/latest /api/readings)
├── sensor.py         # Sensor polling loop, LED control, thresholds
├── database.py       # SQLite3 layer (init, insert, query)
├── blynk_client.py   # Blynk HTTP API client
├── init_db.py        # One-shot DB initialisation helper
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container image definition
├── docker-compose.yml
└── .env              # Environment variable template
```

---

## Blynk Virtual Pins

| Pin | Sensor      |
|-----|-------------|
| V0  | Temperature |
| V1  | Humidity    |
| V2  | Pressure    |
| V4  | Status      |

## V3 was a switch. This was to act as a killswitch when pressing the button on sensehat, but was removed as acting up

---

## LED Behaviour

| Condition           | LED Colour |
|---------------------|------------|
| Temperature > 35 °C | 🔴 Red     |
| Temperature < 20 °C | 🔵 Blue    |
| 20 °C – 35 °C       | 🟢 Green   |

## Add -5°C correction, but the temp has still been high the last couple week, so running this value higher than normal. The higher end should could be brought down to 30°C and lower 17°C

---

## Quick Start

### 1. Configure environment

```bash
nano .env
```

### 2. Create the DB directory

```bash
mkdir -p /home/toomsey/assignement
```

### 3. Build and run with Docker Compose

```bash
docker compose up --build -d
```

### 4. Check logs

```bash
docker compose logs -f
```

### 5. Query the API

```bash
# Latest reading
curl http://localhost:5002/api/latest

# All readings (newest first, max 500)
curl http://localhost:5002/api/readings

# Health check
curl http://localhost:5002/health
```
## Running on port 5002, as when testing Flask became active on 5000 and 5001. Change the port number to speed up development. Ideally, I should have reset port after use.

---

## Running Locally (without Docker)

```bash
pip install -r requirements.txt
python init_db.py          # create DB schema once
python app.py              # start sensor loop + Flask
```

---

## Environment Variables

| Variable          | Default                                  | Description                              |
|-------------------|------------------------------------------|------------------------------------------|
| `BLYNK_AUTH_TOKEN`| `BLYNK_AUTH_TOKEN`                       | Blynk device auth token                  |
| `BLYNK_SERVER`    | `https://blynk.cloud`                    | Blynk server URL                         |
| `BLYNK_TIMEOUT`   | `5`                                      | HTTP request timeout (seconds)           |
| `DB_PATH`         | `/home/toomsey/assignement/sense_data.db`| SQLite database path                     |
| `POLL_INTERVAL`   | `30`                                     | Seconds between sensor reads             |
| `TEMP_HOT`        | `35`                                     | °C threshold for HOT status / red LED    |
| `TEMP_COLD`       | `20`                                     | °C threshold for COLD status / blue LED  |
| `TEMP_CORRECTION` | `-5`                                     | Offset applied to raw SenseHat temp      |

---

## API Endpoints

### `GET /`
Service info and endpoint list.

### `GET /health`
Returns `{"status": "ok"}`.

### `GET /api/latest`
Returns the most recent sensor reading as JSON.

### `GET /api/readings`
Returns up to 500 most recent readings, newest first.

---

## Notes

- The SenseHat's on-board temperature sensor is influenced by the Pi's CPU heat.  
  The `TEMP_CORRECTION` offset (default `-5`) compensates for this.  
- On non-Pi hardware (e.g. your laptop), the app automatically falls back to
  mock sensor values so you can test the API and Blynk integration without hardware.
- Tried to add Google Nest Thermostat API intregration, but was having issue with 
  Pub/Sub rights. See Nest folder for screenshoots.
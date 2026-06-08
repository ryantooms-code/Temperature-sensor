"""
sensor.py - SenseHat sensor polling loop
Reads temperature, humidity, pressure from SenseHat every POLL_INTERVAL seconds.
- Determines status string based on temperature thresholds
- Updates SenseHat LED matrix with colour indicator
- Stores reading in SQLite database
- Pushes reading to Blynk server
"""

import time
import logging
import os

from database import init_db, insert_reading
from blynk_client import push_to_blynk

logger = logging.getLogger(__name__)

# How often to read sensors (seconds)
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "30"))

# Temperature thresholds
TEMP_HOT  = float(os.environ.get("TEMP_HOT",  "35"))   # °C — LED goes red above this
TEMP_COLD = float(os.environ.get("TEMP_COLD", "20"))   # °C — LED goes blue below this

# ── Colours ──────────────────────────────────────────────────────────────────
RED    = (255, 0,   0)
BLUE   = (0,   0,   255)
GREEN  = (0,   200, 0)


def _get_sense():
    """
    Import and return a SenseHat instance.
    Wrapped so the rest of the module can be imported on non-Pi hardware
    (e.g. during unit tests) without crashing.
    """
    try:
        from sense_hat import SenseHat  # type: ignore
        return SenseHat()
    except Exception as exc:
        logger.warning("SenseHat not available: %s — using mock values.", exc)
        return None


def _read_sensors(sense):
    """
    Read temperature, humidity, and pressure.
    SenseHat's CPU can inflate the temperature reading; a small correction
    factor is applied. Adjust TEMP_CORRECTION in your environment if needed.
    """
    correction = float(os.environ.get("TEMP_CORRECTION", "-5"))

    if sense is None:
        # Mock values for development / Docker desktop testing
        import random
        return (
            round(25.0 + random.uniform(-8, 15), 2),
            round(55.0 + random.uniform(-10, 10), 2),
            round(1013.0 + random.uniform(-5, 5), 2),
        )

    raw_temp = sense.get_temperature()
    temperature = round(raw_temp + correction, 2)
    humidity    = round(sense.get_humidity(), 2)
    pressure    = round(sense.get_pressure(), 2)
    return temperature, humidity, pressure


def _determine_status(temperature: float) -> str:
    if temperature > TEMP_HOT:
        return "HOT"
    if temperature < TEMP_COLD:
        return "COLD"
    return "NORMAL"


def _set_led(sense, status: str):

    if sense is None:
        return

    colour_map = {
        "HOT":    RED,
        "COLD":   BLUE,
        "NORMAL": GREEN,
    }
    colour = colour_map.get(status, GREEN)
    sense.clear(*colour)
    logger.debug("LED set to %s for status %s", colour, status)


def start_sensor_loop():

    init_db()
    sense = _get_sense()

    logger.info(
        "Sensor loop started. Poll interval: %ds  Hot: >%.1f°C  Cold: <%.1f°C",
        POLL_INTERVAL, TEMP_HOT, TEMP_COLD
    )

    while True:
        try:
            temperature, humidity, pressure = _read_sensors(sense)
            status = _determine_status(temperature)

            logger.info(
                "Reading — Temp: %.2f°C  Hum: %.2f%%  Pres: %.2f hPa  Status: %s",
                temperature, humidity, pressure, status
            )

            # 1. Update SenseHat LED
            _set_led(sense, status)

            # 2. Persist to SQLite
            insert_reading(temperature, humidity, pressure, status)

            # 3. Push to Blynk (non-blocking; errors are caught inside)
            push_to_blynk(temperature, humidity, pressure, status)

        except Exception as exc:
            logger.error("Sensor loop error: %s", exc, exc_info=True)

        time.sleep(POLL_INTERVAL)

"""
Blynk client for pushing sensor data to the Blynk cloud service.

Virtual pin mapping:
  V0 — Temperature
  V1 — Humidity
  V2 — Pressure
  V4 — Status  (V3 was used for switch to act as kill switch, but is now unused)
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

# ── Configuration (set these in your .env or Docker environment) ─────────────
BLYNK_AUTH_TOKEN = os.environ.get("BLYNK_AUTH_TOKEN", "pSbVAjTPl9HX_ObS3Pe3WzlsBaN5TK1O").strip()
BLYNK_SERVER     = os.environ.get("BLYNK_SERVER", "https://blynk.cloud")

# Virtual pin assignments
PIN_TEMPERATURE = "V0"
PIN_HUMIDITY    = "V1"
PIN_PRESSURE    = "V2"
PIN_STATUS      = "V4"

# Seconds before a Blynk HTTP request times out
REQUEST_TIMEOUT = int(os.environ.get("BLYNK_TIMEOUT", "5"))


def _update_pin(pin: str, value) -> bool:

    url = f"{BLYNK_SERVER}/external/api/update?token={BLYNK_AUTH_TOKEN}&{pin}={value}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            logger.debug("Blynk %s ← %s  (200 OK)", pin, value)
            return True
        else:
            logger.warning(
                "Blynk %s update failed: HTTP %d — %s",
                pin, response.status_code, response.text.strip()
            )
            return False
    except requests.exceptions.Timeout:
        logger.warning("Blynk %s update timed out after %ds.", pin, REQUEST_TIMEOUT)
        return False
    except requests.exceptions.ConnectionError as exc:
        logger.warning("Blynk connection error for %s: %s", pin, exc)
        return False
    except Exception as exc:
        logger.error("Unexpected Blynk error for %s: %s", pin, exc, exc_info=True)
        return False


def push_to_blynk(temperature: float, humidity: float, pressure: float, status: str):
    token = BLYNK_AUTH_TOKEN.strip()
    if not token or len(token) < 10:
        logger.warning("BLYNK_AUTH_TOKEN appears missing or too short — skipping.")
        return

    results = {
        PIN_TEMPERATURE: _update_pin(PIN_TEMPERATURE, temperature),
        PIN_HUMIDITY:    _update_pin(PIN_HUMIDITY,    humidity),
        PIN_PRESSURE:    _update_pin(PIN_PRESSURE,    pressure),
        PIN_STATUS:      _update_pin(PIN_STATUS,      status),
    }

    successes = sum(results.values())
    logger.info(
        "Blynk update: %d/4 pins OK  (T=%.2f H=%.2f P=%.2f Status=%s)",
        successes, temperature, humidity, pressure, status
    )

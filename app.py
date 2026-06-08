import threading
import logging
from flask_app import create_app
from sensor import start_sensor_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting SenseHat Monitor...")

    # Start sensor polling in background thread
    sensor_thread = threading.Thread(target=start_sensor_loop, daemon=True)
    sensor_thread.start()
    logger.info("Sensor polling thread started.")

    # Start Flask API
    app = create_app()
    logger.info("Flask API starting on port 5000...")
    app.run(host="0.0.0.0", port=5002, debug=False, use_reloader=False)

import argparse
import json
import logging
import os
import random
import threading
import time
from datetime import datetime

from data_collection import get_config, validate_config, check_thresholds, send_email_alert

LOG_FILE = 'data_log.txt'
DATA_COLLECTION_INTERVAL = 1  # seconds
CONFIG_FILE = 'config.ini'

exit_event = threading.Event()
file_lock = threading.RLock()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_data():
    """Simulate sensor data collection."""
    return {
        'timestamp': datetime.now().isoformat(),
        'debit': random.uniform(0.1, 10.0),
        'pression': random.uniform(1.0, 5.0),
        'niveau_eau': random.uniform(0.0, 100.0),
    }


def store_data(data):
    """Append a JSON line with the collected data to the log file."""
    with file_lock, open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data) + '\n')


def run():
    config = get_config(CONFIG_FILE)
    validate_config(config)

    sender = config.get('email', 'sender')
    recipient = config.get('email', 'recipient')
    password = os.getenv('EMAIL_PASSWORD', '')

    try:
        while not exit_event.is_set():
            data = collect_data()
            store_data(data)
            logger.info("Collected data: %s", data)

            alerts = check_thresholds(data, config)
            for subject, body in alerts:
                try:
                    send_email_alert(sender, password, recipient, subject, body)
                except Exception:
                    logger.exception("Failed to send alert")

            time.sleep(DATA_COLLECTION_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    finally:
        exit_event.set()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Leak detection application")
    parser.add_argument('--interval', type=float, default=DATA_COLLECTION_INTERVAL,
                        help='Data collection interval in seconds')
    args = parser.parse_args()

    DATA_COLLECTION_INTERVAL = args.interval
    run()

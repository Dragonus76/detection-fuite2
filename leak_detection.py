import time
import random
import logging
import threading
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# Configuration
DATA_COLLECTION_INTERVAL = 1  # seconds
LOG_FILE = 'data_log.txt'

# Lock for file writing
file_lock = threading.RLock()

def collect_data():
    """
    Simulates data collection from sensors.
    """
    try:
        debit = random.uniform(0.1, 10.0)
        pression = random.uniform(1.0, 5.0)
        niveau_eau = random.uniform(0.0, 100.0)
    except Exception as e:
        logging.error(f"Error in data collection: {e}")
        return None

    return {
        'timestamp': datetime.now().isoformat(),
        'debit': debit,
        'pression': pression,
        'niveau_eau': niveau_eau,
    }

def store_data(data):
    """
    Store the collected data.
    For this example, data is simply written to a list.
    """
    try:
        return data
    except Exception as e:
        logging.error(f"Error in storing data: {e}")

# Variable used to stop the data collection loop.
exit_event = threading.Event()

def main():
    logging.info("Starting data collection...")
    data_collection = []
    try:
        while not exit_event.is_set():
            data = collect_data()
            if data is not None:
                logging.info("Collected data: {}".format(data))
                # Store the data
                data_collection.append(store_data(data))
            # Wait between data collections
            time.sleep(DATA_COLLECTION_INTERVAL)
            if exit_event.is_set():
                break
    except KeyboardInterrupt:
        logging.info("Data collection stopped by user")
    except Exception:
        logging.exception("An unexpected error occurred.")
    finally:
        logging.info("Stopping data collection.")
        exit_event.set()

        # Finish log file
        with open(LOG_FILE, 'w', encoding='utf-8') as file:
            json.dump(data_collection, file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    # Stop the data collection loop by pressing 'Enter'
    input_thread = threading.Thread(target=input, args=("Press 'Enter' to stop data collection...\n",))
    input_thread.daemon = True
    input_thread.start()

    # Run the main function
    main()

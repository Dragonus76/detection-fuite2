import time
import random
import logging
import threading
import json
import matplotlib.pyplot as plt
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# Configuration
DATA_COLLECTION_INTERVAL = 1  # seconds
LOG_FILE = 'data_log.txt'

# Lock for file writing
file_lock = threading.RLock()

exit_event = threading.Event()

def collect_data():
    while not exit_event.is_set():
        try:
            debit = random.uniform(0.1, 10.0)
            pression = random.uniform(1.0, 5.0)
            niveau_eau = random.uniform(0.0, 100.0)

            return {
                'timestamp': datetime.now().isoformat(),
                'debit': debit,
                'pression': pression,
                'niveau_eau': niveau_eau,
            }

        except Exception as e:
            logging.error(f"Error in data collection: {e}")

def store_data():
    while not exit_event.is_set():
        data = collect_data()
        if data is not None:
            try:
                with file_lock:
                    with open(LOG_FILE, 'a', encoding='utf-8') as file:
                        file.write(json.dumps(data) + "\n")
            except Exception as e:
                logging.error(f"Error in storing data: {e}")

def visualize():
    plt.ion()
    while not exit_event.is_set():
        try:
            with file_lock:
                with open(LOG_FILE, 'r', encoding='utf-8') as file:
                    data = [json.loads(line) for line in file]
            timestamps = [item['timestamp'] for item in data]
            debit = [item['debit'] for item in data]
            pression = [item['pression'] for item in data]
            niveau_eau = [item['niveau_eau'] for item in data]
            plt.cla()
            plt.plot(timestamps, debit, label="debit")
            plt.plot(timestamps, pression, label="pression")
            plt.plot(timestamps, niveau_eau, label="niveau_eau")
            plt.legend()
            plt.pause(0.1)
        except Exception as e:
            logging.error(f"Error in visualization: {e}")

if __name__ == '__main__':
    # Stop the data collection loop by pressing 'Enter'
    input_thread = threading.Thread(target=input, args=("Press 'Enter' to stop data collection...\n",))
    input_thread.daemon = True
    input_thread.start()

    # Run the visualization in another thread
    visualize_thread = threading.Thread(target=visualize)
    visualize_thread.daemon = True
    visualize_thread.start()

    # Run the data collection and storing in another thread
    data_thread = threading.Thread(target=store_data)
    data_thread.daemon = True
    data_thread.start()

    try:
        while True: 
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Data collection stopped by user")
        exit_event.set()

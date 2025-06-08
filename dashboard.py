from flask import Flask, render_template
import json
import os

from data_collection import get_config

LOG_FILE = 'data_log.txt'
CONFIG_FILE = 'config.ini'

app = Flask(__name__)


def load_data():
    """Return data from LOG_FILE as a list of dicts."""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


@app.route('/')
def index():
    config = get_config(CONFIG_FILE)
    city = config.get('location', 'city', fallback='Casablanca')
    data = load_data()
    return render_template('dashboard.html', city=city, data=data[-100:])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

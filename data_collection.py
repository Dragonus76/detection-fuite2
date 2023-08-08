import time
import logging
import configparser
import smtplib
from email.mime.text import MIMEText
import os
from getpass import getpass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.ini'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SLEEP_INTERVAL = 5
MAX_ATTEMPTS = 3

def get_config(file_path):
    config = configparser.ConfigParser()
    if not os.path.exists(file_path):
        logger.error(f"Config file {file_path} does not exist.")
        raise FileNotFoundError(f"Config file {file_path} does not exist.")

    try:
        config.read(file_path)
    except configparser.Error as e:
        logger.error(f"Error reading config file: {e}")
        raise e

    return config

def validate_config(config):
    assert 'email' in config, "Section 'email' is missing in the config file."
    assert 'sender' in config['email'], "Option 'sender' is missing in the 'email' section."
    assert 'recipient' in config['email'], "Option 'recipient' is missing in the 'email' section."

    assert 'thresholds' in config, "Section 'thresholds' is missing in the config file."
    assert 'seuil_debit' in config['thresholds'], "Option 'seuil_debit' is missing in the 'thresholds' section."
    assert 'seuil_pression' in config['thresholds'], "Option 'seuil_pression' is missing in the 'thresholds' section."
    assert 'seuil_niveau_eau' in config['thresholds'], "Option 'seuil_niveau_eau' is missing in the 'thresholds' section."

def send_email_alert(sender, password, recipient, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    for attempt in range(MAX_ATTEMPTS):
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
            server.quit()
            logger.info("Email sent successfully.")
            break
        except smtplib.SMTPException as e:
            if attempt < MAX_ATTEMPTS - 1:  # if it's not the last attempt
                logger.warning(f"Error sending email (attempt {attempt + 1}): {e}. Retrying in {SLEEP_INTERVAL} seconds...")
                time.sleep(SLEEP_INTERVAL)
            else:  # if it's the last attempt
                logger.error(f"Error sending email after {MAX_ATTEMPTS} attempts: {e}")
                raise e

def get_data():
    return {'debit': 4.5, 'pression': 2.6, 'niveau_eau': 86.0}

def check_thresholds(data, config):
    alerts = []

    for key, value in data.items():
        threshold = float(config.get('thresholds', f'seuil_{key}'))

        if value > threshold:
            logger.warning("Fuite détectée! %s anormal: %s", key, value)
            alerts.append(('Alerte de fuite', f'Fuite détectée! {key.capitalize()} anormal: {value}'))

    return alerts

def main():
    config = get_config(CONFIG_FILE)
    validate_config(config)

    sender = config.get('email', 'sender')
    password = os.getenv("EMAIL_PASSWORD")
    if not password:
        password = getpass("Enter your email password: ")
    recipient = config.get('email', 'recipient')

    try:
        while True:
            data = get_data()
            logger.info(f"Collected data: {data}")
            alerts = check_thresholds(data, config)
            for subject, body in alerts:
                send_email_alert(sender, password, recipient, subject, body)
            time.sleep(SLEEP_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Programme terminé.")
    except Exception as e:
        logger.error("An unexpected error occurred: ", exc_info=True)

if __name__ == "__main__":
    main()

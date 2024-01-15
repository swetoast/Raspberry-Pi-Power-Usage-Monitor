# Raspberry Pi Power Usage Monitor

This project is a Flask-based web application designed to monitor and calculate the real-time power usage of various Raspberry Pi models.

## Features

- Identifies the model of the Raspberry Pi it's running on.
- Calculates power usage based on CPU usage.
- Provides power usage information via a web interface.

## Installation

This application requires Flask, psutil, platform, subprocess, and configparser Python libraries. You can install them using pip:

```bash
pip install flask psutil platform subprocess configparser
```
## Usage

Run the script with Python:

```bash
python3 power_usage.py
```

Access the power usage information by navigating to the /power_usage route on your web browser.

## Configuration

Server configuration can be customized through the power_usage.conf file. The configuration includes settings for HTTPS, the certificate and key paths for SSL, and the host and port for the server.
Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

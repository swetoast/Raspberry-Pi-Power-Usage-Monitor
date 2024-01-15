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

Here is an example of what the power_usage.conf file might look like:

```
[DEFAULT]
https_enabled = True
cert_path = /path/to/cert.pem
key_path = /path/to/key.pem
host = 127.0.0.1
port = 5000
```

## Homeassistant Example

```
sensor:
  - platform: rest
    name: Power Usage
    resource: https://192.168.0.3/power_usage
    value_template: '{{ value_json.power_usage }}'
    unit_of_measurement: 'W'
    scan_interval: 60
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

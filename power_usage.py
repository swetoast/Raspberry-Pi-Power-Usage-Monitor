from flask import Flask, jsonify, redirect, url_for, request
import psutil
import platform
import subprocess
import configparser

app = Flask(__name__)

power_values = {
    "Raspberry Pi 3 Model B Plus": {"idle_power": 1.15, "max_power": 3.6},
    "Raspberry Pi 4 Model B": {"idle_power": 3.0, "max_power": 6.0},
    "Raspberry Pi 2 Model B": {"idle_power": 1.15, "max_power": 3.0},
    "Raspberry Pi Zero": {"idle_power": 0.1, "max_power": 1.2},
    "Raspberry Pi Zero W": {"idle_power": 0.3, "max_power": 1.3},
    "Raspberry Pi 3 Model A Plus": {"idle_power": 1.2, "max_power": 3.8},
    "Raspberry Pi 5 Model B": {"idle_power": 2.7, "max_power": 6.4},
    "Raspberry Pi 1 Model B": {"idle_power": 0.7, "max_power": 2.5},
    "Raspberry Pi 1 Model A": {"idle_power": 0.5, "max_power": 2.0},
    "Raspberry Pi 1 Model B+": {"idle_power": 0.7, "max_power": 2.5},
    "Raspberry Pi 1 Model A+": {"idle_power": 0.5, "max_power": 2.0},
}

def get_model():
    model_info = subprocess.check_output(["cat", "/proc/device-tree/model"])
    model_info = model_info.decode("utf-8")
    model_info = model_info.split('Rev')[0].strip()
    return model_info

model = get_model()

if model not in power_values:
    raise ValueError(f"Power values for {model} are not defined.")

idle_power = power_values[model]["idle_power"]
max_power = power_values[model]["max_power"]

def calculate_power_usage(usage_percentage):
    if usage_percentage < 0 or usage_percentage > 100:
        raise ValueError("Usage percentage should be between 0 and 100.")
    power_usage = idle_power + (max_power - idle_power) * (usage_percentage / 100)
    return power_usage

def get_current_usage_percentage():
    cpu_percentages = psutil.cpu_percent(percpu=True)
    usage_percentage = sum(cpu_percentages) / len(cpu_percentages)
    return usage_percentage

@app.route('/power_usage', methods=['GET'])
def power_usage():
    usage_percentage = get_current_usage_percentage()
    power_usage = calculate_power_usage(usage_percentage)

    throttled_state = subprocess.check_output(["vcgencmd", "get_throttled"])
    throttled_state = throttled_state.decode("utf-8").strip()
    throttled_hex = throttled_state.split('=')[1]

    return jsonify({"power_usage": power_usage, "throttled_state": throttled_hex})

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('power_usage')), 302

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('power_usage.conf')
    https_enabled = config.getboolean('DEFAULT', 'https_enabled')
    cert_path = config.get('DEFAULT', 'cert_path')
    key_path = config.get('DEFAULT', 'key_path')
    host = config.get('DEFAULT', 'host')
    port = config.getint('DEFAULT', 'port')
    if https_enabled:
        context = (cert_path, key_path)
    else:
        context = None
    app.run(host=host, port=port, debug=False, ssl_context=context)

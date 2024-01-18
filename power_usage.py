from flask import Flask, jsonify, redirect, url_for, request
import psutil
import platform
import subprocess
import configparser
import logging
import os

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
    try:
        model_info = subprocess.run(["cat", "/proc/device-tree/model"], check=True, capture_output=True, text=True)
        model_info = model_info.stdout
        model_info = model_info.split('Rev')[0].strip()
        return model_info
    except Exception as e:
        logging.error(f"Error getting model: {e}")
        return None

def get_cpu_frequency():
    cpu_freq = psutil.cpu_freq()
    return cpu_freq.current

model = get_model()

if model not in power_values:
    raise ValueError(f"Power values for {model} are not defined.")

idle_power = power_values[model]["idle_power"]
max_power = power_values[model]["max_power"]

def calculate_power_usage(usage_percentage, cpu_frequency):
    if usage_percentage < 0 or usage_percentage > 100:
        raise ValueError("Usage percentage should be between 0 and 100.")
    power_usage = idle_power + (max_power - idle_power) * (usage_percentage / 100) * (cpu_frequency / 1000)
    return power_usage

def get_current_usage_percentage():
    cpu_percentages = psutil.cpu_percent(percpu=True)
    usage_percentage = sum(cpu_percentages) / len(cpu_percentages)
    return usage_percentage

def get_voltage(component):
    try:
        voltage_info = subprocess.run(["vcgencmd", "measure_volts", component], check=True, capture_output=True, text=True)
        voltage_info = voltage_info.stdout.strip()
        voltage = voltage_info.split('=')[1].replace('V', '')
        return float(voltage)
    except Exception as e:
        logging.error(f"Error getting voltage: {e}")
        return None

@app.route('/power_usage', methods=['GET'])
def power_usage():
    usage_percentage = get_current_usage_percentage()
    cpu_frequency = get_cpu_frequency()
    power_usage = calculate_power_usage(usage_percentage, cpu_frequency)
    throttled_state = subprocess.check_output(["vcgencmd", "get_throttled"])
    throttled_state = throttled_state.decode("utf-8").strip()
    throttled_hex = throttled_state.split('=')[1]
    core_voltage = get_voltage("core")
    sdram_c_voltage = get_voltage("sdram_c")
    sdram_i_voltage = get_voltage("sdram_i")
    sdram_p_voltage = get_voltage("sdram_p")

    return jsonify({
        "power_usage": power_usage,
        "throttled_state": throttled_hex,
        "core_voltage": core_voltage,
        "sdram_c_voltage": sdram_c_voltage,
        "sdram_i_voltage": sdram_i_voltage,
        "sdram_p_voltage": sdram_p_voltage,
        "cpu_frequency_mhz": cpu_frequency
    })

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('power_usage')), 302

if __name__ == '__main__':
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'power_usage.conf')
    config.read(config_path)
    https_enabled = config.getboolean('DEFAULT', 'https_enabled', fallback=False)
    cert_path = config.get('DEFAULT', 'cert_path', fallback=None)
    key_path = config.get('DEFAULT', 'key_path', fallback=None)
    host = config.get('DEFAULT', 'host', fallback='127.0.0.1')
    port = config.getint('DEFAULT', 'port', fallback=5000)
    if https_enabled:
        context = (cert_path, key_path)
    else:
        context = None
    app.run(host=host, port=port, debug=False, ssl_context=context)

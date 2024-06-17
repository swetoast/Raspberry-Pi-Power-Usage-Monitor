from flask import Flask, jsonify, redirect, url_for, request
import psutil
import platform
import subprocess
import configparser
import logging
import os

class RaspberryPi:
    power_values = {
        "Raspberry Pi 3 Model B Plus": {"idle_power": 1.15, "max_power": 3.6},
        "Raspberry Pi 4 Model B": {"idle_power": 3.0, "max_power": 6.0},
        "Raspberry Pi 2 Model B": {"idle_power": 1.15, "max_power": 3.0},
        "Raspberry Pi Zero": {"idle_power": 0.1, "max_power": 1.2},
        "Raspberry Pi Zero W": {"idle_power": 0.3, "max_power": 1.3},
        "Raspberry Pi 3 Model A Plus": {"idle_power": 1.2, "max_power": 3.8},
        "Raspberry Pi 5 Model B": {"idle_power": 2.7, "max_power": 7.5},
        "Raspberry Pi 1 Model B": {"idle_power": 0.7, "max_power": 2.5},
        "Raspberry Pi 1 Model A": {"idle_power": 0.5, "max_power": 2.0},
        "Raspberry Pi 1 Model B+": {"idle_power": 0.7, "max_power": 2.5},
        "Raspberry Pi 1 Model A+": {"idle_power": 0.5, "max_power": 2.0},
    }

    def __init__(self):
        self.model = self.get_model()
        if self.model not in self.power_values:
            raise ValueError(f"Power values for {self.model} are not defined.")
        self.idle_power = self.power_values[self.model]["idle_power"]
        self.max_power = self.power_values[self.model]["max_power"]

    @staticmethod
    def get_model():
        try:
            model_info = subprocess.run(["cat", "/proc/device-tree/model"], check=True, capture_output=True, text=True)
            model_info = model_info.stdout
            model_info = model_info.split('Rev')[0].strip()
            return model_info
        except Exception as e:
            logging.error(f"Error getting model: {e}")
            return None

    @staticmethod
    def get_cpu_frequency():
        cpu_freq = psutil.cpu_freq()
        return cpu_freq.current

    @staticmethod
    def get_min_frequency():
        cpu_freq = psutil.cpu_freq()
        return cpu_freq.min

    @staticmethod
    def get_max_frequency():
        cpu_freq = psutil.cpu_freq()
        return cpu_freq.max

    @staticmethod
    def get_cpu_temperature():
        temperature_info = os.popen('vcgencmd measure_temp').readline()
        temperature = float(temperature_info.replace("temp=","").replace("'C\n",""))
        return temperature

    @staticmethod
    def calculate_power_usage(usage_percentage, cpu_frequency, min_frequency, max_frequency, idle_power, max_power):
        if usage_percentage < 0 or usage_percentage > 100:
            raise ValueError("Usage percentage should be between 0 and 100.")
        relative_frequency = (cpu_frequency - min_frequency) / (max_frequency - min_frequency)
        power_usage = idle_power + (max_power - idle_power) * (usage_percentage / 100) * relative_frequency
        return power_usage

    @staticmethod
    def get_current_usage_percentage():
        cpu_percentages = psutil.cpu_percent(percpu=True)
        usage_percentage = sum(cpu_percentages) / len(cpu_percentages)
        return usage_percentage

    @staticmethod
    def get_voltage(component):
        try:
            voltage_info = subprocess.run(["vcgencmd", "measure_volts", component], check=True, capture_output=True, text=True)
            voltage_info = voltage_info.stdout.strip()
            voltage = voltage_info.split('=')[1].replace('V', '')
            return float(voltage)
        except Exception as e:
            logging.error(f"Error getting voltage: {e}")
            return None

class PowerUsageApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.pi = RaspberryPi()
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/power_usage', methods=['GET'])
        def power_usage():
            usage_percentage = self.pi.get_current_usage_percentage()
            cpu_frequency = self.pi.get_cpu_frequency()
            min_frequency = self.pi.get_min_frequency()
            max_frequency = self.pi.get_max_frequency()
            power_usage = self.pi.calculate_power_usage(usage_percentage, cpu_frequency, min_frequency, max_frequency, self.pi.idle_power, self.pi.max_power)
            throttled_state = subprocess.check_output(["vcgencmd", "get_throttled"])
            throttled_state = throttled_state.decode("utf-8").strip()
            throttled_hex = throttled_state.split('=')[1]
            core_voltage = self.pi.get_voltage("core")
            sdram_c_voltage = self.pi.get_voltage("sdram_c")
            sdram_i_voltage = self.pi.get_voltage("sdram_i")
            sdram_p_voltage = self.pi.get_voltage("sdram_p")
            cpu_temperature = self.pi.get_cpu_temperature()

            return jsonify({
                "power_usage": power_usage,
                "throttled_state": throttled_hex,
                "core_voltage": core_voltage,
                "sdram_c_voltage": sdram_c_voltage,
                "sdram_i_voltage": sdram_i_voltage,
                "sdram_p_voltage": sdram_p_voltage,
                "cpu_frequency_mhz": cpu_frequency,
                "cpu_temperature": cpu_temperature
            })

        @self.app.errorhandler(404)
        def page_not_found(e):
            return redirect(url_for('power_usage')), 302

    def run(self):
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
        self.app.run(host=host, port=port, debug=False, ssl_context=context)

if __name__ == '__main__':
    app = PowerUsageApp()
    app.run()

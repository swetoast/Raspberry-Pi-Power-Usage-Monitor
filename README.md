# Raspberry Pi Power Usage Monitor

This script is a Flask application that monitors the power usage of a Raspberry Pi. It calculates the power usage based on the CPU usage percentage and the idle and max power values of the specific Raspberry Pi model.

## Features

- **Power Usage Calculation**: The script calculates the power usage based on the CPU usage percentage and the idle and max power values of the specific Raspberry Pi model.
- **Voltage Measurement**: The script measures the voltage of various components of the Raspberry Pi.
- **Throttled State**: The script retrieves the throttled state of the Raspberry Pi.

## API Endpoints

- `/power_usage`: This endpoint returns the current power usage, throttled state, and voltages of various components of the Raspberry Pi.

## Error Handling

- The script redirects all 404 errors to the `/power_usage` endpoint.

## Running the Application

The application can be run with HTTPS enabled or disabled. The settings for running the application are read from a configuration file named `power_usage.conf`.

## Configuration

The `power_usage.conf` file should contain the following settings:

- `https_enabled`: A boolean value indicating whether HTTPS is enabled.
- `cert_path`: The path to the SSL certificate file.
- `key_path`: The path to the SSL key file.
- `host`: The host on which the application should run.
- `port`: The port on which the application should listen.

Server configuration can be customized through the power_usage.conf file. The configuration includes settings for HTTPS, the certificate and key paths for SSL, and the host and port for the server.

Here is an example of what the power_usage.conf file might look like:

```
[DEFAULT]
https_enabled = False
cert_path = /path/to/cert.pem
key_path = /path/to/key.pem
host = 127.0.0.1
port = 5000
```

## Note

Please make sure to update the `power_values` dictionary in the script with the correct idle and max power values for your specific Raspberry Pi model.

## Homeassistant Example

```
sensor:
  - platform: rest
    resource: http://IP_ADDRESS/power_usage
    name: Raspberry Pi Power Usage
    json_attributes:
      - power_usage
      - throttled_state
      - core_voltage
      - sdram_c_voltage
      - sdram_i_voltage
      - sdram_p_voltage
    value_template: '{{ value_json["power_usage"] }}'
    unit_of_measurement: 'W'
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

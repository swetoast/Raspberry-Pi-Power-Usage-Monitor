# Raspberry Pi Power Usage Monitor

This Flask application monitors the power usage of a Raspberry Pi. It calculates the power usage based on the CPU usage percentage and the idle and max power values of the specific Raspberry Pi model.

## Features

- **Power Usage Calculation**: The application calculates the power usage based on the CPU usage percentage and the idle and max power values of the specific Raspberry Pi model.
- **Voltage Measurement**: The application measures the voltage of various components of the Raspberry Pi.
- **Throttled State**: The application retrieves the throttled state of the Raspberry Pi.

## API Endpoints

- `/power_usage`: This endpoint returns the current power usage, throttled state, and voltages of various components of the Raspberry Pi.

## Error Handling

- The application redirects all 404 errors to the `/power_usage` endpoint.

## Running the Application

The application can be run with HTTPS enabled or disabled. The settings for running the application are read from a configuration file named `power_usage.conf`.

## Configuration

The `power_usage.conf` file should contain the following settings:

- `https_enabled`: A boolean value indicating whether HTTPS is enabled.
- `cert_path`: The path to the SSL certificate file.
- `key_path`: The path to the SSL key file.
- `host`: The host on which the application should run.
- `port`: The port on which the application should listen.

Here is an example of what the `power_usage.conf` file might look like:

```conf
[DEFAULT]
https_enabled = False
cert_path = /path/to/cert.crt
key_path = /path/to/key.key
host = 127.0.0.1
port = 5000
```

## Homeassistant Integration

You can integrate this application with Home Assistant using the following configuration:

```yaml
sensor:
- platform: integration
    source: sensor.example_device_endpoint
    name: 'Example Energy Usage'
    unit_prefix: k
    unit_time: h

  - platform: rest
    name: "Example Device: Endpoint"
    resource: "http://IP_ADDRESS:PORT/power_usage"
    value_template: "{{ value_json.power_usage }}"
    json_attributes:
      - power_usage
      - throttled_state
      - core_voltage
      - sdram_c_voltage
      - sdram_i_voltage
      - sdram_p_voltage
      - cpu_frequency_mhz
    unit_of_measurement: 'W'
    device_class: energy
    state_class: measurement
```

## Contributing

Contributions are welcome. For major changes, please open an issue first to discuss what you would like to change.

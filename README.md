# Network UPS Tool (NUT) - Full — Custom Home Assistant Integration

Exposes **every variable** your UPS reports via NUT as a Home Assistant sensor — not just the fixed subset the built-in integration hardcodes.

## Why this exists

The built-in HA NUT integration maps a fixed list of known variables. Anything `upsc <ups>` returns that isn't in that list is silently dropped. For APC (and other UPS brands), this can mean 20–40 variables are missing.

This integration calls `GetUPSVars()` dynamically and creates one sensor per variable, regardless of whether it's in any hardcoded list.

## Installation

1. Copy the `nut_full/` folder into your HA config directory:
   ```
   /config/custom_components/nut_full/
   ```

2. Restart Home Assistant.

3. Go to **Settings → Devices & Services → Add Integration** and search for **Network UPS Tool (NUT) - Full**.

4. Enter your NUT server host, port (default 3493), and credentials.

## What you get

- One `sensor.` entity per NUT variable (e.g. `sensor.ups_input_voltage`, `sensor.ups_battery_runtime`)
- Proper device classes, units, and icons for ~50 known variables (see `const.py`)
- Unknown variables fall back to a generic text sensor with `mdi:information-outline`
- Device-info variables (`ups.serial`, `ups.firmware`, `driver.*`, etc.) are marked as `diagnostic`
- Numeric measurement sensors get `state_class: measurement` for long-term statistics
- Each sensor has a `nut_variable` attribute showing the raw NUT variable name

## Sensor naming

NUT variable `input.voltage.nominal` → entity `sensor.input Voltage Nominal` with unique ID scoped to `host:port:ups_name:variable`.

## Known variables with metadata

See `const.py → VARIABLE_META` for the full list. Covers:
- `battery.*` — charge, voltage, runtime, temperature, current
- `input.*` — voltage, current, frequency, power (real and apparent)
- `output.*` — voltage, current, frequency, power
- `ups.*` — load, power, temperature, efficiency, status, delays

## Compatibility

Tested against PyNUTClient 2.1.0. Works with any NUT server (local or remote) that accepts unauthenticated connections or username/password auth.

## APC BX1200MI example variables

Running `upsc apc@localhost` on a BX1200MI typically exposes:

```
battery.charge           battery.charge.low
battery.charge.warning   battery.mfr.date
battery.runtime          battery.runtime.low
battery.type             battery.voltage
battery.voltage.nominal  device.mfr
device.model             device.serial
device.type              driver.debug
driver.flag.allow_killpower  driver.name
driver.parameter.pollfreq    driver.parameter.port
driver.parameter.synchronous driver.state
driver.version           driver.version.data
driver.version.internal  input.frequency
input.sensitivity        input.transfer.high
input.transfer.low       input.voltage
input.voltage.nominal    output.current
output.frequency         output.voltage
output.voltage.nominal   ups.beeper.status
ups.delay.shutdown       ups.delay.start
ups.firmware             ups.firmware.aux
ups.id                   ups.load
ups.mfr                  ups.mfr.date
ups.model                ups.productid
ups.realpower.nominal    ups.serial
ups.status               ups.test.interval
ups.test.result          ups.timer.reboot
ups.timer.shutdown       ups.timer.start
ups.vendorid             ups.watchdog.status
```

All of these will be created as sensors automatically.

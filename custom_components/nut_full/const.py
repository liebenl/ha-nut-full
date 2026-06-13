"""Constants for NUT Full integration."""

DOMAIN = "nut_full"
DEFAULT_PORT = 3493
DEFAULT_SCAN_INTERVAL = 30  # seconds

# Maps NUT variable name prefixes/patterns to HA device classes and units.
# Used for richer sensor metadata. Falls back to generic sensor for unknowns.
VARIABLE_META: dict[str, dict] = {
    # Battery
    "battery.charge":           {"unit": "%",   "device_class": "battery",     "icon": "mdi:battery"},
    "battery.charge.low":       {"unit": "%",   "device_class": "battery",     "icon": "mdi:battery-low"},
    "battery.charge.warning":   {"unit": "%",   "device_class": "battery",     "icon": "mdi:battery-alert"},
    "battery.current":          {"unit": "A",   "device_class": "current",     "icon": "mdi:current-dc"},
    "battery.current.total":    {"unit": "A",   "device_class": "current",     "icon": "mdi:current-dc"},
    "battery.runtime":          {"unit": "s",   "device_class": "duration",    "icon": "mdi:timer-outline"},
    "battery.runtime.low":      {"unit": "s",   "device_class": "duration",    "icon": "mdi:timer-alert-outline"},
    "battery.temperature":      {"unit": "°C",  "device_class": "temperature", "icon": "mdi:thermometer"},
    "battery.voltage":          {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    "battery.voltage.high":     {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    "battery.voltage.low":      {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    "battery.voltage.nominal":  {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    # Input
    "input.current":            {"unit": "A",   "device_class": "current",     "icon": "mdi:current-ac"},
    "input.current.nominal":    {"unit": "A",   "device_class": "current",     "icon": "mdi:current-ac"},
    "input.frequency":          {"unit": "Hz",  "device_class": "frequency",   "icon": "mdi:sine-wave"},
    "input.frequency.nominal":  {"unit": "Hz",  "device_class": "frequency",   "icon": "mdi:sine-wave"},
    "input.power":              {"unit": "W",   "device_class": "power",       "icon": "mdi:flash"},
    "input.realpower":          {"unit": "W",   "device_class": "power",       "icon": "mdi:flash"},
    "input.voltage":            {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    "input.voltage.maximum":    {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    "input.voltage.minimum":    {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    "input.voltage.nominal":    {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    "input.transfer.high":      {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    "input.transfer.low":       {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    # Output
    "output.current":           {"unit": "A",   "device_class": "current",     "icon": "mdi:current-ac"},
    "output.current.nominal":   {"unit": "A",   "device_class": "current",     "icon": "mdi:current-ac"},
    "output.frequency":         {"unit": "Hz",  "device_class": "frequency",   "icon": "mdi:sine-wave"},
    "output.frequency.nominal": {"unit": "Hz",  "device_class": "frequency",   "icon": "mdi:sine-wave"},
    "output.power":             {"unit": "W",   "device_class": "power",       "icon": "mdi:flash"},
    "output.realpower":         {"unit": "W",   "device_class": "power",       "icon": "mdi:flash"},
    "output.voltage":           {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    "output.voltage.nominal":   {"unit": "V",   "device_class": "voltage",     "icon": "mdi:lightning-bolt"},
    # UPS
    "ups.efficiency":           {"unit": "%",   "device_class": None,          "icon": "mdi:percent"},
    "ups.load":                 {"unit": "%",   "device_class": None,          "icon": "mdi:gauge"},
    "ups.load.high":            {"unit": "%",   "device_class": None,          "icon": "mdi:gauge-full"},
    "ups.power":                {"unit": "W",   "device_class": "power",       "icon": "mdi:flash"},
    "ups.power.nominal":        {"unit": "W",   "device_class": "power",       "icon": "mdi:flash"},
    "ups.realpower":            {"unit": "W",   "device_class": "power",       "icon": "mdi:flash"},
    "ups.realpower.nominal":    {"unit": "W",   "device_class": "power",       "icon": "mdi:flash"},
    "ups.temperature":          {"unit": "°C",  "device_class": "temperature", "icon": "mdi:thermometer"},
    "ups.beeper.status":        {"unit": None,  "device_class": None,          "icon": "mdi:volume-high"},
    "ups.delay.reboot":         {"unit": "s",   "device_class": "duration",    "icon": "mdi:timer"},
    "ups.delay.shutdown":       {"unit": "s",   "device_class": "duration",    "icon": "mdi:timer-off"},
    "ups.delay.start":          {"unit": "s",   "device_class": "duration",    "icon": "mdi:timer-play"},
    "ups.status":               {"unit": None,  "device_class": None,          "icon": "mdi:power-plug"},
}

# Variables to mark as diagnostic (device info, not operational data)
DIAGNOSTIC_PREFIXES = (
    "ups.firmware",
    "ups.mfr",
    "ups.model",
    "ups.serial",
    "ups.vendorid",
    "ups.productid",
    "ups.id",
    "driver.",
    "device.",
)

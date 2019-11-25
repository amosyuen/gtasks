"""Constants for gtasks."""
# Base component constants
DOMAIN = "gtasks"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.2.0"
PLATFORMS = ["sensor", "binary_sensor"]
REQUIRED_FILES = [
    ".translations/en.json",
    "const.py",
    "config_flow.py",
    "manifest.json",
    "sensor.py",
    "services.yaml",
    "binary_sensor.py",
]
ISSUE_URL = "https://github.com/BlueBlueBlob/gtasks/issues"
ATTRIBUTION = "Data from this is provided by gtasks."

# Icons
ICON = "mdi:check-bold"

# Device classes
SENSOR_UNIT_OF_MEASUREMENT = "Task(s)"

# Configuration
CONF_BINARY_SENSOR = "binary_sensor"
CONF_SENSOR = "sensor"
CONF_NAME = "name"
CONF_CREDENTIALS_LOCATION = "credentials_location"
CONF_DEFAULT_LIST = "default_list"
CONF_TOKEN_FILE = "token_location"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_TOKEN_LOCATION = '/config/token.pickle'

#Services attributes
ATTR_TASK_TITLE = "task_title"
ATTR_DUE_DATE = "due_date"

#Services names
SERVICE_NEW_TASK = "new_task"
SERVICE_COMPLETE_TASK = "complete_task"


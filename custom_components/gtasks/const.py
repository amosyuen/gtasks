"""Constants for gtasks."""
# Base component constants
DOMAIN = "gtasks"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.4.2"
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
CONF_TASKS_LISTS = "tasks_lists"
CONF_TOKEN_PATH = "token_location"
CONF_TOKEN_NAME = 'token.pickle'

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_TOKEN_LOCATION = '/config'


#Services attributes
ATTR_TASK_TITLE = "task_title"
ATTR_DUE_DATE = "due_date"
ATTR_TASKS_LIST = "tasks_list"

#Services names
SERVICE_NEW_TASK = "new_task"
SERVICE_COMPLETE_TASK = "complete_task"

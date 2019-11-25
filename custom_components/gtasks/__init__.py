"""
Component to integrate with gtasks.

For more details about this component, please refer to
https://github.com/BlueBlueBlob/gtasks
"""
import os
from datetime import timedelta, date, datetime
import logging
import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.util import Throttle
from homeassistant.core import callback

from gtasks_api import GtasksAPI

from integrationhelper.const import CC_STARTUP_VERSION

from .const import (
    CONF_BINARY_SENSOR,
    CONF_NAME,
    CONF_SENSOR,
    DEFAULT_NAME,
    DEFAULT_TOKEN_LOCATION,
    DOMAIN_DATA,
    DOMAIN,
    ISSUE_URL,
    PLATFORMS,
    REQUIRED_FILES,
    VERSION,
    CONF_CREDENTIALS_LOCATION,
    CONF_TOKEN_FILE,
    CONF_DEFAULT_LIST,
    ATTR_TASK_TITLE,
    ATTR_DUE_DATE,
    SERVICE_NEW_TASK,
    SERVICE_COMPLETE_TASK,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

NEW_TASK_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TASK_TITLE): cv.string,
        vol.Optional(ATTR_DUE_DATE): cv.date,
    }
)

COMPLETE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TASK_TITLE): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_CREDENTIALS_LOCATION): cv.string,
                vol.Required(CONF_DEFAULT_LIST): cv.string,
                vol.Optional(CONF_TOKEN_FILE, default = DEFAULT_TOKEN_LOCATION): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up this component using YAML."""
    
    if config.get(DOMAIN) is None:
        # We get her if the integration is set up using config flow
        return True

    # Print startup message

    # Check that all required files are present
    file_check = await check_files(hass)
    if not file_check:
        return False

    # Create DATA dict
    hass.data[DOMAIN_DATA] = {}

    # Get "global" configuration.
    creds = config[DOMAIN].get(CONF_CREDENTIALS_LOCATION)
    default_list = config[DOMAIN].get(CONF_DEFAULT_LIST)
    token_file = config[DOMAIN].get(CONF_TOKEN_FILE)
    hass.data[DOMAIN_DATA]["creds"] = creds
    hass.data[DOMAIN_DATA]["token_file"] = token_file
    hass.data[DOMAIN_DATA]["default_list"] = default_list
    _LOGGER.debug('hass : {}'.format(hass.data[DOMAIN_DATA]))
    return True

async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""
    
    conf = hass.data.get(DOMAIN_DATA)
    if config_entry.source == config_entries.SOURCE_IMPORT:
        if conf is None:
            hass.async_create_task(
                hass.config_entries.async_remove(config_entry.entry_id)
            )
        return False

    # Print startup message
    _LOGGER.debug(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
    )

    # Create DATA dict
    #hass.data[DOMAIN_DATA] = {}

    # Get "global" configuration.

    # Configure the client.
    
    creds = hass.data[DOMAIN_DATA]["creds"]
    token_file = hass.data[DOMAIN_DATA]["token_file"]
    default_list = hass.data[DOMAIN_DATA]["default_list"]
    gapi = hass.data[DOMAIN_DATA].get("gtasks_obj", GtasksAPI(creds, token_file))
    _LOGGER.debug('gtasks : {}'.format(gapi))
    hass.data[DOMAIN_DATA]["client"] = GtasksData(hass, gapi, default_list)
    
    # Add binary_sensor
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, "binary_sensor")
    )

    # Add sensor
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )

    @callback
    def new_task(call):
        title = call.data.get(ATTR_TASK_TITLE)
        due_date = call.data.get(ATTR_DUE_DATE, None)
        client = hass.data[DOMAIN_DATA]["client"]
        task = {}
        task['title'] = title
        if due_date:
             task['due'] = datetime.strftime(due_date, '%Y-%m-%dT00:00:00.000Z')

        _LOGGER.debug('task : {}'.format(task))
        try:
            client._service.tasks().insert(tasklist=client.default_list_id, body=task).execute()
        except Exception as e:
            _LOGGER.exception(e)
            
            
    @callback
    def complete_task(call):
        task_name = call.data.get(ATTR_TASK_TITLE)
        client = hass.data[DOMAIN_DATA]["client"]
        service = client._service
        try:
            task_id = client.gapi.get_task_id(client.default_list_id, task_name)
            task_to_complete = service.tasks().get(tasklist=client.default_list_id, task=task_id).execute()
            task_to_complete['status'] = 'completed'
            service.tasks().update(tasklist=client.default_list_id, task=task_to_complete['id'], body=task_to_complete).execute()
        except Exception as e:
            _LOGGER.exception(e)
        
    #Register "new_task" service
    hass.services.async_register(
        DOMAIN, SERVICE_NEW_TASK, new_task, schema=NEW_TASK_SCHEMA
    )

    
    #Register "comple_task" service
    hass.services.async_register(
        DOMAIN, SERVICE_COMPLETE_TASK, complete_task, schema=COMPLETE_TASK_SCHEMA
    )
    
    return True


class GtasksData:
    """This class handle communication and stores the data."""

    def __init__(self, hass, gapi, default_list):
        """Initialize the class."""
        self.hass = hass
        self.gapi = gapi
        self._service = self.gapi.service
        _LOGGER.debug('gapi : {} , service : {}'.format(self.gapi,self._service))
        self.default_list = default_list
        self.default_list_id = self.gapi.get_taskslist_id(self.default_list)
        _LOGGER.debug('task list id : {}'.format(self.default_list_id))

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update_data(self):
        today = date.today().strftime('%Y-%m-%dT00:00:00.000Z')
        request_sensor = self._service.tasks().list(tasklist=self.default_list_id, showCompleted= False)
        request_binary_sensor = self._service.tasks().list(tasklist=self.default_list_id, showCompleted=False, dueMax=today )
        tag_sensor = CONF_SENSOR + "_data"
        tag_binary = CONF_BINARY_SENSOR + "_data"
        try:
            tasks_list_sensor = await self.hass.async_add_executor_job(request_sensor.execute)
            self.hass.data[DOMAIN_DATA][tag_sensor] = tasks_list_sensor['items']
            _LOGGER.debug('tasks_list : {}'.format(tasks_list_sensor))
        except Exception as e:
            _LOGGER.exception(e) 
        try:
            tasks_list_binary = await self.hass.async_add_executor_job(request_binary_sensor.execute)
            self.hass.data[DOMAIN_DATA][tag_binary] = tasks_list_binary['items']
            _LOGGER.debug('tasks_list : {}'.format(tasks_list_binary))
        except Exception as e:
            _LOGGER.exception(e)

async def check_files(hass):
    """Return bool that indicates if all files are present."""
    # Verify that the user downloaded all files.
    base = f"{hass.config.path()}/custom_components/{DOMAIN}/"
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue


async def async_remove_entry(hass, config_entry):
    """Handle removal of an entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(
            config_entry, "binary_sensor"
        )
        _LOGGER.debug(
            "Successfully removed binary_sensor from the gtasks integration"
        )
    except ValueError:
        pass

    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
        _LOGGER.debug("Successfully removed sensor from the gtasks integration")
    except ValueError:
        pass

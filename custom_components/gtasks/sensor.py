"""Sensor platform for Gtasks."""
from homeassistant.helpers.entity import Entity
from datetime import timedelta, date
from uuid import getnode as get_mac

from .const import (
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN_DATA,
    ICON,
    DOMAIN,
    SENSOR_UNIT_OF_MEASUREMENT,
    CONF_SENSOR,
)

from datetime import datetime, timedelta

async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    async_add_entities([GtasksSensor(hass, discovery_info)], True)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    async_add_devices([GtasksSensor(hass, {})], True)


class GtasksSensor(Entity):
    """blueprint Sensor class."""

    def __init__(self, hass, config):
        self.hass = hass
        self.attr = {}
        self._state = None
        self._list = hass.data[DOMAIN_DATA]["default_list"]
        self._name = '{}_{}'.format(config.get("name", DEFAULT_NAME),self._list)
        self._unique_id = '{}-{}-{}'.format(get_mac() , CONF_SENSOR, self._name)

    async def async_update(self):
        """Update the sensor."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["client"].get_tasks()

        # Get new data (if any)
        task_list = self.hass.data[DOMAIN_DATA].get("tasks_list", None)
        data = []
        # Check the data and update the value.
        if task_list is None:
            self._state = self._state
        else:
            self._state = len(task_list)
            for t in task_list:
                jtask = {}
                jtask["task_title"] = '{}'.format(t.title)
                jtask["due_date"] = '{}'.format(t.due_date)
                data.append(jtask)

        # Set/update attributes
        self.attr["attribution"] = ATTRIBUTION
        self.attr["tasks"] = data


    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self._unique_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "Gtasks",
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def unit_of_measurement(self):
        return SENSOR_UNIT_OF_MEASUREMENT

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr

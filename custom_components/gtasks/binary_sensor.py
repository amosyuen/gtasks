"""Binary sensor platform for gtasks."""
from homeassistant.components.binary_sensor import BinarySensorDevice
from datetime import timedelta, date, datetime
from uuid import getnode as get_mac

from .const import (
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN_DATA,
    DOMAIN,
    CONF_BINARY_SENSOR,
)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup binary_sensor platform."""
    async_add_entities([GtasksBinarySensor(hass, discovery_info)], True)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    tasks_lists = hass.data[DOMAIN_DATA]["tasks_lists"]
    for list in tasks_lists:
        async_add_devices([GtasksBinarySensor(hass, {}, list)], True)


class GtasksBinarySensor(BinarySensorDevice):
    """gtasks binary_sensor class."""

    def __init__(self, hass, config, list):
        self.hass = hass
        self.attr = {}
        self._status = False
        self._list = list
        self._name = '{}_{}'.format(config.get("name", DEFAULT_NAME),self._list)
        self._unique_id = '{}-{}-{}'.format(get_mac() , CONF_BINARY_SENSOR, self._name)

    async def async_update(self):
        """Update the binary_sensor."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["client"].update_binary_data(self._list)

        # Get new data (if any)
        passed_list = self.hass.data[DOMAIN_DATA].get(self._list + CONF_BINARY_SENSOR + "_data", None)
        data = []
        # Check the data and update the value.
        if not passed_list or passed_list is None:
            self._status = False
        else:
            for task in passed_list:
                dict = {}
                dict['taskt_title'] = '{}'.format(task['title'])
                dict['due_date'] = datetime.strftime(datetime.strptime(task['due'], '%Y-%m-%dT00:00:00.000Z').date(), '%Y-%m-%d')
                tdelta = date.today() - datetime.strptime(task['due'], '%Y-%m-%dT00:00:00.000Z').date()
                dict['days_overdue'] = tdelta.days
                data.append(dict)
            self._status = True

        # Set/update attributes
        self.attr["attribution"] = ATTRIBUTION
        self.attr["tasks"] = data

    @property
    def unique_id(self):
        """Return a unique ID to use for this binary_sensor."""
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
        """Return the name of the binary_sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self._status

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr

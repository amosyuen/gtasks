"""Adds config flow for Gtasks."""
from collections import OrderedDict

import asyncio
import logging
import voluptuous as vol

from gtasks2 import Gtasks

from homeassistant import config_entries

from homeassistant.util.json import load_json

from .const import DOMAIN, DOMAIN_DATA

DATA_FLOW_IMPL = "gtasks_flow_implementation"
_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class GtasksFlowHandler(config_entries.ConfigFlow):
    """Config flow for Gtasks."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    
    def __init__(self):
        
        self._auth_url = "" 

    async def async_step_init(self, user_input=None):
        """Initialize."""
        self._errors = {}
        
        _LOGGER.info("init config flow")
        
        
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")
            
            
        return await self.async_step_link(user_input)
        
    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        return await self.async_step_init(user_input)
        
    async def async_step_link(self, user_input=None):
        
        url = self.hass.data[DOMAIN_DATA]["auth_url"]
        _LOGGER.info('url : {}'.format(url))
        if not url:
            return self.async_create_entry(title="Connected", data={})
        
        if user_input is not None:
            if user_input["auth_code"] is not None:
                try:
                    await self.hass.async_add_executor_job(
                        self.hass.data[DOMAIN_DATA]["gtasks_obj"].finish_login,
                        user_input["auth_code"]
                    )
                except Exception as e:
                    _LOGGER.exception(e)
                    raise e
                return self.async_create_entry(title="Connected", data={})

        return self.async_show_form(
            step_id="link",
            description_placeholders={"url": url},
            data_schema=vol.Schema({vol.Required("auth_code"): str}),
            errors=self._errors,
        )

    async def async_step_import(self, user_input):  # pylint: disable=unused-argument
        """Import a config entry.
        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})


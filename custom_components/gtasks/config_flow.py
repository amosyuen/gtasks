"""Adds config flow for Gtasks."""
from collections import OrderedDict

import asyncio
import os
import logging
import voluptuous as vol

from homeassistant import config_entries
from gtasks_api import GtasksAPI

from homeassistant.util.json import load_json

from .const import DOMAIN, DOMAIN_DATA, DEFAULT_TOKEN_LOCATION, CONF_TOKEN_NAME

DATA_FLOW_IMPL = "gtasks_flow_implementation"
_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class GtasksFlowHandler(config_entries.ConfigFlow):
    """Config flow for Gtasks."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    
    def __init__(self):
        self._auth_url = "" 
        self.token_file = ""
        self.creds = ""
        self.gtasks_obj  = None
        self.tasks_lists = []
        self.all_lists = []

    async def async_step_init(self, user_input=None):
        """Initialize."""
        self._errors = {}
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")

        try:
            if self.creds and self.token_file:
                self.gtasks_obj = GtasksAPI(self.creds, self.token_file)
                if self.gtasks_obj.auth_url:
                    self._auth_url = self.gtasks_obj.auth_url
                else:
                    return self.async_create_entry(title="Connected", data={})
        except Exception as e:
            _LOGGER.exception(e)
            raise e

        return await self.async_step_config(user_input)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        return await self.async_step_init(user_input)

    async def async_step_config(self, user_input=None):
        token_path = ""
        creds = ""
        errors = {}
        if user_input is not None:
            if await self.hass.async_add_job(os.path.isfile, user_input["creds"]):
                if await self.hass.async_add_job(os.path.isdir, user_input["token_path"]):
                    try:
                        self.token_file = '{}/{}'.format(user_input["token_path"], CONF_TOKEN_NAME)
                        self.gtasks_obj = await self.hass.async_add_executor_job(
                            GtasksAPI,
                            user_input["creds"],
                            self.token_file)
                        self.creds = user_input["creds"]
                    except Exception as e:
                        _LOGGER.exception(e)
                        raise e
                    if self.gtasks_obj.auth_url:
                        self._auth_url = self.gtasks_obj.auth_url
                        return await self.async_step_auth()
                    else:
                        self.all_lists = await self._get_all_lists()
                        return await self.async_step_list()
                else:
                    errors["token_path"] = "no_token_path"
            else:
                errors["creds"] = "no_creds"

        return self.async_show_form(
            step_id="config",
            data_schema=vol.Schema(
                {
                    vol.Required("creds") : str,
                    vol.Optional("token_path", default = DEFAULT_TOKEN_LOCATION): str,
                }),
            errors=errors,
        )

    async def async_step_list(self, user_input=None):
        errors = {}
        finish_choice = False
        all_lists_name = self.all_lists
        list_added = ""

        if user_input is not None:
            if "tasks_list" in user_input:
                self.tasks_lists.append(user_input["tasks_list"])
            else:
                if not self.tasks_lists:
                    errors["tasks_list"] = "no_list"
            for list_name in all_lists_name:
                if list_name in self.tasks_lists:
                    all_lists_name.remove(list_name)
            for tl in self.tasks_lists:
                list_added += tl + " "
            if user_input["finish_choice"]:
                data = {}
                data["creds"] = self.creds
                data["token_file"] = self.token_file
                data["tasks_lists"] = self.tasks_lists
                return self.async_create_entry(title="Connected", data=data)

        data_schema = OrderedDict()
        if self.tasks_lists:
            data_schema[vol.Optional("tasks_list")] = vol.In(all_lists_name)
        else:
            data_schema[vol.Required("tasks_list")] = vol.In(all_lists_name)
        data_schema[vol.Optional("finish_choice", default = False)] = bool
        return self.async_show_form(
            step_id="list",
            description_placeholders={"lists_added": list_added},
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )

    async def async_step_auth(self, user_input=None):
        url = self._auth_url
        if not url:
            return await self.async_step_list()
        
        if user_input is not None:
            if user_input["auth_code"] is not None:
                try:
                    await self.hass.async_add_executor_job(
                        self.gtasks_obj.finish_login,
                        user_input["auth_code"]
                    )
                except Exception as e:
                    _LOGGER.exception(e)
                    raise e
                self.all_lists = await self._get_all_lists()
                return await self.async_step_list()

        return self.async_show_form(
            step_id="auth",
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

    async def _get_all_lists(self):
        all_lists_name = []
        try:
            request = self.gtasks_obj.service.tasklists().list()
            all_lists = await self.hass.async_add_executor_job(request.execute)
            for taskslist in all_lists['items']:
                all_lists_name.append(taskslist['title'])
        except Exception as e:
            _LOGGER.exception(e)
            raise e
        return all_lists_name

"""Config flow for PlugShare."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, API_BASE_URL, DEFAULT_AUTH, DEFAULT_USER_AGENT

class PlugShareConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PlugShare."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle initial step."""
        errors = {}

        if user_input is not None:
            location_id = str(user_input["location_id"]).strip()
            
            # Validate location ID against API
            session = async_get_clientsession(self.hass)
            url = API_BASE_URL.format(location_id=location_id)
            headers = {
                "Authorization": DEFAULT_AUTH,
                "User-Agent": DEFAULT_USER_AGENT,
                "Accept": "application/json, text/plain, */*",
            }

            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        title = data.get("name", f"Station {location_id}")
                        await self.async_set_unique_id(location_id)
                        self._abort_if_unique_id_configured()
                        return self.async_create_entry(title=title, data={"location_id": location_id})
                    else:
                        errors["base"] = "invalid_location"
            except Exception:
                errors["base"] = "cannot_connect"

        schema = vol.Schema({
            vol.Required("location_id"): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
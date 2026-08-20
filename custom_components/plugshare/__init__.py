"""The PlugShare Integration."""
from datetime import datetime, timedelta, timezone
import logging
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_BASE_URL, DEFAULT_AUTH, DEFAULT_USER_AGENT, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PlugShare from a config entry."""
    location_id = entry.data["location_id"]
    scan_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    
    session = async_get_clientsession(hass)
    url = API_BASE_URL.format(location_id=location_id)
    
    headers = {
        "Authorization": DEFAULT_AUTH,
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.plugshare.com",
        "Referer": f"https://www.plugshare.com/location/{location_id}",
    }

    async def async_update_data():
        try:
            async with asyncio.timeout(15):
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"PlugShare API error {response.status}: {await response.text()}")
                    data = await response.json()
                    data["_last_api_refresh"] = datetime.now(timezone.utc).isoformat()
                    return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with PlugShare API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"PlugShare {location_id}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
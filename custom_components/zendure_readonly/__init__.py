from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import ZendureCoordinator


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, entry):
    host = entry.data["host"]

    coordinator = ZendureCoordinator(hass, host)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault("zendure_readonly", {})
    hass.data["zendure_readonly"][entry.entry_id] = coordinator

    # Forward to platforms (sensor, etc.)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok

"""Binary sensor platform for PlugShare."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up PlugShare binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data
    location_id = str(data.get("id"))

    station = data.get("stations", [{}])[0]
    network_name = (
        station.get("network", {}).get("name")
        or station.get("cpo_name")
        or "PlugShare"
    )
    serial_number = station.get("name") or station.get("network_ext_id")

    device_info = DeviceInfo(
        identifiers={(DOMAIN, location_id)},
        name=data.get("name", f"PlugShare {location_id}"),
        manufacturer=network_name,
        model=data.get("poi_name", "EV Charger"),
        serial_number=serial_number,
        configuration_url=f"https://www.plugshare.com/location/{location_id}",
    )

    entities = [
        PlugShareOpen247BinarySensor(coordinator, location_id, device_info),
        PlugShareUnderRepairBinarySensor(coordinator, location_id, device_info),
        PlugShareFastChargerBinarySensor(coordinator, location_id, device_info),
        PlugShareAccessCardBinarySensor(coordinator, location_id, device_info),
    ]

    async_add_entities(entities)

class PlugShareBaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base binary sensor for PlugShare."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator)
        self._location_id = location_id
        self._attr_device_info = device_info

class PlugShareOpen247BinarySensor(PlugShareBaseBinarySensor):
    """24/7 Access status."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "24/7 Access"
        self._attr_unique_id = f"plugshare_{location_id}_open247"
        self._attr_icon = "mdi:clock-check-outline"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self):
        return bool(self.coordinator.data.get("open247", False))

class PlugShareUnderRepairBinarySensor(PlugShareBaseBinarySensor):
    """Maintenance alert flag."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Under Repair"
        self._attr_unique_id = f"plugshare_{location_id}_under_repair"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self):
        # Turns 'on' (Problem) if under_repair is True or status indicates repair
        d = self.coordinator.data
        return bool(d.get("under_repair", False) or "REPAIR" in d.get("status", ""))

class PlugShareFastChargerBinarySensor(PlugShareBaseBinarySensor):
    """DC Fast Charger indicator."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Fast Charger (DCFC)"
        self._attr_unique_id = f"plugshare_{location_id}_is_fast_charger"
        self._attr_icon = "mdi:flash"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self):
        return bool(self.coordinator.data.get("is_fast_charger", False))

class PlugShareAccessCardBinarySensor(PlugShareBaseBinarySensor):
    """RFID/Access Card Requirement."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Requires Access Card"
        self._attr_unique_id = f"plugshare_{location_id}_requires_access_card"
        self._attr_device_class = BinarySensorDeviceClass.LOCK
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self):
        try:
            return bool(self.coordinator.data["stations"][0].get("requiresAccessCard", False))
        except (IndexError, KeyError):
            return False
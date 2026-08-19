"""Sensor platform for PlugShare."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.util import dt as dt_util

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up PlugShare sensors."""
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
        PlugShareMainStatusSensor(coordinator, location_id, device_info),
        PlugShareAvailableStallsSensor(coordinator, location_id, device_info),
        PlugShareOccupiedStallsSensor(coordinator, location_id, device_info),
        PlugShareCostSensor(coordinator, location_id, device_info),
        PlugShareNetworkSensor(coordinator, location_id, device_info),
        PlugShareParkingTypeSensor(coordinator, location_id, device_info),
        PlugSharePoiSensor(coordinator, location_id, device_info),
        PlugShareStationIdSensor(coordinator, location_id, device_info),
    ]

    # Dynamically generate sensors for all outlets
    stations = data.get("stations", [])
    if stations:
        for idx, outlet in enumerate(stations[0].get("outlets", [])):
            entities.append(PlugShareOutletSensor(coordinator, location_id, idx, device_info))
            entities.append(PlugShareLastChangedSensor(coordinator, location_id, idx, device_info))
            entities.append(PlugSharePowerSensor(coordinator, location_id, idx, device_info))
            entities.append(PlugShareVoltageSensor(coordinator, location_id, idx, device_info))
            entities.append(PlugShareAmperageSensor(coordinator, location_id, idx, device_info))

    async_add_entities(entities)

class PlugShareBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for PlugShare."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator)
        self._location_id = location_id
        self._attr_device_info = device_info

class PlugShareMainStatusSensor(PlugShareBaseSensor):
    """Overall location status sensor."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Overall Status"
        self._attr_unique_id = f"plugshare_{location_id}_overall_status"
        self._attr_icon = "mdi:ev-station"

    @property
    def native_value(self):
        status = self.coordinator.data.get("status", "Unknown")
        return status.replace("_", " ").title()

    @property
    def extra_state_attributes(self):
        d = self.coordinator.data
        st = d.get("stations", [{}])[0]
        return {
            "location_id": d.get("id"),
            "station_id": st.get("id"),
            "serial_number": st.get("name"),
            "latitude": d.get("latitude"),
            "longitude": d.get("longitude"),
            "address": d.get("address"),
            "total_stations": d.get("station_count"),
            "connector_types": d.get("connector_types"),
            "score": d.get("confidence"),
            "cost_description": d.get("cost_description"),
        }

class PlugShareAvailableStallsSensor(PlugShareBaseSensor):
    """Available stalls counter."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Available Stalls"
        self._attr_unique_id = f"plugshare_{location_id}_available_stalls"
        self._attr_icon = "mdi:car-electric"
        self._attr_native_unit_of_measurement = "stalls"

    @property
    def native_value(self):
        return int(self.coordinator.data.get("available_station_count", 0))

class PlugShareOccupiedStallsSensor(PlugShareBaseSensor):
    """Occupied stalls counter."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Occupied Stalls"
        self._attr_unique_id = f"plugshare_{location_id}_in_use_stalls"
        self._attr_icon = "mdi:car-connected"
        self._attr_native_unit_of_measurement = "stalls"

    @property
    def native_value(self):
        return int(self.coordinator.data.get("in_use_station_count", 0))

class PlugShareCostSensor(PlugShareBaseSensor):
    """Pricing and tariff sensor."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Charging Cost"
        self._attr_unique_id = f"plugshare_{location_id}_cost"
        self._attr_icon = "mdi:currency-usd"

    @property
    def native_value(self):
        try:
            return self.coordinator.data["stations"][0]["outlets"][0]["prices"][0].get("tariff_generated_text", "Free")
        except (IndexError, KeyError, TypeError):
            return self.coordinator.data.get("cost_description", "Unknown")

class PlugShareNetworkSensor(PlugShareBaseSensor):
    """Network operator sensor."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Network Provider"
        self._attr_unique_id = f"plugshare_{location_id}_network"
        self._attr_icon = "mdi:lan"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        try:
            return self.coordinator.data["stations"][0]["network"].get("name", "Unknown")
        except (IndexError, KeyError):
            return "Unknown"

class PlugShareParkingTypeSensor(PlugShareBaseSensor):
    """Parking access type sensor."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Parking Type"
        self._attr_unique_id = f"plugshare_{location_id}_parking_type"
        self._attr_icon = "mdi:parking"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self.coordinator.data.get("parking_type_name", "Unknown")

class PlugSharePoiSensor(PlugShareBaseSensor):
    """Point of interest categorization."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Location Type"
        self._attr_unique_id = f"plugshare_{location_id}_poi_name"
        self._attr_icon = "mdi:map-marker-outline"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self.coordinator.data.get("poi_name", "Unknown")

class PlugShareOutletSensor(PlugShareBaseSensor):
    """Individual outlet status sensor."""
    def __init__(self, coordinator, location_id, outlet_index, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._outlet_index = outlet_index
        self._attr_name = f"Plug {outlet_index + 1} Status"
        self._attr_unique_id = f"plugshare_{location_id}_outlet_{outlet_index + 1}"
        self._attr_icon = "mdi:power-plug"

    @property
    def native_value(self):
        try:
            status = self.coordinator.data["stations"][0]["outlets"][self._outlet_index].get("status", "Unknown")
            return status.replace("_", " ").title()
        except (IndexError, KeyError):
            return "Unavailable"

    @property
    def extra_state_attributes(self):
        try:
            outlet = self.coordinator.data["stations"][0]["outlets"][self._outlet_index]
            return {
                "connector_name": outlet.get("connector_name"),
                "power_type": outlet.get("power_type"),
                "evse_id": outlet.get("evse_ext_id"),
            }
        except (IndexError, KeyError):
            return {}

class PlugShareLastChangedSensor(PlugShareBaseSensor):
    """Timestamp of the last status change on a specific plug."""
    def __init__(self, coordinator, location_id, outlet_index, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._outlet_index = outlet_index
        self._attr_name = f"Plug {outlet_index + 1} Last Changed"
        self._attr_unique_id = f"plugshare_{location_id}_plug_{outlet_index + 1}_status_changed"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self):
        try:
            raw_ts = self.coordinator.data["stations"][0]["outlets"][self._outlet_index].get("status_changed_at")
            return dt_util.parse_datetime(raw_ts) if raw_ts else None
        except (IndexError, KeyError):
            return None

class PlugSharePowerSensor(PlugShareBaseSensor):
    """Max rated kW output of the outlet."""
    def __init__(self, coordinator, location_id, outlet_index, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._outlet_index = outlet_index
        self._attr_name = f"Plug {outlet_index + 1} Power"
        self._attr_unique_id = f"plugshare_{location_id}_plug_{outlet_index + 1}_power"
        self._attr_native_unit_of_measurement = "kW"
        self._attr_device_class = SensorDeviceClass.POWER

    @property
    def native_value(self):
        try:
            return float(self.coordinator.data["stations"][0]["outlets"][self._outlet_index].get("kilowatts", 0))
        except (IndexError, KeyError, TypeError):
            return None

class PlugShareVoltageSensor(PlugShareBaseSensor):
    """Voltage rating of the outlet."""
    def __init__(self, coordinator, location_id, outlet_index, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._outlet_index = outlet_index
        self._attr_name = f"Plug {outlet_index + 1} Voltage"
        self._attr_unique_id = f"plugshare_{location_id}_plug_{outlet_index + 1}_volts"
        self._attr_native_unit_of_measurement = "V"
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        try:
            return self.coordinator.data["stations"][0]["outlets"][self._outlet_index].get("volts")
        except (IndexError, KeyError):
            return None

class PlugShareAmperageSensor(PlugShareBaseSensor):
    """Amperage rating of the outlet."""
    def __init__(self, coordinator, location_id, outlet_index, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._outlet_index = outlet_index
        self._attr_name = f"Plug {outlet_index + 1} Current"
        self._attr_unique_id = f"plugshare_{location_id}_plug_{outlet_index + 1}_amps"
        self._attr_native_unit_of_measurement = "A"
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        try:
            return self.coordinator.data["stations"][0]["outlets"][self._outlet_index].get("amps")
        except (IndexError, KeyError):
            return None

class PlugShareStationIdSensor(PlugShareBaseSensor):
    """Hardware station and serial identification."""
    def __init__(self, coordinator, location_id, device_info):
        super().__init__(coordinator, location_id, device_info)
        self._attr_name = "Station ID"
        self._attr_unique_id = f"plugshare_{location_id}_station_id"
        self._attr_icon = "mdi:identifier"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        try:
            return self.coordinator.data["stations"][0].get("id")
        except (IndexError, KeyError):
            return "Unknown"

    @property
    def extra_state_attributes(self):
        try:
            st = self.coordinator.data["stations"][0]
            return {
                "serial_number": st.get("name"),
                "network_ext_id": st.get("network_ext_id"),
                "cpo_id": st.get("cpo_id"),
            }
        except (IndexError, KeyError):
            return {}
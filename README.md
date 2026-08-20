# PlugShare for Home Assistant

![](custom_components/plugshare/brand/icon.png)

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![HACS Validation](https://github.com/nadeemsultan/homeassistant-plugshare/actions/workflows/hacs.yaml/badge.svg)](https://github.com/nadeemsultan/homeassistant-plugshare/actions/workflows/hacs.yaml)

A custom integration for Home Assistant to monitor PlugShare EV charging locations, real-time stall availability, individual plug status, power ratings, and charging session timestamps.

## Features
- **Live Occupancy:** Real-time available and in-use stall counters.
- **Plug Monitoring:** Per-outlet status (for example, `Charging`, `Available`, or `Out of order`), power output (kW), voltage (V), current (A), and status change timestamps.
- **Location Diagnostics:** Pricing/tariffs, 24/7 access flags, repair problem alerts, and station hardware serial numbers.
- **UI Config Flow:** Simple setup using standard PlugShare Location IDs.

## Requirements

- Home Assistant 2024.1.0 or newer.
- Internet access from the Home Assistant host.
- A valid PlugShare location ID.

This integration does not require PlugShare account credentials. It retrieves station data from the PlugShare cloud service.


## Entities & Data Provided
Each configured PlugShare station creates a primary device representing the location with the following sensors and binary sensors. Entity IDs are generated from the station name.

### Station Sensors
| Entity | Entity ID pattern | Entity Category | Value | Description |
|---|---|---|---|---|
| Overall Status | `sensor.<station_name>_overall_status` | — | Text | Station operating status, such as `Available` or `Unknown`. Includes a `last_api_refresh` attribute containing the timestamp of the most recent successful PlugShare API poll. |
| Available Stalls | `sensor.<station_name>_available_stalls` | — | Number (`stalls`) | Currently open charging stalls. |
| Occupied Stalls | `sensor.<station_name>_occupied_stalls` | — | Number (`stalls`) | Stalls actively charging or otherwise occupied. |
| Charging Cost | `sensor.<station_name>_charging_cost` | — | Text | Tariff, hourly rate, or cost summary. |
| Network Provider | `sensor.<station_name>_network_provider` | Diagnostic | Text | Charging network or operator name. |
| Parking Type | `sensor.<station_name>_parking_type` | Diagnostic | Text | Parking access type, such as `Public` or `Customer Only`. |
| Location Type | `sensor.<station_name>_location_type` | Diagnostic | Text | Point-of-interest category, such as `Hotel` or `Parking Garage`. |
| Station ID | `sensor.<station_name>_station_id` | Diagnostic | Text | Station identifier. |

### Station Binary Sensors
| Entity | Entity ID pattern | Entity Category | Device Class | `on` state |
|---|---|---|---|---|
| 24/7 Access | `binary_sensor.<station_name>_24_7_access` | Diagnostic | — | Location is open 24/7. |
| Under Repair | `binary_sensor.<station_name>_under_repair` | — | `problem` | Station is under maintenance or its status indicates repair. |
| Fast Charger (DCFC) | `binary_sensor.<station_name>_fast_charger_dcfc` | Diagnostic | — | Location offers DC fast charging (Level 3). |
| Requires Access Card | `binary_sensor.<station_name>_requires_access_card` | Diagnostic | `lock` | An RFID keycard or membership fob is required. |

### Per-Outlet Sensors
For every outlet returned in the station metadata during setup (`Plug 1`, `Plug 2`, and so on), the integration creates:

| Entity | Entity ID pattern | Entity Category | Device Class | Unit | Description |
|---|---|---|---|---|---|
| Plug X Status | `sensor.<station_name>_plug_x_status` | — | — | — | Status returned by the API, formatted for display. |
| Plug X Power | `sensor.<station_name>_plug_x_power` | — | `power` | `kW` | Maximum rated power output. |
| Plug X Voltage | `sensor.<station_name>_plug_x_voltage` | Diagnostic | `voltage` | `V` | Rated connector voltage. |
| Plug X Current | `sensor.<station_name>_plug_x_current` | Diagnostic | `current` | `A` | Rated amperage limit. |
| Plug X Last Changed | `sensor.<station_name>_plug_x_last_changed` | — | `timestamp` | API-provided timezone | Parsed timestamp for the plug's last status change. |

## Installation

### Via HACS (Custom Repository)
1. In Home Assistant, open **HACS** > Three dots menu (top right) > **Custom repositories**.
2. Add repository URL: `https://github.com/nadeemsultan/homeassistant-plugshare`
3. Set Category to **Integration** and click **Add**.
4. Search for **PlugShare** and click **Download**.
5. Restart Home Assistant.

### Manual Installation
1. Download the latest release from the [Releases](https://github.com/nadeemsultan/homeassistant-plugshare/releases) page.
2. Copy the `custom_components/plugshare` folder into your Home Assistant `/config/custom_components/` directory.
3. Restart Home Assistant.


## Configuration
1. Go to **Settings** > **Devices & Services** > **Add Integration**.
2. Search for **PlugShare**.
3. Enter the target **Location ID**. The ID is the number at the end of a PlugShare location URL, such as `741158` in `https://www.plugshare.com/location/741158`.
4. Submit the form and complete the setup.

Each PlugShare location can only be configured once. To monitor another location, add another PlugShare integration entry with its own Location ID.

## Polling and Updates

- Station data is refreshed every 180 seconds (3 minutes).
- API requests time out after 15 seconds.
- The integration uses cloud polling, so availability depends on both Home Assistant's internet connection and the PlugShare service.
- The integration does not provide local charger control or guarantee hardware-level real-time status.

## Troubleshooting

| Message | Meaning | Action |
|---|---|---|
| Failed to connect to the PlugShare API. | Home Assistant could not reach the PlugShare service. | Check the Home Assistant host's internet access and review the Home Assistant logs. |
| Invalid Location ID or station not found. | The ID is invalid or the location is unavailable. | Verify the numeric ID in the PlugShare location URL. |
| This PlugShare location is already configured. | The location has already been added. | Use the existing integration entry or configure a different location. |

If data stops updating, check **Settings** > **System** > **Logs** for PlugShare errors. Temporary API or network failures may resolve on the next polling cycle.

## Data Limitations

Sensor values depend on the data returned by PlugShare. A station may have missing or stale pricing, ratings, outlet specifications, or availability data. Outlet entities are created from the station metadata available during setup, so stations with incomplete outlet information may expose fewer per-outlet sensors.

PlugShare status should be treated as informational and may not exactly match the physical state of a charger. This integration is read-only and does not start, stop, or control charging sessions.

## Removing the Integration

To remove a configured location, go to **Settings** > **Devices & Services**, open the **PlugShare** integration, and choose **Delete**. To change a Location ID, remove the existing entry and add PlugShare again with the new ID.

## Support

Before opening an issue, include the Home Assistant version, integration version, affected Location ID, relevant log messages, and a description of the expected and actual behavior. Do not include credentials or private network information.

- [Report a problem](https://github.com/nadeemsultan/homeassistant-plugshare/issues)
- [Project repository](https://github.com/nadeemsultan/homeassistant-plugshare)
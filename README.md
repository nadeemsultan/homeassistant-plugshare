# PlugShare for Home Assistant

A custom integration for Home Assistant to monitor PlugShare EV charging locations, real-time stall availability, individual plug status, power ratings, and charging session timestamps.

## Features
- **Live Occupancy:** Real-time available and in-use stall counters.
- **Plug Monitoring:** Per-outlet status (`Charging`, `Available`, `Outoforder`), power output (kW), voltage (V), current (A), and status change timestamps.
- **Location Diagnostics:** Pricing/tariffs, 24/7 access flags, repair problem alerts, and station hardware serial numbers.
- **UI Config Flow:** Simple setup using standard PlugShare Location IDs.

## Installation

### Via HACS (Custom Repository)
1. In Home Assistant, open **HACS** > Three dots menu (top right) > **Custom repositories**.
2. Add repository URL: `https://github.com/nadeemsultan/homeassistant-plugshare`
3. Set Category to **Integration** and click **Add**.
4. Search for **PlugShare EV Tracker** and click **Download**.
5. Restart Home Assistant.

### Manual Installation
1. Download the latest release from the [Releases](https://github.com/nadeemsultan/homeassistant-plugshare/releases) page.
2. Copy the `custom_components/plugshare` folder into your Home Assistant `/config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration
1. Go to **Settings** > **Devices & Services** > **Add Integration**.
2. Search for **PlugShare EV Tracker**.
3. Enter the target **Location ID** (e.g., from `https://www.plugshare.com/location/741158`, the ID is `741158`).
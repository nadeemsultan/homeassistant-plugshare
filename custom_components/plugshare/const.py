"""Constants for the PlugShare integration."""
from datetime import timedelta

DOMAIN = "plugshare"
DEFAULT_SCAN_INTERVAL = 180  # seconds

API_BASE_URL = "https://api.plugshare.com/v3/locations/{location_id}"
DEFAULT_AUTH = "Basic d2ViX3YyOkVOanNuUE54NHhXeHVkODU="
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
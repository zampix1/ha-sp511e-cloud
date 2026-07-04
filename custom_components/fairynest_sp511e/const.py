"""Constants for the SP511E integration."""

from __future__ import annotations

DOMAIN = "fairynest_sp511e"

CONF_ACCOUNT = "account"
CONF_PASSWORD = "password"
CONF_COUNTRY_CODE = "country_code"
CONF_DEVICE_SELECTOR = "device_selector"
CONF_SESSION_SID = "session_sid"
CONF_SESSION_TOKEN = "session_token"

DEFAULT_COUNTRY_CODE = "1"
DEFAULT_DEVICE_SELECTOR = "SP511E"
DEFAULT_SCAN_INTERVAL_SECONDS = 30

PLATFORMS = ["button", "light", "number", "select", "sensor"]

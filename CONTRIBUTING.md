# Contributing

Before opening an issue or pull request:

1. Confirm the device is an SP511E or clearly state the exact controller model.
2. State whether the official app still controls the device.
3. Redact account, password, session token, `hashKey`, `deviceCode`, `productKey`, LAN IPs, and private Home Assistant entity IDs.
4. Do not attach APKs, pulled app data, captures, or Home Assistant `.storage` files.
5. Include Home Assistant version, integration version, and the relevant log excerpt after redaction.

This integration is unofficial and cloud dependent. Changes should avoid raw command injection and keep writes limited to mapped SP511E commands.

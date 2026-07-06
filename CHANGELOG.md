# Changelog

## 0.1.8

- Records vendor command failures such as `407 device is offline` in the last command sensor instead of raising opaque Home Assistant service errors.
- Avoids optimistic state updates when the vendor cloud rejects a write.
- Adds cloud connectivity/state diagnostic sensors.

## 0.1.7

- Removes the temporary `sp511e_cloud.*` service alias because Home Assistant 2026.7 treats the alias as a missing integration when loading service descriptions.

## 0.1.6

- Fixes Home Assistant 2026.7 import compatibility by keeping the config entry service field local to the integration.

## 0.1.5

- Registers command services during global integration setup, before any config entry or entity platform work.
- Uses Home Assistant task scheduling for the initial refresh to avoid setup failure on newer core versions.

## 0.1.4

- Registers command services before entity platforms are loaded.
- Keeps command services available even if an entity platform setup fails.

## 0.1.3

- Ensures the integration loads entities and services even when the first cloud refresh fails.
- Runs the initial cloud refresh in the background instead of blocking Home Assistant setup.

## 0.1.2

- Restores the Home Assistant technical domain to `fairynest_sp511e` so existing config entries, entities and dashboards keep working.
- Keeps the public integration name as `SP511E Cloud`.
- Keeps `sp511e_cloud.*` as temporary service aliases for users who installed `0.1.0`.

## 0.1.1

- Adds a legacy `fairynest_sp511e` domain shim so existing Home Assistant config entries created before the public rename keep loading.
- Adds legacy service aliases under `fairynest_sp511e.*` so dashboards and scripts created before the public rename keep working after installing `SP511E Cloud`.
- Keeps the public integration domain as `sp511e_cloud`.

## 0.1.0

- Initial HACS-ready release candidate.
- Adds a cloud-dependent Home Assistant integration for SP511E controllers.
- Provides light, effect select, brightness/speed/sensitivity numbers, service calls, buttons, sensors, config flow, session refresh, and redacted diagnostics.

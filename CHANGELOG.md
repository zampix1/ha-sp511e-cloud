# Changelog

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

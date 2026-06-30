# Release Audit

## Repository Candidate

- Intended repository: `hass-fairynest-sp511e-cloud`
- Domain: `fairynest_sp511e`
- Publication status: prepared as a HACS custom repository candidate.
- Current recommendation: publishable as a private/test release candidate after replacing `CHANGE_ME` metadata and testing install from a real GitHub repository.

## Public Positioning

Home Assistant custom integration for FairyNest SP511E LED strip controllers.

This is a cloud-dependent integration. It is not local-only and does not emulate the controller's Aliyun IoT channel.

## Included Files

- Root metadata: `README.md`, `hacs.json`, `LICENSE`, `CHANGELOG.md`, `SECURITY.md`, `CONTRIBUTING.md`, `PUBLISHING.md`.
- Workflows: `.github/workflows/hacs.yml`, `.github/workflows/hassfest.yml`, `.github/workflows/tests.yml`.
- Component: `custom_components/fairynest_sp511e`.
- Assets: controller photo, integration icon/logo, redacted dashboard screenshots.
- Tests: `tests/test_fairynest_component_api.py`.

## Architecture

- Config flow logs in to the FairyNest cloud.
- Session SID/token are stored in Home Assistant config entry data and refreshed when authentication expires.
- Polling reads state from FairyNest `user/info`.
- Writes use mapped `SPLED.*` commands through `user/device/control`.
- No raw payload write service is exposed.

## Home Assistant Metadata

- `iot_class`: `cloud_polling`
- `config_flow`: `true`
- `integration_type`: `device`
- `codeowners`: placeholder must be replaced.
- `documentation`: placeholder GitHub URL must be replaced.
- `issue_tracker`: placeholder GitHub URL must be replaced.

## Privacy Risks

No account, password, session token, `hashKey`, `deviceCode`, `productKey`, LAN IP, private path, APK, capture, or Home Assistant `.storage` file should be embedded.

Diagnostics redact common credential and identifier keys.

## Testable Without Hardware

- Python syntax compilation.
- Static API/protocol helper tests.
- HACS metadata validation in GitHub Actions.
- Hassfest validation in GitHub Actions.
- Privacy string audit.

## Current Local Check Results

- `python -m compileall -q .\custom_components .\tests`: passed.
- `python -m unittest discover -s tests`: passed, 4 tests.
- Cache audit: no `__pycache__`, `*.pyc` or `*.pyo` left in the release ZIP.
- Manual privacy audit: no `secrets/`, `captures/`, APK, PCAP, logs, raw reverse artifacts, known account, password, HA token, or vendor password in the release ZIP.

## Residual Blockers Before Public Release

- Replace all `CHANGE_ME` placeholders.
- Set final copyright owner in `LICENSE`.
- Install from the real GitHub repository through HACS as a custom repository.
- Verify config flow and session refresh on a clean Home Assistant instance.
- Create release `v0.1.0`.

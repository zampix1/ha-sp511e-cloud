# SP511E Cloud Home Assistant Custom Component

Custom integration nativa per controller LED SP511E via cloud/app originale.

## Cosa sostituisce

Questo componente sostituisce il package YAML basato su `rest`, `rest_command`,
helper e template light. Non richiede il gateway Python sul PC per il runtime
normale.

## Entita

- `light.*`: strip SP511E con power, RGB, brightness ed effetti.
- `select.* Effect`: selezione diretta dei 24 effetti mappati.
- `number.*`: slider nativi per brightness, speed e music sensitivity.
- `button.*`: refresh, restore standard e all off.
- Sensori diagnostici:
  - Power
  - Effect
  - Brightness
  - Speed
  - Color Hex
  - Music Sensitivity
  - Device IP
  - SSID
  - Last Command

## Servizi

- `sp511e_cloud.set_effect`
- `sp511e_cloud.set_speed`
- `sp511e_cloud.set_music_sensitivity`
- `sp511e_cloud.restore_standard`
- `sp511e_cloud.all_off`
- `sp511e_cloud.refresh`

## Setup

1. Copiare questa directory in:

   ```text
   /config/custom_components/sp511e_cloud
   ```

2. Riavviare Home Assistant.
3. Andare in `Impostazioni > Dispositivi e servizi > Aggiungi integrazione`.
4. Cercare `SP511E Cloud`.
5. Inserire account, password, country code e selector `SP511E`.

Le credenziali vengono salvate da Home Assistant nel config entry storage,
non nei file del componente. Non committare mai `.storage` o dump di sessione.

## Migrazione dal package YAML

Durante il test lasciare attivo il vecchio package. Quando la custom integration
ha creato entita funzionanti:

1. aggiornare la dashboard verso la nuova `light.*`;
2. sostituire gli script YAML con servizi `sp511e_cloud.*`;
3. rinominare o disabilitare `/config/packages/sp511e_cloud_sala_pranzo.yaml`;
4. riavviare HA e verificare che non restino entita duplicate necessarie.

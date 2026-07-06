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
  - Connectivity
  - Cloud State
  - Last Command

## Servizi

- `fairynest_sp511e.set_effect`
- `fairynest_sp511e.set_speed`
- `fairynest_sp511e.set_music_sensitivity`
- `fairynest_sp511e.restore_standard`
- `fairynest_sp511e.all_off`
- `fairynest_sp511e.refresh`

## Setup

1. Copiare questa directory in:

   ```text
   /config/custom_components/fairynest_sp511e
   ```

2. Riavviare Home Assistant.
3. Andare in `Impostazioni > Dispositivi e servizi > Aggiungi integrazione`.
4. Cercare `SP511E Cloud`.
5. Inserire account, password, country code e selector `SP511E`.

Le credenziali vengono salvate da Home Assistant nel config entry storage,
non nei file del componente. Non committare mai `.storage` o dump di sessione.

Se la cloud restituisce `407 device is offline`, il comando viene registrato in
`sensor.* Last Command` con `success: false` e lo stato ottimistico non viene
applicato.

## Migrazione dal package YAML

Durante il test lasciare attivo il vecchio package. Quando la custom integration
ha creato entita funzionanti:

1. aggiornare la dashboard verso la nuova `light.*`;
2. sostituire gli script YAML con servizi `fairynest_sp511e.*`;
3. rinominare o disabilitare `/config/packages/fairynest_sp511e_sala_pranzo.yaml`;
4. riavviare HA e verificare che non restino entita duplicate necessarie.

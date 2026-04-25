# Zendure Readonly Integration

Custom Home Assistant integration for Zendure SolarFlow systems.

## Features
- Battery SOC
- Solar input
- Grid import/export
- Microinverter backfeed / backup power output
- Energy Dashboard compatible sensors

## Installation (HACS)
1. Add this repository in HACS --> Integrations.
2. Install "Zendure Readonly" (`https://github.com/CodeCasterNL/zendure-readonly`).
3. Restart Home Assistant.
4. Add "Zendure Readonly" integration via UI, configuring your (singular) battery.

## Requirements
- Home Assistant 2026+
- Zendure local API enabled (should be by default)

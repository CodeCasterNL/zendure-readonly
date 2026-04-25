from homeassistant.components.integration.sensor import IntegrationSensor
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


###
# Setup - registers all sensor entities, passing the coordinator for coordinated data retrieval.
###

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        BatterySOC(coordinator, entry),

        SolarInputPower(coordinator, entry),

        TotalImportPower(coordinator, entry),
        TotalExportPower(coordinator, entry),

        EPSOutputPower(coordinator, entry),
        EPSReverseInputPower(coordinator, entry),

        BatteryVoltage(coordinator, entry),
        BatteryTemperature(coordinator, entry),
    ])


# =========================
# Sensor base class
# =========================
class ZendureSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def available(self):
        return self.coordinator.data is not None

    @property
    def device_info(self):
        data = self.coordinator.data or {}

        sn = data.get("sn", self._entry.entry_id)

        return {
            "identifiers": {(DOMAIN, sn)},
            "name": f"Zendure {sn}",
            "manufacturer": "Zendure",
            "model": data.get("product", "SolarFlow"),
            "sw_version": data.get("version"),
        }

# =========================
# BATTERY
# =========================

class BatterySOC(ZendureSensor):
    _attr_unique_id = "zendure_soc"
    _attr_name = "Battery SOC"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data["properties"].get("electricLevel")


class BatteryVoltage(ZendureSensor):
    _attr_unique_id = "zendure_voltage"
    _attr_name = "Battery Voltage"
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data["properties"].get("BatVolt", 0) / 100


class BatteryTemperature(ZendureSensor):
    _attr_unique_id = "zendure_temp"
    _attr_name = "Battery Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data["properties"].get("hyperTmp", 0) / 100


# =========================
# SOLAR INPUT
# =========================

class SolarInputPower(ZendureSensor):
    _attr_unique_id = "zendure_solar_power"
    _attr_name = "Solar Input Power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None

        p = self.coordinator.data["properties"]

        return (
            p.get("solarPower1", 0)
            + p.get("solarPower2", 0)
            + p.get("solarPower3", 0)
            + p.get("solarPower4", 0)
        )


# =========================
# Input/Output
# =========================

class TotalImportPower(ZendureSensor):
    _attr_unique_id = "zendure_power_import"
    _attr_name = "Power Import"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        
        grid_power = self.coordinator.data["properties"].get("gridInputPower", 0)
        solar_power = self.coordinator.data["properties"].get("solarInputPower", 0)
        # minus chimney outputHomePower?
        return grid_power + solar_power

class TotalExportPower(ZendureSensor):
    _attr_unique_id = "zendure_power_export"
    _attr_name = "Power Export"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    
    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        
        home_power = self.coordinator.data["properties"].get("outputHomePower", 0)
        #pack_power = self.coordinator.data["properties"].get("outputPackPower", 0)
        
        return home_power # + pack_power

# =========================
# EPS OUTPUT (EMERGENCY POWER)
# =========================

class EPSOutputPower(ZendureSensor):
    _attr_unique_id = "zendure_eps_output"
    _attr_name = "EPS Output Power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None

        p = self.coordinator.data["properties"]

        if p.get("offGridState", 0) == 1:
            return p.get("gridOffPower", 0)

        return 0


# =========================
# EPS REVERSE INPUT (MICROINVERTERS)
# =========================

class EPSReverseInputPower(ZendureSensor):
    _attr_unique_id = "zendure_eps_reverse"
    _attr_name = "Microinverter Input (EPS Backfeed)"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None

        p = self.coordinator.data["properties"]

        if p.get("acCouplingState", 0) != 0:
            return p.get("gridOffPower", 0)

        return 0

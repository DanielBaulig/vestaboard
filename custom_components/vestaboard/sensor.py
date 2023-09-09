from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)

from .const import DOMAIN

class VestaboardLineEntity(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, line):
        super().__init__(coordinator)
        self.line = line

    @property
    def name(self):
        return f"Vestaboard Line {self.line}"

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data[self.line]
        self.async_write_ha_state()


async def async_setup_entry(hass, config, async_add_entities):
    async_add_entities(
        [VestaboardLineEntity(hass.data[DOMAIN][config.entry_id]['coordinator'], line) for line in range(6)]
    )

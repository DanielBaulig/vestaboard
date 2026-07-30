from homeassistant.components.text import TextEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

class VestaboardLineTextEntity(CoordinatorEntity, TextEntity):
    """Text entity for editing a single Vestaboard line."""
    
    _attr_has_entity_name = True

    def __init__(self, coordinator, line):
        """Initialize the text entity."""
        super().__init__(coordinator)
        self.line = line
        self._attr_unique_id = f"{coordinator.vestaboard.host}_line_{line}_text"
        self._attr_native_max = coordinator.columns
        self._attr_native_min = 0
        self._attr_mode = "text"

    @property
    def name(self):
        """Return the name of the entity."""
        return f"Line {self.line}"

    @property
    def native_value(self):
        """Return the current value."""
        if self.coordinator.data and len(self.coordinator.data) > self.line:
            # Return the current line content, stripped of trailing spaces
            return self.coordinator.data[self.line].rstrip()
        return ""

    async def async_set_value(self, value: str) -> None:
        """Set new text value and update the board."""
        # Get current lines from coordinator
        current_lines = list(self.coordinator.data) if self.coordinator.data else [''] * self.coordinator.rows
        
        # Update the specific line
        current_lines[self.line] = value
        
        # Write to the board
        result = await self.coordinator.vestaboard.write(current_lines)
        
        if result:
            # Request a refresh to update all entities
            await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


async def async_setup_entry(hass, config, async_add_entities):
    """Set up Vestaboard text entities."""
    coordinator = hass.data[DOMAIN][config.entry_id]['coordinator']
    
    # Create text entities for each line based on detected board dimensions
    async_add_entities(
        [VestaboardLineTextEntity(coordinator, line) for line in range(coordinator.rows)]
    )

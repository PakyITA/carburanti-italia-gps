import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Carburanti Italia GPS from a config entry."""
    
    # Inizializziamo il Coordinator correttamente
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER, # <--- Questo è quello che mancava o era None
        name="carburanti_italia_gps",
        update_method=async_update_data, # Funzione che scarica i dati
        update_interval=timedelta(minutes=30),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault("carburanti_italia_gps", {})[entry.entry_id] = coordinator
    
    # Carica la piattaforma sensor
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_update_data():
    """Funzione per recuperare i dati (da implementare o chiamare dal sensor)"""
    # Qui andrebbe la chiamata API al Mise
    _LOGGER.debug("Aggiornamento dati carburanti...")
    return {}

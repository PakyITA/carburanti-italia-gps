import logging
import requests
import voluptuous as VOL
from datetime import timedelta
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE, ATTR_ATTRIBUTION

_LOGGER = logging.getLogger(__name__)

CONF_RADIUS = "radius"
DEFAULT_NAME = "Carburante Italia"
SCAN_INTERVAL = timedelta(minutes=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    VOL.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    VOL.Required(CONF_LATITUDE): cv.latitude,
    VOL.Required(CONF_LONGITUDE): cv.longitude,
    VOL.Optional(CONF_RADIUS, default=5): cv.positive_int,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    lat = config.get(CONF_LATITUDE)
    lon = config.get(CONF_LONGITUDE)
    radius = config.get(CONF_RADIUS)
    
    add_entities([CarburantiSensor(name, lat, lon, radius)], True)

class CarburantiSensor(SensorEntity):
    def __init__(self, name, lat, lon, radius):
        self._name = name
        self._lat = lat
        self._lon = lon
        self._radius = radius
        self._state = None
        self._attributes = {}

    @property
    def name(self): return self._name

    @property
    def native_value(self): return self._state

    @property
    def extra_state_attributes(self): return self._attributes

    @property
    def unit_of_measurement(self): return "€/L"

    def update(self):
        # URL delle API dell'Osservaprezzi Carburanti (Mise)
        # Nota: L'integrazione originale punta a un endpoint che spesso cambia
        url = "https://carburanti.mise.gov.it/osp-app/search/area"
        payload = {
            "lat": self._lat,
            "lng": self._lon,
            "radius": self._radius
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data.get("array"):
                # Prendiamo il primo risultato (il più vicino/economico)
                best_price = data["array"][0]
                self._state = best_price.get("prezzo")
                self._attributes = {
                    "stazione": best_price.get("nome"),
                    "indirizzo": best_price.get("indirizzo"),
                    "carburante": best_price.get("carburante"),
                    "ultimo_aggiornamento": best_price.get("dtCom")
                }
        except Exception as e:
            _LOGGER.error("Errore durante l'aggiornamento dei prezzi: %s", e)

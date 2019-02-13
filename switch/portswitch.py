import logging
import voluptuous as vol

from homeassistant.components.switch import (SwitchDevice, PLATFORM_SCHEMA)
from homeassistant.const import (CONF_NAME, CONF_URL, CONF_PORT, CONF_USERNAME, CONF_PASSWORD, CONF_IP_ADDRESS)
from requests import session
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['beautifulsoup4==4.6.3']

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'portswitch'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_URL): cv.url,
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_PORT): cv.positive_int,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the PortSwitch."""
    url = config.get(CONF_URL)
    ip = config.get(CONF_IP_ADDRESS)
    port = config.get(CONF_PORT)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    name = config.get(CONF_NAME)

    switch = portswitch(name, url, ip, port, username, password)
    add_entities([switch])


class portswitch(SwitchDevice):
    """Representation of a switch that can open a port."""

    def __init__(self, name, url, ip, port, username, password):
        """Initialize the Port switch."""
        self._state = None
        self._name = name
        self._url = url
        self._ip = ip
        self._port = port
        self._username = username
        self._password = password
        self._payload_login = {
            'MR4LoginApply': 'Doorgaan',
            'loginUsername': self._username,
            'loginPassword': self._password,
        }
        self._payload_select_port = {
            'PortForwardingCreateRemove': '0',
            'PortForwardingTable': self._port,
        }
        self._payload_port_state = {
            'PortForwardingApply': '2',
            'PortForwardingCreateRemove': '0',
            'PortForwardingDesc': 'port_' + str(self._port),
            'PortForwardingExtIp': '0.0.0.0',
            'PortForwardingExtStartPort': self._port,
            'PortForwardingLocalEndPort': self._port,
            'PortForwardingLocalIp': self._ip,
            'PortForwardingLocalStartPort': self._port,
            'PortForwardingProtocol': '4',
            'PortForwardingTable': '0',
        }
        #self.update()

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    #@property
    #def should_poll(self):
    #    """Polling is needed."""
    #    return False

    def turn_on(self, **kwargs):
        try:
            """Turn the device on."""
            self.turn_on_off(1)

        except ():
            _LOGGER.error("Can't open port %s", str(self._port))
        
        #self.update()

    def turn_off(self, **kwargs):
        try:
            """Turn the device off."""
            self.turn_on_off(0)

        except ():
            _LOGGER.error("Can't close port %s", str(self._port))

        #self.update()

    def update(self):
        self._state = False
        try:
            """Get port state"""
            with session() as c:
                c.post(self._url + "/goform/loginMR4", data=self._payload_login)
                response = c.get(self._url + "/RgForwarding.asp")
                c.get(self._url + "/logout.asp")

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('div', attrs={'class':'table_data table_data12'})
            rows = table.find_all('tr')
            for row in rows:
                cells = row.findAll("td")
                if len(cells) == 11:
                    row_ip = cells[0].find(text=True)
                    row_port = cells[1].find(text=True)
                    row_status = cells[8].find(text=True)
                    if row_ip == self._ip and row_port == str(self._port):
                        if row_status == 'Yes':
                            self._state = True
                        continue

        except ():
            _LOGGER.error("Unable to receive port state")

    def turn_on_off(self, state):
        self._payload_port_state['PortForwardingEnabled'] = state
        with session() as c:
            c.post(self._url + "/goform/loginMR4", data=self._payload_login)
            c.post(self._url + "/goform/RgForwarding", data=self._payload_select_port)
            c.post(self._url + "/goform/RgForwarding", data=self._payload_port_state)
            c.get(self._url + "/logout.asp")
# Home-assistant portswitch for ubee evw321b ziggo modem

## About


## Installation
Add the 'switch' folder with it's content into your custom_components folder `/config/custom_components` in home-assistant.

## Configuration
See example for configuring a switch for port 80 and a switch for port 443
Example:
```yaml
switch:
  - platform: portswitch
    name: Port 80
    url: http://10.0.0.1 (Modem url)
    ip_address: '10.0.0.10' (Ip address to forward to) 
    port: 80
    username: (modem username)
    password: (modem password)

  - platform: portswitch
    name: Port 443
    url: http://10.0.0.1
    ip_address: '10.0.0.10'
    port: 443
    username: (modem username)
    password: (modem password)
```

## Known issues

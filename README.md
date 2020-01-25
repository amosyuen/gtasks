[![CodeFactor](https://www.codefactor.io/repository/github/blueblueblob/gtasks/badge)](https://www.codefactor.io/repository/github/blueblueblob/gtasks)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)


## Before installation
Create a create a credentials.json from [Google API](https://console.developers.google.com/apis/credentials)

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `gtasks`.
4. Download _all_ the files from the `custom_components/gtasks/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Upload your credentials.json file as configured in your configuration.yaml
7. Restart Home Assistant
8. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Google Tasks"
9. Copy paste authentication url in your browser (don't need to be on host)
10. Authenticate and copy paste the result code in HA to finish integration.

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/gtasks/.translations/en.json
custom_components/gtasks/__init__.py
custom_components/gtasks/binary_sensor.py
custom_components/gtasks/config_flow.py
custom_components/gtasks/const.py
custom_components/gtasks/manifest.json
custom_components/gtasks/sensor.py
```

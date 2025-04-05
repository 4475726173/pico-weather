This [MicroPython](https://micropython.org/) program runs on the
[**Raspberry Pi Pico W**](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) microcontroller and collects
environmental data, such as indoor and outdoor temperature, humidity, atmospheric
pressure, and weather forecasts for the next day. The data is displayed on an OLED screen.

- The [DS18B20](https://www.farnell.com/datasheets/2345098.pdf) 1-wire digital thermometer measures the outdoor temperature.
- The [BME280](https://www.alldatasheet.com/datasheet-pdf/view/1132060/BOSCH/BME280.html) sensor measures indoor temperature, humidity, and atmospheric pressure.
- Weather forecast data is fetched from [Deutscher Wetterdienst](https://www.dwd.de/DE/Home/home_node.html), a German weather service.
- Information is displayed using the [SSD1306](https://www.alldatasheet.com/datasheet-pdf/pdf/1425553/ETC/SSD1306.html) chip, with the device driver and the [Writer](https://github.com/peterhinch/micropython-font-to-py/tree/master/writer) for text rendering.
- The [Agave](https://github.com/blobject/agave) font is used for displaying information.
- The Pico’s onboard 2.4GHz Wi-Fi is used for connectivity.
- Credentials are stored in text file containing two lines: the SSID and password.

The program continuously updates every 10 minutes for environmental data
and every hour for the weather forecast. The main loop is wrapped in `try/except`
blocks to handle unexpected errors without stopping the program, ensuring it
continues running even if there are issues with Wi-Fi, NTP, or sensors.
The screen will display as much info as possible based on the available data.

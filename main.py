import gc
import socket
import struct
import sys

import ds18x20
import framebuf
import machine
import network
import onewire
import rp2
import urequests
import utime
from machine import I2C, Pin, SoftI2C
from picozero import pico_led

import agave
import bme280
import smallfont
import ssd1306
import writer
from ssd1306 import SSD1306_I2C

WIDTH = 128
HEIGHT = 64

ds_pin = machine.Pin(22)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
i2c = SoftI2C(scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)
bme = bme280.BME280(i2c=I2C(0, sda=Pin(16), scl=Pin(17), freq=399361, timeout=500000))
roms = ds_sensor.scan()

font_writer = writer.Writer(oled, smallfont)


def display_logo():
    logo_data = load_bitmap("logo.pbm")
    display_bitmap(logo_data)
    gc.collect()
    utime.sleep(15)


def get_current_date():
    t = utime.localtime()
    date_str = "{:04d}.{:02d}.{:02d}".format(t[0], t[1], t[2])
    return date_str


weather_codes = {
    0: {"image": "sun.pbm"},
    1: {"image": "sun.pbm"},
    2: {"image": "clouds.pbm"},
    3: {"image": "overcast.pbm"},
    45: {"image": "fog.pbm"},
    48: {"image": "fog.pbm"},
    51: {"image": "drizzle.pbm"},
    53: {"image": "drizzle.pbm"},
    55: {"image": "drizzle.pbm"},
    56: {"image": "snow.pbm"},
    57: {"image": "snow.pbm"},
    61: {"image": "drizzle.pbm"},
    63: {"image": "drizzle.pbm"},
    65: {"image": "rain.pbm"},
    66: {"image": "rain.pbm"},
    67: {"image": "rain.pbm"},
    71: {"image": "snow.pbm"},
    73: {"image": "snow.pbm"},
    75: {"image": "snow.pbm"},
    77: {"image": "drizzle.pbm"},
    80: {"image": "drizzle.pbm"},
    81: {"image": "drizzle.pbm"},
    82: {"image": "showers-violent.pbm"},
    85: {"image": "snow.pbm"},
    86: {"image": "snow.pbm"},
    95: {"image": "showers-violent.pbm"},
    96: {"image": "showers-violent.pbm"},
    99: {"image": "showers-violent.pbm"},
}


def read_ds18x20_temperature():
    try:
        ds_sensor.convert_temp()
        utime.sleep_ms(750)
        for rom in roms:
            temp_out = ds_sensor.read_temp(rom)
            rounded_value = round(float(temp_out))
            temp_out = str(rounded_value) + "C"
            return temp_out
    except Exception as e:
        print(f"Error reading DS18x20 temperature: {e}")
        return "Error"


def read_bme280_temperature():
    try:
        temp, _, _ = bme.values
        utime.sleep_ms(750)
        tvalue = temp[:-1]
        rounded_value = round(float(tvalue))
        temp_in = str(rounded_value) + "C"
        return temp_in
    except Exception as e:
        print(f"Error reading BME280 temperature: {e}")
        return "Error"


def read_bme280_humidity():
    try:
        _, _, hum = bme.values
        utime.sleep_ms(750)
        hvalue = hum[:-1]
        rounded_value = round(float(hvalue))
        humidity = str(rounded_value) + "%"
        return humidity
    except Exception as e:
        print(f"Error reading BME280 humidity: {e}")
        return "Humidity Error"


def read_bme280_pressure():
    try:
        _, pressure_hPa, _ = bme.values
        utime.sleep_ms(750)
        conversion_factor = 0.7500616827
        pres_value = pressure_hPa[:-3]
        numeric_value = float(pres_value)
        corrected_value = numeric_value + 47
        rounded_value = round(corrected_value, 0)
        pressure_mmHg = round(rounded_value * conversion_factor, 2)
        pressure = str(int(pressure_mmHg)) + "mm"
        return pressure
    except Exception as e:
        print(f"Error reading BME280 pressure: {e}")
        return "Pressure Error"


def load_temp_out_bitmap():
    try:
        with open("temp_out.pbm", "rb") as f:
            f.readline()
            f.readline()
            f.readline()
            temp_out_icon = bytearray(f.read())
        return temp_out_icon
    except Exception as e:
        print(f"Error loading bitmap: {e}")
        return None


def load_temp_in_bitmap():
    try:
        with open("temp_in.pbm", "rb") as f:
            f.readline()
            f.readline()
            f.readline()
            temp_in_icon = bytearray(f.read())
        return temp_in_icon
    except Exception as e:
        print(f"Error loading bitmap: {e}")
        return None


def load_hum_bitmap():
    try:
        with open("hum.pbm", "rb") as f:
            f.readline()
            f.readline()
            f.readline()
            hum_icon = bytearray(f.read())
        return hum_icon
    except Exception as e:
        print(f"Error loading bitmap: {e}")
        return None


def load_pres_bitmap():
    try:
        with open("pres.pbm", "rb") as f:
            f.readline()
            f.readline()
            f.readline()
            pres_icon = bytearray(f.read())
        return pres_icon
    except Exception as e:
        print(f"Error loading bitmap: {e}")
        return None


def display_temp_in(temp_in_icon, temperature):
    temperature = read_bme280_temperature()
    oled.fill(0)
    fbuf = framebuf.FrameBuffer(temp_in_icon, 25, 25, framebuf.MONO_HLSB)
    start_x = (128 - 25) // 2
    start_y = (64 - 60) // 2
    oled.blit(fbuf, start_x, start_y)
    font_writer = writer.Writer(oled, agave)
    font_writer.set_textpos(35, 30)
    font_writer.printstring(str(temperature))
    oled.show()
    gc.collect()
    utime.sleep(5)


def display_temp_out(temp_out_icon, temperature):
    temperature = read_ds18x20_temperature()
    oled.fill(0)
    fbuf = framebuf.FrameBuffer(temp_out_icon, 25, 25, framebuf.MONO_HLSB)
    start_x = (128 - 25) // 2
    start_y = (64 - 60) // 2
    oled.blit(fbuf, start_x, start_y)
    font_writer = writer.Writer(oled, agave)
    font_writer.set_textpos(35, 30)
    font_writer.printstring(str(temperature))
    oled.show()
    gc.collect()
    utime.sleep(5)


def display_hum(hum_icon, humidity):
    humidity = read_bme280_humidity()
    oled.fill(0)
    fbuf = framebuf.FrameBuffer(hum_icon, 25, 25, framebuf.MONO_HLSB)
    start_x = (128 - 25) // 2
    start_y = (64 - 60) // 2
    oled.blit(fbuf, start_x, start_y)
    font_writer = writer.Writer(oled, agave)
    font_writer.set_textpos(35, 30)
    font_writer.printstring(str(humidity))
    oled.show()
    gc.collect()
    utime.sleep(5)


def display_pres(pres_icon, pressure):
    humidity = read_bme280_pressure()
    oled.fill(0)
    fbuf = framebuf.FrameBuffer(pres_icon, 25, 25, framebuf.MONO_HLSB)
    start_x = (128 - 25) // 2
    start_y = (64 - 60) // 2
    oled.blit(fbuf, start_x, start_y)
    font_writer = writer.Writer(oled, agave)
    font_writer.set_textpos(17, 30)
    font_writer.printstring(str(pressure))
    oled.show()
    gc.collect()
    utime.sleep(5)


def display_weather_forecast(weather_data):
    if weather_data:
        forecast_codes = weather_data["daily"]["weather_code"]

        for code in forecast_codes:
            weather_image = weather_codes.get(code, {}).get("image")
            if weather_image:
                bitmap_data = load_bitmap(weather_image)
                display_forecast(bitmap_data)
                gc.collect()
                utime.sleep(5)


def load_bitmap(bitmap_file):
    try:
        with open(bitmap_file, "rb") as f:
            f.readline()
            f.readline()
            f.readline()
            data = bytearray(f.read())
        return data
    except Exception as e:
        print(f"Error loading bitmap {bitmap_file}: {e}")
        return None


def display_bitmap(bitmap_data):
    if bitmap_data is None:
        print("Error: No bitmap data to display.")
        return

    fbuf = framebuf.FrameBuffer(bitmap_data, 63, 63, framebuf.MONO_HLSB)
    oled.fill(0)
    start_x = (128 - 63) // 2
    start_y = (64 - 63) // 2
    oled.blit(fbuf, start_x, start_y)
    oled.show()
    gc.collect()


def display_forecast(bitmap_data):
    if bitmap_data is None:
        print("Error: No bitmap data to display.")
        return

    fbuf = framebuf.FrameBuffer(bitmap_data, 55, 55, framebuf.MONO_HLSB)
    oled.fill(0)
    font_writer = writer.Writer(oled, smallfont)
    font_writer.set_textpos(39, 1)
    font_writer.printstring(str("3ABTPA"))
    start_x = (128 - 55) // 2
    start_y = (64 - 39) // 2
    oled.blit(fbuf, start_x, start_y)
    oled.show()
    gc.collect()


def read_credentials():
    try:
        with open("credentials.txt", "r") as f:
            lines = f.readlines()

            if len(lines) < 2:
                print("Error: File does not contain both SSID and PASSWORD.")
                return None, None

            ssid = lines[0].strip().split("=")[1] if "=" in lines[0] else ""
            password = lines[1].strip().split("=")[1] if "=" in lines[1] else ""

            if ssid and password:
                return ssid, password
            else:
                print("Error: Invalid SSID or password.")
                return None, None
    except Exception as e:
        print(f"Error reading credentials: {e}")
        return None, None


def connect_to_wifi():
    ssid, password = read_credentials()

    if ssid is None or password is None:
        print("Error: Cannot retrieve credentials, proceeding without Wi-Fi.")
        return None

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    attempt = 0
    while not wlan.isconnected():
        print(f"Attempt {attempt}: Connection status: {wlan.status()}")
        if attempt > 30:
            print(
                "Failed to connect to Wi-Fi after multiple attempts. Continuing without Wi-Fi."
            )
            return None
        attempt += 1
        print("Waiting for Wi-Fi connection...")
        pico_led.on()
        utime.sleep(0.3)
        pico_led.off()
        utime.sleep(0.3)

    ip = wlan.ifconfig()[0]
    print(f"Connected on {ip}")
    pico_led.on()
    return ip


def get_ntp_time(timezone_offset_seconds):
    NTP_SERVER = "time.apple.com"
    addr = socket.getaddrinfo(NTP_SERVER, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)

    try:
        s.connect(addr)
        s.send(b"\x1b" + 47 * b"\x00")
        data = s.recv(48)
        if data:
            ntp_time = struct.unpack("!12I", data)[10]
            utc_time = ntp_time - 2208988800
            kyiv_time = utc_time + timezone_offset_seconds
            t = utime.localtime(kyiv_time)
            return t
        else:
            print("NTP request timed out or no response")
            return None
    except OSError as e:
        print(f"Error getting NTP time: {e}")
        return None
    finally:
        s.close()


def display_clock(t):
    oled.fill(0)
    font_writer = writer.Writer(oled, agave)
    font_writer.set_textpos(15, 25)
    time_str = "{:02d}:{:02d}".format(t[3], t[4])
    font_writer.printstring(time_str)
    oled.show()


def encode_params(params):
    return "&".join([f"{key}={value}" for key, value in params.items()])


def get_weather_forecast():
    params = {
        "timezone": "Europe/Kyiv",
        "latitude": "49.84443372912856",
        "longitude": "24.026222745102906",
        "daily": "weather_code",
        "forecast_days": "1",
    }

    query_string = encode_params(params)
    url = f"https://api.open-meteo.com/v1/dwd-icon?{query_string}"

    try:
        response = urequests.get(url)
        weather_data = response.json()
        response.close()
        return weather_data
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None


def main():
    weather_data = None
    last_forecast_check = 0
    forecast_day = None
    display_logo()

    while True:
        try:
            temperature_out = read_ds18x20_temperature()
            temperature_in = read_bme280_temperature()
            humidity = read_bme280_humidity()
            pressure = read_bme280_pressure()

            date_str = get_current_date()
            current_day = date_str[:10]

            temp_out_icon = load_temp_out_bitmap()
            display_temp_out(temp_out_icon, temperature_out)
            utime.sleep(10)

            temp_in_icon = load_temp_in_bitmap()
            display_temp_in(temp_in_icon, temperature_in)
            utime.sleep(10)

            hum_icon = load_hum_bitmap()
            display_hum(hum_icon, humidity)
            utime.sleep(10)

            pres_icon = load_pres_bitmap()
            display_pres(pres_icon, pressure)
            utime.sleep(10)

            if utime.time() - last_forecast_check >= 3600:
                last_forecast_check = utime.time()

                ip = connect_to_wifi()
                if ip:
                    display_bitmap(load_bitmap("wi-fi-connected.pbm"))
                    gc.collect()
                    utime.sleep(3)
                    display_bitmap(load_bitmap("forecast.pbm"))
                    gc.collect()
                    new_weather_data = get_weather_forecast()
                    if new_weather_data:
                        weather_data = new_weather_data
                        display_weather_forecast(weather_data)
                        forecast_day = current_day
                    else:
                        print("No forecast data received.")
                        display_bitmap(load_bitmap("wi-fi-disconnected.pbm"))
                        gc.collect()
                        utime.sleep(10)
                else:
                    display_bitmap(load_bitmap("wi-fi-disconnected.pbm"))
                    gc.collect()
                    utime.sleep(10)

            if weather_data and forecast_day == current_day:
                display_weather_forecast(weather_data)
                utime.sleep(10)

            kyiv_time_offset = 2 * 3600
            t = get_ntp_time(kyiv_time_offset)
            if t:
                display_clock(t)
            else:
                print("Could not get time. Displaying last known time.")
                display_clock([2025, 2, 23, 12, 0, 0])

            gc.collect()
            utime.sleep(60)

        except Exception as e:
            print(f"Unexpected error: {e}")
            utime.sleep(5)


main()

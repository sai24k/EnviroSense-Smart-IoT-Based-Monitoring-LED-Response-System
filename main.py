import machine
import time
import network
import urequests as requests
import dht

# --- Sensor & LED Pin Configurations ---
gas_sensor = machine.ADC(machine.Pin(34))  # Adjust ADC pin based on your board
soil_sensor = machine.ADC(machine.Pin(35))
led_red = machine.Pin(5, machine.Pin.OUT)
led_green = machine.Pin(18, machine.Pin.OUT)
led_blue = machine.Pin(19, machine.Pin.OUT)
dht_sensor = dht.DHT11(machine.Pin(23))  # Optional Temp/Humidity sensor

# --- WiFi Configuration ---
SSID = 'Your_WiFi_SSID'
PASSWORD = 'Your_WiFi_Password'

# --- Connect to WiFi ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    print("Connected to WiFi")
    print(wlan.ifconfig())

# --- Read Sensors ---
def read_sensors():
    gas_val = gas_sensor.read()
    soil_val = soil_sensor.read()
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
    except Exception as e:
        temp = None
        hum = None
    return gas_val, soil_val, temp, hum

# --- Control LEDs based on thresholds ---
def control_leds(gas, soil):
    if gas > 600:
        led_red.value(1)
        led_green.value(0)
        led_blue.value(0)
    elif soil < 300:
        led_red.value(0)
        led_green.value(0)
        led_blue.value(1)
    else:
        led_red.value(0)
        led_green.value(1)
        led_blue.value(0)

# --- Send Data to Web Interface (optional ThingSpeak or custom server) ---
def send_data_to_server(gas, soil, temp, hum):
    try:
        url = "https://api.thingspeak.com/update?api_key=YOUR_API_KEY"
        payload = {
            "field1": gas,
            "field2": soil,
            "field3": temp,
            "field4": hum
        }
        full_url = url + "&" + "&".join([f"{k}={v}" for k, v in payload.items() if v is not None])
        response = requests.get(full_url)
        print("Data sent:", response.text)
    except Exception as e:
        print("Failed to send data:", e)

# --- Main Loop ---
connect_wifi()
while True:
    gas, soil, temp, hum = read_sensors()
    print("Gas:", gas, "Soil:", soil, "Temp:", temp, "Humidity:", hum)
    control_leds(gas, soil)
    send_data_to_server(gas, soil, temp, hum)
    time.sleep(10)

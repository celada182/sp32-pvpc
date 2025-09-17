import network
import urequests
import ntptime
import time
from machine import Pin

led_red = Pin(12, Pin.OUT)
led_orange = Pin(14, Pin.OUT)
led_yellow = Pin(27, Pin.OUT)
led_green = Pin(26, Pin.OUT)
led_blue = Pin(25, Pin.OUT)

led_red.value(1)
time.sleep(0.5)
led_red.value(0)
led_orange.value(1)
time.sleep(0.5)
led_orange.value(0)
led_yellow.value(1)
time.sleep(0.5)
led_yellow.value(0)
led_green.value(1)
time.sleep(0.5)
led_green.value(0)
led_blue.value(1)
time.sleep(0.5)
led_blue.value(0)

led_red_next = Pin(18, Pin.OUT)
led_orange_next = Pin(5, Pin.OUT)
led_yellow_next = Pin(17, Pin.OUT)
led_green_next = Pin(16, Pin.OUT)
led_blue_next = Pin(4, Pin.OUT)

led_red_next.value(1)
time.sleep(0.5)
led_red_next.value(0)
led_orange_next.value(1)
time.sleep(0.5)
led_orange_next.value(0)
led_yellow_next.value(1)
time.sleep(0.5)
led_yellow_next.value(0)
led_green_next.value(1)
time.sleep(0.5)
led_green_next.value(0)
led_blue_next.value(1)
time.sleep(0.5)
led_blue_next.value(0)

sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
  print("Connecting to WiFi: ", end="")
  sta_if.active(True)
  sta_if.connect('Wokwi-GUEST', '')
  while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)
  print(" Connected!")

try:
  ntptime.settime()
  print("Local time synchronization completed")
except:
  print("Error syncing time")

localtime = time.localtime()
today = "{}-{}-{}".format(localtime[0], localtime[1], localtime[2])
print("Today's date:", today)

print("Fetching ESIOS data: ", end="")
url = "https://api.esios.ree.es/archives/70/download_json?locale=es&date=" + today
resp = urequests.get(url)
data = resp.json()
print("Data fetched!") 

current_hour = localtime[3] + 2  # Adjust for timezone if necessary
print(f"Current hour: {current_hour}h")
current_price = None
next_price = None
prices = []

for item in data["PVPC"]:
  hour = int(item["Hora"].split("-")[0])
  price = float(item["PCB"].replace(",", "."))
  prices.append(price)
  if hour == current_hour:
    current_price = price
    print(f"Current hour price: {price} €/MWh")
  if hour == current_hour + 1:
    next_price = price
    print(f"Next hour price: {price} €/MWh")

sorted_prices = sorted(prices)
blue = sorted_prices[0]
print(f"Today's minimum {blue} €/MWh ------ BLUE")
green = sorted_prices[5]
print(f"Today's next minimum {sorted_prices[5]} €/MWh ------ GREEN")
yellow = sorted_prices[11]
print(f"Today's mid {sorted_prices[11]} €/MWh ------ YELLOW")
orange = sorted_prices[17]
print(f"Today's previous maximum {sorted_prices[17]} €/MWh ------ ORANGE")
red = sorted_prices[23]
print(f"Today's maximum {sorted_prices[23]} €/MWh ------ RED")

def price_color(price):
  if price == red:
    return "RED"
  elif red > price >= orange:
    return "ORANGE"
  elif orange > price >= yellow:
    return "YELLOW"
  elif yellow > price >= green:
    return "GREEN"
  else:
    return "BLUE"
  
def turn_on_led(color):
  if color == "RED":
    led_red.value(1)
  elif color == "ORANGE":
    led_orange.value(1)
  elif color == "YELLOW":
    led_yellow.value(1)
  elif color == "GREEN":
    led_green.value(1)
  elif color == "BLUE":
    led_blue.value(1)

def turn_on_next_led(color):
  if color == "RED":
    led_red_next.value(1)
  elif color == "ORANGE":
    led_orange_next.value(1)
  elif color == "YELLOW":
    led_yellow_next.value(1)
  elif color == "GREEN":
    led_green_next.value(1)
  elif color == "BLUE":
    led_blue_next.value(1)
  
current_color = price_color(current_price)
turn_on_led(current_color)
print(f"Current price color: {current_color}")
next_color = price_color(next_price)
turn_on_next_led(next_color)
print(f"Next price color: {next_color}")
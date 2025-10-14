import wifimgr
from time import sleep
import machine
import urequests
import time

try:
  import usocket as socket
except:
  import socket

led = machine.Pin(2, machine.Pin.OUT)

wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D

# Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
print("ESP OK")

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

current_color = price_color(current_price)
print(f"Current price color: {current_color}")
next_color = price_color(next_price)
print(f"Next price color: {next_color}")

def web_page():
  if led.value() == 1:
    gpio_state="ON"
  else:
    gpio_state="OFF"
  
  html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
  <p>GPIO state: <strong>""" + gpio_state + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
  <p><a href="/?led=off"><button class="button button2">OFF</button></a></p></body></html>"""
  return html
  
try:
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(('', 80))
  s.listen(5)
except OSError as e:
  machine.reset()

while True:
  try:
    if gc.mem_free() < 102000:
      gc.collect()
    conn, addr = s.accept()
    conn.settimeout(3.0)
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = str(request)
    print('Content = %s' % request)
    led_on = request.find('/?led=on')
    led_off = request.find('/?led=off')
    if led_on == 6:
      print('LED ON')
      led.value(1)
    if led_off == 6:
      print('LED OFF')
      led.value(0)
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')

import wifimgr
from time import sleep
import machine
import urequests
import time
from machine import Pin, SPI
import gc9a01
import random

#from truetype import NotoSans_32 as font
from bitmap import vga1_8x16 as small_font
from bitmap import vga1_16x32 as font

try:
  import usocket as socket
except:
  import socket

# Screen
tft = gc9a01.GC9A01(
    SPI(2, baudrate=80000000, polarity=0, sck=Pin(10), mosi=Pin(11)),
    240,
    240,
    reset=Pin(12, Pin.OUT),
    cs=Pin(9, Pin.OUT),
    dc=Pin(8, Pin.OUT),
    backlight=Pin(40, Pin.OUT),
    rotation=0,
    buffer_size=16*32*2)

tft.init()
tft.fill(gc9a01.BLACK)

led = machine.Pin(2, machine.Pin.OUT)

tft.text(small_font, "Configuracion", 60, 20, gc9a01.WHITE)
tft.text(small_font, "Connectar red Wi-Fi:", 30, 40, gc9a01.WHITE)
tft.text(font, "WifiManager", 30, 60, gc9a01.WHITE)
tft.text(small_font, "Abrir en navegador web:", 30, 100, gc9a01.WHITE)
tft.text(font, "192.168.4.1", 30, 120, gc9a01.WHITE)
tft.text(small_font, "Selccionar red Wi-Fi", 30, 160, gc9a01.WHITE)
tft.text(small_font, "Introducir contrasena", 30, 180, gc9a01.WHITE)


wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D

# Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
print("Internet Connection OK")
tft.fill(gc9a01.BLACK)
tft.text(font, "Connectado", 30, 60, gc9a01.WHITE)
tft.fill(gc9a01.BLACK)

previous_hour = -1

def center(font, s, row, color=gc9a01.WHITE):
        screen = tft.width()                     # get screen width
        width = tft.write_len(font, s)           # get the width of the string
        if width and width < screen:             # if the string < display
            col = tft.width() // 2 - width // 2  # find the column to center
        else:                                    # otherwise
            col = 0                              # left justify

        tft.write(font, s, col, row, color)      # and write the string

def fetch_data():
    max_attempts = 5
    attempts = 0
    response = None
    while attempts < max_attempts and response is None :
        attempts = attempts + 1
        print("Fetching ESIOS data: ")
        url = "https://api.esios.ree.es/archives/70/download_json?locale=es&date=" + today
        try:
            resp = urequests.get(url)
            return resp.json()
        except:
            print("Error fetching")

def get_data():
    data = fetch_data()

    current_price = None
    next_price = None
    prices = []

    for item in data["PVPC"]:
      hour = int(item["Hora"].split("-")[0])
      price = float(item["PCB"].replace(",", "."))
      # Convert price MWh to KWh
      price = price / 1000
      prices.append(price)
      if hour == current_hour:
        current_price = price
        print(f"Current hour price: {price} €/KWh")
      if hour == current_hour + 1:
        next_price = price
        print(f"Next hour price: {price} €/KWh")

    sorted_prices = sorted(prices)
    blue = sorted_prices[0]
    print(f"Today's minimum {blue} €/KWh ------ BLUE")
    green = sorted_prices[5]
    print(f"Today's next minimum {green} €/KWh ------ GREEN")
    yellow = sorted_prices[11]
    print(f"Today's mid {yellow} €/KWh ------ YELLOW")
    orange = sorted_prices[17]
    print(f"Today's previous maximum {orange} €/KWh ------ ORANGE")
    red = sorted_prices[23]
    print(f"Today's maximum {red} €/KWh ------ RED")
    
    def price_color(price):
      if price == red:
        return gc9a01.RED
      elif red > price >= orange:
        return gc9a01.color565(255,165,0)
      elif orange > price >= yellow:
        return gc9a01.YELLOW
      elif yellow > price >= green:
        return gc9a01.GREEN
      else:
        return gc9a01.BLUE

    current_color = price_color(current_price)
    next_color = price_color(next_price)
    
    tft.fill_rect(0, 50, 120, 140, current_color)
    tft.text(small_font, "Actual", 20, 60, gc9a01.BLACK, current_color)
    tft.text(small_font, f"{current_price}", 20, 150, gc9a01.BLACK, current_color)
    tft.text(small_font, "EUR/KWh", 20, 170, gc9a01.BLACK, current_color)
    
    tft.fill_rect(120, 50, 120, 140, next_color)
    tft.text(small_font, "Siguiente", 140, 60, gc9a01.BLACK, next_color)
    tft.text(small_font, f"{next_price}", 140, 150, gc9a01.BLACK, next_color)
    tft.text(small_font, "EUR/KWh", 140, 170, gc9a01.BLACK, next_color)
    
    # Legend
    tft.text(small_font, "Min", 45, 200, gc9a01.WHITE)
    tft.fill_rect(80, 205, 10, 10, gc9a01.BLUE)
    tft.fill_rect(95, 205, 10, 10, gc9a01.GREEN)
    tft.fill_rect(110, 205, 10, 10, gc9a01.YELLOW)
    tft.fill_rect(125, 205, 10, 10, gc9a01.color565(255,165,0))
    tft.fill_rect(140, 205, 10, 10, gc9a01.RED)
    tft.text(small_font, "Max", 160, 200, gc9a01.WHITE)


# Main
while True:
    localtime = time.localtime()
    today = "{}-{}-{}".format(localtime[0], localtime[1], localtime[2])
    current_hour = localtime[3] # Adjust for timezone if necessary
    if (current_hour != previous_hour):
        tft.fill(gc9a01.BLACK)
        print("Today's date:", today)
        tft.text(small_font, f"{today} {current_hour}h", 60, 30, gc9a01.WHITE)
        previous_hour = current_hour
        print(f"Current hour: {current_hour}h")
        get_data()

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


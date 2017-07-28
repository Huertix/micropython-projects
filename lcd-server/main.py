import machine
import socket

from time import sleep_ms, ticks_ms
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

# pins = [machine.Pin(i, machine.Pin.IN) for i in (0, 2, 4, 5, 12, 13, 14, 15)]

# html = """<!DOCTYPE html>
# <html>
#     <head> <title>ESP8266 Pins</title> </head>
#     <body> <h1>ESP8266 Pins</h1>
#         <table border="1"> <tr><th>Pin</th><th>Value</th></tr> %s </table>
#     </body>
# </html>
# """

html2 = """<!DOCTYPE html>
<html>
    <head> <title>ESP8266</title> </head>
    <body> <h1>ESP8266</h1>
        <div> path is: {} </div> 
    </body>
</html>
"""

def lcd_display(msg):
    global lcd
    lcd.clear()
    lcd.backlight_on()
    lcd.display_on()
    lcd.putstr("Request path\n{}".format(msg))


def parse_request(text):
    global p2
    if text != '':
        request_line = text.split("\r\n")[0]
        request_line = request_line.split()
        print(request_line)
        # Break down the request line into components
        (request_method,  # GET
         path,            # /hello
         request_version  # HTTP/1.1
         ) = request_line
        print("Method:", request_method)
        print("Path:", path)
        print("Version:", request_version)

        path = path.strip('/')

        if path == 'toggle':
            p2.value(not p2.value())

        elif path == 'on':
            p2.value(0)
        
        elif path == 'off':
            p2.value(1)

        elif path == 'favicon.ico':
            return 
            
        lcd_display(path)
        return path


def build_response(content):
    return html2.format(content)


def init():
    global p2
    global lcd
    p2 = Pin(2, Pin.OUT)
    p2.value(1)
    i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.clear()
    lcd.display_off()
    lcd.backlight_off()

def main():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print('listening on', addr)

    while True:
        cl, addr = s.accept()
        print('client connected from', addr)

        cl_file = cl.makefile('rwb', 0)

        # while True:
        #     line = cl_file.readline()
        #     if not line or line == b'\r\n':
        #         break
        # rows = ['<tr><td>%s</td><td>%d</td></tr>' % (str(p), p.value()) for p in pins]
        # response = html % '\n'.join(rows)
        content = parse_request(cl.recv(4096).decode('utf-8'))
        response = build_response(content)
        

        cl.send(response)
        cl.close()


init()
main()
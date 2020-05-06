import json
import falcon
import RPi.GPIO as GPIO
from time import sleep
import json
import ADC0832
import Adafruit_DHT

# Excitation Voltage for sensors
pin = 15

# initialize GPIO
GPIO.setwarnings(False)

# Excitation Voltage
def output_fromGPIO(pin, output):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, output)
    sleep(0.1)

def get_temperature():
    try:
        output_fromGPIO(pin,True)
        _, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 4)
        return temperature
    finally:
        output_fromGPIO(pin,False)

def get_humidity():
    try:
        output_fromGPIO(pin,True)
        humidity, _ = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 4)
        return humidity
    finally:
        output_fromGPIO(pin,False)


def get_moisture():
    try:
        ADC0832.setup()
        output_fromGPIO(pin,True)
        while True:
            moisture = ADC0832.getResult(0)
            if moisture != -1:
                return moisture
            sleep(1)

    except:
        ADC0832.destroy()
    finally:
        output_fromGPIO(pin,False)


def get_light():
    try:
        ADC0832.setup()
        output_fromGPIO(pin,True)
        light = ADC0832.getResult(1) - 80
        print(light)
        if light < 0:
            light = 0
        return light
    except:
        ADC0832.destroy()
    finally:
        output_fromGPIO(pin,False)


class CheckHumidity(object):

    def on_get(self, req, resp):
        msg = {
            "key": "humidity",
            "value": get_humidity()
        }
        resp.body = json.dumps(msg)


class CheckTemperature(object):
    def on_get(self, req, resp):
        msg = {
            "key": "temperature",
            "value": get_temperature()
        }
        resp.body = json.dumps(msg)


class CheckMoisture(object):
    def on_get(self, req, resp):
        msg = {
            "key": "moisture",
            "value": get_moisture()
        }
        resp.body = json.dumps(msg)


class CheckLight(object):
    def on_get(self, req, resp):
        msg = {
            "key": "light",
            "value": get_light()
        }
        resp.body = json.dumps(msg)


app = falcon.API()
app.add_route("/humidity", CheckHumidity())
app.add_route("/temperature", CheckTemperature())
app.add_route("/moisture", CheckMoisture())
app.add_route("/light", CheckLight())


if __name__ == "__main__":
    from wsgiref import simple_server
    httpd = simple_server.make_server("0.0.0.0", 8000, app)
    httpd.serve_forever()

import time
import RPi.GPIO as gpio
import threading

global g_state
global led_pins

global light1_red
global light1_yello
global light1_green

global light2_red
global light2_yello
global light2_green

def setup():
    global g_state
    global led_pins

    global light1_red
    global light1_yello
    global light1_green

    global light2_red
    global light2_yello
    global light2_green

    light1_red = 5
    light1_yello = 6
    light1_green = 13

    light2_red = 16
    light2_yello = 20
    light2_green = 21

    g_state=1 #켜져있는 신호등 상태를 저장하는 전역변수
    led_pins = [light1_red,light1_yello,light1_green,light2_red,light2_yello,light2_green] # 빨노초 빨노초

    gpio.setmode(gpio.BCM)
    for x in led_pins:
        gpio.setup(x, gpio.OUT)
        gpio.output(x, 0)
        #LED초기화 및 끄기

def get_input(): #쓰레드로 만들어서 입력을 받는 함수
    global g_state
    try:
        while True:
            g_state=int(input())
            #print("input: ",STATE)
            #input을 받아서 전역변수에 저장한다
    except KeyboardInterrupt:
        gpio.cleanup()

def light1_on():
    global g_state
    global led_pins
    gpio.output(light1_red,0)
    gpio.output(light1_green,1) #1번 신호등의초록불 ON
    g_state=1 #state를 1로 변환(1번 신호등이 켜지므로)
    print("light1 on")
    for i in range(0,10): #state의 변화가 일어날 경우, 함수 종료
        time.sleep(0.3)#0.3초씩 10번, 즉 3초동안 파란불 켜짐
        #print(STATE)
        if(g_state!=1):
            break

def light2_on():
    global g_state
    global led_pins
    gpio.output(light2_red,0)
    gpio.output(light2_green,1)
    g_state=2
    print("light2 on")
    for i in range(0,10):
        time.sleep(0.3)
        #print(STATE)
        if(g_state!=2):
            break


def light1_to_red():#1번 신호등의 색을 붉은색으로 변화시키는 과정이다.
    gpio.output(light1_green, 0)
    gpio.output(light1_yello, 1)
    time.sleep(1)
    gpio.output(light1_yello,0)
    gpio.output(light1_red,1)


def light2_to_red():
    gpio.output(light2_green, 0)
    gpio.output(light2_yello, 1)
    time.sleep(1)
    gpio.output(light2_yello,0)
    gpio.output(light2_red,1)


def traffic_light():
    try:
        while True:
            light1_on()
            light1_to_red()
        
            light2_on()
            light2_to_red()

    except KeyboardInterrupt:
        gpio.cleanup()


    #상태 변경을 위한 STATE입력 함수를 쓰레드로 돌린다.

try:
    if __name__== "__main__":
        setup()

        input_thread = threading.Thread(target=get_input)
        input_thread.start()

        traffic_light_thread = threading.Thread(target=traffic_light)
        traffic_light_thread.start()


except KeyboardInterrupt:
    gpio.cleanup()

#스레드는 한번만 실행할 수 있다.
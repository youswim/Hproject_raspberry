import time
import RPi.GPIO as gpio
import threading

global g_state
global led_pins

def setup():
    global g_state
    global led_pins
    g_state=1 #켜져있는 신호등 상태를 저장하는 전역변수
    led_pins = [5,6,13,16,20,21] # 빨노초 빨노초

    gpio.setmode(gpio.BCM)
    for x in led_pins:
        gpio.setup(x, gpio.OUT)
        gpio.output(x, 0)
        #LED초기화 및 끄기

def get_input(): #쓰레드로 만들어서 입력을 받는 함수
    global g_state
    while True:
        g_state=int(input())
        #print("input: ",STATE)
        #input을 받아서 전역변수에 저장한다

def light1_on():
    global g_state
    global led_pins
    gpio.output(led_pins[0],0)
    gpio.output(led_pins[2],1) #1번 신호등의초록불 ON
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
    gpio.output(led_pins[3],0)
    gpio.output(led_pins[5],1)
    g_state=2
    print("light2 on")
    for i in range(0,10):
        time.sleep(0.3)
        #print(STATE)
        if(g_state!=2):
            break


def light1_to_red():#1번 신호등의 색을 붉은색으로 변화시키는 과정이다.
    gpio.output(led_pins[2], 0)
    gpio.output(led_pins[1], 1)
    time.sleep(1)
    gpio.output(led_pins[1],0)
    gpio.output(led_pins[0],1)


def light2_to_red():
    gpio.output(led_pins[5], 0)
    gpio.output(led_pins[4], 1)
    time.sleep(1)
    gpio.output(led_pins[4],0)
    gpio.output(led_pins[3],1)


def traffic_light():
    try:
        while True:
            light1_on()
            light1_to_red()
        
            light2_on()
            light2_to_red()

    except KeyboardInterrupt:
        pass


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
    pass

#스레드는 한번만 실행할 수 있다.
from flask import Flask
import time
import RPi.GPIO as gpio
import threading
import requests

#13
#필요한 코드 : 신호등 시간 연장
#현재 몇번 신호등이 켜져있는지, 남은시간은 몇초인지 서버에 전송


app = Flask(__name__)

def get_input(): #쓰레드로 만들어서 입력을 받는 함수
    global STATE
    while True:
        STATE=int(input())
        #print("input: ",STATE)
        #input을 받아서 전역변수에 저장한다

def light1_on():
    global STATE
    global current_light
    global current_time

    gpio.output(LED[0],0)
    STATE=1 #state를 1로 변환(1번 신호등이 켜지므로)
    
    current_light = "light1 on"
    print(current_light)

    gpio.output(LED[2],1) #1번 신호등의초록불 ON
    current_time = 3

    for i in range(1,31): #state의 변화가 일어날 경우, 함수 종료
        time.sleep(0.1)#0.3초씩 10번, 즉 3초동안 파란불 켜짐
        if(i%10 == 0):
            print(i)
            current_time = current_time - 1
            print(current_time)
        #print(STATE)
        if(STATE!=1):
            break

def light2_on():
    global STATE
    global current_light
    global current_time

    gpio.output(LED[3],0)
    STATE=2
    
    current_light = "light2 on"
    print(current_light)
    
    gpio.output(LED[5],1)
    current_time = 3
    for i in range(1,31):
        time.sleep(0.1)
        if(i%10 == 0):
            current_time = current_time - 1
            print(current_time)
        #print(STATE)
        if(STATE!=2):
            break


def light1_to_red():#1번 신호등의 색을 붉은색으로 변화시키는 과정이다.
    gpio.output(LED[2], 0)
    gpio.output(LED[1], 1)
    time.sleep(1)
    gpio.output(LED[1],0)
    gpio.output(LED[0],1)


def light2_to_red():
    gpio.output(LED[5], 0)
    gpio.output(LED[4], 1)
    time.sleep(1)
    gpio.output(LED[4],0)
    gpio.output(LED[3],1)


def traffic_light():
    try:
        while True:
            light1_on()
            light1_to_red()
        
            light2_on()
            light2_to_red()

    except KeyboardInterrupt:
        pass


def led_time():
    print("led_time 실행")
    try:
        global current_light
        global current_time

        URL ='http://192.168.55.242:8080/ledtime/'

        a = "init"
        data1 = {
            "ledTime":a
        }
        while True:
            time.sleep(0.1)
            a = current_light+" : "+str(current_time)
            data1 = {
                "ledTime":a
            }
            print(data1)
            
            res = requests.post(URL, json=data1)

            #print(current_light)
            #print(current_time)
            
    except KeyboardInterrupt:
        pass


global STATE
STATE=1 #켜져있는 신호등 상태를 저장하는 전역변수
LED = [5,6,13,16,20,21]

global current_light
current_light = "init"

global current_time
current_time = "init"

gpio.setmode(gpio.BCM)
for x in LED:
    gpio.setup(x, gpio.OUT)
    gpio.output(x, 0)
    #LED초기화 및 끄기

input_thread = threading.Thread(target=get_input)
input_thread.start()

traffic_light_thread = threading.Thread(target=traffic_light)
traffic_light_thread.start()

led_time_thread = threading.Thread(target=led_time)
led_time_thread.start()
    #상태 변경을 위한 STATE입력 함수를 쓰레드로 돌린다.



  
try:
    @app.route('/')
    def SetUp():
        return "Hello server!"
    
    @app.route("/led1/on")
    def led_1_on():
        global STATE
        STATE = 1
        print("led1 on")
        return "LED 1 ON"

    @app.route("/led2/on")
    def led_2_on():
        global STATE
        STATE = 2
        print("led2 on")
        return "LED 2 ON"

    if __name__== "__main__":
        app.run("0.0.0.0", port="18080")  

except KeyboardInterrupt:
    gpio.cleanup()
    pass


gpio.cleanup()


#스레드는 한번만 실행할 수 있다.
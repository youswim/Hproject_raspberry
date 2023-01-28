import time
import RPi.GPIO as gpio
import threading
import pika

global g_host_name
global g_queue_name

global g_state
global g_led_pins

global g_light1_red
global g_light1_yello
global g_light1_green

global g_light2_red
global g_light2_yello
global g_light2_green

def setup():
    global g_host_name
    global g_queue_name

    g_host_name = "localhost"
    g_queue_name = "snowdeer_queue"

    global g_state
    global g_led_pins

    global g_light1_red
    global g_light1_yello
    global g_light1_green

    global g_light2_red
    global g_light2_yello
    global g_light2_green

    g_light1_red = 5
    g_light1_yello = 6
    g_light1_green = 13

    g_light2_red = 16
    g_light2_yello = 20
    g_light2_green = 21

    g_state = 1  # 켜져있는 신호등 상태를 저장하는 전역변수
    g_led_pins = [g_light1_red, g_light1_yello, g_light1_green,
                  g_light2_red, g_light2_yello, g_light2_green]  # 빨노초 빨노초

    gpio.setmode(gpio.BCM)
    for x in g_led_pins:
        gpio.setup(x, gpio.OUT)
        gpio.output(x, 0)
        # LED초기화 및 끄기


def get_input():  # 쓰레드로 만들어서 입력을 받는 함수
    global g_state
    try:
        while True:
            g_state = int(input())
            #print("input: ",STATE)
            # input을 받아서 전역변수에 저장한다
    except KeyboardInterrupt:
        gpio.cleanup()


def receive_message_from_mq():

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=g_host_name))
    channel = connection.channel()

    channel.queue_declare(queue=g_queue_name, arguments={'x-message-ttl': int(1000)})

    def callback(ch, method, properties, body):
        global g_state
        print("Message is Arrived %r" % body)
        g_state = int(body)

    channel.basic_consume(queue=g_queue_name, on_message_callback=callback, auto_ack=True)

    try:
        print("Waiting for messages.")
        channel.start_consuming()
    except KeyboardInterrupt:
        pass

def light1_on():
    global g_state
    global g_led_pins
    gpio.output(g_light1_red, 0)
    gpio.output(g_light1_green, 1)  # 1번 신호등의초록불 ON
    g_state = 1  # state를 1로 변환(1번 신호등이 켜지므로)
    print("light1 on")
    for i in range(0, 10):  # state의 변화가 일어날 경우, 함수 종료
        time.sleep(0.3)  # 0.3초씩 10번, 즉 3초동안 파란불 켜짐
        # print(STATE)
        if(g_state != 1):
            break


def light2_on():
    global g_state
    global g_led_pins
    gpio.output(g_light2_red, 0)
    gpio.output(g_light2_green, 1)
    g_state = 2
    print("light2 on")
    for i in range(0, 10):
        time.sleep(0.3)
        # print(STATE)
        if(g_state != 2):
            break


def light1_to_red():  # 1번 신호등의 색을 붉은색으로 변화시키는 과정이다.
    gpio.output(g_light1_green, 0)
    gpio.output(g_light1_yello, 1)
    time.sleep(1)
    gpio.output(g_light1_yello, 0)
    gpio.output(g_light1_red, 1)


def light2_to_red():
    gpio.output(g_light2_green, 0)
    gpio.output(g_light2_yello, 1)
    time.sleep(1)
    gpio.output(g_light2_yello, 0)
    gpio.output(g_light2_red, 1)


def traffic_light():
    gpio.output(g_light1_red, 1)
    gpio.output(g_light2_red, 1)
    try:
        while True:
            light1_on()
            light1_to_red()

            light2_on()
            light2_to_red()

    except KeyboardInterrupt:
        gpio.cleanup()

    # 상태 변경을 위한 STATE입력 함수를 쓰레드로 돌린다.


try:
    if __name__ == "__main__":
        setup()

        input_thread = threading.Thread(target=get_input)
        input_thread.start()

        receive_message = threading.Thread(target=receive_message_from_mq)
        receive_message.start()

        traffic_light_thread = threading.Thread(target=traffic_light)
        traffic_light_thread.start()


except KeyboardInterrupt:
    gpio.cleanup()

# 스레드는 한번만 실행할 수 있다.

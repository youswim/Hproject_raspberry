import time
import RPi.GPIO as gpio
import threading
import pika

global g_on_light_number

g_host_name = "localhost"
g_queue_name = "snowdeer_queue"

g_light1_red = 5
g_light1_yello = 6
g_light1_green = 13

g_light2_red = 16
g_light2_yello = 20
g_light2_green = 21

def setup():
    led_pins = [g_light1_red, g_light1_yello, g_light1_green,
                  g_light2_red, g_light2_yello, g_light2_green]  # 빨노초 빨노초

    gpio.setmode(gpio.BCM)
    for x in led_pins:
        gpio.setup(x, gpio.OUT)
        gpio.output(x, 0)
        # LED초기화 및 끄기


def get_input():  # 쓰레드로 만들어서 입력을 받는 함수
    global g_on_light_number
    try:
        while True:
            g_on_light_number = int(input())
            #print("input: ",STATE)
            # input을 받아서 전역변수에 저장한다
    except KeyboardInterrupt:
        gpio.cleanup()


def receive_message_from_mq():

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=g_host_name))
    channel = connection.channel()

    channel.queue_declare(queue=g_queue_name, arguments={'x-message-ttl': int(1000)})

    def callback(ch, method, properties, body):
        global g_on_light_number
        print("Message is Arrived %r" % body)
        g_on_light_number = int(body)

    channel.basic_consume(queue=g_queue_name, on_message_callback=callback, auto_ack=True)

    try:
        print("Waiting for messages.")
        channel.start_consuming()
    except KeyboardInterrupt:
        pass

def light_on(g_light_red, g_light_green, light_number):
    global g_on_light_number
    gpio.output(g_light_red, 0)
    gpio.output(g_light_green, 1)  # 1번 신호등의초록불 ON
    g_on_light_number = light_number  # state를 1로 변환(1번 신호등이 켜지므로)
    print("light{} on".format(light_number))
    for i in range(0, 10):  # state의 변화가 일어날 경우, 함수 종료
        time.sleep(0.3)  # 0.3초씩 10번, 즉 3초동안 파란불 켜짐
        # print(STATE)
        if(g_on_light_number != light_number):
            break

def light_to_red(light_red, light_yello, light_green):  # 1번 신호등의 색을 붉은색으로 변화시키는 과정이다.
    gpio.output(light_green, 0)
    gpio.output(light_yello, 1)
    time.sleep(1)
    gpio.output(light_yello, 0)
    gpio.output(light_red, 1)

def traffic_light():
    gpio.output(g_light1_red, 1)
    gpio.output(g_light2_red, 1)
    try:
        while True:
            light_on(g_light1_red, g_light1_green, 1)
            light_to_red(g_light1_red, g_light1_yello, g_light1_green)

            light_on(g_light2_red, g_light2_green, 2)
            light_to_red(g_light2_red, g_light2_yello, g_light2_green)

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

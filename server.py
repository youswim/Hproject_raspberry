#-*- coding:utf-8 -*-

from flask import Flask
from flask import jsonify
import time
import threading
import requests
import pika

global g_on_light_number
global g_light_time

g_host_name = "localhost"
g_change_request_queue = "change_request_queue"
g_light_time_queue = "light_time_queue"

app = Flask(__name__)

@app.route('/')
def SetUp():
    return "Hello server!"
    
@app.route("/led1/on")
def led_1_on():
    send_message("1")
    print("led1 on")
    return "LED 1 ON"

@app.route("/led2/on")
def led_2_on():
    send_message("2")
    print("led2 on")
    return "LED 2 ON"

@app.route("/ledtime")
def get_led_time():
    return jsonify(
        light_number = g_on_light_number,
        time = g_light_time
    )

def receive_message_from_mq():

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=g_host_name))
    channel = connection.channel()

    channel.queue_declare(queue=g_light_time_queue, arguments={'x-message-ttl': int(1000)})

    def callback(ch, method, properties, body):
        global g_on_light_number
        global g_light_time

        print("Message is Arrived %r" % body)
        splitted_body = str(body).split(" ")
        g_on_light_number = splitted_body[0]
        g_light_time = splitted_body[1]

    channel.basic_consume(queue=g_light_time_queue, on_message_callback=callback, auto_ack=True)

    try:
        print("Waiting for messages.")
        channel.start_consuming()
    except KeyboardInterrupt:
        pass

def send_message(light_number):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=g_host_name))
    channel = connection.channel()

    channel.queue_declare(queue=g_change_request_queue, arguments={'x-message-ttl' : int(1000)})

    channel.basic_publish(exchange='', routing_key=g_change_request_queue, body=light_number)
    print(f"Sent message.\n{light_number}")
    connection.close()


try:
    if __name__== "__main__":

        receive_message_from_mq = threading.Thread(target=receive_message_from_mq)
        receive_message_from_mq.start()

        app.run("0.0.0.0", port="18080")  

except KeyboardInterrupt:
    pass

#스레드는 한번만 실행할 수 있다.

#-*- coding:utf-8 -*-

from flask import Flask
import time
import threading
import requests
import pika

g_host_name = "localhost"
g_queue_name = "snowdeer_queue"

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

def send_message(light_number):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=g_host_name))
    channel = connection.channel()

    channel.queue_declare(queue=g_queue_name, arguments={'x-message-ttl' : int(1000)})

    channel.basic_publish(exchange='', routing_key=g_queue_name, body=light_number)
    print(f"Sent message.\n{light_number}")
    connection.close()


try:
    if __name__== "__main__":
        app.run("0.0.0.0", port="18080")  

except KeyboardInterrupt:
    pass

#스레드는 한번만 실행할 수 있다.

#-*- coding:utf-8 -*-

from flask import Flask
from flask import jsonify
import time
import threading
import requests
import pika

global g_on_light_number
global g_light_time
global light_status
light_status = ""

g_host_name = "localhost"
g_change_request_queue = "change_request_queue"
g_light_time_queue = "light_time_queue"

app = Flask(__name__)

@app.route('/')
def SetUp():
    return "Hello server!"

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
        global light_status

        decoded_body = body.decode('utf-8')
        # print("Message is Arrived : %s"%(decoded_body))
        if(light_status != decoded_body):
            light_status = decoded_body
            print("Now light status : %s"%(light_status))
            splitted_body = light_status.split(" ")
            g_on_light_number = int(splitted_body[0])
            g_light_time = int(splitted_body[1])
    

    channel.basic_consume(queue=g_light_time_queue, on_message_callback=callback, auto_ack=True)

    try:
        print("Waiting for messages.")
        channel.start_consuming()
    except KeyboardInterrupt:
        pass

try:
    if __name__== "__main__":

        receive_message_from_mq = threading.Thread(target=receive_message_from_mq)
        receive_message_from_mq.start()

        app.run("0.0.0.0", port="18080")  

except KeyboardInterrupt:
    pass

#스레드는 한번만 실행할 수 있다.

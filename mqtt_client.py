import os
import ssl
import threading
import time
import traceback
import secrets
from client_conf import ClientConf
import paho.mqtt.client as mqtt
import uuid 

class MqttClient:
    def __init__(self, client_conf: ClientConf):
        self.__host = client_conf.host
        self.__port = client_conf.port
        self.__access_key = client_conf.access_key
        self.__access_code = client_conf.access_code
        self.__topic = client_conf.topic
        self.__paho_client: Optional[mqtt.Client] = None
        self.__connect_result_code = -1
        self.__default_backoff = 1000
        self.__retry_times = 0
        self.__min_backoff = 1 * 1000  # 1s
        self.__max_backoff = 30 * 1000  # 30s

        self.user_close=False
        self._on_topic_callback = None

    def set_topic_callback(self,topic_callback):
        self._on_topic_callback = topic_callback

    def connect(self):
        self.__valid_params()
        rc = self.__connect()
        while rc != 0:
            # 退避重连
            low_bound = int(self.__default_backoff * 0.8)
            high_bound = int(self.__default_backoff * 1.0)
            random_backoff = secrets.randbelow(high_bound - low_bound)
            backoff_with_jitter = int(pow(2, self.__retry_times)) * (random_backoff + low_bound)
            wait_time_ms = self.__max_backoff if (self.__min_backoff + backoff_with_jitter) > self.__max_backoff else (
                    self.__min_backoff + backoff_with_jitter)
            wait_time_s = round(wait_time_ms / 1000, 2)
            print("client will try to reconnect after " + str(wait_time_s) + " s")
            time.sleep(wait_time_s)
            self.__retry_times += 1
            self.close()  # 释放之前的connection
            rc = self.__connect()
            # rc为0表示建链成功，其它表示连接不成功
            if rc != 0:
                print("connect with result code: " + str(rc))
                if rc == 134:
                    print("connect failed with bad username or password, "
                          "reconnection will not be performed")
                    pass
        return rc
    def __connect(self):
        try:

            user_name = self.__access_key
            pass_word = self.__access_code

            guid_str = str(uuid.uuid4())

            #self.__paho_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "mqttClient")
            self.__paho_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "mc_"+guid_str)
            # 关闭自动重试， 采用手动重试的方式刷新时间戳
            self.__paho_client._reconnect_on_failure = False
            # 设置回调函数
            self._set_callback()
            # topic放在userdata中，回调函数直接拿topic订阅
            self.__paho_client.user_data_set(self.__topic)
            self.__paho_client.username_pw_set(user_name, pass_word)
            # 当前mqtt broker仅支持TLS1.2
            #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            # 不校验服务端证书
            #context.verify_mode = ssl.CERT_NONE
            #context.check_hostname = False
            #self.__paho_client.tls_set_context(context)

            rc = self.__paho_client.connect(self.__host, self.__port)
            self.__connect_result_code = rc
            if rc == 0:
                threading.Thread(target=self.__paho_client.loop_forever, args=(1, False), name="MqttThread").start()
            # 等待建链
            time.sleep(1)
        except Exception as e:
            self.__connect_result_code = -1
            print("Mqtt connection error. traceback: " + traceback.format_exc())
        if self.__paho_client.is_connected():
            return 0
        else:
            return self.__connect_result_code
    def __valid_params(self):
        assert self.__access_key is not None
        assert self.__access_code is not None
        assert self.__topic is not None

    @staticmethod
    def current_time_millis():
        return str(int(round(time.time() * 1000)))
    def _set_callback(self):
        # 当平台响应连接请求时，执行self._on_connect()
        self.__paho_client.on_connect = self._on_connect
        # 当与平台断开连接时，执行self._on_disconnect()
        self.__paho_client.on_disconnect = self._on_disconnect
        # 当订阅topic时，执行self._on_subscribe
        self.__paho_client.on_subscribe = self._on_subscribe
        # 当接收到一个原始消息时，执行self._on_message()
        self.__paho_client.on_message = self._on_message
    def _on_connect(self, client, userdatas, flags, rc: mqtt.ReasonCode, properties):
        if rc == 0:
            print("Connected to Mqtt Broker!")
            for userdata in userdatas:
                client.subscribe(userdata, 1)
        else:
            # 只有当用户名或密码错误，才不进行自动重连。
            # 如果这里不使用disconnect()方法，那么loop_forever会一直进行重连。
            if rc == 134:
                self.__paho_client.disconnect()
            print("Failed to connect. return code :" + str(rc.value) + ", reason" + rc.getName())
    def _on_subscribe(self, client, userdata, mid, granted_qos, properties):
        print("Subscribed: " + str(mid) + " " + str(granted_qos) + " topic: " + self.__topic[mid-1])
    def _on_message(self, client, userdata, message: mqtt.MQTTMessage):
        if self._on_topic_callback is not None:
            self._on_topic_callback(message.topic, message.payload)
        else:
            print("topic " + message.topic + " Received message: " + message.payload.decode())
    def _on_disconnect(self, client, userdata, flags, rc, properties):
        print("Disconnect to Mqtt Broker. " )
        # 断链后将客户端主动关闭，手动重连刷新时间戳
        try:
            self.__paho_client.disconnect()
        except Exception as e:
            print("Mqtt connection error. traceback: " + traceback.format_exc())
        if not self.user_close:
            self.connect()

    def publish(self, topic: str, payload: str):
        if self.__paho_client is not None and self.__paho_client.is_connected():
            try:
                self.__paho_client.publish(topic, payload)
            except Exception as e:
                print("Mqtt publish error. traceback: " + traceback.format_exc())

    def close(self):
        self.user_close=True
        if self.__paho_client is not None and self.__paho_client.is_connected():
            try:
                self.__paho_client.disconnect()
                print("Mqtt connection close")
            except Exception as e:
                print("paho client disconnect failed. exception: " + str(e))
        else:
            pass

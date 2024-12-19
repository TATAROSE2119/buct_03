from typing import Optional
class ClientConf:
    def __init__(self):
        # mqtt订阅地址
        self.__host: Optional[str] = None
        # mqtt订阅端口号
        self.__port: Optional[int] = None
        # mqtt接入凭据access_key
        self.__access_key: Optional[str] = None
        # mqtt接入凭据access_code
        self.__access_code: Optional[str] = None
        # mqtt订阅topic
        self.__topic: Optional[str] = None


    @property
    def host(self):
        return self.__host
    @host.setter
    def host(self, host):
        self.__host = host
    @property
    def port(self):
        return self.__port
    @port.setter
    def port(self, port):
        self.__port = port
    @property
    def access_key(self):
        return self.__access_key
    @access_key.setter
    def access_key(self, access_key):
        self.__access_key = access_key
    @property
    def access_code(self):
        return self.__access_code
    @access_code.setter
    def access_code(self, access_code):
        self.__access_code = access_code
    @property
    def topic(self):
        return self.__topic
    @topic.setter
    def topic(self, topic):
        self.__topic = topic


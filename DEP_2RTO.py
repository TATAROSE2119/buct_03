from client_conf import ClientConf
from mqtt_client import MqttClient
import os
from typing import Optional
import json
import time
import numpy as np
import threading

lock = threading.Lock()
event = threading.Event()
received_message = None
set_time = 100



########定义数字实验台控制指令##############
#设置点值
commadaction = {
        "command": "action",
        "value":[] #[{"name": 'FV201.OP', "value": '10'}, {"name": 'FCV401.OP', "value": '50'}]
    }

# #系统重置
# commadreset = {
#         "command": "reset",
#         "value":{'工艺':'RTO','工况': '调控初态(甲苯2g)'}
#     }

#运行一步
commadstep = {
        "command": "step",
        "value":0
    }

#设置运行模式
commadmode = {
        "command": "mode",
        "value":0 # 0 手动调用step运行，用于训练; 1 自动运行，用于验证
    }


def onTopic(topic, payload):
    if topic=="$iot/buct_zd_03/user/observation":
        onObservation(payload)

#观察到返回数据
def onObservation(bdata):
    global received_message,event,lock

    # 将 bytes 解码为字符串
    json_str = bdata.decode('utf-8')
    
    # 将字符串转换为 Python 字典
    data = json.loads(json_str)

    with lock:
        if data["type"]=="info01":
            # 虚拟试验台重置成功
            received_message=data["datalist"]
        elif data["type"]=="info02":
            # 执行指令成功
            received_message=data["datalist"]
        elif data["type"]=="data":
            # 返回观察数据
            values_list = [float(value) for value in data["datalist"].values()]

            received_message=data["datalist"]
            # print(data["datalist"])
        else:
            received_message=bdata

    #print(received_message)
    # 设置事件，通知 A 函数继续执行
    event.set()

class ESRTOEnv:
    def __init__(self):

        #连接数字试验台服务器，并启动需要的工况
        self.client_conf = ClientConf()
        self.client_conf.host = "avaktcm.iot.gz.baidubce.com"
        self.client_conf.port = 1883
        self.client_conf.topic = ["$iot/buct_zd_03/user/observation","$iot/buct_zd_03/user/reward"]
        # mqtt接入凭据access_key可使用环境变量的方式注入
        self.client_conf.access_key = "thingidp@avaktcm|buct_zd_03|0|MD5"
        # mqtt接入凭据access_code可使用环境变量的方式注入
        self.client_conf.access_code = "9b2bb671cfc6a89439e9aca94cabbf10"
        #百度不需要
        #client_conf.instance_id = "903a512c-e0dd-4031-851c-7c93973e80bc"
        self.mqtt_client = MqttClient(self.client_conf)
        self.mqtt_client.set_topic_callback(onTopic)
        self.action_name = ['TT211.SP', 'VCH4.OP', 'ACH4.op', 'EACH4.OP', 'TE201ST.OP', 'B201HZ.OP', 'B301HZ.OP'
                            , 'FCV401.OP', 'FV202.OP', 'T1STMAN.OP', 'T2STMAN.OP', 'cv202.OP', 'cv205.OP'
                            , 'cv204.OP', 'cv207.OP']
        if self.mqtt_client.connect() != 0:
            print("init failed")

    def close(self):
        self.mqtt_client.close()
        
    def reset(self,condition):

        #global received_message
        commadreset = {
                        "command": "reset",
                        "value":{'工艺':'二室RTO','工况': condition}
                       }

        event.clear() 

        #启动指定的工况
        self.mqtt_client.publish("$iot/buct_zd_03/user/command", json.dumps(commadreset))

        event.wait(timeout=set_time)  # 可以指定超时时间，比如10秒
        if event.is_set():
            with lock:
                print("接收到消息:",received_message)
                # return received_message
            state_0 = self.step()   
                
            return state_0
        else:
            print("等待超时，未接收到消息,重新尝试发送指令")
            return self.reset(condition) #继续循环

    def step(self):

        #global received_message

        event.clear() 

        #启动指定的工况
        self.mqtt_client.publish("$iot/buct_zd_03/user/command", json.dumps(commadstep))

        event.wait(timeout=set_time)  # 可以指定超时时间，比如10秒
        if event.is_set():
            with lock:
                return received_message
        else:
            print("等待超时，未接收到消息,重新尝试发送指令")
            return self.step() #继续循环
    def get_action(self,state0):
        action_list = []
        for i in range(len(self.action_name)):
            action_list.append(float(state0[self.action_name[i]]))
        # print('action_list',type(action_list))
        return action_list
        


    def action(self,actions):

        #global received_message

        event.clear() 
        global pre_action 
        pre_action = actions
        #启动指定的工况
        commadaction["value"] = []
        # if len(actions) != 9:
        #     return "actions length is not 9"
        for index, action_name in enumerate(self.action_name):
            commadaction["value"].append({"name": f'{action_name}', "value": str(actions[index])})
        
        self.mqtt_client.publish("$iot/buct_zd_03/user/command", json.dumps(commadaction))

        event.wait(timeout=10)  # 可以指定超时时间，比如10秒
        if event.is_set():
            with lock:
                return received_message
        else:
            print("等待超时，未接收到消息,重新尝试发送指令")
            return self.action(actions) #继续循环

    def mode(self,mode):

        #global received_message

        event.clear() 

        commadmode["value"] = mode
        self.mqtt_client.publish("$iot/buct_zd_03/user/command", json.dumps(commadmode))

        event.wait(timeout=set_time)  # 可以指定超时时间，比如10秒
        if event.is_set():
            with lock:
                return received_message
        else:
            print("等待超时，未接收到消息,重新尝试发送指令")
            return self.mode(mode) #继续循环
    def action_dictfn(self, curr_dict):
        global pre_action 
        action_dict =  dict(zip(self.action_name,pre_action))
        # print('curr_dict',type(curr_dict))
        for i in curr_dict.keys():
            action_dict[i] = curr_dict[i]
        return list(action_dict.values())      
        
env=ESRTOEnv()

def DEP_2RTO():
    return env
# -*- coding: utf-8 -*-
#导入和连接服务器是必须的
from DEP_2RTO import DEP_2RTO
import pandas as pd
from tqdm import tqdm
import webbrowser  
  
# 工程综合实践 URL ，手动填写服务器 
url = "https://aidoc.es-online.com.cn:7863/server-detail.html?name=3%E5%8F%B7%E6%9C%8D%E5%8A%A1%E5%99%A8&type=2%E5%AE%A4"  
  
# 使用默认的网页浏览器打开URL  
webbrowser.open(url)

# 连接数字试验台服务器
ConnectedRTO = DEP_2RTO()

# 初始化状态列表和动作列表
# 可选工况列表：入口甲烷浓度固定、入口甲烷浓度波动
state = ConnectedRTO.reset('入口甲烷浓度波动') 
action = ConnectedRTO.get_action(state)
state_list = []

# 设置实验总运行时长, s
run_time = 100

# 开展实验
for i in tqdm(range(run_time)):
    
    # 在运行到第5s时，修改部分动作列表的值
    # if i == 5:
    #     """  可修改的动作列表：
    #        'TT211.SP', 'VCH4.OP', 'ACH4.op', 
    #        'EACH4.OP', 'TE201ST.OP', 'B201HZ.OP', 
    #         'B301HZ.OP', 'FCV401.OP', 'FV202.OP', 
    #         'T1STMAN.OP', 'T2STMAN.OP', 'cv202.OP', 
    #         'cv205.OP', 'cv204.OP', 'cv207.OP'
    #     """    
    #     action = ConnectedRTO.action_dictfn({"T1STMAN.OP": 30, "FV202.OP": 40}) 

    # 赋予控制值
    ConnectedRTO.action(action)

    # 执行数字实验，将状态数据状态存入列表
    state_list.append(ConnectedRTO.step())

# 将数据保存为CSV文件
pd.DataFrame(state_list).to_csv('./data.csv')
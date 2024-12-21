# -*- coding: utf-8 -*-
# 导入和连接服务器是必须的
from DEP_2RTO import DEP_2RTO
import pandas as pd
from tqdm import tqdm
import webbrowser
import numpy as np

# 工程综合实践 URL ，手动填写服务器
url = "https://aidoc.es-online.com.cn:7863/server-detail.html?name=3%E5%8F%B7%E6%9C%8D%E5%8A%A1%E5%99%A8&type=2%E5%AE%A4"

# 使用默认的网页浏览器打开URL
webbrowser.open(url)

# 连接数字试验台服务器
ConnectedRTO = DEP_2RTO()

# 初始化状态列表和动作列表
state = ConnectedRTO.reset('入口甲烷浓度固定')
action = ConnectedRTO.get_action(state)
state_list = []

# 设置实验总运行时长, s
run_time = 100

# 分析范围
T1_range = range(20, 300, 20)  # 提升阀切换时间 T1
T2_range = range(20, 300, 20)  # 提升阀切换时间 T2
FV202_range = np.linspace(0, 100, 11)  # 热旁通阀门开度，0%到100%，步长10%

# 保存实验结果
results = []

# 遍历 T1、T2 和热旁通阀门开度组合
for T1 in T1_range:
    for T2 in T2_range:
        for FV202 in FV202_range:

            # 重置系统状态
            state = ConnectedRTO.reset('入口甲烷浓度固定')

            # 初始化动作字典
            action = ConnectedRTO.get_action(state)
            action = ConnectedRTO.action_dictfn({"T1STMAN.OP": T1, "T2STMAN.OP": T2, "FV202.OP": FV202})

            # 运行实验
            for i in tqdm(range(run_time)):
                # 赋予控制值
                ConnectedRTO.action(action)

                # 执行数字实验，将状态数据状态存入列表
                current_state = ConnectedRTO.step()
                state_list.append(current_state)

                # 记录实验数据
                if i == run_time - 1:  # 只记录最后一个时间点的结果
                    results.append({
                        "T1": T1,
                        "T2": T2,
                        "FV202": FV202,
                        "产热量": current_state.get('HFV202.PV', 0)  # 记录热旁通去锅炉的热量
                    })

# 将结果保存为CSV文件
results_df = pd.DataFrame(results)
results_df.to_csv('./static_optimization_results.csv', index=False)

# 将完整的状态列表数据保存
pd.DataFrame(state_list).to_csv('./data.csv', index=False)

print("实验完成，结果已保存为 static_optimization_results.csv")

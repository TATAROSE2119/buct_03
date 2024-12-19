

# 项目概述

本项目旨在通过基于北京东方仿真控制技术有限公司开发的高精度蓄热式热力氧化炉，封装成动态仿真环境，提供测试案例，帮助用户了解如何调用该环境下进行机器学习、深度学习以及（但不限于）强化学习的研究和开发。项目包含了一系列Python脚本、Jupyter Notebook文件和环境配置文件，这些资源不仅展示了强化学习的应用，还覆盖了更广泛的机器学习领域，使用户能够灵活进行各种机器学习任务。

# 文件说明

mindsporerl.yaml：Anaconda环境依赖配置文件，包含了运行本项目所需的所有Python库。
mqtt_client.py、client_conf.py、esrto.py：这些文件提供了与特定环境（如MQTT服务器或ES RTO环境）进行通信的功能，不仅限于强化学习，也可能在其他机器学习任务中用到。
demo.ipynb：一个Jupyter Notebook文件，用于演示如何与环境进行基本交互的方法，包括重置工况/初次启动工况、执行动作、运行获取当前数据等方法。
demo.py：与demo.ipynb相对应的Python脚本，方便在IDE中直接运行和调试。
rto.ipynb：另一个Jupyter Notebook文件，专注于展示如何与仿真环境交互完成DQN强化学习案例，包括模型定义、训练、评估等过程。


# 准备工作

下载并安装Anaconda：访问Anaconda官网下载并安装Anaconda。

# 运行步骤

1. 导入环境依赖
在Anaconda的Environments界面中，点击Import按钮，选择mindsporerl.yaml文件导入环境依赖。
2. 运行Demo和示例
方法1：使用Python脚本：在VS Code、PyCharm等IDE中，加载demo.py或其他Python脚本文件，并在IDE的终端或命令行中运行。
方法2：使用Jupyter Notebook：启动Jupyter Notebook，打开demo.ipynb、rto.ipynb或其他Notebook文件，按照文件中的说明运行每个单元格。
3. 编写自己的算法
基于提供的示例，你可以开始编写自己的机器学习或深度学习算法。完成异常状态检测、故障诊断、工艺优化等任务。

# 注意事项

1.确保在正确的环境中运行代码，避免版本冲突或依赖缺失的问题。
2.本项目提供的代码和示例仅供参考和学习使用，可能需要根据实际环境和需求进行调整和优化。


  




​	


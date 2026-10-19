![](https://image.3001.net/images/20200502/1588416692_5ead50b45b6c2.jpg!small)

##  DeathRansom

**DeathRansom是一款基于Python开发的勒索软件平台，DeathRansom生成的勒索软件将带有强大的绕过技术，该工具仅出于教育目的，请不要将其用于恶意行为。**

###  何为勒索软件？

勒索软件是恶意软件的一种，它可以加密目标设备中的所有文件，并向用户显示勒索赎金的请求信息，攻击者会在这里显示需要支付的赎金金额，一般都会要求通过比特币进行支付，然后设置一个解密文件的最后时间，当然攻击者也有可能直接删除目标用户的文件。

##  工具运行机制

首先，工具脚本会判断当前勒索软件是否处于沙盒、调试器和虚拟机等环境，并尝试绕过它们。

接下来，工具会以deathransom.py脚本中第六十行所定义的根目录路径开始对目标文件进行加密。

最后，工具将会下载勒索请求脚本，禁用目标设备的CMD命令行工具、任务管理器和注册表工具，然后开启计时器以删除目标文件。

##  工具使用

首先，广大研究人员需要使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/ReddyyZ/DeathRansom.git

接下来切换到项目目录内，运行下列命令安装依赖组件：

    
    
    pip install -r requirements.txt
    
        python3 -m pip install PyQt5

接下来，使用下列命令生成密钥并将公共密钥上传至pastebin，复制原始链接，然后修改deathransom.py中第七行的站点地址：

    
    
    python generate_key.py

将time_script.py和main.py装换成exe文件，这里需要使用Python2版本的pyinstaller将time_script转换成exe文件：

    
    
    pyinstaller --onefile --windowed <FILE>

为了转换勒索请求的main.py文件，我们则需要使用Python3版本的pyinstaller：

    
    
    pyinstaller --onefile --windowed main.py

最后，将生成的脚本文件上传到任意一个文件托管服务中，修改deathransom.py文件中的第28和31行代码中的链接。然后使用Python2版本的pyinstaller将deathransom.py转换为exe可执行文件。

##  绕过技术

###  反编译

创建多个变量来让反编译更难实现。

###  反调试器

使用ctypes函数windll.kernel32.IsDebuggerPresent()来判断调试器是否处于活动状态。

###  反虚拟机

判断目标设备的MAC地址是否跟标准虚拟机MAC地址相同。

###  反沙盒

通过多种方法检测当前环境是否为沙盒环境。

##  如何编辑勒索信息

如需编辑勒索信息，用户还需要安装[PySide2](https://pypi.org/project/PySide2/)。接下来，打开main.ui文件，然后根据自己的需要进行勒索信息修改即可。

##  工具演示视频

![](https://image.3001.net/images/20200502/1588416776_5ead5108253d1.jpg!small)

> 视频地址：[https://www.*******.com/watch?v=N3Km-> TpPBp0](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=N3Km-TpPBp0)

##  PT-BR演示视频

![](https://image.3001.net/images/20200502/1588416789_5ead5115b5038.jpg!small)

> 视频地址：[https://www.*******.com/watch?v=wiWBa-> SfNCU](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=wiWBa-SfNCU)

###  讨论组

如果你对DeathRansom的使用有疑问的话，可以进入讨论组进行交流研究：【[点我访问](https://discord.gg/v5d3PZ9)】。

##  项目地址

> DeathRansom：【[GitHub传送门](https://github.com/ReddyyZ/DeathRansom)】

 ***
参考来源：[ReddyyZ](https://github.com/ReddyyZ/DeathRansom)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


2022 年 12 月 9 日，研究人员在 PyPI 中发现又一个供应链攻击。2022 年 12 月 6 日名为 aioconsol 的 Python
包发布，同一天发布了三个版本。与此前披露的名为 shaderz 的 Python 包类似，并没有相关的描述信息。

![image.png-195.2kB](https://image.3001.net/images/20221222/1671694614_63a40916deda8955932d9.png!small)项目描述

![image.png-215.4kB](https://image.3001.net/images/20221222/1671694615_63a409179b3fde30e9f2b.png!small)版本发布

该 Python 包的 2.0 版在 setup.py 脚本中包含恶意代码，将二进制内容写入名为 test.exe 的文件，这作为安装过程中的一部分。

![image.png-139.6kB](https://image.3001.net/images/20221222/1671694616_63a409186ce222c180475.png!small)2.0
版的 setup.py

在 0.0 版本与 1.0 版本中，`__init__.py`脚本也有类似的恶意代码，如下所示：

![image.png-156.1kB](https://image.3001.net/images/20221222/1671694617_63a409193e7ea4f0000b9.png!small)1.0
版恶意代码

![image.png-151.6kB](https://image.3001.net/images/20221222/1671694618_63a4091a07ed588927900.png!small)0.0
版恶意代码

VirusTotal 中部分引擎将该 EXE 可执行文件标记为恶意：

![image.png-430.6kB](https://image.3001.net/images/20221222/1671694619_63a4091b0bbf8636cbfbd.png!small)VirusTotal
检测信息

## 具体行为

执行该 EXE 可执行文件，创建名为 stub.exe 的子进程。

![image.png-179.7kB](https://image.3001.net/images/20221222/1671694620_63a4091cde2e62ee403f0.png!small)进程运行

程序在 `%USER%\AppData\Local\Temp\onefile_%PID_%TIME%`处释放多个文件：

![image.png-549.9kB](https://image.3001.net/images/20221222/1671694622_63a4091e3531f2397e076.png!small)释放文件

释放的可执行文件 stub.exe 被少数引擎检出：

![image.png-201.3kB](https://image.3001.net/images/20221222/1671694623_63a4091fec03e3a46ef97.png!small)VirusTotal
检测信息

执行 test.exe 后，会将自身复制到 `%USER%\AppData\Local\WindowsControl`名为 Control.exe 以及释放
run.bat 的批处理文件。

![image.png-96.1kB](https://image.3001.net/images/20221222/1671694624_63a40920eb25aac178d02.png!small)创建文件

run.bat 脚本显示文件 Control.exe 的路径，确保在启动时运行。

![image.png-55.7kB](https://image.3001.net/images/20221222/1671694625_63a409219405340b8abf5.png!small)run.bat

尝试连接到多个 IP 地址，进行敏感数据的泄露：

![image.png-307.8kB](https://image.3001.net/images/20221222/1671694626_63a4092232ded99ab3f3d.png!small)与
104.20.67.143 的网络连接

![image.png-298.2kB](https://image.3001.net/images/20221222/1671694627_63a40923545449992a5fc.png!small)与
104.20.68.143 的网络连接

![image.png-317.7kB](https://image.3001.net/images/20221222/1671694628_63a409249e54a07900453.png!small)与
172.67.34.170 的网络连接

![image.png-116kB](https://image.3001.net/images/20221222/1671694629_63a40925ca9911e9d17b9.png!small)与
185.106.92.188 的网络连接

![image.png-389.4kB](https://image.3001.net/images/20221222/1671694630_63a4092679c2a78833809.png!small)双方通信的加密数据

## 结论

研究人员在不到一周的时间内两次发现针对 Python 的供应链攻击，这说明攻击者对这种攻击方式非常青睐。用户也需要高度警惕不明来源安装的 Python
包，其中很可能包含恶意软件。

## IOC

> 52e6efbbfb1fdeb976e2464c542bc17747d213d67f28dff4d7df0879df23fd7e  
> 8124cec491e0249bc4a9f3f9d3755201b0e8c28068ce8c4b528217dbb94afd13  
> 104.20.67.143  
> 104.20.68.143  
> 172.67.34.170  
> 185.106.92.188

## 参考来源

> [Fortinet](https://www.fortinet.com/blog/threat-research/new-supply-chain-> attack-uses-python-package-index-aioconsol)


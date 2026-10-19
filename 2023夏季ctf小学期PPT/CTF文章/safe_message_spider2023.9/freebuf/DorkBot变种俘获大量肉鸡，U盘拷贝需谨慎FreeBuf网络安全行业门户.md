## 1.简述

**近日，深信服EDR安全团队接到某用户反馈，其内网170多台主机被检测出僵尸网络病毒，而且奇怪的是，这些主机之间并没有通过网络进行传播感染，那么为何被感染的主机一直增多呢？深信服EDR安全团队通过深入追踪分析，发现这个病毒是通过U盘进行传播感染，是DorkBot的一个变种。通过深信服安全云脑，发现DorkBot仍然还是比较流行的僵尸网络病毒家族。**

该DorkBot病毒变种属于蠕虫病毒，被感染的所有主机都会沦为黑客的肉鸡，不定期对外网主机进行DDoS攻击，同时其还具有极强的隐蔽性，运行之后会把恶意代码注入到合法进程，然后删除自身，使得客户很难发现主机被感染了。

##  **2.攻击场景**

###  **2.1** **病毒流程**

![图片.png](https://image.3001.net/images/20180731/1533030877_5b6031dd91a65.png!small)

###  **2.** **2** **攻击现场**

运行ProcessHacker查看进程列表，发现有三个可疑的进程svchost.exe、mspaint.exe、calc.exe（这三个进程皆没有窗口）。

![图片.png](https://image.3001.net/images/20180731/1533030887_5b6031e7e664e.png!small)

查看该svchost.exe进程的信息，发现它没有父进程，猜测它应该是被病毒创建出来的孤儿进程（合法的svchost.exe父进程为services.exe）。

![图片.png](https://image.3001.net/images/20180731/1533030898_5b6031f2682d1.png!small)

calc.exe也没有父进程，同时calc.exe还试图连接可疑IP。

![图片.png](https://image.3001.net/images/20180731/1533030909_5b6031fd3490e.png!small)

这三个进程特征行为几乎相同，我们以mspaint.exe为例进行检测。使用工具发现，其内存中存在RWX内存段和PE结构，这是很典型的进程注入特征。

![图片.png](https://image.3001.net/images/20180731/1533030917_5b60320550eca.png!small)

通过检索字符串，更加确凿该进程被注入了，而且恶意行为可能是窃取某些网站的密码。

![图片.png](https://image.3001.net/images/20180731/1533030926_5b60320eadb20.png!small)

mspaint.exe和calc.exe一样都有连接可疑IP的行为。

![图片.png](https://image.3001.net/images/20180731/1533030934_5b6032165eb37.png!small)

病毒为了实现开机自启动，在注册表中添加了Updater.exe.exe的自启动项（该文件此时已被我们的EDR工具所隔离）。

![图片.png](https://image.3001.net/images/20180731/1533030942_5b60321eb27a7.png!small)

##  **3.病毒分析**

###  **3.1 病毒结构**

![图片.png](https://image.3001.net/images/20180731/1533030951_5b6032275bb9c.png!small)

###  **3.2** **注入模块**

在主函数的开头，病毒母体创建一个线程完成calc.exe进程的创建及注入。

![图片.png](https://image.3001.net/images/20180731/1533030960_5b603230ab7ae.png!small)

注入恶意代码到svchost.exe。

![图片.png](https://image.3001.net/images/20180731/1533030971_5b60323b0c465.png!small)

在svchost.exe的内存中发现了一个可疑PE文件。

![图片.png](https://image.3001.net/images/20180731/1533030980_5b603244d1591.png!small)

创建进程mspaint.exe并注入恶意代码，该工作由svchost.exe完成。

![图片.png](https://image.3001.net/images/20180731/1533030989_5b60324d39e08.png!small)

###  **3.** **3** **通信模块**

病毒将网络连接相关的所有API写入了scot节，运行时对它们进行动态加载，所以我们在函数导入表中根本看不到这些API。 ****

![图片.png](https://image.3001.net/images/20180731/1533030998_5b603256d6cf4.png!small)

当mspaint.exe运行时，这些API就会被动态加载和调用，以下是mspaint.exe跟其中一个C &C服务器通信的过程。

![图片.png](https://image.3001.net/images/20180731/1533031006_5b60325e4b713.png!small)

![图片.png](https://image.3001.net/images/20180731/1533031017_5b60326944632.png!small)

从Wireshark抓到的流量可以发现，这发送的数据应该是被编码后的指令。

![图片.png](https://image.3001.net/images/20180731/1533031025_5b603271e93d7.png!small)

###  **3.** **4** ******DDo** **S** **模块**

跟C&C服务器通信后，C&C服务器会不定期对所有肉鸡下发攻击命令，攻击主要是以DDos的形式进行的。如下是肉鸡向外进行SYN Flood和UDP
Flood的过程。 ****

![图片.png](https://image.3001.net/images/20180731/1533031033_5b603279e5303.png!small)![图片.png](https://image.3001.net/images/20180731/1533031038_5b60327e66cea.png!small)

###  **3.** **5** **传播模块**

该病毒通过U盘进行传播，相关代码在进程svchost.exe中实现。

![图片.png](https://image.3001.net/images/20180731/1533031047_5b6032875d4aa.png!small)![图片.png](https://image.3001.net/images/20180731/1533031052_5b60328c7c97c.png!small)
![图片.png](https://image.3001.net/images/20180731/1533031056_5b603290b308f.png!small)

### **3.** **6** **隐藏模块**

病毒最后会将自己添加到注册表启动项中，实现开机自启动。

![图片.png](https://image.3001.net/images/20180731/1533031067_5b60329b94f08.png!small)

然后创建一个子进程将病毒母体删除。

![图片.png](https://image.3001.net/images/20180731/1533031075_5b6032a39a5eb.png!small)

##  **4.解决方案**

（1）终止红框中的恶意进程，其中svchost.exe是没有父进程的svchost.exe。

![图片.png](https://image.3001.net/images/20180731/1533031085_5b6032ade3a7a.png!small)

（2）删除HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run项下的Windows Update
Installer键以及对应的文件C:\Users\Administrator\AppData\Roaming\WindowsUpdate\Updater.exe。

![图片.png](https://image.3001.net/images/20180731/1533031093_5b6032b559e34.png!small)

（3）删除U盘中的隐藏文件（病毒母体和autorun.inf），在这之前要设置文件显示选项为显示隐藏文件。

（4）建议对全网进行一次安全检查和杀毒扫描，结合安全服务，加强防护工作。推荐使用深信服安全感知+防火墙+终端响应平台，对内网进行感知、查杀和防护。

##  **5.相关IOC**

 **文件MD5:**

44EA6A2CEEF1A2D49A66A78E85B73F15

7BCCE7FD7E247C7C6BCF762F3863E806

 *** 本文作者：千里目安全实验室，转载注明来自FreeBuf.COM**  


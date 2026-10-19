**近日，深信服接到某金融客户反馈，其Linux服务器中了勒索病毒，深信服安全团队研究发现，该勒索病毒加密后缀为.lucky，是新的勒索病毒变种，其传播模块复用了Satan的传播方式，实现了Linux下的自动化传播，我们将其命名为lucky勒索病毒。**

![1.jpg](https://image.3001.net/images/20181129/1543458401_5bff4e61b3ad1.jpg!small)

##  **0x01** **攻击流程**

![2.jpg](https://image.3001.net/images/20181129/1543458428_5bff4e7c929cc.jpg!small)

ft32是病毒母体，conn32是传播模块，cry32是lucky勒索模块。

1.ft32病毒自复制成.loop并添加自启动项。

2..loop从黑客服务器上下载传播模块conn32和勒索模块cry32并运行。

3.cry32对系统中的文件进行加密，加密后缀名为.lucky。

4.conn32对内网主机进行扫描，并利用多个流行漏洞，传播病毒母体。

该程序在启动时会根据启动参数argv[1]来判断是否进行install，使用argv[0]本身程序名来检测是否以LTMP或者.loop启动。LTMP启动方式目前没有什么动作，直接返回。

直接执行ft32，不带任何参数，将会复制自身到.loop程序中，并且以.loop创建一个进程：

![3.jpg](https://image.3001.net/images/20181129/1543458441_5bff4e89bbfb3.jpg!small)

当ft32结束之后，.loop运行中，会根据自身进程名是否为.loop来创建.hash，下载.conn，.crypt，LTMP，RTMP等等恶意程序。

![4.jpg](https://image.3001.net/images/20181129/1543458450_5bff4e9211cbd.jpg!small)

且执行.conn和.crypt，.conn为传播组件，.crypt为加密组件。

![5.jpg](https://image.3001.net/images/20181129/1543458457_5bff4e99ae01d.jpg!small)

除了下载恶意组件来完成目的，.loop还会通过计划任务，开机自启动等来实现持久性：

![6.jpg](https://image.3001.net/images/20181129/1543458470_5bff4ea6470c2.jpg!small)

##  **0x02 lucky** **勒索加密体**

读取/tmp/Ssession文件：

![7.jpg](https://image.3001.net/images/20181129/1543458488_5bff4eb82fe46.jpg!small)

遍历系统文件进行加密，加密后缀为“.lucky”：

![8.jpg](https://image.3001.net/images/20181129/1543458506_5bff4eca22368.jpg!small)

排除如下目录：  
![9.jpg](https://image.3001.net/images/20181129/1543458523_5bff4edb9f754.jpg!small)

加密文件类型：

![10.jpg](https://image.3001.net/images/20181129/1543458533_5bff4ee577453.jpg!small)

上传被加密文件的数量、大小以及获取到的Ssession：  
![11.jpg](https://image.3001.net/images/20181129/1543458544_5bff4ef094afc.jpg!small)

生成加密信息：  
![12.jpg](https://image.3001.net/images/20181129/1543458554_5bff4efa0b891.jpg!small)

## **0x03** **传播模块**

conn与Satan的传播模块一致，跟Windows版本一样，主要利用以下漏洞进行攻击：

1.JBoss反序列化漏洞(CVE-2013-4810)

2.JBoss默认配置漏洞(CVE-2010-0738)

3.Tomcat任意文件上传漏洞（CVE-2017-12615）

4.Tomcat web管理后台弱口令爆破

5.Weblogic WLS 组件漏洞（CVE-2017-10271）

6.Windows SMB远程代码执行漏洞MS17-010

7.Apache Struts2远程代码执行漏洞S2-045

8.Apache Struts2远程代码执行漏洞S2-057

比较有意思的是，我们在该Linux样本中发现了大量.exe的字样，我们初步怀疑该样本是个跨平台样本，通过Web应用漏洞对Windows、Linux进行无差别攻击，后续的分析也印证了这一点。

![13.png](https://image.3001.net/images/20181129/1543458874_5bff503a77083.png!small)

###  **核心函数**

![14.jpg](https://image.3001.net/images/20181129/1543458893_5bff504d4bcd5.jpg!small)

###  **Tomcat** **任意文件上传漏洞**

针对Linux系统 ，Tomcat上传漏洞传播ft32&ft64病毒母体。

![15.jpg](https://image.3001.net/images/20181129/1543458910_5bff505ec3be2.jpg!small)

针对Windows系统，Tomcat上传漏洞传播fast.exe病毒母体。

![16.png](https://image.3001.net/images/20181129/1543458923_5bff506bab48c.png!small)

###  **Tomcat** **管理后台弱口令爆破**

![17.png](https://image.3001.net/images/20181129/1543458938_5bff507acd559.png!small)

###  **Struts2** **远程执行** **S2-045** **漏洞**

会根据目标OS执行不同的恶意命令：

![18.jpg](https://image.3001.net/images/20181129/1543458954_5bff508a4a474.jpg!small)

###  **Struts2** **远程执行** **S2-057** **漏洞**

![19.jpg](https://image.3001.net/images/20181129/1543458967_5bff509715be3.jpg!small)

###  **Weblogic WLS** **组件漏洞**

![20.jpg](https://image.3001.net/images/20181129/1543458980_5bff50a44247e.jpg!small)

###  **JBoss** **默认配置漏洞**

![21.jpg](https://image.3001.net/images/20181129/1543458994_5bff50b27514f.jpg!small)

###  **SMB** **远程代码执行漏洞**

![22.jpg](https://image.3001.net/images/20181129/1543459004_5bff50bc65c1e.jpg!small)

##  **0x04** **解决方案**

1.隔离感染主机：已中毒计算机尽快隔离，关闭所有网络连接，禁用网卡。

2.切断传播途径：关闭潜在终端的SMB 445等网络共享端口，关闭异常的外联访问。深信服下一代防火墙用户，可开启IPS和僵尸网络功能，进行封堵。

3.查找攻击源：手工抓包分析或借助深信服安全感知。

4.查杀病毒：推荐使用深信服EDR进行查杀。

5.修补漏洞：打上以下漏洞相关补丁，漏洞包括“永恒之蓝”漏洞，JBoss反序列化漏洞(CVE-2013-4810)、JBoss默认配置漏洞(CVE-2010-0738)、Tomcat任意文件上传漏洞（CVE-2017-12615）、Weblogic
WLS 组件漏洞（CVE-2017-10271）、apache Struts2远程代码执行漏洞S2-045、Apache
Struts2远程代码执行漏洞S2-057。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**


## **僵尸网络概况**

近日，阿里云安全监测并捕获到一个针对云服务器发起攻击的新型僵尸网络，由于其使用的扫描、攻击程序名为AutoUpdate，我们也据此将其命名为AutoUpdate僵尸网络。

阿里云安全专家分析发现，该僵尸网络除了常规的持久化、挖矿牟利、隐藏自身等行为外，更会扫描失陷服务器的磁盘，盗取云账号Access
Key等核心数据，对用户的账号和数据安全造成极高风险。此外，扫描攻击所使用的漏洞武器种类繁多，对数十种常见服务均造成威胁，危害极大。

AutoUpdate僵尸网络的传播行为在7月7日左右达到顶峰，略微沉寂三天后又出现了新一波传播扩散的苗头：

![](https://image.3001.net/images/20210721/1626834422_60f785f66999745c60704.png!small)

 **用户应提高警惕，可以购买安全产品进行有效防护，当前包括云防火墙在内的多款阿里云安全产品已支持检测、拦截该僵尸网络的攻击。**

##  **详细分析**

蠕虫的行为主要分为以下几个阶段：

初始攻

|

建立据点

|

横向移动

|

持久化

|

收尾  
  
---|---|---|---|---  
  
远程服务漏洞利用(Spring、Shiro、Weblogic、知名OA...)

|

破坏防御-关闭安全软件

|

内外网漏洞扫描

|

执行流劫持-动态链接库注入

|

清除命令记录  
  
未授权访问(Docker、Redis...)

|

清理其他僵尸网络

|

入侵可免密登录主机

|

进程隐藏

|

挖矿/资源劫持  
  
爆破攻击(Tomcat、数据库...)

|

写入webshell

|  
|  
|

应用凭据窃取及二次利用  
  
##  **网络传播手段**

该僵尸网络使用Go语言编写恶意软件，并针对Linux和Windows系统分别编译，因此在这两种系统的主机上都能够运行和传播。

下面以Linux系统上的运行、传播过程为例进行说明：

![](https://image.3001.net/images/20210721/1626834613_60f786b515d4b5c9701ba.png!small)

###  **看似合法的恶意域名**

该僵尸网络使用
[http://m.windowsupdatesupport.org](http://m.windowsupdatesupport.org/d/loader.sh)作为主要的恶意程序下载域名，该域名与微软下载更新所使用的正常网址极为相似，容易导致防御侧混淆和漏过。

此外，攻击者还注册了 gunupdatepkg.com 这个与正常域名非常相似的域名，用来存放利用fastjson漏洞时需要的恶意LDAP远程源文件。

###  **下载和更新恶意程序**

失陷服务器首先会被执行命令，下载并运行[hxxp://m.windowsupdatesupport.org/d/loader.sh](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)。

loader.sh则会下载并运行kworkers，后者会读取[hxxp://m.windowsupdatesupport.org/d/](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)windowsupdatev1.json
文件。

![](https://image.3001.net/images/20210721/1626834879_60f787bf8e651ab1ff0b5.png!small)

windowsupdatev1.json是该僵尸网络的配置文件，其中包括了恶意文件名称、url及其最新版本信息：

![](https://image.3001.net/images/20210721/1626834938_60f787faa332ad02a9d7a.png!small)

之后将每个文件的最新版本号与存储在主机上文件.{filename}_ver中的原有版本号进行对比，需要更新则kill原有进程，下载新程序并执行。

 **漏洞扫描攻击和横向传播**

攻击和扫描程序AutoUpdate会利用数十种漏洞武器，对包括PostgreSQL, Mssql,
Fastjson、Docker、致远OA、Jenkins、WebLogic、Tomcat在内的服务进行漏洞扫描和攻击：

![](https://image.3001.net/images/20210721/1626834972_60f7881c954591d48ad3f.png!small)

利用的漏洞至少包括：

多种OA软件的远程命令执行

Spring boot actuator远程命令执行

Shiro反序列化漏洞

Struts2远程命令执行

Weblogic远程命令执行

Docker未授权访问

Jenkins 未授权命令执行

Tomcat 爆破

....

此外，攻击者通过hxxp://[m.windowsupdatesupport.org/task_scheduler](http://m.windowsupdatesupport.org/task_scheduler)这个地址下发扫描任务，控制失陷主机扫描的网段

![](https://image.3001.net/images/20210721/1626835189_60f788f5958e252b5c8e2.png!small)

除了AutoUpdate外，sshkey.sh文件会读取失陷主机曾经免密登录过的主机列表，并在这些主机上执行恶意命令，同样达到横向传播的目的：![](https://image.3001.net/images/20210721/1626835258_60f7893a024f17f443bc0.png!small)

##  **主机层面行为**

###  **Access key** **盗取**

在AutoUpdate程序中，存在一个非常危险的函数infocollect()，它会盗取用户的Access key
，具体做法为遍历所有文件夹，寻找以下后缀的配置文件：

.conf

.properties

.yml

.config

然后使用正则匹配，在文件内容中寻找符合Access key和Secret
key长度的字符串，并将找到的Ak/sk通过http请求发送给攻击者控制的恶意服务器
[hxxp://](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)mail.windowsupdatesupport.org。

![](https://image.3001.net/images/20210721/1626835626_60f78aaabf267e49a9de2.png!small)

由于获取AK后能够调用云账号下的所有资源和功能，一旦AK泄露，需要尽快重置，以避免进一步的损失和风险。

###  **终止安全软件和其他僵尸网络进程**

loader.sh中含有终止安全软件的指令，具体行为是结束几种主机安全HIDS产品的进程：

![](https://image.3001.net/images/20210721/1626836192_60f78ce062b7beadb6317.png!small)

此外，为确保能够独占失陷主机的CPU，该僵尸网络还会kill其他僵尸网络的进程

![](https://image.3001.net/images/20210721/1626836213_60f78cf5701fa1eb669b9.png!small)

###  **附加链接库隐藏进程**

下载processhider.c文件并编译成libc2.28.so后，将该文件附加到ld.so.preload，从而达到隐藏自身进程的目的

![](https://image.3001.net/images/20210721/1626836242_60f78d121d24900a30e62.png!small)

##  **安全解决方案**

当前云防火墙已支持对AutoUpdate所利用的多种高危漏洞攻击进行检测和拦截，如下图所示：

![](https://image.3001.net/images/20210721/1626836287_60f78d3f64527e42011d1.jpg!small)

点击右侧“详情”按钮即可查看具体信息和攻击payload：

![](https://image.3001.net/images/20210721/1626836315_60f78d5beb2485af5095c.png!small)

##  **IOC**

###  **恶意域名**

*.windowsupdatesupport.org

*.gunupdatepkg.com

###  **Url**

[hxxp://m.windowsupdatesupport.org/d/loader.sh](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)

[hxxp://m.windowsupdatesupport.org/d/](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)dbus

[hxxp://m.windowsupdatesupport.org/d/](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)hideproc.sh

[hxxp://m.windowsupdatesupport.org/d/](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)ssh_key.sh

[hxxp://m.windowsupdatesupport.org/d/windowsupdatev1.json](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)

[hxxp://m.windowsupdatesupport.org/d/](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)autoupdate

[hxxp://m.windowsupdatesupport.org/d/](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)kworkers

[hxxp://m.windowsupdatesupport.org/d/service.exe](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)

[hxxp://m.windowsupdatesupport.org/d/](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)inj.exe

[hxxp://m.windowsupdatesupport.org/d/](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)runtime.dll

[hxxp://m.windowsupdatesupport.org/d/](http://m.windowsupdatesupport.org/d/windowsupdatev1.json)updater.exe

###  **Md5**

1295507537170a526985e1a40250ed36

8d02db4dad1522baa10f9ca03f224dba

5fb1d8d515f9cf17102772a4bc023e78

46171ccf2302e01fa6cb0a97e081a885


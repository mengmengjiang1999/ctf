## **0x00 CALDERA是什么?**

 **CALDERA**
中文名被译为火山口，是一个由python语言编写的红蓝对抗工具（攻击模拟工具）。是MITRE公司的一个研究项目，该工具的攻击流程是建立在ATT&CK攻击行为模型和知识库之上的，接近于APT攻击行为模式。（根据v4.2版本的ATT&CK攻击行为模型，一共分为14个主要攻击流程。）

![image.png](https://image.3001.net/images/20210310/1615359111_60486c87609ca8e90d6e1.png!small)

图 1 CALDERA图标

![image.png](https://image.3001.net/images/20210310/1615359111_60486c87e2640db285eb7.png!small)

图 2 ATT&CK模型的14个主要流程

CALDERA可以手动 **模拟红队** 事先设定好攻击流程，进行自动化攻击和事件响应，同时也可以扮演蓝队根据相应的威胁做出应对手段。

  

##  **0x01 红队（Red Team）是什么？**

红队的说法起源于军事中，在战争中人们意识到，为了更好地防御，需要攻击自己的防御系统以发现薄弱点，然后可以更好地防御。从而逐渐地演变成“战争游戏”，也就是“红蓝对抗”。

红队的职责要尽可能模拟真实世界中收集政治、经济和科技情报的境外国家资助的黑客团伙等，红队测试某种程度上可以说是 **合法的高级持续性威胁**
(APT)。在这种完全贴近真实攻击的测试活动中，能够测试企业安全防护体系的阻断（prevention）、检测（detection）和响应（response）能力。

### 渗透测试和红队的区别

渗透测试中只关注给定目标系统的漏洞，红队测试则完全不一样。

红队在测试过程中关注的是如何规划一条攻击路径来达到目的。在整个红队测试过程中不一定要也不一定会发现目标组织的漏洞，只要能达到目的，任何形式的攻击手段都可以使用，包括但不限于web或者操作系统漏洞、社会工程学、物理渗透、攻击上下游合作供应商等。

如果说渗透测试是点到为止的话，那么红队测试就是不讲武德。

  

##  **0x02 CALDERA安装**

 **1\. 安装环境**

Kali Linux

Google Chrome浏览器

（建议使用kali系统进行安装,并事先安装好谷歌浏览器。）

 **2\. 源码下载**

  * 我们先从GitHub上的MITER官方CALDERA主页查看版本，可以看到当前最新版本是 **3.0.0**

<https://github.com/mitre/caldera>

![image.png](https://image.3001.net/images/20210310/1615359112_60486c88adddbf6135b5c.png!small)

图 3 GitHub上查看最新版本号

  * 在Kali上使用GitHub的克隆命令最后加上当前最新版本号。

git clone https://github.com/mitre/caldera.git --recursive --branch 3.0.0

![image.png](https://image.3001.net/images/20210310/1615359113_60486c893b233921d4713.png!small)

图 4 克隆GitHub源文件

  * 源码下载好后进入目录，安装框架所需模块。

cd cladera

pip3 install -r requirements.txt

![image.png](https://image.3001.net/images/20210310/1615359113_60486c89caa5e92dd7bed.png!small)

图 5 安装所需python模块

  * 启动CALDERA攻击模块。

python3 server.py --insecure

![image.png](https://image.3001.net/images/20210310/1615359116_60486c8c416d26f19cb5d.png!small)

图 6 启动CALDERA

  * 浏览器输入http://localhost:8888,如果能打开CALDERA登录页面，那么恭喜你，CALDERA的安装成功了。

![image.png](https://image.3001.net/images/20210310/1615359118_60486c8e49d096ea3de74.png!small)

图 7 连接CALDERA登录页面

##  **0x03 Campaigns/Agents模块**

靶机：Windows10专业版（IP：192.168.178.154）

 **1\. 登录**

有三个默认账户：

![image.png](https://image.3001.net/images/20210310/1615359118_60486c8eaea4528ea9616.png!small)

我们先以red用户作为演示。

 **2\. agents**

用户登录后点击左上角的 **Navigate(导航栏)** ，我们可以看到CALDERA的所有功能和模块。我们先来演示一下 **agents模块**
的用法。

![image.png](https://image.3001.net/images/20210310/1615359119_60486c8f1e498ce66b4fc.png!small)

图 8 Navigate

![image.png](https://image.3001.net/images/20210310/1615359119_60486c8fe5066a7ac33bd.png!small)

图 9 选择agents模块

打开模块后，先点击” **Clieck here to deploy an agent**
”(点击发送一个代理)，然后根据我们的需求选择payload类型和靶机的操作系统，如图，我选择的是 **54ndc47**
（sandcat）以及windows系统的 **payload** 。 **app.contact.http**
这一栏输入CALDERA服务端的IP和端口号（默认8888）。

![image.png](https://image.3001.net/images/20210310/1615359121_60486c919d61932f7d385.png!small)

图 10 生成Payload

在靶机上执行生成的powershell命令，建立代理链接。

![image.png](https://image.3001.net/images/20210310/1615359123_60486c938f5f9130e6a9d.png!small)

图 11 执行powershell命令

回到CALDERA的agents页面,可以看到一条新的链接建立（如果没有请刷新页面）。

![image.png](https://image.3001.net/images/20210310/1615359124_60486c9485c1d8c7e2f76.png!small)

图 12 建立连接

点击PID号可以查看该链接的详细信息。

![image.png](https://image.3001.net/images/20210310/1615359126_60486c96d2cd09b1346a4.png!small)

这些信息中包括了连接方式、主机名、用户名、用户权限、连接时间、处理器、操作系统、代理的运行程序等等。

下一章我们将继续深入CALDERA红队工具的使用，尽请期待。

  

 **免责声明** ：本文提及的技术仅可用于私人学习测试等合法场景中，任何不当利用该技术所造成的刑事、民事责任均与本文作者无关。


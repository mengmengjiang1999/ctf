一、Think介绍

Think是一款以网页浏览器为基础设计的远端桌面连接工具，不局限用户端使用那种作业平台，都可以通过采用HTML5为标准的浏览器来达到远端控制。通过利用最新的网络技术如AJAX，WebSockets和HTML5等，ThinVNC提供安全的，高性能的基于web的远程桌面访问。

二、漏洞描述

ThinVNC使用基本身份验证对用户进行身份验证以访问Web
VNC界面。部署VNC服务器时，将在服务器端设置要使用的凭据。没有运行VNC服务器的固定端口，当尝试使用错误的身份验证凭据进行多重验证时，它将引发HTTP
401错误。可以使用以下向量来绕开它：

/../../../../../../../../../windows/win.ini

此目录遍历攻击向量使我们可以读取系统上的任何文件。我们可以使用相同的向量来窃取VNC客户端的凭据。窃取它们后，我们可以使用凭据来破坏VNC服务器。随后，我们可以通过终端访问VNC服务器。

三、漏洞影响范围

ThinVNC 1.0b1

四、环境准备

操作系统| IP地址| 用途  
---|---|---  
Win7| 192.168.37.203| 靶机  
Win10 专业版| 192.168.37.193| 攻击机  
  
五、漏洞环境搭建

1、在靶机（Windows7）下载ThinVNC客户端。

下载地址：https://sourceforge.net/projects/thinvnc/

![1688628853_64a66e75a4ce2cb1fb594.png!small](https://image.3001.net/images/20230706/1688628853_64a66e75a4ce2cb1fb594.png!small)

2、解压ThinVNC到靶机，直接运行文件夹下的ThinVnc.exe文件，开启服务即可。

![1688628879_64a66e8f36334237649e1.png!small](https://image.3001.net/images/20230706/1688628879_64a66e8f36334237649e1.png!small)

服务开启后，根目录会生成配置文件，存储着VNC的明文登录凭证，结果如下图所示。

![1688628909_64a66ead5ddfe77fa21b2.png!small](https://image.3001.net/images/20230706/1688628909_64a66ead5ddfe77fa21b2.png!small)

六、漏洞验证

1、访问ThinVNC服务地址：http://192.168.37.203:8081/进入VNC登录界面，结果如下图所示。

![1688628948_64a66ed414ba6b296ecbe.png!small](https://image.3001.net/images/20230706/1688628948_64a66ed414ba6b296ecbe.png!small)

2、通过构造payload来读取ThinVNC配置文件，结果如下图所示。

![1688628985_64a66ef9e81ac4d55fdd5.png!small](https://image.3001.net/images/20230706/1688628985_64a66ef9e81ac4d55fdd5.png!small)

3、步骤2通过获取到的User=admin，Password=admin进行登录，结果如下图所示。

![1688629019_64a66f1b8342e23805eba.png!small](https://image.3001.net/images/20230706/1688629019_64a66f1b8342e23805eba.png!small)

七、防范建议

针对此漏洞，可通过以下防护措施进行漏洞防范。

1、禁止存储明文凭证；

2、切勿使用HTTP进行基本身份验证。


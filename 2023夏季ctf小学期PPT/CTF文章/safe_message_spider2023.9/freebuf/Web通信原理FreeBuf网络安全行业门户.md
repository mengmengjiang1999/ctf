## Web服务器通信原理

![1622596790_60b6dcb6aa7b74f369a83.png!small?1622596792210](https://image.3001.net/images/20210602/1622596790_60b6dcb6aa7b74f369a83.png!small?1622596792210)

### 一.基础知识介绍

 **常见的服务器系统:**

![1622545831_60b615a7b3ceb4ab1be6b.png!small?1622545830280](https://image.3001.net/images/20210601/1622545831_60b615a7b3ceb4ab1be6b.png!small?1622545830280)

 **Windows** 和 **Linux** 的区别:

    
    
    Windows的路径:C:\Windows\Help>  
    Linux的路径:/etc/init#

看到看到 **盘符** 一定是WINDOWS，看到 **/** 开头一般都是LIUNX( 拿macOS做系统很罕见)

 **绝对路径,相对路径**

> 绝对路径:文件在硬盘上真正存在的路径
>
>  
>
>
> 相对路径:自己相对与目标位置

 **CMD命令**

 **渗透测试** 常用的Cmd命令:

> dir 显示当前目录
>
> net user查看
>
> cd 跳转XX目录
>
> systeminfo 查看计算机信息
>
> ipconfig 查询自己的ip地址

 **网络知识方面**

 **IP** :内网IP和公网IP;

判断方法:(知道内网地址了,其他的就是公网地址)

>  **内网地址** 取值范围:
>
>  **A类** ：10.0.0.0-10.255.255.255
>
>  **B类** ：172.16.0.0-172.31.255.25
>
>  **C类** ：192.168.0.0-192.168.255.255

 **DNS(域名系统)** :

>  **域名** 实际上是为了方便记忆所发明的一个字符型标识
>
>  **DSN** 将域名转化为ip的一个协议  
>  **子域名** : 顶级域名、二级域名、三级域名.(几个点就是几级)

![1622551538_60b62bf2d9069ce839602.png!small?1622551537377](https://image.3001.net/images/20210601/1622551538_60b62bf2d9069ce839602.png!small?1622551537377)

 **端口(port)** :

> 每个端口对应不同的服务
>
>  **范围** 是从0 到65535（2^16-1）

![1622551744_60b62cc0695cf2f185f9b.png!small?1622551742877](https://image.3001.net/images/20210601/1622551744_60b62cc0695cf2f185f9b.png!small?1622551742877)

 **HTTP协议( **超文本传输协议** )**:

> 是互联网上应用最为广泛的一种网络协议
>
> 设计HTTP最初的目的是为了提供一种发布和接收HTML页面的方法,访问网站大都是用HTTP协议
    
    
     **HTTP数据包的简介** :  
    GET / HTTP/1.1                                   **#GET是请求方式  HTTP/1.1是协议版本** Host: node3.buuoj.cn:25028                       **#Host是访问的域名** User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36              # **告诉HTTP服务器， 客户端使用的操作系统和浏览器的名称和版本  
    ** Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9    **#浏览器端可以接受的媒体类型** Accept-Encoding: gzip, deflate                       # **浏览器申明自己接收的编码方法** Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7   **#浏览器申明自己接收的字符集**

###  

### 网页浏览的流程

 **访客角度分析** :

    
    
     **输入协议://域名访问== >DNS服务器找对应IP==>IP收到请求,进行处理返回结果给你==>浏览器将结果处理展示给你看**

> 一. 用户在浏览器输入协议://域名,
>
> 二. 用户浏览器通过系统 → 向DNS服务器查询域名对应的IP地址
>
> 三. 用户浏览器向查询到的IP地址(Web服务器)发起HTTP请求
>
> 四. 服务器分析用户请求，从中提取数据，处理后返回一个http响应
>
> 五. 浏览器收到响应后提取状态、协议编码、正文的有效信息，然后翻译成人类能够直观理解的图形界面并显示

###  

### Web容器:

> Web容器可以向发出请求的浏览器提供文档的程序。
>
> WEB容器是一种被动程序：只有其他计算机发出的请求该容器时，容器才会响应。
>
>
> Web容器的主要功能是存储，处理和传递网页给客户。客户端和服务器之间的通信使用超文本传输​​协议（HTTP）进行。交付的页面最常见的是HTML文档，除了文本内容之外，还可能包含图像，样式表和脚本。

![1622558048_60b6456062d2dee286c09.png!small?1622558046637](https://image.3001.net/images/20210601/1622558048_60b6456062d2dee286c09.png!small?1622558046637)

  

![1622558051_60b645633babf5c1f4a71.png!small?1622558049521](https://image.3001.net/images/20210601/1622558051_60b645633babf5c1f4a71.png!small?1622558049521)

 **Web容器** 的解析：

![1622604346_60b6fa3ad3b34015dc7bc.png!small?1622604349733](https://image.3001.net/images/20210602/1622604346_60b6fa3ad3b34015dc7bc.png!small?1622604349733)

## 快速自建web安全测试环境

### 什么是动态语言

 **动态语言** 是对 **服务器行为的编程** 。这被称为 **服务器端脚本或服务器脚本** 。

![1622604068_60b6f9244ce4ef47a9cbf.png!small?1622604068413](https://image.3001.net/images/20210602/1622604068_60b6f9244ce4ef47a9cbf.png!small?1622604068413)

 **常见的服务器脚本** :

    
    
    Asp,Aspx(windows);  
    PHP(全平台);  
    JSP(全平台)（java）  
    python(全平台)

动态语言 **能做什么** ：

> 1.动态地向 web 页面 **编辑、改变或添加** 任何的内容
>
> 2.对由 HTML 表单提交的用户请求或数据 **进行响应**
>
> 3. **访问** 数据或数据库，并向浏览器返回结果
>
> 4.为 **不同的用户** 定制页面
>
> 5.提高 **网页安全性** ，使您的网页代码不会通过浏览器被查看到

### 服务器环境的快速搭建

 **常见服务器** 快速搭建的软件:

>  **JSP(Tomcat)**
>
>  **PHP(PHPStudy)** **windows**
>
>  **PHP(lnmp) linux**
>
>  **宝塔、Lamp**

### PhPstudy功能介绍

PHPStudy使用说明教程:
[https://www.php.cn/phpstudy-377909.html﻿](https://www.php.cn/phpstudy-377909.html
"phpstudy使用说明教程")

### 快速搭建一个网站(通过CMS)

>  **CMS** 意为"内容管理系统",实际上就是一个 **快速建站的模板** ，常见的CMS有织梦、Dz论坛等
>
>  **获取CMS源码方式：** 可以去 **官方下载** 也可以去一些 **源码交流论坛** 还可以去 **github** 下载

 **织梦CMS** ：[http://www.dedecms.com/products/dedecms/downloads/
](http://www.dedecms.com/products/dedecms/downloads/ "织梦CMS")

> CMS源码解压后放入 **WWW目录** ，然后直接去访问 **upload文件夹** ，然后可以直接进入 **安装引导**
>
> 安装过程仅仅只需要你输入 **数据库密码** 就可以安装成功了
>
>  **install 文件夹**

![1622610443_60b7120b36e4506e29553.png!small?1622610443324](https://image.3001.net/images/20210602/1622610443_60b7120b36e4506e29553.png!small?1622610443324)


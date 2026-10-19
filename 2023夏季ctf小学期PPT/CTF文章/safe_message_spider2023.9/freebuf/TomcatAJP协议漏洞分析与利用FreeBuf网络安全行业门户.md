原创 合天网安实验室 合天智汇

## 0x01 漏洞基本信息  

漏洞名称：Tomcat AJP协议漏洞

CVE编号：CVE-2020-1938

漏洞简介：2020年2月4日，Apache
Tomcat官方发布了新的版本，该版本修复了一个影响所有版本（7.*、8.*、9.*）的文件包含漏洞，但官方暂未发布安全公告，2020年2月20日，CNVD发布了漏洞公告，对应漏洞编号：CNVD-2020-10487。漏洞是Tomcat
AJP协议存在缺陷而导致，攻击者利用漏洞可以构造特定参数，读取服务器webapp/ROOT下的任意文件。若目标服务器同时存在文件上传功能，攻击者可进一步通过文件包含实现远程代码执行。目前，厂商已发布新版本完成漏洞修复。

漏洞影响范围：

> Apache Tomcat 6Apache Tomcat 7 < 7.0.100Apache Tomcat 8 < 8.5.51Apache
> Tomcat 9 < 9.0.31  
>

## 0x02 漏洞起因  

以下内容来自：https://mp.weixin.qq.com/s/GzqLkwlIQi_i3AVIXn59FQ

tomcat默认的conf/server.xml中配置了2个Connector，一个为8080的对外提供的HTTP协议端口，另外一个就是默认的8009
AJP协议端口，两个端口默认均监听在外网ip，如下图所示：

![v2-5923e02d5621ea55ae9b2b2294d7d106_hd.j](https://pic4.zhimg.com/80/v2-5923e02d5621ea55ae9b2b2294d7d106_hd.jpg)

当tomcat服务启动后，查看端口可以发现8009端口已经处于监听状态：

![v2-b6cc5dc8934e6710f7516c352444df2e_hd.j](https://pic1.zhimg.com/80/v2-b6cc5dc8934e6710f7516c352444df2e_hd.jpg)

tomcat在接收ajp请求的时候会调用org.apache.coyote.ajp.AjpProcessor来处理ajp消息，prepareRequest将ajp里面的内容取出来设置成request对象的Attribute属性，如下图：

![v2-113674c17c2ce434e01e41fa1182c17d_hd.j](https://pic3.zhimg.com/80/v2-113674c17c2ce434e01e41fa1182c17d_hd.jpg)

因此可以通过这种特性，控制request对象的以下三个Attribute属性：

javax.servlet.include.request_uri

javax.servlet.include.path_info

javax.servlet.include.servlet_path

然后封装成对应的request之后,继续走servlet的映射流程，如下图所示:

![v2-c88beef5374ee1470df261596d95b1ff_hd.j](https://pic1.zhimg.com/80/v2-c88beef5374ee1470df261596d95b1ff_hd.jpg)

具体的映射方式这里就不介绍了。

## 0x03 漏洞利用方式  

1、利用DefaultServlet实现任意文件下载

当url请求未在映射的url列表里面，会通过tomcat默认的DefaultServlet，根据上面的三个属性来读取文件,如下图所示:

![v2-abfacd593eafec5645b2***3d5151bdc_hd.j](https://pic1.zhimg.com/80/v2-abfacd593eafec5645b2***3d5151bdc_hd.jpg)

通过serveResource方法来获取资源文件：

![v2-***bf04730b150413d8fd51ad5c5a32a_hd.j](https://pic3.zhimg.com/80/v2-***bf04730b150413d8fd51ad5c5a32a_hd.jpg)

通过getRelativePath来获取资源文件路径：

![v2-b5570c667b5189cd3c0cbbd32970ef69_hd.j](https://pic1.zhimg.com/80/v2-b5570c667b5189cd3c0cbbd32970ef69_hd.jpg)

然后通过控制ajp控制的上述三个属性来读取文件,操控上述三个属性，从而可以读取到/WEB-INF下面的所有敏感文件，不限于class、xml、jar等文件。

2、通过jspservlet实现任意后缀文件包含

当url（比如http://xxx/xxx/xxx.jsp）请求映射在org.apache.jasper.servlet.JspServlet这个servlet的时候，也可以通过上述三个属性来控制访问的jsp文件,如下图所示:

![v2-5ba9c2d88c9435e41ccfef6951dc8123_hd.j](https://pic4.zhimg.com/80/v2-5ba9c2d88c9435e41ccfef6951dc8123_hd.jpg)

控制路径之后就能以jsp解析该文件，所以只需要一个内容可控的文件即可实现rce。

## 0x04 AJP协议规范  

参考https://tomcat.apache.org/connectors-doc/ajp/ajpv13a.html

## 0x05 漏洞利用环境  

靶机：centos7+tomcat8.5.30

攻击机：win7+python3

## 0x06 漏洞利用过程  

1、Tomcat版本检测

通常在Apache Tomcat官网下载的安装包名称中，会包含当前Tomcat的版本号，用户可通过查看解压后的文件夹名称，来确定当前的版本。比如：

![v2-ed551973c539b288ff8830b15d607cce_hd.j](https://pic1.zhimg.com/80/v2-ed551973c539b288ff8830b15d607cce_hd.jpg)

如果解压后的Tomcat目录名称被修改过，或者通过Windows Service
Installer方式安装，使用软件自带的version模块来获取当前的版本。进入Tomcat安装目录的bin目录，输入命令./version.sh后，可查看当前的软件版本号：

![v2-ccc32d4d17457d8c6fa1d87fedfefdf7_hd.j](https://pic1.zhimg.com/80/v2-ccc32d4d17457d8c6fa1d87fedfefdf7_hd.jpg)

2、通过python脚本文件读取及文件包含进行RCE

公众号回复关键词 文件读取获取脚本地址

用法：

python3 2020-10487.py 172.26.1.182 -f WEB-INF/web.xml

![v2-3962c2c015c46f680cb1c9b1aafe6991_hd.j](https://pic3.zhimg.com/80/v2-3962c2c015c46f680cb1c9b1aafe6991_hd.jpg)

可以看到成功读取到了ROOT/WEB-INF下的web.xml文件（如果ROOT下存放了网站的源代码，就会被不法分子通过读取该源码，然后进行代码审计，导致其他漏洞的发生），web.xml文件：

![v2-dc9b733dc09f36476fbfe8561b763dd4_hd.j](https://pic2.zhimg.com/80/v2-dc9b733dc09f36476fbfe8561b763dd4_hd.jpg)

文件包含进行RCE（实际环境中需要有上传点）：

因为是实验环境，并没有上传点，所以我们已经在webapp/ROOT下存放了一个名为exec.txt的文件，来模拟文件上传后的文件，然后包含该文件即可进行RCE。

exec.txt内容为执行“whoami”代码：

<%out.println(new java.io.BufferedReader(new
java.io.InputStreamReader(Runtime.getRuntime().exec("whoami").getInputStream())).readLine());%>

用法：python3 CVE-2020-1938.py 172.26.1.182 -f exec.txt --rce 1

![v2-c365b969566a5a1fd8ca307ac220195b_hd.j](https://pic2.zhimg.com/80/v2-c365b969566a5a1fd8ca307ac220195b_hd.jpg)

## 0x07 漏洞修复建议  

1、临时禁用AJP协议端口：在conf/server.xml配置文件中注释掉117行的<Connector port="8009"
protocol="AJP/1.3"redirectPort="8443" /> ，然后重启服务器。

![v2-d3a146906b518ab860470a7f5256c956_hd.j](https://pic3.zhimg.com/80/v2-d3a146906b518ab860470a7f5256c956_hd.jpg)

再次进行文件读取就会抛出异常，修复成功：

![v2-0d2f0564d07256bc2cddab74e0db8794_hd.j](https://pic1.zhimg.com/80/v2-0d2f0564d07256bc2cddab74e0db8794_hd.jpg)

2、下载官方最新版：

<https://tomcat.apache.org/download-70.cgi>

<https://tomcat.apache.org/download-80.cgi>

<https://tomcat.apache.org/download-90.cgi>

合天网安实验室已经上新了【Tomcat AJP协议漏洞】实验，快访问下面的链接学习吧！

[实验:Tomcat
AJP协议漏洞(合天网安实验室)](http://www.hetianlab.com/expc.do?w=exp_ass&ec=ECID85eb-b142-4c98-a8ad-c926f1986c40)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  


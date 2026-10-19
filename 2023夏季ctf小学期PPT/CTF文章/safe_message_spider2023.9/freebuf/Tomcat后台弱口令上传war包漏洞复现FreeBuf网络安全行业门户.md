原创： free雅轩  合天智汇

  
  

近期在项目中碰到的ApacheTomcat中间件愈来愈多，于是乎。想着做一个整理。将ApacheTomcat中间件的几大较为重要的高危漏洞做一个总结整理复现。用作来巩固更新自己的知识库。

在这里感谢公司Bearcat师傅和残忆师傅以及李师傅等指导和共享精神。

首先我们先来了解以下Tomcat的概念：

Tomcat是我们在工作中所使用的一款开源轻量级的Web应用程序服务器。通常情况下在中小型系统或者并发量较小的场合下使用，常用来与JSP脚本结合使来解析脚本语言部署搭建网站等系统。

在这里我们将Tomcat的几大高危漏洞整理至以下：

1、Tomcat后台弱口令上传war包

2、Tomcat的PUT的上传漏洞(CVE-2017-12615)

3、Tomcat反序列化漏洞(CVE-2016-8735)

4、Tomcat JMX服务器弱口令

5、Tomcat 样例目录session操控漏洞

6、Tomcat本地提权漏洞(CVE-2016-1240)

7Tomcat win版默认空口令漏洞(CVE-2009-3548)

在这里解释一下War包的概念：war包是用来进行Web开发时一个网站项目下的所有代码,包括前台HTML/CSS/JS代码,以及后台JavaWeb的代码。当开发人员开发完毕时,就会将源码打包给测试人员测试,测试完后若要发布则也会打包成War包进行发布。War包可以放在Tomcat下的webapps或word目录,当Tomcat服务器启动时，War包即会随之解压源代码来进行自动部署。

先来看第一个Tomcat后台弱口令上传war包。在这里我们就是利用暴力破解或者弱口令猜解的方式得到tomcat的后台登陆认证账户，即在登陆成功之时利用tomcat管理控制台WARfile
to deploy

自动部署war的功能将我们的木马进行上传部署。在这里我们本地给大家准备的实验环境如下：

 **JDK1.8.0**

ApacheTomcat7.0.88(关于爆破本来应该使用6版本，不过为了总结更多关于防御的知识，所以这里我使用7版本的)

在这里jdk以及tomcat的安装配置我就不细讲了。大家可以自行百度。准备好如下图所示的实现环境后，接下来我们来开始复现操作。

![图片.png](https://image.3001.net/images/20181010/1539142747_5bbd745b463e5.png!small)

在这里我们设置一个8090的本地代理端口，以防止和tomcat默认的本地8080端口所冲突造成不必要的影响。

我们随便输入12345账户密码来进行爆破。

  
![图片.png](https://image.3001.net/images/20181010/1539142756_5bbd74642adae.png!small)  

  
![图片.png](https://image.3001.net/images/20181010/1539142765_5bbd746d8b11e.png!small)  

得到账户密码是利用Authorization该授权字段以base64方式传递账户信息。

得到他的加密方式，接下来我们拿去解密分析他的数据传递方法。

  
![图片.png](https://image.3001.net/images/20181010/1539142775_5bbd7477325d4.png!small)  

可以得出tomcat在授权认证时，将账号与密码用冒号进行组合再辅以base64加密所传递。接下来我们构造字典来进行爆破。

利用burp抓包发送到Intrude模糊测试模块来进行暴力破解。

![图片.png](https://image.3001.net/images/20181010/1539142783_5bbd747f4d11e.png!small)  

上面我们得到了tomcat数据传递格式为username：password的格式，这是就要使用到burp模糊测试模块中的customiterator自定义迭代类型的payload，官方的解释是该类型的payload共分为8个占位符，每一个占位又可以指定简单列表的payload类型。再根据占位的数值，与每一个payload列表区进行笛卡儿积生成集合组。

得到最终的payload列表。我的理解就是利用数学中的笛卡儿积进行集合，去拼凑各种可能存在的payload可能列表。设置格式如下：

![图片.png](https://image.3001.net/images/20181010/1539142792_5bbd7488ca4c5.png!small)  

按照payload类型分组进行设置Position参数，比如说我们要爆破的Tomcat数据。需要设置的第一个Position参数就是username参数，然后再进行添加payload字典。以此类推第二个参数就是冒号：，第三个就是password字段。设置完成后再需要对数据字段进行base64编码就可以爆破了。设置方法如下图所示：

  
![图片.png](https://image.3001.net/images/20181010/1539142800_5bbd7490719bc.png!small)  

以上就收tomcat基础认证爆破，当然我们还可以去自己收集匹配号的三个字段字典或者base64加密过的字典以及metasploit中的tomcat爆破，更加方便进行爆破。方式多样，根据自己的需求去使用。

爆破很多次，发现正确的用户名密码字典爆破出来一直是失败的401状态码。我们可以在tomcat的后台jar脚本文件中发现一串警告信息。

![图片.png](https://image.3001.net/images/20181010/1539142808_5bbd749831a4e.png!small)  

这是由于在tomcat6版本以后针对爆破做了锁定机制的设置。我们先去更改一下。为了方便演示。

在conf/server.xml中添加一段failureCount="500"lockOutTime="0"超时锁定数的设置。

![图片.png](https://image.3001.net/images/20181010/1539142815_5bbd749fab762.png!small)  

即可解除针对爆破次数过多的用户的锁定机制。爆破成功之后来到Tomcat后台即可部署我们的war木马文件来进行提权操作。

![图片.png](https://image.3001.net/images/20181010/1539142823_5bbd74a77206d.png!small)  

  
![图片.png](https://image.3001.net/images/20181010/1539142830_5bbd74aeacfcf.png!small)  

Tomcat后台弱口令上传war包进行getshell的篇幅到此为止。

修复方案：

1、在系统上以低权限运行Tomcat应用程序。创建一个专门的 Tomcat服务用户，该用户只能拥有一组最小权限（例如不允许远程登录）。

2、增加对于本地和基于证书的身份验证，部署账户锁定机制（对于集中式认证，目录服务也要做相应配置）。在CATALINA_HOME/conf/web.xml文件设置锁定机制和时间超时限制。

3、以及针对manager-gui/manager-status/manager-script等目录页面设置最小权限访问限制。

  


## 一：漏洞简介

Spring Cloud
Config为分布式系统的外部配置提供客户端的服务端的支持。使用了它，开发人员就可以在一个中心仓库管理应用程序在所有环境中的外部配置。2020-02-26
Spring 收到漏洞报告, Spring Cloud Config Server
存在目录穿越漏洞。在配置仓库为本地native的情况下，攻击者可以获取config-server服务器上的任意带后缀文件。

## 二：利用条件

修改配置文件src/main/resources/configserver.yml

主要是设置profiles.active为native，设置search-locations为任意文件夹。

## 三：影响版本

2.2.x prior to 2.2.2

2.1.x prior to 2.1.7

## 四：漏洞复现

从github下载spring-cloud-config模块：https://github.com/spring-cloud/spring-cloud-config/archive/v2.1.5.RELEASE.zip

导入IDEA其中的spring-cloud-config-server模块，Maven+SpringBoot项目

修改配置文件src/main/resources/configserver.yml

主要是设置profiles.active为native

设置search-locations为任意文件夹

![image](https://image.3001.net/images/20220321/1647849486_6238300e48fcd26e2238a.png!small)

然后从ConfigServerApplication类启动，访问localhost:8888

然后在上方设置的search-locations路径下随便创建一个文件，写点东西，然后尝试读取这个文件

Payload：

**http://127.0.0.1:8888/1/1/..()..()..()..()..()..()..()..()..(_)Code/key.txt**

[
**http://127.0.0.1:8888/1/1/..%28_%29..%28_%29..%28_%29..%28_%29..%28_%29..%28_%29..%28_%29..%28_%29Code/key.txt**](http://127.0.0.1:8888/1/1/..\(_\)..\(_\)..\(_\)..\(_\)..\(_\)..\(_\)..\(_\)..\(_\)Code/key.txt)

访问后成功读取：

![image](https://image.3001.net/images/20220321/1647849502_6238301e5045b5a283da4.png!small)

## 五：漏洞分析

Config Server通过路径/{name}/{profile}/{label}/{path}对外提供配置文件，POC会通过路由到这个接口

然后我们先看下org\springframework\cloud\config\server\resource\ResourceController.java

![image](https://image.3001.net/images/20220321/1647849513_623830294bbf8c77c721a.png!small)

传入的参数代表的意思如下：

name：仓库名称

profile：配置文件环境（dev,test,pro）

label：分支（1.0.0）

**：通配子目录

通过断点调试我们可以看到name、profile、label的值

![image](https://image.3001.net/images/20220321/1647849526_62383036856d933c13131.png!small)

没看到path的值，这里path的值是通过getFilePath方法解析之后得到的，跟进getFilePath

![image](https://image.3001.net/images/20220321/1647849537_62383041949cec29388ec.png!small)

可以看到getFilePath方法中将path解析成了我们的文件名，然后通过format方法拼接了我们传入的参数，然后return path的值，继续往下

![image](https://image.3001.net/images/20220321/1647849549_6238304d0805870436a5a.png!small)

可以看到getFilePath方法的值会传入retrieve方法，跟进

![image](https://image.3001.net/images/20220321/1647849558_62383056e28589f5b6c01.png!small)

可以看到retrieve方法中将name和label传入了resolveName和resolveLabel，我们跟进看看

![image](https://image.3001.net/images/20220321/1647849568_623830603fb7965508943.png!small)

resolveName方法的作用是将(_)替换成/ ，但是条件不满足，返回

![image](https://image.3001.net/images/20220321/1647849580_6238306c310d949aee8e9.png!small)

resolveLabel方法也是将(_)替换成 / 并且条件满足，所以我们的数据被替换成了 ../../../../../../../../../Code

继续往下，程序执行到findOne方法，跟进看看

![image](https://image.3001.net/images/20220321/1647849591_6238307721ea8a911e7cf.png!small)

![image](https://image.3001.net/images/20220321/1647849599_6238307f79cf55127f195.png!small)

进入到findOne方法中，可以看到这个方法中this.service.getLocations应该是调用配置文件（也就是我们之前配置的那个），然后跟我们传入的参数重新拼接，得到两个路径：

![image](https://image.3001.net/images/20220321/1647849609_62383089e3ec80ec08f68.png!small)

![image](https://image.3001.net/images/20220321/1647849619_623830934f6259ddf22a1.png!small)

后边的getProfilePaths方法是根据profile构造文件路径，最后得到我们传入的值。

在下边我们看到程序做了非法路径的判断，但是是针对path的，而我们的payload是在label中：

![image](https://image.3001.net/images/20220321/1647849637_623830a5328db7fb007d7.png!small)

最后我们成功读取了文件

## 六：参考链接

> https://4ra1n.love/post/hwsaMZANl
>
> https://www.freebuf.com/news/232744.html


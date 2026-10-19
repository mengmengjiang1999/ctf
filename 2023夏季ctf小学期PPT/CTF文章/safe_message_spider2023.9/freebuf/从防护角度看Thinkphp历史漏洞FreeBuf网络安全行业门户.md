## 一、前言  

**19年初，网上公开了2个Thinkphp5的RCE漏洞，漏洞非常好用，导致有很多攻击者用扫描器进行全网扫描。我们通过ips设备持续观察到大量利用这几个漏洞进行批量getshell的攻击流量，本文主要从流量角度简要分析和利用thinkphp进行攻击的全网扫描和getshell流量痕迹。**

##  二、Thinkphp RCE漏洞和扫描流量

###  2.1漏洞原理回顾

**2.1.15.0.x版本漏洞**

原理在于Thinkphp处理请求的关键类为Request(thinkphp/library/think/Request.php)，该类可以实现对HTTP请求的一些设置

Thinkphp支持配置“表单伪装变量”，默认情况下该变量值为_method，因此在method()中，可以通过“表单伪装变量”进行变量覆盖实现对该类任意函数的调用，并且$_POST作为函数的参数传入。可以构造请求来实现对Request类属性值的覆盖，例如覆盖filter属性（filter属性保存了用于全局过滤的函数），从而实现代码执行。

**2.1.25.1.x-5.2.x版本漏洞**

与5.0.x版本漏洞相似，漏洞点都存在于Request(thinkphp/library/think/Request.php)类中，其中：

![image.png](https://image.3001.net/images/20200303/15832310018623.png!small)$method变量是$this->method，其等同于POST的“_method”参数值，可以利用覆盖$filter的属性值（filter属性保存了用于全局过滤的函数），从而实现代码执行。

该漏洞触发时会出现警告级别的异常导致程序终止，此时需要设置忽略异常提示，在public/index.php中配置error_reporting(0)忽略异常继续运行代码，如下图：

![image.png](https://image.3001.net/images/20200303/15832310195938.png!small)

###  2.2Thinkphp漏洞全网扫描

从流量角度来看，利用Thinkphp漏洞就是发一个http包。我们发现某黑客的扫描器是先写一个简单的一句话作为指纹，后续再访问这个文件看是否返回指纹信息，访问成功说明shell已经成功，基本就是发两个http包，扫描器记下成功写入的shell的网站ip和url然后手工用菜刀连接，进行后续操作。

从IPS设备日志和人工验证，攻击者的攻击步骤包含2步：1、全网扫描发送exp，根据指纹识别是否getshell；2、菜刀连接，进行远程控制；

 **2.2.1全网扫描发送exp**

一般扫描日志都是遍历B段或C段，时间也比较密集，某个被记录的扫描器日志片段如下，

![image.png](https://image.3001.net/images/20200303/15832310554287.png!small)具备3个特征：1、目的ip为相同C段或者B段，2、端口比较固定，3扫描时间非常密集

扫描器发送的确认shell已经写入成功的报文，采用扫描器专用的指纹，所以ips是没有这种检测规则的。

 **2.2.2菜刀连接**

在攻击者手工菜刀连接被攻陷的站点时，也会被ips检测到，通过上下文关联溯源到thinkphp漏洞作为攻击者的突破口。挑选几个当时记录的典型案例：

**被攻陷的郑州服务器1** **（122.114.24.216** **）：**

![image.png](https://image.3001.net/images/20200303/15832310772908.png!small)该网站确实为thinkphp5发开，当时webshell木马还在服务器上未被删除。可以通过服务器访问黑客上传的该木马，指纹信息为baidu，扫描器用这个指纹来自动判断getshell成功并记录url。

![image.png](https://image.3001.net/images/20200303/15832312201119.png!small)**被攻陷的四川服务器（182.151.214.106**
**）：**

**被攻陷的四川服务器（182.151.214.106** **）：**

这个案例木马虽然被清除，但是当时服务器还是可以连通，服务器也是thinkphp框架，用户名疑似chanpei

![image.png](https://image.3001.net/images/20200303/15832312578585.png!small)设备记录了黑客连接木马并执行网络查询命令时的报文，得到的信息与以上报错信息一致。并且看得出服务器也所处为内网的一台机器，截图看到至少该网络包含192.168.9.0和192.168.56.0两个子网，如下图：

![image.png](https://image.3001.net/images/20200303/15832312691583.png!small)**被攻陷的美国服务器（161.129.41.36**
**）：**

美国这台服务器上的webshell也被清理掉了，通过设备抓包，发现有黑客使用了相同的webshell木马，即 x.php，怀疑是同一批黑客。

![image.png](https://image.3001.net/images/20200303/1583231282920.png!small)黑客在浏览美国服务器上x.php（webshell）文件内容时，设备记录了x.php的密码为xiao，并且标志位也是baidu。

![image.png](https://image.3001.net/images/20200303/15832312931618.png!small)可以看出利用这两个Thinkphp高危RCE漏洞，当时是扫到了大量的服务器漏洞的。

##  三、总结

本文结合Thinkphp的历史漏洞原理，分享了发现利用Thinkphp漏洞攻击成功的案例。目前设备每天检测到最多的日志就是weblogic、struts2、thinkphp这类直接getshell的日志或者ssh
rdp暴力破解日志。很多攻击者一旦发现最新的exp就装备到自己的扫描器上面全网一阵扫，一天下来可能就是若干个shell。所以出现高危漏洞后建议用户及时打上补丁，配置好安全设备策略，从实际几个案例来看，扫描器的风险一直都在。如果能配置好网站禁止ip直接访问，能在某种程度上缓解一下这种威胁。由于水平有限，欢迎大家指出文中的错误和交流指教

 **参考资料：**

> <https://xz.aliyun.com/t/3629>
>
> [https://www.freebuf.com](https://www.freebuf.com/)

***本文作者：新华三攻防团队，转载请注明来自FreeBuf.COM**


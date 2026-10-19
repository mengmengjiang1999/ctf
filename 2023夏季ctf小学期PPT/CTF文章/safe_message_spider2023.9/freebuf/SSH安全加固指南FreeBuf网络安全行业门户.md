本文翻译自：<https://www.putorius.net/how-to-secure-ssh-daemon.html>

SSH（Secure
Shell）是一种能够让用户安全访问远程系统的网络协议，它为不安全网络中的两台主机提供了一个强加密数据通信通道。SSH是Linux、UNIX系统管理员操作和管理主机的首选方式。虽然SSH比其他通信方式更加安全，但是错误的配置也可能导致其出现安全问题。这篇文章的目的就是提供一个帮助你加固SSH的指南。

这篇指南将涉及到很多选项，但这些选项并不适合所有的服务器，只有你自己了解自己的环境配置、用户基础以及数据的重要性，因此到底哪些配置适合于你的系统，完全取决于你、你公司的安全策略或者是你组织内的某些人。

## 写在前面

以下内容适用于本指南，除非另有说明

  * 本文所编辑的SSH配置文件指的是`sshd_config`文件，而不是`ssh_config`（注意`ssh`后面的有个`d`）。

  * 任何对SSH配置的修改都需要重启服务后生效。

  * 我们所要讨论的绝大多数选项已经写在`sshd_config`文件中了，在进行配置前最好确认是否已经设置了该选项，盲目设置将会导致冲突。

  * SSH配置文件中有许多带有注释的行（注释以`#`开头），注释掉的选项将不会在服务中启用，若要使其生效，需要删除前面的`#`。

  * 注释通常显示为该选项的默认值。

## 仅使用SSHv2 协议

SSHv1是已知的对于SSH协议的不安全实现，为了确保系统的完整性，应当将SSH服务配置为仅接受SSHv2连接。

通过取消以下行配置的注释，来配置SSH服务仅接受SSHv2协议。

    
    
    Protocol 2

备注：RedHat和CentOS在7.4版本之后使用SSHv2作为默认配置，但是“我”仍喜欢将该行写入配置文件。

## 关闭或者延迟压缩

SSH可以使用gzip算法压缩数据，如果压缩软件中存在漏洞，就可能影响到系统。

关于在快速连接上是否需要启用压缩，已经进行了很多讨论，普遍认为压缩实际上会减慢处理速度，除非你使用慢速连接（调制解调器、ISDN等）。如果必须使用压缩功能，请使用延迟功能来确保在压缩开始前对用户进行身份验证。

关闭压缩功能（推荐）：

    
    
    Compression no

要将压缩延迟到身份认证后，则需要修改为：

    
    
    Compression delayed

> 这里的“快速连接”和“慢速连接”没太理解，原文为“fast connections”、“slow
> connection”，可能指的就是通信信道的传输速率吧。

## 限制身份验证最大尝试次数

限制用户失败认证的最大次数是一个缓解暴力攻击的好方法。将`MaxAuthTries`设置为比较小的数字（x），将会在用户x次失败尝试后强制断开会话。

限制最大身份验证尝试次数，请修改`sshd_config`中的配置为如下：

    
    
    MaxAuthTries 3

You can set this number as low as you like, but 3 is a good balance between
security and convenience in my opinion.

你可以任意调低这个数字，但是我认为“3”是在安全和便利之间较为平衡的设置。

## 禁用root账户登录

如果你允许root用户登录，则不能将操作关联到用户，强制用户使用特定于用户的账户登录可以确保问责机制。此外，这样设置还可以进一步保护root账户免受其他类型的攻击。

阻止用户使用root账户登录，请修改配置如下：

    
    
    PermitRootLogin no

强烈建议使用此配置。

## 显示最后一次登录的日期和时间

这通常是现代系统中的默认设置，但是检查其是否正确配置仍然很重要。通过打印最后一次登录的日期和时间，用户可以意识到未经授权的账户登录事件，这将对进一步调查无法识别的访问提供帮助。

输出最后一次登录日期和时间，请修改配置如下：

    
    
    PrintLastLog yes

这是条安全的捷径。

## 结束空闲的SSH会话

无限期地将SSH会话保持打开状态不是一个好主意，因为用户可能离开他们的工作站，这给了一个未授权用户在无人看管的工作站上执行命令的好机会。最好的办法是在短时间内终止空闲的SSH会话，不给他人留机会。

`ClientAliveCountMax`选项和`ClientAliveInterval`选项相互配合，例如要在十五分钟 **（900秒）**
后关闭不活动的会话，修改配置文件如下：

    
    
    ClientAliveInterval 900  
    ClientAliveCountMax 0

更多有关`ClientAliveInterval`的说明：

> 设置超时间隔（以 **秒**
> 为单位），在此间隔后，如果未从客户端接收到任何数据，sshd服务端将通过加密的通道发送消息请求客户端回应。默认值为0，表示不会执行该操作。

更多有关`ClientAliveCountMax`的说明：

> 设置客户端探活消息（上文所述操作）的数量，如果发送客户端探活消息达到此阈值，则sshd服务端将断开客户端连接，从而终止会话。

指定白名单用户

你可以通过白名单指定那些经过授权的用户来连接SSH服务器，只有在这个列表中的用户才有权登录SSH，其他人则不行。这样做好处多多。

若 **仅** 允许 "pfloyd"、 "rwaters"和 "dgilmour"这三个 用户的话，修改配置文件如下：

    
    
    AllowUsers pfloyd rwaters dgilmour

你同样可以使用`DenyUsers`来禁止某些用户，比如这样修改配置文件：

    
    
    DenyUsers root ncarter ajmclean hdorough

这个设置并不是总是可用的，如果你的环境可以支持此配置，那肯定会提高安全性的。

## 禁用空密码

确保任何SSH连接都需要一个非空的密码字符串（这并不会影响SSH密钥认证登录模式）。

修改配置文件如下：

    
    
    PermitEmptyPasswords no

这是另一个简单却重要的配置，建议对所有非特殊情况下使用。

如果你使用密码认证，实施密码复杂性规则是一个明智的选择。这些规则可以是由你的组织制定，或者尝试以下“最佳实践”：

  * 密码长度大于x

  * 密码至少包含x个小写字符

  * 密码至少包含x个大写字符

  * 密码至少包含x个数字

  * 密码至少包含x个特殊字符

  * 密码不得包含用户名（正向或者反向）

想要了解更多有关设置密码复杂性的信息，可以参看[《如何在RedHat中强制设置密码复杂性》](https://putorius.net/forcing-password-complexity-in-red-hat.html)，虽然这篇文章针对RedHat的，但是它可以在任何使用最新版的PAM（可插拔身份验证模块）的Linux系统上运行。

## 禁用基于受信主机的无密码登录

`rhosts`文件是一种控制系统间信任的关系的方法，如果一个系统信任另一个系统，则这个系统不需要密码就允许来自受信认系统的登录。这是一个老旧的配置，应当在SSH配置中明确禁用。

确保SSH不允许受信主机连接，请修改配置文件如下：

    
    
    IgnoreRhosts yes

`rhosts`文件已经很少使用了，建议在多数情况下启用该配置。

## 禁用基于已知主机的访问

`known_hosts`文件用于标识服务器，当用户启动SSH连接时，SSH会将服务器指纹与`known_hosts`文件中存储的指纹进行比较，来确保用户连接到的是正确的系统。这个配置与`rhosts`配置相互配合，确保与远程主机连接时需要密码（通过设置该选项，来保证每一次连接都将远程主机视为“非信任”主机）。

在身份验证时忽略已知主机，请修改配置文件如下：

    
    
    IgnoreUserKnownHosts yes

这个配置适用于绝大多数环境。

## 禁用基于主机的身份认证

这个功能类似于基于受信主机的认证，但是仅用于SSH-2，在我的经验里这个功能很少使用，应当设置为`no`。

禁用基于基于主机的身份认证，请修改配置文件如下：

    
    
    HostBasedAuthentication no

这个选项默认情况下设置为`no`，但是为了保险起见，我将其显式添加到配置文件中。

## 禁用X11Forwarding

X11Forwarding允许通过SSH会话远程执行程序，并在客户端显式图形界面。如果没有特殊需求，则应将其禁用。

禁用X11Forwarding，请修改配置文件如下：

    
    
    X11Forwarding no

X11Forwarding很少使用，我建议在大多数系统上禁用该功能。

## 使用非常规端口

默认情况下，SSH监听在TCP 22
端口，黑客和脚本小子经常对这个端口进行扫描，来判断目标是否运行SSH，另外2222和2121也是常用的监听端口，最好不要使用这些端口，请使用不常见的高端端口，例如示例中的9222端口。

设置SSH监听在非常规端口，请修改配置文件如下；

    
    
    Port 9222

我通常不修改位于防火墙后面的那些默认端口，但是如果您的主机暴露在互联网或者其他不受信任的网络中，这样的设置是必要的。

注意：不要忘记更改防火墙规则，允许流量访问你自定义的端口。

## 将服务绑定到指定IP

默认情况下，SSH会监听本机上配置的所有IP地址，但是你应该指定SSH绑定在特定的IP，最好是在专用VLAN中的地址。

指定绑定地址，请修改配置文件如下

    
    
    ListenAddress 10.0.0.5

这个设置通常与端口绑定相互配合。

## 保护SSH密钥

### 保护主机私钥

你应该保护主机私钥防止未授权的访问，如果私钥泄露，则主机可能会被假冒，因此所有的私钥文件都应设置为仅允许root用户访问（对应权限为0600）。

使用`ls`命令列出`/etc/ssh/`文件夹下所有的私钥文件：

    
    
    ls -l /etc/ssh/*key

使用`chmod`命令设置私钥文件权限：

    
    
    chmod 0600 /etc/ssh/*key

大多数情况下，私钥文件存储在`/etc/ssh/`文件夹下，但是也有可能存储在其他目录中，通过以下命令可以检索配置文件中设置的存储位置：

    
    
    grep -i hostkey /etc/ssh/sshd_config

### 保护主机公钥

虽然公钥不如私钥那么重要，但你还是应该对其进行保护，因为如果公钥被篡改，则可能会使SSH服务无法正常工作或者拒绝服务，因此需要配置权限仅允许root账户对其进行修改（对应权限为0644）。

使用`ls`命令列出`/etc/ssh/`目录下所有的公钥文件：

    
    
    ls -l /etc/ssh/*pub

使用`chmod`命令修改公钥文件权限：

    
    
    chmod 0644 /etc/ssh/*pub

通常情况下公钥和私钥存放在同一目录下，或者使用上一节的方法查找存放路径。

## 检查用户特定的配置文件

用户可能会在无意间将自己的home目录或者其他某些文件设置成全局可写（比如777权限），在这种情况下，其他用户将有权修改用户特定的配置，并以其他用户的身份登录到服务器。可以通过使用`StrictModes`选项来检查home目录的配置。

>
> `StrictModes`设置ssh在接收登录之前是否检查用户home目录和rhosts文件的权限和所有权，`StrictModes`为yes必需保证存放公钥的文件夹的拥有者与登陆用户名是相同的。

确保启用严格模式，请修改配置文件如下：

    
    
    StrictModes yes

建议使用此方法，尤其是对于有大量用户的系统。

## 防止特权升级

SSH通过创建一个无特权的子进程来接收传入的连接，实现权限分离。用户身份验证后，SSH将使用该用户的权限创建另一个进程。

在我所了解的系统中，这个选项默认都是开启的，但是为了保险起见，建议还是手动修改配置文件，显式指定该配置：

    
    
    UsePrivilegeSeparation sandbox

使用`sandbox`可以增加其他限制。

## 使用密钥进行身份验证

该功能并不一定在所有系统上都可用，但是使用SSH密钥身份验证有很多优点。密钥验证比人类可以轻松记住的任何密码都要强大的多，同时还提供了无需密码的身份验证，使用更加便利。

启用密钥身份验证，请修改配置文件如下：

    
    
    PubkeyAuthentication yes

该选项在大多数系统上默认为`yes`。

更多有关SSH密钥身份验证的信息，请参考 [How to Setup SSH Key
Authentication](https://putorius.net/how-to-setup-ssh-key-authenitication.html)。

## 禁用不使用的身份验证方法

Linux管理员知道优秀的安全实践是停止并删除所有用不到的服务，同样，你也应该禁用SSH中不使用的其他任何身份验证方法。

在这里，我将向你展示禁用所有身份验证的方法，但是请注意：不要全部禁用它们，请保留需要的。

### 禁用 GSSAPI 认证

通过“通用安全服务应用程序接口”（GSSAPI），可以使用高级配置和其他身份验证方法（除口令、密钥认证方式之外的），如果你不使用此功能，则请修改配置文件如下：

    
    
    GSSAPIAuthentication no

### 禁用Kerberos认证

同样，如果不需要则禁用：

    
    
    KerberosAuthentication no

### 禁用口令认证

如果配置了更高级的认证方式，则可禁用口令认证：

    
    
    PasswordAuthentication no

### 禁用密钥认证

如果你使用了其他身份认证方式，则可以禁用密钥身份认证。相比其他办法，使用密钥认证是风险较小的办法。如需禁用，修改配置文件如下：

    
    
    PubkeyAuthentication no

## 使用符合FIPS 140-2标准的密码

使用符合FIPS 140-2的规范，避免使用弱加密算法，请修改配置文件如下：

    
    
    Ciphers aes128-ctr,aes192-ctr,aes256-ctr

这样的设置限制了可用于SSH的加密方式，因此应用前需确认任何可能会用到的老旧客户端、脚本或应用程序的兼容性。

> “FIPS 140-2” 为美国国家标准和技术委员会发布的针对密码模块的安全需求标准，作为联邦信息处理标准在政府机构广泛采用。

## 使用符合FIPS 140-2标准的MAC

与上一小节相同，使用符合FIPS 140-2的规范，避免使用弱加密哈希算法：

    
    
    MACs hmac-sha2-256,hmac-sha2-512

## 配置主机防火墙过滤传入的SSH连接

检查传入SSH连接也是保护SSH的好方法，可以仅允许特定的IP或子网连接到系统，下面将演示通过[iptables](https://putorius.net/basic-of-iptables-opening-ports-on.html)、[firewalld](https://putorius.net/introduction-to-firewalld-basics.html)和 [Uncomplicated Firewall (UFW)](https://putorius.net/ufw-uncomplicated-firewall-basics.html)配置防火墙的方法。

### 使用iptables过滤SSH连接

允许特定IP连接：

    
    
    iptables -I INPUT -p tcp -s <指定的IP> --dport 22 -j ACCEPT

允许特定的子网：

    
    
    iptables -I INPUT -p tcp -s <指定子网> --dport 22 -j ACCEPT

更多有关`iptables`的使用方法，请参考[The Basics of IPTables](https://putorius.net/basic-of-iptables-opening-ports-on.html)自己度娘

### 通过Firewalld过滤SSH连接

允许特定IP连接SSH：

    
    
    firewall-cmd --permanent --zone=public --add-rich-rule=' rule family="ipv4"   source address="<指定IP>"   port protocol="tcp" port="22" accept'

允许特定子网：

    
    
    firewall-cmd --permanent --zone=public --add-rich-rule='   rule family="ipv4"   source address="<指定子网>"   port protocol="tcp" port="22" accept'

### 使用UFW过滤SSH连接

允许特定IP连接SSH：

    
    
    sudo ufw allow from <指定IP> to any port 22

允许特定子网：

    
    
    sudo ufw allow from <指定子网> to any port 22

## 设置一个Banner

以我的经验来看，这样做弊大于利，虽然修改Banner（连接提示信息）可以阻止一些脚本小子，但是数经验丰富的老鸟可能会将其视为一种挑衅，因此如果确实要增加Banner，请考虑消息的语气。

启用自定义Banner，请修改配置文件如下：

    
    
    Banner /etc/issue

编辑`/etc/issue`文件，即可添加连接到SSH后的提示信息。

## 其他可选程序

有很多程序可以用来帮我们组织攻击，其中最著名的是[fail2ban](https://www.fail2ban.org/wiki/index.php/Main_Page)，它通过扫描日志来查找恶意行为，并通过更新防火墙规则等操作来阻止可疑IP。关于fail2ban的配置不在本文的讨论范围。

## 总结

在本文中，我介绍了许多选项来帮助保护你的SSH服务，正如我在简介中所述，每种设置的可用性取决于您，只有您可以权衡这些设置的便利性和安全性。了解可用的选项是一个好的开始，我认为本文涵盖了有关安全方面的大多数选项，如果你使用了本文所有的配置，那么你的配置将超过《美国国防信息系统局安全技术信息指南》的要求。


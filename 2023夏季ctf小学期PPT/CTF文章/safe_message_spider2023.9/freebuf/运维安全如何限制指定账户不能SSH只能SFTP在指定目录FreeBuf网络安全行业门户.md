***本文作者：ForrestX386，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

 **最近，我司线上搞了一台文件中转服务器，用于sftp上传下载一些文件（包括测试日志之类），但是领导希望用的人只能在特定目录上传下载，不能获取Linux
shell之类。运维安全部研究了一番之后，搞了一个方案，可以限制特定组内的用户只能sftp 连接上去至指定目录，ssh 连接就提示只接受sftp
连接，总算是满足了领导的要求。现在总结一下，和大家分享一下, 测试与分析如下。**

## 0x01 测试环境配置

比如以限制sftpgroup 组的用户都只能在自己的家目录sftp 上传下载，不能ssh 连接获取shell为例进行说明，假设zhangsan
是被限制的账户之一

### 1、新建一个sftpgroup，以组为单位进行限制

    
    
    groupadd sftpgroup

![新建一个sftpgroup](https://image.3001.net/images/20180910/1536580806_5b965cc61b60c.png!small)

### 2、 新建一个账户zhangsan，加入sftpgroup

    
    
    useradd -d /home/zhangsan -s /usr/sbin/nologin -M -N -gsftpgroup zhangsan

![新建一个账户zhangsan](https://image.3001.net/images/20180910/1536580861_5b965cfdba7ab.png!small)

这里shell 设置为/usr/sbin/nologin, 使其无法获取交互式shell，其实这里设置成啥都无所谓，关键点在4节中的ForceCommand
internal-sftp 配置，稍后会解释。

### 3、zhangsan账户以公钥方式认证，额外配置如下

    
    
    mkdir -p /home/zhangsan/.ssh
    
    chown zhangsan:sftpgroup /home/zhangsan/.ssh
    
    chmod 700 /home/zhangsan/.ssh
    
    cat xxx.pub >/home/zhangsan/.ssh/authorized_keys
    
    chown zhangsan:sftpgroup /home/zhangsan/.ssh/authorized_keys
    
    chmod 700 /home/zhangsan/.ssh/authorized_keys

![zhangsan账户以公钥方式认证](https://image.3001.net/images/20180910/1536581453_5b965f4d79b04.png!small)

### 4、 配置sshd_config

配置如下：

![配置sshd_config](https://image.3001.net/images/20180910/1536581514_5b965f8af020c.png!small)

这里有3点需要解释：

 **Subsystem sftp /usr/lib/openssh/sftp-server 更为 internal-sftp，这两者有什么区别呢？**

简单的说默认sftp 进程由单独的二进制文件：/usr/lib/openssh/sftp-server启动，而internal-sftp
则无需外部二进制文件额外启动一个进程，整合在sshd进程内了。

![整合在sshd进程内](https://image.3001.net/images/20180910/1536581711_5b96604fca9ff.png!small)

internal-sftp相较于 /usr/lib/openssh/sftp-server 优点在于：

> 性能好，无需额外进程了嘛；
>
> 安全性好，无需用户登录shell，且可使用ChrootDirectory 限制sftp行为活动的目录；
>
> sftp-server 的存在主要是向后兼容。

![internal-sftp](https://image.3001.net/images/20180910/1536582051_5b9661a3d7988.png!small)

综上，考虑internal-sftp的安全性，故更改为internal-sftp。

 **Match指令是用来干什么的？**

Match指令主要用于条件匹配，比如上图：

    
    
    Match group sftpgroup

这告诉sshd 进程，sftpgroup 用户组中的用户适用下面的限制：

> ChrootDirectory %h # 限制sftp的活动目录在其Home 目录；
>
> X11Forwarding no # 禁止X11转发；
>
> AllowTcpForwarding no # 禁止tcp转发。
    
    
    ForceCommand internal-sftp

![Match指令](https://image.3001.net/images/20180910/1536582572_5b9663acc9c09.png!small)

 **ForceCommand internal-sftp 是什么意思？**

防止用户执行他们自己自定义的命令，限制用户命令执行上下文为sftp（可以理解为用户的'shell'就是sftp 那个上下文环境），
即：用户除了能执行sftp中允许的命令外，其他命令啥也执行不了

## 0x02 测试验证

### 1、ssh 连接失败

![ssh
连接失败](https://image.3001.net/images/20180910/1536584178_5b9669f29a11f.png!small)

ssh 连接提示只接受sftp connection，这就是0x02提到的ForceCommand internal-sftp
配置的效果，如果配置了这个，不管zhangsan这个用户的登录shell是啥都不好使。 如果去掉0x02提到的ForceCommand internal-sftp 配置，则ssh连接时候提示如下：

![ssh
连接失败](https://image.3001.net/images/20180910/1536586341_5b9672651dcab.png!small)

### 2、sftp连接被接受，但活动目录受限

![sftp连接被接受，但活动目录受限](https://image.3001.net/images/20180910/1536584283_5b966a5b811f4.png!small)

只能sftp连接，且限制在了/home/zhangsan这个目录下。

## 参考

> <https://serverfault.com/questions/660160/openssh-difference-between-> internal-sftp-and-sftp-server>
>
> <https://man.openbsd.org/sshd_config>

***本文作者：ForrestX386，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


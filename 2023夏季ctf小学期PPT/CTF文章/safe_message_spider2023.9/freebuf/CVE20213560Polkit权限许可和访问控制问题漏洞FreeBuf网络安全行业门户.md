Polkit，也称为PolicyKit，是Linux系统中使用的一个框架，用于定义和管理与系统权限和访问控制相关的策略。它提供了一种控制各种操作和资源权限的方法，允许非root
用户执行管理任务，而无需授予他们完全的超级用户(root)
权限。该漏洞源于当请求进程在调用polkit_system_bus_name_get_creds_sync之前断开与dbus-daemon的连接时，该进程无法获得进程的唯一uid和pid，也无法正确验证请求进程的权限导致。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 有  
  
## Part2 漏洞描述

‍漏洞名称|

Polkit权限许可和访问控制问题漏洞  
  
---|---  
CVE编号| CVE-2021-3560  
漏洞类型| 本地权限提升  
漏洞等级| 7.8 高危 (High）  
公开状态| 公开  
漏洞描述|

通过对创建的pipe进行操作，可篡改只读文件缓存，进行权限提升。  
  
时间线|

Red Hat Enterprise Linux 8

Fedora 21 (or later)

Debian Testing (“Bullseye”)

Ubuntu 20.04 LTS (“Focal Fossa”)  
  
受影响版本|

2022-2-16 NVD发布  
  
##  **分析环境:**

Ubuntu 20.04.2

## Part3漏洞复现

### 若要复现该漏洞，需要在进程执行完毕前结束该进程，首先获得进程的执行时间，来判断需要在多久后结束进程。

![图片](https://image.3001.net/images/20230712/1689140466_64ae3cf28910a4a84ae36.png!small)

然后在进程执行完毕前，将进程结束，可能需要执行多次才可成功，成功后成功添加sudo组成员用户”andi”。

![图片](https://image.3001.net/images/20230712/1689140476_64ae3cfc1fb3758117c96.png!small)

可以使用同样的方法对该账户设置密码。

![图片](https://image.3001.net/images/20230712/1689140486_64ae3d06a613f43a424d1.png!small)![图片](https://image.3001.net/images/20230712/1689140496_64ae3d104bef003a989da.png!small)

多次运行后，设置密码成功，切换至账户’andi’。

在使用低权限用户的情况下，添加sudo组用户andi并登录，获取root权限。

![图片](https://image.3001.net/images/20230712/1689140506_64ae3d1a8ae1bce556a17.png!small)

![图片](https://image.3001.net/images/20230712/1689140517_64ae3d25a1d2761be367d.png!small)

## Part4 漏洞分析

D-Bus(Desktop Bus) 是一种供应用程序相互通信的消息系统，允许在同一台机器上并发运行的多个进程之间进行通信。D-Bus
是作为freedesktop.org项目的一部分而开发的，旨在标准化Linux桌面环境提供的服务。![图片](https://image.3001.net/images/20230712/1689140534_64ae3d3608c32a2ce34b1.png!small)该漏洞存在于
Polkit 对身份验证凭据的处理中，可以通过低权限帐户绕过身份验证过程并以提升的权限执行任意命令。

在通过PoC，执行dbus-send命令时，会经历以下几个阶段:

1\. dbus-send要求accounts-daemon创建一个新用户。

2\. accounts-daemon从接收D-Bus消息dbus-send。该消息包括发送者的唯一总线名称。让我们假设它是“:1.96”。此名称附加到消息中，dbus-daemon不能伪造。

3\. accounts-daemon询问Polkit连接：1.96是否被授权创建新用户。

4\. Polkit要求dbus-daemon提供连接的UID：1.96。

5\. 如果连接:1.96的UID为“0”，则Polkit立即授权该请求。否则，它会向身份验证代理发送允许授权请求的管理员用户列表。

6\. 身份验证代理打开一个对话框以从用户那里获取密码。

7\. 身份验证代理将密码发送给Polkit。

8\. Polkit将“是”回复发送回accounts-daemon.

9\. accounts-daemon创建新的用户帐户。

该漏洞发生在第四步，如果在该过程中，UID不再存在，Polkit会以错误的方式处理该异常。Polkit不会将此请求拒绝，而是会认为请求来自于UID0的进程，该请求会使用root权限通过。因不能确定程序在运行时，每一个环节的具体运行时间，所以在上述的实验过程中，我们需要多次执行命令，才能在合适的时间段结束dbus-send。

## Part5 修复缓解建议

建议linux各发行版升级到漏洞修复后的版本

RHEL 8：

https://access.redhat.com/security/cve/CVE-2021-3560

Fedora 21及更高版本：

https://bugzilla.redhat.com/show_bug.cgi?id=1967424

Debian testing (“bullseye”)：

https://security-tracker.debian.org/tracker/CVE-2021-3560

Ubuntu 20.04：

https://ubuntu.com/security/CVE-2021-3560


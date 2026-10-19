## 漏洞说明

polkit是默认安装在很多Linux发行版上的系统服务。CVE-2021-3560是polkit中潜伏了7年之久的漏洞，于2021年6月份公布。该漏洞能使非特权本地用户获得系统root权限。CVE-2021-3560漏洞于polkit
0.113版引入，但是很多流行的Linux发行版直到最近才引入包含漏洞的版本。下表展示的是一些流行的Linux发行版及是否包含此漏洞的情况：

![](https://image.3001.net/images/20210721/1626834430_60f785febce0db41581a9.jpg!small)

为了帮助解释该漏洞，首先对dbus-send命令执行过程进行说明。

![](https://image.3001.net/images/20210720/1626777513_60f6a7a92983bf3ce14cd.png!small)

虚线上方的两个进程dbus-send和Authentication Agent是非特权用户进程。线下的那些是特权系统进程。中间是dbus-daemon，它处理所有的通信：其他四个进程通过发送 D-Bus 消息相互通信。下面是通过dbus-send创建新用户的事件顺序：

1\. dbus-send要求accounts-daemon创建一个新用户。

2\. accounts-daemon从dbus-send接收 D-Bus 消息。该消息包含唯一的连接名称，我们假设它是“:1.96”。此名称被dbus-daemon附加到消息中，且不能被伪造。

3\. accounts-daemon向polkit询问连接:1.96 是否被授权以创建新用户。

4\. polkit向dbus-daemon询问连接:1.96的 UID。

5\. 如果连接:1.96 的 UID 为“0”，则 polkit 立即授权该请求。否则，它会向身份验证代理发送允许授权请求的管理员用户列表。

6\. Authentication Agent打开一个对话框以从用户那里获取密码。

7\. Authentication Agent将密码发送给 polkit。

8\. polkit 将“是”回复发送回accounts-daemon。

9\. accounts-daemon 创建新的用户帐户。

CVE-2021-3560漏洞位于上述事件序列的第四步。如果 polkit 向dbus-daemon请求总线:1.96 的 UID，但总线:1.96
不再存在，会发生什么？dbus-daemon正确处理这种情况并返回错误。但事实上 polkit 没有正确处理该错误，它没有拒绝请求，而是将请求视为来自
UID 0 的进程。换句话说，它立即授权请求。向dbus-demon请求总线UID的函数为polkit_system_bus_name_get_creds_sync。

## 利用过程

操作系统：Ubuntu20.04

该漏洞非常容易被利用，它需要的只是标准的工具，比如终端的几个命令bash、kill和dbus-send，本节中描述的PoC依赖两个软件包`accountsservice`和`gnome-control-center``。`在
Ubuntu等桌面图形系统上，这两个软件包通常默认安装。该漏洞与`accountsservice`或`gnome-control-center`没有任何关系，它们只是 polkit 客户端，同时是方便利用的载体。

为了避免重复触发身份验证对话框，建议从 SSH 会话运行命令：

![](https://image.3001.net/images/20210720/1626777554_60f6a7d211234798bab8f.png!small)

该漏洞是通过启动dbus-send命令但在 polkit 仍在处理请求的过程中将其杀死而触发的。为了确定杀死dbus-send进程的时间，首先我们要测量dbus-send正常运行的时间：

![](https://image.3001.net/images/20210720/1626777574_60f6a7e6a3b238d6c94b8.png!small)

因此我们可以在7毫秒内杀死dbus-send进程进程以触发漏洞，完成用户创建的目的：

![](https://image.3001.net/images/20210720/1626777607_60f6a807bbd9c0ad30e74.png!small)

接着使用同样的方式为这个用户设置密码：

![](https://image.3001.net/images/20210720/1626777636_60f6a824a48d2ccfd3c8d.jpg!small)

最后，我们就可以以boris2身份登录并成为root用户：

![](https://image.3001.net/images/20210720/1626777669_60f6a84510b65fbbdc898.jpg!small)

## 漏洞处理建议

目前该漏洞已经被修复，建议参考Linux各发行版本的官方通告及时升级更新：

 **RHEL 8** **：**

https://access.redhat.com/security/cve/CVE-2021-3560

 **Fedora 21** **及更高版本：**

https://bugzilla.redhat.com/show_bug.cgi?id=1967424

 **Debian testing (** **“bullseye** **”)** **：**

https://security-tracker.debian.org/tracker/CVE-2021-3560

 **Ubuntu 20.04** **：**

https://ubuntu.com/security/CVE-2021-3560

## 参考

> https://github.blog/2021-06-10-privilege-escalation-polkit-root-on-linux-> with-bug/#vulnerability

转载请注明“转自奇安信代码卫士 https://codesafe.qianxin.com”


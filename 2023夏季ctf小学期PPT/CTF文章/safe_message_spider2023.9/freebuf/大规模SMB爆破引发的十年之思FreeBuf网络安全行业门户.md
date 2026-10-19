**近日，千里目安全实验室EDR安全团队持续收到大量企业用户反馈，称其内网很多服务器存在大规模SMB爆破现象，但一直查不到问题根因。**

我们深入研究发现，这是服务器中了飞客蠕虫之后，横向发起的大规模SMB爆破。由于此变种飞客蠕虫构造精巧，以注入方式驻留系统进程之中，且病毒体文件具备隐藏和对抗属性，非常难以察觉。

有趣的是，飞客蠕虫早在2008年伴随着MS08-067漏洞就出现了，期间出现了多个变异版本。MS08-067漏洞最早在2008年即发布，距今有十年之久，仍然有大量用户感染，非常值得深思！此外，主机在修复漏洞的情况下，通过IPC方式的弱密码SMB爆破，仍然可以感染目标主机！

在此，我们再次提醒用户，安全无小事，即使是十年之久的老漏洞，也要勤打补丁，同时要避免主机弱密码问题，防止被爆破成功！

## 0x01 攻击场景

此次攻击，场景相对比较复杂，但构造精巧，病毒体仅仅是一个几百KB的dll。这里以mwpxx.dll为例，此文件即飞客蠕虫病毒体。通常，飞客蠕虫病毒体，是以随机名字命令的dll文件。  

![图片.png](https://image.3001.net/images/20180413/15236103505011.png!small)  

如上图，mwpxx.dll病毒体可以被多个系统进程加载或注入。系统进程一旦加载或注入成功，便自动携带了一整套的飞客蠕虫攻击功能，包括提权、探测目标主机系统版本、MS08-067漏洞攻击、SMB爆破、感染移动设备、下载恶意文件、连接C&C服务器等等。

攻击顺序如下：

> 1.rundll32.exe或service.exe加载mwpxx.dll，执行飞客蠕虫功能。
>
> 2.判断系统进程svchost.exe和explorer.exe是否存在mwpxx.dll，如否则使用APC注入mwpxx.dll。
>
> 3.注入成功后，进行提权。
>
> 4.内网探测目标主机系统版本，为MS08-067和SMB爆破做准备。
>
> 5.执行MS08-067漏洞攻击，如成功则复制病毒体自身到目标主机并运行起来。
>
> 6.不管漏洞攻击是否成功，都会对目标主机进行基于IPC的SMB爆破，成功则同样复制病毒体自身到目标主机。
>
> 7.遍历系统，尝试发现并感染移动设备。
>
> 8.下载恶意文件，连接C&C服务器。

步骤5和6，即漏洞攻击和SMB爆破，只要有一种成功，则成功感染一台内网主机，感染后的主机又重复1到8步骤。

## 0x02 漏洞攻击

如果Payload是通过service.exe进行加载的，则通过NetpwPathCanonicalize触发，执行MS08-067漏洞攻击。

![图片.png](https://image.3001.net/images/20180413/15236103656923.png!small)  

触发漏洞之后，发送相应的恶意代码给包含MS08-067漏洞的主机。

![图片.png](https://image.3001.net/images/20180413/15236103715445.png!small)  

如果Payload是通过svchost.exe -k
netsvcs加载的，同样执行NetpwPathCanonicalize触发后面要执行的MS08-067漏洞攻击。

![图片.png](https://image.3001.net/images/20180413/152361037646.png!small)  

当Payload是通过svchost.exe -k NetworkService加载的，则Hook DN相关函数操作。

![图片.png](https://image.3001.net/images/20180413/15236103815582.png!small)  

防止杀毒软件访问网站进行下载升级，相关的杀毒软件列表如下。

![图片.png](https://image.3001.net/images/20180413/15236103872788.png!small)  

## 0x03 SMB爆破

不管漏洞攻击是否成功，飞客蠕虫都会通过IPC攻击开放SMB端口的主机，并进行爆破。因此，内网极可能存在大规模的SMB爆破现象。

![图片.png](https://image.3001.net/images/20180413/1523610394959.png!small)  

爆破的密码字典：  

![图片.png](https://image.3001.net/images/20180413/15236104005041.png!small)  

## 0x04 感染移动设备

飞客蠕虫执行后，还会感染移动存储设备，如下图。

![图片.png](https://image.3001.net/images/20180413/1523610409838.png!small)

![图片.png](https://image.3001.net/images/20180413/1523610416753.png!small)

![图片.png](https://image.3001.net/images/20180413/15236104224089.png!small)  

复制自身到下面的路径：

“\RECYCLER\S-%d-%d-%d-%d%d%d-%d%d%d-%d%d%d-%d\”，然后通过

rundll32.exe
\RECYCLER\S-%d-%d-%d-%d%d%d-%d%d%d-%d%d%d-%d\payload.dll，ekepuf来执行Payload程序，同时将这行命令写入到可移动磁盘的autorun.inf文件中，进行移动磁盘的感染。

## 0x05 连接C&C服务器

飞客蠕虫通过解析XML来控制相应的网络请求端口，如下图所示：

![图片.png](https://image.3001.net/images/20180413/15236104307485.png!small)

![图片.png](https://image.3001.net/images/20180413/15236104377542.png!small)  

发送的数据包格式，如下图所示：

![图片.png](https://image.3001.net/images/20180413/15236104472552.png!small)

判断时间，尝试解析相应的域名地址（baidu.com、google.com、yahoo.com、msn.com、ask.com、w3.org等），判断网络是否连通，如下图所示：

![图片.png](https://image.3001.net/images/20180413/15236104593682.png!small)

然后通过gethostbyname获得主机名，并通过相应的域名产生算法，生成随机域名，然后连接下载并执行相应的程序。

![图片.png](https://image.3001.net/images/20180413/15236104745792.png!small)
![图片.png](https://image.3001.net/images/20180413/15236104801942.png!small)  

相应的域名生成算法（DGA）：
![图片.png](https://image.3001.net/images/20180413/15236104886419.png!small)  

## 0x05 解决方案

> 1、隔离感染主机：已中毒计算机尽快隔离，关闭所有网络连接，禁用网卡。
>
> 2、切断传播途径：关闭潜在终端的SMB 445等网络共享端口，关闭异常的外联访问。
>
> 3、查找攻击源：借助安全感知类产品定位攻击源。
>
>
> 4、查杀病毒：使用专杀<http://media.kaspersky.com/utilities/VirusUtilities/EN/kidokiller.zip>。
>
> 5、修补漏洞：打上“MS08-067”漏洞补丁，请到微软官网，下载对应的漏洞补丁（<https://docs.microsoft.com/zh-> cn/security-updates/Securitybulletins/2008/ms08-067>）。
>
> 6、修改密码：如果主机账号密码比较弱，建议重置高强度的密码。

 ***本文作者：千里目安全实验室，转载请注明来自 FreeBuf.COM**  


作者: **启明星辰ADLab**

#### 一、基本功能简述

目前针对物联网设备的恶意软件越来越普遍，一般来说针对物联网设备的攻击分为两个方面：一方面是通过自动化工具使用密码字典尝试批量猜解物联网设备的管理员帐号及密码，导致攻击者可以轻易访问物联网设备（物联网设备被攻击者控制）；另一方面是因为物联网设备存在安全漏洞，攻击者利用漏洞来对设备进行攻击，达到控制设备的目的。被控制的物联网设备往往会被攻击者集中起来，组建僵尸网络，从而发起DDoS攻击。

近日，Palo Alto
Networks的研究人员发现了Linux僵尸网络Tsunami的新变种，并命名为Amnesia。Amnesia即为通过利用漏洞来对物联网设备进行攻击的恶意软件，Amnesia也是首个采用虚拟机检测技术来躲避恶意软件分析沙箱的Linux嵌入式恶意软件。Amnesia僵尸网络允许攻击者利用远程代码执行漏洞对未打补丁的数字视频录像机设备发起攻击。该远程代码执行漏洞由安全专家Rotem
Kemer在2016年3月22日披露，其中全球大概70多家厂商受到影响，这些厂商均使用了由TVT
Digital（深圳同为）生产的设备。根据目前的扫描数据，全球有227000台设备受此漏洞影响，主要受影响的国家和地区包括：中国台湾、美国、以色列、土耳其和印度。
![](https://images.seebug.org/content/images/2017/05/amnesia1.png-w331s)

本次发现的Amnesia僵尸网络运行在PowerPC架构上，首先攻击者通过暴力猜解或者其他手段感染DVR设备，使Amnesia恶意代码在DVR上开始运行，当Amnesia运行后，它会连接远程C&C，并根据控制指令中指定的IP范围扫描网络中的其他DVR设备进行传播。
![](https://images.seebug.org/content/images/2017/05/amnesia2-1.png-w331s)

#### 二、逆向分析描述

##### 1.反虚拟机

Amnesia是首个采用虚拟机检测技术来躲避恶意软件分析沙箱的Linux嵌入式恶意代码。针对Windows或安卓的恶意软件常常会采用虚拟机检测技术来躲避沙箱环境的分析，然而该技术在Linux嵌入式系统上却很少采用。当僵尸网络Amnesia发现自身运行于VirtualBox、VMware或QEMU虚拟机中，它将删除系统中的所有文件来阻碍恶意软件分析沙箱的正常运行。

Linux系统中的`/sys/class/dmi/id`目录里存放了主机的相关硬件信息，包括产品信息、主板信息、Bios信息等，Amnesia就是通过读取该目录中的文件获取当前主机的硬件信息。当Amnesia运行时会读取`/sys/class/dmi/id/product_name`和`/sys/class/dmi/id/sys_vendor`文件，并匹配其中是否包含关键字“VirtualBox”、“VMware”和“QEMU”来判断当前目标系统是否为虚拟机。
![](https://images.seebug.org/content/images/2017/05/amnesia3.png-w331s)
当检测到当前主机为虚拟机时，Amnesia将开启自我删除，并删除Linux根目录、当前用户主目录、工作目录，这些删除操作相当于擦除整个Linux系统，会对整个系统造成损害。
![](https://images.seebug.org/content/images/2017/05/amnesia4.png-w331s)

##### 2.主要行为

当目标系统不是虚拟机环境时，Amnesia会执行命令来更改系统限制。
![](https://images.seebug.org/content/images/2017/05/amnesia5.png-w331s)
其中主要命令包括：  命令 | 注释  
---|---  
echo 80000500 > /proc/sys/fs/nr_open 1>/dev/null 2>/dev/null  |
更改进程可以打开的最大文件描述符的数量  
ulimit -n 1000 1>/dev/null 2>/dev/null | 更改进程可以打开的最大文件描述符的数量  
ulimit -n 10000 1>/dev/null 2>/dev/null | 更改进程可以打开的最大文件描述符的数量  
ulimit -n 100000 1>/dev/null 2>/dev/null | 更改进程可以打开的最大文件描述符的数量  
ulimit -n 1000000 1>/dev/null 2>/dev/null | 更改进程可以打开的最大文件描述符的数量  
ulimit -n 10000000 1>/dev/null 2>/dev/null | 更改进程可以打开的最大文件描述符的数量  
echo 1 > /proc/sys/net/ipv4/tcp_tw_recycle 1>/dev/null 2>/dev/null |
开启tcp_tw_recycle选项，能够更快地回收TIME-WAIT套接字  
sysctl -w net.ipv4.tcp_moderate_rcvbuf=\"0\" 1>/dev/null 2>/dev/null |
关闭TCP内存自动调整功能  
sysctl -w fs.file-max=999999999999999999 1>/dev/null 2>/dev/null | 更改文件句柄的最大数量  
  
当目标系统不是虚拟机环境时，Amnesia会根据当前用户的权限将自身拷贝到`/etc/init.d/.reboottime`和`/etc/cron.daily/.reboottime`,然后修改用户目录下的`.bashrc、.bash_profile`文件，实现自身随系统启动运行。Amnesia会杀死与Telnet及SSH相关的进程，来防止管理员或其他攻击者通过远程登录来控制设备。
![](https://images.seebug.org/content/images/2017/05/amnesia6.png-w331s)
将自身写入到用户目录下`.bashrc、.bash_profile`实现随系统启用运行。
![](https://images.seebug.org/content/images/2017/05/amnesia7.png-w331s)
_杀死与Telnet相关进程。_ 杀死与SSH相关进程。

##### 3.控制指令

Amnesia采用IRC协议与C&C进行通信，其中支持的控制指令较多，而且包括许多与DDoS攻击相关的指令。通过对控制命令的进一步分析，发现Amnesia使用了与Tsunami恶意代码相同的控制指令，也进一步印证了Amnesia为Tsunami的新变种。
![](https://images.seebug.org/content/images/2017/05/amnesia8.png-w331s)

##### 4.漏洞利用

在控制指令中包括两个特殊的指令CCTVSSCANNER和CCTVPROCS。其中，CCTVSSCANNER用来扫描DVR设备，CCTVPROCS用来对存在漏洞的设备进行攻击。

当Amnesia收到CCTVSSCANNER指令时，Amnesia会构造请求向指定的IP地址发起连接，然后读取返回内容，如果返回内容中包括“Cross
Web
Server”，则表示该DVR设备存在。Amnesia会构造请求并在请求中加入要远程执行的shell命令发起对DVR设备的访问。(其中{IFS}&&shell，由于Swedish不存在，所以会执行`tar
-zxf /mnt/mtd/WebSites/language.tar.gz Swedish && shell命令 /* -C
/nfsdir/language`命令。即Swedish后面连接的shell命令会被执行，这就导致了远程命令执行。
(关于该漏洞的详细信息可参阅http://www.kerneronsec.com/2016/02/remote-code-execution-in-cctv-dvrs-of.html)

![](https://images.seebug.org/content/images/2017/05/amnesia10.png-w331s) TVT
DVR设备处理请求时的代码调用图如下：
![](https://images.seebug.org/content/images/2017/05/amnesia11.png-w331s)

#### 三、总结

随着越来越多的物联网设备连接至互联网，那些不安全的物联网设备正在成为威胁实施者眼中唾手可得并可轻松利用的成熟果实。正如臭名昭著的Mirai僵尸网络，针对网络摄像头和家庭路由器等设备中的登录漏洞进行攻击利用，发起了迄今为止已知的规模最大的DDoS攻击。如果物联网设备制造商不能确保其设备的绝对安全，对数字经济的潜在影响将是毁灭性的。

#### 四、IOC

**C &C:**

    
    
        ukranianhorseriding.net
        surrealzxc.co.za
        inversefierceapplied.pw

**Sample SHA-256:**

    
    
    c80048aab22ef18e4271a0d6c6c85d7f9720653ba003861776dcecb2bd63878a  
    719142b7e103e66d9b56596f467f36a7dad34ade106b1aa61844c5904476e533  
    b05b0cfad6d32f9a56865d1e24cf02b6642892f60ad5d972b2f291484d5c7b50  
    06d30ba7c96dcaa87ac584c59748708205e813a4dffa7568c1befa52ae5f0374  
    10aa7b3863f34d340f960b89e64319186b6ffb5d2f86bf0da3f05e7dbc5d9653  
    175fe89bbc8e44d45f4d86e0d96288e1e868524efa260ff07cb63194d04ea575  
    1d8bc81acbba0fc56605f60f5a47743491d48dab43b97a40d4a7f6c21caca12a  
    2f9cd1d07c535aae41d5eed1f8851855b95b5b38fb6fe139b5f1ce43ed22df22  
    327f24121d25ca818cf8414c1cc704c3004ae63a65a9128e283d64be03cdd42e  
    37b2b33a8e344efcaca0abe56c6163ae64026ccef65278b232a9170ada1972af  
    3a595e7cc8e32071781e36bbbb680d8578ea307404ec07e3a78a030574da8f96  
    4313af898c5e15a68616f8c40e8c7408f39e0996a9e4cc3e22e27e7aeb2f8d54  
    46ea20e3cf34d1d4cdfd797632c47396d9bdc568a75d550d208b91caa7d43a9b  
    4b0feb1dd459ade96297b361c69690ff69e97ca6ee5710c3dc6a030261ba69e0  
    4db9924decd3e578a6b7ed7476e499f8ed792202499b360204d6f5b807f881b8  
    5e6896b39c57d9609dc1285929b746b06e070886809692a4ac37f9e1b53b250c  
    64f03fff3ed6206337332a05ab9a84282f85a105432a3792e20711b920124707  
    6b2885a4f8c9d84e5dc49830abf7b1edbf1b458d8b9d2bafb680370106f93bc3  
    6b29b65c3886b6734df788cfc6628fbee4ce8921e3c0e8fc017e4dea2da0fd0b  
    885dce73237c4d7b4d481460baffbd5694ab671197e8c285d53b551f893d6c09  
    886136558ec806da5e70369ee22631bfb7fa06c27d16c987b6f6680423bc84b0  
    8f57ec9dfba8cf181a723a6ac2f5a7f50b4550dd33a34637cf0f302c43fd0243  
    9351ee0364bdbb5b2ff7825699e1b1ee319b600ea0726fd9bb56d0bd6c6670cb  
    9c7a5239601a361b67b1aa3f19b462fd894402846f635550a1d63bee75eab0a2  
    a010bf82e2c32cba896e04ec8dbff58e32eee9391f6986ab22c612165dad36a0  
    ad65c9937a376d9a53168e197d142eb27f04409432c387920c2ecfd7a0b941c8  
    aeb480cf01696b7563580b77605558f9474c34d323b05e5e47bf43ff16b67d6a  
    b113ec41cc2fd9be9ac712410b9fd3854d7d5ad2dcaac33af2701102382d5815  
    b13014435108b34bb7cbcef75c4ef00429b440a2adf22976c31a1645af531252  
    b3d0d0e2144bd1ddd27843ef65a2fce382f6d590a8fee286fda49f8074711545  
    bdefa773e3f09cdc409f03a09a3982f917a0cc656b306f0ece3dd1a2564a8772  
    c03b403d5de9778a2ec5949d869281f13976c2fc5b071e0f5f54277680c80902  
    cb2382b818993ef6b8c738618cc74a39ecab243302e13fdddb02943d5ba79483  
    ce61dcfc3419ddef25e61b6d30da643a1213aa725d579221f7c2edef40ca2db3  
    d0bda184dfa31018fe999dfd9e1f99ca0ef502296c2cccf454dde30e5d3a9df9  
    e7d6b3e1fba8cdf2f490031e8eb24cd515a30808cdd4aa15c2a41aa0016f8082  
    eb54dc959b3cc03fbd285cef9300c3cd2b7fe86b4adeb5ca7b098f90abb55b8a  
    f23fecbb7386a2aa096819d857a48b853095a86c011d454da1fb8e862f2b4583  
    f6af2fa4f987df773d37d9bb44841a720817ce3817dbf1e983650b5af9295a16  
    f7a737cb73802d54f7758afe4f9d0a7d2ea7fda4240904c0a79abae732605729  
    f7cf1e0d7756d1874630d0d697c3b0f3df0632500cff1845b6308b11059deb07  
    f97848514b63e9d655a5d554e62f9e102eb477c5767638eeec9efd5c6ad443d8  

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员。截止目前，ADLab通过CVE发布Windows、Linux、Unix等操作系统安全或软件漏洞近300个，持续保持亚洲领先并确立了其在国际网络安全领域的核心地位。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。
![](https://images.seebug.org/content/images/2017/05/adlab.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/302/>


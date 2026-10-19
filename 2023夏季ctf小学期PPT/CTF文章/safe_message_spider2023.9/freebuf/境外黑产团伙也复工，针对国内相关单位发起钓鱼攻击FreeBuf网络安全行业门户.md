## 概述

近日，奇安信病毒响应中心在日常样本监控过程中发现境外黑客团伙以国内某银行的名义向相关单位发送钓鱼邮件诱导收件人打开附件，从而运行恶意程序，导致单位信息、机密文件被窃取。

样本使用目前流行的混淆器，在执行过程中多次内存加载，最终运行NanoCore远控，连接远程服务器上传敏感数据。

通过奇安信大数据平台监测，已有国内相关单位中招，为防止威胁进一步扩散，病毒响应中心负责任地对相关样本进行披露和分析。

##  邮件分析

![图片.png](https://image.3001.net/images/20200311/1583892636_5e68489c5aaec.png!small)

其发件人高仿中航船舶的邮件系统（@avicships.com），而中航船舶真实的邮箱地址为@avicship.com，差一个”s”，非常具有迷惑性。

![图片.png](https://image.3001.net/images/20200311/1583892705_5e6848e17a63e.png!small)

附件内容如下：

![图片.png](https://image.3001.net/images/20200311/1583892711_5e6848e746c85.png!small)

从附件名称可以判断该黑客团伙似乎不懂中文。

## 样本分析

文件名  
| MD5  
| Packer/compiler  
| 类型  
  
---|---|---|---  
**CIBC payment instruction.exe** **** |  8aecbcff2863ca8fb5f6eb352f95d608 |
Asprotect |  PE文件  
  
脱壳后，为Delphi编写的混淆器，在执行过程中会将自身复制到%appdata%/
Microsoft目录下，命名为microsoft.exe并启动。自解密一段代码：

![图片.png](https://image.3001.net/images/20200311/1583892874_5e68498a93a7e.png!small)

在启动目录下释放microsoft.vbs，用于持久化：

![图片.png](https://image.3001.net/images/20200311/1583892908_5e6849acba8d6.png!small)

创建自身进行进程替换：

![图片.png](https://image.3001.net/images/20200311/1583892912_5e6849b073f3b.png!small)

进程替换的PE为VC编写，作为loader从资源节读取数据：

![图片.png](https://image.3001.net/images/20200311/1583892924_5e6849bc52eff.png!small)

最后进行内存加载.net编写的NanoCore远控，外层加了Eazfuscator壳：

![图片.png](https://image.3001.net/images/20200311/1583892954_5e6849da658ef.png!small)

NanoCore的C2域名btcexchamge.duckdns.org，storexchange.duckdns.org

## 关联分析

在日常样本监控过程中我们发现，除了该团伙使用Delphi编写的混淆器外，勒索软件也在使用，在Hakbit勒索最新的变种中（.ravack），同样使用了Delphi编写的混淆器，但是执行流程稍有不同，Hakbit勒索外层在执行过程中并没有进行持久化操作，而判断了虚拟机的存在，之后分配了一块内存，进行了一次shellcode的调用操作。

![图片.png](https://image.3001.net/images/20200311/1583893322_5e684b4a29787.png!small)

Shellcode的功能依然是进程替换，替换后的PE和上述报告中的相同，为VC编写的Loader，最终内存加载Hakbit勒索程序。

从外层Delphi执行的结果的差异我们可以基本判断该混淆器已经非常成熟，应该存在众多选项供用户选择，预计未来一段时间会有大量的恶意软件使用该混淆器。

根据奇安信大数据多维度平台进行关联，我们发现该团伙还会仿冒德意志银行对德国相关公司进行手法相似的攻击。

![图片.png](https://image.3001.net/images/20200311/1583893330_5e684b521c8be.png!small)

文件名  
| MD5  
| Packer/compiler  
| 类型  
  
---|---|---|---  
**Deutsche Bank AG Instruction.exe** **** |  452fe9d3b013a98568355342b79e9b6a
|  Autoit |  PE文件  
  
Autoit脚本会将NanoCore注入到RegSvcs.exe进程中：

![图片.png](https://image.3001.net/images/20200311/1583893380_5e684b8413f58.png!small)

C2与上述相同。

该团伙还会仿冒DHL邮件：

![图片.png](https://image.3001.net/images/20200311/1583893410_5e684ba2795c9.png!small)

文件名  
| MD5  
| Packer/compiler  
| 类型  
  
---|---|---|---  
**Parcel information.exe** **** |  744d77a3c5859d9acf5dd7b13ce7fab4 |  VB |
PE文件  
  
VB代码会将NanoCore注入到RegAsm.exe进程中。C2：doublegrace.ddns.net

最近两年，病毒响应中心的检测到仿冒中航船舶作为发件人的商贸信越来越多，收件人平时不注意的话很难分辨出真伪，最终导致恶意代码执行，公司数据被窃取。

如发件人为@avicships.net：

![图片.png](https://image.3001.net/images/20200311/1583893515_5e684c0b814c3.png!small)

文件名  
| MD5  
| Packer/compiler  
| 类型  
  
---|---|---|---  
**New Project - Marine Altantic.doc** **** |  3bb5deb9ca20a1fe586b2a8a68ccc68f
|  Rtf |  Word文档  
  
文档使用11882漏洞，像远程服务器下载payload（hxxp://dubem.top/nwama/nwama.exe），域名已经无法访问。

## 总结

目前，越来越多的境外黑客团伙向国内相关单位发送经过精心伪造的钓鱼邮件，由于邮件内容为中文且伪造的过于逼真外加上相关人员安全意识较低，最终导致单位受到较大的财产损失。因此，奇安信病毒响应中心提醒用户，疫情在家远程办公，不要点击来源不明的邮件和可执行文件，同时提高个人的安全意识，从而可以防止用户隐私信息被盗取的风险，奇安信病毒响应中心会持续对国内黑产进行挖掘和跟踪。

同时基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对该家族的精确检测。

## IOC

文件Hash：

8aecbcff2863ca8fb5f6eb352f95d608

452fe9d3b013a98568355342b79e9b6a

744d77a3c5859d9acf5dd7b13ce7fab4

Domain：

doublegrace.ddns.net

btcexchamge.duckdns.org

storexchange.duckdns.org


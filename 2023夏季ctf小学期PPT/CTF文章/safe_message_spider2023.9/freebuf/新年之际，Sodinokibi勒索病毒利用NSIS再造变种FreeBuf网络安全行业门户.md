**时间总是过得飞快，圣诞节已悄悄溜走，我们即将迎来新年。2020年将要开启21世纪新的十年 -2020年代。节日里在人们充满欢声笑语的同时，往往计算机病毒的活跃度也会随之上升。回顾2019年,
勒索病毒和挖矿病毒更是牢牢占据在计算机流行病毒榜首，侠盗Gandcrab、GlobeImposter以及Sodinokibi等比较知名的勒索病毒，他们在这一年里不仅频繁更新，还不断地开创新的传播方式。**

近期，亚信安全监测到多个勒索病毒异常活跃，这其中就包括知名的Sodinokibi勒索病毒，本次截获的Sodinokibi勒索病毒利用Windows安装程序制作工具NSIS（Nullsoft
Scriptable Install System）进行打包，然后伪装成Adobe Flash安装包进行传播。NSIS（Nullsoft
Scriptable Install System）是一个开源的 Windows
系统下安装程序制作程序。它提供了安装、卸载、系统设置、文件解压缩等功能。如其名字所指出的那样，NSIS
是通过它的脚本语言来描述安装程序的行为和逻辑的。NSIS中的System插件是其中比较知名的插件，它可以提供开发人员分配，释放和复制内存，能够从任何DLL调用任何导出的函数，与COM对象进行交互，并对64位整数执行数学运算等操作。

由于Sodinokibi勒索病毒更新时间是在圣诞节和元旦到来之际，勒索通知信也变得具有“节日气氛”，亚信安全将其命名为Ransom.Win32.SODINOKIBI.AUWTZ。

![](https://image.3001.net/images/20191231/1577758654_5e0aafbe5b926.png!small)

Sodinokibi勒索病毒最早出现在2019年4月份，早期版本使用Web服务相关漏洞传播，后来发现该勒索病毒通过垃圾邮件附件传播。不仅传播方式发生变化，其使用的外壳保护技术也在不断更新和变换，我们对此进行了梳理。亚信安全也将会持续关注该勒索病毒的动态和发展。

**事件时间** | **外壳技术** | **传播方式** | **亚信安全检测名**  
---|---|---|---  
**2019** **年** **4** **月** | PE加壳解密 | Web服务漏洞 | 早期版本 TROJ_FR.620727BA  
**2019** **年** **8** **月** **21** **日** | 混淆的JS脚本 | 垃圾邮件 | TROJ_FRS.0NA103H619  
**2019** **年** **8** **月** **23** **日** | PowerShell脚本 | 以无文件的方式在内网扩散 |
Ransom.Win32.SODINOKIBI.AUWT  
**2019** **年** **10** **月** **28** **日** | 内存动态解密 | 垃圾邮件（附件伪装成Excel文档） |
Ransom.Win32.SODINOKIBI.AUWTS  
**2019** **年** **11** **月** **28** **日** | 反调试 内存动态解密 | 垃圾邮件（附件伪装成Word文档） |
Ransom.Win32.SODINOKIBI.AUWTR  
**2019** **年** **12** **月** **3** **日** | .NET进程注入 | 垃圾邮件（附件伪装成PDF文件） |
Ransom.MSIL.SODINOKIBI.A  
**2019** **年** **12** **月** **26** **日** | NSIS软件打包 | 垃圾邮件（附件伪装成Adoble
Flash安装文件） | Ransom.Win32.SODINOKIBI.AUWTZ  
  
## 病毒详细分析

该病毒利用Windows安装程序制作工具NSIS（Nullsoft Scriptable Install System）进行打包，然后伪装成Adobe
Flash安装包进行传播：

![](https://image.3001.net/images/20191231/1577758665_5e0aafc9e55d8.png!small)

其使用NSIS软件打包，提取后的文件包括NSIS插件文件system.dll以及加密的病毒主体文件416352975：

![](https://image.3001.net/images/20191231/1577758677_5e0aafd5c3533.png!small)

![](https://image.3001.net/images/20191231/1577758684_5e0aafdc4ecf2.png!small)

打包该勒索样本的NSIS脚本如下：

![](https://image.3001.net/images/20191231/1577758692_5e0aafe483ae1.png!small)

将脚本整理后，我们发现其主要的功能是将加密的勒索病毒主体文件416352975映射到内存空间，在内存里进行解密然后执行：

![](https://image.3001.net/images/20191231/1577758704_5e0aaff06f699.png!small)

![](https://image.3001.net/images/20191231/1577758712_5e0aaff82e4c1.png!small)

要获取解密后的勒索payload需要进行动态调试，从内存dump。首先在分配的内存中解密相关数据：

![](https://image.3001.net/images/20191231/1577758721_5e0ab001dc9c2.png!small)

解密后的数据如下：

![](https://image.3001.net/images/20191231/1577758729_5e0ab0090e38e.png!small)

然后进行整合，创建进程执行：

![](https://image.3001.net/images/20191231/1577758759_5e0ab027239fc.png!small)

![](https://image.3001.net/images/20191231/1577758771_5e0ab0331c874.png!small)

解密后的文件就是Sodinokibi勒索病毒主体payload文件，具有此勒索的典型入口：

![](https://image.3001.net/images/20191231/1577758781_5e0ab03de1e51.png!small)

此勒索病毒加密后的文件后缀名为随机文件名：

![](https://image.3001.net/images/20191231/1577758791_5e0ab0474b312.png!small)

勒索提示信息文件j37k8zju-readme.txt，内容如下所示：

![](https://image.3001.net/images/20191231/1577758799_5e0ab04f75411.png!small)

加密文件之后会修改桌面背景图片，如下所示：

![](https://image.3001.net/images/20191231/1577758815_5e0ab05f4356f.png!small)

## 解决方案

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装；
>
> 尽量关闭不必要的文件共享；
>
> 请注意备份重要文档。备份的最佳做法是采取3-2-1规则，即至少做三个副本，用两种不同格式保存，并将副本放在异地存储。

### IOC

**文件** **SHA-1** | **文件名称** | **亚信安全检测名**  
---|---|---  
6d6d889655fb9c64ddfb****51261e99 | Adobe® Flash® Player 32.0 |
Ransom.Win32.SODINOKIBI.AUWTZ  
  
***本文作者：亚信安全，转载请注明来自FreeBuf.COM**


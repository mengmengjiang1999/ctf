# **背景** ****

TA505为proofpoint披露的网络犯罪组织，其相关活动可以追溯到2014年。该组织攻击目标为全球金融机构，采用大规模发送恶意邮件的方式进行攻击，曾经大范围传播Dridex，Locky等恶意程序。近年来各国执法机构已针对该组织采取了多次打击行动，比如通过打击Dridex等僵尸网络来削弱其影响，但都没有起到明显效果，直至今日，TA505仍然在网络上非常活跃。

近日，奇安信威胁情报中心在日常样本监测中发现了TA505新的一轮攻击活动，本轮攻击中TA505仍然使用恶意邮件作为入口，诱使受害者通过邮件中的短链接下载恶意excel文档并启用宏，通过宏代码执行恶意功能，有趣的是恶意宏执行后会弹出一个进度条图片用于迷惑用户。

奇安信威胁情报中心将会对TA505攻击组织历史活动进行简单回顾，之后对本次活动进行详细分析。

#  **T** **A505** **历史活动回顾** ****

2014-2015年，传播Dridex僵尸网络，期间也分发了Shifu银行木马。2016年开始同时分发Locky勒索病毒与Dridex僵尸网络，之后主要以Locky为主。2017年还出现了传播Globelmposter勒索病毒的行为。

![图片.png](https://image.3001.net/images/20191024/1571912356_5db17aa458370.png!small)

2018年通过大规模发送恶意邮件传播FlawedAmmyy恶意软件，邮件附件为内嵌SettingContent-ms文件的恶意PDF文档，文档被打开后SettingContent-ms文件中的PowerShell命令会下载并执行FlawedAmmyy恶意软件。

![图片.png](https://image.3001.net/images/20191024/1571912367_5db17aafb9145.png!small)

2019年开始传播ServHelper后门，并且利用了当时刚公开不久的Excel4.0宏来加载恶意程序。

![图片.png](https://image.3001.net/images/20191024/1571912379_5db17abbaf045.png!small)

2019年9月，TA505开始使用新的下载者木马用于分发恶意软件，同时提升了攻击文档的迷惑性，本次攻击活动中分发了FlawedGrace，FlawedAmmyy，Snatch等多种恶意软件。

![图片.png](https://image.3001.net/images/20191024/1571912404_5db17ad4e2630.png!small)

#  **本次攻击流程图** ****

整体流程图如下:

![图片.png](https://image.3001.net/images/20191024/1571912422_5db17ae6d3c06.png!small)

#  **样本分析** ****

##  **Excel** **样本分析** ****

文件名|  schedule_Oct-Dec(1).xls  
---|---  
MD5| d68f7ad8bb1358b15924c4b51398135b  
SHA1| b1fec6a4dc7471fdc0e4bdef27c647dc449c9b34  
文件大小/Byte| 746,496  
  
样本名为schedule_Oct-Dec(1).xls，意为”10月到12月的时间表”，样本打开后会提示受保护的文档，要求用户启用宏，如果用户点击启用宏，文档中的恶意宏代码就会被执行。

![图片.png](https://image.3001.net/images/20191024/1571912432_5db17af0aba82.png!small)

宏代码入口在Excel对象Sem中。

样本将路径信息存储在UserForm3窗体中两个TextBox控件的Tag属性中。

![图片.png](https://image.3001.net/images/20191024/1571912448_5db17b0064382.png!small)

宏代码执行过程中会弹出一个进度条图片迷惑用户，并通过窗体的触发函数执行下一阶段恶意宏代码，其中ReplaceCurrentModule函数为主要功能函数。

![图片.png](https://image.3001.net/images/20191024/1571912462_5db17b0e644dd.png!small)

ReplaceCurrentModule函数会将样本表格中部分内容另存为临时路径下dependence.xls，之后将dependence.xls中oleObject1.bin提取到临时路径并从中解密出恶意dll，dll路径为C:\Documents
and
Settings\Administrator\Templates\hadstop1.dll，最后使用LoadLibraryW加载hadstop1.dl。

![图片.png](https://image.3001.net/images/20191024/1571912471_5db17b17e2141.png!small)

释放的dependence.xls截图如下，可见与样本本身完全一致。

![图片.png](https://image.3001.net/images/20191024/1571912479_5db17b1f66d3f.png!small)

##  **hadstop1.dll** **样本分析** ****

文件名|  hadstop1.dll  
---|---  
Dll导出名| fixup.dll  
MD5| 176a96a5338004245869bf82ed55f0b4  
SHA1| 69257644953428c5d85ae2977cf43c1e1e0e4131  
文件大小/Byte| 286,720  
编译时间| 2019/10/13 20:06:56 (5DA383E0)  
  
Hadstop1.dll作用为shellcode loader，负责解密并执行下一阶段shellcode。

![图片.png](https://image.3001.net/images/20191024/1571912487_5db17b271327e.png!small)

Shellcode会在内存中解密出下一阶段dll文件。

![图片.png](https://image.3001.net/images/20191024/1571912496_5db17b303b8d2.png!small)

在内存中执行PE加载操作后执行DllEntryPoint，此dll负责执行恶意功能。

![图片.png](https://image.3001.net/images/20191024/1571912501_5db17b35bf521.png!small)

##  **恶意功能dll分析** ****

Dll导出名|  getandgodll_Win32.dll  
---|---  
MD5| 3ce1c7e77bd3a4af2c94c57f8ad0eb3e  
SHA1| 3a26f8c4abe9d12fb6ae512dd8df2822a5b44865  
文件大小/Byte| 278,528  
编译时间| 2019/10/13 19:28:26 (5DA37ADA)  
  
Dll的恶意功能主要在导出函数Keio中实现，样本会搜集系统的计算机名，用户名，系统版本等信息，之后通过POST的方式上传到C2地址”
<https://office365-eu-update.com/2023>”，C2地址为硬编码在样本中。

![图片.png](https://image.3001.net/images/20191024/1571912508_5db17b3c7e272.png!small)

C2会返回给样本下一阶段恶意代码下载地址以及运行参数，如果返回数据含有参数”RD86”，说明返回的下载地址为dll文件，样本会将dll注入到自身进程并运行，如果没有”RD86”参数，说明返回下载地址为exe文件，样本会通过CreateProcessW直接执行。样本也会判断”RD64”参数，但是没有对应行为。

![图片.png](https://image.3001.net/images/20191024/1571912514_5db17b42eb9c1.png!small)

#  **总结** ****

TA505组织从被发现到今天已有近5年的时间，伴随着针对该组织的打击行动，其技术手段也在不断变化，从攻击的复杂度，演化路径及该组织曾使用的其他多类样本来看，TA505组织持续不断的在改进恶意程序以保证其攻击的有效性，而且从近几次攻击可以发现，TA505开始使用更具针对性的邮件内容和更具迷惑性的文档信息，从而提高受害者中招的概率，在此奇安信威胁情报中心提醒各位用户慎重点击来源不明的文档，防止受到恶意软件的攻击。

目前奇安信集团全线产品，包括天眼、SOC、态势感知、威胁情报平台，支持对涉及该报告相关的攻击活动检测，通过奇安信威胁情报平台对C2域名进行查询，可见已被标记为TA505组织。

#  **I** **OC** ****

##  **M** **D5** ****

d68f7ad8bb1358b15924c4b51398135b

176a96a5338004245869bf82ed55f0b4

##  **C** **2** ****

office365-eu-update.com

##  **文件名** ****

getandgodll_Win32.dll

fixup.dll

#  **参考链接** ****

[1][ _https://www.proofpoint.com/us/threat-insight/post/ta505-distributes-new-sdbbot-remote-access-trojan-get2-downloader_](https://www.proofpoint.com/us/threat-insight/post/ta505-distributes-new-sdbbot-remote-access-trojan-get2-downloader)

 __

[2][ _https://ti.qianxin.com/blog/articles/excel-4.0-macro-utilized-by-ta505-to-target-financial-institutions-recently/_](https://ti.qianxin.com/blog/articles/excel-4.0-macro-utilized-by-ta505-to-target-financial-institutions-recently/) __

 __

[3][ _https://ti.qianxin.com/blog/articles/excel-4.0-macro-utilized-by-ta505-to-target-financial-institutions-recently/_](https://ti.qianxin.com/blog/articles/excel-4.0-macro-utilized-by-ta505-to-target-financial-institutions-recently/)


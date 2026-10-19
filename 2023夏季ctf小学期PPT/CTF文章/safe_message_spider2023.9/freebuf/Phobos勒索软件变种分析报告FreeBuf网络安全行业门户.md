##  一、概述

**近日，安天CERT在梳理网络安全事件时发现Phobos勒索软件家族新变种，该勒索软件家族于2019年初被发现，并不断更新病毒变种。此变种最早于2019年9月末被发现，其传播方式主要为RDP暴力破解和钓鱼邮件。此勒索软件变种使用“RSA+AES”算法加密文件，暂时没有解密工具。程序运行后不仅加密文档文件还会加密可执行文件，并在加密后创建两种类型的勒索信，一种为txt格式，另一种为hta格式。Phobos勒索软件家族在全球多个行业扩散，感染面积大，变种更新频繁。**

我们分析发现，Phobos勒索软件家族与2016年出现的CrySIS/Dharma勒索软件家族所使用的加密方式、部分代码段、勒索信外观与内容，以及用于加密文件的命名方式都较为相似。不排除为同一作者或Phobos勒索软件攻击者购买、利用CrySIS/Dharma勒索软件相关代码。

经验证，安天智甲终端防御系统（英文简称IEP）可实现对Phobos勒索软件家族变种的查杀与有效防护。

##  二、Phobos勒索软件概览

表 2 1 Phobos勒索软件新变种概览

传播方式  |  RDP（远程桌面控制协议）暴力破解，钓鱼邮件  
---|---  
加密文件命名方式  |  <原文件名>+<原文件后缀名>+<勒索信中的个人ID>+<联系邮箱>+<.deal>  
联系方式  |  butters.felicio@aol.com  
加密文件类型  |  所有文件格式  
勒索币种与金额  |  比特币（实际金额通过邮箱与攻击者沟通后得知）  
是否有针对性  |  不具备针对性  
能否解密  |  暂时不能解密  
是否内网传播  |  否  
勒索信界面  |  ![](https://www.antiy.cn/images/20191016/20191016-1.png)  
  
###  2.1 Phobos勒索软件家族演进史

Phobos勒索软件家族从2019年初期开始在全球流行，并持续更新以致出现了大量变种。通过RDP暴力破解和钓鱼邮件等方式扩散到企业与个人用户中，感染数量持续增长。

![](https://image.3001.net/images/20191017/1571283734_5da7e316c7d77.png!small)

图2- 1 Phobos勒索软件家族变种演进史

##  三、Phobos勒索软件新变种样本分析

###  3.1 Phobos勒索软件新变种样本标签

表 3 1 Phobos勒索软件新变种样本信息

病毒名称  |  Trojan/Win32.Wacatac  
---|---  
原始文件名  |  AntiRecuvaAndDB.exe  
MD5  |  4CBCF650C75C6CD0CC16ED24C3B24DE6  
文件大小  |  50.5 KB (51,712 字节)  
时间戳  |  2019-06-19 08:00:06  
数字签名  |  无  
加壳类型  |  无  
编译语言  |  Microsoft Visual C++  
VT首次上传时间  |  2019-10-07 14:43:13  
VT检测结果  |  57/70  
  
###  3.2 被加密文件格式

此次勒索软件变种使用了“RSA+AES”加密算法对文件进行加密，加密后的文件名为：

<原文件名>+<原文件后缀名>+<勒索信中的个人ID>+<联系邮箱>+<.deal>

被加密文件如下图所示。

![](https://image.3001.net/images/20191017/1571283769_5da7e33968057.png!small)

图3- 1 被加密文件

###  3.3 Phobos勒索软件勒索信

该勒索软件变种加密后生成两种类型的勒索信，一种后缀名为.txt格式，另一种后缀名为.hta格式。此新变种勒索信内容与以往的Phobos勒索软件勒索信内容有所不同，Phobos勒索软件家族其它变种的勒索信中会告知受害者如何购买比特币支付赎金，但此变种的勒索信中并未体现，只表达了受害者的文件已被加密，并告知联系邮箱地址等信息。

![](https://image.3001.net/images/20191017/1571283778_5da7e342365b2.png!small)

图3- 2 txt格式勒索信内容对比

![](https://image.3001.net/images/20191017/1571283787_5da7e34bcc52e.png!small)

图3- 3 hta格式勒索信内容对比

###  3.4 Phobos勒索软件新变种行为分析

关闭系统防火墙

勒索软件利用netsh命令关闭防火墙。

![](https://image.3001.net/images/20191017/1571283800_5da7e358a83e5.png!small)

图3- 4 关闭并禁用防火墙

禁用并关闭防火墙，命令如下（两条命令功能相同，但适用于不同的操作系统）：

    
    
    netsh advfirewall set currentprofile state off
    
        netsh firewall set opmode mode=disable

添加注册表实现开机自启动

将自身复制到系统“启动”文件夹，实现自启动功能，路径如下：

> C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
>
> C:\Users\System\AppData\Roaming\Microsoft\Windows\Start
> Menu\Programs\Startup

![](https://image.3001.net/images/20191017/1571283822_5da7e36e0088b.png!small)

图3- 5 将自身复制到%Startup%启动文件夹中

![](https://image.3001.net/images/20191017/1571283836_5da7e37c193e3.png!small)

图3- 6 将自身复制到%AppData%启动文件夹中

添加注册表启动项，以达到开机启动的目的：

> HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
>
> HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run

将家族变种版本信息追加到加密文件中

该勒索软件变种对文件内容加密完成后，在文件末尾追加两部分数据。一部分为对应文件扩展名的加密数据，另一部分是该勒索软件家族的变种标识，使用不同的数据来区别不同版本的Phobos勒索软件变种。两个部分数据前面均通过“0”字节填充将其与加密内容分开。

![](https://image.3001.net/images/20191017/1571283844_5da7e384d1ea0.png!small)

图3- 7 文件末尾追加数据

##  四、防护建议与IEP防护视频演示链接

提醒广大用户，及时备份重要文件，且文件备份应与主机隔离；及时安装更新补丁，避免一切勒索软件利用漏洞感染计算机；对非可信来源的邮件保持警惕，避免打开附件或点击邮件中的链接；尽量避免打开社交媒体分享的来源不明的链接，给信任网站添加书签并通过书签访问；避免使用弱口令或统一的口令；确保所有的计算机在使用远程桌面服务时采取VPN连接等安全方式，如果业务上无需使用远程桌面服务，建议将其关闭；可以使用反病毒软件（如智甲）扫描邮件附件，确认安全后再运行。

目前，安天智甲终端防御系统可实现对Phobos勒索软件家族变种的查杀与有效防护。

![](https://image.3001.net/images/20191017/1571283851_5da7e38b921db.png!small)

图4- 1 智甲拦截防护界面

> Phobos勒索软件变种-无IEP防护视频演示链接：<https://v.qq.com/x/page/f3009m1k7r3.html>
>
> Phobos勒索软件变种-IEP防护视频演示链接：<https://v.qq.com/x/page/b3009ta9lj4.html>

 ***本文作者： antiylab，转载请注明来自FreeBuf.COM**  


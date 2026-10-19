**TrickBot木马最早发现于2016年，早期是一款专门针对银行发动攻击的木马程序，其攻击目标包括400余家知名国际银行。近年来，该木马不断地发展，其攻击范围已经不仅限于银行和金融企业，也拓展到了其他行业，其主要的目的是窃取企业和用户敏感信息。TrickBot木马的很多功能与另外一款银行木马程序Dyreza非常相似，其早期版本，没有任何字符串加密功能，也基本没有采用其他的对抗手段，但目前流行的TrickBot不仅使用了强大的加密功能，还使用了多种安全对抗技术，使得安全人员对其进行代码分析越来越困难。**

近期，亚信安全截获通过伪装成
“企业员工年度奖金计划报告”的垃圾邮件传播的TrickBot木马最新变种，用户一旦点击邮件中的链接，病毒母体文件（亚信安全检测为TrojanSpy.Win32.TRICKBOT.TIGOCFM）将会被执行，下载各种窃取信息和内网传播的模块，收集和窃取用户敏感信息，尤其是在新年伊始，企业正在进行年度汇总的特殊时期，需要严密防范此类垃圾邮件和钓鱼邮件攻击。

![](https://image.3001.net/images/20200106/1578298789_5e12eda5b3400.png!small)

##  **详细分析**

###  **TrickBot** **木马攻击流程：**

![](https://image.3001.net/images/20200106/1578298798_5e12edaea910b.png!small)

###  **TrickBot** **木马恶意模块**

![](https://image.3001.net/images/20200106/1578298805_5e12edb5619ef.png!small)

###  **母体文件分析**

本次截获的样本是MFC编写，伪装成dhtml2 MFC Application程序且具有合法的数字签名，具体文件信息如下：

![](https://image.3001.net/images/20200106/1578298832_5e12edd08e225.png!small)

该病毒首先获取资源模块BIZETTO数据，然后解密出恶意代码：

![](https://image.3001.net/images/20200106/1578298856_5e12ede80412c.png!small)![](https://image.3001.net/images/20200106/1578298872_5e12edf84ec5c.png!small)

![](https://image.3001.net/images/20200106/1578298888_5e12ee08e1841.png!small)

病毒首先会访问远端C&C服务器地址hxxps://myxxxxxxxxalip.com/raw获取IP地址：

![](https://image.3001.net/images/20200106/1578298905_5e12ee1916731.png!small)![](https://image.3001.net/images/20200106/1578298924_5e12ee2c82b93.png!small)![](https://image.3001.net/images/20200106/1578298938_5e12ee3af2db1.png!small)

然后继续解密和整理出恶意的PowerShell命令并执行，其主要功能是从远端C&C服务器下载其核心的TrickBot Loader程序：

![](https://image.3001.net/images/20200106/1578298953_5e12ee494ad8e.png!small)![](https://image.3001.net/images/20200106/1578298966_5e12ee56815be.png!small)![](https://image.3001.net/images/20200106/1578298978_5e12ee62af0c4.png!small)

PowerShell脚本的主要功能是下载其核心的TrickBot Loader程序到本地临时目录，然后执行。具体脚本代码以及运行进程如下所示：

![](https://image.3001.net/images/20200106/1578298994_5e12ee723e8ad.png!small)![](https://image.3001.net/images/20200106/1578299002_5e12ee7a03431.png!small)![](https://image.3001.net/images/20200106/1578299006_5e12ee7e8c091.png!small)

###  **TrickBot Loader** **程序分析**

从之前的PowerShell脚本内容可知，下载后的文件首先需要进行XOR后才可以执行。具体文件内容如下所示：

![](https://image.3001.net/images/20200106/1578299026_5e12ee9236415.png!small)

其会将自身复制到ProgramData目录中并且执行，如果该文件已经存在，其将会执行后续的恶意行为：

![](https://image.3001.net/images/20200106/1578299038_5e12ee9ed9353.png!small)

其首先从资源模块读取相关数据，然后进行多次解密：

![](https://image.3001.net/images/20200106/1578299050_5e12eeaa77af5.png!small)

![](https://image.3001.net/images/20200106/1578299059_5e12eeb3e8baa.png!small)

获取系统信息版本以便确定后续的下载和加载的模块版本：

![](https://image.3001.net/images/20200106/1578299074_5e12eec28ca19.png!small)

加载特定的DLL文件来检测是否存在杀毒软件，其对应关系如下：

特定DLL文件  |  杀毒软件  
---|---  
cmdvrt32.dll  |  科摩多网络安全套装 COMODO Internet Security  
snxhk.dll  |  AVAST  
  
![](https://image.3001.net/images/20200106/1578299097_5e12eed98edf9.png!small)![](https://image.3001.net/images/20200106/1578299108_5e12eee48bee8.png!small)

该程序多次且频繁进行解密出需要运行的恶意代码，增加调试难度：

![](https://image.3001.net/images/20200106/1578299122_5e12eef220a6f.png!small)![](https://image.3001.net/images/20200106/1578299135_5e12eeffdf079.png!small)

下载恶意模块，注入到explorer.exe进程中执行：

![](https://image.3001.net/images/20200106/1578299149_5e12ef0d93755.png!small)

![](https://image.3001.net/images/20200106/1578299160_5e12ef1894001.png!small)

![](https://image.3001.net/images/20200106/1578299170_5e12ef227b655.png!small)

通过创建计划任务进行本地持久化：

![](https://image.3001.net/images/20200106/1578299194_5e12ef3a6cb24.png!small)

###  **TrickBot** **木马恶意模块作用**

TrickBot木马持续对其恶意模块进行更新和修改，然后通过远程服务器进行下发，从首次发现至今，已经存在多个恶意模块，覆盖了多个功能，其中包括邮件信息收集，浏览器数据窃取以及内网扩散等模块。具体模块与其对应功能如下：

**模块名称** |  **功能类型** |  **具体功能**  
---|---|---  
pwgrab32  |  数据窃取  |  窃取来自Filezilla，Microsoft Outlook和WinSCP等应用程序的凭据。  
shareDll32  |  内网渗透  |  在整个网络中进行自我传播  
wormDll32  |  内网渗透  |  尝试使用NetServerEnum和LDAP查询识别网络中的服务器和域控制器  
networkDll32  |  内网渗透和数据窃取  |  扫描网络并窃取相关网络信息  
importDll32  |  数据窃取  |  负责窃取浏览器数据，例如浏览历史记录，Cookie和插件等  
systeminfo32  |  数据窃取  |  收集系统信息，如操作系统，CPU和内存信息，用户帐户，已安装程序和服务的列表。  
mailsearche***  |  数据窃取  |  搜索受感染系统的文件以收集电子邮件地址以进行信息窃取。  
injectDll32  |  数据窃取  |  执行Web浏览器注入窃取金融账户信息  
  
扫描网络和窃取网络信息：

![](https://image.3001.net/images/20200106/1578299210_5e12ef4abefaf.png!small)

![](https://image.3001.net/images/20200106/1578299231_5e12ef5f07200.png!small)

##  **解决方案**

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装；
>
> 请到正规网站下载应用程序；
>
> 浏览网页的时候不随意下载安装程序；
>
> 请注意备份重要文档。备份的最佳做法是采取3-2-1规则，即至少做三个副本，用两种不同格式保存，并将副本放在异地存储。

**IOC**

**文件** **SHA-1** |  **文件名称** |  **亚信安全检测名**  
---|---|---  
880cecc01ecc88500e22d33dc9d0c762  |  Print.exe  |
TrojanSpy.Win32.TRICKBOT.TIGOCFM  
  
***本文作者： 亚信安全，转载请注明来自FreeBuf.COM**  
  
  
  
  


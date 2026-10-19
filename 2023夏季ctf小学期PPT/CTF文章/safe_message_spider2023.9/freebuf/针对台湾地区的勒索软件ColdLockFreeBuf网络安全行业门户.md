**近期名为ColdLock的勒索软件有针对性的攻击了台湾地区的几个组织，勒索软件会对数据库和电子邮件服务器进行加密。该攻击开始于5月初，对恶意软件的分析表明，ColdLock与Lockergoga，Freezing和EDA2勒索软件具有相似性。**

##  传播方式

目前尚不清楚攻击者是如何进入受害者网络，可以确定的是攻击者以某种方式获得了目标组织Active
Directory服务器的访问权限，从而下载勒索软件并在目标域内运行。

有效负载是.NET可执行文件（.DLL文件）的形式，文件使用ConfuserEx进行包装，使用PowerShell反射加载来运行DLL文件：

![](https://image.3001.net/images/20200512/1589253958_5eba17463b0e8.png!small)它还包含两项检查，
首先检查是否存在%System Root%\ProgramData\readme.tmp，防止系统受到相同感染：

![](https://image.3001.net/images/20200512/1589254033_5eba1791e727b.png!small)之后检查系统时间，它只会在下午12:10或之后运行，如果时间更早，它将休眠15秒钟，直到符合时间条件。

![](https://image.3001.net/images/20200512/1589254112_5eba17e088789.png!small)

##  加密方式

在加密任何文件之前，如果服务正在运行，它将终止系统上的多个服务：

> mariadb
>
> msexchangeis
>
> mssql
>
> mysql
>
> oracleservice

它还将终止Outlook进程。

![](https://image.3001.net/images/20200512/1589254230_5eba18565d729.png!small)它还会检查系统上运行的Windows版本。
如果运行的是Windows 10，它将执行多个Windows 10特定的进程。禁用Windows
Defender，无法将恶意软件样本发送给Microsoft，推送通知也被禁用。

![](https://image.3001.net/images/20200512/1589254309_5eba18a51a580.png!small)加密时将避开以下目录：

> %System Root%\Program Files
>
> %System Root%\Program Files (x86)
>
> %System Root%\ProgramData
>
> %System Root%\Users\all users
>
> %System Root%\Users\default
>
> {malware directory}
>
> {drive letter}:\System Volume Information
>
> {drive letter}:\$Recycle.bin

以下目录仍会被加密（上述列表的例外）：

> %System Root%\ProgramData\Microsoft\Windows\Start Menu  
>  [](https://www.freebuf.com/wp-admin/post.php?post=236451&action=edit)
>
> %System Root%\Program Files\Microsoft\Exchange Server
>
> %System Root%\Program Files (x86)\Microsoft\Exchange Server
>
> Directories under (Program Files, Program Files (x86), and ProgramData)
> containing any of the following strings:sql、mariadb、oracle

其他目录中的文件是否被加密取决于三个条件：

1、目录中文件数量是否小于100

2、目录中最新写入时间是否晚于2018年1月

3、目录名字不包括以下字符串：

> .git
>
> appdata
>
> cache
>
> image
>
> lib
>
> log
>
> logs
>
> microsoft
>
> reference
>
> res
>
> resource
>
> script
>
> setup
>
> skin
>
> temp
>
> theme
>
> third_party
>
> thirdparty

如果满足上述所有条件，它将加密目录中的所有文件，除以下扩展名的文件：

> .avi
>
> .dll
>
> .gif
>
> .iso
>
> .m2ts
>
> .mkv
>
> .mov
>
> .mp3
>
> .msi
>
> .ocx
>
> .tmp
>
> .wmv

不满足部分或全部条件的情况下，它将仅加密以下扩展名的文件：

> .7z
>
> .aspx
>
> .bak
>
> .cpp
>
> .csv
>
> .doc
>
> .docx
>
> .gz
>
> .hwp
>
> .java
>
> .jpg
>
> .jsp
>
> .lnk
>
> .odt
>
> .one
>
> .php
>
> .ppt
>
> .pptx
>
> .pst
>
> .rar
>
> .sh
>
> .sql
>
> .txt
>
> .xls
>
> .xlsx
>
> .xml
>
> .zip

加密黑名单和白名单代码：

![](https://image.3001.net/images/20200512/1589254796_5eba1a8c8355e.png!small)加密采用AES
CBC模式，使用盐和secret key生成所需的密钥和初始化向量（IV），
前者嵌入在代码中，而后者则使用随机生成的32字节长字符串的SHA-256哈希值。 然后，使用硬编码RSA密钥对此进行加密，加密文件为.locked后缀。

AES加密代码：

![](https://image.3001.net/images/20200512/1589254992_5eba1b503273c.png!small)Secret
key生成：

![](https://image.3001.net/images/20200512/1589255011_5eba1b6332c9b.png!small)勒索信息会保存在系统以下位置：

> %Desktop%\How To Unlock Files.Txt
>
> %System Root%\ProgramData\readme.tmp
>
> %User Startup%\How To Unlock Files.Txt
>
> {Encrypted Drive}:\How To Unlock Files.Txt

![](https://image.3001.net/images/20200512/1589255077_5eba1ba5c9b8a.png!small)勒索软件会为更改系统壁纸，显示赎金说明。

##
![](https://image.3001.net/images/20200512/1589255137_5eba1be17b0f6.png!small)

##  总结

表面上看该勒索软件似乎与Lockergoga有关，因为它们加密文件（.locked）有相同扩展名，但其他勒索软件也使用此扩展名。它与Freezing勒索软件家族在域网络传播上使用了相似的方法。该代码还与开源EDA2勒索软件具有相似之处。

勒索软件案件数量从2018年的5500万上升至2019年的6100万，此类威胁更加危险，勒索软件会攻击企业系统并在企业网络内部传播。可以采取以下方法保护系统：

> 1、使用3-2-1规则定期备份文件，以两种不同格式创建三个备份，并在异地存储一个副本。
>
> 2、定期修补和更新应用程序，软件和操作系统。
>
> 3、使用沙箱分析，在隔离环境中执行恶意文件。

##  IOCs

![](https://image.3001.net/images/20200512/1589266134_5eba46d6ba382.png!small)***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/targeted-ransomware-attack-hits-******ese-organizations/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Anti-MalwareBlog+%28Trendlabs+Security+Intelligence+Blog%29)，由Kriston编译，转载请注明来自FreeBuf.COM**

  


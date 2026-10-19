# ****背景概述****

秋收时节，海内外勒索事件不断，在老牌勒索病毒家族不断活跃的情况下，不断有新型的勒索病毒家族出现，近期深信服安服应急响应中心与终端安全团队捕获了一个新型的勒索病毒家族。

该勒索病毒具备了常见的反调试、结束安全软件、加密、删除自身等多个功能。根据加密后缀和在勒索信中留下的邮箱信息，安全专家将其命名为KOXIC勒索病毒，目前暂无公开的解密工具。![](https://image.3001.net/images/20210926/1632626676_614fe7f4a9167cc003d33.png!small)

KOXIC勒索信

#  ** **病毒分析****

![](https://image.3001.net/images/20210926/1632626690_614fe802aba47fcc61ece.png!small)

KOXIC勒索病毒功能列表

##  ** **对抗功能****

###  **反调试**

利用了CheckRemoteDebuggerPresent、IsDebuggerPresent函数判断程序是否被调试，如果被调试则结束程序本身。![](https://image.3001.net/images/20210926/1632626701_614fe80da36be1eed82ab.png!small)

###  **结束安全软件和数据软件**

利用LoadLibraryW函数获取需要用到的dll，并利用动态遍历函数名称对应的序号方式动态获取需要用到的API函数地址。![](https://image.3001.net/images/20210926/1632626714_614fe81ad2015e0950452.png!small)

接着在注册表中关闭了defender相关的安全功能。![](https://image.3001.net/images/20210926/1632626728_614fe82850db62f2ac4da.png!small)

使用工具结束安全软件进程。![](https://image.3001.net/images/20210926/1632626739_614fe833af53bd519ad32.png!small)

停止数据库相关服务。![](https://image.3001.net/images/20210926/1632626752_614fe8406565fa503388e.png!small)

##  ** **加密前****

###  **解密勒索相关信息**

将数据依次传入内存中，并利用异或的方式动态解密出加密后缀以及勒索的文本信息等。![](https://image.3001.net/images/20210926/1632626794_614fe86ab347c549927ee.png!small)![](https://image.3001.net/images/20210926/1632626818_614fe882aa8afccafc2cf.png!small)

勒索后缀为：KOXIC_KRSJO.![](https://image.3001.net/images/20210926/1632626831_614fe88f0b4a81ec4cffa.png!small)

勒索所生成的txt名称为：WANNA_RECOVER_KOXIC_FILEZ_KRSJO.txt![](https://image.3001.net/images/20210926/1632626840_614fe8981e8ea61109d8f.png!small)

![](https://image.3001.net/images/20210926/1632626848_614fe8a0aa57b773c6c19.png!small)

###  **提权：**

利用OpenProcessToken得到进程的令牌句柄提升自身程序权限。![](https://image.3001.net/images/20210926/1632626864_614fe8b0d7e22e69033c5.png!small)

###  **主机** **信息获取** **：**

循环执行命令获取主机信息以及IP地址等，并将信息输出到%temp%目录中![](https://image.3001.net/images/20210926/1632626879_614fe8bfd1cfc074891ff.png!small)![](https://image.3001.net/images/20210926/1632626888_614fe8c82074af40ded38.png!small)

信息其中包括了：CPU、计算机名、计算机组、操作系统版本、IP地址等。![](https://image.3001.net/images/20210926/1632626905_614fe8d918883dc4b5723.png!small)

  

##  ** **加密**** ** **中**** ** **：****

该函数为勒索主要功能，实现了盘符遍历、文件遍历、文件判断、国家判断、和文件加密等功能。![](https://image.3001.net/images/20210926/1632626920_614fe8e8982f9c1bcaea9.png!small)

循环遍历，获取当前主机的盘符和分区信息。![](https://image.3001.net/images/20210926/1632626969_614fe91956c222f45b83b.png!small)

确认后对磁盘的所有文件进行遍历。![](https://image.3001.net/images/20210926/1632626979_614fe923a4842603bed8f.png!small)

对文件进行判断。![](https://image.3001.net/images/20210926/1632626990_614fe92e3f665848e4f87.png!small)

勒索事先已将系统重要文件进行设置，避免在文件加密时将系统重要文件进行加密。![](https://image.3001.net/images/20210926/1632627007_614fe93f9f82cc0bed353.png!small)

该勒索主要勒索的文件类型，依次可以判断出该勒索主要勒索对象是数据库等重要数据设施。![](https://image.3001.net/images/20210926/1632627020_614fe94cbf71691f4a43f.png!small)

确认类型后，在该文件目录生成勒索文本信息。![](https://image.3001.net/images/20210926/1632627030_614fe95602e71b1e6dd14.png!small)![](https://image.3001.net/images/20210926/1632627038_614fe95e72f922a745ea7.png!small)

最后将文件映射到内存，实现对文件进行加密的目的。![](https://image.3001.net/images/20210926/1632627057_614fe971680aeaf5af273.png!small)

将其后缀增加.KOXIC_TSVTF，执行完402220加密函数后，文件数据被加密。

![](https://image.3001.net/images/20210926/1632627066_614fe97aa9e77f452eca8.png!small)![](https://image.3001.net/images/20210926/1632627074_614fe9826d58deda41a63.png!small)

查看文件内容，已完成加密。![](https://image.3001.net/images/20210926/1632627087_614fe98faa8989ded5616.png!small)

##  ** **加密后****

###  **弹出勒索信息：**

利用notepad将%TEMP%目录中的勒索信息弹出。![](https://image.3001.net/images/20210926/1632627098_614fe99ad5278e7b0854a.png!small)

###  **清理现场：**

利用ping达到延时的目的，延时完毕后，删除自身。![](https://image.3001.net/images/20210926/1632627109_614fe9a55e5aa575613c4.png!small)

#  ** **加固建议****

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。


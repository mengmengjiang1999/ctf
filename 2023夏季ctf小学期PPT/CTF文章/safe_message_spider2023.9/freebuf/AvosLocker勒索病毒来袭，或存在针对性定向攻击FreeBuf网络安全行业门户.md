## **背景概述**

2021年6月底，研究人员发现AvosLocker勒索病毒，全球各地都有企业遭受攻击，赎金要求从5万美元到7.5万美元不等。其中美国韩裔社区银行服务提供商之一太平洋银行和中国台湾计算机硬件生产商技嘉科技都在9月和10月遭受过AvosLocker勒索团伙的攻击。

深信服安服应急响应中心近期捕获了AvosLocker勒索病毒的新样本，根据其 **后缀名为avos2** 的特征，推测有可能为
**AvosLocker变种** 。

根据分析，勒索软件执行流程如下图：

![](https://image.3001.net/images/20211116/1637065615_6193a38f466d1a3b94b36.png!small)

生成的勒索信息，值得注意的是，该样本无论在任何机器上运行，生成的ID均相同，推测该样本为 **定向攻击** ；

![](https://image.3001.net/images/20211116/1637065638_6193a3a67f9a02ebf00cf.png!small)

如下图为固定的ID及RSA公钥：

![](https://image.3001.net/images/20211116/1637065651_6193a3b39de09f2cc5ddc.png!small)

修改的勒索桌面：

![](https://image.3001.net/images/20211116/1637065663_6193a3bf7a47296d0f29c.png!small)

目前深信服EDR支持对该病毒进行检测：

![](https://image.3001.net/images/20211116/1637065678_6193a3ceba73b4da606c7.png!small)

##  **样本分析**

###
**1、基本信息**![](https://image.3001.net/images/20211116/1637065700_6193a3e4666635da24190.png!small)

编译时间 2021-09-17 12:01:34

###  **2、功能**

该勒索程序可以使用-h来输出使用参数，此外也注意到该勒索程序原名可能为Sonic。

如下图所示，功能包含对指定路径进行加密、爆破SMB加密共享磁盘、隐藏输出、调整加密线程等：

![](https://image.3001.net/images/20211116/1637065721_6193a3f919256549b176b.png!small)

###  **3、执行流程**

 **3.1前期准备**

勒索病毒启动后创建互斥量Zheic0WaWie6zeiy，防止重复加密。该功能可通过参数进行控制，默认开启此功能：

![](https://image.3001.net/images/20211116/1637065749_6193a4155efd03bc4fc06.png!small)![](https://image.3001.net/images/20211116/1637065759_6193a41f443a9d5912737.png!small)

创建IO队列端口，该队列用来在多线程中共享加密文件路径：

![](https://image.3001.net/images/20211116/1637065780_6193a4341c6a590b3552d.png!small)

根据参数创建线程，默认200，并设置线程优先级为最高：

![](https://image.3001.net/images/20211116/1637065796_6193a4441d05727e77683.png!small)

枚举网络共享及本地磁盘：

![](https://image.3001.net/images/20211116/1637065812_6193a454d8cb42a97d0ce.png!small)

 **3.2查找文件**

解密出文件后缀名，排除带有以下后缀名的文件：

avos、avoslinux、avos2、avos2j、themepack、nls、diagpkg、msi、lnk、exe、cab、scr、bat、drv、rtp、msp、prf、msc、ico、key
ocx 、diagcab、diagcfg、pdb、wpx、hlp、icns、rom、dll、msstyles、
mod、ps1、ics、hta、bin、cmd、ani、386、lock、cur、idx、sys、com、deskthemepack、shs、ldf、theme、mpa、nomedia
spl、cpl、adv、icl、msu

![](https://image.3001.net/images/20211116/1637065825_6193a461931305b028c60.png!small)

解密出其他文件夹名称，勒索程序不会加密以下文件夹中的内容：

![](https://image.3001.net/images/20211116/1637065838_6193a46eb8bf64083ec97.png!small)

向每一个可加密的目录写入勒索信息：

![](https://image.3001.net/images/20211116/1637065851_6193a47b92b5452fec25b.png!small)

完成文件名判断后，将绝对路径发送给共享队列：

![](https://image.3001.net/images/20211116/1637065868_6193a48c17b2dc741faca.png!small)

使用RmStartSession、RmRegisterResources、RmGetList中断文件占用：

![](https://image.3001.net/images/20211116/1637065887_6193a49f4d3848ad18158.png!small)

 **3.3加密过程**

从Queue中获取文件路径：

![](https://image.3001.net/images/20211116/1637065908_6193a4b4ebabb73c24b7a.png!small)

跳过属性为FILE_ATTRIBUTE_SYSTEM的文件（系统文件）：

![](https://image.3001.net/images/20211116/1637065922_6193a4c229c39ded635b1.png!small)

如果文件FILE_ATTRIBUTE_READONLY（只读），则修改文件属性为NORMAL：

![](https://image.3001.net/images/20211116/1637065932_6193a4cc34fed5d93fc3f.png!small)

使用内置的RSA公钥进行加密：

![](https://image.3001.net/images/20211116/1637065944_6193a4d8d42f842ba60c7.png!small)

使用chacha20对文件末尾添加的加密信息进行加密：

![](https://image.3001.net/images/20211116/1637065960_6193a4e8b5ed389c8374a.png!small)

在加密完成后的文件末尾附加加密相关信息：

![](https://image.3001.net/images/20211116/1637065974_6193a4f6f3b20820036bb.png!small)

加密完成后给文件附加上“avo2”后缀并修改桌面背景：

![](https://image.3001.net/images/20211116/1637065990_6193a5069d8631a71b73e.png!small)

##  **安全防护**

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。


## 背景介绍  
 ****

**随着疫情的缓解，各地企业纷纷复工，而勒索病毒家族也并没有停下他们的脚步。近期深信服安全团队就收到多个地区关于用户主机遭受大面积.**H勒索病毒入侵的求助，经过安全团队分析，确认为GlobeImposter勒索病毒家族的最新变种。**

GlobeImposter家族首次出现的时间为2017年5月，随后在2018与2019年出现不同系列的变种，如：以特征字符“.Dragon4444
.Snake4444 .Horse4444 .Goat4444 .Monkey4444”等的“十二生肖”系列，与以“希腊十二主神+
666”为特征的“十二主神”系列等。

攻击者常常通过暴力破解服务器密码，对内网服务器发起扫描并人工投放GlobeImposter勒索病毒进行勒索。

## 一、变种概述

> 病毒变种版本：**H.exe
>
> MD5值：3af2e34e2b5e3632c0c99de82ac5a6e4
>
> SHA256值：987dbef97c27a6f1f45417d3d29eafdf9dcc8c7dee0ef659d0bf0e5424a00b8c

本次主要分析的是GlobeImposter的新变种“C*H”系列中的C3H/**H。该病毒依然使用勒索病毒中常见的RSA+AES加密算法进行加密。

此次变种与18年出现过的版本的不同之处包括但不仅限于以下几点：

> 1、不同于初始版本需要解密才能获得RSA加密相关信息和最后执行的bat脚本，此次变种中将这两者直接以明文的形式写在了程序中。
>
> 2、在设置自启动的注册表键值中进行了调整，从BrowserUpdateCheck调整为CertificatesCheck。
>
> 3、程序执行的过程和步骤顺序进行了调整。
>
> 4、 程序只有一个可执行可写的.rdata段，与我们常见的PE文件拥有多个段并以.test段为代码段不同，查壳工具会认为有壳。

## 二、加密流程

勒索病毒首先拥有一个的RSA公钥（A）。对于当前用户主机，会使用RSA生成一对新的RSA公钥私钥（B）。

其中生成信密钥（B）使用原RSA公钥（A）进行加密后，作为用户ID。

在对系统的文件进行遍历与加密的过程中，对每个文件生成其对应的AES密钥，进行加密。加密文件后，又会将信息与ID通过RSA（B）进行加密并追加在加密文件的末尾。实现勒索。

如果黑客需要解密，只要通过自己的RSA私钥（A），对用户的ID进行解密，就可以得到RSA私钥（B），从而解密文件的末尾得到AES的密钥，再解密出原始文件。

## 三、病毒行为

1、对主流的文件类型加密并添加后缀”.**H”

![](https://image.3001.net/images/20200516/1589598740_5ebf5a140679e.png!small)

2、每个目录下生成一个勒索文档Decryption Info.html

![](https://image.3001.net/images/20200516/1589598853_5ebf5a856a917.png!small)

![](https://image.3001.net/images/20200516/1589598860_5ebf5a8cc5edb.png!small)

3、行为工具监控查看

（1）.执行监控：会创建子程序和cmd命令行进行执行，随后结束；

![](https://image.3001.net/images/20200516/1589598915_5ebf5ac327216.png!small)

（2）.文件监控：大量文件被改写；

![](https://image.3001.net/images/20200516/1589598928_5ebf5ad09607d.png!small)

（3）.注册表监控：改写注册表，如设置自启动等；

![](https://image.3001.net/images/20200516/1589598941_5ebf5add65956.png!small)

（4）.网络行为：无网络行为

## 四、技术分析

### 1、文件结构

该文件只有一个可执行可写的.rdata段，怀疑企图通过这种方式逃过扫描，里面存放了的start函数中只有一个main函数，ida反汇编查看结构相对清晰。

![](https://image.3001.net/images/20200516/1589599084_5ebf5b6c3862b.png!small)

### 2、SHA加密密钥

首先程序会将512位的字符串作为参数传入函数中，计算出SHA256的数值作为一份密钥，为后续加密与解密做准备。此处怀疑长字符串与RSA有关。

![](https://image.3001.net/images/20200516/1589599123_5ebf5b9368111.png!small)

![](https://image.3001.net/images/20200516/1589599144_5ebf5ba861038.png!small)

### 3、解密字符串

随后，程序会利用上一步中SHA加密得到的值作为密钥，对程序中的一些资源进行解密；

![](https://image.3001.net/images/20200516/1589599163_5ebf5bbbf1e22.png!small)

分别解密出了勒索文档的名称；

![](https://image.3001.net/images/20200516/1589599178_5ebf5bcaa0218.png!small)

大量Windows系统相关的字符串：

![](https://image.3001.net/images/20200516/1589599187_5ebf5bd38fc47.png!small)

大量罕见的文件格式：

![](https://image.3001.net/images/20200516/1589599197_5ebf5bdd4f427.png!small)

以及后续加密将要用到的密钥：

![](https://image.3001.net/images/20200516/1589599206_5ebf5be68372e.png!small)

（此处.C3H和.**H仅文字上区别，并无实质或版本区别）

初步判断文件格式和与windows有关的字符串是程序将要避开的目标。

### 4、自我复制

随后会获取系统上某一特定路径，将自身复制到该路径上；

![](https://image.3001.net/images/20200516/1589599245_5ebf5c0de1a17.png!small)

利用了GetEnvironmentVariableW，CopyFileW等API函数。

### 5、设置注册表键值

![](https://image.3001.net/images/20200516/1589599263_5ebf5c1fda76c.png!small)

设置了自启动的注册表键值，此处使用了CertificatesCheck，在以前的版本中使用了BrowserUpdateCheck，发生了变化。

### 6、生成用户专属文件

![](https://image.3001.net/images/20200516/1589599314_5ebf5c52c568b.png!small)

其中解密出的字符串是通过利用0123456789ABCDEF进行简单的运算解密出的哈希字符串；

随后通过附加在目录后，去创建用户专属ID的文件，内部保存一些用户的信息；

![](https://image.3001.net/images/20200516/1589599325_5ebf5c5d91b1e.png!small)

随后通过RSA加密算法，对ID文件的内容进行加密；

![](https://image.3001.net/images/20200516/1589599336_5ebf5c684305a.png!small)

再将内容写入文件中，内容如下：

![](https://image.3001.net/images/20200516/1589599346_5ebf5c7215b33.png!small)

### 7、勒索文档的生成

![](https://image.3001.net/images/20200516/1589599404_5ebf5cace3abf.png!small)

生成了Decryption Info.html

### 8、 结束进程

遍历C:\Windows\system32目录下的程序，如果运行中就先结束；

![](https://image.3001.net/images/20200516/1589599428_5ebf5cc4d46fb.png!small)

在动态调试过程中发现主要遍历了一些exe文件，查看是否有对应的进程在运行中，有则结束。

### 9、文件加密

文件加密时首先通过GetLogicalDrives和GetDriveTypeA等API获取磁盘的信息，然后对每一个盘开启一个线程进行加密。线程开启的encrypt函数主要参数为v18，它通过偏移分别包括了加密的key，用户的ID（上面生成的，也会作为加密的信息进行加密），以及文件的路径。

![](https://image.3001.net/images/20200516/1589599498_5ebf5d0a5dd80.png!small)

对文件加密的过程主要用到了AES算法，并且在程序中直接实现，而不是调用API；

![](https://image.3001.net/images/20200516/1589599510_5ebf5d16cb181.png!small)

先利用RSA公钥去加密“010001”写入文件后面，然后再把用户ID写入文件末尾；

![](https://image.3001.net/images/20200516/1589599526_5ebf5d26d18d4.png!small)

从而完成加密，再通过循环不断加密下一个文件。

![](https://image.3001.net/images/20200516/1589599543_5ebf5d37599c0.png!small)

### 10、执行bat脚本

![](https://image.3001.net/images/20200516/1589599594_5ebf5d6ae176b.png!small)

脚本会删除注册表中“Terminal Server Client”中的键值，删除远程桌面连接信息文件default.rdp，还会通过wevtutil.exe
cl的命令清除日志的相关信息。

### 11、自我删除

![](https://image.3001.net/images/20200516/1589599615_5ebf5d7fa52d3.png!small)

通过调用CMD /c del来实现自删除。

## 五、解决方案

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

### 加固建议

> 1.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；
>
> 2.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；
>
> 3.定期使用安全软件进行全盘扫描和处置，定期检测系统漏洞并且进行补丁修复。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**


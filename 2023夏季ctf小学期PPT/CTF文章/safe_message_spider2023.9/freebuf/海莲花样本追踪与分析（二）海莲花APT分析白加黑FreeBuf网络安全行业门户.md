## 一.前言

前文《[海莲花样本追踪与分析（一）](https://www.freebuf.com/articles/system/280679.html)》

这是第二更，针对“白加黑”程序的分析，欢迎各位大佬骚扰，指正，话不多说，进入正题。

补充：所谓的“白加黑”恶意程序也就是利用了合法证书的程序来调用恶意的dll程序实现恶意程序的运行。

## 二.分析过程

分析过程分别从静态和动态做了一定的说明详细如下：

### 2.1 基础信息

样本名称：PROPSYS.dll

样本md5:4780A6131A2461220971E86E2AF0EC07

样本名称：acrobatupdater.exe

样本md5: 31657ADA786863B73FAC28E5BD0753AD

分析：

通过样本信息分析，该exe程序属于Adobe旗下的一款工具，该程序为合法程序：

![1626230117_60ee4d65a2c3597f08206.png!small?1626230120409](https://image.3001.net/images/20210714/1626230117_60ee4d65a2c3597f08206.png!small?1626230120409)

  

调用的dll程序并未包含正常签名疑似恶意程序，该程序主要利用合法的exe来进行调用执行：

![1626230245_60ee4de56a33567a28e29.png!small?1626230245848](https://image.3001.net/images/20210714/1626230245_60ee4de56a33567a28e29.png!small?1626230245848)

### 2.2 静态分析

创建互斥量：947a24f6-275d-4051-8df8-c187a97f65f2，并调用sub_10001AE0函数读取shellcode：

![1626230327_60ee4e3792dab16ef14f4.png!small?1626230330227](https://image.3001.net/images/20210714/1626230327_60ee4e3792dab16ef14f4.png!small?1626230330227)函数主要是读取资源块中的数据，将数据copy到利用VirtualAlloc函数创建的拥有可读可写可执行的空间中了，并利用CreateThread创建新线程，在线程中执行读取出来的shellcode：

![1626230354_60ee4e52933d3ce070ef9.png!small?1626230356031](https://image.3001.net/images/20210714/1626230354_60ee4e52933d3ce070ef9.png!small?1626230356031)

![1626230374_60ee4e662603a768c6ad4.png!small?1626230378559](https://image.3001.net/images/20210714/1626230374_60ee4e662603a768c6ad4.png!small?1626230378559)

### 2.3 动态分析

Shellcode入口位置进行了多次循环解密：

![1626230405_60ee4e851b32274df1a6f.png!small?1626230407230](https://image.3001.net/images/20210714/1626230405_60ee4e851b32274df1a6f.png!small?1626230407230)

创建线程，执行完毕退出后跳转到CobaltStrike的上线、控制模块dll当中：

![1626230422_60ee4e969979d25250a59.png!small?1626230423473](https://image.3001.net/images/20210714/1626230422_60ee4e969979d25250a59.png!small?1626230423473)

CobaltStrike上线、控制模块dll：

![1626230438_60ee4ea6c103aca6f92af.png!small?1626230439840](https://image.3001.net/images/20210714/1626230438_60ee4ea6c103aca6f92af.png!small?1626230439840)

进入控制模块：

![1626230451_60ee4eb3e0ed11e538625.png!small?1626230454028](https://image.3001.net/images/20210714/1626230451_60ee4eb3e0ed11e538625.png!small?1626230454028)

解析出的C2：

185.225.19.100,/viwwwsogou  
sjbingdu.info,/viwwwsogou

![1626230466_60ee4ec29f284ad6b5849.png!small?1626230468261](https://image.3001.net/images/20210714/1626230466_60ee4ec29f284ad6b5849.png!small?1626230468261)

## 三.总结

程序本身没有问题，在于攻击者是如何调用正常程序的函数，引导成自己所需的效果，最终控制主机；对于用户而已，需要小心一切的一切，保障终端安全，确保数据不被泄露，权限不被控制，终端安全极为重要。


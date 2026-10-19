![1602229317_5f80144589084bb64c151.png!small](https://image.3001.net/images/20201009/1602229317_5f80144589084bb64c151.png!small)

## 概述

"海莲花"（OceanLotus），被认为是来自越南的APT攻击组织，自2012年活跃以来，一直针对中国的敏感目标进行攻击活动，是近几年来针对中国大陆进行攻击活动的最活跃的APT攻击组织之一。最近的分析中也有一些有趣的发现。

## 样本混淆特点分析

MD5：84B982D4B5A80792BC8BCB584E26208B

文件名字：wwwlib.dll

Wwwlib.dll这个白加黑dll利用也是很老的套路了，BTW据说在HVV行动中也有红方用到。

文件加了各种混淆，通过观察发现这一批的样本存在如下的混淆特点

1）.将简单功能的汇编指令通过寄存器做复杂处理，感觉就是反着编译器优化的方式来做：

![1602229378_5f8014829ffa13b109ed1.png!small](https://image.3001.net/images/20201009/1602229378_5f8014829ffa13b109ed1.png!small)

![1602229385_5f80148945650ffbc837d.png!small](https://image.3001.net/images/20201009/1602229385_5f80148945650ffbc837d.png!small)

![1602229391_5f80148fbf6a7de81a706.png!small](https://image.3001.net/images/20201009/1602229391_5f80148fbf6a7de81a706.png!small)

![1602229399_5f8014975f8063a46ff29.png!small](https://image.3001.net/images/20201009/1602229399_5f8014975f8063a46ff29.png!small)

2）.data节中存放加密字符串，并且仅在使用时进行解码，每次试用前将加密字符串做为call的参数传入

![1602229414_5f8014a6ea41c046f372a.png!small](https://image.3001.net/images/20201009/1602229414_5f8014a6ea41c046f372a.png!small)

可以看到解码函数被调用次数很多：

![1602229431_5f8014b77269cd9a12077.png!small](https://image.3001.net/images/20201009/1602229431_5f8014b77269cd9a12077.png!small)

3）.控制流混淆。在.data节中插入常量值，这些值用于条件跳转的比较中，data节中的常量与代码段中的常量进行比较，因此代码跳转始终会发生：

![1602229445_5f8014c5bc33fed1a7f06.png!small](https://image.3001.net/images/20201009/1602229445_5f8014c5bc33fed1a7f06.png!small)

![1602229451_5f8014cb86ebea9ffbf97.png!small](https://image.3001.net/images/20201009/1602229451_5f8014cb86ebea9ffbf97.png!small)

由于使用了上述的混淆干扰分析，因此代码打开后看起来很混乱。

3）样本分析：

样本结构接近2019年初曝光的样本基本结构:

![1602229467_5f8014db9749c78befe0e.png!small](https://image.3001.net/images/20201009/1602229467_5f8014db9749c78befe0e.png!small)

跳过之前的各种混淆代码，在virtualAlloc下断点，

![1602229482_5f8014eab617bdd251f41.png!small](https://image.3001.net/images/20201009/1602229482_5f8014eab617bdd251f41.png!small)

进入到一段shellcode：

![1602229497_5f8014f96c531818dc665.png!small](https://image.3001.net/images/20201009/1602229497_5f8014f96c531818dc665.png!small)

继续下断内存申请：

![1602229509_5f8015055239536e40dea.png!small](https://image.3001.net/images/20201009/1602229509_5f8015055239536e40dea.png!small)

进入第二段shellcode，可以看出第一第二段shellcode的起点是类似的，也是可以做为检测特征的，正常的代码里面不会用e8
接0x0000这样的地址。

![1602229520_5f801510ee7c8d74bacc8.png!small](https://image.3001.net/images/20201009/1602229520_5f801510ee7c8d74bacc8.png!small)

在shellcode的结尾可以看到username，computername字符串，以及第三段要解密的shellcode：

![1602229540_5f80152403882cad30e22.png!small](https://image.3001.net/images/20201009/1602229540_5f80152403882cad30e22.png!small)

同时通过读取PEB获取kerner 32.dll等dll的导出函数：

![1602229552_5f801530009ca1ab61dca.png!small](https://image.3001.net/images/20201009/1602229552_5f801530009ca1ab61dca.png!small)

再分配一段小的内存用于解密分段解密shellcode：

![1602229562_5f80153ac36af07a8f7d0.png!small](https://image.3001.net/images/20201009/1602229562_5f80153ac36af07a8f7d0.png!small)

![1602229570_5f8015427b2d6a3c45ace.png!small](https://image.3001.net/images/20201009/1602229570_5f8015427b2d6a3c45ace.png!small)

获取系统网卡的的信息：

![1602229589_5f801555461f31e09a38b.png!small](https://image.3001.net/images/20201009/1602229589_5f801555461f31e09a38b.png!small)

通过advapi32的cryptcreatehash等系列函数，最终解密shellcode：

![1602229613_5f80156d233666bf97c2f.png!small](https://image.3001.net/images/20201009/1602229613_5f80156d233666bf97c2f.png!small)

![1602229617_5f801571abd15ccefee77.png!small](https://image.3001.net/images/20201009/1602229617_5f801571abd15ccefee77.png!small)

![1602229621_5f8015759bdf4ba647ed0.png!small](https://image.3001.net/images/20201009/1602229621_5f8015759bdf4ba647ed0.png!small)

下图为第三段shellcode完成解密后，可以看到也是e8 0000000开头：

![1602229630_5f80157ec9b2d4f3b48bd.png!small](https://image.3001.net/images/20201009/1602229630_5f80157ec9b2d4f3b48bd.png!small)

进入第三段shellcode后可以看到最终payload的域名：

![1602229643_5f80158b357a49151cc49.png!small](https://image.3001.net/images/20201009/1602229643_5f80158b357a49151cc49.png!small)

读取文件后写入内存并跳入内存执行，但是目前该url已经无响应：

![1602229653_5f801595b77a8fdf3a911.png!small](https://image.3001.net/images/20201009/1602229653_5f801595b77a8fdf3a911.png!small)

<https://tothesky.merseine.com/hh2z>

通过查询该域名的威胁情报发现还有其他样本与其通信：

![1602229666_5f8015a21edea97826b96.png!small](https://image.3001.net/images/20201009/1602229666_5f8015a21edea97826b96.png!small)

对新样本进行调试发现shellcode入口点一致：

![1602229677_5f8015ad75fb59b3e38ba.png!small](https://image.3001.net/images/20201009/1602229677_5f8015ad75fb59b3e38ba.png!small)

将第三段shellcode dump，与第一个样本对比，发现仅连接的url的地址略有不同：

![1602229687_5f8015b7a6a073c679c6c.png!small](https://image.3001.net/images/20201009/1602229687_5f8015b7a6a073c679c6c.png!small)

![1602229692_5f8015bcda21c0aafb700.png!small](https://image.3001.net/images/20201009/1602229692_5f8015bcda21c0aafb700.png!small)

## 样本聚类尝试

此批次恶意样本的shellcode及第一个混淆特点都特征明显，选择第一个混淆特点转换为Yara规则：

    
    
    rule OceanLotus_aug
    
    {
    
    meta:
    
    description = “OceanLotus_aug”
    
    strings:
    
    $a = {50 8b c6 83 e8 01 58}
    
    $b={52 8b d1 23 d1 5a}
    
    $c={50 8b c1 23 c1 5“8}
    
    condition:
    
    ($a or $b or $c)
    
    }

测试后找到相似样本50+个,粗略验证后发现全是海莲花在8-9月份攻击中用的:

![1602229713_5f8015d1ce9a84c598ab3.png!small](https://image.3001.net/images/20201009/1602229713_5f8015d1ce9a84c598ab3.png!small)

![1602229719_5f8015d710d568e2326d4.png!small](https://image.3001.net/images/20201009/1602229719_5f8015d710d568e2326d4.png!small)


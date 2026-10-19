## 概述

近日，奇安信病毒响应中心在日常黑产挖掘过程中发现一个新型木马架构，该架构主要出现在全球华语地区，作者疑似具有中文背景。

该木马架构的免杀效果非常好，采用压缩文件中放置LNK文件的形式进行投递，样本执行过程中利用了Photodex ProShow
Producer软件的栈溢出漏洞来执行shellcode，经过几轮内存加载后最终运行大灰狼远控，远程控制受害者电脑。按照以往奇安信对于黑产的命名，我们将该木马架构命名为金指狗，英文名[Goldfinger](https://movie.douban.com/subject/1293828/)Dog

由于存在漏洞的软件的数字签名仍可用，奇安信病毒响应中心判断危害较大，为防止威胁进一步扩散，奇安信病毒响应中心负责任地对该木马架构进行披露和分析。

## 样本分析

执行流程如下：

![图片.png](https://image.3001.net/images/20200520/1589937888_5ec486e03eae0.png!small)

样本信息如下：

****文件名 **** |  ****MD5 **** |  ****Pack **er/compiler** |  ****类型 ****  
---|---|---|---  
**会员充值盈亏表格.xlsx.rar** **** |  4540572e6036c78b234651bb93a0942e |  None |
rar文件  
  
VT查杀效果如下：

![图片.png](https://image.3001.net/images/20200520/1589937980_5ec4873c127cd.png!small)  

诱饵文件如下：![图片.png](https://image.3001.net/images/20200520/1589937984_5ec48740ecbe7.png!small)  

压缩包内容如下：

![图片.png](https://image.3001.net/images/20200520/1589937993_5ec48749c8737.png!small)  

而解压后显示如下,其余文件被隐藏：

![图片.png](https://image.3001.net/images/20200520/1589938000_5ec4875098a8e.png!small)

月充值亏损计算表.lnk文件指向Rundll32，双击后执行如下命令：

rundll32.exe url.dll, FileProtocolHandler m.com

从lnk文件中可以看到[win-mfq3ac4596g](https://www.virustotal.com/gui/search/metadata%253A%2522win-mfq3ac4596g%2522)可能为攻击者的机器ID。

![图片.png](https://image.3001.net/images/20200520/1589938008_5ec48758bc307.png!small)

m.com实际上为Photodex ProShow Producer软件的运行程序，签名截图如下：

![图片.png](https://image.3001.net/images/20200520/1589938016_5ec487604cadb.png!small)

漏洞出现在if.dnt模块的导出函数InitIF()中，调用链如下

![图片.png](https://image.3001.net/images/20200520/1589938022_5ec487668e3ab.png!small)

在初始化过程中，会读取同目录下的load文件，由于没有对文件内容进行严格的判断导致程序会调用memcpy将load文件中的数据拷贝到栈中，经典栈溢出漏洞。

![图片.png](https://image.3001.net/images/20200520/1589938029_5ec4876d4552c.png!small)

触发该漏洞逻辑的条件需要m.com读取以下文件，缺一不可。

If.dnt->defscr->proshow_e.bmp->proshow.phd->load，所以压缩包中才会有数量众多的非PE文件。

![图片.png](https://image.3001.net/images/20200520/1589938038_5ec4877620269.png!small)

利用漏洞的方式也很古老，通过覆盖SEH的回调函数，并触发异常来执行shellcode：

![图片.png](https://image.3001.net/images/20200520/1589938045_5ec4877d55c33.png!small)

Shellcode内容如下：

![图片.png](https://image.3001.net/images/20200520/1589938051_5ec4878381b8b.png!small)

通过FS寄存器动态获取API，之后打开同目录下的X文件：

![图片.png](https://image.3001.net/images/20200520/1589938059_5ec4878b67589.png!small)

X文件的内容为第二阶段的Shellcode：

![图片.png](https://image.3001.net/images/20200520/1589938065_5ec48791736d3.png!small)

第二阶段shellcode，在执行过程中打开同目录下的A文件，A文件带有某互联网公司的签名：

![图片.png](https://image.3001.net/images/20200520/1589938070_5ec4879620a49.png!small)

但该签名文件内部可能被该团伙修改，A文件中附加了一段经过简单异或后的可执行文件：

![图片.png](https://image.3001.net/images/20200520/1589938075_5ec4879b5dacf.png!small)

Shellcode读取上述数据，解密后并内存加载：

![图片.png](https://image.3001.net/images/20200520/1589938081_5ec487a143936.png!small)

内存加载后的PE是经过魔改的大灰狼远控，弹出诱饵的逻辑如下，可以看到诱饵的种类支持jpg、txt、xls：

![图片.png](https://image.3001.net/images/20200520/1589938088_5ec487a84d050.png!small)

目前服务器已经无法访问。

## 关联分析

通过对shellcode进行关联，我们找到了该金指狗进行免杀测试的样本。

****文件名 **** |  ****MD5 **** |  ****Pack **er/compiler** |  ****类型 ****  
---|---|---|---  
**牛逼.exe** **** |  ce1fdb8e108229e2f7ed504c03c9296e |  VC |  PE文件  
  
PDB：C:\Users\Administrator\source\repos\shellcode编写\Debug\shellcode编写.pdb

Shellcode如下：

![图片.png](https://image.3001.net/images/20200520/1589938125_5ec487cd9ee0d.png!small)

从shellcode测试样本的免杀情况或许可以解释该木马框架为什么只有寥寥少数杀软报毒：

![图片.png](https://image.3001.net/images/20200520/1589938130_5ec487d2e9592.png!small)

值得注意的是shellcode测试样本的上传时间为2019-02-20
08:32:14，这意味着从2019年初至今这一年多的时间里该框架的木马一直处于免杀状态。

![图片.png](https://image.3001.net/images/20200520/1589938134_5ec487d6e076c.png!small)

接着我们对该木马框架滥用的某互联网产商签名的文件进行关联，发现了大量的被修改的白签名文件：

![图片.png](https://image.3001.net/images/20200520/1589938140_5ec487dc113a2.png!small)

通过这些文件我们找到了一些同源样本：

**文件名** |  **MD5** |  **Packer/compiler** |  **类型**  
---|---|---|---  
**支付凭证2019110154.exe** **** |  8fdadc6073e0f29aec48a76e71286053 |  SFX |
自解压文件  
**过内SM或未SM 62（A16）财务统计信息联络表.rar** |  42a8dc3a244eb0de36e35e1147533d95 |  None
|  Rar文件  
**2** **月份会员流水量.7z** **** |  79e9e10a3f305a461e954a08e7bfeb81 |  None |  7z文件  
**dsd111.zip** |  96c96ad15b301d3187bb86f2617d76c4 |  None |  7z文件  
**008.xml.zip** **** |  5604420ba9d55b4762712dc354ded12e |  None |  Zip文件  
**008 2.zip** |  1b66f6e3609dfd9be06d4eb2dc8d314b |  None |  Zip文件  
**006wutu.zip** **** |  de3e7086deb12770364bb8148f4ab1ab |  None |  Zip文件  
**001.xml.zip** |  9450b6019b051a16dbd1c299ba233e8e |  None |  Zip文件  
  
部分释放的诱饵整理如下：

![图片.png](https://image.3001.net/images/20200520/1589938150_5ec487e6315f7.png!small)

这些样本的执行链与上述流程相同，同属金指狗木马框架，但执行细节稍有不同，如“支付凭证2019110154.exe”是通过SFX自解压程序释放执行m.com的，样本挂在短链接上，而短链接指向国内的动态域名。

****ITW **** |  
|  ****DGA **** |  ****  
---|---|---|---  
**[c7.gg/fPHrA](http://c7.gg/fPHrA)** **** |  
|  1.220idc.com/%E6%94%AF%E4%BB%98%E5%87%AD%E8%AF%812019110154.exe |  
  
而在“008.xml.zip”中，则是通过F.exe进行调用的：

****文件名 **** |  ****MD5 **** |  ****Packer/compiler **** |  ****类型 ****  
---|---|---|---  
**f.exe** **** |  ee96cbc0294b6e931778f40d6b8f3c9f |  .net |  PE文件  
  
PDB：C:\Users\Administrator\Desktop\run\3.0\obj\Release\xxx.pdb

.net编写，调用powershell来启动m.com

![图片.png](https://image.3001.net/images/20200520/1589938279_5ec488672a69e.png!small)

有的样本还出现了LNK的拼写错误：

![图片.png](https://image.3001.net/images/20200520/1589938285_5ec4886d3f033.png!small)

在“0082.zip”样本中弹出的诱饵如下：

![图片.png](https://image.3001.net/images/20200520/1589938289_5ec4887193da2.png!small)

结合上述细节，我们推测金指狗木马架构可能已经被写马者定制化出售，由于存在多个组织购买该木马架构的可能性，所以上述关联的样本可能属于不同的黑产组织。

## 总结

国内黑产发展至今，我们发现一部分高端黑产团伙正在摆脱以往人们对黑产只会抓鸡、挖矿的“刻板印象”，开始研究上层投放链，执行链等技术，而不是仅仅对单一样本进行免杀处理。对于这类的黑产我们之前也有过披露，如金眼狗、金钻狗等，从攻防角度来讲，我们认为，这种现象的出现与流行，就要求国内安全厂商必须不断提升自身产品水平。与此同时，奇安信病毒响应中心提醒用户，疫情在家远程办公，不要点击来源不明的邮件和可执行文件，同时提高个人的安全意识，从而可以防止用户隐私信息被盗取的风险，奇安信病毒响应中心会持续对国内黑产进行挖掘和跟踪。

同时基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对该家族的精确检测。

## IOC

文件Hash：

4540572e6036c78b234651bb93a0942e

ce1fdb8e108229e2f7ed504c03c9296e

8fdadc6073e0f29aec48a76e71286053

42a8dc3a244eb0de36e35e1147533d95

79e9e10a3f305a461e954a08e7bfeb81

96c96ad15b301d3187bb86f2617d76c4

5604420ba9d55b4762712dc354ded12e

1b66f6e3609dfd9be06d4eb2dc8d314b

de3e7086deb12770364bb8148f4ab1ab

9450b6019b051a16dbd1c299ba233e8e

ee96cbc0294b6e931778f40d6b8f3c9f


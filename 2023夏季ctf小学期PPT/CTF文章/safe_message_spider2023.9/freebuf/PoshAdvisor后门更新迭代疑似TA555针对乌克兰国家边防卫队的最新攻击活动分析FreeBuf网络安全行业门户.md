**概述**

近日，奇安信威胁情报中心红雨滴团队在日常的样本监测过程中，捕获一例针对乌克兰国家边防卫队伊斯梅尔支队的攻击样本，该样本伪装成乌克兰国家财政局进行鱼叉邮件投递，诱导受害者启用带有恶意宏代码的附件文档。一旦恶意宏代码得以执行，便会在受害者机器上运行PoshAdvisor恶意软件，从而控制受害者计算机。

经溯源关联，该攻击文档疑似来自TA555组织[1]，TA555是国外安全组织Proofpoint追踪命名的黑客组织，在以往的攻击活动中，该组织的目标通常为酒店，餐厅，电信行业，本次攻击活动是该组织第一次针对政府机构的活动。

##  **样本** **分析** ****

###  **诱饵** **文档** ****

文件名|  Звернення керівнику підприємства.eml  
---|---  
MD5| 4423c37da26868ec578baa5514b8308a  
  
攻击者伪装为乌克兰财政部门以致领导人为主题进行鱼叉邮件投递

![图片.png](https://image.3001.net/images/20190731/1564564965_5d415de5cd484.png!small)

诱导受害者打开带有恶意宏代码的附件постанова_29_07_2019(2).doc（2019/7/29 决议）

![图片.png](https://image.3001.net/images/20190731/1564564979_5d415df3df7ba.png!small)

### **恶意代码** ****

一旦受害者启用宏，恶意宏代码便会执行powershell从远程[ _https://23.227.194.58/_
_（7_](https://23.227.194.58/%EF%BC%887)位随机字符）.png获取恶意代码执行。

![图片.png](https://image.3001.net/images/20190731/1564564994_5d415e029464a.png!small)  

在分析该样本时，服务器已失效，无法获取后续，但奇安信威胁情报中心高对抗沙箱在捕获该样本时，已成功获取后续。

![图片.png](https://image.3001.net/images/20190731/1564565018_5d415e1a68f6f.png!small)  

从远程服务器下载powershell执行，该段powershell继续从远程服务器<https://23.227.194.58/>（9位随机字符）.png获取后续执行

![图片.png](https://image.3001.net/images/20190731/1564565031_5d415e2732ee3.png!small)

红雨滴团队高对抗沙箱获取后续如下：

![图片.png](https://image.3001.net/images/20190731/1564565050_5d415e3a20f53.png!small)  

###  **PoshAdvisor** ****

该段powershell首先加载c#dll到内存中，并调用其B6ILdR()函数

![图片.png](https://image.3001.net/images/20190731/1564565066_5d415e4a07ed6.png!small)

B6ILdR()获取系统版本号等信息

![图片.png](https://image.3001.net/images/20190731/1564565105_5d415e7155c19.png!small)

  

之后执行一段base64解码的powershell

![图片.png](https://image.3001.net/images/20190731/1564565116_5d415e7c54385.png!small)

此段powershell主要功能为获取系统信息上传，通过cmd命令获取系统信息

![图片.png](https://image.3001.net/images/20190731/1564565129_5d415e8976ae0.png!small)

之后调用c#中的fqlw函数生成URL路径，该函数主要将B6ILdR()函数获取系统信新格式化后的字符经异或等处理后组成url路径，并在post方法后加上.asp后缀，其他方法加上.jpg后缀。

![图片.png](https://image.3001.net/images/20190731/1564565136_5d415e902a844.png!small)  

将通过cmd命令获取的系统信息上传到23.227.194.58/（urlpath）.asp

![图片.png](https://image.3001.net/images/20190731/1564565224_5d415ee8b2c64.png!small)

接着从注册表中获取outlook邮箱配置信息上传

![图片.png](https://image.3001.net/images/20190731/1564565230_5d415eeec8dca.png!small)

截取当前屏幕上传

![图片.png](https://image.3001.net/images/20190731/1564565237_5d415ef581662.png!small)  

当此段powershell执行结束后，进入接受指令流程，从23.227.194.58/（urlpath）.jpg获取指令执行，当获取的数据长度大于等于48时，进入远控功能流程

![图片.png](https://image.3001.net/images/20190731/1564565249_5d415f0169b16.png!small)  

获取数据的第一位为指令位，通过判断第一位的数据从而执行不同功能

![图片.png](https://image.3001.net/images/20190731/1564565270_5d415f161195c.png!small)  

远控指令功能如下表

指令| 功能  
---|---  
0| 调用Ka2l7Xn3O函数执行shellcode  
1| 通过iex执行powershell指令并将执行结果上传  
2| 下载dll保存到%temp%目录下并通过ChlVniP4q6函数调用执行  
3| 下载exe报道%temp%目录下并执行  
99| 退出  
其他| 根据偏移4的id下载执行shellcode  
  
## **溯源** **关联** ****

经关联分析，红雨滴团队安全研究员发现本次攻击活动实现的后门与2018年proofpoint披露的TA555组织的PoshAdvisor后门基本一致，只是在功能上更加完善丰富，因此我们认定本次攻击活动幕后团伙是TA555的可能性极大。

###  **诱饵** **文档对比** ****

本次攻击活动的诱饵文档与之前TA505的文档基本一致，如下图

![图片.png](https://image.3001.net/images/20190731/1564565287_5d415f271e228.png!small)  

###  **后门** **对比** ****

本次攻击活动获取系统信息powershell代码与TA555基本一致![图片.png](https://image.3001.net/images/20190731/1564565297_5d415f3136c99.png!small)

在功能代码上，本次攻击活动的后门功能较之TA555更加完善丰富

![图片.png](https://image.3001.net/images/20190731/1564565333_5d415f554729a.png!small)

## **总结** ****

从本次捕获TA555新样本来看，该团伙已开始转变攻击目标，从酒店餐厅等行业转变到政府机构，政治目的开始越发浓厚，其攻击武器功能也越发完善。奇安信威胁情报中心红雨滴团队将持续追踪该团伙的最新动态。

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对此类攻击的精确检测。

## **IOC** ****

 **样本MD5** ****

4423c37da26868ec578baa5514b8308a

c5661d589ee98e8b370acaceb7f5445e

1d045444d74bc63c8b30d9089c8da24f

03580beba48ab744b1468459603e715d

87c6e0daabe6f71a86f3a9c24a090944

30bbf8a8d2c0ad4e2ffbfdc6c5ed476b

37457ea1d0f093145f8d645779c363ac

1e2b0f55562277fc4f3cfec340397f10

**C &C地址** ****

23.227.194.58

## **参考** ****

[1][ _https://www.proofpoint.com/us/threat-insight/post/new-modular-downloaders-fingerprint-systems-part-2-advisorsbot_](https://www.proofpoint.com/us/threat-insight/post/new-modular-downloaders-fingerprint-systems-part-2-advisorsbot)


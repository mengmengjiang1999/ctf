**TransparentTribe
APT组织，又称ProjectM、C-Major，是一个来自巴基斯坦的APT攻击组织，主要通过鱼叉式钓鱼邮件对特定国家政府、军事目标发起攻击，该组织活动最早可以追溯到2012年，并于2016年被proofpoint首次披露，此前深信服安全团队首发布过一篇《来自TransparentTribe
APT组织的窃密》的报告，近期又获取到一例TransparentTribe
APT组织的最新变种样本，此样本的诱饵文档为日历型电子表格，通过执行表格中宏代码释放恶意程序，窃取受害者主机的敏感信息。样本执行整体流程图：**

![](https://image.3001.net/images/20191029/1572314243_5db79c83c091e.png!small)

## 分析诱饵文档文件

1.打开诱饵表格文档。

![](https://image.3001.net/images/20191029/1572314282_5db79caa510cf.png!small)

2.文档里面包含恶意的宏代码，执行宏代码，表格文档如下：

![](https://image.3001.net/images/20191029/1572314297_5db79cb9e89f3.png!small)

恶意宏代码会释放恶意程序到相应的目录并执行,进程信息如下所示：

![](https://image.3001.net/images/20191029/1572314318_5db79cce8986c.png!small)

释放的恶意程序目录，如下所示：

![](https://image.3001.net/images/20191029/1572314339_5db79ce3a05c1.png!small)

3.表格中包含的恶意宏代码，如下所示：

![](https://image.3001.net/images/20191029/1572314362_5db79cfa61129.png!small)

动态调试宏代码，首先会解密出相应的恶意文件路径目录字符串，然后读取窗口中的数据写入生成的恶意文件中，如下所示：

![](https://image.3001.net/images/20191029/1572314381_5db79d0d6b0db.png!small)

窗体的数据如下所示：

![](https://image.3001.net/images/20191029/1572314394_5db79d1a66381.png!small)

解压相应的数据压缩包文件，并调用生成的恶意文件。

![](https://image.3001.net/images/20191029/1572314407_5db79d275c481.png!small)

解压drivertoolkit.zip文件。

![](https://image.3001.net/images/20191029/1572314421_5db79d357597c.png!small)

## 分析drivertoolkit.tmp文件

1.判断系统是否存在如下进程，如果存在则退出，如下所示：

![](https://image.3001.net/images/20191029/1572314461_5db79d5d07b7e.png!small)

检测的进程列表：

python.exe、fiddler.exe、virtualBox.exe、VBoxService.exe、bitcoin-qt.exe、dotPeek.exe、dotPeek64.exe、jetbrains.exe、vmware.exe

2.设置系统自启动项快捷方式，如下所示：

![](https://image.3001.net/images/20191029/1572314530_5db79da23a541.png!small)

快捷方式用于启动C:\ProgramData\twainResolver\twainResolver.scr程序，如下所示：

![](https://image.3001.net/images/20191029/1572314546_5db79db2da2ba.png!small)

3.读取文件中的数据，生成恶意文件C:\ProgramData\twainResolver\twainResolver.scr，如下所示：

![](https://image.3001.net/images/20191029/1572314563_5db79dc34344b.png!small)

4.最后启动恶意程序C:\ProgramData\twainResolver\twainResolver.scr。

![](https://image.3001.net/images/20191029/1572314592_5db79de0d13b6.png!small)

## 分析twainResolver.scr文件

1.收集主机上的进程信息，上传到远程服务器，如下所示：

![](https://image.3001.net/images/20191029/1572314631_5db79e0749b0b.png!small)

捕获到如下的流量数据包：

![](https://image.3001.net/images/20191029/1572314660_5db79e241b48e.png!small)

传输的数据如下：

![](https://image.3001.net/images/20191029/1572314674_5db79e32a9bd9.png!small)

2.由于远程服务器失效了，上传数据失败，无法返回相应的数据。

![](https://image.3001.net/images/20191029/1572314703_5db79e4f7830c.png!small)

3.由于返回的数据为空，所以无法从远程服器下载相应的恶意程序，程序直接退出，如下所示：

![](https://image.3001.net/images/20191029/1572314719_5db79e5f60b5d.png!small)

猜测会下载一个RAT远控类程序，但已失效，无法获取到该RAT程序，进行下一步的分析，大多数的APT攻击组织主要目标是为了窃密，在执行的最后一般会释放一个RAT类的恶意程序控制受害者机器，并从受害者机器上获取有价值的信息。

## IOC

### MD5：

39AE6F1FD36C08E8199A9725906A9F0A |  Social_Calendar.xls  
---|---  
A579D7CF970B388558AA257CD84DCF52 | drivertoolkit.tmp  
BE399F59585A6167D0404CC76DF2FAF8 | drivertoolkit.zip  
D7FFFB36D22A36D9757CCC8FFA032D31 |  twainResolver.scr  
  
### C&C:

> 198.54.119.174

### URL:

> hxxp://isroddp.com/rEmt1t_pE7o_pe0Ry/hipto.php

### PDB:

> C:\Users\Carlos\source\repos\drivertoolkit\Release\drivertoolkit.pdb

***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**


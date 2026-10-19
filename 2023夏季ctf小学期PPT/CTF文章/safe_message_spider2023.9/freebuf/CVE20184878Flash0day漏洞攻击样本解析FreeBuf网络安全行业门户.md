***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 背景

 **2018年1月31日，韩国CERT发布公告称发现Flash
0day漏洞的野外利用，攻击者执行针对性的攻击；2月1日Adobe发布安全公告，确认Adobe Flash Player 28.0.0.137
及早期版本存在远程代码执行漏洞（CVE-2018-4878）；2月2日，Cisco
Talos团队发布了事件涉及攻击样本的简要分析；2月7日，Adobe发布了CVE-2018-4878漏洞的安全补丁。本文基于Talos文章中给出的样本及360安全卫士团队输出的报告，对相关样本做进一步的解析以丰富相应的技术细节，但是不涉及CVE-2018-4878漏洞的分析。**

## Flash 0day漏洞的载体

Flash 0day
CVE-2018-487漏洞利用代码被嵌入到Office文档中，样本使用Excel文档为载体，内嵌了一个动画用于加载其中恶意的Flash组件：

![0.png](https://image.3001.net/images/20180208/15180568705680.png!small)

该诱饵文件中包含一个ActiveX对象，打开文件后会加载其中的Flash内容：

![image.png](https://image.3001.net/images/20180208/15180580056944.png!small)

此activeX1.bin不能直接通过AS3打开：

![1.png](https://image.3001.net/images/20180208/15180568445518.png!small)

将FWS前面的数据删除，AS3即可正常反编译：

![2.png](https://image.3001.net/images/20180208/15180569005530.png!small)

此SWF本身是一个loader，运行前初始化了一个URLrequest实例，实例设置了对应的完成事件，通过该实例和远端服务器通信获取Exploit的解密秘钥后，调用Decrypt解密对应的Exploit代码：

![3.png](https://image.3001.net/images/20180208/15180569204620.png!small)

构造的发送初始数据的URL请求如下所示，具体包含：

> 1\. 唯一标示id
>
> 2\. Flash版本
>
> 3\. 系统版本

攻击者通过这些基础信息确定目标系统是否在漏洞的影响范围内，这也是Flash漏洞利用中的常规操作，即Exploit本身不轻易落地，只有当本地环境确认后，再从C&C服务器返回对应的Exploit及对应的解密密钥。

![4.png](https://image.3001.net/images/20180208/15180569573767.png!small)

提交的数据包样例如下所示：

![5.png](https://image.3001.net/images/20180208/15180571876178.png!small)

在此之后，通过该请求返回的密钥解密得到Exploit执行：

![6.png](https://image.3001.net/images/20180208/15180572154148.png!small)

## Payload分析

因为提供解密Exploit密钥的网站连接已经被移除，所以目前无法得到Exploit代码本身，因此本文是对Cisco
Talos团队所提供的CVE-2018-4878漏洞利用完成以后的落地Payload进行分析，相应的文件Hash为：d2881e56e66aeaebef7efaa60a58ef9b

该样本从资源JOK获取数据并注入到一个自启的wscript进程中执行：

![7.png](https://image.3001.net/images/20180208/1518057252380.png!small)

资源JOK中的数据：

![8.png](https://image.3001.net/images/20180208/15180572744138.png!small)

注入的数据开头是一段加载代码，主要功能是重定位以及通过XOR解密之后的第二段Shellcode，解密密钥通过加密Shellcode第一个字节与0x90
XOR操作获得：

![9.png](https://image.3001.net/images/20180208/15180573118709.png!small)

Shellcode2首先获取Kernel32基址，之后通过90909090标记找到后续需要解密的PE文件地址：

![10.png](https://image.3001.net/images/20180208/15180574323838.png!small)

通过加密PE第一个字节与0x4D做XOR操作获取PE的解密Key，并解密出最后的PE文件：

![11.png](https://image.3001.net/images/20180208/15180574549046.png!small)

如下代码所示开始对应PE文件的解密：

![12.png](https://image.3001.net/images/20180208/15180574749660.png!small)

之后该恶意PE文件被重新拷贝到一段申请的内存中修复导入表并执行：

![13.png](https://image.3001.net/images/20180208/1518057504108.png!small)

## ROKRAT后门

被Shellcode加载到内存中执行的恶意代码是一个EXE程序，为ROKRAT家族后门远控。该样本会通过网盘上传数据，网盘的API
Key会内置在样本数据里，下图为提取到的字符串的信息，样本会通过API调用4个国外主流的网盘包括：pcloud、box、dropbox、yandex

![14.png](https://image.3001.net/images/20180208/1518057549193.png!small)

从文件中获取到Key的代码如下：

![15.png](https://image.3001.net/images/20180208/15180575705851.png!small)

上传到网盘的文件名格式为pho_[随机生成的8字节hex值(机器标识)]_[上传次数递加]，构造文件名的代码如下：

![16.png](https://image.3001.net/images/20180208/1518057591407.png!small)

![17.png](https://image.3001.net/images/20180208/15180576144523.png!small)

## 网盘数据

使用得到的Key请求pcloud可以获取网盘的注册人信息，注册邮箱为cheseolum@naver.com，注册时间为2017年12月11日：

![18.png](https://image.3001.net/images/20180208/15180576386083.png!small)

使用listfolder API获取根目录的文件列表如下：

![19.png](https://image.3001.net/images/20180208/15180576649053.png!small)

然后通过API获取指定文件的下载链接：

[https://api.pcloud.com/getfilelink?path=%s&forcedownload=1&skipfilename=1](https://api.pcloud.com/getfilelink?path=%s&forcedownload=1&skipfilename=1)

![20.png](https://image.3001.net/images/20180208/15180576866975.png!small)

通过把上述返回结果中的hosts和path字段拼接起来得到路径下载文件，中间的16进制数据是随机生成的8字节Hex值，下载得到的部分文件列表如下：

![21.png](https://image.3001.net/images/20180208/15180576948766.png!small)  

分析这些文件得到的数据格式如下：

文件前部的数据为机器的型号和机器名信息以及执行起恶意代码的宿主路径：

![22.png](https://image.3001.net/images/20180208/15180581938390.png!small)  

从文件的偏移0x45F开始的为图片的数据结构信息，后面包括4个字节的图片长度及后续的图片内容数据：  

![23.png](https://image.3001.net/images/20180208/15180577041914.png!small)

图片为电脑的截屏，如下是其中的一个例子：  

![24.png](https://image.3001.net/images/20180208/15180582624254.png!small)  

我们见到的数据最早上传时间为2月2日，这个时间点晚于攻击被揭露之后，所以几乎所有电脑桌面截图都是安全分析人员或沙箱的：  

![25.png](https://image.3001.net/images/20180208/15180577187090.png!small)  

## 参考链接

Flash 0-Day In The Wild: Group 123 At TheControls:

<http://blog.talosintelligence.com/2018/02/group-123-goes-wild.html>

Security Advisory for Flash Player | APSA18-01

<https://helpx.adobe.com/security/products/flash-player/apsa18-01.html>

## IOC

**pcloud** **网盘访问** **Token**  
---  
FvpEZb8OdiCFSNHJZQMKbO7ZjkYXAL509nzzFNnu2Tosb53KxcKy  
**文件** **HASH**  
5f97c5ea28c0401abc093069a50aa1f8  
d2881e56e66aeaebef7efaa60a58ef9b  
  
***本文作者：360天眼实验室，转载请注明来自FreeBuf.COM**


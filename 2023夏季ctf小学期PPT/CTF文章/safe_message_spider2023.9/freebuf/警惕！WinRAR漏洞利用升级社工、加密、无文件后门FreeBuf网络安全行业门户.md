## 背景  

**2019年2月22日，360威胁情报中心截获了首个利用WinRAR漏洞（CVE-2018-20250）传播木马程序的恶意ACE文件。并提醒用户务必对此高危漏洞做好十足的防护措施。**

**正如我们的预测，在接下来的几天内，360威胁情报中心截获了多个使用WinRAR漏洞传播恶意程序的样本，并且我们还观察到了多个利用此漏洞进行的APT攻击活动。可以明显的看到，攻击者针对该漏洞利用做了更精心的准备，比如利用WinRAR压缩包内图片列表不可预览来诱导目标极大概率解压恶意文件、将恶意ACE文件加密后投递、释放“无文件”后门等。**

**事实证明，利用该漏洞传播恶意程序的攻击行为正处在爆发的初期阶段，并且不排除在将来被攻击者用于制作蠕虫类的病毒造成更广泛的威胁。360威胁情报中心再次提醒各用户及时做好漏洞防护措施。（见“缓解措施”一节）**

## 样本分析

360威胁情报中心针对最具代表性的几类样本进行了分析，相关分析如下。

利用图片列表诱导解压：

**MD5** |  d7d30c2f26084c6cfe06bc21d7e813b1  
---|---  
**文件名** |  10802201010葉舒華.rar  
  
该恶意压缩文件利用了WinRAR压缩包内图片列表不可预览的特性，诱导目标大概率解压文件从而触发漏洞。当受害者打开RAR压缩包后可以看到很多图片文件：

![image.png](https://image.3001.net/images/20190227/1551261094_5c765da68e465.png!small)

出于好奇，用户一般会点击打开其中的一张图片查看：

![image.png](https://image.3001.net/images/20190227/1551261101_5c765dad5c165.png!small)

如果受害者对图片内容很感兴趣，但WinRAR又无法预览所有图片的情况下，则只好解压该压缩包，这样漏洞则会被触发，极大的提高了攻击成功率，解压后的诱饵图片列表：

![image.png](https://image.3001.net/images/20190227/1551261109_5c765db5057ca.png!small)

漏洞触发后，会在%AppData%\Microsoft\Windows\StartMenu\Programs\Startup目录释放OfficeUpdateService.exe，当用户重启计算机或者注销登录后将执行恶意代码：

![image.png](https://image.3001.net/images/20190227/1551261114_5c765dbaa897e.png!small)

### Backdoor（OfficeUpdateService.exe）

OfficeUpdateService.exe是使用C#编写的远控程序，其通信地址为conloap.linkin.tw:8080。其提供的功能大致有计算机管理（重启/关闭）、文件管理（上传/下载/遍历）、远程SHELL、木马管理（安装/卸载）、屏幕抓取、录音等功能。

![image.png](https://image.3001.net/images/20190227/1551261121_5c765dc1ec46c.png!small)

![image.png](https://image.3001.net/images/20190227/1551261162_5c765dea88b9a.png!small)

C&C地址为：conloap.linkin.tw:8080

![image.png](https://image.3001.net/images/20190227/1551261134_5c765dce15d6e.png!small)

## 多个类似样本

此外，我们还捕获到数个国外类似利用社会工程学和该漏洞结合的攻击样本。

**MD5** |  f8c9c16e0a639ce3b548d9a44a67c8c1  
---|---  
**文件名** |  111.rar  
  
解压后的诱饵图片列表：

![image.png](https://image.3001.net/images/20190227/1551261144_5c765dd8130bf.png!small)

**MD5** |  f9564c181505e3031655d21c77c924d7  
---|---  
**文件名** |  test.rar  
  
解压后的诱饵图片列表：

![image.png](https://image.3001.net/images/20190227/1551261185_5c765e013bca1.png!small)

## 目标阿拉伯地区：释放“无文件”后门

**MD5** |  e26ae92a36e08cbaf1ce7d7e1f3d973e  
---|---  
**文件名** |  JobDetail.rar  
  
该样本包含了一份工作地点位于沙特阿拉伯的招聘广告PDF文档（诱饵），如果用户使用WinRAR解压该文件并触发漏洞后，WinRAR会释放恶意脚本Wipolicy.vbe到用户开机启动目录，最终的恶意代码为PowerShell编写的远程控制程序，整个执行过程全部在内存中实现，其通信地址为：hxxps://manage-shope.com:443。

该样本包含一份工作招聘广告，如下图所示：

![image.png](https://image.3001.net/images/20190227/1551261195_5c765e0b2df52.png!small)

招聘广告中工作地点位于沙特阿拉伯：

![image.png](https://image.3001.net/images/20190227/1551261201_5c765e11d80f1.png!small)

漏洞触发后会在%AppData%\Microsoft\Windows\StartMenu\Programs\Startup目录释放Wipolicy.vbe：

![image.png](https://image.3001.net/images/20190227/1551261208_5c765e18e428d.png!small)

### Wipolicy.vbe分析

该样本为加密的VBS脚本，解密后的部分脚本如下图所示：

![image.png](https://image.3001.net/images/20190227/1551261215_5c765e1f4f2ec.png!small)

该VBS脚本将执行一段PowerShell脚本，PowerShell脚本解密后如下图：

![image.png](https://image.3001.net/images/20190227/1551261222_5c765e26c2a09.png!small)

该段PowerShell会下载hxxp://local-update.com/banana.png并利用图片隐写术解密出第二段PowerShell脚本，脚本部分内容如下图：

![image.png](https://image.3001.net/images/20190227/1551261238_5c765e3671197.png!small)

第二段PowerShell脚本将从hxxps://manage-shope.com:443下载第三段数据并利用AES解密为第三段PowerShell脚本，以下是第三段PowerShell部分脚本：

![image.png](https://image.3001.net/images/20190227/1551261244_5c765e3c59a49.png!small)

该PowerShell脚本包含了完整的远程控制代码，提供的功能有启动多个CMD、上传文件、下载文件、加载执行模块、执行其他PowerShell脚本等功能，其通信地址为：hxxps://manage-shope.com:443

## 加密的ACE文件

**MD5** |  65e6831bf0f3af34e19f25dfaef49823  
---|---  
**文件名** |  Сбор информации для переезда в IQ-квартал.rar  
  
另外，我们还捕获到了一个加密的恶意ACE文件，由于恶意文件使用密码加密，故我们暂时无法得知最终释放的恶意代码内容。不过可以发现，攻击者也在尝试将恶意ACE文件进行加密来防止受害者以外的人员获取其中的恶意代码，具有较高的针对性和自我保护意识。

360威胁情报中心针对ACE文件的加解密过程进行了分析，过程如下：

首先，该恶意ACE样本进行了加密，但是解压时输入错误密码，仍然可以看到会解压到对应的启动目录下：

![image.png](https://image.3001.net/images/20190227/1551261254_5c765e4659328.png!small)

但该样本实际上并没有解压成功：

![image.png](https://image.3001.net/images/20190227/1551261259_5c765e4be93a3.png!small)

于是我们分析了WinRAR在处理带密码的ACE数据的处理过程，WinRAR中UNACEV2.dll的加载入口如下：

![image.png](https://image.3001.net/images/20190227/1551261297_5c765e7196278.png!small)

对应的函数如下，专门用于处理ACE的压缩包文件：

![image.png](https://image.3001.net/images/20190227/1551261302_5c765e765a60f.png!small)

86行的函数对应解压到当前目录的操作：

![image.png](https://image.3001.net/images/20190227/1551261307_5c765e7be846d.png!small)

进入函数sub_1395F10，该函数第74行对应了漏洞的入口点，运行之后对应的目标的释放文件将被创建：

![image.png](https://image.3001.net/images/20190227/1551261355_5c765eab435a4.png!small)

之后进入解压逻辑，UNACEV2包含了自身的解压逻辑，因此和WinRAR无关，整个解压写入文件过程如下：

> 1.首先通过函数fun_Allocmemory分配一段用于存放解压数据的内存，其大小和解压数据一致；
>
> 2.再通过函数fun_GetEncryptkey获取用户输入的密钥；
>
> 3.然后通过函数fun_DecryptCompress解压对应的数据到第一步分配的内存中；
>
> 4.最后通过函数fun_EctraceoFile将内存中的数据写入到之前的文件中。

这样就导致即使输入了错误的密码依然会将第一份分配的初始化内存写入到启动目录下：

![image.png](https://image.3001.net/images/20190227/1551261361_5c765eb1be3c4.png!small)

我们创建了一个测试ACE文件，如下所示分配的内存地址为0x0b4a0024：

![image.png](https://image.3001.net/images/20190227/1551261367_5c765eb71772c.png!small)

获取压缩包的密钥A1B2C3D4E5：

![image.png](https://image.3001.net/images/20190227/1551261374_5c765ebeb5ace.png!small)

如下所示解压出的对应内容：

![image.png](https://image.3001.net/images/20190227/1551261380_5c765ec411d81.png!small)

当输入错误的密码时，依然会写入数据，写入的数据为乱码：

![image.png](https://image.3001.net/images/20190227/1551261386_5c765eca56e07.png!small)

## 总结

截止文章完成时，360威胁情报中心还陆续观察到了多个利用此漏洞进行的APT攻击活动。

事实证明，利用WinRAR漏洞（CVE-2018-20250）传播恶意程序的攻击行为正处在爆发的初期阶段，并且不排除在将来被攻击者用于制作蠕虫类的病毒造成更广泛的威胁。360威胁情报中心再次提醒各用户及时做好漏洞防护措施。

## 缓解措施

1.软件厂商已经发布了最新的WinRAR版本，360威胁情报中心建议用户及时更新升级WinRAR（5.70 beta 1）到最新版本，下载地址如下：

> 32位：<http://win-rar.com/fileadmin/winrar-versions/wrar57b1.exe>
>
> 64位：<http://win-rar.com/fileadmin/winrar-versions/winrar-x64-57b1.exe>

2.如暂时无法安装补丁，可以直接删除漏洞的DLL（UNACEV2.DLL），这样不影响一般的使用，但是遇到ACE的文件会报错。

目前，基于360威胁情报中心的威胁情报数据的全线产品，包括360威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、360
NGSOC等，都已经支持对此类攻击的精确检测。

## IOC

**恶意ACE** **文件MD5**  
---  
d7d30c2f26084c6cfe06bc21d7e813b1  
f9564c181505e3031655d21c77c924d7  
65e6831bf0f3af34e19f25dfaef49823  
9cfb87f063ab3ea5c4f3934a23e1d6f9  
f8c9c16e0a639ce3b548d9a44a67c8c1  
e26ae92a36e08cbaf1ce7d7e1f3d973e  
**木马MD5**  
782791b7ac3daf9ab9761402f16fd407  
**恶意脚本MD5**  
ad121c941fb3f4773701323a146fb2cd  
**C &C**  
manage-shope.com:443  
  
## 参考链接

[1].<https://mp.weixin.qq.com/s/Hz-uN9VEejYN6IHFBtUSRQ>（首个完整利用WinRAR漏洞传播的恶意样本分析）

[2].<https://research.checkpoint.com/extracting-code-execution-from-winrar/>

[3].<https://twitter.com/360TIC/status/1099987939818299392>

[4].<https://ti.360.net/advisory/articles/360ti-sv-2019-0009-winrar-rce/>

 ***本文作者：360天眼实验室，转载请注明来自FreeBuf.COM**


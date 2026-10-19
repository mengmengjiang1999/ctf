![](https://image.3001.net/images/20191011/1570801260_5da0866c0a52e.png!small)

##  写在前面的话

 **Sednit组织，也被称为APT28、Fancy
Bear、Sofacy或STRONTIUM，从2004年起该组织一直活跃至今，而且只要该组织参与的网络攻击活动一般都会上报纸头条。在2019年8月20日，该组织又发动了一波新的网络攻击活动，而这一波攻击活动针对的也是Sednit组织的老“对象”：东欧和中亚国家的大使馆和外交部。**

接下来，我们一起跟随ESET的研究人员看一看，Sednit的攻击者们又往Zebrocy恶意软件家族中增添了哪些新型的攻击组件。

##  分析概述

此次这一波新型的网络攻击由一封包含了恶意附件的网络钓鱼邮件作为攻击开始的起点，其中的恶意附件可以启动一系列恶意组件下载器，并最终作为后门执行。研究人员目前已经在2019年8月22日向VirusTotal上传过一份恶意邮件样本了，[Telsy
TRT](https://blog.telsy.com/zebrocy-dropbox-remote-injection)也对活动的攻击向量进行了分析，感兴趣同学可以点击【[这里](https://blog.telsy.com/zebrocy-dropbox-remote-injection)】了解更多。

正如其他[研究人员](https://securelist.com/zebrocys-multilanguage-malware-salad/90680/)预测的那样，Sednit组织在他们的恶意软件组件中新增了一种开发语言支持，更准确的来说，是他们针对恶意Payload下载器增加了Nim语言支持。不过，Sednit的攻击者仍在努力完善他们的Golang下载器，并且将之前采用Delphi开发的后门用Golang重构。

##  复杂的入侵活动

下图显示的攻击者一步一步实现成功入侵的过程，即从一开始目标用户在收件箱中收到恶意电子邮件，到最终在目标用户的设备上部署后门：

![](https://image.3001.net/images/20191011/1570801271_5da086777594d.png!small)

当目标用户受到Zebrocy感染之后，整个攻击链会比较复杂，因为攻击者会在最终的Payload被执行之前，在目标设备上安装至少六个恶意软件组件。因此，这种类型的攻击活动非常容易被安全产品标记。

研究人员发现，钓鱼邮件中携带的附件文档其实是一份空白文档，但这个恶意文档引用了一个托管在Dropbox上的远程模板：wordData.dotm。使用Word打开这个文档之后，它将会下载wordData.dotm，并将其合并到相关文档的工作环境中，其中还包括模板中隐藏的内容，具体情况如下图所示：

![](https://image.3001.net/images/20191011/1570801276_5da0867c123b9.png!small)

wordData.dotm文件中还包含恶意宏，文档被打开后恶意宏也将被执行，不过具体将取决于目标设备中Microsoft
Word的版本，有的版本默认会禁用VBA宏功能，如果被禁用的话，恶意软件还会提示用户启用宏功能。除此之外，恶意文档中还包含一个嵌入的ZIP压缩文件（恶意宏在执行之后会对其进行解压提取操作）。

如第一张截图所示，wordData.dotm中的宏会打开另一个文档：lmss.doc，而lmss.doc文件需要恶意宏从wordData.dotm中提取出来。lmss.doc中的恶意宏辉执行lmss.exe，也就是Zebrocy最新的Nim下载器，它同样是从wordData.dotm中提取出来的，而且wordData.dotm并不会直接执行下载器。

需要注意的是，lmss.doc中包含的VBA代码可以执行新型的Nim下载器，而且它还嵌入了一个Base64编码的可执行程序，根据其文档属性，lmss.doc创建于2019年1月份，并且在8月20日进行过修改，也就是此次攻击活动开始前的几个小时：

![](https://image.3001.net/images/20191011/1570801288_5da086883084c.png!small)

lmss.doc中嵌入的可执行程序是一个Autolt下载器（SHA-1:
6b300486d17d07a02365d32b673cd6638bd384f3），这个下载器在这里没啥作用，也就是让文档变得更大了些，很可能是因为攻击者忘记把它删掉了，反正Sednit的人也经常干这种事情。

##  下载器分析

Sednit的攻击者曾使用过多种采用不同语言开发的下载器，在此次活动中使用他们使用的是最新的一款，即采用Nim语言开发的下载器。他们在这个下载器中新增了两个特性，第一个就是反沙箱技术，并且检测可执行文件的第一个字母（十六进制0x6c）是否被篡改过。

![](https://image.3001.net/images/20191011/1570801293_5da0868dcc77f.png!small)另一个特性就是代码混淆，攻击者使用了代码混淆技术来重构恶意组件的URL地址字符串，以增加静态分析工具的分析难度：

![](https://image.3001.net/images/20191011/1570801298_5da0869203180.png!small)

随后，Nim下载器会从中获取动态链接库（DLL）
Payload：ospsvc.dll，然后拷贝到“C:\ProgramData\Java\Oracle\”，最后通过regsv***
/s将其以服务的形式执行。

ospsvc.dll是一个采用Golang编写的下载器，它跟此前Sednit使用过的下载器有很大不同。

Sednit之前使用的Golang下载器会收集大量目标设备的信息，并将其发送至C2服务器。但这一个下载器在数据收集方面轻量化了很多。它的main_init()函数包含的库会初始化下列函数，下列函数的功能和作用想必大家可以直接看得出来：

![](https://image.3001.net/images/20191011/1570801302_5da086964d3a6.png!small)

由于DLL Payload是以服务的形式运行的，所以我们需要仔细看看main_DllRegisterServer()函数：

![](https://image.3001.net/images/20191011/1570801318_5da086a65aece.png!small)

在攻击的下一个阶段，恶意软件会获取目标设备桌面的屏幕截图，并执行攻击者通过C2服务器发送过来的命令。截图操作自下载器执行之后开始，每35秒截图一次，然后以Base64编码形式发送至C2服务器。C2服务器的响应信息格式如下：

    
    
    <spaces>|<cmd to execute>|<name of the binary to drop>|<binary to drop>

##  新型后门分析

新型的Zebrocy后门采用的是Golang开发，不过这种后门的特性跟之前采用Delphi开发的后门基本一致。

通过分析main_init()函数的库初始化代码，我们可以看到新的入口点，即一个使用了十六进制编码的AES算法：

![](https://image.3001.net/images/20191011/1570801326_5da086aee978a.png!small)

其中，image_jpeg_init方法被替换成了image_png_init，可能是因为PNG格式的图片更合适吧。

下面的Python代码段介绍的是恶意软件所使用的解密算法：

    
    
    key = arg[-6:].decode('hex')
    
        enc = arg[:-6].decode('hex')
    
        ''.join(chr(ord(i) ^ ord(j)) for i, j in zip(itertools.cycle(key), enc))

**新增的后门功能：**

> 1、文件属性篡改，例如创建、修改和删除属性；
>
> 2、截图功能；
>
> 3、驱动器枚举；
>
> 4、命令执行（通过cmd.exe）实现；
>
> 5、计划任务；

##  网络数据

C2服务器的通信数据包样本请求如下：

    
    
    POST [REDACTED URI] HTTP/1.1
    
        Host: [REDACTED IP]
    
        User-Agent: Go-http-client/1.1
    
        Content-Length: 297
    
        Content‑Type: multipart/form‑data; boundary=b116f1e0a94eff1bb406531e74bb0feba65687cf90ec8a64fc409f230fbd
    
        Accept-Encoding: gzip
    
        –b116f1e0a94eff1bb406531e74bb0feba65687cf90ec8a64fc409f230fbd
    
        Content-Disposition: form-data; name=”filename”; filename=”[REDACTED]”
    
        Content-Type: application/octet-stream
    
        1
    
        –b116f1e0a94eff1bb406531e74bb0feba65687cf90ec8a64fc409f230fbd–

##  总结

新型的后门表明Sednit组织目前仍处于活跃状态，而且攻击者似乎正在使用其他语言来重构他们的恶意软件，这样可以尽可能地避免被安全产品检测到。

**入侵威胁标识符IoC**

 **网络地址**

>
> [https://www.dropbox](https://www.dropbox/)[.]com/s/foughx315flj51u/wordData.dotm?dl=1
>
> 185.221.202[.]35

##  参考资料

> 1、<https://unit42.paloaltonetworks.com/sofacy-creates-new-go-variant-of-> zebrocy-tool/>
>
> 2、<https://securelist.com/a-zebrocy-go-downloader/89419/>
>
> 3、<https://www.vkremez.com/2018/12/lets-learn-dissecting-apt28sofacy.html>
>
> 4、<https://www.vkremez.com/2018/12/lets-learn-dissecting-apt28sofacy.html>

***参考来源：[welivesecurity](https://www.welivesecurity.com/2019/09/24/no-summer-vacations-zebrocy/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


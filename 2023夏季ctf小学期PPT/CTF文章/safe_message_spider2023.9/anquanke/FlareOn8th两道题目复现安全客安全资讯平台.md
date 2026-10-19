# Flare-On 8th两道题目复现

阅读量 **205634**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-17 10:30:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t015d994deee747ec45.png)

Flare-On8由FireEye公司于今年9月份至10月份期间举办，共10道题目。笔者从中选取了自己感兴趣的三道题目进行复现，下文是前两道题目复现过程中所作笔记，第三道题目涉及到的技术点及分析过程笔者会单独写一篇文章。

  * 题目下载：[Flare-On8 Challenges](https://flare-on.com/files/Flare-On8_Challenges.zip)
  * WriteUp：[Flare-On 8 Challenge Solutions](https://www.mandiant.com/resources/flare-on-8-challenge-solutions)

## 0x01 Challenge 5:Flare Linux VM

题目描述如下：

![](https://p1.ssl.qhimg.com/t0125272000f1f41a8f.png)

压缩包中文件：

![](https://p2.ssl.qhimg.com/t019425c14063d8949e.png)

使用VMWare导入`FLARE Linux VM.ovf`文件，在打开虚拟机之前将网络连接修改为”桥接模式”，方便后续通过`scp`复制文件：

![](https://p5.ssl.qhimg.com/t012ef2bd90abe48f0b.png)

以`root`身份登录，密码为 **flare** 。进入到`Documents`目录下查看：

![](https://p4.ssl.qhimg.com/t017fd422c0d4247e86.png)

新建一TXT文件，过一段时间查看发现其扩展名由`.txt`变为`.txt.broken`。使用`crontab
-l`命令列出计划任务(若读者之前未接触过，可翻阅《鸟哥的Linux私房菜》第15章或是[crontab(5) — Linux manual
page](https://man7.org/linux/man-pages/man5/crontab.5.html))：

![](https://p0.ssl.qhimg.com/t0140cd7cd2ecebd613.png)

在另一Linux虚拟机中使用`scp`命令将该文件复制出来，查看其详细信息：

![](https://p4.ssl.qhimg.com/t01e8a3c90fafabe0c7.png)

将`getenv`函数返回值与”/Documents”字符串拼接成绝对路径传递给`opendir`函数，调用`readdir`函数遍历该目录下文件。
将`d_name`字段值与`.`及`..`进行比较，之后判断后缀是否为`.broken`：

![](https://p0.ssl.qhimg.com/t01c1e1720a78102730.png)

如果上述条件均不满足，则进行加密：

![](https://p0.ssl.qhimg.com/t011c48e022d669a587.png)

加密函数只对原文件前0x400字节进行加密并写入`.broken`文件(若不足0x400字节，最后`.broken`文件亦是0x400字节大小，具体见下面对`encrypt`函数的分析)，之后调用`remove`函数来删除原文件。

![](https://p1.ssl.qhimg.com/t01d0627e4c1aca20d8.png)

![](https://p0.ssl.qhimg.com/t01a44650435a50ca28.png)

可以看到其加密函数采用变形RC4算法，区别在于最后的异或运算。使用`crontab
-r`命令删除计划任务，将`Documents`目录下所有文件的`.broken`扩展名去掉：

    
    
    #!/bin/bash
    
    for name in `ls *.broken`
    do
        mv $name ${name%.broken}
    done
    

再执行一次`/usr/lib/zyppe`即可完成解密。逐一查看解密后文件，发现下面四个文件内容是未加密的：

![](https://p3.ssl.qhimg.com/t012a23c7767d4b0457.png)

按照`ugali.txt`文件给出提示，将`Sausages.txt`
和`Spaghetti.txt`拖入CyberChef，执行Arithmetic/Logic中的Rotate Left运算：

![](https://p0.ssl.qhimg.com/t014f5876a9bc77137f.png)

![](https://p3.ssl.qhimg.com/t01b89fcc1b09c0c236.png)

“c3BhZ2hldHRp”是”spaghetti”的Base64编码：

![](https://p5.ssl.qhimg.com/t013f59990391ab96fa.png)

按照`shopping_list.txt`文件给出提示，进入`/usr/bin`目录，发现存在`dot`文件：

![](https://p1.ssl.qhimg.com/t01cc6a65fadd4147c4.png)

使用IDA打开：

![](https://p0.ssl.qhimg.com/t01d86ecb4c90bce6a8.png)

计算输入的SHA256值，与`b3c20caa9a1a82add9503e0eac43f741793d2031eb1c6e830274ed5ea36238bf`进行比较，相等才会中止循环。按照`shopping_list.txt`文件给出顺序，查看`reeses.txt`：

![](https://p1.ssl.qhimg.com/t01c523d43685d5e34a.png)

笔者一开始按照提示使用`Reese's`作为Key去解密`ice_cream.txt`，尝试数次结果均为乱码。按`shopping_list.txt`文件给出顺序，下一文件应为`banana_chips.txt`，结果如下：

![](https://p5.ssl.qhimg.com/t016c30cf20b7735ce6.png)

其他以B开头文件通过异或运算解码出内容如下：

![](https://p5.ssl.qhimg.com/t01cd7dec4cdd72dbb6.png)

其他以R开头文件亦可使用Base64解码出内容：

![](https://p1.ssl.qhimg.com/t01325e6c6b73f98faf.png)

笔者起初以为`ENCODED_BYTE + 27 + NUMBER1 * NUMBER2 -NUMBER3`公式中3个`NUMBER`是前边解码出的三个字节，但尝试后发现并不是，而是环境变量：

![](https://p1.ssl.qhimg.com/t01fe31b02622e716db.png)

代入三个环境变量，公式化简为`ENCODED_BYTE-4`。笔者同时查看了`.bashrc`文件：

![](https://p3.ssl.qhimg.com/t018be6a9bfed8246ef.png)

使用公式解密`ice_cream.txt`，`iced_coffee.txt`及`instant_noodles.txt`：

![](https://p0.ssl.qhimg.com/t0111bdcef79f7d08da.png)

![](https://p4.ssl.qhimg.com/t01d9703de883f801bf.png)

![](https://p0.ssl.qhimg.com/t01d2501632d5f7595d.png)

笔者在解码出`ice_cream.txt`结果时，不知道其内容有何作用，等解码出`instant_noodles.txt`结果时回看，发现每个数字对应字母各不相同，那么0xMS——0x64，`iced_coffee.txt`结果中给出的`SREFBE`——493513。以493513作为RC4算法的Key去解密`nachos.txt`，`natillas.txt`及`nutella.txt`：

![](https://p1.ssl.qhimg.com/t01e01ba0392d016588.png)

![](https://p5.ssl.qhimg.com/t01bb3dc7ac12577285.png)

![](https://p2.ssl.qhimg.com/t01e520d0e76d0a9e70.png)

根据提示进行搜索，算法应使用Bifid Cipher：

![](https://p4.ssl.qhimg.com/t013dbd47542ff1f952.png)

Key应使用`eggs`：

![](https://p5.ssl.qhimg.com/t01a907c8adbd189369.png)

解密以D开头文件：

![](https://p0.ssl.qhimg.com/t0111617d920a2ed776.png)

![](https://p2.ssl.qhimg.com/t01e041a56ea71b9794.png)

根据提示，于Documents目录下看到隐藏文件`.daiquiris.txt`，使用Bifid Cipher解密：

![](https://p5.ssl.qhimg.com/t01a14c2561dcd8285c.png)

搜索Giovan Battista Bellaso相关，确定下一步应使用维吉尼亚密码(Key是microwaves)：

![](https://p4.ssl.qhimg.com/t01198eb7b0f2b529b6.png)

解密以O开头文件：

![](https://p0.ssl.qhimg.com/t010b085a66ff9b53c5.png)

![](https://p4.ssl.qhimg.com/t01f1771f040e03fb8f.png)

![](https://p2.ssl.qhimg.com/t016f61e2f7754bf53b.png)

根据文件给出的推特账号进行搜索：

![](https://p1.ssl.qhimg.com/t017f02f7f43c6a2575.png)

从中提取出AES解密所需Key及IV：

![](https://p0.ssl.qhimg.com/t01ec446f2786bcc79c.png)

![](https://p5.ssl.qhimg.com/t012b41ffdf6c8184a0.png)

解密以T开头文件：

![](https://p4.ssl.qhimg.com/t01257e94bcfc505334.png)

![](https://p3.ssl.qhimg.com/t015d3f268831ea6a02.png)

![](https://p5.ssl.qhimg.com/t010ddc1e68d498bfb0.png)

`/etc/Quijote.txt`中内容来自《堂吉诃德》，使用在线西班牙语词频分析工具分析其中出现的独特单词个数：

![](https://p5.ssl.qhimg.com/t0139f4c00242e2a32c.png)

将所有十六进制ASCII码转换成字符：

![](https://p5.ssl.qhimg.com/t010c4fe28cc0b39140.png)

输入`dot`，得到Flag：

![](https://p1.ssl.qhimg.com/t01961355a1ca84cac0.png)

这道题目前面部分对勒索软件`zyppe`的分析是很有意思的，笔者之前未接触过Linux平台的恶意软件分析。后面部分环环相扣，梳理清楚逻辑之后按部就班使用CyberChef解密即可得出Flag，难度偏易。

## 0x02 Challenge 7:spel

题目只给了一个PE文件，查看基本信息：

![](https://p0.ssl.qhimg.com/t01163b6685e942fab3.png)

拖入IDA查看，分析了很长一段时间才完成，其函数数量非常多：

![](https://p0.ssl.qhimg.com/t011ed8fe05f51646c3.png)

放入沙箱中，没有检测出有效信息：

![](https://p2.ssl.qhimg.com/t019e990d326425d166.png)

运行界面：

![](https://p5.ssl.qhimg.com/t0133cedbc162d40f22.png)

关闭之后，可以看到其仍在后台运行：

![](https://p2.ssl.qhimg.com/t01a20d2cf3ba70531b.png)

看到官方WriteUp上提到capa，之前一直没有使用过该工具。按照[capa explorer
documentation](https://github.com/mandiant/capa/blob/master/capa/ida/plugin/README.md)给出步骤搭建好环境，capa
rules下载链接文中已经给出，下载到本地后于Settings——capa rules path一栏中填写即可。`capa.exe
spel.exe`部分输出结果：

![](https://p2.ssl.qhimg.com/t01b0d2682da630b30b.png)

将上面结果与IDA插件capa explorer分析结果结合，在Search一栏中输入”stackstring”，定位到相关函数后勾选”Limit
results to current function”：

![](https://p2.ssl.qhimg.com/t01244fdb54f1431145.png)

切换模式查看，发现是很长一段向栈中写值指令，直接跳转到0x14017973B处向上回溯：

![](https://p0.ssl.qhimg.com/t0123c0a66592581d38.png)

可以看到总长度为0x2ED2D，之后调用`VirtualAllocExNuma`函数申请同样大小且具有 **PAGE_EXECUTE_READWRITE**
权限的一块内存，并将内容复制到新内存块中，最终跳转到新内存块执行：

![](https://p4.ssl.qhimg.com/t0141c048eef3302150.png)

初始化部分寄存器之后跳转到Offset 0x40处执行：

![](https://p1.ssl.qhimg.com/t0153ce77b07b03083b.png)

以往笔者遇到下图向栈中写字符串操作，是通过动调在合适指令处设断点后观察内存：

![](https://p1.ssl.qhimg.com/t015acddfc1180fe640.png)

在看官方WriteUp时，看到其提及FLOSS与Ironstrings两个工具：

  * FLOSS：[Github Releases](https://github.com/mandiant/flare-floss/releases/tag/v1.7.0)
  * Ironstrings：[Github](https://github.com/mandiant/flare-ida/tree/master/python/flare/ironstrings)

关于Ironstrings的安装可以参考[FLARE Script Series: Recovering Stackstrings Using
Emulation with ironstrings](https://www.fireeye.com/blog/threat-research/2019/02/recovering-stackstrings-using-emulation-with-ironstrings.html)一文。

以`--no-static-strings`参数运行FLOSS：

![](https://p3.ssl.qhimg.com/t010b830d3e7ee59b5b.png)

执行ironstrings.py脚本：

![](https://p2.ssl.qhimg.com/t01396cef352181cfa7.png)

之后通过RCX传递Hash值给`sub_A1C`函数获取`LdrLoadDll`与`LdrGetProcedureAddress`调用地址：

![](https://p1.ssl.qhimg.com/t01fd378a7639374cbc.png)

将stackstring传递给上述两个函数获取地址并调用之，Offset
0xB28处存储一PE文件。`GetNativeSystemInfo`判断当前运行环境，获取PE文件Image Optional
Header中ImageBase及SizeOfImage字段值后调用`VirtualAlloc`函数申请内存空间(第一次以ImageBase作为`lpAddress`，申请失败则置为NULL)。接下来根据各区段VirtualAddress，PointerToRawData及SizeOfRawData加载区段至申请内存空间中，根据重定位表进行重定位。调用`VirtualProtect`设置各区段`flNewProtect`值，通过`RtlAddFunctionTable`函数设置异常，最终通过PE文件Image
Optional Header中AddressOfEntryPoint字段定位入口点完成加载。

关于以上描述过程使用的Reflective DLL Injection技术可参阅[DOUBLEPULSAR Usermode Analysis:
Generic Reflective DLL Loader](https://blog.f-secure.com/doublepulsar-usermode-analysis-generic-reflective-dll-loader/)一文。

将其加载DLL Dump出来之后，capa检测到其.data区段中存有另一PE文件：

![](https://p4.ssl.qhimg.com/t01c415dc941ef6399c.png)

从EntryPoint执行到DllMain，传递PE文件存储地址给加载函数进行加载：

![](https://p2.ssl.qhimg.com/t01a9a6d6a1b57ed3f2.png)

![](https://p0.ssl.qhimg.com/t018f04e43d8c86d82b.png)

之后调用`sub_27327D0`获取其导出函数Start地址进行调用：

![](https://p0.ssl.qhimg.com/t012f04731e607310db.png)

![](https://p3.ssl.qhimg.com/t01b55ca09c1d63403c.png)

首先是异或解密stackstring：

![](https://p3.ssl.qhimg.com/t01a0989794095766e9.png)

其流程是申请一块内存—>向栈中写值—>XOR解密—>复制至申请内存空间，官方WriteUp中给出了解密IDAPython脚本，笔者分析时直接在函数结束处设置断点，观察内存内容：

![](https://p4.ssl.qhimg.com/t01159bc89fc694b83f.png)

官方WriteUp中提到一个IDA Plugin——Shellcode
Hashes，笔者觉得很好用，可以提高静态分析的效率和体验。该插件与上文提及的Ironstrings都位于[flare-ida](https://github.com/mandiant/flare-ida)中，将shellcode_hashes_search_plugin.py与`flare`目录一同复制到IDA的`Plugins`目录之后即可使用，选择`\flare-ida\shellcode_hashes`目录下的`sc_hashes.db`数据库文件即可：

![](https://p2.ssl.qhimg.com/t01c8bd0e8f936dfc4d.png)

![](https://p2.ssl.qhimg.com/t01966adc1b4f0a9c9c.png)

![](https://p5.ssl.qhimg.com/t0131eb3a62ccfc4707.png)

前者是上文提及`sub_A1C`函数，后者是最后Dump出来的DLL中函数。

接下来调用`sub_180001A40`，`sub_180001990`会调用该函数两次——第一次传递给它的第二个参数值为1，第二次传递有两种情况：2或是8，若Filename为”Spell.EXE”则传递2，否则传递8。第一次调用会解密一串字符串，获取Filename及加载名为PNG的资源：

![](https://p2.ssl.qhimg.com/t015b4012f1380c5c67.png)

![](https://p2.ssl.qhimg.com/t015623b96e0e612e58.png)

![](https://p0.ssl.qhimg.com/t0103e3f2d29c6a20ac.png)

`sub_180001A40`保存获取到的相关信息时结构如下(后面还有一串字符`inactive`，没有放在图中)：

![](https://p5.ssl.qhimg.com/t0135f21fb3cb9828f5.png)

`sub_180002E60`函数判断Filename是否等于”Spell.EXE”：

![](https://p4.ssl.qhimg.com/t014ec11db0bae48eed.png)

![](https://p3.ssl.qhimg.com/t01d84380da1d374b74.png)

若不等返回0，那么传递给`sub_180001A40`函数第二个参数值为8：

![](https://p2.ssl.qhimg.com/t013ee07265065bcb8e.png)

直接退出：

![](https://p3.ssl.qhimg.com/t0169d553d9b6cceac2.png)

将程序命名为”Spell.EXE”之后再次调试，便可进入到`sub_180001A40`函数处理第二个参数为2的情形：

![](https://p0.ssl.qhimg.com/t015e05a71a8365cdfa.png)

第二个参数为2时会调用`sub_180001F80`，该函数会向inactive[.]flare-on[.]com发起连接，根据接收到的不同命令执行不同的操作。后续在看官方WriteUp时，其提到FakeNet-NG工具，笔者在虚拟机里按照[FakeNet Genie: Improving Dynamic Malware Analysis with Cheat
Codes for FakeNet-NG](https://www.mandiant.com/resources/improving-dynamic-malware-analysis-with-cheat-codes-for-fakenet-ng)一文进行了配置，之后再次进行调试，分析出`sub_180002070`函数(由`sub_180001F80`调用)会处理三种命令：

  * exe：调用`sub_180002410`
  * run：调用`sub_180002590`
  * flare-on.com：返回1

`sample_custom_response.ini`中TcpRawFile字段为同目录下文件，该文件存储要返回的命令：

![](https://p1.ssl.qhimg.com/t017bdbe7fffefbdb77.png)

![](https://p4.ssl.qhimg.com/t013831b4485559c924.png)

当该函数返回1时，会进入到之后的`sub_180002A20`函数，设置注册表键值。接下来调用`sub_180002F70`，若返回1则进入`sub_180002730`设置另一注册表键值。第一个设置的键值：

![](https://p2.ssl.qhimg.com/t01955fe092e86097d9.png)

该结果由”flare-on.com”与`0x1B8A7E991DC19F1415891D8A`异或而来：

![](https://p4.ssl.qhimg.com/t0107f5dd01a392d007.png)

![](https://p0.ssl.qhimg.com/t01a91deeb20d85b20d.png)

![](https://p4.ssl.qhimg.com/t013333e1d251957cff.png)

`sub_180002730`通过switch将Flag与`0xFAE58ED80D859C9B8D87ACD7A7B7A4E2C3C1A806C29633`进行异或：

![](https://p4.ssl.qhimg.com/t01c89e9a8ad45bdea8.png)

之后再次调用`sub_180002A20`设置第二个键值：

![](https://p3.ssl.qhimg.com/t0170af37ec1640e2d9.png)

![](https://p4.ssl.qhimg.com/t01acd85a6515463ff6.png)

这道题目很贴合实际的样本分析，官方WriteUp中有这样一段话可以概括之：This challenge was inspired by multiple
malware samples we’ve analyzed over the last year。其使用的Reflective DLL
Injection技术，stackstring，API
Hashes，混淆字符串直到使用时才解密，C2等笔者在之前的样本分析过程都曾遇到过，而此题将其都融合在一个里面，是很有意思的一道题目。在分析过程中，结合官方WriteUp学习了几个新工具或是IDA
Plugin(capa，FLOSS，Ironstrings，shellcode_hashes，FakeNet-NG)的使用，方便以后的样本分析。

## 0x03 参阅链接

  * [crontab(5) — Linux manual page](https://man7.org/linux/man-pages/man5/crontab.5.html)
  * [getenv(3) — Linux manual page](https://man7.org/linux/man-pages/man3/getenv.3.html)
  * [readdir(3) — Linux manual page](https://man7.org/linux/man-pages/man3/readdir.3.html)
  * [Linux编程—readdir](https://www.jianshu.com/p/fab29726e763)
  * [RC4—Wikipedia](https://en.wikipedia.org/wiki/RC4)
  * [教你三招快速文件批量重命名方法](https://segmentfault.com/a/1190000024416655)
  * [Bifid cipher—Wikipedia](https://en.wikipedia.org/wiki/Bifid_cipher)
  * [FireEye’s Open-Source Tool – CAPA to Identify Malware Capabilities](https://www.socinvestigation.com/fireeyes-open-source-tool-capa-to-identify-malware-capabilities-2/)
  * [DOUBLEPULSAR Usermode Analysis: Generic Reflective DLL Loader](https://blog.f-secure.com/doublepulsar-usermode-analysis-generic-reflective-dll-loader/)
  * [Using Precalculated String Hashes when Reverse Engineering Shellcode](https://www.mandiant.com/resources/precalculated-string-hashes-reverse-engineering-shellcode)
  * [FakeNet Genie: Improving Dynamic Malware Analysis with Cheat Codes for FakeNet-NG](https://www.mandiant.com/resources/improving-dynamic-malware-analysis-with-cheat-codes-for-fakenet-ng)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERFZE** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/265361](/post/id/265361)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Malware](/tag/Malware)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhimg.com/t01a9ce08613e49eaf2.png) ERFZE

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


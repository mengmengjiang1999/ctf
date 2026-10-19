## 序言

前两天在“蜂鸟”图标的社交网站看到一个高危样本，便下载审查一番。文件是一个压缩包，压缩包中有两个普通图片、一个EXE和一个DLL文件（wwlib.dll）。

![](https://image.3001.net/images/20190904/1567611648_5d6fdb00c33f4.png!small)

通过使用VirusTotal查询MD5后发现只有wwlib.dll被杀毒引擎检出为恶意文件，于是笔者不老道的经验判断这是一个普通的DLL劫持操作。在一番动态运行后发现确实如此，然后就按照DLL劫持的分析思路进行分析，结果并没有找到具体得恶意代码执行处。之后经过多个小时的奋斗，终于发现wwlib.dll使用类似“热补丁”技术修改了系统ntdll.LdrLoadDLL函数的返回地址使其跳转到wwlib.dll的恶意函数进而执行多层shellcode。

热补丁：又称为patch，指能够修复[软件漏洞](https://baike.baidu.com/item/%E8%BD%AF%E4%BB%B6%E6%BC%8F%E6%B4%9E/3879396)的一些[代码](https://baike.baidu.com/item/%E4%BB%A3%E7%A0%81/86048)，是一种快速、低成本修复产品软件版本缺陷的方式，可以运行状态下对程序进行修复。

## “热补丁”位置

压缩包中的exe文件作用只是用来加载wwlib.dll，所以我们只对wwlib.dll进行详细分析。

文件名：wwlib.dll

MD5：6875f307d95790ca25c1da542ea736a8

wwlib.dll被加载后首先执行sub_1000101A函数，获取ntdll.LdrLoadDll的函数地址并将其返回地址进行修改。

![](https://image.3001.net/images/20190904/1567611693_5d6fdb2d169a5.png!small)

ntdll.LdrLoadDll的返回地址被修改为跳转到wwlib.dll的sub_1000168E函数。

修改前：

![](https://image.3001.net/images/20190904/1567611764_5d6fdb740a13f.png!small)

修改后：

![](https://image.3001.net/images/20190904/1567611773_5d6fdb7d573ea.png!small)

除了以上修改外作者还开辟了新的内存空间并写入跳转到ntdll.LdrLoadDll返回地址7c9364ee的代码。但是在调试时并未发现有执行改代码的操作，怀疑是作者的测试代码。

![](https://image.3001.net/images/20190904/1567611807_5d6fdb9f4ee08.png!small)

修改了以上代码就能确保恶意代码被顺利执行。

## 如何触发执行恶意代码？

以下结果是使用32位的win
XP调试而得。当加载DLL文件时调用Kernel32.LoadLibraryA函数，经过下图中的层层调用最终执行ntdll.LdrLoadDll函数。

![](https://image.3001.net/images/20190904/1567611945_5d6fdc29428e8.png!small)

由于ntdll.LdrLoadDll函数的返回地址“7c9364ee”被修改为跳转到wwlib.1000168E地址。“热补丁”设置成功后只要进行加载DLL动作即可触发恶意代码，下面是对恶意代码下断点分析的内容。

## 解密执行shellcode

恶意代码首先将修改过的ntdll函数返回地址恢复，对比上一节的图片可知将“E9 9B B1 6C 93”恢复为“C2 10 00 90 90”。

![](https://image.3001.net/images/20190904/1567611984_5d6fdc507c733.png!small)

将解密后的shellcode拷贝到新开辟的内存空间并执行。

![](https://image.3001.net/images/20190904/1567612022_5d6fdc7617b8b.png!small)

启动线程进行连接C2操作。

![](https://image.3001.net/images/20190904/1567612140_5d6fdceccd60e.png!small)

获取网卡信息。

![](https://image.3001.net/images/20190904/1567612171_5d6fdd0ba365e.png!small)

线程解密C2地址后启动新的线程进行网络操作。

![](https://image.3001.net/images/20190904/1567612201_5d6fdd2993156.png!small)

请求地址https:// cloud.doomdns.org/hk12获取下一阶段shellcode代码。

![](https://image.3001.net/images/20190904/1567612234_5d6fdd4a87d50.png!small)

执行下载的shellcode代码。

![](https://image.3001.net/images/20190904/1567612288_5d6fdd801f6b5.png!small)

## 总结

详细分析后发现这并不是一个简单的DLL劫持操作，而是通过精心构造的跳转执行恶意代码。shellcode代码虽然有很多层，但是执行逻辑与代码风格基本相同。只要耐下心来，一层一层跟下去就能找到恶意代码的执行逻辑。

想到很多朋友不能在VirusTotal直接下载样本，笔者将本文的样本放置在github上供大家学习研究。本文种若有遗漏错误之处，欢迎大家批评指正、留言交流。

样本地址：

> <https://github.com/ShareSample/Hot-Patch-Sample>

## IOC

> 3061f320d47a6c985bd219f5ac14ff8a
>
> cloud.doomdns.org
>
> https:// cloud.doomdns.org/hk12

 ***本文原创作者：DD黃藥師BB，本文属于FreeBuf原创奖励计划，未经许可禁止转载**


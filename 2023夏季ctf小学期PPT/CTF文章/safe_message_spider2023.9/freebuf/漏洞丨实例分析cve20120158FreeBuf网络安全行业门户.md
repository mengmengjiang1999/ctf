## 一、漏洞简介

CVE-2012-0158是一个office栈溢出漏洞，Microsoft Office 2003
sp3是2007年9月18日由微软公司创作的一个办公软件，他的MSCOMCTL.ocx中的MSCOMCTL.ListView控件检查失误，由于读取长度和验证长度都在文件中，这样参数可以人为修改，触发缓冲区溢出漏洞。

## 二、漏洞环境准备

系统版本

|

目标程序

|

调试软件

|

16进制编辑器  
  
---|---|---|---  
  
XP SP3

|

Microsoft Office 2003

|

od、x32dbg

|

010Editor  
  
## 三、漏洞验证

这里我借用了一个帖子的POC，借用POC帖子(https://bbs.pediy.com/thread-207638.htm)  
在XP SP3中安装office2003：

![](https://image.3001.net/images/20221214/1670998875_63996b5b5aaf198141a9b.png!small)

之后下载POC。拖到虚拟机中，用office打开，弹出个计算机（注意这个POC用一次会损坏，需要备份）：

  

![](https://image.3001.net/images/20221214/1670998877_63996b5d22e62d3e28900.png!small)

## 四、漏洞分析

首先用OD附加office，F9运行，然后用office打开POC文件（新的）：

  

![](https://image.3001.net/images/20221214/1670998877_63996b5dd1d77acaa89e7.png!small)

查看堆栈：

![](https://image.3001.net/images/20221214/1670998878_63996b5e6d0cb13a698c3.png!small)

啥也没看出来，堆栈前后看了一下也没发现形似shellcode的东西，下了几个断点也没有，只能另寻他法！  
俩个办法

（1）把POC拖到010Editor看看有没有特征可以看看  
（2）对弹出计算器用到的函数下断点

先用第一个办法：  
拖到010Editor中，搜搜有没有9090（nop滑板指令，大部分会有这种指令用来凑数或者保护数据等）之类的，运气不错，找到相似的。

  
![](https://image.3001.net/images/20221214/1670998879_63996b5f286839f1aac91.png!small)

9090909090909090前面有四个字节，像一个库里面的地址7FFA4512，后面一堆看着像shellcode，附加office，看看这个地址是个啥东西：

![](https://image.3001.net/images/20221214/1670998879_63996b5fa9eb3ab1d9a48.png!small)

一个jmp esp，典型的跳板指令，差不多就是这个地方溢出返回值，我们尝试改一下这里，验证一下：

![](https://image.3001.net/images/20221214/1670998880_63996b605dc6eeae8c40a.png!small)

把这个跳板改成11111111试试：

![](https://image.3001.net/images/20221214/1670998881_63996b611fc7ee6925d37.png!small)

保存，OD附加office，打开poc，EIP果然等于11111111：

![](https://image.3001.net/images/20221214/1670998881_63996b619740ed84678a8.png!small)

这就算撞到了溢出点，我们用原来的POC，在jmp esp这里下硬件断点看看堆栈情况：

![](https://image.3001.net/images/20221214/1670998882_63996b622871bc1a11a86.png!small)

断点断在jmpesp，继续运行，到了shellcode的地方：![](https://image.3001.net/images/20221214/1670998882_63996b62bb95610408149.png!small)

从这里也能够看出溢出函数末尾是ret 8，esp直接+8，F8运行几步，弹出计算器：

![](https://image.3001.net/images/20221214/1670998883_63996b63a47c9f06d3a43.png!small)

我们试着替换shellcode，改成自己的弹窗shellcode，不改变文件原来大小，替换掉9090909090909090后面的shellcode就行，因为我的shellcode结尾会自动退出程序，所以不需要管原来shellcode长度过长的问题，但是这里卡了一个bug，修改完shellcode之后，并没有出现弹窗，猜想可能是我们自己的shellcode结尾接了原来的字节码，导致识别出错，于是我把我们的弹窗shellcode后面8字节改成90，成功弹窗（这里发现改过得POC不再是一次性的了，可能是因为弹窗shellcode长度较小，不会被破坏）：![](https://image.3001.net/images/20221214/1670998884_63996b643f90cdd615c0f.png!small)

下面给出我刚才替换的弹窗shellcode：

FC 68 6A 0A 38 1E 68 63 89 D1 4F 68 32 74 91 0C  
8B F4 8D 7E F4 33 DB B7 04 2B E3 66 BB 33 32 53  
68 75 73 65 72 54 33 D2 64 8B 5A 30 8B 4B 0C 8B  
49 1C 8B 09 8B 69 08 AD 3D 6A 0A 38 1E 75 05 95  
FF 57 F8 95 60 8B 45 3C 8B 4C 05 78 03 CD 8B 59  
20 03 DD 33 FF 47 8B 34 BB 03 F5 99 0F BE 06 3A  
C4 74 08 C1 CA 07 03 D0 46 EB F1 3B 54 24 1C 75  
E4 8B 59 24 03 DD 66 8B 3C 7B 8B 59 1C 03 DD 03  
2C BB 95 5F AB 57 61 3D 6A 0A 38 1E 75 A9 33 DB  
53 68 66 66 66 66 68 66 66 66 66 8B C4 53 50 50  
53 FF 57 FC 53 FF 57 F8

这是替换shellcode结尾部分：

![](https://image.3001.net/images/20221214/1670998884_63996b64e0604e8e12be9.png!small)

这是一次简单的替换，接下来我们继续分析这个漏洞的前因后果，我们使用改过的的弹窗POC，我们在jmp esp处下断点：

![](https://image.3001.net/images/20221214/1670998885_63996b65c160156ae1fdb.png!small)

断点断在jmp esp处，我们在栈的前面发现调用了一个MSCOMTL模块的函数，我们调到对应的地址上面，记录这个地址275C8A0A，并下断点：

![](https://image.3001.net/images/20221214/1670998886_63996b6683e50efb2b4eb.png!small)

重新运行，断在了断点处：

![](https://image.3001.net/images/20221214/1670998887_63996b67567d9d15326d7.png!small)

F8单步调试，发现这个函数结束后，弹窗弹出，说明这个函数就是关键函数，而结尾也如我们之前所想，是ret 8：

![](https://image.3001.net/images/20221214/1670998887_63996b67eabf6bf60f85e.png!small)

接下来就是着重分析这个函数，重新调试，断在这个函数头部（push ebp是函数头）：

![](https://image.3001.net/images/20221214/1670998888_63996b68a7320ae62d5e9.png!small)

我们发现执行完下面这个函数，返回值被修改，我们shellcode拷贝进去，也即是说这个拷贝函数是关键函数：

![](https://image.3001.net/images/20221214/1670998889_63996b69721d9c005181a.png!small)

继续分析这个函数，下断点，重新运行，断在关键函数

这里：

![](https://image.3001.net/images/20221214/1670998890_63996b6a29f4672171659.png!small)

F7跟进去，分析函数：

![](https://image.3001.net/images/20221214/1670998890_63996b6ab3ef29319ced6.png!small)

拷贝参数ECX=8282，这是一个关键点，拷贝之后，返回地址被淹没，因为这个漏洞就是因为拷贝长度都在文本中存着，所以我们试着在POC中搜索8282：

![](https://image.3001.net/images/20221214/1670998891_63996b6b6d0fa95e4e582.png!small)

这里有俩个8282，我们都修改一下，分别改成1111和2222，再回到这个函数观察：

![](https://image.3001.net/images/20221214/1670998892_63996b6c39f95a4e4d4db.png!small)

可以看到数据已经不同，有点缺陷是我们改的姿势不对，数据变成02001111和02022，接下来运行会卡住，所以这里是一个验证代码，俩个数值只能相等，继续把俩处地址改成2222，直接观察关键函数里面拷贝那块的ECX赋值结果：

![](https://image.3001.net/images/20221214/1670998893_63996b6d567609be42d16.png!small)

和我们预期一样，文本中原来2个8282是拷贝字符串长度还有其验证，俩者必须一样，其次会根据这个数值对字符串进行拷贝。下面给一张图解：

![](https://image.3001.net/images/20221214/1670998894_63996b6e0a14d1e0a78e3.png!small)

前俩个红线处是拷贝长度还有其验证数值，第三个红线是一个jmp esp跳板，之后隔八字节就可以放shellcode。

# 五、结束

CVE-2012-0158这个漏洞分析到此结束。


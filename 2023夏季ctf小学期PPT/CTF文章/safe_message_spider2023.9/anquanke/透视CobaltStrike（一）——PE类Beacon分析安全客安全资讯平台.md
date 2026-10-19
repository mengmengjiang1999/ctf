# 透视CobaltStrike（一）——PE类Beacon分析

阅读量 **295268**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-21 14:30:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0143994605f2f662e3.jpg)

## 背景

CobaltStrike作为先进的红队组件，得到了多个红队和攻击者的喜爱。2020年年底的时候，看到有人在传cs4.2，于是顺便保存了一份。然后一拖就到了今天才打开，关于CobaltStrike外层木马的分析网上已经有很多，但是内层的payload好像没有多少分析文章，那我就刚好借4.2这个契机，详细分析一下CobaltStrike的组件。

## 测试上线

为了使得文章更加完整，还是花少量的篇幅介绍一下CobaltStrike的基本使用，关于使用方面的详细介绍，可以在网上找到很多文章，笔者也正在翻译CobaltStrike4.2的官方文档。

网络情况如下  
kali:192.168.74.134  
win7:192.168.74.128

首先需要保证kali和win7之前的系统能互通。

![](https://p3.ssl.qhimg.com/t0193bd664568a65905.png)

通常来说一个网段内就不会有啥问题，如果出现win7能ping通kali，但是kali无法ping通win7的情况，多半是win7主机的防火墙原因，关闭即可：

![](https://p2.ssl.qhimg.com/t01e0fc7193ef1c9966.png)

接下来解压4.2的包得到如下文件：

![](https://p0.ssl.qhimg.com/t019e481cf5becb22eb.png)

按道理来说，应该单独启一个服务器作为CobaltStrike的teamServer，这里为了方便就直接在kali上启动了。

首先在kali上启动teamserver这个文件，参数1是服务器地址，这里填本机地址，参数2是登录密码 这里填的123456

![](https://p1.ssl.qhimg.com/t010b0b2d80dc223108.png)

接着使用另外一个终端进入到此目录然后启动CobaltStrike文件然后将host和pasword更改为刚才设置的地址即可：

![](https://p5.ssl.qhimg.com/t0192237c19c71f9e60.png)

成功登录上CobaltStrike客户端：

![](https://p2.ssl.qhimg.com/t01594d2f0c09a4eaf5.png)

连接上服务器之后，首先通过这个耳机图标添加一个监听器

![](https://p3.ssl.qhimg.com/t01644b2167b25af638.png)

监听器的话主要是分为Beacon和Foreign。

Beacon译为信标，是目前CobaltStrike最常用的监听器，Beacon系列的协议为CobaltStrike内部协议，包括DNS、HTTP、HTTPS等常见协议，Foreign是外部监听器，可与MSF或Armitage交互

![](https://p1.ssl.qhimg.com/t019eb12eda04e857b3.png)

实验方便，这里就创建一个HTTP类型的Beacon

![](https://p2.ssl.qhimg.com/t01df6fac4ee7bcd3f5.png)

以exe为例，监听器设置好之后，在选项菜单中选择

Attacks -> Packages -> Windows Executable(S) 创建样本，选择好协议之后点击Generate然后选择保存路径即可。

![](https://p2.ssl.qhimg.com/t016fa70c6f6061f231.png)

这里顺便说一下，关于Attacks的几个选项，Attacks的Packages下一共有五个选项

![](https://p4.ssl.qhimg.com/t01e6507660cc157dc5.png)

其中  
HTML Application 生成hta形式的恶意payload  
MS Office Macro 生成宏文档的payload  
Payload Generator 生成各种语言的payload

![](https://p0.ssl.qhimg.com/t01427c473e9afcc1a2.png)

Windows Executable 生成可执行的分段payload  
Windows Executable(S) 生成可执行的不分段Payload

如果选择了分段payload，也就意味着生成的原始文件会很小，原始文件是一个downloader，用于从C2下载并加载后续的payload。反之，如果选择不分段的payload，则原始文件是一个loader，可以直接将shellcode加载执行。  
目前比较主流的方式应该是不分段。

需要注意的是，由于CobaltStrike的木马是框架生成的，所以理论上来讲，不会存在两个完全一样的CobaltStrike木马，即便使用同样的方式生成木马，得到的文件也是不同的。.

这里我按照一样的流程，生成了两个样本，通过对比工具可以看到两个代码段差不多，但是data段完全不同。

![](https://p0.ssl.qhimg.com/t011414f6fb568ce41e.png)

此时将其中一个exe复制到win7中运行，即可成功上线：

![](https://p1.ssl.qhimg.com/t01238cce283e50d1bc.png)

关于上线后可对目标主机执行的操作这里不在赘述，后面为对恶意样本的二进制分析。

## 不分段Beacon分析

###  外层loader

原始的Beacon是一个loader，样本WinMain中主要是调用了sub_4027F0和sub_401840两个函数，最后有一个10s的死循环

![](https://p5.ssl.qhimg.com/t019d69f7bfedf022a4.png)

经过简单分析，第一个函数sub_4027F0没有什么实际功能，主要功能在第二个函数sub_401840中，该函数主要是拼接一个管道名称然后创建线程执行sub_401713函数

![](https://p1.ssl.qhimg.com/t0134daaa042fdadb2b.png)

在1713函数中程序会通过1648函数进行管道创建和和连接

![](https://p4.ssl.qhimg.com/t0198eaeff7173498cd.png)

此样本创建的管道名为\\\\.\pipe\MSSE-1480-server，连接管道之后通过WriteFile将edi所指向的第一段数据写入到管道中

![](https://p0.ssl.qhimg.com/t01e3066df4e3db2276.png)

该段数据硬编码在文件的data段偏移14的地方：

![](https://p1.ssl.qhimg.com/t010dbdeddca3735bc0.png)

至此，线程执行完成，线程1的功能主要是创建管道并将data段预编码的数据读取到管道中，读取完成之后，程序会jmp到sub_4017e2继续执行

![](https://p2.ssl.qhimg.com/t015bd942d060202217.png)

17E2函数首先会通过malloc分配一段空间，在sleep之后通过ReadFile去将管道中的数据读取出来

![](https://p2.ssl.qhimg.com/t0192193b8c8629517f.png)

读取到这片shellcode之后，程序会通过VirtualAlloc分配一片内存，然后通过一个循环异或解密数据放入到这片内存中

![](https://p4.ssl.qhimg.com/t015f20db75ffa95f6e.png)

经过分析可知，这里是在循环异或四个字节的数据，这四个字节的数据所在位置是[ebp+10]的地方，也就是00403008

![](https://p5.ssl.qhimg.com/t0147fd44690659b792.png)

这段用于循环异或的数据就在data段偏移8的地方，在此样本中用于循环异或的数据是D1 1B 2E 36

![](https://p2.ssl.qhimg.com/t01dd33896425c03089.png)

异或的第二段数据就是刚才从管道读出来的数据：

![](https://p0.ssl.qhimg.com/t01b593a1ed902f7523.png)

两段数据成功异或解密出一段shellcode，将该段shellcode保存为1.bin

![](https://p5.ssl.qhimg.com/t011e3bbb0d5b70a6dd.png)

解密之后程序会创建线程2，在线程2中jmp eax跳转到shellcode执行：

![](https://p2.ssl.qhimg.com/t01b51737228c8d7ef0.png)

###  内层shellcode

内层的shellcode入口如下

![](https://p4.ssl.qhimg.com/t01aa8c05eac2d75ee3.png)

程序会在第一个call ebx中VirtualAlloc分配一段内存空间，然后将005D0000这段数据拷贝过去，然后在call
eax处跳转到后面的代码继续执行：

![](https://p3.ssl.qhimg.com/t01af186bb32efa907f.png)

过来之后，通过入口处的hex数据可知这里实际上是1.bin中的DLLEntryPoint：

![](https://p3.ssl.qhimg.com/t01be00819b36cd3650.png)

**网络请求**

在DLL_main函数中解密出请求地址：

![](https://p0.ssl.qhimg.com/t0140afbb4414c7bc55.png)

解密请求头和请求路径：

![](https://p0.ssl.qhimg.com/t01fb7ed68a1d80e107.png)

与目标服务器建立连接

![](https://p3.ssl.qhimg.com/t019b9a4190777e5a0d.png)

Http方式进行通信，请求协议为GET：

![](https://p3.ssl.qhimg.com/t0152f567255dea0f71.png)

成功通信后，通过InternetReadFile读取返回值存到eax中：

![](https://p3.ssl.qhimg.com/t018950d7ce64e34669.png)

程序解析返回值，然后将其传递到sub_10007E69函数中根据switch执行对应的操作，这里一共是101个case，表示4.2的CobaltStrike应该至少有101种不同的操作：

![](https://p5.ssl.qhimg.com/t01fb7bb88349cabbe4.png)

以<ls>指令为例，当攻击者在CobaltStrike服务端输出<ls>指令之后，C端的CobaltStrike会进入到 case
52，获取当前路径下所有的文件信息：

![](https://p3.ssl.qhimg.com/t01401a694cd7e523bb.png)

获取并保存所有信息：

![](https://p0.ssl.qhimg.com/t016f9fad10389d2ee4.png)

命令执行成功之后，程序会再次建立连接，用POST请求的方式将数据返回回服务器：

![](https://p3.ssl.qhimg.com/t0184344ed70f993428.png)

成功通信之后，程序最后会进行一个Sleep，Sleep时间默认为60s，服务器可更改这个时间。

![](https://p3.ssl.qhimg.com/t010db9507a37637804.png)

这里休眠的时间就是CobaltStrike的默认心跳时间，60s：

![](https://p1.ssl.qhimg.com/t017024d6ec71ffa595.png)

可以通过CobaltStrike的控制端修改休眠时间，这里修改为10s：

![](https://p5.ssl.qhimg.com/t017303388e27e465d5.png)

修改之后则下次通信开始休眠时间更改为10s

![](https://p5.ssl.qhimg.com/t01eac01753f9abb109.png)

到这里，原始的HTTP协议Beacon就基本分析完成了，受害者主机上线之后，会通过一个循环上线，循环中会有一个60s的sleep是CobaltStrike的默认心跳时长。

## shellcode对比

经过上面的简单分析，可以知道CobaltStrike默认的Beacon马是一个loader，主要是将data段偏移14地方开始的数据与data段偏移8开始的四个字节进行循环异或得到一个payload然后加载执行。解密出来的payload其实是一个dll文件，在dll的DllMain函数中会向目标C2发起网络请求，如果请求成功则解析服务器的返回值，根据返回值执行不同的语句，在此版本的Beacon中，一共有101个case。执行执行完成之后，会再次请求服务器并将数据返回回去，最后进行一个心跳休眠，默认是60s。

我们已经知道了使用相同的方法生成出来的马也是有很大差异的，他们的主要差异表现在解码之前的数据，前面的代码基本是一致的。

![](https://p3.ssl.qhimg.com/t01011c1c05327d24ce.png)

并且从上面的分析中可以得到的结论是，异或的两段数据其实是一整块数据，不同的是，数据1从data段偏移08的地方开始截取，数据2从data段偏移14的地方开始截取。

将两个loader异或解密得到的payload进行对比，可以看到的是两个样本前面的代码居然完全一致，仅有data段的部分数据不同：

![](https://p1.ssl.qhimg.com/t01daed63054e51aa49.png)

## 特征分析

首先来看看3.14版本和4.0版本的CobaltStrike
Beacon，总的来说，早期版本的Beacon到目前最新的4.2，默认生成的Beacon在代码层面几乎没有任何改变，入口点、函数调用、地址等等均保持一致：

![](https://p5.ssl.qhimg.com/t01a6063ad4e32f4981.png)

早期CobaltStrike的特征之一是在data段偏移0xC地方的值为连续的4个a:

![](https://p5.ssl.qhimg.com/t01e44892105ebc14e5.png)

经过简单的分析可以得知从3.14到4.0都保持着这样的特征，在上面的分析中可以得知CobaltStrike4.2的Beacon在解密内层dll时会从data段偏移0x8处取4个字节循环对0x14开始的地方进行异或。而早期的CobaltStrike解密方式是从data段0x08开始的地方取4个字节对0x10开始的地方进行循环异或。这算是一个比较大的改变。(从cs4.1开始，data段的数据就已经发生改变了)

![](https://p5.ssl.qhimg.com/t01cddcc90bce5f1af2.png)

此外，还有一个保持到了4.2的特征是位于rdata头部的管道名格式：%c%c%c%c%c%c%c%c%cMSSE-%d-server

![](https://p0.ssl.qhimg.com/t01cbe97d8b6f6dd20e.png)

由于CobaltStrike最开始设计的一个重要反沙箱思想就是通过管道读取数据，如果沙箱不模拟管道，那么就不能跑到后续的dll。虽然CobaltStrike目前已经不靠这个进行免杀和反沙箱，但设计之初的架构导致了CobaltStrike截止到4.2版本，默认生成的Beacon还是保留了该协议，所以该断管道协议是CobaltStrike的重要特征。可以直接使用yara规则对该段字符串进行查询。

所以理论上来讲，若攻击者使用默认配置生成CobaltStrike木马并且未对程序进行改变的话，还是非常容易识别的。

但是也有例外：

![](https://p3.ssl.qhimg.com/t018971438a0f3628e5.png)

所以笔者在思考有没有什么方式能更简单粗暴的识别默认的CobaltStrike，而不用去考虑它在data段偏移0xC的地方是否是连续的4个a，不用考虑样本数据是否通过管道传输。

回到4.2Beacon样本的分析中，根据解密后payload的头部数据可以推测出如下一条CobaltStrike的特征：

data节偏移08的地方开始往后数4个字节，异或data节偏移14的地方开始往后数10个字节，应该得到payload头部的十个字节(针对CobaltStrike4.2版本Beacon
HTTP监听器)：

4D 5A 52 45 E8 00 00 00 00

所以可以写个简单的脚本来判断样本是否为CobaltStrike4.2

    
    
    import pefile
    import binascii
    import sys
    import os
    
    def isCobaltStrike(fullFilePath):
        filepath = fullFilePath
        pe = pefile.PE(filepath)
        for section in pe.sections:
            secname = str(section.Name)
            if secname.find(".data") != -1:
                dataAddress = section.VirtualAddress
                #data段偏移8的地方开始取4个字节
                data1 = binascii.b2a_hex(pe.get_data(dataAddress+8,4))
                #data段偏移0x14的地方开始取9个字节
                data2 = binascii.b2a_hex(pe.get_data(dataAddress+0x14,9))
    
        datalist1 = []
        datalist2 = []
    
        for i in range(0,len(data1),2):
            tmp = (int(chr(data1[i]),16) * 16 + int(chr(data1[i+1]),16))
            datalist1.append(tmp)
    
        for i in range(0,len(data2),2):
            tmp = (int(chr(data2[i]),16) * 16 + int(chr(data2[i+1]),16))
            datalist2.append(tmp)
    
        xorintlist = []
        CobaltStrike42_shellcode_header = [77, 90, 82, 69, 232, 0, 0, 0, 0]
    
        #循环异或，判断异或后的数据是否是Beacon的dll 针对4.2
        for i in range(0,len(datalist2),1):
            if i < 4:
                xorint =int(datalist1[i]) ^ int(datalist2[i])
            else:
                xorint =int(datalist1[i%4]) ^ int(datalist2[i])
            xorintlist.append(xorint)
    
    
        if xorintlist == CobaltStrike42_shellcode_header:
            print( fullFilePath + "is CobaltStrike4.2")
    
    
    if __name__ == "__main__":
        if len(sys.argv) < 2:
            print("Usage: python3 getcs4.2.py <filePaht>")
            quit()
        else:
            filePath = sys.argv[1]
        for root,dirs,files in os.walk(filePath):
            for f in files:
                fullFilePath = os.path.join(root,f)
                with open(fullFilePath,'rb') as fp:
                    mz = fp.read(2)
                if mz == b"MZ":
                    isCobaltStrike(fullFilePath)
    

至于4.2之前的版本，就需要找到各个版本的cs生成Beacon，然后看看数据存放的位置，以及解密出来的shellcode头部了

![](https://p0.ssl.qhimg.com/t014c102ae1719cad67.png)

## 分段Beacon分析

接下来看看分段shellcode的样本。

分段shellcode样本大小虽然只有14kb，与278KB的不分段Beacon相差甚远，但前面的代码部分几乎是完全一致的，解密方法也还是data偏移08的地方数4个字节循环对data段偏移14的地方进行异或，解密之后jmp
eax跳转到shellcode执行：

![](https://p5.ssl.qhimg.com/t015d2ec0156f3c3001.png)

而此次解出来的shellcode不再是跟之前就完全不同：

![](https://p1.ssl.qhimg.com/t016017c60bbef4a245.png)

解密出来的shellcode主要是通过动态解密和jmp eax的方式完成的API的调用：

![](https://p1.ssl.qhimg.com/t018a6b0216ba87ad5c.png)

连接目标主机：

![](https://p0.ssl.qhimg.com/t018fef5216d6b9d5ee.png)

请求指定地址

![](https://p3.ssl.qhimg.com/t0193ef4bd4322cc246.png)

发起请求：

![](https://p4.ssl.qhimg.com/t01ef0f309d9b95e45c.png)

请求成功之后开辟一段新的内存空间：

![](https://p0.ssl.qhimg.com/t01d7511d67d93e725e.png)

通过多次InternetReadFile将返回回来的shellcode读取到新开辟的内存空间中

![](https://p4.ssl.qhimg.com/t01d3c5129a6ed1f494.png)

程序将所有的shellcode下载回来之后，会通过一个小循环对shellcode进行解密：

![](https://p2.ssl.qhimg.com/t01b27b3485ef6b28bc.png)

解密之后的shellcode和上面分析的内层dll就有点类似了：

![](https://p1.ssl.qhimg.com/t019b024382941eb334.png)

从3AE0056的4D 5A 52 45 E8 00 开始算，这后面的shellcode和之前解密出来的应该是同一个，call
ebx进去分配一段空间，将自身拷贝过去，然后call eax到新的内存空间去，call过去就是内层dll的dllmain函数。

![](https://p5.ssl.qhimg.com/t01bc31378b88a7ad05.png)

经过对两类样本的简单分析，可以看出CobaltStrike关键的代码都在dll中。无论是分段式的加载方式也好，不分段的加载方式也好，最后都由这个dll执行关键操作。所以理论上来讲，CobaltStrike的外层是可以随便改变的，只要能够把内层的dll加载起来就可以。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jux1a** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/228123](/post/id/228123)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [红蓝对抗](/tag/红蓝对抗)
  * [CobaltStrike](/tag/CobaltStrike)

 **+1** __9赞

 __收藏

![](https://p0.ssl.qhimg.com/t01c900f6a705a10464.png) jux1a

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


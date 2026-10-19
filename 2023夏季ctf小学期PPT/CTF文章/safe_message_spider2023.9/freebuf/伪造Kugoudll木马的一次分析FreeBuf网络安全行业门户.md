****

*****本文作者：索马里的海盗，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  
**

##  **0x1.背景**

 **近几天，在XX任务中发现存在异常诡异的流量最终通过端口定位到该程序，便是故事的开始。**  

### **基本信息**

 **![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533007205_5b5fd565634d3.png!small)**

复制到虚拟机上，简单查一下Proteug10 发现是一款专业电路仿真软件。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533007278_5b5fd5ae86e39.png!small)

是不是你们电路工程的同学转向做安全了啊  

Server.exe，无数字签名，仿冒其他软件，猜测是一个木马

资源未见敏感信息。

##  ** **0x2.动态行为分析****

挂着虚拟机运行程序对程序进行监视行为，分析监视数据。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533007504_5b5fd69025e6f.png!small)分析行为监控，发现程序将自己复制到了C盘Microsoft
Plarsb目录下，并且创建了服务来达到自启动目的。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533007578_5b5fd6da85c98.png!small)

并且程序对 121.18.238.56:8080和142.4.105.65:9090端口有网络访问，和当时设备监控的目标也是同一个。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533007631_5b5fd70fc5af9.png!small)![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533007644_5b5fd71c6954d.png!small)前者关机（或防ping），后者存活，推测可能在吃鸡。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533007693_5b5fd74dbe071.png!small)

查找到为美国服务器（发现近几年的恶意程序服务端IP大部分都是来自美利坚众合国）

端口扫描结果：

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533007743_5b5fd77f5b710.png!small)

端口开的太少如果开的多几率高一点，砸门可以搞一波反渗透本人渗透思路局限，还请大虾赐教。

##  ** **0x3.逆向分析****

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008063_5b5fd8bf36434.png!small)
程序开始获取InternetOpenA函数地址，推测可能会下载网络文件。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008202_5b5fd94a02ef5.png!small)

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008218_5b5fd95a562c3.png!small)（F6616FC73090D751AFD98A6194A14358）像是一个32位HASH。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008240_5b5fd97056718.png!small)

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008278_5b5fd996012be.png!small)

没解密出来唉，在这里开始大量出现程序内所用到的字符串。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008414_5b5fda1e93f03.png!small)

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008465_5b5fda5130e26.png!small)

这里出现了默认分组的字样，2010字样，并且在IP138查询了外网地址，猜测可能是GH0ST变种。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008491_5b5fda6b051e5.png!small)

提权。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009575_5b5fdea7d1f8e.png!small)

创建了以“傻逼360”命名的事件对象，可以确定不正常了。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008561_5b5fdab1da7fb.png!small)

确认目标路径存不存在，这里后面我用OD也跟到这里来了这个会先检测存不存这个文件，不存在就创建。  

木马又复制了一个新的程序到这个C:\program Files\Microsoft Plarsb\Nlwxaoc.exe

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008588_5b5fdacc1a57c.png!small)下面进入if了去判断，创建相应文件夹。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008743_5b5fdb6744e3d.png!small)

将自己拷贝至目标路径内。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008782_5b5fdb8ee7872.png!small)

运行拷贝过去的文件，它这样做和直接运行有啥区别吗，真是感叹作者的脑瓜。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008826_5b5fdbba3c81f.png!small)

到这程序申请内存和堆操作，最后ExitPROCESS，下面我用OD动态跟。  
![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008884_5b5fdbf49e726.png!small)

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008960_5b5fdc4069616.png!small)申请堆。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533008995_5b5fdc63ebc08.png!small)然后获取程序启动信息路径和程序自身的信息。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009032_5b5fdc88bdfff.png!small)之后获取系统启动信息：硬件型号，系统版本，系统环境变量。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009055_5b5fdc9fcb20a.png!small)

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009091_5b5fdcc390e81.png!small)释放新的文件，如上面从行为监控的大致一样。  

通过loadPE查看加载的DLL只有一个，但在内存中动态使用loadLibrary去加载其他DLL猜测是来躲避查杀软件检测。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009132_5b5fdcecabf28.png!small)

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009141_5b5fdcf5d9a6c.png!small)

这里还PUSH了一堆密文：  

    
    
    xepdy0Q/xlU4bgAmDBixsFQS1PVMwfwe4WfV0HkKVyhpPH+3PqGW0ugVvJ2UpqFD1mNQiNw8SFRK1EULt7q/BhA4ejT/BEVY6sU8CNeuKdHmUAsM766VbK1zVougYQWvTJ9kczqMSSMody1B39rGDSj5iqw76x4BjPPnq3BEOrT7Ptkw3HqNHs5ghFvuH7q5kWUbjQ0bmISMRlPZ2N1BXkfBv+XOWuPz+EBQwSXU2AIYVeEkd/9JaUjmyOsHzGxEGypoU9Spv7a4eKJEdgMEfug1g/9uUyGTElb2IFALYaAZbHGNOA8XkUMmB56zQvlxcVB6L7W0XwDbjGkYobD//6QSmNEyVZKPk83fuF+ZzstmxA2z0SSS4dAEGG2/m++k+K8ycWu5ucIsuUzAdx6D+ZJEr/PekcHMP5H3PeQGM3+lVC7NDscisDc4q4MjIX/KqZNFiWAipvBgOYQEN3BpN7K9cFKUhj2e/j/2CJfTAs+vWutmrT+IgSm4jm+RA2Qau1Y4GIQgocYTyQ==

![图片2.png](https://image.3001.net/images/20180731/1533009266_5b5fdd723cc86.png!small)

根据密文形式猜测，很有可能是AES/DES加密，根据12345678和12345678admins尝试解密失败。  

至此，程序一阶段执行完毕，大概行为：

> 1.确认C盘目标目录是否存在
>
> 2.创建目标目录并复制
>
> 3.启动复制后的文件
>
> 4.提权
>
> 5.一堆加密的代码
>
> 6.退出

我们跟到第二个阶段的程序看看有没有新东西。

程序启动（C:\Program Files\Microsoft Plarsb\Nlwxaoc.exe）：![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009705_5b5fdf29d1c3c.png!small)

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533011375_5b5fe5afd720c.png!small)

第二个程序中再次出现这段密文，我觉得很有必要在lstrlenA函数下断点跟一下。

在二次运行阶段第一次通过注册表创建了服务。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009774_5b5fdf6e1da82.png!small)删除C:\Picture.exe，下载<http://121.18.238.56:8080/aaa.exe>并再次通过API创建服务。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009799_5b5fdf87395fe.png!small)

第二阶段退出。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009826_5b5fdfa20d444.png!small)

到这程序也有申请内存和堆操作，最后ExitPROCESS，接着第三阶段。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009904_5b5fdff02ea42.png!small)![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533009913_5b5fdff9cb233.png!small)

开始连接此IP，并且打开网址：<http://r.pengyou.com/fcg-bin/cgi_get_portrait.fcg?uins=12345678> 由于朋友网接口失效，无法判断此网址作用。搞了那么久不会就是想交个朋友吧。

![u=3256093748,4221223979&fm=173&s=D5B336D51E625A134A29A0F903004033&w=500&h=363&img.JPEG](https://image.3001.net/images/20180731/1533010106_5b5fe0ba1e154.jpeg!small)

我尝试在VirtualAlloc下断，发现其动态申请了一段指定起始地址为10000000的内存。

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010134_5b5fe0d6dee17.png!small)

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010164_5b5fe0f40d6f8.png!small)

根据之前的信息进行推测这里应该还是一个模块，在10000000处下硬件写入断点看看是什么时候写入的数据：  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010187_5b5fe10b69569.png!small)

向上追踪esi地址，发现了一段经过UPX加壳的PE数据：  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010214_5b5fe126b54ed.png!small)

根据MZ头位置确定PE_HEADER：（0x0047005C+0x0128 = 0x00470184）  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010234_5b5fe13a117b1.png!small)

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010240_5b5fe14049dc0.png!small)

找到了NT头，找0B01，确定OPTIONAL_HEADER位置：  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010254_5b5fe14ea2c3d.png!small)

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010261_5b5fe1550a8d1.png!small)

SizeOfHeaders：0x1000  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010275_5b5fe1633ed9c.png!small)

NumberOfSections：3  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010296_5b5fe178810a9.png!small)

继续向下找节表，节表如图所示，共3个节，

> 第一个节名：UPX0，SizeofRawData：0
>
> 第一个节名：UPX1，SizeofRawData：00051400
>
> 第三个节名：rsrc，SizeofRawData：00001C00

故整个PE文件实际大小：SizeOfHeaders（0x1000）+ UPX0（0）+ UPX0（00051400）+ rsrc（00001C00） =
0x54000

用MZ头所在内存起始地址加上计算出来的整个文件的大小：

    
    
    0x47005C + 0x54000 = 4C405C

所以现在可以确定这个PE文件在内存里边的整段位置为：

0x47005C – 0x4C405C，在x32dbg中选中这段内存，右键保存为二进制数据，得到一个dll：

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010332_5b5fe19c0a034.png!small)

查看文件信息可得知，此文件伪装成酷狗音乐DLL文件运作：  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010356_5b5fe1b4b84d5.png!small)

加了UPX。  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010377_5b5fe1c9e68f0.png!small)

老规矩，ESP定律。

DLL导出表

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010461_5b5fe21d28a7a.png!small)

导入表中大多是一些之前简单分析的函数。

截屏

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010485_5b5fe235ac01c.png!small)

路由相关

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010503_5b5fe2473692d.png!small)

添加用户

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010523_5b5fe25bcbcf2.png!small)

下载文件  

![伪造kugou
dll木马的一次分析](https://image.3001.net/images/20180731/1533010548_5b5fe27494e88.png!small)

至此结束吧。这个木马最终会加载这个DLL至0x10000000并且进入这个模块继续执行，看了一下无非就是一些木马的常用功能。

按照以往做法这里是不是应该总结一张木马运行图，抱歉，运行图我不会画，但是画画我会，送上在下画的小鸡啄米图。

![搜狗截图18年07月31日1223_1.png](https://image.3001.net/images/20180731/1533011062_5b5fe476cfccb.png!small)

 ***本文作者：索马里的海盗，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  


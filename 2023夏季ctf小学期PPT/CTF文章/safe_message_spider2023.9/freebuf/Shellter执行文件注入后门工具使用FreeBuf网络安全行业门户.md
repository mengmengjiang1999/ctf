##

## Shellter介绍

Shellter 是将代码注入到正常的PE文件当中，将有效载荷重新编码（此处为 shellcode）以绕过防病毒 (AV)
软件，而且必须是32位的程序，应用程序的 PE（可移植可执行文件）文件格式的动态感染器。

## 下载及安装

Shellter可运行 Linux 、Mac 、Windows 环境，在 Windows 下运行，需要安装
Linux子系统，可通过官方提供地址进行下载：https://www.shellterproject.com/download/，搭建是在Kali环境下进行，个人感觉比较方便

    
    
    apt-get install shellter

![1623915002_60caf9fac772db0f22917.png!small?1623915003348](https://image.3001.net/images/20210617/1623915002_60caf9fac772db0f22917.png!small?1623915003348)

    
    
    dpkg --add-architecture i386 && apt-get update && apt-get install wine32

![1623915085_60cafa4d44eebed836727.png!small?1623915085755](https://image.3001.net/images/20210617/1623915085_60cafa4d44eebed836727.png!small?1623915085755)

    
    
    shellter 

![1623915133_60cafa7de023d3d37e65d.png!small?1623915134600](https://image.3001.net/images/20210617/1623915133_60cafa7de023d3d37e65d.png!small?1623915134600)

## Shellter使用

共有三个模式供选择

![1623915213_60cafacd4a7240068becb.png!small?1623915213831](https://image.3001.net/images/20210617/1623915213_60cafacd4a7240068becb.png!small?1623915213831)

选择自动模式，输入"A" 即可， 现在需要选择一个可执行（exe）文件 (exe) 必须为32位，要不然会报错无法执行），操作如下

![1623915629_60cafc6d291aefc4f0b78.png!small?1623915629514](https://image.3001.net/images/20210617/1623915629_60cafc6d291aefc4f0b78.png!small?1623915629514)

成功创建 DisASM.dll 文件

![1623915738_60cafcdacd6ee3690f96c.png!small?1623915739385](https://image.3001.net/images/20210617/1623915738_60cafcdacd6ee3690f96c.png!small?1623915739385)

启用隐身模式

![1623915996_60cafddc64f6d6196b740.png!small?1623915996828](https://image.3001.net/images/20210617/1623915996_60cafddc64f6d6196b740.png!small?1623915996828)

选择攻击载荷，这里自定义负载和有效负载，这里选择有效负载输入" L"

![1623916168_60cafe8804f79c154b644.png!small?1623916168558](https://image.3001.net/images/20210617/1623916168_60cafe8804f79c154b644.png!small?1623916168558)

设置 LHOST 和 LPORT 键入本地主机 IP 和会话使用的本地端口

![1623916287_60cafeff0d2e5611eb483.png!small?1623916287641](https://image.3001.net/images/20210617/1623916287_60cafeff0d2e5611eb483.png!small?1623916287641)

按回车继续，Shellter 程序会退出，执行文件已经修改好了

![1623917475_60cb03a37d9316ef9e00d.png!small?1623917476083](https://image.3001.net/images/20210617/1623917475_60cb03a37d9316ef9e00d.png!small?1623917476083)

运行MSF开启监听

![1623917179_60cb027bdee697b2f3c4b.png!small?1623917180594](https://image.3001.net/images/20210617/1623917179_60cb027bdee697b2f3c4b.png!small?1623917180594)

将修改好的 PE 执行文件运行

![1623917239_60cb02b767bc978d7cbe3.png!small?1623917239887](https://image.3001.net/images/20210617/1623917239_60cb02b767bc978d7cbe3.png!small?1623917239887)

  


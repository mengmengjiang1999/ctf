![](https://image.3001.net/images/20191218/1576635621_5df98ce5c16d3.png!small)

## 套件介绍

 **[ _Protobuf_](https://developers.google.com/protocol-buffers/)是Google设计的一种序列化格式，目前已被广泛应用在各种Android端、Web端和桌面端应用程序之中。它由一种用于声明数据结构的语言组成，并且能够根据目标的实现方式，来为其编译代码以及其他类型的结构数据。**

PBTK（Protobuf toolkit）是一套功能完整的脚本，可以通过统一的GUI来访问，PBTK主要提供了以下两个重要功能：

一、从目标程序中提取Protobuf结构，将其转换回可读的.protos格式，并且支持下列实现：

> 1、所有主流的Java运行时（base, Lite, Nano, Micro, J2ME），以及完整的Proguard支持；
>
> 2、二进制代码包含嵌入式反射元数据（通常是C++，有时是Java和其他绑定）；
>
> 3、使用JsProtoUrl运行时的Web应用程序；

二、通过一个方便的图形界面编辑、重放和模糊化发送到Protobuf网络端点的数据，该界面允许您实时编辑Protobuf消息的字段并查看结果。

![](https://image.3001.net/images/20191218/1576635643_5df98cfb371ac.png!small)

## 工具安装

PBTK要求使用Python >= v3.5、PyQt 5、Python-Protobuf
3以及其他的依赖组件（例如Chromium、jad和dex2jar等等）来运行提取脚本。

Archlinux用户可以直接运行[ _下列命令_](https://aur.archlinux.org/packages/pbtk-git/)来完成安装：

    
    
    $ yaourt -S pbtk-git
    
    $ pbtk

在其他Linux发行版系统中，我们可以直接运行下列命令完成工具的安装：

    
    
    $ sudo apt install python3-pip git openjdk-9-jre
    
    $ sudo pip3 install protobuf pyqt5 requests websocket-client
    
    $ git clone<https://github.com/marin-m/pbtk>
    
    $ cd pbtk
    
    $ ./gui.py

当然了，PBTK也支持在Windows平台杀昂使用，我们安装好依赖组件并运行GUI之后，工具将会提醒我们进行下一步操作，按提示操作即可。

命令行使用

GUI可以通过主脚本来启动：

    
    
    ./gui.py

下列脚本也可以单独进行使用，不需要通过GUI来启动：

    
    
    ./extractors/jar_extract.py [-h] input_file [output_dir]
    
    ./extractors/from_binary.py [-h] input_file [output_dir]
    
    ./extractors/web_extract.py [-h] input_url [output_dir]

## 常规工作流

假设我们需要对一款Android应用程序进行逆向分析，我们可以先选择一个我们熟悉的反编译工具，然后按常规方式并通过HTTP向目标以POST数据的形式发送Protobuf格式内容。

打开PBTK，我们将会看到下图所示界面：

![](https://image.3001.net/images/20191218/1576635667_5df98d13972b7.png!small)

第一步就是将.protos文件转换为text格式，如果目标为Android应用，我们可以打开一个APK文件，然后剩下的就交给PBTK吧！

完成之后，在命令行编辑器中切换到“~/.pbtk/protos/<your APK name>”路径下，该App的.protos文件都在这个路径下。

回到我们的反编译工具，我们可以将感兴趣的数据通过HTTPS来向目标节点进行发送，并通过调用由生成的代码构成的类来序列化Protobuf消息。

![](https://image.3001.net/images/20191218/1576635683_5df98d232e633.png!small)

后面这个类应该可以直接对应到我们.protos目录中的某一个结构，比如说com.foo.bar.a.b将对应com/foo/bar/a/b.proto。那么接下来，我们选择需要作为输入的.proto文件，然后填写一些相关的节点信息：

![](https://image.3001.net/images/20191218/1576635688_5df98d28cc462.png!small)

我们还可以提供一些样本原始的Protobuf数据并发送至目标节点，相关数据可以通过mitmproxy或Wireshark捕获，或以十六进制编码的形式粘贴进去。

第三步，点击按钮，看看奇迹如何发生！工具将生成一个表示Protobuf结构的树形图（重复的字段以“+”作为后缀，必需的字段没有复选框）：

![](https://image.3001.net/images/20191218/1576635693_5df98d2d90921.png!small)

只需在一个区域上鼠标悬停即可获得焦点，如果字段是整数类型，请使用鼠标滚轮将其递增/递减，悬停时也会显示枚举信息。

## 本地数据存储

PBTK会将提取出的.proto信息存储至“~/.pbtk/protos/”（Linux）或“%APPDATA%\pbtk\protos”（Windows）路径下。基于HTTP节点的数据存储以JSON对象形式在“~/.pbtk/endpoints/”：

    
    
    [{
    
    "request": {
    
    "transport": "pburl",
    
    "proto": "[www.google.com/VectorTown.proto](http://www.google.com/VectorTown.proto)",
    
    "url": "<https://www.google.com/VectorTown>",
    
    "pb_param": "pb",
    
    "samples": [{
    
    "pb": "!....",
    
    "hl": "fr"
    
    }]
    
    },
    
    "response": {
    
    "format": "other"
    
    }
    
    }]

## 项目地址

> PBTK：【[ _GitHub传送门_](https://github.com/marin-m/pbtk)】

 *** 参考来源：[ _marin-m_](https://github.com/marin-m/pbtk)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


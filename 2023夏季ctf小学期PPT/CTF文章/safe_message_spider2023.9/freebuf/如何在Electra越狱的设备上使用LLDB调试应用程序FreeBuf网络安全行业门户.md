**![title.jpg](https://image.3001.net/images/20180529/15275482581593.jpg!small)**

**在3月18日的时候，我就曾发表过一篇关于在Electra越狱的设备上使用LLDB调试应用程序的文章。本文我将在此基础上，做进一步的更新优化。**

我试图在google搜索，有关使用[Electra](https://coolstar.org/electra/)越狱的iOS设备上调试AppStore应用程序的简要说明。但令我失望的是，竟然没有找到任何有用的资料。因此我决定写一篇相关的指南，经过我的测试它非常的适用于我，但我无法确定它是否同样适用于你。我在以下设备进行了测试：

运行iOS 11.1.2的iPhone 7

运行iOS 11.0.1的iPhone 5s

这两款设备都使用Electra jailbreak 1.0.4进行了越狱。

##  **从Xcode将** debugserver **部署到你的设备**

首先，通过ssh连接到你的iOS设备，查看/Developer/usr/bin/debugserver是否存在。如果不存在则，

> 在Mac上运行Xcode
>
> 为iOS打开ObjC项目（或从头创建一个新项目）
>
> 保持Xcode运行状态。将你的iOS设备连接到USB

接着在Xcode中你应该看到，如下红框内所示的信息：

![preparing_debug.png](https://image.3001.net/images/20180529/15275482894171.png!small)

等到“准备调试支持iPhone”完成。然后在设备上检查
/Developer/usr/bin/debugserver。此时，debugserver二进制文件应该已经存在。

## 通过USB进行调试

对我而言，它只在我通过USB进行调试时才有效。如果Mac上未安装iproxy，请通过brew进行安装：

    
    
    $ brew install usbmuxd

然后在Mac控制台中运行：

    
    
    $ iproxy 6666 6666 &
    $ iproxy 2222 22 &

最后，将iPhone连接到USB。就是这样，我们准备开始。

## 将LLDB attach到已经运行的进程

在你的Mac控制台上，连接iPhone：

    
    
    $ ssh -p 2222 root@localhost

在iPhone的控制台中运行

    
    
    # ps ax

找到你想要attach的进程的pid。然后运行

    
    
    # /electra/jailbreakd_client <the pid> 1
    # /Developer/usr/bin/debugserver localhost:6666 -a <the pid>

如果你看到和我类似的内容

    
    
    debugserver-@(#)PROGRAM:debugserver  PROJECT:debugserver-360.0.26.14
     for arm64.
    Attaching to process 1418...
    Listening to port 6666 for a connection from localhost...

则表明运行一切正常。现在，在Mac上打开另一个控制台，然后运行

    
    
    $ lldb

在LLDB控制台中运行

    
    
    (lldb) platform select remote-ios
    (lldb) process connect connect://localhost:6666

## 在LLDB下运行应用程序

在你的Mac控制台上，连接iPhone：

    
    
    $ ssh -p 2222 root@localhost

在iPhone的控制台中运行

    
    
    # /Developer/usr/bin/debugserver localhost:6666 -x backboard /var/containers/Bundle/Application/<path to the app binary>

如果你看到和我类似的内容

    
    
    debugserver-@(#)PROGRAM:debugserver  PROJECT:debugserver-360.0.26.14
     for arm64.
    Listening to port 6666 for a connection from localhost...

则表明运行一切正常。现在，在Mac上打开另一个控制台，然后运行

    
    
    $ lldb

在LLDB控制台中运行

    
    
    (lldb) platform select remote-ios
    (lldb) process connect connect://localhost:6666

重要提示！如果你遇到了错误，请尝试：

> 在没有调试器的情况下运行应用程序
>
> 如前一节所述，将调试器attach到应用程序
>
> 关闭（LLDB）应用程序
>
> 在调试器下再次运行应用程序

 ***参考来源：[kov4l3nko](https://kov4l3nko.github.io/blog/2018-05-25-my-experience-with-lldb-and-electra-jb/#deploying-debugserver-from-xcode-to-your-device)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  


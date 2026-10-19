**注意：本文中分析使用的app并非我个人所有。因此，为了保护所有者的隐私我已将包含在其中的识别信息全部去除。**

 **本文我将为大家演示，如何在运行时使用cycript从app中提取信息，并允许攻击访问app的PIN。**

 **该bug是在运行iOS 10.2的越狱iPhone 5s上发现的。请注意，早期或更高版本的iOS可能与此处使用的工具不兼容。**

## 1) Clutch

我们将使用'Clutch 2'（公共iOS解密工具）来解密和提取应用程序的.ipa文件，我们稍后需要转储并检查应用程序类的Objective-C头文件。

Clutch可以在这里下载到：<https://github.com/KJCracks/Clutch>

请按照安装说明在你的设备上安装Clutch。

如果你运行Clutch2时返回了“Permission Denied”错误，则可能是由于你没有赋予文件正确的读写执行权限。你可以执行以下命令尝试解决：

    
    
    $ chmod a+x /usr/bin/Clutch2
    

然后运行命令：

    
    
    $ Clutch2 -i
    

你将看到已安装应用程序列表。选择你要使用的应用并复制它的bundleID值运行以下命令：

    
    
    $ Clutch2 –b <BundleID>
    

这时你应该会看到一条消息告诉你，破解的二进制文件已被转储以及被保存的路径位置。

接着，你需要将二进制文件传输到Mac上进行分析。你可以通过多种方式实现这一点，但我更喜欢使用CyberDuck。你可以使用任何自己喜欢的文件传输软件，或者ssh到你的手机，并scp
.ipa文件到你计算机上即可。

获取.ipa文件后，你只需解压缩文件即可访问其中的内容。（注：在执行此操作之前，你可能需要先手动将文件类型更改为.zip）。

## 2) class-dump

下一步我们将使用名为class-dump的工具，转储应用程序的运行时头文件。你可以通过brew在你的计算机上安装这个工具：

    
    
    $ brew install class-dump
    

首先，我们找到应用程序的可执行文件。你可以在.ipa文件夹中找到此文件，路径位置为/Payload/.app/AppName。

运行：

    
    
    $ class-dump /Payload/<AppName>.app/AppName > dumpedHeaders
    

其中的'dumpedHeaders'是你将要创建转储的文件。

现在，你应该能够在任何文本编辑器（例如Sublime）中查看“dumpedHeaders”。我们打开文件并在其中搜索一些关键字，我首先搜索了'authorize'，'login'或'pin'这几个关键字，并很快定位到了我要查找的内容。

![Screen-Shot-2018-06-26-at-8.18.05-AM.png](https://image.3001.net/images/20180712/15313497873031.png!small)

可以看到在DTPinLockController类中，有一个NSString *pin属性。我们继续下一步。

## 3) cycript

首先，将最新版本的cycript下载至你的计算机上：<http://www.cycript.org/>

然后，通过文件传输软件（如CyberDuck，sftp，scp或任何你喜欢的工具）将cycript传送到你的设备上。

最后，ssh到你的设备并运行如下命令安装cycript：

    
    
    $ dpkg -i cycript.deb
    

现在你可以尝试运行cycript，并确认#cy提示符是否出现。（请确保在下一步操作之前退出cycript）。

现在我们已准备好hook我们的目标app。想要查找进程ID，请确保该app已在你的手机设备上正确运行：

    
    
    $ ps aux
    

复制你目标app的PID并运行：

    
    
    $ cycript -p <PID>
    

现在你已成功hook到了该进程，并且可以在其运行时探索该应用程序。

由于该app需要输入PIN码，此时我的应用程序已在手机上打开并跳转到了PIN码输入界面，如下：

![Screen-Shot-2018-06-26-at-8.35.49-AM.png](https://image.3001.net/images/20180712/15313498121890.png!small)

为了确认我看到的ViewController名称，我在cycript中运行：

    
    
    cy# UIApp.keyWindow.rootViewController
    

结果返回：

    
    
    DTPinLockController
    

现在，回顾我的class-dump可以看到，这确实是我之前发现'pin'
NSString属性的界面，因此我应该能够在运行时访问它的值。查看PIN是否非安全存储运行：

    
    
    cy# UIApp.keyWindow.rootViewController.pin
    

Bingo!在运行时我们成功获取到了PIN码：

![pic_2.png](https://image.3001.net/images/20180712/15313498336632.png!small)

现在我们可以在app上输入获取的PIN码来进行确认，我成功获取到了应用的访问权限！

 ***参考来源：[allysonomalley](https://www.allysonomalley.com/2018/06/26/bypassing-apps-pin-protection-with-cycript/)， FB小编 secist 编译，转载请注明来自FreeBuf.COM**


![](https://image.3001.net/images/20200211/1581435862_5e42cbd6013f3.jpg!small)

**Fugu是目前第一款开源的针对Checkm8漏洞的越狱工具。**

##  支持的设备

当前版本的Fugu仅支持iPad Pro（2017）和iPhone 7（iOS 13-13.3.1）。

##  项目获取

广大研究人员可以使用下列命令将项目代码克隆至本地：

    
    
    git clone https://github.com/LinusHenze/Fugu.git

##  项目构建

注意：广大研究人员也可以直接从本项目的【[Release页面](https://github.com/LinusHenze/Fugu/releases)】下载Fugu的预编译版本。

在构建Fugu之前，请确保已安装好了Xcode以及Homebrew。

然后使用Homebrew来安装llvm和binutils：

    
    
    brew install llvm binutils

接下来，在Xcode中打开Fugu项目，选择Fugu作为目标并进行项目构建。构建完成后，Xcode将在构建目录中生成Fugu项目以及一个Shellcode目录，然后我们就可以开始使用Fugu了。

##  工具使用

我建议大家以无参数的形式运行Fugu，并查看所有的可用选项。

如果你想要对你的苹果设备进行越狱操作，可以直接运行下列命令：

    
    
    Fugu iStrap

你可能需要多次运行该命令才可以成功启用Fugu，如果你尝试了四、五次都没成功的话，请调整设备进入DFU模式后再进行尝试。

该命令将会向你的苹果设备发送一个内核启动引导程序以及iDownload（一款能够用来向苹果设备发送文件或执行命令的程序）。

##  安装Sileo、SSH和MobileSubstrate

注意：越狱有风险，操作需谨慎，请备份好所有文件后再进行操作，如操作对设备造成的损坏，请用户自行承担。

确保你的设备上已经安装好了libusbmuxd，如果没有安装，你可以通过Homebrew并使用下列命令来安装libusbmuxd：

    
    
    brew install libusbmuxd

安装好usbmuxd之后，启动你的苹果设备并进入越狱模式。同时，确保你的设备已通过USB连接到了你的macOS设备上。

接下来，使用下列命令安装Sileo：

    
    
    python install_sileo.py

运行该脚本之后，将会下载所有安装Sileo所需的组件并完成Sileo的安装。安装完成之后，你将会在应用程序栏中看到Sileo的图标。此时，SSH将会在后台运行，请确保已经修改了root/mobile密码。

##  组件

###  Fugu由下列组件构成：

> 1、Fugu：macOS应用程序，可以通过checkm8漏洞来利用你苹果设备中的安全缺陷，并上传iStrap、iStrap加载器以及iDownload。
>
> 2、iStrap加载器：一段Shellcode代码，iBoot后会修复iBoot并加载iStrap。
>
> 3、iStrap：内核启动引导程序，会在苹果设备启动时显示，它会修复内核，注入启动参数并向内核注入Shellcode。
>
> 4、iDownload：运行在苹果设备上的程序，会在启动引导过程中完成安装。程序会监听端口1337，并且会给用户提供一个类似Bash的接口。

##  许可证协议

本项目的开发与发布（除第三方代码）遵循GPL v3开源许可证协议。

##  项目地址

> Fugu：【[GitHub传送门](https://github.com/LinusHenze/Fugu)】

***参考来源：[LinusHenze](https://github.com/LinusHenze/Fugu)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


![](https://image.3001.net/images/20200304/1583319884_5e5f8b4c9bdd4.jpg!small)

##  WiFi Passview

 **WiFi
Passview是一款基于Batch脚本实现的开源程序，它可以帮助我们在几秒钟之内轻松恢复WiFi密码。目前，该工具仅支持Windows操作系统。本质上来说，WiFi
Passview跟webpassview和mailpassview这样的密码查看器类似，但是这个脚本功能更加强大，运行速度更快，使用起来也更加方便。**

> 免责声明：WiFi Passview仅为测试目的使用，请不要将其用于恶意用途。

##  工具运行机制

从本质上来说，WiFi Passview可以算是WiFi密码管理器的Batch脚本实现方式，它可以帮助我们使用命令行工具来查看WiFi密码，这就是WiFi
Passview的运行机制：

    
    
    netsh wlan show profiles

当你在使用该工具时，只需几秒钟，你就可以轻松从目标设备上提取出存储在其中的WiFi密码。

##  功能介绍

当前版本的WiFi Passview提供了以下几种功能：

> 1、仅需几秒钟时间，便可提取存储在目标设备中所有可用/有效的WiFi密码；
>
> 2、提取指定目标SSID的WiFi密码；
>
> 3、存储提取到的密码；
>
> 4、添加额外选项；
>
> 5、无需人工读取关键内容，该工具可以帮助我们整理并输出；
>
> 6、无需管理员权限即可运行该工具；
>
> 7、独立的Batch脚本程序；
>
> 8、高度可定制；

##  工具使用

首先，各位研究人员需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/WarenGonzaga/wifi-passview.git

接下来，找到项目目录中的"wifi-passview-vX.X.X.bat"文件，然后使用Batch文件的运行方式来执行*.bat文件，而且无需使用到管理员权限。

###  工具运行截图

下面给出的是WiFi Passview的运行截图：

![](https://image.3001.net/images/20200304/1583319932_5e5f8b7c1e3ca.png!small)

##  自定义/个性化定制/开发

首先，还是需要使用本文给出的方式将项目下载到本地设备上。接下来，在命令行中切换到项目根目录，然后运行下列命令：

    
    
    npm install
    
        npm install gulp-cli -g && npm install gulp -D

接下来，根据我们自己的需求来修改“./src/config.json”文件。定制修改完成之后，需要使用下列命令来启动项目的构建进程：

    
    
    gulp build

如果你想要重置构建进程，可以直接使用下列命令：

    
    
    gulp cleandev

如果你编辑了“./src/core.bat”文件，你可以使用“gulp test”，并结合“gulp build”和“gulp
cleandev”来快速检查定制工具的质量情况。

当然了，你还可以使用下列命令来查看所有可用的“gulp”命令：

    
    
    gulp --tasks

##  许可证协议

> WiFi Passview的开发与发布遵循[MIT开源许可证协议](https://opensource.org/licenses/MIT)。

##  项目地址

> WiFi Passview：【[GitHub传送门](https://github.com/WarenGonzaga/wifi-passview)】

 *** 参考来源：[WarenGonzaga](https://github.com/WarenGonzaga/wifi-passview)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


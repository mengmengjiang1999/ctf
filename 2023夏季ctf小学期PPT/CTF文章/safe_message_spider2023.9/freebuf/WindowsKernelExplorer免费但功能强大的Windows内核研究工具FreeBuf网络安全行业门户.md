## 介绍

 **Windows Kernel Explorer（你可以称其为“WKE”）是一款免费但功能强大的Windows内核研究工具。它支持从Windows
XP到Windows
10的所有32位和64位版本。跟类似WIN64AST和PCHunter这样的热门工具相比，WKE的可自定义程度更高，而且还可以在不需要升级代码文件的情况下直接在最新版本的Windows
10上运行。**

### WKE工具获取

下载地址：【[GitHub传送门](https://github.com/AxtMueller/Windows-Kernel-Explorer)】

代码克隆命令：

    
    
    git clone https://github.com/AxtMueller/Windows-Kernel-Explorer.git

## 为何WKE可以直接在最新版本Windows 10上运行？

如果当前系统环境缺少组件的话，WKE将会自动下载所需的符号文件，下载安装完成之后，WKE中90%的功能都可以正常使用了。如果符号文件里面没有所需数据的话，WKE将会尝试从DAT文件中获取（所以新版Windows
10发布之后，我会上传最新的DAT文件到GitHub）。如果没有联网的话，WKE只有50%的功能可用。

## 如何自定义WKE

你可以通过编辑配置文件来对WKE进行定制开发。目前，你可以设置设备名称和驱动器的符号链接名称，以及过滤器属性。除此之外，你还可以启用内核模式和用户模式特征随机化来躲避恶意软件的检测。如果你重命名了WKE的EXE文件，你还需要同时重命名SYS/DAT/INI文件的文件名。

### 主要功能

> 1、 进程管理（模块、线程、内存、窗口和窗口Hook等等）；
>
> 2、 文件管理；
>
> 3、 注册表管理；
>
> 4、 内核模式调用，过滤器，计时器、NDIS块和WFP功能管理；
>
> 5、 内核模式钩子扫描（MSR、EAT、IAT、SSDT、SSSDT、IDT、IRP、OBJECT）；
>
> 6、 用户模式钩子扫描（内核调用表、EAT、IAT）；
>
> 7、 内存编辑器和符号解析器；
>
> 8、 保护进程、隐藏/保护/重定向文件或目录，保护注册表；
>
> 9、 驱动、进程和进程模块路径修改；
>
> 10、启用/禁用某些Windows组件；

## 工具运行截图

WindowsXP 32位：

![Windows-Kernel-Explorer](https://image.3001.net/images/20190121/1548086061_5c45eb2da7fb9.png!small)

WindowsXP 64位：

![Windows-Kernel-Explorer](https://image.3001.net/images/20190121/1548086072_5c45eb380b228.png!small)

Windows10 32位：

![Windows-Kernel-Explorer](https://image.3001.net/images/20190121/1548086161_5c45eb91279d7.png!small)

Windows10 64位：

![Windows-Kernel-Explorer](https://image.3001.net/images/20190121/1548086172_5c45eb9cbb4ca.png!small)

主菜单：

![Windows-Kernel-Explorer](https://image.3001.net/images/20190121/1548086184_5c45eba820e4f.png!small)

模块路径修改：

![Windows-Kernel-Explorer](https://image.3001.net/images/20190121/1548086194_5c45ebb2ddf76.png!small)

内存编辑器（打印结构体）：

![Windows-Kernel-Explorer](https://image.3001.net/images/20190121/1548086208_5c45ebc084a9d.png!small)

内存编辑器（反编译函数）

![Windows-Kernel-Explorer](https://image.3001.net/images/20190121/1548086220_5c45ebcc2c155.png!small)

 *** 参考来源：[AxtMueller](https://github.com/AxtMueller/Windows-Kernel-Explorer)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


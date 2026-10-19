![](https://image.3001.net/images/20200310/1583848251_5e679b3b133f8.png!small)

##  Projectsandcastle

 **Projectsandcastle是一款针对iPhone的Android/Linux支持工具，该工具可以给广大研究人员提供以下实用工具:**

> 1、loader/ 通过pongoOS加载内核和设备树
>
> 2、syscfg/ 可从目标设备的syscfg分区中提取配置信息
>
> 3、hx-touchd/ 触摸屏幕支持守护进程
>
> 4、hcdpack/ 可从源码文件中提取蓝牙固件信息

###  内核

内核可以从下列GitHub库中获取到稳定版本（linux-stable）：

> <https://github.com/corellium/linux-sandcastle>

###  Buildroot

Projectsandcastle的Linux Ramdisk使用了buildroot来进行构建，我们提供的定制版本buildroot可以从下列地址获取：

> <https://github.com/corellium/sandcastle-buildroot>

Buildroot是一款简单、高效且易于使用的工具，它可以帮助我们通过交叉编译来生成一个嵌入式的Linux系统。

相关操作文档可以在上述地址中的docs/manual文件中找到，你可以使用命令“make manual-text”来生成一个文本文档，或读取output/docs/manual/manual.text文件。

我们可以按照下列方式来构建和使用buildroot工具：

> 1、运行命令“make menuconfig”；
>
> 2、选择目标架构，以及需要编译的代码包；
>
> 3、运行“make”命令；
>
> 4、等待编译完成；
>
> 5、在output/images目录中找到内核、bootloader、root文件系统等内容；

在线文档：【[点我查看](http://buildroot.org/docs.html)】

##  Android应用程序

###  安装APK文件

广大研究人员可以使用下列命令安装APK文件：

    
    
    adb install foo.apk

但是，这种方式会存在以下限制因素：

> 1、如果是纯Java APK文件，并且不需要该项目所不支持的硬件的话，则可以正常运行；
>
> 2、仅包含了ARMv7代码（32位）的APK文件将无法运行；
>
> 3、包含了ARMv8代码（64位）的APK文件将需要对代码进行重构后方可运行；

###  重构代码库

我们需要将代码库文件按照16KB页面大小来构建，首先，当代码库链接成功时，尝试运行下列选项/命令：

    
    
    -z common-page-size=0x4000 -z max-page-size=0x4000

如果连接器使用了C编译器来封装，那你可能还需要使用下列参数：

    
    
    -Wl,-z,common-page-size=0x4000 -Wl,-z,max-page-size=0x4000

如果一切正常的话，可以使用“readelf -l”：

如果没有RELRO段，请检查具有不同属性的LOAD段是否占用了同一个16KB页；

如果有RELRO段，请确保它在16kB页边界上开始或结束；有时编译器会将RELRO放在RW段的开始处（然后RELRO应该在16k边界处结束），有时会将其放在末尾（然后RELRO应该在16k边界处开始）。

如果还存在问题的话，请检查代码库的源代码，并检查PAGE_SIZE、kPageSize、PAGE_SHIFT、PAGE_BITS等位置。

##  项目地址

>
> Projectsandcastle：【[GitHub传送门](https://github.com/corellium/projectsandcastle)】

 ***
参考来源：[corellium](https://github.com/corellium/projectsandcastle)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


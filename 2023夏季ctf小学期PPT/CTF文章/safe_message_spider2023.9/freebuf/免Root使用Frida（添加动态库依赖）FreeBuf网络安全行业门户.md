在
[非ROOT环境下使用Frida及调试](https://mp.weixin.qq.com/s?__biz=MzI1NjEyMzgxMw==&mid=2247484635&idx=1&sn=563c8637a5b124c4e997805a36586fab&chksm=ea2a3211dd5dbb0779097a12891917bdeb7753ba26c37e3d9ca9ab786cabd00ca2df03dae498&token=1057249047&lang=zh_CN#rd)中通过修改smail代码实现在非ROOT的情况下使用Frida。前面提到这种方式有一个明显的缺点就是要修改smali源代码。这篇文章主要来说怎样在不修改源代码的情况下在非ROOT情况下使用Frida。

### Frida-gadget

Frida的Gadget是一个共享库，可以在不适合Injected操作模式的情况下由要检测的程序加载。

这可以通过多种方式完成, 例如:

  * 修改程序的源代码
  * 修补它或其一个库，例如 通过使用诸如insert_dylib之类的工具
  * 使用动态链接器功能，例如LDPRELOAD或DYLDINSERT_LIBRARIES

动态链接程序执行其构造函数后，就会立即启动Gadget。根据您的用例，它支持三种不同的交互，其中“Listen”交互是默认的.
您可以通过添加配置文件来覆盖它。 该文件的名称应与Gadget二进制文件完全相同，但文件扩展名为.config。
因此，例如，如果您命名二进制文件FridaGadget.dylib，则将命名配置文件FridaGadget.config。

请注意，您可以随意命名Gadget二进制文件，这对于回避寻找名称为“ Frida”的已加载库的反Frida检测方案很有用。

具体可参见https://frida.re/docs/gadget/#scriptdirectory。

### 动态链接库的加载

可执行文件格式包含了链接在可执行文件上的库。我们可以使用ldd或readelf(Unix)列出这些库。

如果想查看ls依赖的动态库，则可以使用`readelf-d/bin/ls|grep-i NEEDED`。
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)当可执行文件载入的时候，载入器会遍历这些库，并把它们映射到进程到的内存空间中去，并在加载之后调用它的构造方法。

这一想法的原理是添加frida-agent.so作为APK的native库的依赖。而这里使用的工具是lief来实现这个功能。

### LIEF

#### 目的

The purpose of this project is to provide a cross platform library which can
parse, modify and abstract ELF, PE, MachO and Android formats

#### 架构

![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

#### 使用

##### 查看导入表

    
    
    import lief
    
    libnative = lief.parse("/usr/bin/ls")
    # libnative.add_library("libfrida-gadget.so") # Injection!
    imported_function = libnative.imported_functions
    for index, item in enumerate(imported_function):
      print(index, item)

运行结果如下：
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

##### 遍历Section

    
    
    import lief
    
    libnative = lief.parse("/usr/bin/ls")
    # libnative.add_library("libfrida-gadget.so") # Injection!
    for section in libnative.sections:
      print(section.name) # section's name
      print(section.size) # section's size
      print(len(section.content)) # Should match the previous print

运行结果如下：
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

##### ELF格式

首先，ELF文件格式提供了两种视图，分别是链接视图和执行视图。

![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)链接视图是以节（section）为单位，执行视图是以段（segment）为单位。链接视图就是在链接时用到的视图，而执行视图则是在执行时用到的视图。上图左侧的视角是从链接来看的，右侧的视角是执行来看的。

>   * ELF header： 描述整个文件的组织。
>   * Program Header Table: 描述文件中的各种segments，用来告诉系统如何创建进程映像的。
>   * sections 或者
> segments：segments是从运行的角度来描述elf文件，sections是从链接的角度来描述elf文件，也就是说，在链接阶段，我们可以忽略program
> header table来处理此文件，在运行阶段可以忽略section header table来处理此程序（所以很多加固手段删除了section
> header table）。从图中我们也可以看出，segments与sections是包含的关系，一个segment包含若干个section。
>   * Section Header Table: 包含了文件各个section的属性信息。
>

![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)可以通过执行命令`readelf-S/bin/ls`来查看该可执行文件中有哪些section。
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)通过执行命令`readelf
--segments/bin/ls`，可以查看该文件的执行视图。
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)从上面两个图中可以看出，segment是section的一个集和，sections按照一定规则映射到segment。那么为什么需要区分两种不同视图？

>
> 当ELF文件被加载到内存中后，系统会将多个具有相同权限（flg值）section合并一个segment。操作系统往往以页为基本单位来管理内存分配，一般页的大小为4096B，即4KB的大小。同时，内存的权限管理的粒度也是以页为单位，页内的内存是具有同样的权限等属性，并且操作系统对内存的管理往往追求高效和高利用率这样的目标。ELF文件在被映射时，是以系统的页长度为单位的，那么每个section在映射时的长度都是系统页长度的整数倍，如果section的长度不是其整数倍，则导致多余部分也将占用一个页。而我们从上面的例子中知道，一个ELF文件具有很多的section，那么会导致内存浪费严重。这样可以减少页面内部的碎片，节省了空间，显著提高内存利用率。
> 需要注意地是：尽管图中显示的各个组成部分是有顺序的，实际上除了 ELF 头部表以外，其他节区和段都没有规定的顺序

#### 常用API

  1. write(self: lief.ELF.Binary, output: str) → None Rebuild the binary and write it in a file

  2. lief.ELF.parse(args, *kwargs)

Overloaded function.

  * parse(filename: str, dynsymcountmethod: lief.ELF.DYNSYMCOUNTMETHODS = ) -> LIEF::ELF::Binary Parse the given binary and return a Binary object For weird binaries (e.g sectionless) you can choose the method to use to count dynamic symbols (DYNSYMCOUNTMETHODS)

  * parse(raw: List[int], name: str = ‘’, dynsymcountmethod: lief.ELF.DYNSYMCOUNTMETHODS = ) -> LIEF::ELF::Binary Parse the given binary and return a Binary object For weird binaries (e.g sectionless) you can choose the method to use to count dynamic symbols (DYNSYMCOUNTMETHODS)

    * parse(io: object, name: str = ‘’) -> LIEF::ELF::Binary

  1. addlibrary(self: lief.ELF.Binary, libraryname: str) → LIEF::ELF::DynamicEntryLibrary Add a library with the given name as dependency

更多API，可参见https://lief.quarkslab.com/doc/latest/api/python/elf.html。

### 为Frida-gadget添加依赖

通过上面的介绍，可知通过add_library可以为指定的库添加依赖。

通过分析代码可知libgame.so在MainGameActivity的onCreate方法中进行加载，因此选择为libgame.so添加Frida-gadget依赖。

这里将frida-gadget对应的so命名为libgadget.so。
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)python具体实现和效果参见下图:
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

### 交互方式

本篇文章基于的apk依然是领跑娱乐.apk。

#### Listen

默认的方式，添加依赖之后，打包签名安装，具体操作可参见[非ROOT环境下使用Frida及调试](http://blog.didispace.com/tools/online-markdown/%E9%9D%9EROOT%E7%8E%AF%E5%A2%83%E4%B8%8B%E4%BD%BF%E7%94%A8Frida%E5%8F%8A%E8%B0%83%E8%AF%95%5D%28https://mp.weixin.qq.com/s?__biz=MzI1NjEyMzgxMw==&mid=2247484635&idx=1&sn=563c8637a5b124c4e997805a36586fab&chksm=ea2a3211dd5dbb0779097a12891917bdeb7753ba26c37e3d9ca9ab786cabd00ca2df03dae498&token=1057249047&lang=zh_CN#rd%29)。

这种交互方式也可以使用objection相关操作。

#### 脚本方式

在lib/ABI目录新建配置文件libgadget.config，内容如下：

    
    
    {
      "interaction": {
        "type": "script",
        "path": "/data/local/tmp/myscript.js",
        "on_change": "reload"
      }
    }
    

使用配置配置文件必须遵循两个条件：

  * 文件必须和gadget库同名（例如：libgadget.so 和 libgadget.conf）
  * 配置文件必须和gadget库位于同一目录中

第二个要求也就意味着在设备中安装之后，gadget库会会在/data/app/com.lingpao.lpcf622b/lib目录中寻找配置文件。

在安装app之后，当满足下述条件时，Android包管理器会从APK的lib/目录中复制文件：

  * 名字具有lib前缀
  * 名字具有.so后缀
  * 名字是gdbserver

Frida 实现这些要求的源码如下。因此我们只需要给 **libgadget.config添加.so后缀就行了** 。

    
    
    #if ANDROID
      if (!FileUtils.test (config_path, FileTest.EXISTS)) {
        var ext_index = config_path.last_index_of_char ('.');
          if (ext_index != -1) {
            config_path = config_path[0:ext_index] + ".config.so";
          } else {
            config_path = config_path + ".config.so";
          }
      }
    #endif

最终的目录结构如下:
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

##### hook脚本

myscript.js的内容如下:

    
    
    'use strict';
    
    console.log("Waiting for Java..");
    
    Java.perform(function () {
      var Log = Java.use("android.util.Log");
      Log.v("frida-lief", "Have fun!");
    });

##### 运行

重新打包签名安装 然后把脚本推送到配置文件写的目录下面。

    
    
    $ adb push myscript.js /data/local/tmp
    $ adb shell chmod 777 /data/local/tmp/myscript.js

查看是否成功: adb logcat -s "frida-lief:V"

    
    
    --------- beginning of system
    --------- beginning of crash
    --------- beginning of main
    11-14 19:18:18.745 13891 14005 V frida-lief: Have fun!

### 写在最后

优点：

  * 不需要root
  * 不依赖frida-server
  * 可用于绕过anti-frida
  * 不需要修改AndroidManifest.xml和DEX文件

缺点：

  * 需要向APK里添加文件
  * 需要程序有至少一个native库
  * 注入进去的库的加载顺序不能控制

### 公众号

更多Frida相关内容，欢迎关注我的微信公众号:无情剑客。
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

  


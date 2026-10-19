## Vdex Extractor

 **一款命令行工具，用于从Vdex文件反编译和提取Android Dex字节码的工具。**

## 编译

> 克隆此存储库
>
> 如果要为Android设备进行交叉编译，请安装Android NDK
>
> make.sh使用所需的构建目标调用bash脚本`$ ./make.sh`\- 如果CC未从env定义，则默认使用gcc`$ ./make.sh
> gcc` \- 用gcc编译`$ ./make.sh clang` \- 用clang编译`$ ./make.sh cross-android` \-> 使用NDK交叉编译（armeabi-v7a，arm64-v8a，x86和x86_64）可执行文件复制到bin目录下,对于调试版本使用`$
> DEBUG=true ./make.sh`

## 依赖关系

主机系统中应安装以下外部库:

### zlib

macos：`brew install zlib-devel`带macports的macOS： `port install zlib`Linux： `apt
install libz-dev`其他Linux / Unix系统：检查可用的包管理器或从源代码编译使用cygwin的Windows：zlib-devel从cygwin安装程序安装

## 用法

    
    
    $ bin/vdexExtractor -h
                  vdexExtractor ver. 0.5.2
        Anestis Bechtsoudis 
      Copyright 2017 - 2018 by CENSUS S.A. All Rights Reserved.
     -i, --input=   : 输入目录(递归搜索)或单个文件
     -o, --output=  : 输出路径(默认与输入相同)
     -f, --file-override  : 如果文件已经存在允许覆盖(默认:false)
     --no-unquicken       : 禁用unquicken字节码反编译器 (don't de-odex)
     --deps               : 转储经过验证的依赖信息
     --dis                : 启用字节码反汇编器
     --ignore-crc-error   : 反编译Dex 忽略CRC错误
     --new-crc=     : 提取Apk或Dex文件位置校验和文本文件
     --get-api             : 基于Vdex版本获取Android API级别 
     -v, --debug=LEVEL    : 日志级别 默认: '3' (INFO)
     -l, --log-file=: 保存反汇编器或验证依赖项输出到日志文件
     -h, --help           : 帮助信息
    

## 字节码Unquickening解码器

Vdex文件包含所有quick_info数据(旧vtable)，用于恢复字节码优化过程中应用的dexto
-dex转换。这里是创建一个能够快速恢复优化字节码的独立工具，不需要从AOSP构建整个libart。Vdex完全unquicken功能也作为AOSP
oatdump
libart工具的一部分实现。可在[此处](a%20href=)获得。如果你想在Oreo版本中使用oatdump，你可以在[这里](a%20href=)使用相应的补丁，或者在[oatdump
++](a%20href=)工具的fork和build（内部和AOSP_SRC_ROOT工作空间）中使用oreo-release分支。谷歌已经发布了提供的补丁以及ART运行时的Android Pie版本。

## 验证迭代器的依赖关系

当第一次编译(优化)Dex字节码文件时，dex2oat将执行验证依赖项收集器，作为方法学验证者的一部分。验证依赖项收集器类用于记录解析结果和类路径中定义的类/方法/字段的类型可赋值测试。编译驱动程序初始化类并注册正在编译的所有Dex文件。在这个集合之外的Dex文件中定义的类(或者没有关联的Dex文件的合成类)被认为在类路径中。所有记录的依赖关系都存储在生成的Vdex文件中，以及来自OatWriter类的相应Oat文件。vdexExtractor工具集成了一个Vdex依赖项walker函数，该函数能够迭代所有依赖项信息并以人类可读的格式转储它们。以下代码段演示了示例Vdex文件的依赖项转储示例。

    
    
    $ bin/vdexExtractor -i /tmp/BasicDreams.vdex -o /tmp --deps -f
    [INFO] Processing 1 file(s) from /tmp/BasicDreams.vdex
    ------- Vdex Deps Info -------    dex file #0
     extra strings: number_of_strings=2
      0000: 'Ljava/lang/Thread;'
      0001: 'Ljava/lang/Throwable;'
     assignable type sets: number_of_sets=8
      0000: 'Landroid/service/dreams/DreamService;' must be assignable to 'Landroid/content/Context;'
      0001: 'Landroid/view/TextureView;' must be assignable to 'Landroid/view/View;'
      0002: 'Ljava/nio/FloatBuffer;' must be assignable to 'Ljava/nio/Buffer;'
    ...
     unassignable type sets: number_of_sets=0
     class dependencies: number_of_classes=34
      0000: 'Landroid/graphics/Color;' 'must' be resolved with access flags '1'
      0001: 'Landroid/graphics/SurfaceTexture;' 'must' be resolved with access flags '1'
    ...
      0024: 'Ljavax/microedition/khronos/egl/EGL10;' 'must' be resolved with access flags '513'
    ...
     field dependencies: number_of_fields=4
      0000: 'Ljavax/microedition/khronos/egl/EGL10;'->'EGL_DEFAULT_DISPLAY':'Ljava/lang/Object;' is expected to be in class 'Ljavax/microedition/khronos/egl/EGL10;' and have the access flags '9'
      0001: 'Ljavax/microedition/khronos/egl/EGL10;'->'EGL_NO_CONTEXT':'Ljavax/microedition/khronos/egl/EGLContext;' is expected to be in class 'Ljavax/microedition/khronos/egl/EGL10;' and have the access flags '9'
      0002: 'Ljavax/microedition/khronos/egl/EGL10;'->'EGL_NO_DISPLAY':'Ljavax/microedition/khronos/egl/EGLDisplay;' is expected to be in class 'Ljavax/microedition/khronos/egl/EGL10;' and have the access flags '9'
      0003: 'Ljavax/microedition/khronos/egl/EGL10;'->'EGL_NO_SURFACE':'Ljavax/microedition/khronos/egl/EGLSurface;' is expected to be in class 'Ljavax/microedition/khronos/egl/EGL10;' and have the access flags '9'
     method dependencies: number_of_methods=84
      0000: 'Landroid/graphics/Color;'->'HSVToColor':'([F)I' is expected to be in class 'Landroid/graphics/Color;', have the access flags '9
      0001: 'Landroid/opengl/GLES20;'->'glAttachShader':'(II)V' is expected to be in class 'Landroid/opengl/GLES20;', have the access flags '9
      0002: 'Landroid/opengl/GLES20;'->'glClear':'(I)V' is expected to be in class 'Landroid/opengl/GLES20;', have the access flags '9
    ...
     unverified classes: number_of_classes=0
    ----- EOF Vdex Deps Info -----    [INFO] 1 out of 1 Vdex files have been processed
    [INFO] 1 Dex files have been extracted in total
    [INFO] Extracted Dex files are available in '/tmp'
    

## 集成反汇编程序

为了调试反编译器并协助Dex字节码调查任务，实现了一个轻型反汇编程序。反汇编输出非常类似于platform/art项目的AOSP
dexdump2实用程序提供的输出。反汇编程序可以独立于unquickening反编译器使用。以下代码段中说明了示例输出。前缀的行[new]说明了位于该偏移量中的反编译指令（前一行）的输出。请注意，所有加速的偏移和vtable引用都已恢复为原始签名和原型。

    
    
    $ bin/vdexExtractor -i /tmp/Videos.vdex -o /tmp -f --dis -l /tmp/dis.log
    [INFO] Processing 1 file(s) from /tmp/Videos.vdex
    [INFO] 1 out of 1 Vdex files have been processed
    [INFO] 2 Dex files have been extracted in total
    [INFO] Extracted Dex files are available in '/tmp'
    $ head -90 /tmp/dis.log
    ------ Dex Header Info ------    magic        : dex-035
    checksum     : e14de163 (3779977571)
    signature    : 9a91f8e5f2afe2c6b5c2b4853832d3c5ed01aef8
    fileSize     : 8ca638 (9217592)
    headerSize   : 70 (112)
    endianTag    : 12345678 (305419896)
    linkSize     : 0 (0)
    linkOff      : 0 (0)
    mapOff       : 8ca568 (9217384)
    stringIdsSize: ef06 (61190)
    stringIdsOff : 70 (112)
    typeIdsSize  : 29f4 (10740)
    typeIdsOff   : 3bc88 (244872)
    protoIdsSize : 3df9 (15865)
    protoIdsOff  : 46458 (287832)
    fieldIdsSize : a79d (42909)
    fieldIdsOff  : 74c04 (478212)
    methodIdsSize: fed7 (65239)
    methodIdsOff : c88ec (821484)
    classDefsSize: 2288 (8840)
    classDefsOff : 147fa4 (1343396)
    dataSize     : 73d594 (7591316)
    dataOff      : 18d0a4 (1626276)
    -----------------------------    file #0: classDefsSize=8840
      class #0: a.a ('La$a;')
       access=0601 (PUBLIC INTERFACE ABSTRACT)
       source_file=SourceFile, class_data_off=851907 (8722695)
       static_fields=0, instance_fields=0, direct_methods=0, virtual_methods=2
       virtual_method #0: onMenuItemSelected (La;Landroid/view/MenuItem;)Z
        access=0401 (PUBLIC ABSTRACT)
        codeOff=0 (0)
       virtual_method #1: invokeItem (Landroid/support/v7/view/menu/MenuItemImpl;)Z
        access=0401 (PUBLIC ABSTRACT)
        codeOff=0 (0)
      class #1: a.b ('La$b;')
       access=0601 (PUBLIC INTERFACE ABSTRACT)
       source_file=SourceFile, class_data_off=851913 (8722707)
       static_fields=0, instance_fields=0, direct_methods=0, virtual_methods=1
       virtual_method #0: invokeItem (Landroid/support/v7/view/menu/MenuItemImpl;)Z
        access=0401 (PUBLIC ABSTRACT)
        codeOff=0 (0)
      class #2: SupportMenu ('Landroid/support/v4/internal/view/SupportMenu;')
       access=0601 (PUBLIC INTERFACE ABSTRACT)
       source_file=SourceFile, class_data_off=0 (0)
      class #3: a ('La;')
       access=0001 (PUBLIC)
       source_file=SourceFile, class_data_off=85191b (8722715)
       static_fields=1, instance_fields=25, direct_methods=12, virtual_methods=74
       direct_method #0: <clinit> ()V
        access=10008 (STATIC CONSTRUCTOR)
        codeOff=1abb50 (1751888)
        quickening_size=4 (4)
          1abb60: 1260                                   |0000: const/4 v0, #int 6 // #6
          1abb62: 2300 e426                              |0001: new-array v0, v0, [I // type@26e4
          1abb66: 2600 0700 0000                         |0003: fill-array-data v0, 0000000a // +00000000
          1abb6c: 6900 1900                              |0006: sput-object v0, La;.sCategoryToOrder:[I // field@0019
          1abb70: 7300                                   |0008: return-void-no-barrier
    [new] 1abb70: 0e00                                   |0008: return-void
          1abb72: 0000                                   |0009: nop // spacer
          1abb74: 0003 0400 0600 0000 0100 0000 0400 ... |000a: array-data (16 units)
       direct_method #1: invokeItem (Landroid/support/v7/view/menu/MenuItemImpl;)Z
        access=10001 (PUBLIC CONSTRUCTOR)
        codeOff=1abb94 (1751956)
        quickening_size=22 (34)
          1abba4: 1211                                   |0000: const/4 v1, #int 1 // #1
          1abba6: 1200                                   |0001: const/4 v0, #int 0 // #0
          1abba8: 7010 dbf9 0200                         |0002: invoke-direct {v2}, Ljava/lang/Object;.<init>:()V // method@f9db
          1abbae: e620 4000                              |0005: iput-quick v0, v2, [obj+0040]
    [new] 1abbae: 5920 0400                              |0005: iput v0, v2, La;.mDefaultShowAsAction:I // field@0004
          1abbb2: eb20 4a00                              |0007: iput-boolean-quick v0, v2, [obj+004a]
    [new] 1abbb2: 5c20 1200                              |0007: iput-boolean v0, v2, La;.mPreventDispatchingItemsChanged:Z // field@0012
          1abbb6: eb20 4700                              |0009: iput-boolean-quick v0, v2, [obj+0047]
    [new] 1abbb6: 5c20 0d00                              |0009: iput-boolean v0, v2, La;.mItemsChangedWhileDispatchPrevented:Z // field@000d
          1abbba: eb20 4d00                              |000b: iput-boolean-quick v0, v2, [obj+004d]
    [new] 1abbba: 5c20 1600                              |000b: iput-boolean v0, v2, La;.mStructureChangedWhileDispatchPrevented:Z // field@0016
          1abbbe: eb20 4800                              |000d: iput-boolean-quick v0, v2, [obj+0048]
    [new] 1abbbe: 5c20 0f00                              |000d: iput-boolean v0, v2, La;.mOptionalIconsVisible:Z // field@000f
          1abbc2: eb20 4500                              |000f: iput-boolean-quick v0, v2, [obj+0045]
    [new] 1abbc2: 5c20 0a00                              |000f: iput-boolean v0, v2, La;.mIsClosing:Z // field@000a
          1abbc6: 2200 fe25                              |0011: new-instance v0, Ljava/util/ArrayList; // type@25fe
          1abbca: 7010 6bfb 0000                         |0013: invoke-direct {v0}, Ljava/util/ArrayList;.<init>:()V // method@fb6b
          1abbd0: e820 3800                              |0016: iput-object-quick v0, v2, [obj+0038]
    [new] 1abbd0: 5b20 1700                              |0016: iput-object v0, v2, La;.mTempShortcutItemList:Ljava/util/ArrayList; // field@0017
          1abbd4: 2200 2c26                              |0018: new-instance v0, Ljava/util/concurrent/CopyOnWriteArrayList; // type@262c
          1abbd8: 7010 cdfc 0000                         |001a: invoke-direct {v0}, Ljava/util/concurrent/CopyOnWriteArrayList;.<init>:()V // method@fccd
          1abbde: e820 3000                              |001d: iput-object-quick v0, v2, [obj+0030]
    [new] 1abbde: 5b20 1100                              |001d: iput-object v0, v2, La;.mPresenters:Ljava/util/concurrent/CopyOnWriteArrayList; // field@0011
          1abbe2: e823 1000                              |001f: iput-object-quick v3, v2, [obj+0010]
    

## Dex转换器

Android 9（Pie）版本推出了一种新型的Dex文件，即Compact
Dex（Cdex）。Cdex是一种ART内部文件格式，它压缩各种Dex数据结构（例如方法头）并对多索引文件中的常见数据blob（例如字符串）进行重复数据删除。来自输入应用程序的Dex文件的重复数据删除数据存储在Vdex容器的共享部分中。

现在由于Vdex容器存储的是Cdex文件而不是标准的Dex，因此vdexExtractor后端（从版本019开始）已经更新并支持它们。但是，由于该工具未实现Dex
IR，因此无法在不使用外部工具的情况下将Cdex文件转换回标准Dex。为此，编写了`“compact_dex_converter”`工具，该工具使用来自AOSP
art repo的libdexlayout（Dex
IR）。该工具的源代码可在[此处](a%20href=)获得。编译工具需要分配必要的AOSP回购并构建为AOSP模块。为方便起见，vdexExtractor正在实现一个帮助工具（请参阅下一节中的“tools
/ deodex”），该工具下载一组预编译的二进制文件并包装所需的自动化。此外，可以从以下链接下载“compact_dex_converter”二进制文件：

### Linux x86-64

> 使用共享库：https：//1drv.ms/u/s !ArDC4mvMyPrRhEsiuPjOF_ssIfOe
>
> 使用共享库调试：https：//1drv.ms/u/s！ArDC4mvMyPrRhE3Z2jdBXJIhazjc
>
> 静态编译：https：//1drv.ms/u/s !ArDC4mvMyPrRhEq96XX-LsCACF2s
>
> 静态编译调试：https：//1drv.ms/u/s！ArDC4mvMyPrRhEwmwM8--zdhoCB2

### Linux x86-64旧CPU（没有SSE4.2和没有POPCNT ＃29）

> 使用共享库：https：//1drv.ms/u/s！ArDC4mvMyPrRhFP46IyBqOtihS9s
>
> 使用共享库调试：https：//1drv.ms/u/s！ArrDC4mvMyPrRhFXEGW9vrlMlTKDJ
>
> 静态编译：https：//1drv.ms/u/s！ArDC4mvMyPrRhFIFZCF9TtEHVooc
>
> 静态编译的调试：https：//1drv.ms/u/s！ArDC4mvMyPrRhFSMELB_H3w5Cdfe

### ARM64（aarch64）

> 使用共享库：https：//1drv.ms/u/s！ArDC4mvMyPrRhEindMOf3aWCbQRr
>
> 使用共享库调试：https：//1drv.ms/u/s！ArDC4mvMyPrRhEnU9Ei_3MeQipGr
>
> 静态编译：不支持

### 苹果系统

> 使用共享库：https：//1drv.ms/u/s！ArDC4mvMyPrRhE45gEUNolEiZ50u
>
> 使用共享库调试：https：//1drv.ms/u/s！ArDC4mvMyPrRhFG5WH_zNz0jNarZ
>
> 静态编译：不支持

二进制名称中的`'s'`后缀代表“静态编译”，而`“d”`代表`“debug”`构建。它们也可以组合在一起（例如`'ds'` \- 静态编译的调试版本）。

## 实用脚本

### extract-apps-from-device.sh

从连接的Android设备中提取安装包(用户和系统)的ART编译器输出资源(oat、ART、vdex)。还支持提取APK档案的安装包。由于应用了DAC权限，一些系统应用程序数据在没有根访问的情况下可能无法提取。

    
    
    $ scripts/extract-apps-from-device.sh -h
      Usage: extract-apps-from-device.sh [options]
        options:
          -o|--output <dir>  : Output directory to save extracted data (default is '.')
          -d|--device <devID>: Device serial to use instead of default interactive selection
          --system-apps      : Extract system apps too (default is user apps only)
          --apks             : Extract apks (default is optimized files only)
          -h|--help          : This help message
    $ scripts/extract-apps-from-device.sh --system-apps -o /tmp/art_data --apks
    [INFO]: Enumerating connected Android devices
    [INFO]: Trying to extract data from '163' packages
    [INFO]: Extracted data stored under '/tmp/art_data'
    

### update-vdex-location-checksums.sh使用从输入Apk存档文件中提取的CRCs更新Vdex文件位置校验和。有关如何使用该特性欺骗ART和绕过SafetyNet应用程序完整性检查的更多信息，请参阅[此处](a%20href=)。

    
    
    $ scripts/update-vdex-location-checksums.sh -h
      Usage: update-vdex-location-checksums.sh [options]
        options:
          -i|--input <file> : Input Vdex file to repair location checksum(s) within
          -a|--app <file>   : Input Apk file to extract location checksum(s) from
          -o|--output <dir> : Directory to save updated Vdex file (default is '.')
          -h|--help         : This help message
    

### tools/deodex/run.sh帮助工具，以批量方式将(deodex)
Vdex资源反编译回标准Dex文件。该工具自动处理CompactDex文件(如Android
Pie中介绍的)，并使用compact_dex_converter工具(更多信息在[这里](a%20href=))转换回StandardDex。由于转换器是作为AOSP源代码的一部分进行编译的，为了方便起见，开发人员维护了一组用于Linux和maacOS的二进制文件。

    
    
    $ tools/deodex/run.sh -h
      Usage: run.sh [options]
        options:
          -i|--input <path> : Directory with Vdex files or single file
          -o|--output <dir> : Directory to save deodex'ed resources (default is '.')
          -k|--keep         : Keep intermediate files (default 'false')
          -h|--help         : This help message
    $ tools/deodex/run.sh -i /tmp/vdex_samples -o /tmp/deodexed_samples
    [INFO]: Processing 140 input Vdex files
    [INFO]: 140 binaries have been successfully deodexed
    

***参考来源：[github](a%20href=)，由周大涛编译，转载请注明来自FreeBuf.COM**


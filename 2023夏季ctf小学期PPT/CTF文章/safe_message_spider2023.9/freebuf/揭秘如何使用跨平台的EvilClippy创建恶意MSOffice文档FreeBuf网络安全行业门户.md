***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

 **今天给大家介绍的是一款名叫EvilClippy的开源工具，EvilClippy是一款专用于创建恶意MS
Office测试文档的跨平台安全工具，它可以隐藏VBA宏和VBA代码，并且可以对宏代码进行混淆处理以增加宏分析工具的分析难度。当前版本的EvilClippy支持在Linux、macOS和Windows平台上运行，实现了跨平台特性。**

![111111111.png](https://image.3001.net/images/20190429/1556550097_5cc711d149fe1.png!small)  

## 功能介绍

1、 在GUI编辑器中隐藏VBA宏；

2、 混淆安全分析工具；

3、 VBA Stomping；

4、 引入VBA P-Code伪编码；

5、 设置远程VBA项目锁定保护机制；

6、 通过HTTP提供VBA Stomped模板；

## 工具效果

目前，该工具生成的默认Cobalt Strike宏可以绕过所有主流的反病毒产品以及宏分析工具。

### 技术分析

EvilClippy使用了[OpenMCDF库](https://github.com/ironfede/openmcdf/)来修改MS
Office的CFBF文件，并利用了[MS-OVBA规范](https://docs.microsoft.com/en-us/openspecs/office_file_formats/ms-ovba/)和特性。该工具重用了部分[Kavod.VBA.Compression](https://github.com/rossknudsen/Kavod.Vba.Compression)代码来实现压缩算法，并且使用了Mono
C#编译器实现了在Linux、macOS和Windows平台上的完美运行。

## 工具安装

注：跨平台编译代码可以在该项目的releases页面下获取。

### macOS和Linux

确保安装了Mono，然后运行下列命令：

    
    
    mcs/reference:OpenMcdf.dll,System.IO.Compression.FileSystem.dll/out:EvilClippy.exe *.cs

然后运行EvilClippy：

    
    
    mono EvilClippy.exe –h

### Windows

确保安装了Visual Studio，然后在Visual Studio开发者命令行窗口中输入下列命令：

    
    
    csc/reference:OpenMcdf.dll,System.IO.Compression.FileSystem.dll/out:EvilClippy.exe *.cs

然后在命令行中运行EvilClippy：

    
    
    EvilClippy.exe –h

## 工具使用

显示帮助信息

    
    
    EvilClippy.exe –h

在GUI中隐藏宏

    
    
    EvilClippy.exe -g macrofile.doc

VBA Stomp（P-Code伪编码）

    
    
    EvilClippy.exe -s fakecode.vba macrofile.doc

为VBA Stomping设置目标Office版本信息

    
    
    EvilClippy.exe -s fakecode.vba -t 2016x86 macrofile.doc

设置随机模块名（混淆安全分析工具）

    
    
    EvilClippy.exe -r macrofile.doc

通过HTTP提供VBA Stomp模板；

    
    
    EvilClippy.exe -s fakecode.vba -w 8080 macrofile.dot

设置远程VBA项目锁定保护

    
    
    EvilClippy.exe -u macrofile.doc

解除保护：

    
    
    EvilClippy.exe -uu macrofile.doc

## 项目地址

EvilClippy：【[GitHub传送门](https://github.com/outflanknl/EvilClippy)】

## 参考资料

1、 <https://outflank.nl/blog/2018/10/28/recordings-of-our-derbycon-and-brucon-presentations/>

2、 <https://vbastomp.com/>

3、 <https://github.com/bontchev/pcodedmp>

* 参考来源：[outflanknl](https://github.com/outflanknl/EvilClippy)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM


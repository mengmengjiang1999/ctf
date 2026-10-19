![](https://image.3001.net/images/20210905/1630831112_61348208b23a3ad922b17.png!small)

## Doldrums介绍

Doldrums是一款功能强大的逆向工程分析工具，主要针对的是Android端Flutter应用程序。具体来说，Doldrums是一个针对Flutter/Dart
Android代码（一般称之为libapp.so）的解析器和信息提取器，支持所有的Dart
v2.10发行版。在运行时，Doldrums可以导出隔离快照中存在的所有类。

注意：该工具当前处于测试版本，还缺少某些反序列化功能和一些类的信息。

## 关于Flutter和Dart

Flutter是谷歌的移动UI框架，可以快速在iOS和Android上构建高质量的原生用户界面。
Flutter可以与现有的代码一起工作。在全世界，Flutter正在被越来越多的开发者和组织使用，并且Flutter是完全免费、开源的。

而Dart则是谷歌开发的计算机编程语言，后来被Ecma
(ECMA-408)认定为标准。它被用于web、服务器、移动应用和物联网等领域的开发。它是宽松开源许可证（修改的BSD证书）下的开源软件。

## 工具要求

Doldrums的运行需要使用pyelftools来解析ELF格式内容，我们可以使用下列命令安装该组件：

    
    
    pip3 install pyelftools

## 工具使用

该工具的使用非常简单，我们可以直接运行下列命令，将libapp.so和output分别替换为相应的二进制文件以及目标输出文件。需要注意的是，verbose选项仅支持
Dart snapshot v2.12：

    
    
    python3 src/main.py [-v] libapp.so output

工具期待的输出即为导出的所有类，下面给出的是导出类的格式：

    
    
    class MyApp extends StatelessWidget {
    
        Widget build(DynamicType, DynamicType) {
    
            Code at absolute offset: 0xec85c
    
        }
    
     
    
        String myPrint(DynamicType, DynamicType) {
    
            Code at absolute offset: 0xeca80
    
        }
    
    }

绝对代码偏移量表明的是原生函数在libapp.so文件中的具体位置。

## 项目地址

 **Doldrums：** 【[ _GitHub传送门_](https://github.com/rscloura/Doldrums)】

## 参考资料

> [ _https://rloura.wordpress.com/2020/12/04/reversing-flutter-for-android-> wip/_](https://rloura.wordpress.com/2020/12/04/reversing-flutter-for-> android-wip/)

> [
> _https://github.com/mildsunrise/darter_](https://github.com/mildsunrise/darter)

>  
>


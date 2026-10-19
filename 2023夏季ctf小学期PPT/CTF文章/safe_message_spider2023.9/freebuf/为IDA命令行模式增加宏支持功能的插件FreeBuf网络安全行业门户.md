## 介绍

### 什么是climacros？

 **CLI宏是一种生产力工具，可让您在IDA的命令行界面（Python，IDC，WinDbg，BochDbg，Gdb等）中定义和使用静态或动态宏。**

![climacros-vid-1.gif](https://image.3001.net/images/20190430/1556627013_5cc83e45211c4.gif!small)

## 用法

安装后，climacros始终处于活动状态。它带有一组预定的宏

![为IDA命令行模式增加宏支持功能的插件](https://image.3001.net/images/20190430/1556627046_5cc83e6678401.png!small)

要创建或编辑新宏，只需从“快速插件视图”窗口（Ctrl-3）调用宏编辑器。

## 静态宏

静态宏在CLI中按原样替换。例如以下宏：

![为IDA命令行模式增加宏支持功能的插件](https://image.3001.net/images/20190430/1556627057_5cc83e712cf9e.png!small)

执行时输出以下内容：

![为IDA命令行模式增加宏支持功能的插件](https://image.3001.net/images/20190430/1556627062_5cc83e76da2aa.png!small)

## 动态宏

可以定义动态宏，这些宏通过评估返回字符串的Python表达式而得到扩展。例如，该`idc.here()`命令非常有用，可以缩写为较短的宏，例如`$!`或`${here}`。要定义动态宏，只需用`${`和包围其表达式`}$`。长形式的宏`${here}`用于`idc.here()`表达的定义如下：

![为IDA命令行模式增加宏支持功能的插件](https://image.3001.net/images/20190430/1556627069_5cc83e7d0cbeb.png!small)

简短形式`$!`：

![为IDA命令行模式增加宏支持功能的插件](https://image.3001.net/images/20190430/1556627074_5cc83e82615bc.png!small)

当CLI命令中存在宏时，将调用该宏：

![为IDA命令行模式增加宏支持功能的插件](https://image.3001.net/images/20190430/1556627079_5cc83e876c765.png!small)

## 内联替换

您不必定义宏以便在CLI中进行表达式扩展。如果您需要在CLI中进行一次性表达式扩展，只需定义内联表达式：

    
    
    fn =  “ test _ $ {str（sum（range（10）））} $。bin ”
    

要么：

    
    
    v =  “ $ {str（1 + 2 + 3 + 4）} $ ”
    

表达式应始终求值为 **字符串** ，因此始终记住`str()`表达式，或者`"%x" % expr`如果它不返回字符串，则将其格式化。

## 安装

climacros是用C
++编写的，带有IDA的SDK，因此它应该像常规插件一样进行部署。将插件二进制文件复制到以下任一位置：`/plugins``%APPDATA%\Hex-Rays/plugins`由于该插件使用IDA的SDK而没有其他特定于操作系统的功能，因此该插件应该可以编译为macOS和Linux。我只提供MS
Windows二进制文件。请查看[发布页面](a%20href=)。第一次运行插件时，它将填充默认的宏。如果删除所有宏，除非删除以下文件，否则不会返回默认宏：`%APPDATA%\Hex-Rays/firstrun.climacros`。

 ***参考来源：[github](http://a%20href=)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**


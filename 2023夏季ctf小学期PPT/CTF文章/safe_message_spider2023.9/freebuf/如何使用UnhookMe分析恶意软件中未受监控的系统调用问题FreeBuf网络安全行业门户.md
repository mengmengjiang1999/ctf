![](https://image.3001.net/images/20210907/1630946818_61364602f1a48dc1c5642.png!small)

## 关于UnhookMe

UnhookMe是一款 **通用的Windows API动态解析工具** ，可以帮助广大研究人员 **分析和处理恶意软件中未受监控的系统调用问题。**

在这个侵入式反病毒产品和EDR产品盛行的年代，很多网络攻击者必须拥有强大的工具来绕过这些安全防御工具。而动态导入解析器能够在运行中取消已用函数的钩子，这也是增强攻击者攻击能力的又一方法。

而UnhookMe可以帮助广大研究人员在编译的可执行文件的PE头中保持可视性。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mgeeky/UnhookMe.git

## 工具使用

我们总共需要在自己的解决方案中引入五个C++源文件/头文件。不过，你的主程序文件仅需要引入两个必要的头文件即可，文件描述如下：

resolver.h - 头文件中包含了UnhookingImportResolver的大部分实现；

resolver.cpp - 包含了全局选项的源代码；

usings.h - 一个非常大的头文件，包含了针对常见Windows API的using类型定义；

PE.cpp - 自定义PE解析器源代码文件；

PE.h - 自定义PE解析器源头文件；

## 必须的头文件

你的程序仅需要下列两个必要的头文件：

    
    
    #include "usings.h"
    
    #include "resolver.h"

## 全局选项

下面给出的是解析器的全局配置选项，我们可以根据自己的需要来进行修改，这些参数全部定义在resolver.cpp文件中：

globalQuietOption - 如果你不想获取输出，则设置为true；

globalVerboseOption - 如果你想要获取详细的Verbose输出，则设置为true；

globalAntiSplicingOption - 解除函数钩子；

globalLogFilePath - 重定向输出日志；

    
    
    bool globalQuietOption = false;
    
    bool globalVerboseOption = true;
    
    bool globalAntiSplicingOption = true;
    
     
    
    wchar_t globalLogFilePath[MAX_PATH] = L"";

## 工具使用样例

![](https://image.3001.net/images/20210907/1630947231_6136479f3ec9d60cbccf1.gif)

![](https://image.3001.net/images/20210907/1630947318_613647f6002d8a29ac19a.gif)

## 项目地址

 **UnhookMe：** 【[ _GitHub传送门_](https://github.com/mgeeky/UnhookMe)】


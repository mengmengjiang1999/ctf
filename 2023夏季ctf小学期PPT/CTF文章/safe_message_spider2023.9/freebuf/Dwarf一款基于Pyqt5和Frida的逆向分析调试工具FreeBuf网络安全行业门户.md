今天给大家介绍的是一款名叫Dwarf的逆向分析调试工具，该工具基于Pyqt5和Frida实现，专为逆向工程师、安全破解人员和安全分析专家设计。

![](https://image.3001.net/images/20190821/1566399930_5d5d5dbaa2d55.png!small)

##  Dwarf

**Dwarf本质上是一款调试器，这个项目起初知识想使用PyQt来给Frida增加一个有好的UI界面，并且主要用于Android端。但是通过开发人员的努力之后，该工具已经支持iOS端了。目前，得益于整个社区的共同努力，该工具已完全开源，并且支持对任何类型的操作系统进行分析，并运行在任意桌面端操作系统。**

##  功能介绍

###  多系统多平台支持

Dwarf基于PyQt5实现，可以直接在任何支持Python的操作系统上运行，并且使用了Frida作为后端，功能得到了稳定保证。

###  动态分析

允许执行动态指令，我们的Frida代理会在目标系统中加载，并允许我们设置断点。除此之外，它还可以终端模块构造器来帮助我们构造初始化函数。而且跟踪器、寄存器和其他功能模块可以帮助我们降低逆向分析的调试难度。

###  静态分析

我们构建了多种功能插件来扩展Dwarf的功能，它们可以帮助我们快速完成后端模块分析以及模拟。而且还提供了一套工具集和两个控制台接口来接收JavaScript以及Python脚本。

###  自动化

很多研究人员在调试和分析的过程中，都会想要让很多任务完成得快一点，尤其是那些重复性工作，Dwarf就可以帮助大家加速这个过程。

可以生成大量命令行参数并将它们注入到目标代理中，例如：

    
    
    python3 dwarf.py -t android -sp -p com.android.target -s myagent.js

提供了JavaScript API来添加钩子和断点。

提供了API来控制目标程序。

###  可扩展

Dwarf内置的插件系统允许我们注入PyQt小工具，并通过多个Dwarf代码Python
API来与目标设备进行交互。插件还允许我们注入自定义Frida代理来扩展或创建新的JavaScript API。

##  工具安装

###  工具要求

1、Frida服务器；

2、Python 3；

###  安装与运行：

    
    
    git clone <https://github.com/iGio90/Dwarf>
    
        cd Dwarf
    
        pip3 install -r requirements.txt
    
        python3 dwarf.py

##  可选项

你还可以通过下列方式安装Dwarf：

    
    
    sudo python3 setup.py install

然后运行下列命令即可使用工具：

    
    
    dwarf /bin/man open
    
        dwarf -t android -s myagent.js -sp com.target

##  工具配置

我们可以将下列代码拷贝至.dwarf中：

    
    
    "dwarf_ui_hexedit_bpl":32 (default: 16) - Bytes per line in hexview
    
        "dwarf_ui_hexstyle":"upper", "lower" (default: "upper") - overallhexstyle 0xabcdef or 0xABCDEF (note: click on the "Offset (X)" inhexview to change)
    
        "dwarf_ui_font_size":12 (default: 12) - (note: hexview/disasm use other font wait for settingsdlg orchange lib/utils.py get_os_monospace_font())

##  工具运行截图

##
![](https://image.3001.net/images/20190821/1566400002_5d5d5e028c81a.png!small)![](https://image.3001.net/images/20190821/1566400002_5d5d5e029a028.png!small)![](https://image.3001.net/images/20190821/1566400002_5d5d5e026d167.png!small)![](https://image.3001.net/images/20190821/1566400003_5d5d5e0358f47.png!small)![](https://image.3001.net/images/20190821/1566400003_5d5d5e037bc22.png!small)![](https://image.3001.net/images/20190821/1566400003_5d5d5e0362a8b.png!small)

##  项目地址

> Dwarf：【[GitHub传送门](https://github.com/iGio90/Dwarf)】

 ***
参考来源：[iGio90](https://github.com/iGio90/Dwarf)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


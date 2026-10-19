![](https://image.3001.net/images/20230828/1693234410_64ecb4eaacc72804db13b.png!small)

## 关于airpydump

airpydump是一款功能强大的无线网络数据包实时分析工具，airpydump的核心类似于Aircrack套件中的airodump-ng。在该工具的帮助下，广大研究人员将能够轻松捕捉和分析无线网络实时数据包。

## 工具运行机制

当前版本的airpydump支持三种工作模式，即读取模式、实时模式和隐蔽模式。读取模式用于通过airodump、wireshark或airpydump在安全研究的早期阶段读取已写入的捕获文件。如果你正在执行某些任务，不想看到实时流量，只想在任务操作结束之后查看的话，就可以使用隐蔽模式了。值得一提的是，任何时候按下Ctrl+C键，都可以直接查看到当前已捕捉到的数据包。实时模式使用了Python的curses库，可以在无线适配器捕获到实时数据包后立即打印。

需要注意的是，不要在脚本执行过程中修改终端窗口的大小，因为可能会导致脚本运行崩溃。

## 工具下载

由于该工具基于纯Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

接下来，广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/hash3liZer/airpydump.git

## 工具使用样例

    
    
    [usage] python airpydump.py [arguments]

## 工具运行参数

    
    
    -h, --help                      查看工具帮助手册
    
    -i, --interface=                 监控模式要使用的接口
    
    -r, --read=                   提前读取一个捕捉到的网络数据包文件，例如packets.cap
    
    -w, --write=                    将捕捉到的数据包写入到一个文件中
    
    -c, --curses                    使用curses库打印实时捕捉到的网络数据包
    
    -i, --live                      该参数必须在隐蔽模式和实时模式下使用

## 工具模式选择

### 读取模式

    
    
    python airpydump.py -r [/path/to/.cap/file]

### 隐蔽模式

    
    
    python airpydump.py -i [Monitor Interface] --live

### 实时模式

    
    
    python airpydump.py -i [Monitor Interface] --live --curses

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/hash3liZer/airpydump/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **airpydump** ：【[ _GitHub传送门_](https://github.com/hash3liZer/airpydump)】

## 参考资料

> [ _admin@shellvoide.com_](mailto:admin@shellvoide.com)
>
> [ _https://www.shellvoide.com/_](https://www.shellvoide.com/)


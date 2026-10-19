![](https://image.3001.net/images/20230828/1693152319_64eb743fc7e7df3061181.jpg!small)  

## 关于Fi6S

Fi6S是一款功能强大且高效的IPv6端口扫描工具，该工具的运行速度非常快，支持通过异步发送和处理原始数据包来实现其功能。该工具的设计原理和目标与[
_Masscan_](https://github.com/robertdavidgraham/masscan)非常相似，并且目前处于积极开发中，未来版本将新增更多高级功能。

## 工具安装

由于该工具基于C语言开发，因此我们首先需要在本地设备上安装并配置好C程序编译工具，例如最新版本的Visual
Studio。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/sfan5/fi6s.git

### 代码构建/编译

该工具在大多数Linux操作系统中的代码构建都非常简单，接下来我们以Ubuntu为例。

将项目代码克隆至本地之后，在命令行终端中切换到项目目录下，然后运行下列命令完成代码编译所需要的其他组件：

    
    
    cd fi6s/
    
    apt install gcc make git libpcap-dev

现在，运行下列命令即可完成代码编译和构建：

    
    
    make BUILD_TYPE=release

此时，我们将能够在./fi6s路径下找到构建好的Fi6S扫描器可执行文件。

需要注意的是，Fi6S仅在Linux操作系统上进行过完整测试，理论上支持在其他类UNIX平台上运行。

## 工具使用

该工具的使用非常简单，Fi6S会尝试对目标自动执行扫描检测任务，例如数据源、路由器MAC地址和源IP地址等等：

    
    
    # ./fi6s -p 80,8000-8100 2001:db8::/120

上述命令将执行下列任务：

> 1、扫描2001:db8::/120子网（总共256个地址）；
>
> 2、扫描TCP端口80和8000-8100（总共102个端口）；
>
> 3、每秒尽可能多地发送数据包；
>
> 4、将扫描结果输出以列表格式输出；

工具还提供了很多不同的方法来指定要扫描的地址范围，使用 --print-hosts可以打印所有的IP地址，或使用--print-summary快速了解扫描情况概述。

使用fi6s --help命令可以查看工具更多的高级功能选项和命令参数。

### Banner获取

我们可以使用--banners选项来获取Banner：

    
    
    # ip6tables -A INPUT -p tcp -m tcp --dport 12345 -j DROP
    
    # ./fi6s -p 22 --banners --source-port 12345 2001:db8::xx

### UDP

UDP扫描不需要在数据包到达操作系统堆栈之前丢弃数据包，但对于避免ICMPv6无法访问响应洪泛来说，还是需要的，此时我们只需要提供一个额外的--udp选项即可：

    
    
    # ip6tables -A INPUT -p udp -m udp --dport 12345 -j DROP
    
    # ./fi6s -p 53 --banners --udp --source-port 12345 2001:db8::xx

需要注意的是，与TCP不同，UDP场景下只有扫描Fi6S支持其协议的端口，才会得到有用的（或任何）结果。此时，你可以使用--list-protocals来查看可用协议列表。

## 许可证协议

本项目的开发与发布遵循[ _GNU_](https://github.com/sfan5/fi6s/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Fi6S** ：【[ _GitHub传送门_](https://github.com/sfan5/fi6s)】

## 参考资料

> [
> _https://github.com/robertdavidgraham/masscan_](https://github.com/robertdavidgraham/masscan)


![](https://image.3001.net/images/20201104/1604494330_5fa2a3fa38bb15f9b5c05.png!small)

## dnxfirewall

dnxfirewall是一套包含了经过优化的高性能应用程序及服务套件，它可以将一个标准的Linux系统转换成一个基于空间区域的下一代防火墙系统。dnxfirewall中的所有软件都可以相互进行交互，并配合运行。dnxfirewall基于纯Python实现，防火墙内的应用程序和服务都是基于模块化设计的，因此很多定制化的修改和功能实现都可以不费吹灰之力即可实现。主安全模块对通过系统的所有通信连接、数据流和消息来进行直接/内联控制。也就是说，根据不同的协议，如果启用了全面检查的话，我们可以通过卸载较低级别的控制来保持整个系统内的最高数据吞吐量。除此之外，dnxfirewall提供了一个自定义的IPTable链，允许管理员在不覆盖dnx安全模块的情况下，捕捉到所有的数据包流。

## 包含的功能

DNS代理

> 基于块的分类（TLD、子字符串匹配）
>
> 基于用户添加的白名单/黑名单或自定义常规类创建
>
> 带有可选UDP回退的本机DNS over TLS转换
>
> 本地dns服务器
>
> 软件故障转移
>
> 二级记录缓存

IP代理

> 基于复现的主机过滤
>
> 地理位置过滤器
>
> LAN限制（禁用所有未列入白名单的IP地址对LAN的访问）

IPS/IDS（WAN/内联）

> 拒绝服务检测/防御
>
> 端口扫描检测/防御

轻量级DHCP服务器（自定义）

> IP保留
>
> 安全警报集成

通用服务

> 日志处理
>
> 数据库管理
>
> Syslog客户端（UDP、TCP、TLS）：当前该功能处于测试状态，这个服务默认不会启用。

其他功能

> IPv6禁用
>
> 预构建IPTable规则
>
> DNS绕过防御（HTTPS、TCP、TLS）
>
> 默认情况下，所有到wan的入站连接都已断开
>
> IPTABLES自定义链管理挂钩到数据包流

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/DOWRIGHTTV/dnxfirewall.git

## 工具配置

出于部署方便的考虑，SQLite3是当前版本dnxfirewall默认使用的数据库系统。我们也可以通过调整dnx_configure/dnx_constants.py中定义的环境变量“SQL_VERSION”来使用PostgreSQL数据库。警告：初始化配置后再调整数据库的话，可能会导致dnxfirewall的运行出现问题。

首先，编辑data/config.json和data/dhcp_server.json来映射我们的系统[接口]。接下来，将所有的系统服务文件移动到系统的systemd目录下。然后，配置系统接口，必须将LAN设置为本地网络的默认网关。

配置完成后，针对我们当前的系统架构来编译python-netfilterqueue，确保文件名为netfilter.so，并将其存储至dnxfirewall/netfilter目录下。

然后，针对我们当前的系统架构编译dnx_iptools/binary_search.pyx，确保文件名为binary_search.so，并将其存储至dnxfirewall/dnx_iptools目录下。

最后，运行工具提供的部署脚本来安装工具即可。

## 工具演示视频

视频地址：【[
_油管链接_](http://www.youtube.com/watch?feature=player_embedded&v=6NvRXlNjpOc)】

## 许可证协议

dnxfirewall项目的开发与发布遵循AGPL v3开源许可证协议。

## 项目地址

dnxfirewall：【[ _GitHub传送门_](https://github.com/DOWRIGHTTV/dnxfirewall)】


![](https://image.3001.net/images/20200111/1578715608_5e1949d876433.jpg!small)

##  IoTShark

**IoTShark是一款物联网监控服务平台，它可以帮助广大研究人员监控其物联网设备所发送或接收的数据趋势。通常情况下，采取适当的配置来设置中间人攻击测试需要花费相当长的时间，对于那些在计算机安全甚至计算机科学方面几乎没有经验的人来说，这几乎是一项不可能完成的任务。**

IoTShark旨在通过运行一个脚本来安全研究人员提供一个几乎全自动化的解决方案，并监控他们的物联网设备。研究人员只需要选择他们想要监视的设备，这个程序将通过发动ARP攻击、设置包转发和中间人包嗅探器来处理其余的繁重工作。它还有一个易于使用和交互的Web
UI，用户可以根据端口、类型和时间戳过滤数据包，从而更广泛地了解传输的数据量和时间。

除此之外，IoTShark还可以对某些类型的数据进行数据分类，例如heartbeat消息、数据传输和异常等等。

##  工具下载

广大研究人员可以使用下列命令直接将本项目源码克隆至本地：

    
    
    git clone https://github.com/sahilmgandhi/IotShark.git

##  工具使用

注意，该工具的正常运行需要安装Python 3环境。

首先，运行下列命令安装该工具的必要依赖库：

    
    
    $pip3 -r requirements.txt

接下来，设置IP转发：

    
    
    $sudo sysctl net.inet.ip.forwarding=1

最后，使用下列命令运行IoTShark：

    
    
    sudo python3 mitm_main.py

##  主程序脚本

创建一个Python Virtual虚拟环境，然后安装相关的依赖组件包：

> virtualenv --python=`which python3` venv
>
> source venv/bin/activate
>
> python -r requirements.txt

确保你的本地主机开启了数据包转发功能，这一点对于实现中间人攻击来说是非常重要的，在macOS上，我们可以通过下列命令来完成配置：

    
    
    sudo sysctl net.inet.ip.forwarding=1

配置完成后，我们就可以运行主程序脚本“mitm_main.py”了。

当前版本的主程序脚本会完成以下几件事情：

> 1、扫描目标子网中的所有主机，子网通过-s参数来进行配置；
>
> 2、扫描每一台主机的硬件厂商以及操作系统信息；
>
> 3、在被选主机和网关路由器间执行ARP攻击；
>
> 4、将捕捉到的数据以图形化的形式输出给用户，该功能需要通过-f参数启用；

在ARP攻击完成之后，我们就可以通过WireShark来测试目标设备间的捕捉流量了，设置的过滤器如下所示：

    
    
    (ip.src==192.168.0.215 or ip.dst==192.168.0.215) and tcp.port != 443

##  数据文件格式

捕捉到的数据将以csv文件格式进行存储，数据结构格式如下所示：

    
    
    {timestamp, incoming_bytes, outgoing_bytes, srcport, dstport, transfer_protocol, connection_protocol, srcip, dstip}
    
        123123213, 0, 240, 36, 80, 65124, HTTP, UDP, 192.168.0.215, 104.24.4.5
    
        123123240, 300, 0, 800, 443, 65125, HTTPS, TCP, 104.24.4.5, 192.168.0.215

##  项目地址

> IoTShark：【[GitHub传送门](https://github.com/sahilmgandhi/IotShark)】

 ***
参考来源：[sahilmgandhi](https://github.com/sahilmgandhi/IotShark)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


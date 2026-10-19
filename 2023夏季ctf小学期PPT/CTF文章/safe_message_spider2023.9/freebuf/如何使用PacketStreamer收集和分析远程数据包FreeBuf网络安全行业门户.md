## 关于PacketStreamer

PacketStreamer是一款高性能远程数据包捕获和收集工具，该工具由Deepfence开发，并且应用到了Deepfence的[
_ThreatStryker_](https://deepfence.io/threatstryker/)安全监控平台中以根据需要从云工作负载来收集网络流量，并帮助广大研究人员进行信息安全取证分析。本质上来说，PacketStreamer可以算是针对云环境的分布式tcpdump。

## 工具特性

> 1、轻量级工具
>
> 2、支持捕捉数据流，并且不会进行额外处理
>
> 3、可移植性
>
> 4、跨虚拟机
>
> 5、支持Kubernetes和AWS Fargate
>
> 6、支持Linux和Windows系统

## 工具机制

PacketStreamer的传感器会在目标服务器上启动，传感器负责捕捉流量数据，部署过滤器，然后将捕捉到的流量传输到中央接收器中。在这个过程中，还可以使用TLS对业务流进行压缩和/或加密。

PacketStreamer对接收器支持从多个远程传感器接收PacketStreamer数据流，并将数据包写入到一个本地pcap文件。

工具运行机制如下图所示：

![](https://image.3001.net/images/20220625/1656148508_62b6d21cb328754876e2c.png!small)

PacketStreamer传感器在远程主机上收集原始网络数据包，并使用BPF过滤器选择要捕获的数据包，并将它们转发到中央接收进程，在那里它们将以pcap格式导入。传感器非常轻量级，对远程主机的性能影响很小。PacketStreamer传感器可以在裸机服务器、Docker主机和Kubernetes节点上运行。

PacketStreamer接收器接受来自多个传感器的网络流量，并将其收集到单个中央pcap文件中。然后，我们可以处理pcap文件或将流量实时反馈到各种网络数据处理工具中，如Zeek、Wireshark
Suricata，或作为机器学习模型的实时数据流。

## 工具部署

首先，我们需要在设备上安装并配置好Golang环境，并在构建PacketStreamer之前安装好Golang工具链以及libpcap-dev。

    
    
    sudo apt install golang-go libpcap-dev

接下来，使用下列命令将该项目源码克隆至本地，并完成代码构建：

    
    
    git clone https://github.com/deepfence/PacketStreamer.git
    
    cd PacketStreamer/
    
    make

## 工具使用

下列命令可以运行一个PacketStreamer接收器，并监听端口8081，然后将pcap输出写入到“/tmp/dump_file”路径（具体请查看[
_receiver_
_.yaml_](https://github.com/deepfence/PacketStreamer/blob/main/contrib/config/receiver.yaml)）：

    
    
    ./packetstreamer receiver --config ./contrib/config/receiver.yaml

下列命令可以在本地或远程主机中运行一个或多个PacketStreamer，我们可以在[ _sensor_
_.yaml_](https://github.com/deepfence/PacketStreamer/blob/main/contrib/config/sensor-local.yaml)文件中编写服务器地址：

    
    
    # 在目标主机运行以捕捉或转发流量
    
    # 拷贝并编辑样例sensor-local.yaml文件，并添加接收器主机的地址
    
     
    
    cp ./contrib/config/sensor-local.yaml ./contrib/config/sensor.yaml
    
    ./packetstreamer sensor --config ./contrib/config/sensor.yaml

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/deepfence/PacketStreamer/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **PacketStreamer** ：【[
_GitHub传送门_](https://github.com/deepfence/PacketStreamer)】

## 参考资料

> [
> _https://deepfence.io/threatstryker/_](https://deepfence.io/threatstryker/)
>
> [
> _https://github.com/elastic/beats/tree/master/packetbeat_](https://github.com/elastic/beats/tree/master/packetbeat)
>
> [ _https://github.com/eldadru/ksniff_](https://github.com/eldadru/ksniff)
>
> [
> _https://deepfence.github.io/PacketStreamer/_](https://deepfence.github.io/PacketStreamer/)
>
> [
> _https://github.com/deepfence/PacketStreamer/blob/main/SECURITY.md_](https://github.com/deepfence/PacketStreamer/blob/main/SECURITY.md)
>
> [ _https://join.slack.com/t/deepfence-community/shared_invite/zt-> podmzle9-5X~qYx8wMaLt9bGWwkSdgQ_](https://join.slack.com/t/deepfence-> community/shared_invite/zt-podmzle9-5X~qYx8wMaLt9bGWwkSdgQ)


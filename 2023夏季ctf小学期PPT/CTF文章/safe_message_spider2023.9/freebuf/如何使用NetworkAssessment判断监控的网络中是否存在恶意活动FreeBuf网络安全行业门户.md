![](https://image.3001.net/images/20230824/1692878476_64e7468cb6df120d6135a.png!small)  

## 关于Network_Assessment

Network_Assessment是一款功能强大的网络可疑活动监控工具，该工具在Wireshark或TCPdump的加持下，可以帮助广大研究人员根据记录下的网络流量数据，来检测和判断正在监控的目标网络中是否存在恶意活动。

## 功能特性

Network_Assessment基于纯Python开发，可以对给定的.pcap文件执行网络流量分析，并尝试检测下列可疑的网络活动或攻击行为：

> 1、DNS隧道；
>
> 2、SSH隧道；
>
> 3、TCP会话劫持；
>
> 4、SMB攻击；
>
> 5、SMTP或DNS攻击；
>
> 6、IPv6分片攻击；
>
> 7、TCP RST攻击；
>
> 8、SYS洪泛攻击；
>
> 9、UDP洪泛攻击；
>
> 10、Slowloris攻击；

除此之外，该脚本还将尝试检测包含了可疑关键字（例如“密码”、“登录名”、“管理员”等）的数据包，并将检测到的可疑活动或攻击行为显示在控制台中以方便广大研究人员查看。

当前版本的Network_Assessment主要包含下列功能：

> 1、get_user_input()：从用户处获取.pcap文件的路径地址；
>
> 2、get_all_ip_addresses(capture)：返回一个包含了所有数据源和目标IP地址的数据集合；
>
> 3、detect_*函数：用于检测指定攻击或可疑行为；
>
> 4、main()函数：执行工具脚本的主要操作。首先，它会从用户处获取.pcap文件的路径，然后对其进行分析并尝试检测指定的攻击行为或可疑活动；

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python
3环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/alperenugurlu/Network_Assessment.git

然后切换到项目目录中，并使用pip3命令和项目提供的requirements.txt文件安装该工具所需的其他依赖组件：

    
    
    cd Network_Assessment/
    
    pip3 install -r requirements.txt

## 工具运行

首先，我们可以使用下列命令执行工具脚本，并按照提示输入.pcap文件的路径即可：

    
    
    python3 Network_Compromise_Assessment.py
    
    Please enter the path to the .pcap or .pcapng file: /root/Desktop/TCP_RST_Attack.pcap

工具运行结果如下图所示：

![](https://image.3001.net/images/20230824/1692878544_64e746d06f8e0b70fbb1d.png!small)

## 项目地址

 **Network_Assessment** ：【[
_GitHub传送门_](https://github.com/alperenugurlu/Network_Assessment)】

## 参考资料

> [ _https://www.linkedin.com/in/alperen-> ugurlu-7b57b7178/_](https://www.linkedin.com/in/alperen-ugurlu-7b57b7178/)


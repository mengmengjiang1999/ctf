![](https://image.3001.net/images/20230830/1693368561_64eec0f1c30f767d4e36b.gif!small)

## 关于Prowler

Prowler是一款功能强大的分布式网络漏洞扫描工具，该工具可以在一个树莓派集群上实现其功能。在该工具的帮助下，广大研究人员可以轻松对目标网络执行安全扫描、收集设备指纹、查看开放端口和常用服务、以及常规的安全漏洞扫描等等。

## 功能介绍

当前版本的Prowler支持下列网络安全功能：

> 1、扫描一个网络（一个特定的子网或IP地址列表）中与活动网络设备相关的所有IP地址；
>
> 2、使用指纹来识别目标设备类型；
>
> 3、扫描和判断目标设备的任意开放端口；
>
> 4、将端口与常见服务相关联；
>
> 5、使用厂商默认手册数据测试设备并识别常见凭证；
>
> 6、通过一个[ _仪表盘_](https://github.com/tlkh/prowler-dashboard)提醒用户是否发现了安全漏洞；

## 硬件要求

> 1、树莓派[ _集群HAT_](https://clusterhat.com/)（Pi Zero W * 4）；
>
> 2、树莓派3；
>
> 3、目标网络中需要有设备接入；

![](https://image.3001.net/images/20230830/1693368589_64eec10d999d3f5f7292f.png!small)

![](https://image.3001.net/images/20230830/1693368599_64eec11762a88e9701bbc.jpg!small)

![](https://image.3001.net/images/20230830/1693368618_64eec12a3a149678c6746.jpg!small)

## 工具软件栈

> 1、Raspbian Stretch;
>
> 2、Raspbian Stretch Lite；
>
> 3、Python 3；
>
> 4、相关Python依赖组件（详见requirements.txt）；
>
> 5、Ansible（用于管理整个集群）；

![](https://image.3001.net/images/20230830/1693368632_64eec138d4c178c36dff9.png!small)

## Python依赖组件

> [ _dispy_](http://dispy.sourceforge.net/)
>
> [ _pythohn_ _-libnmap_](https://nmap.org/)
>
> paramiko
>
> [ _eel_](https://github.com/tlkh/prowler-dashboard)
>
> [ _rabbitmq_](https://www.rabbitmq.com/)

## 工具部署

由于该工具基于Python 3开发，因此我们首先需要在控制器树莓派上安装并配置好Python 3环境。

首先，广大研究人员可以使用下列命令将该项目源码克隆至本地（树莓派）：

    
    
    git clone https://github.com/tlkh/prowler.git

接下来，切换到项目目录中，并使用pip3命令和项目提供的requirement.txt文件在控制器树莓派中安装该工具所需的其他依赖组件：

    
    
    cd prowler/
    
    sudo pip3 install -r requirements.txt

然后运行下列命令在所有工作节点上安装好必要的代码包：

    
    
    ansible-playbook playbooks/setup_node.yml

使用下列命令将Prowler和dispy代码库克隆到所有工作节点中：

    
    
    ansible-playbook playbooks/clone_repos.yml

在控制器树莓派上运行下列命令，以确保所有的Pi Zero都已成功启动：

    
    
    clusterhat on

最后，在控制器树莓派上运行下列命令就可以启动Prowler了：

    
    
    python3 cluster.py

如需修改要扫描的IP地址范围，可以直接修改cluster.py文件中的下列对应内容：

    
    
    test_range = []
    
     
    
        for i in range(0, 1):
    
        
    
            for j in range(100, 200):
    
            
    
                test_range.append("172.22." + str(i) + "." + str(j))

## 工具使用样例

如需在多台设备上执行SSH命令，请安装好pssh：

    
    
    pssh -h pssh-hosts -l username -A -i "command"

创建集群（在compute.py文件中）：

    
    
    cluster = dispy.JobCluster(compute, nodes='pi0_ip', ip_addr='pi3_ip')

检查网络连通性：

    
    
    ansible all -m ping
    
    ping p1.local -c 1 && ping p2.local -c 1 && ping p3.local -c 1 && ping p4.local -c 1

设备温度检测：

    
    
    /opt/vc/bin/vcgencmd measure_temp && pssh -h workers -l pi -A -i "/opt/vc/bin/vcgencmd measure_temp" | grep temp

## 工具运行截图

仪表盘：

![](https://image.3001.net/images/20230830/1693368732_64eec19c27282f7870847.jpg!small)

扫描监控器：

![](https://image.3001.net/images/20230830/1693368741_64eec1a5e2b3b4cb0958f.png!small)

RPI监控器：

![](https://image.3001.net/images/20230830/1693368751_64eec1af9103945e48479.jpg!small)

命令行终端：

![](https://image.3001.net/images/20230830/1693368759_64eec1b7ddf2e2d957424.png!small)

iPad端监控：

![](https://image.3001.net/images/20230830/1693368769_64eec1c10779a7bd56cee.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/tlkh/prowler/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Prowler** ：【[ _GitHub传送门_](https://github.com/tlkh/prowler)】

## 参考资料

> [ _https://github.com/tlkh/prowler-> dashboard_](https://github.com/tlkh/prowler-dashboard)
>
> [ _https://clusterhat.com/setup-software_](https://clusterhat.com/setup-> software)
>
> [ _http://dispy.sourceforge.net/_](http://dispy.sourceforge.net/)
>
> [ _https://github.com/tlkh/prowler-> dashboard_](https://github.com/tlkh/prowler-dashboard)
>
> [ _https://www.rabbitmq.com/_](https://www.rabbitmq.com/)
>
> [ _https://clusterhat.com/_](https://clusterhat.com/)
>
> [ _https://tlkh.github.io/prowler/_](https://tlkh.github.io/prowler/)


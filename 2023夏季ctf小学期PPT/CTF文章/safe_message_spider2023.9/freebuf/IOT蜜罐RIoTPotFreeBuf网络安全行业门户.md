**目 录**

  1. 一. 介绍
  2. 二. 系统架构
  3. 三. 安装
  4. 四. 运行
  5. 五. 日志分析
  6. 六. 思考
  7. 七. 参考

# 一. 介绍

RiotPot是一个功能齐全的交互式蜜罐，主要专注于IOT和OT协议，同时也能够模拟其他服务。

该蜜罐主要通过插件的形式加载到蜜罐中去，使RiotPot成为模块化且非常便携的蜜罐系统。运行的服务是在运行时候加载的，这意味着蜜罐即使能够根据变化实时变化。

# 二. 系统架构

![1656900623_62c24c0f4882623563fd8.png!small](https://image.3001.net/images/20220704/1656900623_62c24c0f4882623563fd8.png!small)

图1-1 系统架构

该架构包含六大部分(如图1-1 系统架构)

RIoTPot core：负责容器网络配置、管理和编排所需模块

Configuration &
Orchestration：配置模块在启动时候为RIoTPot提供所需要的参数。这包括特定协议和配置文件模拟的用户偏好以及所需的交互级别。

Attack Capture and Noise Filter：攻击捕获和过滤掉从互联网范围的搜索(如Shodan和Censys)接收到的可以流量。

Hybrid-Interaction (Low and High-Interaction modes)
:RIotPot用Go语言实现，并通过包促进模块化结构和开发。

Attack Database：攻击数据库存储蜜罐收到的所有攻击流量。

# 三. 安装

建议采用docker方式安装

# riotpot/depoyments

$ docker-compose -p riotpot -f docker-compose.yml up -d --build # 构建完成之后开启蜜罐系统  
  
---  
  
Docker镜像(如图1-2 docker镜像)

![1656900637_62c24c1db667239cd862f.png!small](https://image.3001.net/images/20220704/1656900637_62c24c1db667239cd862f.png!small)

图1-2 docker镜像

TIPS:

1.docker-compose 版本必须支持3.8版本

2.build/docker/Dockerfile、build/docker/Dockerfile.documentation 文件中添加RUN go
env -w GOPROXY=https://goproxy.io,direct

# 四. 运行

开启蜜罐

# riotpot/deployments

$ docker-compose up  
  
---  
  
关闭蜜罐

# riotpot/deployments

$ docker-compose down -v  
  
---  
  
运行界面(如图1-3 后端界面)

默认提供7中服务(httpd、echod、sshd、telnetd、mqttd、coapd、modbusd)

![1656900657_62c24c31c8692131b9933.png!small](https://image.3001.net/images/20220704/1656900657_62c24c31c8692131b9933.png!small)

图1-3 后端界面

# 五. 日志分析

RioTPot攻击日志主要存于PostgreSQL数据库

httpd、telnetd攻击payload(如图1-4 攻击payload)

![1656900670_62c24c3e8f36b463da21c.png!small](https://image.3001.net/images/20220704/1656900670_62c24c3e8f36b463da21c.png!small)

图1-4 攻击payload

TIPS:

  1. 默认5432端口没有映射出来，需要修改docker-compose.yml文件(ports: "5432:5432")

# 六. 思考

如何将市面上常见的物联网设备以模拟方式放入RiotPot蜜罐中?

默认提供的服务以插件化方式开发,存放于plugin目录下(如图1-5 服务插件)

![1656900688_62c24c50e16279040f056.png!small](https://image.3001.net/images/20220704/1656900688_62c24c50e16279040f056.png!small)

图1-5 服务插件

各个服务对应各个服务接口，并将攻击payload实时存储于PostgreSQL数据库中

优点:

1.服务采用插件化方式，鲁棒性较强

2.可模拟诸多常见IOT协议

缺点

1.无法有效模拟真实设备，只能提供简单服务

现有的框架下，攻击payload都是现成开发好的模块，无法模拟设备进程。如何对该框架进行二次开发，将设备模拟功能添加，感兴趣的小伙伴可以思考下。

# 七. 参考

https://github.com/aau-network-security/riotpot


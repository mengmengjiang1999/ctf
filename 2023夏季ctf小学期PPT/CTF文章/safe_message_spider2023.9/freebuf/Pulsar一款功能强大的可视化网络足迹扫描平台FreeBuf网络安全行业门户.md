![](https://image.3001.net/images/20200404/1585992168_5e8851e8b8290.png!small)

## Pulsar

Pulsar是一款专为红队研究人员、渗透测试人员和Bug
Hunter们设计的自动化网络足迹扫描平台，该工具可以帮助我们在对目标组织基础设施了解不多的情况下，尽可能多地发现组织面向外部的资产。在实现网络数据可视化的同时，Pulsar还可以给出针对目标的基础脆弱性评分，并试图找出基础设施中的薄弱点及其与其他资源之间的关系。除此之外，它还可以当作自定义漏洞扫描程序来扫描大规模范围或未知范围的安全问题。值得一提的是，Pulsar是100%免费的，不需要任何API密钥就可以直接使用它的全部功能。

## 核心功能

> 1、子域名扫描与发现
>
> 2、云资源发现
>
> 3、基础漏洞扫描
>
> 4、扫描策略和优化
>
> 5、数据可视化
>
> 6、协作和数据导出
>
> 7、计划和通知
>
> 8、REST API支持
>
> 9、外部API集成
>
> 10、OAUTH集成
>
> 11、自定义扫描器扩展

## 整合的项目

> 1、[OWASP Amass](https://owasp.org/www-project-amass/)
>
> 2、[Nmap](https://nmap.org/)
>
> 3、[RIPEstat API](https://stat.ripe.net/docs/data_api)
>
> 4、[CloudEnum](https://github.com/initstring/cloud_enum)
>
> 5、[SSH Audit](https://github.com/arthepsy/ssh-audit)
>
> 6、[WhatWeb](https://github.com/urbanadventurer/WhatWeb)
>
> 7、[NVD Data Feed](https://nvd.nist.gov/vuln/data-feeds)

## 工具安装

如果你想要使用外部API，请参考【[ _这篇文档_](https://www.freebuf.com/wp-admin/post.php?post=232520&action=edit#external-apis-integration)】。

如需使用电子邮件提醒，请在工具安装之前编辑portal/portal/settings.py文件中的EMAIL_BACKEND SETTINGS参数。

### Windows安装

 **依赖要求**

1、Git-tools：点击【[ _这里_](https://gitforwindows.org/)】完成下载和安装。

2、Docker引擎和Docker-Compose：

> Docker安装请参考【[ _这里_](https://docs.docker.com/ee/docker-ee/windows/docker-> ee/)】。
>
> Docker-Compose安装请参考【[ _这里_](https://docs.docker.com/compose/install/)】。

 **安装操作**

首先，使用下列命令将最新版本的Pulsar项目源码克隆至本地：

    
    
    git clone https://github.com/FooBallZ/pulsar

接下来切换到项目目录中，运行PowerShell安装器：

    
    
    PS> .\install.ps1

然后，按照安装器指令完成工具安装。这里，你需要确保将生成的密码存储好，管理员密码可以在/admin/中的Django管理员控制台中修改。

最后，访问<https://localhost:8443/>以登录Pulsar控制台，并生成默认凭证。

### Linux安装

 **依赖要求**

1、Git-tools-使用包管理工具安装git：

    
    
    sudo apt install git

2、Docker引擎和Docker-Compose：

> Docker安装请参考【[ _这里_](https://docs.docker.com/install/linux/docker-> ce/debian/)】。
>
> Docker-Compose安装请参考【[ _这里_](https://docs.docker.com/compose/install/)】。

 **安装操作**

首先，使用下列命令将最新版本的Pulsar项目源码克隆至本地：

    
    
    git clone https://github.com/FooBallZ/pulsar

接下来切换到项目目录中，运行Bash安装器：

    
    
    # ./install.sh

然后，按照安装器指令完成工具安装。这里，你需要确保将生成的密码存储好，管理员密码可以在/admin/中的Django管理员控制台中修改。

最后，访问<https://localhost:8443/>以登录Pulsar控制台，并生成默认凭证。

## 工具使用

建议的工作流如下：

> 1、从向控制台添加新资产开始
>
> 2、运行被动发现扫描任务（已禁用主动选项）
>
> 3、在“网络”选项卡中标记所有误报
>
> 4、运行主动扫描
>
> 5、查看和导出扫描结果
>
> 6、在启用重复扫描的情况下再次运行定期扫描

### 资产查看

![](https://image.3001.net/images/20200404/1585992244_5e8852347a572.png!small)

### 添加资产

点击“Add”按钮，创建新资产对象，新资产定义包括：

> 1、名称-组织机构短名称；
>
> 2、域名-根域名，用于开启枚举任务；

### 扫描资产

点击“Scan”按钮，初始化扫描进程，并打开下列策略配置窗口：

![](https://image.3001.net/images/20200404/1585992268_5e88524c75953.png!small)

### 导出资产

点击“Export”按钮，即可将数据以下列格式导出：

> CSV
>
> JSON
>
> MARKDOWN
>
> PDF

### 自定义扫描插件

插件样本配置如下：

![](https://image.3001.net/images/20200404/1585992284_5e88525c1879e.png!small)

### 自定义扫描设置和变量

类似Nmap扫描标记之类的设置可以在portal/pulsar/modules/scanner_utils.py文件中的scan_settings变量中进行配置：

    
    
    scan_settings = {
    
    'heavy_processes': ['amass', 'zdns'], # consider Nmap
    
    'cmd_timeout': '2h', # linux timeout syntax i.e. 10s 10m 10h 10d
    
    'nmap_host_timeout': '10m',
    
    'amass_timeout': '20',
    
    'amass_flags': '-noalts ',
    
    'nmap_tcp_flags': '-Pn -n -sS -vv',
    
    'nmap_udp_flags': '-Pn -n -sU -vv',
    
    'resolvers': '1.1.1.1:53,8.8.8.8:53,64.6.64.6:53,74.82.42.42:53,1.0.0.1:53,8.8.4.4:53,64.6.65.6:53'
    
    }

### 协作组

Django管理员控制台中的协作组允许我们创建一个协同工作组并同时支持多用户访问资产对象。配置协作组，需要完成下列两个步骤的操作。

首先，创建一个新的协作组，然后分配用户和角色：

![](https://image.3001.net/images/20200404/1585992310_5e8852762de92.png!small)

接下来，为协作组分配资产：

![](https://image.3001.net/images/20200404/1585992316_5e88527c50bb4.png!small)

## 工具架构

Pulsar是一个基于Docker-Compose文件的平台即服务产品，它的实现架构是可以轻松扩展的，并能够兼容和部署到多种常见云端环境中。

其中的Docker容器架构如下:

![](https://image.3001.net/images/20200404/1585992333_5e88528d653d8.jpg!small)

## 项目地址

> Pulsar：【[ _GitHub传送门_](https://github.com/FooBallZ/pulsar)】

 *** 参考来源：[
_FooBallZ_](https://github.com/FooBallZ/pulsar)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


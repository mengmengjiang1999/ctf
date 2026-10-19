![](https://image.3001.net/images/20210823/1629726936_6123a8d8e59daebeba329.png!small)

## 关于MacHound

MacHound是Bloodhound审计工具的一个扩展组件，可以帮助广大研究人员收集和分析macOS主机上活动目录之间的关系。MacHound还可以收集macOS设备上已登录用户和管理员组成员的相关信息，并将这些信息存储至Bloodhound数据库中。除了使用HasSession和AdminTo之外，MacHound还可以向Bloodhound数据库中添加其他内容：

CanSSH：允许连接主机的实体（SSH）；

CanVNC：允许连接主机的实体（VNC）；

CanAE：允许在主机上执行AppleEvent脚本的实体；

## 数据收集

### 已登录用户（HassSession）

MacHound使用了utmpx API来查询当前活动用户，并使用OpenDirectory和成员API验证活动目录用户。

### 管理员组

MacHound能够收集下列本地管理员组的活动目录成员：

    
    
    admin
    
    com.apple.access_ssh
    
    com.apple.remote_ae
    
    com.apple.access_screensharing

## 组件

MacHound主要由两大组件构成：即收集器和注入器。

### 收集器（Collector）

MacHound的收集器是一个Python
3.7脚本，可以在加入了活动目录的macOS主机上运行。收集器负责查询本地OpenDirectory和活动目录，以及特权用户和组的相关信息。数据输出是一个JSON文件，其中将包含所有收集到的信息。

### 注入器（Ingestor）

MacHound的注入器也是一个Python
3.7脚本，它负责解析数据的JSON文件，并与Neo4J数据库连接，然后将数据注入至数据库中。注入器使用了Neo4J的Python库来从Neo4J数据库来查询信息，注入器必须在能够跟Neo4J数据库建立TCP连接的主机上运行。

## 工具要求

MacHound需要在主机上安装并配置好Python 3.7环境，并且注入器需要Python 3.7版本的Neo4J库。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/XMCyber/MacHound.git

## 工具使用

收集器默认不需要使用任何参数即可完成所有的信息查询，并将数据输出至./output.json。收集器必须以root用户权限运行：

    
    
    collector.py -o <output_file> -c <Admin,CanSSH,CanVNC,CanAE,HasSession> [-v] [-l log_file_path]

### 注入器

注入器必须部署在能够跟Bloodhound的Neo4J数据库建立TCP连接的主机上运行，最好是将Neo4J数据库部署在本地服务器上，以避免安全风险。注入器需要安装Python版的Neo4J驱动程序。

    
    
    ingestor.py <url_to_neo4j> -u <username> -p <password> -i <json_folder>

## 许可证协议

本项目的开发与发布遵循GPL-3.0开源许可证协议。

## 项目地址

 **MacHound：** 【[ _GitHub传送门_](https://github.com/XMCyber/MacHound)】


![](https://image.3001.net/images/20190924/1569298451_5d899813cc7cf.png!small)

## 背景

**对于任何一个安全工程师来说，在确保网络安全之前首先了解他们的网络是至关重要的，但这并不是一项轻松的任务且耗时耗力。在中大型组织的网络中，如果没有网络架构图，则相当于掉落到了一个“盲”的世界，而采用手动验证的方式更是不切实际。因此，为了确保整个网络的安全，重要的是对所有连接到你网络的系统有一个全面的了解，而不论其类型，功能，技术等。**

## 简介

LetsMapYourNetwork（LMYN）是一款物理网络可视化工具，其旨在为安全工程师和网络管理员提供易于使用的界面，以图形形式显示其网络，而无需手动操作，其中一个节点表示一个系统，而节点之间的关系表示连接。

LMYN分两个阶段进行：

学习：在此阶段，LMYN通过执行网络命令并查询API来“学习”网络，然后利用响应来构建图形数据库。用户可以在任意时间执行任意学习活动，LMYN会将结果合并到现有数据库中。

监视：这是一个连续的过程，其中LMYN会监视“范围内（in-scope）”网络的任何更改，将其与现有信息进行对比，并相应地更新图形数据库。

该工具中使用了以下技术：

> Django Python
>
> Neo4j DB
>
> Sigma JS
>
> Celery and RabbitMQ

## 优点

以图形的形式可视化基础架构网络，使其更“可见”，为安全工程师和网络管理员提供了良好的分析和对关键领域的绝对关注。

另外，“Let’s Map Your
Network”完全基于实际网络一部分的“种子”系统执行的网络操作或通过查询API来制图。因此，在网络映射中不会出现人为错误。

## 在哪使用

> 网络架构“验证”
>
> 网络管理员故障排除
>
> 内部网络漏洞评估和渗透测试

## 相关演示

[BlackHatEurope2018
演示幻灯片](https://github.com/varchashva/LetsMapYourNetwork/blob/master/docs/LetsMapYourNetwork_BlackHat.pdf)

[演示视频](https://www.%2A%2A%2A%2A%2A%2A%2A.com/channel/UC77eNGlIzjGL0fgx3i6Hcyw)

## 主要特性

### 1\. 项目管理

用户可以创建和删除多个项目，从不同角度查看同一网络和/或同时分析多个网络

在一个项目中，所有学习活动的结果将被整理成一个单一的视图，从而提供网络的整体视图

### 2\. 现有CMDB的批量加载

用户可以将其现有的CMDB文件上传到LMYN中，它将为实际网络提供“增量（delta）”

因此，LMYN将提供其CMDB中而非网络中的隔离，反之亦然，以便用户对恶意系统采取措施

对于不同类型的系统，它使用不同的颜色代码方案，例如，在网络中运行但未在CMDB中显示的系统将显示为红色节点

### 3\. 执行按需网络活动的能力

除了上传CMDB文件，用户还可以对任意项目执行以下网络活动：

跟踪路由到任意目标主机

对任何IP和/或范围进行网络扫描（接受所有已知的IP格式）

LMYN将整合上述执行结果到同一项目中，以构建网络

### 4\. 云（AWS）支持

LMYN从AWS API获取拓扑信息，例如VPC，子网，对等操作（Peering），Internet网关等，并以图形形式表示

LMYN将AWS网络进行逻辑隔离，将其划分为“区域> VPC>子网>实例（Regions > VPCs > Subnets >
Instances）”，并相应地对它们进行分组

### 5\. 枚举

LMYN将执行多个枚举探针来识别操作系统和设备类型，以及网络构建时间

对于AWS，LMYN将通过查询AWS API来获取实例信息，例如平台，状态，VPC，子网等。

如果枚举成功，则LMYN将为每个节点分配一个相关的图标

### 6\. 仅分析“感兴趣”网络的能力

一旦用户使用多个活动（CMDB上传，ad-hoc网络活动，云扫描，枚举）构建网络，那么用户只能从UI部分的整个数据库中筛选出“感兴趣”的网络

可以根据基本操作（例如IP范围，目标主机）或枚举详细信息（Linux，Windows，路由器，VPC，子网，状态等）执行过滤。

过滤过程允许执行“与”和“或”类运算，例如 “all IP in range 192.168.1.1/24 and Windows”

过滤过程允许用户在数据库中输入所有信息，并在运行时决定用户所看到的内容

### 7\. 持续监控

此外，LMYN还可以监视一段时间内的任何现有网络

用户可以以图形的形式识别他们的网络是如何变化的（哪些系统正在断开连接到网络）

LMYN同样会利用颜色代码方案，来隔离网络中不同类型的系统，例如所有不活动的节点将显示为灰色

### 8\. 后端活动和用户界面的隔离

LMYN通过UI在功能上隔离后端活动

LMYN具有Celery和RabbitMQ的实现；因此，无论背景活动如何，用户都能够拥有一个无缝的UI

LMYN会跟踪所有后台活动的状态并定期更新UI

### 9.Docker支持

所有这些都可以在docker中实现

## 安装

使用 DockerHub - 仅 Linux

1\. 安装[docker & docker-compose](https://docs.docker.com/install/linux/docker-ce/debian/#install-using-the-repository)

sudo apt-get update

sudo apt-get install docker-ce docker-compose

2\.
wget<https://raw.githubusercontent.com/varchashva/LetsMapYourNetwork/master/docker-compose.yml>

3\. docker-compose up

4\. 在浏览器中打开<http://localhost:9999/core>

### 对于 Windows 用户

1\. 从GitHub下载LMYN并提取所有内容。建议在Python主目录中提取例如C:\python\LMYN ($LMYN_HOME)

2\. 安装python

转到python[下载](https://www.python.org/downloads/release/python-2715)部分，然后单击[Windows
x86 MSI installer for
32-bit](https://www.python.org/ftp/python/2.7.15/python-2.7.15.msi)或[Windows
x86-64 MSI installer for 64-bit
user](https://www.python.org/ftp/python/2.7.15/python-2.7.15.amd64.msi)

使用所有默认设置安装下载的python文件

3\. 从此处下载[nmap](https://nmap.org/dist/nmap-7.70-setup.exe)并使用所有默认设置进行安装

4\. 下载RabbitMQ-Server并使用所有默认设置进行安装

5\. 安装Microsoft Visual Studio C++

32位用户仅安装[VC
setup](http://download.microsoft.com/download/A/5/4/A54BADB6-9C3F-478D-8657-93B3FC9FE62D/vcsetup.exe)，且所有可选产品UNCHECKED

64位用户使用默认设置安装Windows SDK和.NET Framework

6\. 安装Oracle JDK 8（这是安装和运行Neo4j数据库的先决条件）

在命令提示符下运行命令java -version

如果输出包含版本详细信息，则跳至Neo4j安装，否则继续Java的安装

转到Oracle[下载](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)部分，并使用所有默认设置安装JDK
8

转到JRE的安装目录（例如C:/Program
files/java/jre7/bin），并创建一个文件夹“server”，然后将“client”文件夹的所有内容复制到“server”文件夹

7\. 转到Neo4j[下载](https://neo4j.com/download-center/#releases)部分

选择“Community Server”部分并[下载Windows版本](https://go.neo4j.com/download-thanks.html?edition=community&release=3.4.6&flavour=winzip&_ga=2.141706682.946316120.1534600164-1297405808.1534400604)

右键单击下载的文件，然后解压缩到C:\neo4j目录（具体目录根据你的实际情况而定）

使用管理员权限打开命令提示符，然后cd到提取目录，例如cd C:\neo4j

运行命令bin\neo4j console启动neo4j服务器

浏览到Neo4j Web
console（[http://localhost:7474](http://localhost:7474/)），将默认密码neo4j更改为Neo4j

如有需要，请参考[Neo4j安装指南](https://neo4j.com/docs/operations-manual/current/installation/)。

8\. 使用管理权限打开命令提示符，并浏览到Python主目录，例如cd C:\python

运行命令python -m pip install --trusted-host pypi.python.org
-r$LMYN/LetsMapYourNetwork/requirements.txt

9\. 运行RabbitMQ Server服务，如下

从Windows的“开始”菜单中，选择“All Programs > RabbitMQ Server > Start
Service启动RabbitMQ服务器。

10\. 从$LMYN_HOME目录运行Celery，如下

celery -A LetsMapYourNetwork -l warning

11\. 使用具有管理员权限的相同命令提示符，从Python主目录

运行命令python $LMYN_HOME\LetsMapYourNetwork\manage.py runserver 0.0.0.0:9999
--insecure

12\. 在浏览器中打开<http://localhost:9999/core>

### 了解颜色和节点符号的含义

![](https://camo.githubusercontent.com/3931ac26699d30cf8772a4d0f1586798ab91efa5/68747470733a2f2f706c616365686f6c642e69742f31352f3333333366662f3030303030303f746578743d2b)

#3333ff

这是 SEED 节点

![](https://camo.githubusercontent.com/180b79fbb5403fdc7bb8cf217af065ca271aa662/68747470733a2f2f706c616365686f6c642e69742f31352f3339373161632f3030303030303f746578743d2b)

#3971ac

节点具有外部（公共）IP

![](https://camo.githubusercontent.com/b350dd3c765a9368f855545a4db76a961d3001fc/68747470733a2f2f706c616365686f6c642e69742f31352f3230413844382f3030303030303f746578743d2b)

#20A8D8

节点具有内部（私有）IP

![](https://camo.githubusercontent.com/a9c11549647bd305117676aaf2fad24a48b4c588/68747470733a2f2f706c616365686f6c642e69742f31352f3030393930302f3030303030303f746578743d2b)

#009900

节点存在于CMDB文件中并且处于活动状态

![](https://camo.githubusercontent.com/95e074ae6372e1c80148338998d7217dd3421a46/68747470733a2f2f706c616365686f6c642e69742f31352f6536303030302f3030303030303f746578743d2b)

#e60000

节点存在于CMDB文件中但处于非活动状态

![](https://camo.githubusercontent.com/58a6266c77d2266687f123be9e1f9701369d2f3d/68747470733a2f2f706c616365686f6c642e69742f31352f6136613661362f3030303030303f746578743d2b)

#a6a6a6

此时节点已关闭

![](https://camo.githubusercontent.com/58d9f6abd5754bcb9e719ce7722a81c3984e7679/68747470733a2f2f706c616365686f6c642e69742f31352f6536653665362f3030303030303f746578743d2b)

#e6e6e6

节点是嵌入式路由器或VPC对等体

## LMYN 应用示例

本地子网

![](https://image.3001.net/images/20190924/1569298492_5d89983ccd260.jpg!small)

踪路由到多个目标的网络

![](https://image.3001.net/images/20190924/1569298500_5d899844808ac.jpg!small)

CMDB 上传

![](https://image.3001.net/images/20190924/1569298508_5d89984c6103f.jpg!small)

云网络

![](https://image.3001.net/images/20190924/1569298552_5d8998782526e.jpg!small)

## 联系我

> Email：varchashva [at] gmail [dot] com
>
> LinkedIn：<https://www.linkedin.com/in/pramod-rana-696ba062>
>
> Twitter：<https://twitter.com/IAmVarchashva>

***参考来源：[GitHub](https://github.com/varchashva/LetsMapYourNetwork)，FB小编secist编译，转载请注明来自FreeBuf.COM**


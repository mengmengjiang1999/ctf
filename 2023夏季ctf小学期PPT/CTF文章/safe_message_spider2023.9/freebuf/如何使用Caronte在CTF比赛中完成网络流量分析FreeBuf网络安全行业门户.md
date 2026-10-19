![](https://image.3001.net/images/20210609/1623221014_60c06316123629571e2eb.jpg!small)

## 关于Caronte

Caronte是一款功能强大的网络流量分析工具，可以帮助广大研究人员在CTF比赛或其他网络攻击/防御活动中对捕捉到的网络流量进行分析。该工具能够重新组装pcap文件中捕获的TCP数据包以重建TCP连接，并分析每个连接以查找用户定义的模式。这里所谓的模式，支持用户使用正则表达式或特定于协议的规则来进行定义。分析过程中的连接流将会存储至数据库中，并可以通过Web应用程序以可视化的形式访问。除此之外，Caronte还提供了非常实用的REST
API。

## 功能介绍

支持Docker-Compose，可立即安装使用；

无需配置文件，可通过GUI或API修改配置；

可通过curl或GUI加载待分析的pcap文件；

支持包含特定字符串的规则以识别连接；

可通过服务类型对连接进行标识；

可通过地址、端口、时间和匹配规则等过滤特定连接；

通过时间轴显示每分钟的分析统计；

支持正则表达式搜索；

可对检测到的HTTP连接进行自动化重组；

可通过多种形式查看或导出连接内容；

在JSON树状图查看器中显示JSON内容，在独立窗口中呈现HTML代码；

连接内容视图中高亮显示匹配规则的内容；

支持IPv4和IPv6；

## 工具安装

目前有两种方法来安装Caronte：

> 使用Docker和Docker-Compose，最简单也最快速；
>
> 手动安装依赖组件并编译项目；

### 使用Docker安装

首先，将该项目源码克隆至本地：

    
    
    git clone https://github.com/eciavatta/caronte.git

在命令行终端中，切换到项目根目录，然后运行下列命令：

    
    
    docker-compose up -d

等待镜像编译完成之后，就可以在浏览器中访问“http://localhost:3333”以使用Caronte了。

### 手动安装

首先，我们需要安装好下列依赖组件：

> go >= 1.14 https://golang.org/doc/install
>
> node >= v12 https://nodejs.org/it/download/
>
> yarnpkg https://classic.yarnpkg.com/en/docs/install/
>
> hyperscan >= v5 https://www.hyperscan.io/downloads/

接下来，我们需要手动编译项目，该操作分成两部分：

 **后端：使用下列命令编译：**

    
    
    go mod download && go build

 **前端：使用下列命令编译：**

    
    
    cd frontend && yarn install && yarn build

在运行Caronte之前，还需要开启一个MongoDB实例。【[
_参考资料_](https://docs.mongodb.com/manual/administration/install-community/)】

接下来，使用“./caronte”命令运行代码，可用选项如下：

    
    
    -bind-address    address where server is bind (default "0.0.0.0")
    
    -bind-port       port where server is bind (default 3333)
    
    -db-name         name of database to use (default "caronte")
    
    -mongo-host      address of MongoDB (default "localhost")
    
    -mongo-port      port of MongoDB (default 27017)

## 工具运行截图

### 工具主窗口，包含连接列表和数据流内容

![](https://image.3001.net/images/20210609/1623221101_60c0636d5804551c84b99.png!small)

### 工具主窗口，包含时间轴详情

![](https://image.3001.net/images/20210609/1623221107_60c06373cc2b320296a77.png!small)

### 规则和服务查看

![](https://image.3001.net/images/20210609/1623221115_60c0637b340510e0c87f3.png!small)

### 搜索和pcap查看

![](https://image.3001.net/images/20210609/1623221121_60c0638181f336efffc1f.png!small)

## 项目地址

 **Caronte：** 【[ _GitHub传送门_](https://github.com/eciavatta/caronte)】

## 许可证协议

本项目由[ _Emiliano Ciavatta_](https://eciavatta.dev/)开发与发布，并遵循[
_GPL-3.0_](https://github.com/eciavatta/caronte/blob/main/LICENSE)开源许可证协议。

## 参考资料

[ _https://docs.mongodb.com/manual/administration/install-community/_](https://docs.mongodb.com/manual/administration/install-community/)

[ _https://app.swaggerhub.com/apis-docs/eciavatta/caronte/WIP_](https://app.swaggerhub.com/apis-docs/eciavatta/caronte/WIP)

[ _https://golang.org/doc/install_](https://golang.org/doc/install)

[ _https://nodejs.org/it/download/_](https://nodejs.org/it/download/)

[
_https://classic.yarnpkg.com/en/docs/install/﻿_](https://classic.yarnpkg.com/en/docs/install/)

[ _https://www.hyperscan.io/downloads/﻿_](https://www.hyperscan.io/downloads/)


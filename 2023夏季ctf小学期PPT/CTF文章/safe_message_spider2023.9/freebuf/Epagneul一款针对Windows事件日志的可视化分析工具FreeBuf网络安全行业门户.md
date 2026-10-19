## 关于Epagneul

Epagneul是一款针对Windows事件日志的可视化分析工具，可以帮助广大研究人员以可视化图形的方式查看、分析和审计Windows事件日志。

## 工具体系架构

该工具的 整体运行机制和体系架构如下图所示：

![](https://image.3001.net/images/20220325/1648139689_623c9da98c8463ecf3c19.png!small)

## 工具组件

> [ _Vue.js_](https://v3.vuejs.org/)：该工具所使用的Web框架
>
> [ _Cytoscape.js_](https://js.cytoscape.org/)：该工具所使用的图形可视化和分析库
>
> [ _d3_](https://d3js.org/)：用于显示事件时间轴
>
> [ _neo4j_](https://neo4j.com/)：后端数据库
>
> [ _evtx_](https://github.com/omerbenamram/evtx)：解析Windows XML事件日志格式

## 工具要求

该工具的运行需要在本地设备上安装并配置好Docker和Docker-compose。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/jurelou/epagneul.git

## 工具安装

接下来，切换到项目根目录下，然后运行下列命令进行项目构建：

    
    
    make

### 离线部署

我们可以使用下列命令，在一台联网设备上构建Epagneul的离线版本：

    
    
    make release

上述命令将会在项目目录中创建一个名为“release”的目录，其中将包含可以直接使用的Docker镜像。我们可以把它拷贝到空气间隙设备上，然后云心下列命令：

    
    
    make load
    
    make

上述命令将安装下列工具组件：

> 1、Epagneul Web UI（8080端口）
>
> 2、Epagneul后端（8080端口）
>
> 3、Neo4j（7474端口）

## 项目地址

 **Epagneul：** 【[ _GitHub传送门_](https://github.com/jurelou/epagneul)】

## 参考资料

> [ _https://adsecurity.org/wp-content/uploads/2017/04/2017-BSidesCharm-> DetectingtheElusive-ActiveDirectoryThreatHunting-> Final.pdf_](https://adsecurity.org/wp-> content/uploads/2017/04/2017-BSidesCharm-DetectingtheElusive-> ActiveDirectoryThreatHunting-Final.pdf)
>
> [
> _https://github.com/JPCERTCC/LogonTracer_](https://github.com/JPCERTCC/LogonTracer)
>
> [ _https://github.com/ahmedkhlief/APT-> Hunter_](https://github.com/ahmedkhlief/APT-Hunter)


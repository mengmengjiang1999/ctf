![](https://image.3001.net/images/20200108/1578477499_5e15a7bb0875e.png!small)

##  MultiScanner介绍

**MultiScanner是一款功能强大的文件分析框架，可帮助用户自动化对大量文件集进行分析，并聚合输出分析结果。MultiScanner**了自定义构建的Python脚本、Web
API以及多个软件工具，而这些工具组件可以在MultiScanner中以模块的形式进行功能和并。**

这些模块可以允许开发人员快速完成自定义配置，并且可以轻松集成到框架之中。当前该项目中编写和维护的模块大部分都跟恶意软件分析相关，但该框架并不仅限此范围。有关模块列表，可以在modules/中查找。可以在“分析模块”页面中找到相关的描述和配置选项。

MultiScanner还支持分布式工作流，其中涵盖样本存储、分析和报告查看等等。除此之外，框架还提供了web界面、REST
API、分布式文件系统（GlusterFS）、分布式报表存储/搜索（Elasticsearch）和分布式任务管理（celeri/RabbitMQ）。

###  工具使用

MultiScanner能够以命令行接口、Python API和分布式系统的方式来使用。

###  命令行形式

首先，安装Python v2.7或3.4+，接下来，运行下列命令：

    
    
    $ git clone <https://github.com/mitre/multiscanner.git>
    
        $ cd multiscanner
    
        $ sudo -HE ./install.sh
    
        $ multiscanner init

上述命令将会生成一套默认配置，用户可以在config.ini中查看已启用的模块。

现在，我们就可以使用下列命令来扫描目标文件了，其中<file>参数为需要扫描的文件路径：

    
    
    $ multiscanner <file>

广大用户可以使用下列命令获取MultiScanner所有的命令行选项：

    
    
    $ multiscanner --help

注意，如果你使用的不是RedHat或Debian等Linux发行版，那么你需要使用pip完成安装：

    
    
    $ pip install -r requirements.txt

###  Python API

    
    
    import multiscanner
    
        multiscanner.config_init(filepath)
    
        output = multiscanner.multiscan(file_list)
    
        results = multiscanner.parse_reports(output, python=True)

###  Web接口

首先，安装最新版本的[Docker](https://docs.docker.com/engine/installation/)以及[Docker
Compose](https://docs.docker.com/compose/install/)：

    
    
    $ git clone <https://github.com/mitre/multiscanner.git>
    
        $ cd multiscanner
    
        $ docker-compose up

##  工具配置

有些用户想要使用MultiScanner框架、Web
UI和REST，我们专门构建了一个单独的Docker应用程序，经过简单的环境配置后，广大用户就可以轻松使用MultiScanner框架了：

    
    
    $ docker-compose up

上述命令将会构建必要的容器组件，接下来运行下列命令：

    
    
    api_1      |  * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)

安装完成之后，等待所有的服务开始运行，然后用户就可以使用Web浏览器并访问[http://localhost:8000](http://localhost:8000/)来使用MultiScanner了。

###  配置参数

MultiScanner以及其模块可以通过配置文件config.ini来进行配置，下列给出的是MultiScanner的参数配置列表：

**参数** |  **描述**  
---|---  
**copyfilesto** |  该参数可以让脚本复制每一个要扫描的文件，可以将其将其删除或设置为False以禁用此功能。  
**group-types** |  该参数可以指定一种分析类型，用于将报表分组为多个部分。可以将其删除或设置为False以禁用此功能。  
**storage-config** |  存储配置文件的路径  
**api-config** |  API配置文件的路径  
**web-config** |  Web UI配置文件的路径  
  
##  项目地址

MultiScanner：【[GitHub传送门](https://github.com/mitre/multiscanner)】

 ***
参考来源：[mitre](https://github.com/mitre/multiscanner)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


**今天给大家介绍的是一款名叫Armory的开源工具，该工具可以从多款安全工具中检索和获取大量外部数据，然后将这些数据存储到数据库中，并对数据进行关联处理。**

![1.png](https://image.3001.net/images/20190405/1554448388_5ca70004624b7.png!small)

## 工具介绍

Armory可以从多款安全工具中检索和获取大量外部数据，然后将这些数据存储到数据库中，并对数据进行关联处理。该工具的主要功能是获取多款工具的输出结果，并将其中有价值的数据提供给其他工具，而不是要替换掉某些特定工具。

除此之外，Armory具有高扩展性，广大研究人员可以根据自己的需要来开发功能模块，并以自己期望的格式来导出数据或生成分析报告。

## 工具安装

### 依赖组件

首先，我们需要搭建好虚拟环境，我个人使用的是virtualenvwrapper：【[传送门](http://virtualenvwrapper.readthedocs.io/en/latest/install.html)】

### 安装Armory

将代码库克隆到本地：

    
    
    git clone https://github.com/depthsecurity/armory

安装模块：

    
    
    python setup.py install

为了在工具目录下创建默认的配置目录“~/.armory“和配置文件“settings.ini”，并配置好每一个功能模块，用户需要先运行一次armory。

接下来，用户需要编辑“settings.ini”配置文件并修改base_path选项。该参数需要指向工具目录的根路径。工具模块生成的所有文件都会存放在这个路径下，包括sqlite3数据库。

## 工具使用

该工具的使用分为“功能模块“和“数据报告”这两个部分。

### 功能模块

Armory的功能模块负责运行工具主程序，分析筛选数据，并将最终的数据写入到数据库中。用户可以使用下列命令查看可用的功能模块：

    
    
    armory –lm

模块选项查看：

    
    
    armory -m <module> -M

### 数据报告

数据报告功能的使用跟功能模块的差不多，但数据报告模块的主要功能是从数据库中获取数据，并将其以用户需要的格式进行显示或导出。用户可以使用下列命令查看可用的报告格式：

    
    
    armory –lr

模块选项查看：

    
    
    armory -r <report> -R

## 交互式Shell

该工具还提供了交互式Shell，该功能基于IPython实现，可帮助研究人员运行特定命令或修改数据库值。运行命令如下：

    
    
    armory -shell

默认配置可使用的命令如下：Domain、BaseDomains、IPAddresses、CIDRs、Users、Creds、Vulns、Ports、Urls、ScopeCIDRs。

***参考来源：[depthsecurity](https://github.com/depthsecurity/armory)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


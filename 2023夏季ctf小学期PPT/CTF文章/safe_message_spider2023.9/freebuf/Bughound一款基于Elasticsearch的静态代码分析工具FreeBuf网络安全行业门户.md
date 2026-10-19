![](https://image.3001.net/images/20210828/1630152201_612a26093ef3afabd5256.png!small)

## 关于Bughound

Bughound是一款开源的静态代码分析工具，可以帮助广大研究人员分析自己的代码，并将结果发送至Elasticsearch和Kibana，以更好地审查代码中潜在的安全漏洞。

Bughound拥有自己的Elasticsearch和Kibana
Docker镜像，并且经过预配制，提供了仪表盘，可以更好地以可视化的形式查看代码安全问题。

 **我们可以使用Bughound检测多种类型的漏洞，其中包括：**

> 命令注入
>
> XXE
>
> 不安全的反序列化
>
> 其他

Bughound目前仅支持分析PHP和Java代码，并且包含了一组针对这些语言的不安全函数。开发人员会在将来增加更多的语言和函数支持。

## 工具要求

首先，我们需要使用下列命令安装运行Bughound所需的全部依赖组件：

    
    
    pip3 install -r requirements.txt

除此之外，为了运行Bugbound镜像，你还需要安装好[
_Docker_](https://docs.docker.com/engine/install/)。

## 工具安装

广大研究人员可以使用下列命令来安装最新版本的Bughound：

    
    
    git clone https://github.com/mhaskar/Bughound

上述步骤操作完成之后，我们就可以使用下列命令来运行Bughound了：

    
    
    ./bughound.py

运行脚本之后，你将会看到如下所示的操作界面：

    
    
    ┌─[askar@hackbook]─[/opt/bughound]
    
    └──╼ $./bughound.py
    
     
    
    .______    __    __    _______  __    __    ______    __    __  .__   __.  _______
    
    |   _  \  |  |  |  |  /  _____||  |  |  |  /  __  \  |  |  |  | |  \ |  | |       \
    
    |  |_)  | |  |  |  | |  |  __  |  |__|  | |  |  |  | |  |  |  | |   \|  | |  .--.  |
    
    |   _  <  |  |  |  | |  | |_ | |   __   | |  |  |  | |  |  |  | |  . `  | |  |  |  |
    
    |  |_)  | |  `--'  | |  |__| | |  |  |  | |  `--'  | |  `--'  | |  |\   | |  '--'  |
    
    |______/   \______/   \______| |__|  |__|  \______/   \______/  |__| \__| |_______/
    
     
    
     
    
     
    
              \ /
    
              oVo
    
          \___XXX___/
    
           __XXXXX__
    
          /__XXXXX__\
    
          /   XXX   \
    
               V                  V1.0 Beta
    
     
    
    [+] Example: ./bughound3.py --path vulnerable_code/ --language php --extension .php --name testproject
    
     
    
    usage: bughound.py [-h] [--path PATH] [--git GIT] --language LANGUAGE
    
                       --extension EXTENSION --name NAME [--verbose [VERBOSE]]
    
    bughound.py: error: argument --language is required
    
    ┌─[✗]─[askar@hackbook]─[/opt/bughound]
    
    └──╼ $

### Docker镜像安装

如需安装Bughound Docker镜像，可以直接运行下列命令：

    
    
    docker pull bughound/bughound

上述命令将会远程拉取最新版本的Bughound镜像，并存储至你的计算机中。

接下来，使用下列命令来运行镜像：

    
    
    docker run --name bughound -p5601:5601 -p 9200:9200 bughound/bughound

如果你需要增加最大虚拟内存的话，可以使用下列命令：

    
    
    sysctl -w vm.max_map_count=262144

## 工具使用

如需开始分析代码，你应该使用Bughound.py，该脚本提供了很多操作选项：

    
    
    ┌─[✗]─[askar@hackbook]─[/opt/bughound]
    
    └──╼ $./bughound.py -h
    
     
    
    .______    __    __    _______  __    __    ______    __    __  .__   __.  _______
    
    |   _  \  |  |  |  |  /  _____||  |  |  |  /  __  \  |  |  |  | |  \ |  | |       \
    
    |  |_)  | |  |  |  | |  |  __  |  |__|  | |  |  |  | |  |  |  | |   \|  | |  .--.  |
    
    |   _  <  |  |  |  | |  | |_ | |   __   | |  |  |  | |  |  |  | |  . `  | |  |  |  |
    
    |  |_)  | |  `--'  | |  |__| | |  |  |  | |  `--'  | |  `--'  | |  |\   | |  '--'  |
    
    |______/   \______/   \______| |__|  |__|  \______/   \______/  |__| \__| |_______/
    
     
    
     
    
     
    
              \ /
    
              oVo
    
          \___XXX___/
    
           __XXXXX__
    
          /__XXXXX__\
    
          /   XXX   \
    
               V                  V1.0 Beta
    
     
    
    [+] Example: ./bughound3.py --path vulnerable_code/ --language php --extension .php --name testproject
    
     
    
    usage: bughound.py [-h] [--path PATH] [--git GIT] --language LANGUAGE
    
                       --extension EXTENSION --name NAME [--verbose [VERBOSE]]
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      --path PATH           local path of the source code
    
      --git GIT             git repository URL
    
      --language LANGUAGE   the used programming language
    
      --extension EXTENSION
    
                            extension to search for
    
      --name NAME           project name to use
    
      --verbose [VERBOSE]   show debugging messages
    
    ┌─[askar@hackbook]─[/opt/bughound]
    
    └──╼ $

### 扫描本地项目

比如说，你想要扫描一个本地PHP项目，你可以使用下列命令：

    
    
    ./bughound.py --path /opt/dummyproject --language php --extension .php --name dummyproject

该命令将会在Elasticsearch索引下创建一个名为“dummyproject”的新目录，并爬取本地路径“/opt/dummyproject”中所有扩展名包含“.php”的所有文件，然后将分析结果发送至Elasticsearch。

### 扫描远程Git库

除此之外，我们也可以使用“--git”参数来扫描一个远程Git项目库：

    
    
    ./bughound.py --git https://github.com/DummyCode/DummyProject --language php --extension .php --name dummyproject

Bughound将会自动克隆目标项目库，并将其存储至“projects”目录中，然后对其进行安全扫描与分析。

## 许可证协议

本项目的开发与发布遵循GPL-3.0开源许可证协议。

## 项目地址

 **Bughound：** 【[ _GitHub传送门_](https://github.com/mhaskar/Bughound)】

## 参考资料

> [ _https://shells.systems/unveiling-bughound-a-static-code-analysis-tool-> based-on-elasticsearch_](https://shells.systems/unveiling-bughound-a-static-> code-analysis-tool-based-on-elasticsearch)
>
> [
> _https://docs.docker.com/engine/install/﻿_](https://docs.docker.com/engine/install/)


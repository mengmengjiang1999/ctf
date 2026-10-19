![1.png](https://image.3001.net/images/20190306/1551862491_5c7f8adbb4681.png!small)

**今天给大家介绍的是一款名叫Pompem的开源工具，该工具可以在当前最热门或最重要的漏洞数据库中搜索漏洞以及相应的漏洞利用代码。该工具采用Python开发，可以帮助渗透测试人员或白帽黑客快速完成漏洞审计任务。**

当前的Pompem可搜索的数据库有：PacketStorm
Security、CXSecurity、ZeroDay、Vulners、国家漏洞数据库和WPScan漏洞数据库。

## 项目地址

Pompem：【[GitHub传送门](https://github.com/rfunix/Pompem)】

### 源代码

你可以直接点击【[这里](https://github.com/rfunix/Pompem/archive/v0.2.0.tar.gz)】下载最新的tar包或点击【[这里](https://github.com/rfunix/Pompem/archive/v0.2.0.zip)】下载最新的zip包。

或者，你也可以直接从[Git代码库](https://github.com/rfunix/Pompem)中下载Pompem：

    
    
    $ git clone https://github.com/rfunix/Pompem.git

### 依赖组件

Pompem支持在任何一个安装了[Python
3.5](https://www.python.org/downloads/)的平台上使用，并且需要下列依赖包：

-[Requests 2.9.1+](http://docs.python-requests.org/en/master/)

## 工具安装

使用下列命令安装Pompem：

    
    
    $ pip3.5 install -r requirements.txt

大家也可以使用[virualenv](https://virtualenv.pypa.io/en/stable/)，它可以帮助我们独立出已安装的包，如果你之前没有使用过virtualenv的话，可以参考【[这篇教程](http://docs.python-guide.org/en/latest/dev/virtualenvs)】。

## 工具使用

大家可以使用-h参数获取本项目的基本选项和帮助信息：

    
    
    $ python3.5 pompem.py -h
    
     
    
    Options:
    
      -h, --help                      show this help messageand exit
    
      -s, --search<keyword,keyword,keyword>  text forsearch
    
      --txt                           Write txt File
    
      --html                          Write html File

### 使用样例

    
    
    $python3.5 pompem.py -s Wordpress
    
    $python3.5 pompem.py -s Joomla --html
    
    $python3.5 pompem.py -s "Internet Explorer,joomla,wordpress" --html
    
    $python3.5 pompem.py -s FortiGate --txt
    
    $python3.5 pompem.py -s ssh,ftp,mysql

## 工具运行截图

![2.png](https://image.3001.net/images/20190306/1551862591_5c7f8b3f8e21d.png!small)![3.png](https://image.3001.net/images/20190306/1551862594_5c7f8b4237586.png!small)![4.png](https://image.3001.net/images/20190306/1551862593_5c7f8b4159563.png!small)

***参考来源：[Pompem](https://github.com/rfunix/Pompem)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


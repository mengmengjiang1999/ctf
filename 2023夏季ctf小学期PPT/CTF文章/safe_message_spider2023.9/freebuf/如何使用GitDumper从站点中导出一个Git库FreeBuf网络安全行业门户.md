![](https://image.3001.net/images/20220507/1651936748_62768dec3e68c545464bd.png!small)

## 关于Git-Dumper

Git-Dumper是一款功能强大的代码导出工具，在该工具的帮助下，广大研究人员可以轻松从一个网站中导出目标Git库，并存储到本地设备中进行分析和研究。

## 工具运行机制

该工具首先会检测提供的目录列表是否可用，如果可用，该工具将会以递归的方式下载目标站点中所有的.git目录（该功能与使用wget效果相同）。

如果目录列表不可用，那么该工具将使用多种方法来尽可能地查找更多的文件，具体操作步骤如下：

> 1、获取所有的常见文件，例如.gitignore、.git/HEAD和.git/index等；
>
> 2、通过分析.git/HEAD、.git/logs/HEAD、.git/config和.git/packed-> refs等文件来查找尽可能多的refs，例如refs/heads/master和refs/remotes/origin/HEAD；
>
> 3、通过分析.git/packed-refs、.git/index、.git/refs/*和.git/logs/*来寻找尽可能多的对象（sha1）；
>
> 4、递归获取所有的对象，并分析每一个commit来查找父组件；
>
> 5、运行“git checkout .”命令来恢复当前工作树；

## 工具依赖

本项目基于Python 开发，因此广大研究人员首先需要在本地设备上安装并配置好Python环境。

## 工具下载

### GitHub安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/arthaud/git-dumper.git

### pip安装

我们还可以使用pip来直接安装Git-Dumper：

    
    
    pip install git-dumper

## 源码构建

下载好Git-Dumper之后，可以使用pip命令来安装工具依赖组件：

    
    
    pip install -r requirements.txt

接下来，直接运行下列命令即可：

    
    
    ./git_dumper.py http://website.com/.git ~/website

## 工具帮助信息

    
    
    usage: git-dumper [options] URL DIR
    
    Dump a git repository from a website.
    
    positional arguments:
    
      URL                   url
    
      DIR                   output directory
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      --proxy PROXY         use the specified proxy
    
      -j JOBS, --jobs JOBS  number of simultaneous requests
    
      -r RETRY, --retry RETRY
    
                            number of request attempts before giving up
    
      -t TIMEOUT, --timeout TIMEOUT
    
                            maximum time in seconds before giving up
    
      -u USER_AGENT, --user-agent USER_AGENT
    
                            user-agent to use for requests
    
      -H HEADER, --header HEADER
    
                            additional http headers, e.g `NAME=VALUE`

## 命令解释

> -h, --help：显示工具帮助信息和退出；
>
> \--proxy PROXY：设置使用指定的代理；
>
> -j JOBS, --jobs JOBS：设置同时发送的请求数量；
>
> -r RETRY, --retry RETRY：设置请求发送尝试的最大次数；
>
> -t TIMEOUT, --timeout TIMEOUT：设置最大超时时间，单位为秒；
>
> -u USER_AGENT, --user-agent USER_AGENT：设置用于发送请求的用户代理；
>
> -H HEADER, --header HEADER：设置需要添加的额外HTTP Header；

## 工具使用样例

下列命令可以从目标站点直接导出Git库：

    
    
    git-dumper http://website.com/.git ~/website

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/arthaud/git-dumper/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Git-Dumper：** 【[ _GitHub传送门_](https://github.com/arthaud/git-dumper)】


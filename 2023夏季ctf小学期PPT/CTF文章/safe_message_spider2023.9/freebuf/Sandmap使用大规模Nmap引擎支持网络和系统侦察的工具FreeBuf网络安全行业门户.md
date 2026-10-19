**![Sandmap：使用大规模Nmap引擎支持网络和系统侦察的工具](https://image.3001.net/images/20180522/15269485152075.png!small)**

**Sandmap是一个支持使用大规模Nmap引擎进行网络和系统侦察的工具。它提供了一个非常友好的用户界面，自动化和加速扫描，并允许你轻松地使用各种高级的扫描技术。**

## 主要特性

> 具有运行纯NMAP引擎的简单的CLI
>
> 模块中包含了预定义的扫描
>
> 支持Nmap脚本引擎（NSE）
>
> TOR支持（proxychains）
>
> 一次性执行多项扫描
>
> 30个模块451份扫描配置文件

## 使用

    
    
    # 克隆存储库
    git clone https://github.com/trimstray/sandmap
    
    # 进入sandmap目录
    cd sandmap
    
    # 安装
    ./setup.sh install
    
    # 运行
    sandmap

> bin/sandmap位于/usr/local/bin目录。
>
> man文档位于/usr/local/man/man8目录。

## 模块

可用模块：30

可用扫描配置文件：451

## 配置文件

etc /main.cfg配置文件结构如下：

    
    
    # shellcheck shell=bash
    
    # Specifies the default destination.
    # Examples:
    #   - dest="127.0.0.1,8.8.8.8"
    dest="127.0.0.1"
    
    # Specifies the extended Nmap parameters.
    # Examples:
    #   - params="--script ssl-ccs-injection -p 443"
    params=""
    
    # Specifies the default output type and path.
    # Examples:
    #   - report="xml"
    report=""
    
    # Specifies the TOR connection.
    # Examples:
    #   - tor="true"
    tor=""
    
    # Specifies the terminal type.
    # Examples:
    #   - terminal="internal"
    terminal="internal"

## 运行条件

在运行之前，Sandmap需要加载使用以下外部程序：

> [nmap](https://nmap.org/)
>
> [xterm](https://invisible-island.net/xterm/)
>
> [proxychains](http://proxychains.sourceforge.net/)

## 日志

脚本运行后，会创建一个log/目录，并在其中创建以下带有日志的文件：

> <script_name>.<date>.log - 将所有_logger()函数调用保存在其中
>
> stdout.log - 将_init_cmd()函数的标准输出和错误写入其中。如果要重定向命令的输出，请使用以下语法结构：你的命令
> >>"$_log_stdout" 2>&1 &

## 项目架构

    
    
    | - LICENSE.md   ＃GNU通用公共许可，第3版，2007年6月29日
    | - README.md   ＃帮助文档
    | - CONTRIBUTING.md   ＃项目支持原则
    | - .gitignore   ＃忽略未跟踪的文件
    | - .travis.yml   ＃与Travis CI持续集成
    | - setup.sh   ＃在系统上安装sandmap
    | - bin
        | - sandmap   ＃主脚本（init）
    | - doc   ＃包含文档，图像和手册
        | - man8
            | - sandmap.8  ＃sandmap的man文档
        | - img   ＃图片（例如.gif）
    | - etc   ＃包含配置文件
    | - lib   ＃库，外部函数
    | - log   ＃包含在init之后创建的日志
    | - modules   ＃包含模块
    | - src   ＃包含外部项目文件
        | - helpers    ＃包含核心功能
        | - import   ＃附加lib目录的内容
        | - __init__   ＃包含__main__函数
        | - settings   ＃包含sandmap设置
    | - templates   ＃包含示例和模板文件
    | - tmp   ＃包含临时文件（mktemp）

你可以[在这里](https://github.com/trimstray/sandmap)下载Sandmap。

 ***参考来源：[kitploit](https://www.kitploit.com/2018/05/sandmap-tool-supporting-network-and.html)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  


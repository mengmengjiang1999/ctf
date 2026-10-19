![](https://image.3001.net/images/20200111/1578721564_5e19611c87d79.png!small)

##  LNAV

 **LNAV，即Log File
Navigator，INAV是一款增强型日志文件查看工具，安全审计人员可以利用INAV来分析并检查日志文件，并从中收集到相关的语义信息，例如时间戳和日志级别。使用这些额外的语义信息，INAV可以做很多事情，比如比对来自不同文件的信息，生成信息的直方图，以及帮助审计人员在日志文件中实现快速定位即导航，并帮助研究人员快速有效地发现问题。**

###  工具依赖

在构建和使用INAV之前，研究人员需安装下列工具依赖组件：

> gcc/clang - 兼容C++14的编译器
>
> libpcre - Perl兼容正则表达式（PCRE）库
>
> sqlite - SQLite数据库引擎，需要3.9.0或更高版本
>
> ncurses - 文本UI库
>
> readline - readline文本编辑库
>
> zlib - zlib压缩库
>
> bz2 - bzip2压缩库
>
> libcurl - 根据URL下载文件的cURL库，需要7.23.0或更高版本

###  工具安装

LNAV的安装和配置符合GNU风格，广大安全审计人员可以使用下列命令完成LNAV的安装：

    
    
    $ ./configure
    
        $ make
    
        $ sudo make install

如果广大用户是直接使用下列命令将项目代码克隆至本地的话:

    
    
    git clone https://github.com/tstack/lnav.git

那么我们就需要运行下列编译脚本来完成源码编译，在命令行中切换到源码目录，然后运行下列命令：

    
    
    $ ./autogen.sh

###  Cygwin用户

当然了，大家也可以在Cygwin中完成源码编译。或者说，你也可以直接从AppVeyor中获取已生成好的源码。请记住，此时你仍然需要使用Cygwin来配置INAV的依赖组件，直接运行下列命令即可完成依赖配置：

    
    
    setup-x86_64.exe -q -P libpcre1 -P libpcrecpp0 -P libsqlite3_0 -P libstdc++6

根据我们对目前版本的测试，INAV的x64版本会比x86版本更加稳定。

##  工具使用

安装完成后，广大用户可以直接在无参数的情况下来使用INAV，并查看日志文件：

    
    
    $ lnav

你也可以使用下列命令来查看所有的syslog信息：

    
    
    $ lnav /var/log/messages*

###  配合systemd-journald使用

如果系统中运行了systemd-journald，你也可以使用INAV配合systemd-journald一起使用:

    
    
    $ journalctl | lnav

或者：

    
    
    $ journalctl -f | lnav

由于journalctl的默认输出格式忽略了年份数据，因此如果你查看的日志跨越了多个年份的话，则需要更改输出格式以包含年份，否则lNAV可能会出现错误情况：

    
    
    $ journalctl -o short-iso | lnav

journalctl也可以支持JSON输出格式，INAV还会使用到很多额外的数据域，例如PRIORITY和_SYSTEMD_UNIT：

##  工具截图

下列截图中显示的是一个系统日志文件（syslog），其中的关键内容已高亮显示，错误信息为红色标记，警告信息为黄色标记。

![](https://image.3001.net/images/20200111/1578721705_5e1961a96343b.png!small)

##  项目地址

> GitHub：【[传送门](https://github.com/tstack/lnav)】
>
> 官网：【[传送门](http://lnav.org/)】

 ***
参考来源：[tstack](https://github.com/tstack/lnav)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


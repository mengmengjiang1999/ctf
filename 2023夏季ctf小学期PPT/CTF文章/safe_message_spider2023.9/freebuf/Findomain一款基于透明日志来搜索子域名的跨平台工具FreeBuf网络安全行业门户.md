**今天给大家介绍的是一款名叫Findomain的工具，这是一款能够帮助我们快速枚举/搜索子域名的跨平台工具。**

##  Twitter项目关注

> 开发团队：<https://twitter.com/sechacklabs>
>
> 开发者：<https://twitter.com/edu4rdshl>

![](https://image.3001.net/images/20190820/1566246152_5d5b05086c4db.png!small)

##  功能介绍

> 1、使用证书透明日志搜索子域名（非暴力破解）；
>
> 2、根据用户参数，搜索子域名（有IP或无IP）；
>
> 3、从用户参数（-t）读取搜索目标；
>
> 4、从文件中读取目标列表，并将结果写至输出文件；
>
> 5、将结果写入txt文件；
>
> 6、将结果写入csv文件；
>
> 7、将结果写入JSON文件；
>
> 8、跨平台支持；
>
> 9、支持多种API；
>
> 10、支持代理；

##  跨平台支持

> [Linux](https://github.com/Edu4rdSHL/findomain#installation-in-linux-using-> compiled-artifacts)
>
> [Windows](https://github.com/Edu4rdSHL/findomain#installation-windows)
>
> [MacOS](https://github.com/Edu4rdSHL/findomain#installation-macos)
>
> [ARM](https://github.com/Edu4rdSHL/findomain#installation-arm)
>
> [Aarch64 (RaspberryPi)](https://github.com/Edu4rdSHL/findomain#installation-> aarch64-raspberry-pi)

##  32位代码构建

使用[crate](https://crates.io/crates/findomain)：

    
    
    cargo install findomain

执行工具，cargo安装请参考这篇【[文档](https://doc.rust-lang.org/cargo/commands/cargo-install.html)】。

使用GitHub源代码：

>
> 1、克隆[项目代码](https://github.com/Edu4rdSHL/findomain)或直接从[release页面](https://github.com/Edu4rdSHL/findomain/releases)下载源码；
>
> 2、提取源代码；
>
> 3、切换至项目目录；
>
> 4、执行下列命令：
    
    
    cargo build --release

###  Android安装（Termux）

    
    
    $ pkg install rust make perl
    
        $cargo install findomain
    
        $ cd $HOME/.cargo/bin
    
        $./findomain

###  Linux安装（源码）

    
    
    $ git clone <https://github.com/Edu4rdSHL/findomain.git>
    
        $ cd findomain
    
        $ cargo build --release
    
        $ sudo cp target/release/findomain /usr/bin/
    
         $findomain

###  Linux安装（预编译）

    
    
    $wget <https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-linux>
    
        $chmod +x findomain-linux
    
        $./findomain-linux

###  ARM安装

    
    
    $wget <https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-arm>
    
        $chmod +x findomain-arm
    
        $./findomain -arm

###  Aarch64安装（树莓派）

    
    
    $wget <https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-aarch64>
    
        $chmod +x findomain-aarch64
    
        $./findomain -aarch64

###  macOS安装

    
    
    $wget <https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-osx>
    
        $chmod +x findomain-osx.dms
    
        $./findomain -osx.dms

###  Windows安装

针对Windows平台，用户可以直接下载exe安装工具即可。

> 下载地址：【[findomain-> windows.exe](https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-> windows.exe)】

##  工具使用

用户可以通过两种方式使用该工具，即搜索子域名或搜索子域名+IP地址：

    
    
    findomain 0.2.0
    
        Eduard Tolosa <tolosaeduard@gmail.com>
    
        Atool that use Certificates Transparency logs to find subdomains.
    
        USAGE:
    
            findomain [FLAGS] [OPTIONS]
    
        FLAGS:
    
            -a, --all-apis    Use all the available APIs to perform thesearch. It take more time but you will have a lot of
    
                              more results.
    
            -h, --help        Prints help information
    
            -i, --get-ip      Return the subdomain list with IP addressif resolved.
    
            -V, --version     Prints version information
    
        OPTIONS:
    
            -f, --file <file>        Sets the input file to use.
    
            -o, --output <output>    Write data to output file in the specifiedformat. [possible values: txt, csv, json]
    
            -p, --proxy <proxy>      Use a proxy to make the requests to theAPIs.
    
            -t, --target <target>    Target host

##  使用样例

1、进行简单的子域名搜索，并输出信息：

    
    
    findomain -t example.com

2、使用所有的API进行子域名搜索，并输出信息：

    
    
    findomain -t example.com –a

3、搜索子域名，并将输出导出为CSV文件格式：

    
    
    findomain -t example.com -o csv

4、使用所有的API进行子域名搜索，并将输出导出为CSV文件格式：

    
    
    findomain -t example.com -a -o csv

5、搜索子域名，并解析子域名的IP地址：

    
    
    findomain -t example.com –i

6、使用所有的API进行子域名搜索，，并解析子域名的IP地址：

    
    
    findomain -t example.com -i –a

7、使用所有的API进行子域名搜索，解析子域名的IP地址，，并将输出导出为CSV文件格式：

    
    
    findomain -t example.com -i -a -o csv

8、使用代理（[http://127.0.0.1:8080](http://127.0.0.1:8080/)）搜索子域名：

    
    
    findomain -t example.com -p http://127.0.0.1:8080

##  项目地址

Findomain：【[GitHub传送门](https://github.com/edu4rdshl/findomain)】

 ***
参考来源：[edu4rdshl](https://github.com/edu4rdshl/findomain)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


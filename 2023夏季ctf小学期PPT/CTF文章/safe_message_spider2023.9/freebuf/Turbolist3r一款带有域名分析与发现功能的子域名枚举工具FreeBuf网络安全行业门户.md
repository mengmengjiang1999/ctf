![](https://image.3001.net/images/20200108/1578470593_5e158cc10d6d7.jpg!small)

##  Turbolist3r

**Turbolist3r是子域名发现工具[sublist3r](https://github.com/aboul3la/sublist3r)的一个分支，除了sublist3r原始的资源情报收集功能之外，Turbolist3r还集成了一些针对子域名发现的自动化分析功能。**

Turbolist3r可以针对每一个发现的子域名来查询公共DNS服务器，如果目标子域名存在，那么将会生成已分类好的分析结果，其中包括CNAME和A记录等等。通过对A记录进行分析，我们将有可能发现潜在的渗透测试目标。

请注意，该工具切勿用于非法用途。

##  工具下载

广大用户可使用下列命令将该项目代码克隆至本地：

    
    
    git clone https://github.com/fleetcaptain/Turbolist3r.git

##  工具依赖

Turbolist3r需要使用dnslib、requests和argparse这几个Python模块。其中，subbrute模块用于实现爆破功能。

###  dnslib模块

广大用户可以点击【[这里](https://bitbucket.org/paulc/dnslib/)】下载dnslib模块，或使用下列命令直接下载安装：

    
    
    pip install dnslib

###  requests模块

Ubuntu/Debian安装：

    
    
    sudo apt-get install python-requests

Centos/Redhat安装：

    
    
    sudo yum install python-requests

Linux安装：

    
    
    sudo pip install requests

###  argparse模块：

Ubuntu/Debian安装：

    
    
    sudo yum install python-argparse

使用pip安装：

    
    
    sudo pip install argparse

##  工具使用

**短参数** |  **长参数** |  **描述**  
---|---|---  
-d  |  \--domain  |  目标域名   
-b  |  \--bruteforce  |  启用爆破模块   
-p  |  \--ports  |  针对特定TCP端口扫描子域名   
-v  |  \--verbose  |  启用verbose模式实时查看分析结果   
-t  |  \--threads  |  子域名爆破需用的进程   
-e  |  \--engines  |  指定搜索引擎   
-o  |  \--output  |  将扫描结果存储至text文件中   
-h  |  \--help  |  显示工具帮助信息   
-a  |  \--analyze  |  进行逆向DNS分析并输出结果   
(none)  |  \--saverdns  |  存储逆向DNS分析结果至特定文件  
(none)  |  \--inputfile  |  从文件中读取目标域名，并进行分析  
(none)  |  \--debug  |  调试模式  
-r  |  \--resolvers  |  IP解析   
-q  |  \--quiet  |  静默模式   
  
##  使用样例

查看工具的可选参数：

    
    
    python turbolist3r.py -h

针对特定域名进行子域名分析，并存储输出结果：

    
    
    python turbolist3r.py -d example.com -a --saverdns analysis_file.txt

从文件中读取目标域名：

    
    
    python turbolist3r.py -d example.com -a --inputfile subdomains.txt

子域名枚举：

    
    
    python turbolist3r.py -d example.com

子域名枚举，并存储扫描结果：

    
    
    python turbolist3r.py -d example.com -o example_hosts.txt

子域名枚举，实时查看结果：

    
    
    python turbolist3r.py -v -d example.com

子域名枚举，并启用爆破模式：

    
    
    python turbolist3r.py -b -d example.com

使用特定搜索引擎完成子域名枚举：

    
    
    python turbolist3r.py -e google,yahoo,virustotal -d example.com

##  工具运行截图

![](https://image.3001.net/images/20200108/1578470691_5e158d2303d8c.png!small)

![](https://image.3001.net/images/20200108/1578470695_5e158d2719ffe.png!small)

##  项目地址

Turbolist3r：【[GitHub传送门](https://github.com/fleetcaptain/Turbolist3r)】

***参考来源：[fleetcaptain](https://github.com/fleetcaptain/Turbolist3r)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


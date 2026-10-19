![](https://image.3001.net/images/20200310/1583841303_5e678017c0137.jpg!small)

##  NTLMRecon

**NTLMRecon是一款针对Web应用NTLM认证信息的枚举工具，如果目标Web节点启用了NTLM认证功能，那么广大研究人员就可以使用NTLMRecon来枚举目标相关信息。**

NTLMRecon是一款运行速度快且扩展灵活的NTLM侦察工具，该工具无需外部依赖即可实现其功能。在处理大量潜在IP地址和域名时，NTLMRecon将能够帮助我们快速收集关于目标NTLM节点的相关信息。

注意：该项目的内部字典取自[nyxgeek/lyncsmash](https://github.com/nyxgeek/lyncsmash)库。

##  工具概览

NTLMRecon可以搜索到启用了NTLM的Web节点，然后向其发送伪造的认证请求，并能够尝试从NTLMSSP响应中枚举出下列信息：

> 1、活动目录域名
>
> 2、服务器名
>
> 3、DNS域名
>
> 4、FQDN
>
> 5、父DNS域

由于NTLMRecon利用了一个Python脚本来实现NTLMSSP，这样可以在每次扫描成功之后消除Nmap NSE http-ntlm-info的运行开销。

##  工具安装

###  Arch

如果你运行的是Arch Linux，或其他基于Arch
Linux发行版的系统，你可以点击【[这里](https://aur.archlinux.org/packages/ntlmrecon/)】从AUR获取最新版本的构建文件。

###  通用安装

首先，使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/sachinkamath/ntlmrecon/

建议大家在虚拟环境中使用该文件，安装Virtualenv的命令如下:

    
    
    pip install virtualenv

接下来，使用下列命令创建一个新的虚拟环境，并激活该环境：

virtualenv venv

source venv/bin/activate

运行安装文件：

    
    
    python setup.py install

安装完成之后，你就可以使用下列命令来运行NTLMRecon并查看帮助信息了：

    
    
    ntlmrecon --help

##  工具使用

    
    
             _   _ _____ _     ___  _________
    
                | \ | |_   _| |    |  \/  || ___ \
    
                |  \| | | | | |    | .  . || |_/ /___  ___ ___  _ __
    
                | . ` | | | | |    | |\/| ||    // _ \/ __/ _ \| '_ \
    
                | |\  | | | | |____| |  | || |\ \  __/ (_| (_) | | | |
    
                \_| \_/ \_/ \_____/\_|  |_/\_| \_\___|\___\___/|_| |_|
    
                     v.0.1 beta - Y'all still exposing NTLM endpoints?

usage: ntlmrecon [-h] [--input INPUT | --infile INFILE] [--wordlist WORDLIST]
[--threads THREADS] [--output-type] --outfile OUTFILE [--random-user-agent]
[--force-all] [--shuffle]

optional arguments:

> -h, --help 显示帮助信息或退出
>
> \--input INPUT 以IP地址、URL或CIDR作为输入来枚举NTLM节点
>
> \--infile INFILE 传递本地输入文件
>
> \--wordlist WORDLIST 使用自定义字典覆盖内部字典
>
> \--threads THREADS 设置线程数量 (默认为10)
>
> \--output-type, -o 设置输出文件类型，支持JSON和CSV (默认为CSV)
>
> \--outfile OUTFILE 设置输出文件名称 (默认为ntlmrecon.csv)
>
> \--random-user-agent 使用随机用户代理来发送请求 (默认为 False) (未完成)
>
> \--force-all 强制枚举所有节点 (默认为False)
>
> \--shuffle 打乱输入文件中的数据顺序

##  工具使用样例

###  针对单个URL地址进行侦察

    
    
    $ ntlmrecon --input https://mail.contoso.com --outfile ntlmrecon.csv

###  针对一个CIDR范围或IP地址进行侦察

    
    
    $ ntlmrecon --input 192.168.1.1/24 --outfile ntlmrecon-ranges.csv

###  将目标侦察信息以输入文件的形式提供

NTLMRecon能够自动检测输入文件中每一行数据的类型，并自动将检测结果返回给用户。即使数据是从文本文件中读取出来的，该工具同样也能够自动识别并解析CIDR范围。

输入文件的内容样例如下：

> mail.contoso.com
>
> CONTOSOHOSTNAME
>
> 10.0.13.2/28
>
> 192.168.222.1/24
>
> [https://mail.contoso.com](https://mail.contoso.com/)

如果你想将目标侦察信息以输入文件的形式提供给NTLMRecon，可以直接运行下列命令：

    
    
    $ ntlmrecon --infile /path/to/input/file --outfile ntlmrecon-fromfile.csv

##  项目地址

> NTLMRecon：【[GitHub传送门](https://github.com/sachinkamath/ntlmrecon/)】

 ***
参考来源：[sachinkamath](https://github.com/sachinkamath/ntlmrecon/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


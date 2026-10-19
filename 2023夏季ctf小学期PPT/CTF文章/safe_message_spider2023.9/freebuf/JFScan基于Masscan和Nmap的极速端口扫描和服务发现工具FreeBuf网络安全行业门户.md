## 关于JFScan

JFScan是一个基于Massacn和Nmap实现的极速端口扫描工具，该工具旨在简化各种形式的端口扫描任务，并且能够接收以下形式的扫描目标：URL、域名或IP（包括CIDR）。除此之外，我们还可以使用参数或STDIN来指定包含目标的文件。

JFScan允许我们只输出扫描结果，并将扫描结果跟Nuclei之类的工具进行整合以形成工具链。如果你想要扫描目标Web应用程序中潜在的安全漏洞，那么JFScan输出的“域名:端口”信息将给你提供大量的帮助。

当然了，该工具还可以使用Nmap来进行端口扫描，并使用自定义选项和Nmap的脚本功能来满足我们的日常测试任务。

## 功能介绍

> 1、使用Nmap执行大规模扫描任务；
>
> 2、支持使用Masscan扫描目标，并使用自定义设置在检测到的端口上执行Nmap扫描；
>
> 3、支持扫描各种格式的目标，包括域名；
>
> 4、能够深层包含“域名:端口”格式的扫描输出结果；
>
> 5、支持在STDIN/STDOUT模式下工作，允许我们将结果以数据流的形式转发至其他工具；
>
> 6、自动调整Masscan的数据包速率，无需手动限速；
>
> 7、能够生成标准的Nmap XML格式报告；

## 工具下载&安装

JFScan基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。

在安装之前，还要确保你已经安装并配置好了最新版本的Massacn（v 1.3.2）。接下来，安装libpcap-dev（Debian发行版）或libcap-devel（CentOS发行版）：

    
    
    sudo apt install libpcap-dev

然后，使用下列命令即可将该项目源码克隆至本地，并完成安装：

    
    
    sudo apt-get --assume-yes install git make gcc
    
    git clone https://github.com/robertdavidgraham/masscan
    
    cd masscan
    
    make
    
    sudo make install

其中，Masscan需要root权限才能运行，但考虑到直接以root账号并不安全，因此我们设置了一个CAP_NET_RAW功能：

    
    
    sudo setcap CAP_NET_RAW+ep /usr/bin/masscan

接下来，安装并配置好Python 3和pip3：

    
    
    sudo apt install python3 python3-pip

最后，安装JFScan：

    
    
    $ git clone https://github.com/nullt3r/jfscan.git
    
    $ cd jfscan
    
    $ pip3 install .

如果你无法直接从命令行窗口运行JFScan的话，请检查“PATH”中的“$HOME/.local/bin”是否配置正确。即，直接在“~/.zshrc”或“~/.bashrc”中添加下列内容：

    
    
    export PATH="$HOME/.local/bin:$PATH"

## 工具使用帮助

![](https://image.3001.net/images/20220505/1651764953_6273eed90e7ee2e541f92.png!small)

## 工具使用样例

仅扫描目标端口80和443，速率为10kpps：

    
    
    $ jfscan -p 80,443 --targets targets.txt -r 10000

扫描目标前1000个端口：

    
    
    $ jfscan --top-ports 1000 1.1.1.1/24

指定STDIN目标并管道至Nuclei：

    
    
    $ cat targets.txt | jfscan --top-ports 1000 -q | httpx -silent | nuclei

或者，以位置参数进行配置：

    
    
    $ jfscan --top-ports 1000 1.1.1.1/24 -q | httpx -silent | nuclei

扫描所有指定的目标：

    
    
    $ echo target1 | jfscan --top-ports 1000 target2 --targets targets.txt -q | httpx -silent | nuclei

使用Nmap收集目标设备的更多信息：

    
    
    $ cat targets.txt | jfscan -p 0-65535 --nmap --nmap-options="-sV --scripts ssh-auth-methods"

以文件形式提供目标，包含目标的targets.txt文件格式如下：

    
    
    http://domain.com/
    
    domain.com
    
    1.2.3.4
    
    1.2.3.0/24

## 工具运行截图

 **简单扫描样例：**

![](https://image.3001.net/images/20220505/1651764990_6273eefec9907ad479daf.png!small)

 **使用样例1：**

![](https://image.3001.net/images/20220505/1651764997_6273ef05866aa9876c3d0.png!small)

 **使用样例2：**

![](https://image.3001.net/images/20220505/1651765003_6273ef0be18d8435218b9.png!small)

  

 **Nmap使用1：**

![](https://image.3001.net/images/20220505/1651765017_6273ef19f2c9930f18ac7.png!small)

 **Nmap使用2：**

![](https://image.3001.net/images/20220505/1651765026_6273ef2225794df00284c.png!small)

 **JFScan输入输出处理逻辑：**

![](https://image.3001.net/images/20220505/1651765033_6273ef2914c231907d9f9.png!small)

 **Nmap扫描：**

![](https://image.3001.net/images/20220505/1651765040_6273ef305499c80e702b5.png!small)

 **Masscan+Nmap扫描：**

![](https://image.3001.net/images/20220505/1651765046_6273ef3656c45d0791ada.png!small)

 **工具高级使用：**

![](https://image.3001.net/images/20220505/1651765052_6273ef3c70adf21818543.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/nullt3r/jfscan/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **JFScan：** 【[ _GitHub传送门_](https://github.com/nullt3r/jfscan)】


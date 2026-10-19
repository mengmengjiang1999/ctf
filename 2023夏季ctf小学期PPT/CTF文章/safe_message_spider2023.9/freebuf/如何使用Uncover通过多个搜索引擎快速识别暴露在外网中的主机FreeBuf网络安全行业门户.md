## 关于Uncover

Uncover是一款功能强大的主机安全检测工具，该工具本质上是一个Go封装器，并且使用了多个著名搜索引擎的API来帮助广大研究人员快速识别和发现暴露在外网中的主机或服务器。该工具能够自动化完成工作流，因此我们可以直接使用该工具所生成的扫描结果并将其集成到自己的管道工具中。

当前版本的Uncover支持Shodan、Shodan-InternetDB、Censys和Fofa搜索引擎API。

## 功能介绍

> 1、简单、易用且功能强大的功能，轻松查询多个搜索引擎；
>
> 2、支持多种搜索引擎，其中包括但不限于Shodan、Shodan-InternetDB、Censys和Fofa等；
>
> 3、自动实现密钥/凭证随机化；
>
> 4、支持以STDIN/STDOU实现数据的输入输出；

## 工具安装

Uncover基于Go语言开发，因此广大研究人员首先需要在本地设备上安装并配置好Go
v1.17版本环境。环境配置完成之后，可以直接运行下列命令来下载和安装Uncover：

    
    
    go install -v github.com/projectdiscovery/uncover/cmd/uncover@latest

## 工具使用

使用下列命令可以查看该工具的帮助信息以及命令参数选项：

    
    
    uncover -h

工具支持的参数选项如下所示：

    
    
    Usage:
    
      ./uncover [flags]
    
     
    
    Flags:
    
    INPUT:
    
       -q, -query string[]    搜索查询语句或列表 (文件或逗号分隔或STDIN)
    
       -e, -engine string[]   指定搜索引擎 (例如shodan,shodan-idb,fofa,censys) (默认为shodan)
    
     
    
    CONFIG:
    
       -pc, -provider string  提供商配置文件 (默认为"$HOME/.config/uncover/provider-config.yaml")
    
       -config string   参数配置文件 (默认为"$HOME/.config/uncover/config.yaml")
    
       -timeout int           超时秒数 (默认为30)
    
       -delay int            每次请求之间的间隔秒数 (默认为1)
    
     
    
    OUTPUT:
    
       -o, -output string    存储扫描结果的文件路径
    
       -f, -field string       输出数据中要显示的字段 (例如ip,port,host) (默认为"ip:port")
    
       -j, -json            将输出数据以JSON格式存储
    
       -r, -raw            将远程API返回的数据转换为元数据输出
    
       -l, -limit int         限制返回结果的数量 (默认为100)
    
       -nc, -no-color      禁用输出数据中的颜色高亮显示
    
     
    
    DEBUG:
    
       -silent     近显示输出数据中的扫描结果
    
       -version   显示项目版本信息
    
       -v        显示Verbose输出

## 提供商配置

默认提供商配置文件路径为“$HOME/.config/uncover/provider-config.yaml”，配置文件的样例内容如下：

    
    
    shodan:
    
      - SHODAN_API_KEY1
    
      - SHODAN_API_KEY2
    
    censys:
    
      - CENSYS_API_ID:CENSYS_API_SECRET
    
    fofa:
    
      - FOFA_EMAIL:FOFA_KEY

或者，我们也可以直接将API密钥以环境变量的形式添加到Bash Profile配置文件中：

    
    
    export SHODAN_API_KEY=xxx
    
    export CENSYS_API_ID=xxx
    
    export CENSYS_API_SECRET=xxx
    
    export FOFA_EMAIL=xxx
    
    export FOFA_KEY=xxx

## 工具运行和使用

### 常规使用

Uncover支持多种方式来实现查询，其中包括STDIN或“-q”选项：

    
    
    echo 'ssl:"Uber Technologies, Inc."' | uncover
    
                                            
    
      __  ______  _________ _   _____  _____
    
     / / / / __ \/ ___/ __ \ | / / _ \/ ___/
    
    / /_/ / / / / /__/ /_/ / |/ /  __/ /    
    
    \__,_/_/ /_/\___/\____/|___/\___/_/ v0.0.1    
    
                                            
    
     
    
    projectdiscovery.io
    
     
    
    [WRN] Use with caution. You are responsible for your actions
    
    [WRN] Developers assume no liability and are not responsible for any misuse or damage.
    
    [WRN] By using uncover, you also agree to the terms of the APIs used.
    
     
    
    107.180.12.116:993
    
    107.180.26.155:443
    
    104.244.99.31:443
    
    161.28.20.79:443
    
    104.21.8.108:443
    
    198.71.233.203:443
    
    104.17.237.13:443
    
    162.255.165.171:443
    
    12.237.119.61:443
    
    192.169.250.211:443
    
    104.16.251.50:443

我们还可以将查询内容以文件的形式提供给Uncover，其中每一行包含一个搜索查询语句：

    
    
    cat dorks.txt
    
     
    
    ssl:"Uber Technologies, Inc."
    
    title:"Grafana"

运行结果如下：

    
    
    uncover -q dorks.txt
    
                                            
    
      __  ______  _________ _   _____  _____
    
     / / / / __ \/ ___/ __ \ | / / _ \/ ___/
    
    / /_/ / / / / /__/ /_/ / |/ /  __/ /    
    
    \__,_/_/ /_/\___/\____/|___/\___/_/ v0.0.1    
    
                                            
    
     
    
        projectdiscovery.io
    
     
    
    [WRN] Use with caution. You are responsible for your actions
    
    [WRN] Developers assume no liability and are not responsible for any misuse or damage.
    
    [WRN] By using uncover, you also agree to the terms of the APIs used.
    
     
    
    107.180.12.116:993
    
    107.180.26.155:443
    
    104.244.99.31:443
    
    161.28.20.79:443
    
    104.21.8.108:443
    
    198.71.233.203:443
    
    2607:7c80:54:3::74:3001
    
    104.198.55.35:80
    
    46.101.82.244:3000
    
    34.147.126.112:80
    
    138.197.147.213:8086

### 多个搜索引擎API（Shodan、Censys、Fofa）

Uncover支持使用多个搜索引擎，默认使用的是Shodan，我们还可以使用“engine”参数来指定使用其他搜索引擎：

    
    
    echo jira | uncover -e shodan,censys,fofa
    
     
    
      __  ______  _________ _   _____  _____
    
     / / / / __ \/ ___/ __ \ | / / _ \/ ___/
    
    / /_/ / / / / /__/ /_/ / |/ /  __/ /    
    
    \__,_/_/ /_/\___/\____/|___/\___/_/ v0.0.3  
    
                                            
    
     
    
        projectdiscovery.io
    
     
    
    [WRN] Use with caution. You are responsible for your actions
    
    [WRN] Developers assume no liability and are not responsible for any misuse or damage.
    
    [WRN] By using uncover, you also agree to the terms of the APIs used.
    
     
    
    176.31.249.189:5001
    
    13.211.116.80:443
    
    43.130.1.221:631
    
    192.195.70.29:443
    
    52.27.22.181:443
    
    117.48.120.226:8889
    
    106.52.115.145:49153
    
    13.69.135.128:443
    
    193.35.99.158:443
    
    18.202.109.218:8089
    
    101.36.105.97:21379
    
    42.194.226.30:2626

### Shodan-InternetDB API

Uncover支持使用[ _Shodan_ _-InternetDB
API_](https://internetdb.shodan.io/)来查询给定IP/CIDR输入的所有可用端口。

如果输入数据是以IP/CIDR输入的方式提供的，则Uncover会使用shodan-idb作为默认搜索引擎，否则还是使用Shodan：

    
    
    echo 51.83.59.99/24 | uncover
    
     
    
      __  ______  _________ _   _____  _____
    
     / / / / __ \/ ___/ __ \ | / / _ \/ ___/
    
    / /_/ / / / / /__/ /_/ / |/ /  __/ /    
    
    \__,_/_/ /_/\___/\____/|___/\___/_/ v0.0.3  
    
                                            
    
     
    
        projectdiscovery.io
    
     
    
    [WRN] Use with caution. You are responsible for your actions
    
    [WRN] Developers assume no liability and are not responsible for any misuse or damage.
    
    [WRN] By using uncover, you also agree to the terms of the APIs used.
    
     
    
    51.83.59.1:53
    
    51.83.59.1:10000
    
    51.83.59.2:53
    
    51.83.59.3:25
    
    51.83.59.3:80
    
    51.83.59.3:389
    
    51.83.59.3:443
    
    51.83.59.3:465
    
    51.83.59.3:587
    
    51.83.59.3:993

### 字段过滤

我们可以使用“-f”或“-field”参数来指定返回的字段，当前仅支持“ip”、“port”和“host”：

    
    
    uncover -q jira -f host -silent
    
     
    
    ec2-44-198-22-253.compute-1.amazonaws.com
    
    ec2-18-246-31-139.us-west-2.compute.amazonaws.com
    
    tasks.devrtb.com
    
    leased-line-91-149-128-229.telecom.by
    
    74.242.203.213.static.inetbone.net
    
    ec2-52-211-7-108.eu-west-1.compute.amazonaws.com
    
    ec2-54-187-161-180.us-west-2.compute.amazonaws.com
    
    185-2-52-226.static.nucleus.be
    
    ec2-34-241-80-255.eu-west-1.compute.amazonaws.com

## 工具运行截图

![](https://image.3001.net/images/20220419/1650354811_625e6a7b42d161cf16d1c.png!small)![](https://image.3001.net/images/20220419/1650354825_625e6a89a7f08533d0a93.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/projectdiscovery/uncover/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Uncover：** 【[ _GitHub传送门_](https://github.com/projectdiscovery/uncover)】

## 参考资料

> [ _https://account.shodan.io/register_](https://account.shodan.io/register)
>
> [ _https://censys.io/register_](https://censys.io/register)
>
> [ _https://fofa.info/toLogin_](https://fofa.info/toLogin)
>
> [ _https://internetdb.shodan.io/_](https://internetdb.shodan.io/)


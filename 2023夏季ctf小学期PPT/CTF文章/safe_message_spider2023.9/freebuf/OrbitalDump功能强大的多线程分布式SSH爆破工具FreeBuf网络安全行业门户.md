![](https://image.3001.net/images/20210826/1629972783_6127692fa365e1c716cfe.jpg!small)

## 关于OrbitalDump

OrbitalDump是一款功能强大的多线程分布式SSH爆破工具，该工具基于纯Python开发，可以帮助广大研究人员分析SSH相关的安全问题。

## 工作机制

当该脚本在没有使用“--proxies”参数执行的时候，它将直接执行多线程SSH爆破攻击脚本。如果添加了“--proxies”参数的话，该脚本将会从[
_ProxyScrape_](https://proxyscrape.com/)获取大量SOCKS4代理（数千个），并通过SOCKS4代理来执行所有的暴力破解攻击，因此整个暴力破解攻击尝试并不会受到目标主机在速率方面的限制。

## 工具安装

在使用该工具前，请先确保本地主机已经安装并配置好了Python环境。接下来，广大研究人员就可以直接使用pip来安装OrbitalDump了：

    
    
    pip install -U --user orbitaldump
    
    orbitaldump

除此之外，广大研究人员也可以使用下列命令将该项目源码克隆至本地，并直接运行源码：

    
    
    git clone https://github.com/k4yt3x/orbitaldump.git
    
    cd orbitaldump
    
    python -m orbitaldump

## 工具使用

 **该工具支持的命令如下：**

> -t 10：启动10个暴力破解线程；
>
> -u usernames.txt：从usernames.txt文件中读取用户名，每个用户名单独占一行；
>
> -p passwords.txt：从passwords.txt文件中读取用户名，每个密码单独占一行；
>
> -h example.com：将暴力破解攻击目标设置为example.com；
>
> \--proxies：通过ProxyScrape的代理来执行攻击；
    
    
    python -m orbitaldump -t 10 -u usernames.txt -p passwords.txt -h example.com --proxies

## 工具完整使用

广大研究人员可以使用--help参数来获取OrbitalDump所能执行的所有操作：

    
    
    usage: orbitaldump [--help] [-t THREADS] [-u USERNAME] [-p PASSWORD] -h HOSTNAME [--port PORT] [--timeout TIMEOUT] [--proxies]
    
     
    
    optional arguments:
    
      --help                显示帮助信息并退出
    
      -t THREADS, --threads THREADS
    
                            需要使用的线程数量 (默认: 5)
    
      -u USERNAME, --username USERNAME
    
                            用户名文件路径 (默认: None)
    
      -p PASSWORD, --password PASSWORD
    
                            密码文件路径 (默认: None)
    
      -h HOSTNAME, --hostname HOSTNAME
    
                            目标主机名 (默认: None)
    
      --port PORT           目标端口 (默认: 22)
    
      --timeout TIMEOUT     SSH超时(默认: 6)
    
      --proxies             使用ProxyScrape的SOCKS代理 (默认: False)

## 工具运行演示

![](https://image.3001.net/images/20210826/1629972821_6127695510a332425acdf.png!small)

## 项目地址

 **OrbitalDump：** 【[ _GitHub传送门_](https://github.com/k4yt3x/orbitaldump)】


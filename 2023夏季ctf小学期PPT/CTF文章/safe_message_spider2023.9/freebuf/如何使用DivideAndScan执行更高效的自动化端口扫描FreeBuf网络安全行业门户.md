![](https://image.3001.net/images/20210525/1621895001_60ac27591a5098b49b62d.png!small)

## 关于DivideAndScan

DivideAndScan是一款功能强大的自动化端口扫描工具，该工具可以对完整的端口扫描结果进行解析，并帮助研究人员将扫描结果用于Nmap的执行。

DivideAndScan可以通过下列三个步骤实现更高效地自动化端口扫描任务：

> 针对批量目标执行开放端口扫描；
>
> 针对每个目标执行单独的Nmap扫描；
>
> 将结果整合进一个Nmap报告中，支持不同格式；

针对第一阶段，工具将使用一个快速端口扫描器（Masscan / RustScan /
Naabu），其输出将被解析并存储在数据库（TinyDB）中。接下来，在第二阶段中，根据数据库数据为每个目标启动单独的Nmap扫描，并提供一组开放端口（支持多线程）。最后，在第三阶段，工具会将Nmap输出合并至一个单独的报告中，并且会提供不同的格式（XML
/ HTML / 简单文本/ grepable）。

## 使用场景

渗透测试管理、红队研究；

网络安全作战游戏、CTF比赛；

OSCP认证考试；

## 工具运行机制

![](https://image.3001.net/images/20210525/1621895020_60ac276c98fd6639481f4.png!small)

## 工具安装

### 依赖组件

为了确保DivideAndScan的正常运行，我们需要安装一些其他的端口扫描工具。如果你不想这么麻烦的话，可以直接使用 _Docker_运行。

 **Nmap：**

    
    
    sudo apt install nmap sudo xsltproc -y
    
    sudo nmap --script-updatedb

 **Masscan：**

    
    
    cd /tmp
    
    git clone https://github.com/robertdavidgraham/masscan.git
    
    cd masscan
    
    make
    
    sudo make install
    
    cd && rm -rf /tmp/masscan

 **RustScan：**

    
    
    cd /tmp
    
     
    
    wget -qO- https://api.github.com/repos/RustScan/RustScan/releases/latest \
    
    | grep "browser_download_url.*amd64.deb" \
    
    | cut -d: -f2,3 \
    
    | tr -d \" \
    
    | wget -qO rustscan.deb -i-    
     
    
    sudo dpkg -i rustscan.deb
    
    cd && rm /tmp/rustscan.deb
    
     
    
    sudo wget https://gist.github.com/snovvcrash/c7f8223cc27154555496a9cbb4650681/raw/a76a2c658370d8b823a8a38a860e4d88051b417e/rustscan-ports-top1000.toml -O /root/.rustscan.toml

 **Naabu：**

    
    
    sudo mkdir /opt/projectdiscovery
    
    cd /opt/projectdiscovery
    
     
    
    wget -qO- https://api.github.com/repos/projectdiscovery/naabu/releases/latest \
    
    | grep "browser_download_url.*linux-amd64.tar.gz" \
    
    | cut -d: -f2,3 \
    
    | tr -d \" \
    
    | sudo wget -qO naabu.tar.gz -i-    
     
    
    sudo tar -xvzf naabu.tar.gz
    
    sudo mv naabu-linux-amd64 naabu
    
    sudo rm naabu.tar.gz README.md LICENSE.md
    
    sudo ln -vs /opt/projectdiscovery/naabu /usr/local/bin/naabu

### 本地安装

DivideAndScan可以通过PyPI安装，我们建议广大研究人员使用pipx从GitHub进行安装：

    
    
    ~$ pipx install -f "git+https://github.com/snovvcrash/DivideAndScan.git"
    
    ~$ das

如需进行工具调试，可以使用poetry设置一个开发环境：

    
    
    ~$ git clone https://github.com/snovvcrash/DivideAndScan
    
    ~$ cd DivideAndScan
    
    ~$ poetry install
    
    ~$ poetry run das

### 使用Docker

我们还可以在一个Docker容器中使用DivideAndScan：

    
    
    ~$ docker run -it --rm --name das -v `pwd`:/app snovvcrash/divideandscan

由于该工具需要某些输入数据，并生成某些输出数据，因此你需要指定当前工作目录：

    
    
    ~$ alias das='docker run -it --rm --name das -v `pwd`:/app snovvcrash/divideandscan'
    
    ~$ das

## 工具使用

![](https://image.3001.net/images/20210525/1621895095_60ac27b731a38c55d0875.png!small)

### 帮助信息

    
    
    usage: das [-h] {add,scan,report} ...
    
     
    
     -----------------------------------------------------------------------------------------------    
    |  ________  .__      .__    .___        _____              .____________                       |
    
    |  \______ \ |__|__  _|__| __| _/____   /  _  \   ____    __| _/   _____/ ____ _____    ____    |
    
    |   |    |  \|  \  \/ /  |/ __ |/ __ \ /  /_\  \ /    \  / __ |\_____  \_/ ___\\__  \  /    \   |
    
    |   |    `   \  |\   /|  / /_/ \  ___//    |    \   |  \/ /_/ |/        \  \___ / __ \|   |  \  |
    
    |  /_______  /__| \_/ |__\____ |\___  >____|__  /___|  /\____ /_______  /\___  >____  /___|  /  |
    
    |          \/                 \/    \/        \/     \/      \/       \/     \/     \/     \/   |
    
    |  {@snovvcrash}            {https://github.com/snovvcrash/DivideAndScan}             {vX.Y.Z}  |
    
     -----------------------------------------------------------------------------------------------    
     
    
    positional arguments:
    
      {add,scan,report}
    
        add              run a full port scan {masscan,rustscan,naabu,nmap} and add the output to DB
    
        scan             run targeted Nmap scans against hosts and ports from DB
    
        report           merge separate Nmap outputs into a single report in different formats
    
     
    
    optional arguments:
    
      -h, --help         show this help message and exit
    
     
    
    Psst, hey buddy... Wanna do some organized p0r7 5c4nn1n6?

## 项目地址

 **DivideAndScan：** 【[
_GitHub传送门_](https://github.com/snovvcrash/DivideAndScan)】


![](https://image.3001.net/images/20211122/1637581660_619b835cc7a1eafc9dce7.jpg!small)

## 关于DorkScout

DorkScout是一款功能强大的Google Dork安全扫描工具，在该工具的帮助下，广大研究人员可以轻松地对整个互联网范围内的Google
Dork容器或特定目标执行自动化安全扫描。

DorkScout可以通过Google搜索引擎自动查找互联网上存在安全漏洞的应用程序或机密文件，DorkScout首先会从[
_https://www.exploit-db.com/google-hacking-database_](https://www.exploit-db.com/google-hacking-database)获取可访问到的Dock列表，然后它会扫描一个给定的目标，或扫描所有获取到的Dock。

## 工具安装

DorkScout可以通过多种不同的方式来进行安装，具体如下。

### Go包安装

![](https://image.3001.net/images/20211122/1637581674_619b836aaeddaffbff92a.png!small)

广大研究人员可以通过[ _Golang包管理器_](https://github.com/rust-lang/cargo)来安装DorkScout：

    
    
    go get github.com/R4yGM/dorkscout

这种安装方式适用于所有操作系统平台。

### Docker安装

![](https://image.3001.net/images/20211122/1637581682_619b83726795d8f2e20ed.png!small)

如果你还没有安装Docker的话，请参考这篇【[ _文档_](https://docs.docker.com/engine/install/)】。

首先，你需要从Docker库中拉取DorkScout的Docker镜像（仅17.21MB）【[
_参考文档_](https://hub.docker.com/r/r4yan/dorkscout)】。如果你不想自己拉取镜像，你还可以将该项目源码克隆至本地，然后通过Dockerfile自行构建镜像：

    
    
    git clone https://github.com/R4yGM/dorkscout.git
    docker pull r4yan/dorkscout:latest

接下来，如果你想启动容器，你首先得创建一个卷来将你的文件共享给容器：

    
    
    docker volume create --name dorkscout_data

通过使用Docker，当你在启动容器的时候，它将会自动安装目录中名为“dorkscout”的Dork列表：

    
    
    -rw-r--r-- 1 r4yan r4yan   110 Jul 31 14:56  .dorkscout
    -rw-r--r-- 1 r4yan r4yan 79312 Aug 10 20:30 'Advisories and Vulnerabilities.dorkscout'
    -rw-r--r-- 1 r4yan r4yan  6352 Jul 31 14:56 'Error Messages.dorkscout'
    -rw-r--r-- 1 r4yan r4yan 38448 Jul 31 14:56 'Files Containing Juicy Info.dorkscout'
    -rw-r--r-- 1 r4yan r4yan 17110 Jul 31 14:56 'Files Containing Passwords.dorkscout'
    -rw-r--r-- 1 r4yan r4yan  1879 Jul 31 14:56 'Files Containing Usernames.dorkscout'
    -rw-r--r-- 1 r4yan r4yan  5398 Jul 31 14:56  Footholds.dorkscout
    -rw-r--r-- 1 r4yan r4yan  5568 Jul 31 14:56 'Network or Vulnerability Data.dorkscout'
    -rw-r--r-- 1 r4yan r4yan 49048 Jul 31 14:56 'Pages Containing Login Portals.dorkscout'
    -rw-r--r-- 1 r4yan r4yan 16112 Jul 31 14:56 'Sensitive Directories.dorkscout'
    -rw-r--r-- 1 r4yan r4yan   451 Jul 31 14:56 'Sensitive Online Shopping Info.dorkscout'
    -rw-r--r-- 1 r4yan r4yan 29938 Jul 31 14:56 'Various Online Devices.dorkscout'
    -rw-r--r-- 1 r4yan r4yan  2802 Jul 31 14:56 'Vulnerable Files.dorkscout'
    -rw-r--r-- 1 r4yan r4yan  4925 Jul 31 14:56 'Vulnerable Servers.dorkscout'
    -rw-r--r-- 1 r4yan r4yan  8145 Jul 31 14:56 'Web Server Detection.dorkscout'

这样一来，我们就不需要手动安装他们了，接下来你就可以通过下列命令来执行扫描任务了：

    
    
    docker run -v Dorkscout:/dorkscout r4yan/dorkscout scan <options>

使用你需要的参数选项替换掉命令中的<options>，即可自定义运行DorkScout：

    
    
    docker run -v dorkscout_data:/dorkscout r4yan/dorkscout scan -d="/dorkscout/Sensitive Online Shopping Info.dorkscout" -H="/dorkscout/a.html"

如果你想要使用Docker容器并通过代理来执行扫描，你需要添加“--net host”选项：

    
    
    docker run --net host -v dorkscout_data:/dorkscout r4yan/dorkscout scan -d="/dorkscout/Sensitive Online Shopping Info.dorkscout" -H="/dorkscout/a.html -x socks5://127.0.0.1:9050"

这种安装方式适用于所有操作系统平台。

### 可执行程序

除此之外，我们还可以直接下载已编译好的【[
_工具代码_](https://github.com/R4yGM/dorkscout/releases)】并直接执行。

## 工具使用

    
    
    dorkscout -h
    
    
    Usage:
    
      dorkscout [command]
    Available Commands:
      completion  generate the autocompletion script for the specified shell
      delete      deletes all the .dorkscout files inside a given directory
      help        Help about any command
      install     installs a list of dorks from exploit-db.com
      scan        scans a specific website or all the websites it founds for a list of dorks
    Flags:
      -h, --help   help for dorkscout
    Use "dorkscout [command] --help" for more information about a command.

使用字典和代理执行扫描任务，工具将会以HTML格式返回扫描结果：

    
    
    dorkscout scan -d="/dorkscout/Sensitive Online Shopping Info.dorkscout" -H="/dorkscout/a.html" -x socks5://127.0.0.1:9050

 **扫描结果示例：**

![](https://image.3001.net/images/20211122/1637581740_619b83ac0d35b30bae64e.png!small)

## 安装字典

在开始执行扫描任务的时候，你需要提供Dork列表，这一步可以通过下列命令实现：

    
    
    dorkscout install --output-dir /dorks

接下来，DorkScout就会从exploit.db中获取所有可用的Dork：

    
    
    [+] ./Advisories and Vulnerabilities.dorkscout
    [+] ./Vulnerable Files.dorkscout
    [+] ./Files Containing Juicy Info.dorkscout
    [+] ./Sensitive Online Shopping Info.dorkscout
    [+] ./Files Containing Passwords.dorkscout
    [+] ./Vulnerable Servers.dorkscout
    [+] ./Various Online Devices.dorkscout
    [+] ./Pages Containing Login Portals.dorkscout
    [+] ./Footholds.dorkscout
    [+] ./Error Messages.dorkscout
    [+] ./Files Containing Usernames.dorkscout
    [+] ./Network or Vulnerability Data.dorkscout
    [+] ./.dorkscout
    [+] ./Sensitive Directories.dorkscout
    [+] ./Web Server Detection.dorkscout
    2021/08/11 19:02:45 Installation finished in 2.007928 seconds on /dorks

## 项目地址

 **DorkScout：** 【[ _GitHub传送门_](https://github.com/R4yGM/dorkscout)】

## 参考资料

  * [ _https://www.exploit-db.com/google-hacking-database_](https://www.exploit-db.com/google-hacking-database)
  * [ _https://github.com/rust-lang/cargo_](https://github.com/rust-lang/cargo)
  * [ _https://docs.docker.com/engine/install/_](https://docs.docker.com/engine/install/)
  * [ _https://hub.docker.com/r/r4yan/dorkscout_](https://hub.docker.com/r/r4yan/dorkscout)
  * [ _https://github.com/R4yGM/dorkscout/blob/1.0/Dockerfile_](https://github.com/R4yGM/dorkscout/blob/1.0/Dockerfile)
  * [ _https://github.com/R4yGM/dorkscout/releases_](https://github.com/R4yGM/dorkscout/releases)


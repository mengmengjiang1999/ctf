![fingerprint.jpg](https://image.3001.net/images/20181209/1544322801_5c0c7ef1e9049.jpg!small)

**[Scannerl](https://github.com/kudelskisecurity/scannerl)是由[Kudelski
Securit](https://www.kudelskisecurity.com/)开发的模块化分布式指纹识别引擎，它可以在单个主机上识别数以千计的目标指纹，也可以在多个主机上分布执行分布式的指纹识别。Scannerl会识别zmap到端口扫描的指纹内容。当前的Scannerl版本适用于Debian/Ubuntu/Arch（包括其他的一些发行版本），使用主/从（master/slave）架构，主节点会将工作（主机指纹）分配给其从节点（本地或远程），且整个部署对用户都是透明的。**

## Scannerl 的优势

传统的指纹识别工具在进行大规模分析时，安全研究人员通常会遇到两个限制：首先，这些工具通常都是为一次扫描相对较少的主机而构建的，且不适用于大范围的IP地址。其次，如果对IPS设备保护的大范围IP地址进行指纹识别，则很有可能被列入黑名单导致信息集的不完整和缺失。Scannerl则可以很好的解决这些限制，你不仅可以在单个主机执行指纹识别任务，还可以将任务分布式到多个主机执行。Scannerl还使这些任务的分发完全透明，这使得大型指纹项目的设置和维护更加容易，让安全研究人员有更多的时间专注于分析，而无需手工操作重复繁杂的工作。此外，scannerl还允许你通过几行代码轻松设置特定的指纹分析。创建指纹识别群集不仅易于设置，而且还可以通过在指纹识别活动中添加fine-tuned扫描来进行调整。可以说scannerl是执行大规模指纹识别任务速度最快的工具。了解有关更多scannerl的内容，请参阅以下链接：

> [Fingerprint all the things with scannerl at
> BlackAlps](https://youtu.be/xHF2T5E7OFQ)
>
> [Fingerprinting MySQL with
> scannerl](https://research.kudelskisecurity.com/2017/12/11/fingerprinting-> mysql-with-scannerl/)
>
> [Fingerprint ICS/Scada with
> scannerl](https://research.kudelskisecurity.com/2017/12/13/scannerl-ics-> modules-open-source/)
>
> [Distributed fingerprinting with
> scannerl](https://research.kudelskisecurity.com/2017/06/06/distributed-> fingerprinting-with-scannerl/)
>
> [6 months of ICS
> scanning](https://research.kudelskisecurity.com/2017/10/24/6-months-of-ics-> scanning/)

## 安装

不同安装选项请参阅[wiki安装页面](https://github.com/kudelskisecurity/scannerl/wiki/Installation)。

要从源码安装，首先请确保你已安装Erlang（且版本不低于v.18）以及选择对应于你平台的安装包：[Erlang
downloads](https://www.erlang-solutions.com/resources/download.html)

安装所需的包：

    
    
    # on debian
    $ sudo apt install erlang erlang-src rebar
    
    # on arch
    $ sudo pacman -S erlang-nox rebar

然后构建scannerl：

    
    
    $ git clone https://github.com/kudelskisecurity/scannerl.git
    $ cd scannerl
    $ ./build.sh

查看帮助选项：

    
    
    $ ./scannerl -h

对于[arch
linux](https://www.kitploit.com/search/label/Arch%20Linux)用户可在aur中获取scannerl。

  * [scannerl](https://aur.archlinux.org/packages/scannerl/)
  * [scannerl-git](https://aur.archlinux.org/packages/scannerl-git/)

DEB（Ubuntu，Debian）可在发行版中找到。

RPM（Opensuse，Centos，Redhat）可在<https://build.opensuse.org/package/show/home:chapeaurouge/scannerl>下找到。

###  **分布式设置**

执行分布式扫描需要两种类型的节点：

> 主节点：scannerl二进制文件运行的地方
>
> 从节点：scannerl将连接以分发其所有工作的位置

主节点需要安装和编译scannerl，而从节点只需安装Erlang。整个设置是透明的，由主节点自动完成。

###  **分布式扫描的要求**

> 所有主机都需要安装相同版本的Erlang
>
> 所有主机都可以使用SSH公钥相互连接
>
> 所有主机的名称解析（如未设置正确的DNS，请使用/etc/hosts）
>
> 所有主机都具有相同的[Erlang security
> cookie](http://erlang.org/doc/reference_manual/distributed.html)
>
> 所有主机必须允许连接到Erlang EPMD端口（TCP/4369）
>
> 所有主机都打开了以下端口范围：TCP/11100到TCP/11100+从节点数

## 使用

    
    
    $ ./scannerl -h
       ____   ____    _    _   _ _   _ _____ ____  _
      / ___| / ___|  / \  | \ | | \ | | ____|  _ \| |
      \___ \| |     / _ \ |  \| |  \| |  _| | |_) | |
       ___) | |___ / ___ \| |\  | |\  | |___|  _ <| |___
      |____/ \____/_/   \_\_| \_|_| \_|_____|_| \_\_____|
    
    USAGE
      scannerl MODULE TARGETS [NODES] [OPTIONS]
    
      MODULE:
        -m <mod> --module <mod>
          mod: the fingerprinting module to use.
               arguments are separated with a colon.
    
      TARGETS:
        -f <target> --target <target>
          target: a list of target separated by a comma.
        -F <path> --target-file <path>
          path: the path of the file containing one target per line.
        -d <domain> --domain <domain>
          domain: a list of domains separated by a comma.
        -D <path> --domain-file <path>
          path: the path of the file containing one domain per line.
    
      NODES:
        -s <node> --slave <node>
          node: a list of node (hostnames not IPs) separated by a comma.
        -S <path> --slave-file <path>
          path: the path of the file containing one node per line.
                a node can also be supplied with a multiplier (<node>*<nb>).
    
      OPTIONS:
        -o <mod> --output <mod>     逗号分隔输出模块列表
        -p <port> --port <port>     指定端口
        -t <sec> --timeout <sec>    指纹识别进程超时
        -T <sec> --stimeout <sec>   从节点连接超时（默认值: 10）
        -j <nb> --max-pkt <nb>      最大pkt（int 或 "infinity"）
        -r <nb> --retry <nb>        重试次数（默认值: 0）
        -c <cidr> --prefix <cidr>   使用> cidr前缀进行范围细分（默认值：24）
        -M <port> --message <port>  侦听消息的端口（默认为：57005）
        -P <nb> --process <nb>      每个节点最大同时进程（默认值：28232）
        -Q <nb> --queue <nb>        在队列中最大nb未处理结果（默认为: infinity）
        -C <path> --config <path>   从文件中读取参数，每行一个
        -O <mode> --outmode <mode>  0：表示在Master上, 1：表示在slave上, >1：表示在broker上（默认为: 0）
        -v <val> --verbose <val>    显示详细信息（0 <= int <= 255）
        -K <opt> --socket <opt>     以逗号分隔的套接字选项（key[:value]）
        -l --list-modules           列出可用的fp/out模块
        -V --list-debug             列出可用的debug选项
        -A --print-args             输出args记录
        -X --priv-ports             仅使用1到1024之间的源端口
        -N --nosafe                 即使一些从节点启动失败，也继续执行
        -w --www                    DNS将尝试使用www.<domain>
        -b --progress               显示进度
        -x --dryrun                 dry run

更多内容请参阅[wiki](https://github.com/kudelskisecurity/scannerl/wiki)页面。

###  **单独使用**

Scannerl可以在本地主机上单独使用。但它仍将在运行它的同一主机上创建一个从节点。因此，你同样需要满足上述分布式设置要求。

一个快速的方法是确保你的主机能够自我解析，命令如下：

    
    
    grep -q "127.0.1.1\s*`hostname`" /etc/hosts || echo "127.0.1.1 `hostname`" | sudo tee -a /etc/hosts

并创建一个SSH key将其添加到authorized_keys：

    
    
    cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys

以下示例从本地主机运行了一个针对google.com的HTTP banner抓取。

    
    
    ./scannerl -m httpbg -d google.com

###  **分布式使用**

执行分布式扫描之前，需要预先设置scannerl将使用的主机以分发工作。有关更多信息，请参阅[分布式设置](https://github.com/kudelskisecurity/scannerl#distributed-setup)部分。

Scannerl需要使用的从节点列表可以通过 **-s** 或 **-S** 选项添加。

    
    
    ./scannerl -m httpbg -d google.com -s host1,host2,host3

###  **列出可用模块**

使用-l选项列出可用模块：

    
    
    $ ./scannerl -l
    
    Fingerprinting modules available
    ================================
    
    bacnet             UDP/47808: Bacnet identification
    chargen            UDP/19: Chargen amplification factor identification
    fox                TCP/1911: FOX identification
    httpbg             TCP/80: HTTP Server header identification
                         - Arg1: [true|false] follow redirection [Default:false]
    httpsbg            SSL/443: HTTPS Server header identification
    https_certif       SSL/443: HTTPS certificate graber
    imap_certif        TCP/143: IMAP STARTTLS certificate graber
    modbus             TCP/502: Modbus identification
    mqtt               TCP/1883: MQTT identification
    mqtts              TCP/8883: MQTT over SSL identification
    mysql_greeting     TCP/3306: Mysql version identification
    pop3_certif        TCP/110: POP3 STARTTLS certificate graber
    smtp_certif        TCP/25: SMTP STARTTLS certificate graber
    ssh_host_key       TCP/22: SSH host key graber
    
    Output modules available
    ========================
    
    csv                output to csv
                         - Arg1: [true|false] save everything [Default:true]
    csvfile            output to csv file
                         - Arg1: [true|false] save everything [Default:false]
                         - Arg2: File path
    file               output to file
                         - Arg1: File path
    file_ip            output to stdout (only ip)
                         - Arg1: File path
    file_mini          output to file (only ip and result)
                         - Arg1: File path
    file_resultonly    output to file (only result)
                         - Arg1: File path
    stdout             output to stdout
    stdout_ip          output to stdout (only IP)
    stdout_mini        output to stdout (only ip and result)

###  **模块参数**

可以使用冒号向模块提供参数。例如，文件输出模块：

    
    
    ./scannerl -m httpbg -d google.com -o file:/tmp/result

###  **结果格式**

scannerl返回到输出模块的结果将以以下形式显示：

    
    
    {module, target, port, result}

  * module：使用的模块（Erlang atom）
  * target：IP或主机名（字符串或IPv4地址）
  * port：端口（整数）
  * result：见下文

结果部分的形式为：

    
    
    {{status, type},Value}

其中{status, type}是以下元组之一：

  * {ok，result}：指纹识别目标成功
  * {error，up}：指纹识别未成功，但目标有响应
  * {error，unknown}：指纹识别失败

Value为返回值 - atom原子或元素列表

## Scannerl 扩展

Scannerl的设计和实现考虑了模块化，因此向它添加新模块相当的容易：

>  **Fingerprinting module：** 查询特定协议或服务。例如，fp_httpbg.erl模块允许检索HTTP响应中的服务器条目。
>
>  **Output module：**
> 输出到特定数据库/文件系统或以特定格式输出结果。例如，out_file.erl和out_stdout.erl模块分别允许输出到文件或stdout。

创建新模块，可以参照fp_module.erl和out_behavior.erl源文件形式。

新模块既可以在编译时添加，也可以作为外部文件动态添加。

有关更多信息，请参阅[Wiki页面](https://github.com/kudelskisecurity/scannerl/wiki/Module-Implementation)。

 ***参考来源：[kitploit](https://www.kitploit.com/2018/11/scannerl-modular-distributed.html)，FB小编secist编译，转载请注明来自FreeBuf.COM**  


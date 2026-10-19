![](https://image.3001.net/images/20220818/1660794568_62fdb6c8169c7049c9bf6.png!small)  

## 关于SilentHound

SilentHound是一款针对活动目录域安全的检测工具，该工具可以通过LDAP解析用户、管理员和组信息，并以此来在后台悄悄枚举活动目录域。该工具由[
_Layer_ _8_ _Security_](https://layer8security.com/)的[ _Nick_ __
_Swink_](https://github.com/nickswink)开发和维护，基于纯Python开发，欢迎社区中的广大研究人员下载使用，或提交代码。

## 关于LDAP

LDAP全称是Lightweight Directory Access
Protocol，即轻量目录访问协议。顾名思义，LDAP是设计用来访问目录数据库的一个协议。协议就是标准，并且是抽象的。在这套标准下，AD（Active
Directory，活动目录）是微软的对目录服务数据库的实现。目录服务数据库也是一种数据库，这种数据库相对于我们熟知的关系型数据库（比如MySQL和Oracle），主要有以下几个方面的特点。

> 1、它成树状结构组织数据，类似文件目录一样；
>
> 2、它是为查询、浏览和搜索而优化的数据库，也就是说LDAP的读性能特别强，但是写性能差，而且还不支持事务处理、回滚等复杂功能；

因此，为了能够访问目录数据库，必须设计一台能够访问目录服务数据库的协议，LDAP是其中一种实现协议。

## 工具安装

### Debian安装

    
    
    sudo apt-get install build-essential python3-dev python2.7-dev \
    
    libldap2-dev libsasl2-dev slapd ldap-utils tox \
    
    lcov valgrind

### 使用pipenv（推荐方法）

下列命令将会创建一个单独的隔离虚拟环境：

    
    
    sudo python3 -m pip install --user pipenv
    
    git clone https://github.com/layer8secure/SilentHound.git
    
    cd silenthound
    
    pipenv install

除此之外，我们还可以使用“pipenv shell”命令在一个虚拟环境中打开一个shell，或者使用“pipenv run”命令直接运行操作指令。

### 通过pip安装依赖组件

    
    
    python3 -m pip install -r requirements.txt
    
    python3 silenthound.py -h

## 工具使用帮助

    
    
    $ pipenv run python silenthound.py -h
    
    usage: silenthound.py [-h] [-u USERNAME] [-p PASSWORD] [-o OUTPUT] [-g] [-n] [-k] TARGET domain
    
     
    
    Quietly enumerate an Active Directory environment.
    
     
    
    positional arguments:
    
      TARGET                域控制器IP
    
      domain                包含上下文的域名，例如ACME.com / HOME.local / htb.net
    
     
    
    optional arguments:
    
      -h, --help              显示工具帮助信息和退出
    
      -u USERNAME, --username USERNAME
    
                            使用完全限定域名(bdole@home.local)或LDAP用户名('bob dole')
    
      -p PASSWORD, --password PASSWORD
    
                            活动目录密码
    
      -o OUTPUT, --output OUTPUT
    
                            输出文件名称，针对主机、用户、域管理员和当前工作目录描述创建输出文件
    
      -g, --groups          以用户成员显示组名称
    
      -n, --org-unit         显示组单元
    
      -k, --keywords        在LDAP对象中搜索关键词    

## 输出文件&结果

通过使用“-o”选项将允许工具将每个部分的输出以stdout输出：

    
    
    -rw-r--r--  1 kali  kali   122 Jun 30 11:37 BASENAME-descriptions.txt
    
    -rw-r--r--  1 kali  kali    60 Jun 30 11:37 BASENAME-domain_admins.txt
    
    -rw-r--r--  1 kali  kali  2620 Jun 30 11:37 BASENAME-groups.txt
    
    -rw-r--r--  1 kali  kali    89 Jun 30 11:37 BASENAME-hosts.txt
    
    -rw-r--r--  1 kali  kali  1940 Jun 30 11:37 BASENAME-keywords.txt
    
    -rw-r--r--  1 kali  kali    66 Jun 30 11:37 BASENAME-org.txt
    
    -rw-r--r--  1 kali  kali   529 Jun 30 11:37 BASENAME-users.txt

## 项目地址

 **SilentHound** ：【[
_GitHub传送门_](https://github.com/layer8secure/SilentHound)】

## 参考资料

> [ _https://github.com/nickswink_](https://github.com/nickswink)
>
> [ _https://layer8security.com/_](https://layer8security.com/)

  


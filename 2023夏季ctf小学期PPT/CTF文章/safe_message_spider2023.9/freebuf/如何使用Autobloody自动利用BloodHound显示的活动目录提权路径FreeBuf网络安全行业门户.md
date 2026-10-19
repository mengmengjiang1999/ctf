![](https://image.3001.net/images/20221226/1672056291_63a98de375312e40343c8.png!small)

## 关于Autobloody

Autobloody是一款针对活动目录的安全审查工具，在该工具的帮助下，广大研究人员可以通过自动化的形式利用BloodHound扫描发现的活动目录提权路径来实现权限提升。

如果BloodHound数据库中存在两个对象之间的提权路径，那么该工具将会以自动化的形式通过这两个活动目录对象，即源对象（我们拥有的）和目标对象（我们想要的）来实现权限提升。工具的自动化操作分为两个步骤：

> 1、使用BloodHound数据和Neo4j查询来寻找最佳的权限提升路径；
>
> 2、使用[ _bloodyAD_](https://github.com/CravateRouge/bloodyAD)包执行搜索到的提权路径；

Autobloody基于[
_bloodyAD_](https://github.com/CravateRouge/bloodyAD)实现其功能，而这个包支持使用明文密码、pass-the-hash、pass-the-ticket和证书来进行身份验证，并可以绑定到域控制器的LDAP服务以执行活动目录权限提升。

## 工具依赖

> [ _bloodyAD_](https://github.com/CravateRouge/bloodyAD)
>
> Neo4j python 驱动器
>
> Neo4j（带[ _GDS_ _库_](https://neo4j.com/docs/graph-data-> science/current/installation/)）
>
> BloodHound
>
> Python 3
>
> Gssapi (linux) 或Winkerberos (Windows)

## 工具安装

该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

如果你使用的是Linux设备的话，你还要在自己的操作系统中安装libkrb5-dev以确保Kerberos能够正常运行。

Debian/Ubuntu/Kali：

    
    
    apt-get install libkrb5-dev

Centos/RHEL：

    
    
    yum install krb5-devel

Fedora：

    
    
    dnf install krb5-devel

Arch Linux：

    
    
    pacman -S krb5

接下来，我们可以使用pip命令来直接安装Autobloody：

    
    
    pip install autobloody

或者使用下列命令将该项目源码克隆至本地，并执行安装脚本：

    
    
    git clone --depth 1 https://github.com/CravateRouge/autobloody
    
    pip install .

## 工具使用

首先，我们必须将相关数据导入到BloodHound中（例如使用SharpHound或BloodHound.py），然后Neo4j也必须同时运行起来。

注意：-ds和-dt值是大小写敏感的。

### 工具使用样例

    
    
    autobloody -u john.doe -p 'Password123!' --host 192.168.10.2 -dp 'neo4jP@ss' -ds 'JOHN.DOE@BLOODY.LOCAL' -dt 'BLOODY.LOCAL'

### 工具帮助信息

    
    
    [bloodyAD]$ ./autobloody.py -h
    
    usage: autobloody.py [-h] [--dburi DBURI] [-du DBUSER] -dp DBPASSWORD -ds DBSOURCE -dt DBTARGET [-d DOMAIN] [-u USERNAME] [-p PASSWORD] [-k] [-c CERTIFICATE] [-s] --host HOST
    
     
    
    AD Privesc Automation
    
     
    
    options:
    
      -h, --help             显示工具帮助信息和退出
    
      --dburi DBURI         运行Neo4j的主机 (默认为 "bolt://localhost:7687")
    
      -du DBUSER, --dbuser DBUSER
    
                            Neo4j用户名 (默认为 "neo4j")
    
      -dp DBPASSWORD, --dbpassword DBPASSWORD
    
                            Neo4j密码
    
      -ds DBSOURCE, --dbsource DBSOURCE
    
                            源节点标签，大小写敏感
    
      -dt DBTARGET, --dbtarget DBTARGET
    
                            目标节点标签，大小写敏感
    
      -d DOMAIN, --domain DOMAIN
    
                            用于NTLM身份认证的域
    
      -u USERNAME, --username USERNAME
    
                            用于NTLM身份认证的用户名
    
      -p PASSWORD, --password PASSWORD
    
                            用于NTLM身份认证明文密码或LMHASH:NTHASH
    
      -k, --kerberos
    
      -c CERTIFICATE, --certificate CERTIFICATE
    
                            身份验证证书，例如 "path/to/key:path/to/cert"
    
      -s, --secure           尝试通过TLS使用LDAP，即LDAPS (默认为 LDAP)
    
      --host HOST           域控制器的主机名或IP (例如: my.dc.local or 172.16.1.3)

## 工具限制

当前版本的Autobloody只能支持下列BloodHound边缘的自动化利用：

> MemberOf
>
> ForceChangePassword
>
> AddMembers
>
> AddSelf
>
> DCSync
>
> GetChanges/GetChangesAll
>
> GenericAll
>
> WriteDacl
>
> GenericWrite
>
> WriteOwner
>
> Owns
>
> Contains
>
> AllExtendedRights

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/CravateRouge/autobloody/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Autobloody** ：【[ _GitHub传送门_](https://github.com/CravateRouge/autobloody)】

## 参考资料

> [
> _https://github.com/CravateRouge/bloodyAD_](https://github.com/CravateRouge/bloodyAD)
>
> [ _https://neo4j.com/docs/graph-data-> science/current/installation/_](https://neo4j.com/docs/graph-data-> science/current/installation/)


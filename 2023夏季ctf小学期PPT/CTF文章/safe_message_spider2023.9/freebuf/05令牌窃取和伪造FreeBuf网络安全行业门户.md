## 一、前言

在前几篇文章中给大家介绍了如何从零开始搭建一个属于自己的内网环境以及当我们进入到一个内网环境中，该怎么样判断当前机器所属的环境是工作组还是域？我们需要收集哪些信息？该通过什么方式进行信息收集？从本篇文章开始，我将开始为大家介绍域渗透的思路及方法，本篇文章主要是介绍令牌伪造在各个工具中的应用。

## 二、令牌伪造介绍

**令牌
(token)**是系统的临时秘钥，相当于账号和密码，用来决定是否允许这次请求和判断这次请求是属于哪一个用户的。它允许你在不提供密码或其他凭证的前提下，访问网络和系统资源，这些令牌将持续存在于系统中，除非系统重新启动。

令牌最大的特点就是 **随机性，不可预测** ，黑客或软件无法猜测出令牌。

当不同的用户登录计算机后，都会生成一个访问令牌，这个Token 在用户创建进程或者线程的似乎还会被使用，并不断进行拷贝，一般用户双击运行⼀个进程都会拷贝
explorer.exe 中 的 Access Token
，一般情况下A用户创建的进程，B用户是没有权限进行操作的，因此可以通过令牌伪造的方式伪造一个网络中的另一个用户进行各类操作。所以当一个攻击者需要域管理员的操作权限时候，需要通过假冒域管理员的令牌进行攻击，

令牌有很多种：

  *  **访问令牌(Access Token)** ：表示访问控制操作主体的系统对象

  *  **会话令牌(Session Token)** ：是交互会话中唯一的身份标识符

  *  **密保令牌(Security Token)** ：又叫做认证令牌或硬件令牌，是一种计算机身份校验的物理设备，例如 U 盾

Windows 的 AccessToken 有两种类型：

  *  **Delegation Token** ：授权令牌，它支持交互式会话登录 (例如本地用户直接登录、远程桌面登录访问)

  *  **Impresonation Token** ：模拟令牌，它是非交互的会话 (例如使用 **net use** 访问共享文件夹)。

 **注：** **两种 token 只在系统重启后清除 具有 Delegation token 的用户在注销后，该 Token
将变成Impersonation token，依旧有效** 。

对于令牌窃取很多人可能会存在着一些误解，这不属于一种提权方法，当前系统中的某个进程或线程能访问到什么样的系统资源**,**完全取决于你当前进程是拿着谁的令牌。

默认情况下，我们列举令牌，只能列举出当前用户和比当前用户权限更低的用户令牌。

令牌的数量取决于当前shell的访问级别，如果当前的shell是 **administrator** 或者是 **system**
，我们就可以看到系统中的所有的令牌。

当我们在获取到一台低权限机器的时候，可以通过exp进行提权得到System权限，或者内网横向的时候直接使用永恒之蓝得到的权限也是为System，假如我们利用
mimikatz 和 hashdump不能获得
administrator用户的密码，那我们只能通过令牌窃取进行降权，获得administrator用户的shell，
从而以administrator用户的身份启动某些服务(因为某些服务只能通过administrator用户启动)。

## 三、 **Metasploit** 在令牌窃取中的应用

在这里我们直接通过ms17-010获取到一个System权限的Meterpreter会话，或是通过一些提权手段获取到一个System权限的meterpreter，具体提权手段在后面的文章中会进行讲述。

![image.png](https://image.3001.net/images/20220105/1641312292_61d4702422d18c2646f93.png!small)

在 Metasploit 中集成了一个进行令牌伪造的工具incognito，可以直接进行使用：

    
    
    use incognito
    

![image.png](https://image.3001.net/images/20220105/1641312298_61d4702ac0771503e714c.png!small)

由于当前我们是一个 System 权限，所以我们就可以查看到所有的用户令牌：

    
    
    list_tokens -u
    

[image.png](https://image.3001.net/images/20220105/1641312352_61d470608115b0437d842.png!small)

可以看到当前主机内存在着一个普通域用户和一个域管理用户的令牌，因此我们可以尝试进行窃取。这里我们先窃取一下普通域用户的身份

    
    
    impersonate_token 'C1ay\zhangsan'
    

![image.png](https://image.3001.net/images/20220105/1641312369_61d470713d905ade87b97.png!small)

可以看到窃取成功，但是因为域用户权限太低，无法进行一些高权限的操作。因此我们需要窃取域管理员的令牌：

    
    
    impersonate_token 'C1ay\Administrator'
    

![image.png](https://image.3001.net/images/20220105/1641312399_61d4708fb32dff0caabdd.png!small)

可以看到这时候我们已经成功窃取到了域管理员的令牌，具备域管权限了。因为域管理员可以登录域内任意一台主机，这里也包括域控制器，所以我们也就变相拿到了域控制器10.10.10.8的权限了。

![image.png](https://image.3001.net/images/20220105/1641312411_61d4709b72bd4b25ca34b.png!small)

之后就可以通过定时任务，wmi，psexec、smbexec等方式让域控制器上线到 Metasploit 或者 CobaltStrike 。

如果我们想要返回最初的权限可以只用：

    
    
    rev2self
    

![image.png](https://image.3001.net/images/20220105/1641312422_61d470a6214128adab2f2.png!small)

除了使用 incognito 进行窃取令牌，也可以从进程里窃取令牌，首先使用 ps 命令列出进程 查看进程

![image.png](https://image.3001.net/images/20220105/1641312428_61d470ac018a6d60d91b6.png!small)

用户使用 steal_token pid 窃取令牌就有对应的权限，这里我们尝试窃取域管理员的进程

    
    
    steal_token 2380
    

![image.png](https://image.3001.net/images/20220105/1641312437_61d470b562e4668148ed8.png!small)

可以看到也可以通过窃取域管进程来获取域管权限。

## 四、 **Windows** 平台下 **incognito** 应用

Metasploit 中的 incognito 是从 windows 平台下的 incognito 中
移植过来的，下面来介绍⼀下incognito在windows平台下的使用

下载地址：https://labs.mwrinfosecurity.com/assets/BlogFiles/incognito2.zip

参考手册：https://labs.f-secure.com/assets/142/original/mwri_security-implications-of-windows-access-tokens_2008-04-14.pdf

常用方法如下：

列举当前主机内可用的token：

    
    
    incognito.exe list_tokens -u
    

![image.png](https://image.3001.net/images/20220105/1641312444_61d470bc39f4241584b18.png!small)

窃取某个用户的token：

    
    
    incognito.exe execute [options] <token> <command>
    

这里模拟域管权限的用户：

    
    
    incognito.exe execute -c "C1ay\administrator" cmd.exe
    

![image.png](https://image.3001.net/images/20220105/1641312450_61d470c2e1b11137030d2.png!small)

在窃取成功后，尝试读取域控制器下的c盘的资源

    
    
    dir \\10.10.10.8\c$
    

![image.png](https://image.3001.net/images/20220105/1641312455_61d470c7c41310065cf04.png!small)

## 五、 **CobaltStrike** 在令牌窃取中的应用

首先通过某些手段拿到⼀个 System 权限的 beacon：

![image.png](https://image.3001.net/images/20220105/1641312483_61d470e365c1e5805746b.png!small)

查看当前进程列表：

![image.png](https://image.3001.net/images/20220105/1641312488_61d470e878e870ae37fb7.png!small)

然后在进程列表中选择需要进行窃取的进程，这里我们以窃取域管理员为例：

![image.png](https://image.3001.net/images/20220105/1641312492_61d470ec04f2e3dd6ab4b.png!small)

选择域管理员进程，然后在下方点击inject或者steal token均可，点击inject会创建一个新的会话，具备域管理员权限，效果如下：

![image.png](https://image.3001.net/images/20220105/1641312500_61d470f4873604c7960e7.png!small)

而点击steal token 是使用当前会话窃取进程，不会创建新的会话：

![image.png](https://image.3001.net/images/20220105/1641312506_61d470fad6b08a020eab9.png!small)

可以通过 **rev2self** 恢复原来的身份

![image.png](https://image.3001.net/images/20220105/1641312511_61d470ffafbbed6dd5e93.png!small)

## 六、Empire在令牌窃取中的应用

首先获取一个system权限的agent：

![image.png](https://image.3001.net/images/20220105/1641312518_61d4710620e006e0be29c.png!small)

进入agent中，通过 ps 列出当前的进程列表：

![image.png](https://image.3001.net/images/20220105/1641312522_61d4710acb18deaeb39e7.png!small)

通过steal_token命令来窃取这个域管理令牌

    
    
    steal_token 844
    

![image.png](https://image.3001.net/images/20220105/1641312530_61d47112a25acc5ae5c24.png!small)

可以看到窃取成功，尝试读取域控制器c盘目录的资源

    
    
    shell dir \\10.10.10.8\c$
    

![image.png](https://image.3001.net/images/20220105/1641312535_61d471175c4aa930ce36e.png!small)

## 七、后语

在下篇文章中，我将分别在低权限和高权限下搜集当前机器的密码文件以及各类密码（主机密码、浏览器密码、第三方软件密码），敬请期待！


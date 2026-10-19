# DCShadow

2018年1月24日，在BlueHat安全会议上，安全研究员Benjamin Delpy 和 Vincent Le Toux
公布了针对微软活动目录域的一种新型攻击技术------DCShaow。利用该攻击技术，具有域管理员权限或企业管理员权限的恶意攻击者可以创建恶意域控，然后利用域控间正常同步数据的功能将恶意域控上的恶意对象同步到正在运行的正常域控上。由于执行该攻击操作需要域管理员权限或企业管理员权限，因此该攻击技术通常用于域权限维持。

## 漏洞原理

微软MS-ADTS（MicroSoft Active Directory Technical
Specification）中指出，活动目录是一个依赖于专用服务器架构。域控便是承载此服务的服务器，它托管活动目录对象的数据存储，并与其他的域控互相同步数据，以确保活动目录对象的本地更改在所有域控之间正确的复制。域控间的数据的复制由运行在NTDS服务上一个名为KCC（Knowledge
Consistency Checker）的组件所执行。

KCC的主要功能是生成和维护复制活动目录拓扑、以便于站点内和站点之间的扑拓复制。对于站点内的复制，每个KCC都会生成自己的连接；对于站点之间的复制，每个站点有一个KCC生成所有连接。

两种连接类型，如图所示：

![图片.png](https://image.3001.net/images/20230601/1685626150_64789d26494fb03d918c7.png!small)

![图片.png](https://image.3001.net/images/20230601/1685626161_64789d31d221da3786aca.png!small)

默认情况下，KCC组件每隔15min进行了一次域控间的数据的同步。使用与每个活动目录对象相关联的USN，KCC可以识别环境中发生的变化，并确保域控在复制扑拓中不会被孤立。于是，我们猜测能不能自己注册一个恶意的域控，并注入恶意的对象。这样，KCC在进行域控间数据的同步时，就能将恶意域控上的恶意的对象同步到其他正常的域控上了。

### 1、在活动目录中新增域控

如何在域内注册一个恶意的域控呢？MS-ADTS中指出，在活动目录数据库中通过一些特殊的对象和一定的数据对象层级来标识哪台机器是域控。其中，最关键的便是nTDSDSA对象，该对象用于标识一台主机，是域控的特殊对象，如图所示，是微软官方对于nTDSDSA对象的描述

![图片.png](https://image.3001.net/images/20230601/1685626178_64789d42bfb8dbed00315.png!small)

那么，只要在活动目录中添加一个具有nTDSDSA对象的服务器就好了。拥有什么权限才可以往活动目录中添加nTDSDSA对象呢？通过查看nTDSDSA对象的ACL，可以看到只有域管理员和企业管理员才有权限修改此属性。因此，只有获得域管理员权限或企业管理员权限后，才能在域内添加一个域控。nTDSDSA对象无法通过LDAP进行添加，比如mimikatz中的DCShadow功能模块是通过PRC协议在活动目录中增加nTDSDSA对象的。

### 2、伪造的域控如何被正常域控认可参与域复制

现在已经可以在域内添加一个伪造的恶意域控了，那么该域控如何能被域内正常域控认可并参与域数据的复制呢？需要满足以下两个条件：

  * 被其他服务器信任，也就是说需要拥有有效的身份认证凭据

  * 支持身份认证，以便复制数据时其他正常域控能够连接到伪造的恶意域控上

对于第一个条件，伪造的恶意域控可以通过有效的机器账户提供身份认证凭据，每个nTDSDSA对象都会通过serverReferenceBL属性链接到一个computer对象，还可以实现服务器在DNS环境中的自动注册，这样其他正常的域控就可以定位到伪造的恶意域控上了。

对于第二个条件，可以在域内注册一个SPN，以此来提供身份认证，而需要添加什么的SPN呢？Benjamin Delpy 和 Vincent Le Toux
找到了复制过程中所需的最小的SPN集合，只需要以下两个SPN就可以让其他域控连接到恶意伪造的域控上。

1）目录复制服务（DRS），其SPN格式如下：

    
    
    DPS interface GUID/domain name
    

其中，DRS interface GUID 是一个固定的值，为E3514235-4B06-11D1-AB04-00C04FC2DCD2。而DSA
GUID则是nTDSDSA对象的objectGUID属性的值

2）全局编录服务（GC），用于存储域中的所有对象的信息，其他SPN格式如下：

    
    
    GC/hostname/domain name
    

### 3、强制触发域复制

现在我们已经能够在域内注册一个恶意的伪造域控了，并且能让其他正常的域控信任我们伪造的恶意域控。但是，如何手动强制触发域复制呢？默认域复制操作由KCC组件每隔15min进行一次，显然，等待15min对攻击者来说是不可以接受的，能不能利用其他操作代替KCC组件进行域复制操作呢？后来研究发现，Windows
域服务自带repamin
工具通过调用DRSReplicaAdd函数也能进行域复制操作，mimikatz中的DCShadow模块也是通过DRSReplicaAdd函数强制正常域控发起域复制操作的。

## 漏洞攻击流程

整个漏洞攻击流程如下：

1）通过DCShadow
更改配置架构和注册SPN，从而实现在目标活动目录内注册一个伪造的恶意域控，并且使得伪造的恶意域控能被其他正常的域控认可，能够参与域复制。  
2）在伪造的域控上更改活动目录数据。  
3）强制触发域复制，使得指定的新对象或修改后的属性能够同步进入其他正常域控中，DCShadow 攻击示意图如图所示：

![图片.png](https://image.3001.net/images/20230601/1685626204_64789d5ccd5c8b8895ee1.png!small)

## DCShadow攻击

实验环境如下：

  * 域控系统版本：Windows Server 2012 R2

  * 域控主机名：DC

  * 域控IP：192.168.41.10

  * 域内主机：Win10

  * 域内主机IP：192.168.41.15

  * 域管理员：hack\administrator

  * 域普通用户：hack\jack

攻击扑拓图如下：

![图片.png](https://image.3001.net/images/20230601/1685626217_64789d69e9869758e8310.png!small)

域内主机上已经登录一个普通域用户hack\jack，其具有本地管理员权限。以本地管理员权限打开一个cmd窗口，运行mimikatz.exe执行如下的命令，使得mimikatz.exe当前进程具有System权限

    
    
    token::whoami
    

![图片.png](https://image.3001.net/images/20230601/1685626228_64789d74db931766d7b65.png!small)

或者使用psexec执行如下的命令获取一个具有System权限的cmd窗口，结果如图所示：

    
    
    psexec.exe -i -s cmd.exe
    

![图片.png](https://image.3001.net/images/20230601/1685626240_64789d8031d765c1c6526.png!small)

然后使用mimikatz执行如下的命令进行数据的更改监听，修改用户jack的primarygroupid的值为512，即将其添加到Domain
Admins组中，结果如图所示：

    
    
    #将用户jack的primarygroupid值赋值为512，即将其添加到Domain Admins组中
    lsadump::dcshadow /object:CN=jack,CN=Users,DC=hack,DC=com /attribute:primarygroupid /value:512
    

![图片.png](https://image.3001.net/images/20230601/1685626254_64789d8e3f8de04f4e961.png!small)

也可以执行其他活动目录的数据更改语句，常见的组ID和对应组的关系如图所示：

![图片.png](https://image.3001.net/images/20230601/1685626302_64789dbe17b6d19b95fc6.png!small)

然后打开第二个窗口，这个窗口需要域管理员权限，我们用psexec以域管理员权限hack\administrator身份打开一个cmd窗口，然后执行如下的命令触发正常域控同步数据，如图所示：

    
    
    psexec.exe -u hack\administrator cmd
    

![图片.png](https://image.3001.net/images/20230601/1685626316_64789dcc498ace735e432.png!small)

执行如下的命令触发域复制：

    
    
    lsadump::dcshadow /push
    

![图片.png](https://image.3001.net/images/20230601/1685626329_64789dd9d17f5a237e6ce.png!small)

如图所示，可以看到第一个监听窗口更新：

![图片.png](https://image.3001.net/images/20230601/1685626342_64789de65fe1be8ac0c61.png!small)

对比前后Domian Admins 组内用户发现jack用户已经被添加进来了，如图所示

![图片.png](https://image.3001.net/images/20230601/1685626354_64789df22727b7cf8c730.png!small)

## DCShadow攻击防御

对于防守方或蓝队来说，如何针对DCShadow 攻击进行防御呢？操作如下：

1）及时修复域内漏洞，更新最新补丁，让攻击者无法获得域管理员权限或企业管理员权限，自然也就无法进行DCShadow攻击了。  
2）对于攻击者在获得高权限后进行DCShadow攻击，并没有一个很好的办法来进行防御，但是蓝队可以针对以下的内容进行监控

  * 实时监控Domain Controllers 组织单元中正常的域控对象和站点容器中的nTDSDSA对象，确保两者相配

  * 实时监控域中提供了以GC字符串开头的SPN

  * 实时监控域中提供了目录复制服务但是又不在正常域控中的主机


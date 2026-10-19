通常所说的内网渗透测试，很大程度上就是域渗透测试。搭建域渗透测试环境，在Windows的活动目录环境下进行一系列操作，掌握其操作方法和运行机制，对内网的安全维护有很大的帮助。常见的域环境是使用Windows
Server2012 R2、Windows7或者Windows Server 2008操作系统搭建的Windows域环境。

## 一、前言

在上一篇文章中给大家介绍了一些内网的基础知识，在本篇文章中，我将带领大家通过搭建一个较为接近真实环境的内网环境来加深大家对域的理解。

## 二、环境说明

 **网络适配器的三种配置问题**

  * 桥接模式，虚拟机在网络中将会是一个独立的机器，占有一个自己的IP地址。

  * NAT模式，这是最常用的配置，也是新创建的虚拟机的默认配置，虚拟机和主机共用同一个IP地址。

  * Host-only模式，配置供个体使用的渗透测试实验环境，推荐使用“Host-only”模式作为网络适配器的设置，我们可以通过它访问VM网络，也就是虚拟机只可以与物理机及其他配置了相同网段地址的主机之间建立连接，不能出网。

在本篇文章中我们将搭建一个较为复杂的域环境，大致结构如下：

![image.png](https://image.3001.net/images/20211229/1640715717_61cb55c58a6f8fb10fcb8.png!small)

在搭建域环境前应该先下载对应的系统镜像文件，这里推荐一个网站：

[MSDN, 我告诉你 - 做一个安静的工具站 (itellyou.cn)](https://msdn.itellyou.cn/)

## 二、父域控制器搭建

1、在虚拟网络编辑器中添加一个网卡，类型为仅主机模式，子网地址为10.10.10.0/24，然后右键虚拟机点击设置，将网络适配器模式修改为刚刚添加的网卡。

![image.png](https://image.3001.net/images/20211229/1640715724_61cb55cca989bbab2d50b.png!small)

2、然后设置一下主域控服务器的静态IP地址，不然后面无法添加DNS服务，来到网络适配器选项：

    
    
    IP：10.10.10.8
    子网掩码：255.255.255.0
    默认网关：10.10.10.1
    DNS：10.10.10.8（这个需要和IP地址一致）
    

![image.png](https://image.3001.net/images/20211229/1640715734_61cb55d6048e8936e3f30.png!small)

3、设置一下主机名，右键我的电脑点击属性，继续点击更改，将主机名修改为DC1，在将本机升级为域控制器后，计算机全名会自动变成“DC1.c1ay.lab”。

![image.png](https://image.3001.net/images/20211229/1640715744_61cb55e0e42e83eb8d628.png!small)

设置完主机名后，系统会提示需要重新启动，点击确认即可。

![image.png](https://image.3001.net/images/20211229/1640715755_61cb55ebb523793930016.png!small)

重启后可以看到，机器名已经成功修改。

![image.png](https://image.3001.net/images/20211229/1640715764_61cb55f42674d9c1e67c1.png!small)

4、点击"开始"->"服务器管理器"

![image.png](https://image.3001.net/images/20211229/1640715770_61cb55fa1c176b50ac661.png!small)

5、点击添加角色和功能

![image.png](https://image.3001.net/images/20211229/1640715775_61cb55ff9945f01af6caf.png!small)

在"开始之前"部分，保持默认设置。单击"下一步"按钮，进入"安装类型"部分，选择"基于角色或者基于功能的安装"选项。

![image.png](https://image.3001.net/images/20211229/1640715786_61cb560add208551fa60f.png!small)

单击"下一步"按钮，进入"服务器选择"部分。目前，在服务器池只有当前这台机器，保持默认设置。

![image.png](https://image.3001.net/images/20211229/1640715792_61cb56108fd1e53c14a88.png!small)

单击"下一步"按钮，在"服务器角色"部分勾选"Active Directory域服务"和"DNS服务器"复选框，如下图。

![image.png](https://image.3001.net/images/20211229/1640715800_61cb561820c62f804cc90.png!small)

服务器如果出现安装失败的情况：

![image.png](https://image.3001.net/images/20211229/1640715808_61cb56203ac45acc8d60c.png!small)

因为AD域服务属于服务器功能，所以需要早windows server 机器的服务中开启 “Server”服务，开启步骤如下：

依次点击"控制面板"->"系统与安全”->"管理工具"->"服务"（或者直接通过win+r后输入"services.msc"），在其中选择 “Server”
，双击进入属性，将启动类型改为 "自动"，然后点击"应用"进行启动服务。

在"功能"页面保持默认设置，一直单击"下一步"按钮，进入"确认"部分。确认需要安装的组件，勾选"如果需要，自动重新启动目标服务器"复选框，如下图：

![image.png](https://image.3001.net/images/20211229/1640715816_61cb5628c1cc2ddb4ff02.png!small)

最后点击单击"安装按钮"。

![image.png](https://image.3001.net/images/20211229/1640715822_61cb562e585e486c2bb96.png!small)

在安装完成后点击将此服务器提示为域控制器进行后续操作，

![image.png](https://image.3001.net/images/20211229/1640715828_61cb56342f9b0968406b3.png!small)

6、AD域服务配置

首先在"部署配置"部分单击选中"添加新林(F)"单选按钮，然后输入根域名"c1ay.lab"（必须使用符合DNS命名约定的根域名），如下图。

![image.png](https://image.3001.net/images/20211229/1640715838_61cb563e651a72cb9da26.png!small)

在"域控制器选项"部分，将林功能级别、域功能级别都设置为"Windows Server 2012
R2"。创建域林时，在默认情况下应选择DNS服务器，林中的第一个域控制器必须是全局目录服务器且不能是只读域控制器（RODC）。然后，设置目录服务还原模式的密码（在开机进入安全模式修复活动目录数据库时将使用此密码），如下图：

![image.png](https://image.3001.net/images/20211229/1640715857_61cb5651660bcf4c1e1b2.png!small)

在"DNS选项"部分会出现关于DNS的警告。不必理会该警告，保持默认设置即可。

![image.png](https://image.3001.net/images/20211229/1640715849_61cb56490b1d0adceeb22.png!small)

单击"下一步"按钮，进入"其他选项"部分。在"NetBIOS域名"（不支持DNS域名的旧版本操作系统，例如Windows
98、NT，需要通过NetBIOS域名进行通信）部分保持默认设置。

![image.png](https://image.3001.net/images/20211229/1640715871_61cb565f2672565d7a156.png!small)

单击"下一步"按钮，进入"路径"部分，指定数据库、日志、SYSVOL文件夹的位置，其他选项保持默认设置。

![image.png](https://image.3001.net/images/20211229/1640715877_61cb5665943b85e31f988.png!small)

在查询选项中点击下一步，设置保持默认即可。

![image.png](https://image.3001.net/images/20211229/1640715884_61cb566c4c03d40e3b1cd.png!small)

在先决条件检查中，如果遇到报错情况：域控制器升级的先决条件验证失败。 本地Administrator帐户将成为域 Administrator
帐户。无法新建域，因为本地Administrator帐户密码不符合要求，原因是因为 Administrator
当前机器没有设置密码或密码是⼀个弱密码，我们只需要给 administrator
设置⼀个强密码即可！我们以管理员权限打开命令提示符给administrator 设置⼀个新密码：

    
    
    net user administrator Admin12345
    

![image.png](https://image.3001.net/images/20211229/1640715895_61cb567789b314a4da2d7.png!small)

在通过先决条件检查后点击安装即可，等待域控制器安装完毕后它会重启⼀遍机器。

重启完成后打开服务器管理，可以看到成功添加上了AD DS和 DNS服务。

![image.png](https://image.3001.net/images/20211229/1640715904_61cb56807392f4e60c72d.png!small)

打开网络适配器，会看到再重启以后，dns自动会被修改为127.0.0.1，需要手动进行修改。

![image.png](https://image.3001.net/images/20211229/1640715919_61cb568fcab25f0cc8c5c.png!small)

手动修改后如下，然后重启电脑即可。

![image.png](https://image.3001.net/images/20211229/1640715932_61cb569cce36e144422f4.png!small)

通过 "net config workstation"命令可以看到该主机已经成功登录到域环境中。

![image.png](https://image.3001.net/images/20211229/1640715939_61cb56a36197c54e172c7.png!small)

7、配置父域控制器的DNS区域传输

现在父域控制器和 DNS服务集成，为了让后期搭建完辅域控制器的 DNS 同步主域控制器 DNS，需要把主域控制器的 DNS
服务器_msdcs.c1ay.lab和 c1ay.lab 的起始授权机构(SOA)区域传送设置成允许:

在开始菜单中打开服务管理器，点击工具中的DNS打开dns管理器，依次点击DC1->正向查找区域。

![image.png](https://image.3001.net/images/20211229/1640715946_61cb56aaab3dc5891fad0.png!small)

在_msdcs.c1ay.lab中右键起始授权机构(SOA)，右键属性，在区域传送中勾选允许区域传送，然后点击应用并确定即可。

![image.png](https://image.3001.net/images/20211229/1640715952_61cb56b052bf6861be182.png!small)

对c1ay.lab也执行上述相同的操作。

![image.png](https://image.3001.net/images/20211229/1640715963_61cb56bb3ba2ce0b73e0d.png!small)

至此父域控制器搭建完成。

## 三、辅域控制器搭建

问：为什么要搭建一个辅域控制器呢？

答：无论是在一个大型企业或是集团中，当我们安装了主域控制器之后，为了防止主域控制器临时出现故障，引起一系列的问题，所以我们就需要⼀台辅域控制器临时进行帮忙，也就是做容灾。

1、右键虚拟机点击设置，将网络适配器模式修改为与父域控制相同的模式。

![image.png](https://image.3001.net/images/20211229/1640715974_61cb56c61365f84d61e08.png!small)

2、设置静态IP地址，将DNS指向父域控制器的IP地址。

    
    
    IP：10.10.10.10
    子网掩码：255.255.255.0
    默认网关：10.10.10.1
    DNS：10.10.10.8（这个需要和域控IP地址一致）
    

![image.png](https://image.3001.net/images/20211229/1640715979_61cb56cbd7fde24bbc5bf.png!small)

3、修改计算机名

![image.png](https://image.3001.net/images/20211229/1640715985_61cb56d12566778d974f1.png!small)

4、设置本地管理员administrator的密码

    
    
    net user administrator Admin123
    

![image.png](https://image.3001.net/images/20211229/1640715992_61cb56d8ed647bba1c59d.png!small)

5、将辅域控制器添加到域，和之前的操作一样

![image.png](https://image.3001.net/images/20211229/1640715999_61cb56df823c2de52342c.png!small)

这时候需要输入域管账号密码即可成功加入c1ay.lab域。

![image.png](https://image.3001.net/images/20211229/1640716006_61cb56e6694e2aa3563e5.png!small)

6、加入域后需要进行重启，然后来到"服务器管理器"，还是和搭建主域控制器⼀样的操作：

![image.png](https://image.3001.net/images/20211229/1640716011_61cb56eb2758f7ec9f8c0.png!small)

点击将此服务器升级为域控制器，进入AD域服务配置向导。

7、AD域服务配置向导

我们需要选择将域控制器添加到现有域
，域名填写主域的域名：c1ay.lab，我们需要将BACK\administrator（当前用户）修改为主域的域管账户密码：(这里需要注意的是，如果辅助域控之前没有加入主域控制器，我的当前登录凭据为灰色，只能选择备用凭据进行验证)

![image.png](https://image.3001.net/images/20211229/1640716019_61cb56f37353b1800d439.png!small)

点击下一步来到"域控制器选项"这⾥，我们需要选择默认选择域名系统（DNS）服务器和全局编录，填入新的DSRM密码：admin!@#45。

![image.png](https://image.3001.net/images/20211229/1640716026_61cb56fa0ac75294e8530.png!small)

在DNS选项以后依次保持默认，一直到先决条件检查，如果之前未设置管理员密码为强密码会提示错误，因为我们之前已经通过命令设置好了强密码了，所以直接点击安装即可。

![image.png](https://image.3001.net/images/20211229/1640716032_61cb5700e68a4a4464a48.png!small)

安装好后，机器会自动进行重启。

8、重新配置DNS

    
    
    ⾸选DNS为：10.10.10.10（辅域DNS）
    备⽤DNS为：10.10.10.8⽗域DNS）
    

![image.png](https://image.3001.net/images/20211229/1640716041_61cb57096f9a2c0cd4a86.png!small)

9、配置辅控制器的DNS区域传输

辅域控服务器重启后检查DNS服务器是否已获取到主域控制器传输过来的DNS服务器配置，检查正常后需要把辅域控制器的DNS服务器
_msdcs.c1ay.lab和 c1ay.lab 的起始授权机构(SOA)区域传送设置成允许：

![image.png](https://image.3001.net/images/20211229/1640716049_61cb571186ada643bbb68.png!small)

![image.png](https://image.3001.net/images/20211229/1640716053_61cb57151c951eab634ba.png!small)

到此辅域就安装完成，需要注意的是安装辅域控制器，如果主域控制器DNS和AD集成，辅域控制器会在安装AD后自动同步DNS记录。

## 四、父域添加域机器和用户

这个时候我们搭建好了主域控制器和辅助域控制器，但是域用户很少，这里我们添加几个新的域用户来体现真实环境。

### 4.1 添加域用户

1、首先查看当前域内的用户

    
    
    net user /domain
    

![image.png](https://image.3001.net/images/20211229/1640716059_61cb571bc8f374cb79ae3.png!small)

可以看到只有默认的几个用户。

2、在开始页面里打开服务器管理器，在工具里面选择Active Directory 用户和计算机，右键点击Users点击新建用户。

![image.png](https://image.3001.net/images/20211229/1640716064_61cb5720316c581c6dba7.png!small)

输入需要创建的用户名后，点击下一步。

![image.png](https://image.3001.net/images/20211229/1640716068_61cb5724afe672a3121b5.png!small)

设置密码为Aa123456，将密码设置为永不过期。

![image.png](https://image.3001.net/images/20211229/1640716073_61cb57298d63def83780f.png!small)

这时候就可以看到成功创建了tom用户。

![image.png](https://image.3001.net/images/20211229/1640716079_61cb572f8023584e38447.png!small)

以相同的方式再创建Bob，zhangsan用户。

![image.png](https://image.3001.net/images/20211229/1640716088_61cb5738a999d9f82d140.png!small)

这时候可以看到域用户就创建的差不多了，接下来就要将机器添加到域中。

### 4.2 添加域机器

首先查看域内机器。

    
    
    net view /domain
    

如果服务器上并没有开启Computer Browser服务，会返回6118错误码，如下图。

![image.png](https://image.3001.net/images/20211229/1640716096_61cb5740c3b6d4ad308a9.png!small)

解决方式：

  1. 关闭防火墙

  2. 在命令行输入services.msc打开服务

  3. 开启Server、WorkStation以及Computer Browser服务，将Computer Browser服务属性设置为"手动启动即可"。

![image.png](https://image.3001.net/images/20211229/1640716104_61cb5748ec1935073ca74.png!small)

再次输入命令，可以看到可以正常获取到域内的机器名。

![image.png](https://image.3001.net/images/20211229/1640716111_61cb574faa75cebcef98d.png!small)

 **（1）将Windows 2008 系统添加到域内**

1、首先需要将网络适配器模式修改为与主域控制相同的模式。

![image.png](https://image.3001.net/images/20211229/1640716118_61cb57561e8b656fe0dda.png!small)

2、设置静态IP，将DNS指向域控

    
    
    IP：10.10.10.13
    子网掩码：255.255.255.0
    默认网关：10.10.10.1
    DNS：10.10.10.8（这个需要和域控IP地址一致）
    

![image.png](https://image.3001.net/images/20211229/1640716125_61cb575db48548b4a5b60.png!small)

3、设置主机名并加入域

![image.png](https://image.3001.net/images/20211229/1640716130_61cb57627f8bdd88aed5a.png!small)

这里我们使用刚刚新添加的域用户tom的凭证加入域。

![image.png](https://image.3001.net/images/20211229/1640716137_61cb576909419b30cffe1.png!small)

成功添加进域后，会自动进行重启系统。

![image.png](https://image.3001.net/images/20211229/1640716143_61cb576f4107a407748fc.png!small)

然后使用tom域用户进行登录。

![image.png](https://image.3001.net/images/20211229/1640716151_61cb577785c762d3535c4.png!small)![image.png](https://image.3001.net/images/20211229/1640716153_61cb57794780e38e3cb16.png!small)

这时候在域控制器上可以看到 Windows 2008 机器成功加入到了域内。

![image.png](https://image.3001.net/images/20211229/1640716159_61cb577f91300a2df0071.png!small)

 **（2）将Windows 7 系统添加到域内**

1、将网络适配器模式修改为与主域控制相同的模式。

![image.png](https://image.3001.net/images/20211229/1640716170_61cb578a9db64550b8aa7.png!small)

2、设置静态IP地址，将DNS指向域控IP

    
    
    IP：10.10.10.23
    子网掩码：255.255.255.0
    默认网关：10.10.10.1
    DNS：10.10.10.8（这个需要和域控IP地址一致）
    

![image.png](https://image.3001.net/images/20211229/1640716177_61cb57910512f6e296624.png!small)

3、设置主机名，将主机添加到域内

![image.png](https://image.3001.net/images/20211229/1640716182_61cb57969426ac750b532.png!small)

![image.png](https://image.3001.net/images/20211229/1640716188_61cb579c4e619a2c336e3.png!small)

在域控上查看，发现win7成功添加到了域内

![image.png](https://image.3001.net/images/20211229/1640716192_61cb57a0f34f68df329b7.png!small)

至此，内网环境搭建上篇完成，在下篇会继续介绍子域控搭建以及在不同林之间该怎么建立林信任关系。

## 五、后语

在本篇文章中，我为大家介绍了父域控制器和辅域控制器详细的搭建方式，在下一篇文章中，我将继续为大家介绍子域控制器的搭建方式以及如何在一台Windows
2008 的服务器部署域控，并建立DNS辅助区域及林信任。


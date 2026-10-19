**AlienVault公司的业务主要针对中小型企业提供统一安全管理平台(USM)、开放式威胁情报交换平台（OTX）等网络安全产品，AlienVault开放威胁交换(OTX)是全球权威的开放威胁信息共享和分析网络。OTX提供了一个由威胁研究人员和安全专业人员组成的全球社区，有来自140个国家的5万多名参与者，每天贡献400多万个威胁指标。**  

AlienVault还提供了一个由OTX免费的全球威胁仪表盘，可以在<https://www.alienvault.com/open-threat-exchange/dashboard#/threat> /top获得，该仪表盘展示了来自OTX社区的一些威胁数据。接下来介绍个人对OTX的使用：

## 一、使用电子邮件地址创建OTX帐户（如下图，可以选择使用google或Twitter账号）

1.访问<https://otx.alienvault.com>。

2.在主页的右上角，点击注册。填写出现的表单，输入以下数据：

a.Username；

b.电子邮件地址；

c.您选择的密码；

3.收到邮件后，单击带您到OTX确认页面的链接，然后单击Confirm。这将把您带到OTX主页(<https://otx.alienvault.com/dashboard/new/>)，在那里您将看到所有当前的脉冲活动；

![312312.png](https://image.3001.net/images/20190131/1548921576572.png!small)![6543.png](https://image.3001.net/images/20190131/15489217527203.png!small)

## 二、登录及使用

登录可使用上面创建的账号进行登录，也可使用已经有的Google或Twitter账号，登陆后可看到最新推送的内容，分别是PULSES、ACTIVITY、SUGGESTED
EDITS，你关注的内容，你的动态和参与编辑的内容。

可以通过编辑左侧的group增加你的群组、关注群组。

通过右上角setting和profile来设置个人喜好内容：

![2345678.png](https://image.3001.net/images/20190131/15489221214307.png!small)

![56754554.png](https://image.3001.net/images/20190131/15489229765970.png!small)

## 三、查看图表

可以从仪表盘界面查看当前威胁情况、统计分类、最新推送信息、安全新闻等，注：有些内容无法查看，由于国家法规，不建议翻墙使用，哈哈哈哈~~~

还可以通过搜索来查找比较感兴趣的威胁内容：

![4567432.png](https://image.3001.net/images/20190131/15489254346390.png!small)

## 四、浏览详细内容和其他操作

右上角操作对应home的编辑、关注、群组、下载克隆等。

![5454.png](https://image.3001.net/images/20190131/1548925555477.png!small)

## 五、着重介绍

使用OTX的社区支持的威胁情报来扫描端点，寻找已知的折衷指标(IOCs)。

OTX端点安全使用与昂贵的端点安全工具和DIY开源代理相同的基于代理的方法，它具有免费、简单、可靠的特性。

1.首先，下载并安装AlienVault代理到您想要监控的Windows或Linux设备上。本文以windows为例。注意：windows使用powershell方式安装，支持3.0以上版本。

![の1424.png](https://image.3001.net/images/20190131/15489256648120.png!small)

2.powershell运行安装脚本，发现报错。

![87654.png](https://image.3001.net/images/20190131/15489256849069.png!small)

3.使用管理员运行脚本，并执行set-ExecutionPolicy RemoteSigned开启脚本执行策略。

![345667876.png](https://image.3001.net/images/20190131/15489257059046.png!small)

4.执行成功后，可在账户页面看到终端信息。

![9876.png](https://image.3001.net/images/20190131/15489257326781.png!small)

5.执行扫描，可选择多种扫描方式，包括基于可选pulse的、yara策略的、基于所有策略等、基于订阅更新的等，我们先选择所有策略运行，可通过history查看扫描记录和风险内容。

![67564534.png](https://image.3001.net/images/20190131/15489257502860.png!small)![5245.png](https://image.3001.net/images/20190131/15489257642772.png!small)![24533423.png](https://image.3001.net/images/20190131/15489257831101.png!small)![74643.png](https://image.3001.net/images/20190131/15489257957509.png!small)

## 结束语

AlienVault的特工准备好寻找威胁，通过选择在一个或多个OTX中查找IOCs的预定义查询，可以在OTX的任何端点上启动查询。一旦启动，AlienVault代理将执行查询，查询结果将显示在OTX中的摘要页面上。

注意：在OTX中，没有一种机制可以持续或自动监控端点上出现的威胁。您必须手动启动每个扫描任务。

 ***本文作者：破天·张坤，转载请注明来自FreeBuf.COM**


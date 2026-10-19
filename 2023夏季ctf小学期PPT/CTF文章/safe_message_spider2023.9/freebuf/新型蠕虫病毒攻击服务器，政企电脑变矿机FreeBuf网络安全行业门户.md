##  一、概述

**近日，火绒安全团队截获蠕虫病毒“MinerGuard”新变种，严重威胁企业用户。该病毒通过网络服务器漏洞以及暴力破解服务器的方式迅速传播，并且可跨平台（Windows、linux）交叉感染。病毒入侵电脑后，会释放挖矿病毒挖取门罗币。此外，病毒作者可随时通过远程服务器更新病毒模块，甚至利用以太坊（区块链平台）钱包更新病毒服务器地址。**

火绒工程师分析发现，病毒主要利用网络服务器进行传播：通过ElasticSearch，Weblogic，Spring，Redis，ThinkPHP等多个网络服务软件漏洞传播；对SQL
Server网络服务器进行暴力破解后传播。此外，该蠕虫病毒可以在Windows和Linux两个系统平台中交叉感染。这些传播方式导致使用上述服务器和系统的企业用户面临被攻击的威胁。

病毒入侵电脑后，会释放挖矿病毒挖取门罗币，病毒作者可以随时通过远程服务器派发新的病毒模块。值得一提的是，该病毒还可以通过以太坊钱包更新病毒服务器地址，并且无法被实名查询，而且信息永久有效。

目前，火绒"企业版"和"个人版"最新版均可彻底查杀蠕虫病毒“MinerGuard”。同时，受此类病毒威胁较大的企业用户，我们建议申请安装"火绒企业版"，可有效防御局域网内病毒屡杀不绝的难题。目前火绒免费提供三个月试用期，欢迎大家前来体验试用。

## 二、样本分析

近期，火绒安全实验室截获到一批蠕虫病毒样本，该病毒使用Go语言编写。病毒可以通过漏洞攻击、暴力破解等手段进行传播，且可以同时进行Windows和Linux操作系统的交叉传播。病毒具有更新功能，可以通过远程C&C服务器（hxxp://43.245.222.57:8667）请求更新病毒模块。

有意思的是，病毒除了可以通过C&C服务器进行更新外，还可以通过以太坊转账信息中的input字段内容临时更新C&C服务器地址，之后派发新的病毒模块到本地执行。

用来获取C&C服务器地址的以太坊钱包地址为：0xb017eFb3339FfE0EB3dBF799Db6cb065376fFEda。

在获取C&C服务器地址时，只有该钱包地址向外（包括自己）的交易记录才会生效，所以只有该钱包地址的拥有者才可以执行C&C服务器地址更新的操作。

病毒传播及控制流程如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/203915gk9ri343lfbhcbch.png)

## 病毒传播及控制流程

病毒模块功能描述，如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/203926hovvr8vn6v7vgoze.png)

病毒模块名及功能描述

### networkservice组件

networkservice是主要的传播攻击模块，由于Windows和Linux平台样本代码逻辑相同，分析中仅以Windows平台样本为例。

该模块的主要攻击方式分为漏洞攻击和暴力破解，其中漏洞攻击逻辑中包含有多个网络服务漏洞，包括：ElasticSearch，Weblogic，Spring，Redis，ThinkPHP等，友商在之前报告中已经进行过介绍，此处不进行过多赘述。

暴力破解主要针对Microsoft SQL Server。

networkservice攻击模块主要函数列表如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/203938vrn222e2kk21yydk.png)

漏洞利用函数列表

如果终端被攻击成功，且终端为Winodws 系统，则会执行由Base64编码过的Powershell
代码，用于下载执行（hxxp://43.245.222.57:8667/6H******/init.ps1）病毒组件，init和update脚本内容完全一致，同为下载部署病毒模块，将在介绍病毒更新功能时进行叙述。

如果是Linux
系统，当终端被攻击后，则会下载执行init.sh（hxxp://43.245.222.57:8667/6H******/init.sh）。相关代码如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/203957m0nslffhsfksbsmm.png)

漏洞传播相关代码

### sysguard模块

sysguard模块主要功能是更新C&C服务器地址，并且可以确保病毒持久化驻留中毒终端。该进程被启动后会创建4个线程，主要被用于C&C服务器地址更新、保护启动项、进程守护、版本升级，这4个线程会在下文分别介绍。

相关代码如下图所示：
![](https://attach.52pojie.cn/forum/201904/19/204009iqkcxucp767jvvxv.png)

线程创建

该病毒还会连接C&C服务器上传病毒运行日志，上传信息包括：中毒终端系统类型（Windows/Linux）、病毒模块下发状态等。

相关代码如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/204021meueegineg5g2cf2.png)

上传终端状态

### 服务器地址更新

该线程主要负责在C&C服务器地址失效后，通过指定的以太坊钱包地址：0xb017eFb3339FfE0EB3dBF799Db6cb065376fFEda，获取到下一个可用的C&C服务器地址，Linux和Winodws代码逻辑相同。

相关代码如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/204032ws532x2xsws3k8s2.png)

服务器地址更新代码

首先检查默认的远程C&C服务器（hxxp://43.245.222.57:8667/6H******/CheckCC）连接是否正常，如果无法连接，则会通过hxxp://api.etherscan.io查询指定钱包地址的交易记录，如果from字段中存放的钱包地址为0xb017eFb3339FfE0EB3dBF799Db6cb065376fFEda，则会获取交易记录中“input”字段中存放的C&C服务器地址。但截至到目前，黑客尚未通过此方式进行过C&C服务器地址更新。

相关代码如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/204044qn0bzbdd5vk6h0y6.png)

获取钱包交易记录信息

更新C&C服务器地址相关代码，如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/204056t8j6zskgvf3nrgzs.png)

更新C&C服务器地址

获取到新的地址后，会从该地址下载执行病毒脚本。

例如：hxxp://new_url_cc_server/6H******/init.ps1，由于病毒服务器地址尚未进行过更新
，暂用new_url_cc_server替代C&C服务器地址。

相关代码如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/204104vbmtr1mq1emm8lx0.png)

下载执行病毒脚本

### 权限维持

该线程会在病毒计划任务被删除后继续添加病毒计划任务，首先会获取所有计划任务，如果指定字符串不存在，则会调用升级脚本再次下载执行病毒模块，升级相关代码会在下文进行叙述。

相关代码如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/204117bb2yjqxkchqrrlqh.png)

获取所有计划任务

### 进程守护

该线程的主要功能是保证用于漏洞攻击的networkservice进程和用于挖矿的sysupdate进程在被结束后，可以即时启动。通过WMI查询进程名，如果指定进程不存在，则会再次调用病毒升级逻辑代码。

相关代码如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/204130wn5io3okk5mc6cms.png)

指定进程查询

### 版本升级

该线程的主要功能是用于病毒的版本更新，首先会连接C&C服务器：hxxp://43.245.222.57:8667/6H******/favorite.ico下载favorite.ico文件，此文件包含有最新版本的病毒组件MD5值。

文件内容如下图所示:  
![](https://attach.52pojie.cn/forum/201904/19/204142pk2nqo6bqj6jbk50.png)

病毒组件MD5值

通过计算本地病毒组件的MD5值与云端获取的MD5进行比较，可以判断病毒模块是否需要升级。

组件版本检查代码如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/204153m3aayjsza06aojjj.png)

检查更新

如果本地文件的MD5值与云端获取到的值不相同，那么会连接远程C&C服务器：hxxp://43.245.222.57:8667/6H******/update.ps1下载update.ps1文件并执行。

相关代码如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/204207lpbnkvvnd8yziq88.png)

下载执行PowerShell脚本

update.ps1在被执行后，首先会更新病毒组件，然后将自己拷贝到用户目录下，并注册计划任务，之后每30分钟执行一次。

相关代码如下图所示：  
![](https://attach.52pojie.cn/forum/201904/19/204219qn0jnjxwmpzwpusj.png)

用于更新的PowerShell脚本

## 三、附录

### 样本hash：  
![](https://attach.52pojie.cn/forum/201904/19/204233itxh3a7y2xt52mc7.png)

## 参考文献

《新型挖矿蠕虫PsMiner利用多个高危漏洞大肆传播》—— 360安全大脑

《Linux挖矿病毒DDG改造后重出江湖，蔓延Windows平台》—— 深信服千里目实验室

***本文作者：火绒安全，转载请注明来自FreeBuf.COM**


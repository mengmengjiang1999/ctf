**能够感染互联网环境中的系统的数据管理员勒索软件是由最近在暗网出现的一个新的勒索服务(ransomware-as-a-service**
**，RAAS** **）产生的。**

前几天，一个新的ransomware-as-a-service（RaaS）服务出现在暗网，现在同样的恶意软件样本，被称为数据管理员勒索软件，它生成平台已经在互联网环境中发现。

数据管理员勒索软件是在上周由一个Bleeping Computer的研究员发现的。

> 新的暗网RaaS。目前离线，但要留意。
>
> [http://3whyfziey2vr4lyq]()[.]onion
> [pic.twitter.com/KDmyGjN0Fw](https://t.co/KDmyGjN0Fw)
>
> ——Catalin Cimpanu（@ campuscodi）2018年2月20日

“该服务于2月12日推出但实际上直到2月20日才上线，到了2月22日，安全研究人员已经报告看到了第一个受害者抱怨被感染。”Bleeping
Computer的博客显示。

任何人都可以免费注册并激活RaaS服务账户，并且创造他们自己的勒索软件样本。

这个勒索软件用双重AES和RSA-4096算法加密文件，它还试图加密所有网络广播。一旦文件被加密，这个恶意代码就会加密文件并且在每一个文件夹中放置一封勒索信（“！！！#####
= = =ReadMe = = = #####！！！.htm）。

数据管理员RaaS后面的经营商要求其用户生成其样品分发，反过来，他们提供了一份赎金费用当受害者支付赎金。目前还不清楚向用户提供赎金的百分比。

子公司只需要提供他们的比特币钱包地址，生成加密的二进制，并连同样本解密一起下载恶意软件。  
![Data-Keeper-RaaS-login.png](https://image.3001.net/images/20180226/15196412808707.png!small)  

根据在malware hunter 团队中一个分析了恶意软件的研究员的说法，即便它是用.NET语言书写的，它的质量也非常高。  

  

> 所以，看着数据管理员勒索软件…
>
> 重要的/值得注意的事情是：
>
> ——它是安全的。
>
> ——它是少数使用 PsExec 的 RWs 之一, 并且它应该是第一使用PsExec 的 .NET RaaS。
>
> ——在此之前没有看到任何.NET勒索软件能够像这样被保护。@BleepinComputer @demonslay335
>
> ——MalwareHunterTeam（@ malwrhunterteam）2018年2月22日

> 我们昨天看到的ITW样品由四层组成：
>
> 第一层是一个exe文件，这可以用任意名称降低另一个exe到% LocalAppData
> %以及.ben扩展，然后执行它（WindowStyle.Hidden, Priority.BelowNormal。）。
>
> 第二exe将加载一个dll，加载的dll将加载另一个dll。
>
> ——MalwareHunterTeam（@ malwrhunterteam）2018年2月23日

> 每一层都有自定义字符串和资源保护。然后每一层被ConfuserEx保护。
>
> 听起来像是有人妄想…
>
> ——MalwareHunterTeam（@ malwrhunterteam）2018年2月23日  
>

数据管理员勒索软件是复杂的，它是使用PsExec工具的少数几个勒索软件之一。数据管理员勒索软件使用PsExec在受害者的网络的其他机器上执行恶意软件。

数据管理员勒索软件的实施的一个非常有趣的特点是它并没有为加密的文件添加一个额外的文件扩展名。有了这个技巧，除非受害者试图打开这个文件，否则他不会直到这些文件是否被加密。

“这种方式实际上是很聪明的，因为它引入了对每个受害者的一种不确定感，用户不知道勒索软件对他们的个人电脑造成了多么大的损失。”Bleeping
Computer继续说道。

RAAS平台另外一个奇异的点可能就是分支机构可以自行选择要加密的文件类型，分支机构同样也可以设置赎金的数额。

该平台使用了Tor网络承载的支付服务，这是许多恶意软件的常见选择。

据研究人员介绍，许多已经签署了数据管理员RAAS的骗子在四处传播被感染的二进制文件。

在MalwareHunter的专家告诉Bleening Computer，其中一个分发勒索软件的小组是在家庭自动化系统的服务器上托管恶意代码。

进一步的技术细节和IOCs(the Indicators of Compromise)都包括在Bleeping Computer发布的文章中

最近几周发现，其他的RAAS服务是通过暗网专家GandCrab和 Saturn发布。

参考来源：[security
affairs](http://securityaffairs.co/wordpress/69553/malware/data-keeper-ransomware.html)，DigApis编辑，如需转载请标明来源。


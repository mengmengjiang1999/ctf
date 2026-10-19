## 一、样本简介

**Ryuk勒索病毒最新于2018年8月由国外某安全公司进行报道，短短两周内净赚超过64万美元的比特币，同时跟踪发现它与HERMES勒索病毒相关联，此外也有消息称HERMES勒索病毒与朝鲜黑客组织Lazarus有关联。Ryuk勒索病毒主要通过垃圾邮件以及漏洞利用工具包进行传播，专门用于自定义攻击，Ryuk的感染和传播过程都是由攻击者手动执行的，被加密的文件以.RYK后缀结尾。**

2019年1月份，美国一家印刷厂遭遇了网络攻击，导致美各大报纸发行受阻，根据内部消息，该印刷厂很可能被感染了Ryuk的勒索病毒，同时一家拥有30000家用户的云托管服务提供商在圣诞节前也遭遇了Ryuk勒索病毒的攻击。深信服安全团队密切关注此勒索病毒的最新进展，同时于第一时间拿到了相关样本，并对样本进行了详细分析，此勒索病毒打响了黑产团队2019年利用勒索病毒攻击的序幕。

## 二、详细分析

1.判断操作系统版本，设置自启动项，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192106_5c38472a05ede.png!small)

设置后的相应的自启动项，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192112_5c38473082743.png!small)

2.进程提权操作，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192122_5c38473a61a96.png!small)

提升进程为SeDebugPrivilege权限，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192130_5c3847420d655.png!small)

3.遍历进程，获取进程的登录用户信息，设置令牌访问信息，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192139_5c38474b52b19.png!small)

4.遍历进程，如果进程不是csrss.exe、explorer.exe、lsass.exe这三个进程，则注入相应的勒索病毒入代码到进程中，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192150_5c3847566b00e.png!small)

注入进程，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192173_5c38476dda791.png!small)

然后调用CreateRemoteThread执行相应的代码，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192181_5c38477565ebc.png!small)

5.获取相应的函数地址，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192191_5c38477f321d9.png!small)

6.获取系统版本信息，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192201_5c3847890dac4.png!small)

7.根据系统版本，在不同的路径下写入相应的文件，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192210_5c384792be290.png!small)

相应的路径为:

> C:\Documents and Settings\DefaultUser\sys
>
> C:\users\Public\sys

8.生成相应的密钥，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192221_5c38479deb7c2.png!small)

使用RSA公钥加密生成的密钥，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192233_5c3847a971d79.png!small)

相应的反汇编代码，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192243_5c3847b38c3b2.png!small)

9.在内存中解密出相应的勒索信息，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192252_5c3847bce33bc.png!small)

解密之后的信息，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192264_5c3847c8e781b.png!small)

10.遍历磁盘，加密文件，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192274_5c3847d24e259.png!small)

遍历磁盘目录文件，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192288_5c3847e054b88.png!small)

排除Windows、Mozilia、Recycle.Bin、Chrome、AhnLab等目录，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192302_5c3847ee9611f.png!small)

11.在加密的磁盘文件目录，生成RyukReadMe.txt勒索信息文本文件，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192314_5c3847fa8292e.png!small)

生成的勒索信息文本文件内容，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192327_5c38480700e87.png!small)

BTC钱包地址：1ChnbV4Rt7nsb5acw5YfYyvBFDj1RXcVQu

12.遍历文件，排除dll、lnk、hrmlog、ini、exe后缀的文件，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192337_5c384811f19e2.png!small)

同时排除如下文件名，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192348_5c38481ca86f0.png!small)

13.加密文件，用加密后的文件替换原文件，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192358_5c3848261fac6.png!small)

加密后的文件名为[原文件名]+RYK结尾的后缀，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192454_5c38488650f8a.png!small)

加密文件的过程，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192413_5c38485d12774.png!small)

14.同时此勒索病毒，会枚举网络资源，然后再加密网络资源目录下的文件，如下所示：

![注入型勒索病毒Ryuk](https://image.3001.net/images/20190111/1547192403_5c3848531218c.png!small)

## 三、解决方案

深信服EDR安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

> 1.不要点击来源不明的邮件附件，不从不明网站下载软件
>
> 2.及时给主机打补丁(永恒之蓝漏洞补丁)，修复相应的高危漏洞
>
> 3.对重要的数据文件定期进行非本地备份
>
> 4.尽量关闭不必要的文件共享权限以及关闭不必要的端口，如：445,135,139,3389等
>
> 5.RDP远程服务器等连接尽量使用强密码，不要使用弱密码
>
> 6.安装专业的终端安全防护软件，为主机提供端点防护和病毒检测清理功能

 ***本文作者：千里目安全实验室，转载请注明来自 FreeBuf.COM**


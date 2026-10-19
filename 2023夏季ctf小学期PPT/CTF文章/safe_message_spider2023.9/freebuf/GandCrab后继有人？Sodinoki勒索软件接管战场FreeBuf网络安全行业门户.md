## 背景

 **近日，奇安信威胁情报中心红雨滴安全研究团队(RedDrip)监测到了针对中国用户
投递的且带有中文诱饵的压缩包样本，经分析后确认压缩包内为Sodinokibi勒索病毒。在进行关联分析之后，我们发现诱饵文件与上月初我们捕获到的投递GandCrab[1]的诱饵文件之间存在某些相似的地方，不排除这两起攻击活动由同一个团伙运营，或两者之间联系紧密，有一定程度的人员重合。**

Sodinokibi最早在今年4月份被Talos发现[2]，当时攻击者通过WebLogic服务器零日漏洞CVE-2019-2725发起攻击并投放该恶意负载。他们在分析时发现攻击者在植入Sodinokibi数小时后又植入了GandCrab
v5.2勒索病毒，并猜测这一异常事件可能是因为新样本Sodinokibi在当时没有达到攻击效果，因此再次使用GandCrab来进行钱财勒索。Tesorion在后续的分析报告中，进一步指出了这两个家族在随机URL生成方面的相似性。在本文中我们将指出两者在诱饵文件方面的相似之处，尽管尚无法确认二者的关联，但相信随着更多新线索的出现，真相将逐渐显现出来。

几天前，GandCrab的作者在表示将停止运营该勒索病毒并退休[4]，然而 Sodinokibi
等新样本的出现表明这并不代表勒索类恶意样本的影响会因此而减少
。GandCrab即便真的退出，其一年狂卷25亿美元的“辉煌”业绩并成功逃脱法律制裁，只会更多激励后来者沿着这个技术路线和勒索模式继续作恶，我们绝没有放松警惕的借口，与勒索的搏斗只会持续加强。

## 诱饵分析

MD5 | 12befdd8032a552e603fabc5d37bda35  
---|---  
文件格式 | Email  
  
通过邮件分析，红雨滴团队发现此次攻击疑似针对国内游戏测评公司任玩堂（[www.appgame.com](http://www.appgame.com)），邮件伪装成DHL货物交付延迟通知，获取受害者信任并诱使打开。

![](https://image.3001.net/images/20190605/1559702329_5cf72b39f1dcf.png!small)

附件为压缩包，内含四个文件，可执行文件的属性设置为隐藏，因此正常用户在默认设置情况下是无法看到可执行程序的存在，只能看到两个快捷方式。在设置显示隐藏文件后能看到所有的相关文件：

![](https://image.3001.net/images/20190605/1559702384_5cf72b7085e84.png!small)

## 样本分析

文件名 | 重要信息.doc.exe/聯繫方式.doc.exe  
---|---  
MD5 | e08d8c6d2914952c25df1cd0da66131b  
  
伪装成Office Word的病毒样本首先解密一段ShellCode，并跳转执行该ShellCode：

![](https://image.3001.net/images/20190605/1559702400_5cf72b8063aea.png!small)

![](https://image.3001.net/images/20190605/1559702434_5cf72ba277134.png!small)

ShellCode主要功能为解密核心PayLoad并跳转执行：

![](https://image.3001.net/images/20190605/1559702456_5cf72bb8c11b1.png!small)

核心PayLoad为sodinokibi勒索病毒，动态解密修正137处IAT：

![](https://image.3001.net/images/20190605/1559702474_5cf72bcaed5b0.png!small)

紧接着创建互斥，保证只有一个实例运行：

![](https://image.3001.net/images/20190605/1559702489_5cf72bd936d6f.png!small)

之后解密配置信息，解密函数如下：

![](https://image.3001.net/images/20190605/1559702508_5cf72becaf464.png!small)

解密的配置信息包括公钥、白名单目录、白名单文件、白名单后缀、域名、要结束的进程等信息：

![](https://image.3001.net/images/20190605/1559702523_5cf72bfb9ddce.png!small)

然后将公钥、加密后的后缀等信息保存到注册表HKEY_LOCAL_MACHINE\SOFTWARE\recfg：

![](https://image.3001.net/images/20190605/1559702620_5cf72c5cf0bdb.png!small)

并通过GetKeyboardLayoutList获取键盘布局信息，当遇到下列语言环境时则不进行文件加密：

![](https://image.3001.net/images/20190605/1559702649_5cf72c791ae54.png!small)

判断操作系统位数：

![](https://image.3001.net/images/20190605/1559702719_5cf72cbf9828b.png!small)

![](https://image.3001.net/images/20190605/1559702728_5cf72cc8e989c.png!small)

判断当前进程是否存在配置文件中需要结束的进程，若有则结束该进程

![](https://image.3001.net/images/20190605/1559702741_5cf72cd58a940.png!small)

并通过执行CMD命令删除卷影文件防止用户恢复被加密的文件：

![](https://image.3001.net/images/20190605/1559702749_5cf72cdd3781f.png!small)

删除备份文件：

![](https://image.3001.net/images/20190605/1559702757_5cf72ce59ddb4.png!small)

并在每个目录下生成勒索相关信息：

![](https://image.3001.net/images/20190605/1559702783_5cf72cffe274c.png!small)

最终加密除白名单配置以外的所有文件，将加密后的文件设置为之前保存在注册表中的随机后缀：

![](https://image.3001.net/images/20190605/1559702794_5cf72d0a5cb9d.png!small)

加密结束后，改变桌面背景，显示勒索信息：

![](https://image.3001.net/images/20190605/1559702803_5cf72d134cf5d.png!small)

最后尝试连接配置文件中的域名，发送受害者计算机基本信息：

![](https://image.3001.net/images/20190605/1559702810_5cf72d1a3fcf5.png!small)

## 关联分析

2019年5月，奇安信红雨滴安全团队发布了《卷土重来！中文诱饵Gandcrab勒索软件肆虐五月初》分析文章，有趣的是我们发现这两次的攻击的投递方式几乎一模一样：

![](https://image.3001.net/images/20190605/1559702818_5cf72d2280d47.png!small)

且其快捷方式都泄露了攻击者的电脑名，都为win-0ev5o0is9i7

![](https://image.3001.net/images/20190605/1559702958_5cf72daec1314.png!small)

通过该电脑名我们发现近期韩国ESTsecurity也披露了针对韩国境内传播Sodinoki勒索病毒攻击活动，其攻击手法与此次攻击活动一致，且快捷方式中泄露的电脑名也为win-0ev5o0is9i7

![](https://image.3001.net/images/20190605/1559702970_5cf72dba19a30.png!small)

## 防护建议

1.尽量关闭不必要的端口，如 445、135，139 等，对 3389、5900 等端口可进行白名单配置，只允许白名单内的 IP 连接登陆。

2.采用高强度的密码，避免使用弱口令密码，并定期更换密码。

3.安装奇安信天擎新一代终端安全管理系统。

4.及时更新软件，安装补丁。

## 总结

由于Sodinokibi会通过电子邮件传播，我们建议您不要打开任何未知来源的电子邮件，尤其是不要打开附件。即使附件来自常用联系人，我们也建议您在打开之前，使用奇安信天擎对其进行扫描，以确保它不包含任何恶意文档或文件。

## 参考链接

> [1].[
> _https://mp.weixin.qq.com/s/TKZN9Qvcf_qqikeurdHBpg_](https://mp.weixin.qq.com/s/TKZN9Qvcf_qqikeurdHBpg)
>
> [2].[ _https://blog.talosintelligence.com/2019/04/sodinokibi-ransomware-> exploits-> weblogic.html_](https://blog.talosintelligence.com/2019/04/sodinokibi-> ransomware-exploits-weblogic.html)
>
> [3].[ _https://www.tesorion.nl/aconnection-between-the-sodinokibi-and-> gandcrab-ransomware-families/_](https://www.tesorion.nl/aconnection-between-> the-sodinokibi-and-gandcrab-ransomware-families/)
>
> [4].[ _https://www.zdnet.com/article/gandcrab-ransomware-operation-says-its-> shutting-down/_](https://www.zdnet.com/article/gandcrab-ransomware-> operation-says-its-shutting-down/)
>
> [5].[ _https://blog.alyac.co.kr/2344_](https://blog.alyac.co.kr/2344)

 ***本文作者：奇安信威胁情报中心，转载请注明来自FreeBuf.COM**

